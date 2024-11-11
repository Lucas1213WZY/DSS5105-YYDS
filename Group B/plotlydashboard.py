from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go

df = pd.read_csv('merged_df.csv', encoding="utf-8", encoding_errors='ignore')
df['YearDate'] = pd.to_datetime(df['Year'].astype('str') + '-01-01')
print(df.head())
app = Dash()

app.layout = html.Div(children=[
    html.H1(children='Title of Dash App', style={'textAlign': 'center'}),
    dcc.Dropdown(df["Building Name"].unique(),
                 'Building Name', id='dropdown-selection'),
    html.Section(style={"display": 'grid', "grid-template-columns": 'repeat(12,1fr)'},
                 children=[
                     html.Div(style={"grid-column": "span 6"},
                              children=[dcc.Graph(id='award')]),
                     html.Div(style={"grid-column": "span 6"},
                              children=[dcc.Graph(id='year_trend_line')]),
                     html.Div(style={"grid-column": "span 6"},
                              children=[dcc.Graph(id='violin')]),
                     html.Div(style={"grid-column": "span 3"},
                              children=[dcc.Graph(id='pie_1')]),
                     html.Div(style={"grid-column": "span 3"},
                              children=[dcc.Graph(id='pie_2')]),
                     html.Img(style={"grid-column": "span 3"},
                              src="assets/1.png"),
                     html.Img(style={"grid-column": "span 4"},src="assets/2.png"),


    ]
    )

])


# line
@callback(
    Output('year_trend_line', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    # dff = df[df.country==value]
    year_trend_df = df.groupby('YearDate').agg(
        {'GHG_Intensity': 'mean'}).reset_index()
    fig = px.line(year_trend_df, x='YearDate', y='GHG_Intensity', title="line chart",
                  labels={"GHG_Intensity": "Greenhouse Gas Emissions  Intensity"})
    fig.update_traces(line=dict(color="#365E32"))
    return fig


# Bubble
@callback(
    Output('award', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    x = [0, 1, 2, 3]
    y = [2, 2, 2, 2]
    bubble_data = df.groupby('Award').agg(
        unique_building_count=('Building Name', 'nunique')).reset_index()
    bubble_data['x'] = x
    bubble_data['y'] = y
    # 创建气泡图
    fig = go.Figure(data=[
        go.Scatter(
            x=x,
            y=y,
            mode='markers+text',
            fillcolor="#365E32",
            marker=dict(
                size=bubble_data["unique_building_count"],
                opacity=0.6,
                color="#365E32"
            ),

            text=bubble_data["Award"],
            textposition="top center",
            hoverinfo='text',  # 显示提示框
            hovertext=bubble_data["unique_building_count"]  # 提示框中显示的内容

        )
    ])

    fig.update_layout(title="Pure Bubble Chart", showlegend=False,
                      xaxis=dict(showgrid=False, showline=False,
                                 zeroline=False, visible=False),
                      yaxis=dict(showgrid=False, showline=False, zeroline=False, visible=False), )
    return fig


# pie
@callback(
    Output('pie_2', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    # dff = df[df.country==value]
    melt_cols = ['Building Name', "Scope1", "Scope2", "Scope3"]
    pie_data = df[melt_cols]
    pie_data = pd.melt(pie_data, id_vars='Building Name',
                       var_name='key', value_name='value')

    pie_data = pie_data.groupby('key').agg({"value": 'sum'}).reset_index()
    pie_data['key'] = pie_data['key'].replace('Scope1', 'Scope1+2')
    pie_data['key'] = pie_data['key'].replace('Scope2', 'Scope1+2')
    # pie_data['key'] = df['key'].astype(str)
    print(pie_data.head())
    fig = px.pie(pie_data, names='key', color='key', values='value', title="pie chart ",
                 color_discrete_map={'Scope1+2': '#365E32',
                                     'Scope3': '#E7D37F'})
    fig.update_traces(
        texttemplate='%{label}: %{percent:.2%}', textposition='outside')

    return fig


# histogram
@callback(
    Output('pie_1', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    melt_cols = ['Building Name', "Water", "Waste"]
    pie_data = df[melt_cols]
    pie_data = pd.melt(pie_data, id_vars='Building Name',
                       var_name='key', value_name='value')
    pie_data = pie_data.groupby('key').agg({"value": 'sum'}).reset_index()
    print(pie_data.head())
    fig = px.pie(pie_data, names='key', color='key', values='value', title="scope 1 decomposition ",
                 color_discrete_map={'Water': '#365E32  ',
                                     'Waste': '#81A263'})
    fig.update_traces(
        texttemplate='%{label}: %{percent:.2%}', textposition='outside')
    return fig


# violin
@callback(
    Output('violin', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    melt_cols = ['Building Name', "GHG_Intensity"]
    h_data = df[melt_cols]
    fig = px.violin(h_data, x="GHG_Intensity", box=True, points='all', title="Violin",
                    labels={"GHG_Intensity": "Greenhouse Gas Emissions  Intensity"})
    fig.update_traces(marker=dict(color="green"))
    return fig


if __name__ == '__main__':
    app.run(debug=True)
