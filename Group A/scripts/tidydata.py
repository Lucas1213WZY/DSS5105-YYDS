# %%
import numpy as np
import pandas as pd

# %%
df = pd.read_excel('../data/Spline.xlsx', sheet_name = 'Sheet3', dtype={'POSTAL CODE': str})

df['Building'] = df['Building Name'].str.cat(df['POSTAL CODE'], sep = '_')
df = df.drop(columns=['Index', 'Building Name', 'POSTAL CODE', '2020 EUI'])

cols = list(df.columns)
cols.insert(0, cols.pop(cols.index('Building')))

df = df[cols]

df.rename(columns = {'2021 EUI': 'EUI_2021', '2022 EUI': 'EUI_2022', '2023 EUI': 'EUI_2023'}, inplace = True)

# %%
df.rename(columns = {'Building Type': 'Type', 'Main Function': 'Function', 'Building Size': 'Size', 'Employee(people)': 'Employee', 'Transportation Data in 2023 (km)': 'Transportation', 'gross floor Area (sqm)': 'GFA'}, inplace = True)

time_series_columns = [
    ('Total Energy Consumption(kwh)_2021', 'Total Energy Consumption(kwh)_2022', 'Total Energy Consumption(kwh)_2023'),
    ('Total Waste Consumed(Metric Tons)_2021', 'Total Waste Consumed(Metric Tons)_2022', 'Total Waste Consumed(Metric Tons)_2023'),
    ('Total Water Consumed (m3) _2021', 'Total Water Consumed (m3) _2022', 'Total Water Consumed (m3) _2023'),
    ('Scope 1 GHG Total Emission(t CO2e)_2021', 'Scope 1 GHG Total Emission(t CO2e)_2022', 'Scope 1 GHG Total Emission(t CO2e)_2023'),
    ('Scope 2 GHG Total Emission(t CO2e)_2021', 'Scope 2 GHG Total Emission(t CO2e)_2022', 'Scope 2 GHG Total Emission(t CO2e)_2023'),
    ('Scope 3 GHG Total Emission(t CO2e)_2021', 'Scope 3 GHG Total Emission(t CO2e)_2022', 'Scope 3 GHG Total Emission(t CO2e)_2023'),
    ('GHG Total Emission(t CO2e)_2021', 'GHG Total Emission(t CO2e)_2022', 'GHG Total Emission(t CO2e)_2023'),
    ('EUI_2021', 'EUI_2022', 'EUI_2023')
]

fixed_columns = ['Building', 'latitude', 'longitude', 'Address', 'Type', 'Function', 'Size', 'Employee', 'Transportation', 'GFA']

df_long = pd.wide_to_long(df, stubnames=['Total Energy Consumption(kwh)', 'Total Waste Consumed(Metric Tons)', 'Total Water Consumed (m3) ', 'Scope 1 GHG Total Emission(t CO2e)', 'Scope 2 GHG Total Emission(t CO2e)', 'Scope 3 GHG Total Emission(t CO2e)', 'GHG Total Emission(t CO2e)', 'EUI'],
                          i=fixed_columns, j='Year', sep='_', suffix='\d+').reset_index()

for col in fixed_columns:
    df_long[col] = df_long[col].fillna(method='ffill')

col_to_move = 'Year'
year_column = df_long.pop(col_to_move)
df_long.insert(1, col_to_move, year_column)


df_long.rename(columns = {'Total Energy Consumption(kwh)': 'Energy', 'Total Waste Consumed(Metric Tons)': 'Waste', 'Total Water Consumed (m3) ': 'Water', 
                     'Scope 1 GHG Total Emission(t CO2e)': 'Scope1', 'Scope 2 GHG Total Emission(t CO2e)': 'Scope2', 'Scope 3 GHG Total Emission(t CO2e)': 'Scope3',
                     'GHG Total Emission(t CO2e)': 'GHG_Total'}, inplace = True)

df_long.head()

# %%
df_long.to_excel('../data/tidy_Spline3.xlsx', index=False)


