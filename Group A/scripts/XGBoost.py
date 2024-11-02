import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import numpy as np

# Step 1: Load the dataset
df = pd.read_excel('../data/tidy_RandomNum.xlsx')

# Strip whitespace from column names to avoid matching issues
df.columns = df.columns.str.strip()

# Step 2: Data Preprocessing
# Select relevant columns
features = ['Energy', 'Waste', 'Water', 'Transportation']
target = 'GHG_Total'
X = df[features]
y = df[target]

# Calculate skewness for all variables
skewed_features = pd.concat([X, y], axis=1).apply(lambda x: x.skew()).abs()

# Log transform for skewed features with skewness > 1
log_transformed_features = []
for column in skewed_features.index:
    if skewed_features[column] > 1:
        if (df[column] > 0).all():  # Apply log transform only if all values are positive
            df[column] = np.log1p(df[column])
            log_transformed_features.append(column)

# Update X and y after log transformation
X = df[features]
y = df[target]

# Standardize the features
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X = pd.DataFrame(scaler.fit_transform(X), columns=features)

# Step 3: Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Define the XGBoost model
xgb_model = xgb.XGBRegressor(objective='reg:squarederror', random_state=42)

# Step 5: Hyperparameter Tuning with GridSearchCV
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1, 0.2],
    'subsample': [0.8, 1.0],
    'colsample_bytree': [0.6, 0.8, 1.0],
    'gamma': [0, 0.1, 0.5, 1],
    'reg_alpha': [0, 0.1, 0.5, 1],
}
grid_search = GridSearchCV(estimator=xgb_model, param_grid=param_grid, cv=10, scoring='r2', n_jobs=-1, verbose=2)
grid_search.fit(X_train, y_train)

# Step 6: Train the model with the best parameters
tuned_xgb_model = grid_search.best_estimator_
tuned_xgb_model.fit(X_train, y_train)

# Step 6.1: Save the trained model and scaler
import pickle
with open('../pkl/tuned_xgb_model.pkl', 'wb') as model_file:
    pickle.dump(tuned_xgb_model, model_file)
with open('../pkl/scaler_xgb.pkl', 'wb') as scaler_file:
    pickle.dump(scaler, scaler_file)

# Step 7: Make Predictions
y_pred_train = tuned_xgb_model.predict(X_train)
y_pred_test = tuned_xgb_model.predict(X_test)

print(f'Variables that were log transformed due to high skewness: {log_transformed_features}')

# Step 8: Evaluate the Model

# Step 8.1: SHAP Analysis for Model Explanation
import shap
explainer = shap.Explainer(tuned_xgb_model, X_train)
shap_values = explainer(X_test)

# Plot summary of feature importance
shap.summary_plot(shap_values, X_test)
train_r2 = r2_score(y_train, y_pred_train)
test_r2 = r2_score(y_test, y_pred_test)
test_mse = mean_squared_error(y_test, y_pred_test)
test_mae = mean_absolute_error(y_test, y_pred_test)

print(f'Train R²: {train_r2}')
print(f'Test R²: {test_r2}')
print(f'Test MSE: {test_mse}')
print(f'Test MAE: {test_mae}')

# Step 9: Plot Actual vs Predicted Values
# Inverse log transform for target if log transformation was applied
y_test = np.expm1(y_test)
y_pred_test = np.expm1(y_pred_test)

plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred_test, alpha=0.6)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
plt.xlabel('Actual GHG_Total')
plt.ylabel('Predicted GHG_Total')
plt.title('Actual vs Predicted GHG_Total - XGBoost')
plt.grid(True)
plt.show()

# Step 10: Cross-Validation Accuracy Plot
from sklearn.model_selection import cross_val_score

cv_scores = cross_val_score(tuned_xgb_model, X_train, y_train, cv=10, scoring='r2')

# Plot Cross-Validation R² Scores
plt.figure(figsize=(10, 6))
plt.plot(range(1, len(cv_scores) + 1), cv_scores, marker='o', linestyle='-', color='b')
plt.xlabel('Fold Number')
plt.ylabel('R² Score')
plt.title('Cross-Validation R² Scores - XGBoost')
plt.grid(True)
plt.show()

# Step 11: Feature Importance (Weight)
plt.figure(figsize=(10, 6))
xgb.plot_importance(tuned_xgb_model, importance_type='weight', max_num_features=10)
plt.title('Feature Importance - Weight (XGBoost)')
plt.show()

# Feature Importance (Gain)
plt.figure(figsize=(10, 6))
ax = xgb.plot_importance(tuned_xgb_model, importance_type='gain', max_num_features=10)
for text, patch in zip(ax.texts, ax.patches):
    text.set_position((patch.get_width() + 0.01, patch.get_y() + patch.get_height() / 2))  # Adjust position to be closer to the bar
    text.set_text(f'{float(text.get_text()):.2f}')  # Limit to 2 decimal places
plt.title('Feature Importance - Gain (XGBoost)')
plt.show()

# Feature Importance (Cover)
plt.figure(figsize=(10, 6))
ax = xgb.plot_importance(tuned_xgb_model, importance_type='cover', max_num_features=10)
for text in ax.texts:
    text.set_text(f'{float(text.get_text()):.2f}')  # Limit to 2 decimal places
plt.title('Feature Importance - Cover (XGBoost)')
plt.show()


