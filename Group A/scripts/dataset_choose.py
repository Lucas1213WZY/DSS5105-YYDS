import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import lightgbm as lgb
import matplotlib.pyplot as plt
from scipy.stats import skew

# Load the datasets
file_path_1 = '../data/tidy_RandomNum.xlsx'
file_path_2 = '../data/tidy_DataImpKNN.xlsx'
file_path_3 = '../data/tidy_Spline1.xlsx'
file_path_4 = '../data/tidy_Spline2.xlsx'
file_path_5 = '../data/tidy_Spline3.xlsx'

df1 = pd.read_excel(file_path_1)
df2 = pd.read_excel(file_path_2)
df3 = pd.read_excel(file_path_3)
df4 = pd.read_excel(file_path_4)
df5 = pd.read_excel(file_path_5)

# Define features and target variable
features = ['Energy', 'Waste', 'Water', 'Transportation']
target = 'GHG_Total'

# Function to preprocess data and train models
def preprocess_and_train(df, dataset_name):
    # Drop rows with any negative values
    df = df[(df[features] >= 0).all(axis=1)]
    X = df[features]
    y = df[target]

    # Check skewness of features and target, apply log transformation if needed
    for column in features + [target]:
        skewness = skew(df[column])
        if abs(skewness) > 1:
            df[column] = df[column].apply(lambda x: np.log1p(x))

    # Update features and target after log transformation
    X = df[features]
    y = df[target]

    # Standardize the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    results = {'dataset_name': dataset_name}

    # Random Forest Regressor - Hyperparameter tuning
    param_grid_rf = {
        'n_estimators': [100, 200, 300],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', 'log2']
    }

    grid_search_rf = GridSearchCV(RandomForestRegressor(random_state=42), param_grid_rf, cv=10, scoring='r2', error_score='raise')
    grid_search_rf.fit(X_train, y_train)

    # Train the Random Forest model with the best parameters
    tuned_rf_model = RandomForestRegressor(**grid_search_rf.best_params_, random_state=42)

    # Use cross_val_score to evaluate the model with cross-validation
    cv_scores_rf_r2 = cross_val_score(tuned_rf_model, X_scaled, y, cv=10, scoring='r2')
    cv_scores_rf_mse = cross_val_score(tuned_rf_model, X_scaled, y, cv=10, scoring='neg_mean_squared_error')
    cv_scores_rf_mae = cross_val_score(tuned_rf_model, X_scaled, y, cv=10, scoring='neg_mean_absolute_error')
    results['rf_r2'] = np.mean(cv_scores_rf_r2)
    results['rf_mse'] = -np.mean(cv_scores_rf_mse)
    results['rf_mae'] = -np.mean(cv_scores_rf_mae)

    # Gradient Boosting Regressor - Hyperparameter tuning
    param_grid_gb = {
        'n_estimators': [100, 200, 300],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2],
        'subsample': [0.8, 1.0],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }

    grid_search_gb = GridSearchCV(GradientBoostingRegressor(random_state=42), param_grid_gb, cv=10, scoring='r2', error_score='raise')
    grid_search_gb.fit(X_train, y_train)

    # Train the Gradient Boosting model with the best parameters
    tuned_gb_model = GradientBoostingRegressor(**grid_search_gb.best_params_, random_state=42)

    # Use cross_val_score to evaluate the model with cross-validation
    cv_scores_gb_r2 = cross_val_score(tuned_gb_model, X_scaled, y, cv=5, scoring='r2')
    cv_scores_gb_mse = cross_val_score(tuned_gb_model, X_scaled, y, cv=5, scoring='neg_mean_squared_error')
    cv_scores_gb_mae = cross_val_score(tuned_gb_model, X_scaled, y, cv=5, scoring='neg_mean_absolute_error')
    results['gb_r2'] = np.mean(cv_scores_gb_r2)
    results['gb_mse'] = -np.mean(cv_scores_gb_mse)
    results['gb_mae'] = -np.mean(cv_scores_gb_mae)

    # XGBoost Regressor - Hyperparameter tuning
    param_grid_xgb = {
        'n_estimators': [100, 200, 300],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2],
        'subsample': [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0]
    }

    grid_search_xgb = GridSearchCV(xgb.XGBRegressor(objective='reg:squarederror', random_state=42), param_grid_xgb, cv=5, scoring='r2', error_score='raise')
    grid_search_xgb.fit(X_train, y_train)

    # Train the XGBoost model with the best parameters
    tuned_xgb_model = xgb.XGBRegressor(objective='reg:squarederror', **grid_search_xgb.best_params_, random_state=42)

    # Use cross_val_score to evaluate the model with cross-validation
    cv_scores_xgb_r2 = cross_val_score(tuned_xgb_model, X_scaled, y, cv=5, scoring='r2')
    cv_scores_xgb_mse = cross_val_score(tuned_xgb_model, X_scaled, y, cv=5, scoring='neg_mean_squared_error')
    cv_scores_xgb_mae = cross_val_score(tuned_xgb_model, X_scaled, y, cv=5, scoring='neg_mean_absolute_error')
    results['xgb_r2'] = np.mean(cv_scores_xgb_r2)
    results['xgb_mse'] = -np.mean(cv_scores_xgb_mse)
    results['xgb_mae'] = -np.mean(cv_scores_xgb_mae)

    # LightGBM Regressor - Hyperparameter tuning
    param_grid_lgb = {
        'n_estimators': [100, 200, 300],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2]
    }

    grid_search_lgb = GridSearchCV(lgb.LGBMRegressor(random_state=42, force_row_wise=True), param_grid_lgb, cv=5, scoring='r2', error_score='raise')
    grid_search_lgb.fit(X_train, y_train)

    # Train the LightGBM model with the best parameters
    tuned_lgb_model = lgb.LGBMRegressor(**grid_search_lgb.best_params_, random_state=42, force_row_wise=True)

    # Use cross_val_score to evaluate the model with cross-validation
    cv_scores_lgb_r2 = cross_val_score(tuned_lgb_model, X_scaled, y, cv=5, scoring='r2')
    cv_scores_lgb_mse = cross_val_score(tuned_lgb_model, X_scaled, y, cv=5, scoring='neg_mean_squared_error')
    cv_scores_lgb_mae = cross_val_score(tuned_lgb_model, X_scaled, y, cv=5, scoring='neg_mean_absolute_error')
    results['lgb_r2'] = np.mean(cv_scores_lgb_r2)
    results['lgb_mse'] = -np.mean(cv_scores_lgb_mse)
    results['lgb_mae'] = -np.mean(cv_scores_lgb_mae)

    return results

