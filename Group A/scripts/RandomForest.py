import pandas as pd
from sklearn.ensemble import RandomForestRegressor
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

# Step 4: Define the RandomForest model
rf_model = RandomForestRegressor(random_state=42)

# Step 5: Hyperparameter Tuning with GridSearchCV
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 10, 15, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['sqrt', 'log2', 0.5],
    'bootstrap': [True],
    'max_leaf_nodes': [10, 20, 30]
}
grid_search = GridSearchCV(estimator=rf_model, param_grid=param_grid, cv=10, scoring='r2', n_jobs=-1, verbose=2)
grid_search.fit(X_train, y_train)

# Step 6: Train the model with the best parameters
tuned_rf_model = grid_search.best_estimator_
tuned_rf_model.fit(X_train, y_train)

# Step 6.1: Save the trained model and scaler
import pickle
with open('../pkl/tuned_rf_model.pkl', 'wb') as model_file:
    pickle.dump(tuned_rf_model, model_file)
with open('../pkl/scaler_rf.pkl', 'wb') as scaler_file:
    pickle.dump(scaler, scaler_file)

# Step 7: Make Predictions
y_pred_train = tuned_rf_model.predict(X_train)
y_pred_test = tuned_rf_model.predict(X_test)

print(f'Variables that were log transformed due to high skewness: {log_transformed_features}')

# Step 8: Evaluate the Model

# Step 8.1: Residual Analysis
residuals = y_test - y_pred_test
plt.figure(figsize=(10, 6))
plt.scatter(y_pred_test, residuals, alpha=0.6)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel('Predicted GHG_Total')
plt.ylabel('Residuals')
plt.title('Residuals vs Predicted - RandomForest')
plt.grid(True)
plt.show()
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
plt.title('Actual vs Predicted GHG_Total - RandomForest')
plt.grid(True)
plt.show()

# Step 10: Cross-Validation Accuracy Plot
from sklearn.model_selection import cross_val_score
cv_scores = cross_val_score(tuned_rf_model, X_train, y_train, cv=10, scoring='r2')

plt.figure(figsize=(10, 6))
plt.plot(range(1, len(cv_scores) + 1), cv_scores, marker='o', linestyle='-', color='b')
plt.xlabel('Fold Number')
plt.ylabel('R² Score')
plt.title('Cross-Validation R² Scores - RandomForest')
plt.grid(True)
plt.show()

# Step 11: Feature Importance
# Feature Importance based on impurity
importances = tuned_rf_model.feature_importances_
indices = np.argsort(importances)[::-1]

plt.figure(figsize=(10, 6))
plt.title('Feature Importances - RandomForest')
plt.bar(range(X_train.shape[1]), importances[indices], align='center')
plt.xticks(range(X_train.shape[1]), [features[i] for i in indices], rotation=45)
plt.xlabel('Feature')
plt.ylabel('Importance')
plt.grid(True)
plt.show()

# Permutation Importance
from sklearn.inspection import permutation_importance

perm_importance = permutation_importance(tuned_rf_model, X_test, y_test, n_repeats=10, random_state=42)
sorted_idx = perm_importance.importances_mean.argsort()[::-1]

plt.figure(figsize=(10, 6))
plt.title('Permutation Feature Importance - RandomForest')
plt.bar(range(X_train.shape[1]), perm_importance.importances_mean[sorted_idx], align='center')
plt.xticks(range(X_train.shape[1]), [features[i] for i in sorted_idx], rotation=45)
plt.xlabel('Feature')
plt.ylabel('Importance')
plt.grid(True)
plt.show()

# Partial Dependence Plot
from sklearn.inspection import PartialDependenceDisplay

PartialDependenceDisplay.from_estimator(tuned_rf_model, X_train, features, kind='average', grid_resolution=20)
plt.subplots_adjust(hspace=0.5)
plt.show()


