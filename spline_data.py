import pandas as pd
import numpy as np
from scipy.interpolate import interp1d, lagrange

def interpolate (data1, type):
    data = data1
    if type == 1:
        for i in range(0, len(data.columns), 3):
            subset = data.iloc[:, i:i + 3]
            for index, row in subset.iterrows():
                if sum(row.isna()) == 1:
                    not_nan = row.notna()
                    x = np.where(not_nan)[0]
                    y = row[not_nan].values
                    f = interp1d(x, y, kind='linear', fill_value="extrapolate")
                    nan_idx = np.where(~not_nan)[0][0]
                    subset.iloc[index, nan_idx] = f(nan_idx)
            data.iloc[:, i:i + 3] = subset
        return data

    elif type == 2:
        for i in range(0, len(data.columns), 3):
            subset = data.iloc[:, i:i + 3]
            for index, row in subset.iterrows():
                if sum(row.isna()) == 1:
                    not_nan = row.notna()
                    x = np.where(not_nan)[0] + 1
                    new_index = 0
                    x = np.insert(x, 0, new_index)
                    y = row[not_nan].values
                    y_mid = np.mean(y)
                    y_std = np.std(y)
                    random_value = np.random.uniform(y_mid + 2 * y_std, y[0])
                    y = np.array([random_value] + y.tolist())
                    poly = lagrange(x, y)
                    nan_idx = np.where(~not_nan)[0][0] + 1
                    subset.iloc[index, nan_idx - 1] = poly(nan_idx)
            data.iloc[:, i:i + 3] = subset
        return data

    elif type == 3:
        for i in range(0, len(data.columns), 3):
            subset = data.iloc[:, i:i + 3]
            for index, row in subset.iterrows():
                if sum(row.isna()) == 1 :
                    not_nan = row.notna()
                    x = np.where(not_nan)[0] + 2
                    new_index = [0, 1]
                    x = np.insert(x, 0, new_index)
                    y = row[not_nan].values
                    y_mid = np.mean(y)
                    y_std = np.std(y)
                    random_value1 = np.random.uniform(y_mid + 2 * y_std, y[0])
                    random_value2 = np.random.uniform(y_mid + 2 * y_std, y[0])
                    y = np.array([random_value1, random_value2] + y.tolist())
                    f = interp1d(x, y, kind='quadratic', fill_value="extrapolate")
                    nan_idx = np.where(~not_nan)[0][0] + 2
                    subset.iloc[index, nan_idx - 2] = f(nan_idx)
            data.iloc[:, i:i + 3] = subset
        return data

if __name__ == '__main__':
    data = pd.read_excel('../data/merged_data.xlsx')
    data = data.replace(['NAN','Nan','nan', 0], np.nan)
    # 1 : Linear Interpolation
    # 2 : Lagrange Interpolation
    # 3 : Quadratic Spline Interpolation
    with pd.ExcelWriter('../data/spline_data.xlsx') as writer:
        data1 = data.copy()
        data2 = data.copy()
        data3 = data.copy()
        str_index = data.columns[data.columns.str.contains('_20')].tolist()
        temp = data1[str_index]
        spline_data1 = interpolate(temp, type=1)
        data1[str_index] = spline_data1
        data1.to_excel(writer, sheet_name='spline_data1', index=False)
        temp = data2[str_index]
        np.random.seed(1234)
        spline_data2 = interpolate(temp, type=2)
        data2[str_index] = spline_data2
        data2.to_excel(writer, sheet_name='spline_data2', index=False)
        temp = data3[str_index]
        np.random.seed(1234)
        spline_data3 = interpolate(temp, type=3)
        data3[str_index] = spline_data3
        data3.to_excel(writer, sheet_name='spline_data3', index=False)