# Preprocess and train models for all datasets
results_1 = preprocess_and_train(df1, 'Dataset 1 (tidy_RandomNum)')
results_2 = preprocess_and_train(df2, 'Dataset 2 (tidy_DataImpKNN)')
results_3 = preprocess_and_train(df3, 'Dataset 3 (tidy_Spline1)')
results_4 = preprocess_and_train(df4, 'Dataset 4 (tidy_Spline2)')
results_5 = preprocess_and_train(df5, 'Dataset 5 (tidy_Spline3)')

# Visualization of the results
metrics = ['r2', 'mse', 'mae']
models = ['rf', 'gb', 'xgb', 'lgb']
datasets = [results_1, results_2, results_3, results_4, results_5]
dataset_names = ['Dataset 1 (tidy_RandomNum)', 'Dataset 2 (tidy_DataImpKNN)', 'Dataset 3 (tidy_Spline1)', 'Dataset 4 (tidy_Spline2)', 'Dataset 5 (tidy_Spline3)']

for metric in metrics:
    plt.figure(figsize=(10, 6))
    for i, dataset in enumerate(datasets):
        values = [dataset.get(f'{model}_{metric}', np.nan) for model in models]
        plt.plot(models, values, marker='o', label=dataset_names[i])
    plt.xlabel('Models')
    plt.ylabel(metric.upper())
    plt.title(f'Comparison of {metric.upper()} for Different Models and Datasets')
    plt.legend()
    plt.grid(True)
    plt.show()


