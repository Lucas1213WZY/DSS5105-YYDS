import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
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

# Step 4: Define the GBDT models
gbdt_model = GradientBoostingRegressor(random_state=42)

# Step 5: Hyperparameter Tuning with GridSearchCV for GBDT
param_grid_gbdt = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1, 0.2],
    'subsample': [0.5, 0.8, 1.0],
    'min_samples_split': [5, 10],
    'max_features': ['sqrt', 'log2', 0.5],
    'max_leaf_nodes': [10, 20, 30]
}
grid_search_gbdt = GridSearchCV(estimator=gbdt_model, param_grid=param_grid_gbdt, cv=10, scoring='r2', n_jobs=-1, verbose=2)
grid_search_gbdt.fit(X_train, y_train)

# Step 6: Train the GBDT model with the best parameters
tuned_gbdt_model = grid_search_gbdt.best_estimator_
tuned_gbdt_model.fit(X_train, y_train)

# Step 6.1: Save the trained models and scaler
import pickle
with open('../pkl/tuned_gbdt_model.pkl', 'wb') as model_file:
    pickle.dump(tuned_gbdt_model, model_file)
with open('../pkl/scaler_gbdt.pkl', 'wb') as scaler_file:
    pickle.dump(scaler, scaler_file)

# Step 7: Make Predictions for GBDT
y_pred_train_gbdt = tuned_gbdt_model.predict(X_train)
y_pred_test_gbdt = tuned_gbdt_model.predict(X_test)

print(f'Variables that were log transformed due to high skewness: {log_transformed_features}')

# Step 8: Evaluate the Model

# Step 8.: Partial Dependence Plot
from sklearn.inspection import PartialDependenceDisplay
PartialDependenceDisplay.from_estimator(tuned_gbdt_model, X_train, features, kind='average', grid_resolution=20)
plt.subplots_adjust(hspace=0.5)
plt.show()

# Step 8.2: Cumulative Feature Importance
importances = tuned_gbdt_model.feature_importances_
indices = np.argsort(importances)[::-1]
cumulative_importance = np.cumsum(importances[indices])
plt.figure(figsize=(10, 6))
plt.plot(range(1, len(cumulative_importance) + 1), cumulative_importance, marker='o', linestyle='-', color='b')
plt.xlabel('Number of Features')
plt.ylabel('Cumulative Importance')
plt.title('Cumulative Feature Importance - GBDT')
plt.grid(True)
plt.show()

# Step 8.3: SHAP Analysis
import shap
explainer = shap.Explainer(tuned_gbdt_model, X_train)
shap_values = explainer(X_test)

# Summary plot for feature importance
shap.summary_plot(shap_values, X_test, feature_names=features)

# SHAP dependence plot for a specific feature
shap_values = explainer.shap_values(X_test)
shap.dependence_plot('Energy', shap_values, X_test)

# Step 8.4: Cross-Validation R² Scores Visualization
from sklearn.model_selection import cross_val_score
cv_scores_gbdt = cross_val_score(tuned_gbdt_model, X_train, y_train, cv=10, scoring='r2')

plt.figure(figsize=(10, 6))
plt.plot(range(1, len(cv_scores_gbdt) + 1), cv_scores_gbdt, marker='o', linestyle='-', color='b')
plt.xlabel('Fold Number')
plt.ylabel('R² Score')
plt.title('Cross-Validation R² Scores - GBDT')
plt.grid(True)
plt.show()

# Step 8.5: Residual Analysis
residuals = y_test - y_pred_test_gbdt
plt.figure(figsize=(10, 6))
plt.scatter(y_pred_test_gbdt, residuals, alpha=0.6)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel('Predicted GHG_Total')
plt.ylabel('Residuals')
plt.title('Residuals vs Predicted - GBDT')
plt.grid(True)
plt.show()

# Step 8.6: Actual vs Predicted Values
# Inverse log transform for target if log transformation was applied
y_test_exp = np.expm1(y_test)
y_pred_test_exp = np.expm1(y_pred_test_gbdt)

plt.figure(figsize=(10, 6))
plt.scatter(y_test_exp, y_pred_test_exp, alpha=0.6)
plt.plot([y_test_exp.min(), y_test_exp.max()], [y_test_exp.min(), y_test_exp.max()], 'r--')
plt.xlabel('Actual GHG_Total')
plt.ylabel('Predicted GHG_Total')
plt.title('Actual vs Predicted GHG_Total - GBDT')
plt.grid(True)
plt.show()

# Step 8.7: Feature Importance
importances = tuned_gbdt_model.feature_importances_
indices = np.argsort(importances)[::-1]

plt.figure(figsize=(10, 6))
plt.title('Feature Importances - GBDT')
plt.bar(range(X_train.shape[1]), importances[indices], align='center')
plt.xticks(range(X_train.shape[1]), [features[i] for i in indices], rotation=45)
plt.xlabel('Feature')
plt.ylabel('Importance')
plt.grid(True)
plt.show()

# Step 8.8: Permutation Feature Importance
from sklearn.inspection import permutation_importance
perm_importance_gbdt = permutation_importance(tuned_gbdt_model, X_test, y_test, n_repeats=10, random_state=42)
sorted_idx = perm_importance_gbdt.importances_mean.argsort()[::-1]

plt.figure(figsize=(10, 6))
plt.title('Permutation Feature Importance - GBDT')
plt.bar(range(X_train.shape[1]), perm_importance_gbdt.importances_mean[sorted_idx], align='center')
plt.xticks(range(X_train.shape[1]), [features[i] for i in sorted_idx], rotation=45)
plt.xlabel('Feature')
plt.ylabel('Importance')
plt.grid(True)
plt.show()


