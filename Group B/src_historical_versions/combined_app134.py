import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import io
import dash_bootstrap_components as dbc
from dash import dash_table
import folium
from dash_extensions import BeforeAfter
import dash_leaflet as dl
import base64
import plotly.graph_objects as go


# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY], suppress_callback_exceptions=True)
server = app.server


# Main layout
app.layout = html.Div([
    # Navbar with centered title "GHG Emissions Calculator"
    html.Div(
        dbc.NavbarSimple(
            brand="GHG Emissions Calculator", 
            brand_href="/",
            color="success",
            dark=True,
            style={
                "fontSize": "48px",
                "fontWeight": "bold",
                "textAlign": "center",
                "justifyContent": "center",
                "padding": "30px",
                "margin-bottom": "30px"
            }
        ),
        style={'textAlign': 'center'}
    ),
    
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


# File upload section layout with logo image
file_upload_layout = html.Div([
    html.Img(
        src='./assets/teamlogo.png',
        style={
            'position': 'absolute',
            'top': '10px',
            'right': '10px',
            'width': '500px',  # 控制图片宽度
            'height': 'auto'  # 保持图片比例
        }
    ),
    dbc.Card([
        dbc.CardHeader(html.H2("File Upload", style={'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '28px'})),
        dbc.CardBody([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop your file here or ',
                    html.A('Browse', style={'color': '#17a2b8', 'fontWeight': 'bold', 'fontSize': '18px', 'textDecoration': 'underline'})
                ]),
                style={
                    'width': '100%', 'height': '80px', 'lineHeight': '80px',
                    'borderWidth': '2px', 'borderStyle': 'solid', 'borderColor': '#17a2b8',
                    'borderRadius': '5px', 'backgroundColor': '#ffffff', 'color': '#6c757d',
                    'textAlign': 'center', 'margin': '15px', 'fontSize': '18px',
                    'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)'
                },
                multiple=False
            ),
            html.Div(id='file-upload-status', style={'marginTop': '15px', 'fontSize': '16px'}),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Proceed to Data Quality Check", id="next-button-file", color="info", size="md", style={'width': '100%'}, href='/page-2')
                ], width=3),
            ], justify="center")
        ])
    ])
])


@app.callback(
    Output('file-upload-status', 'children'),  # 显示文件上传状态的输出组件
    Input('upload-data', 'contents'),  # 输入文件内容
    State('upload-data', 'filename'),  # 输入文件名
    State('upload-data', 'last_modified')  # 输入文件最后修改时间
)
def update_output(contents, filename, last_modified):
    if contents is not None:
        content_type, content_string = contents.split(',')
        
        # 解码文件内容
        decoded = base64.b64decode(content_string)
        
        try:
            # 检查文件类型并读取文件内容
            if filename.endswith('.csv'):
                # 读取CSV文件
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif filename.endswith('.xlsx'):
                # 读取Excel文件
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                # 如果文件类型不支持，返回错误信息
                return html.Div(['File format not supported，please upload csv or xlsx file'])
            
            # 如果文件读取成功，显示文件信息
            return html.Div([
                html.H5(f"File {filename} uploaded！"),
                dash_table.DataTable(
                    data=df.head().to_dict('records'),  # 显示数据表的前几行
                    columns=[{'name': i, 'id': i} for i in df.columns],
                    style_table={'overflowX': 'auto'}
                )
            ])
        except Exception as e:
            # 如果发生错误，打印错误信息并返回错误信息
            print(f"Error reading file: {e}")
            return html.Div(['File read failed，please check for the file format.'])
    
    # 如果文件尚未上传，显示提示
    return html.Div(['File not uploaded.'])


# Manual input section layout with logo image
manual_input_layout = dbc.Container([
    html.Img(
        src='./teamlogo.png',
        style={
            'position': 'absolute',
            'top': '10px',
            'right': '10px',
            'width': '100px',  # 控制图片宽度
            'height': 'auto'   # 保持图片比例
        }
    ),
    dbc.Card([
        dbc.CardHeader(html.H2("Manual Data Input", style={
            'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '28px', 'padding': '20px',
            'backgroundColor': '#f8f9fa', 'borderBottom': '2px solid #66A3C2'  
        })),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H5("Region", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='region-input', type='text', placeholder="Enter Region", 
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
                dbc.Col([
                    html.H5("Building Name", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='building-input', type='text', placeholder="Enter Building Name", 
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    html.H5("Year", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='year-input', type='number', placeholder="Enter Year",
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    html.H5("Latitude", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='latitude-input', type='number', placeholder="Enter Latitude", 
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
                dbc.Col([
                    html.H5("Longitude", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='longitude-input', type='number', placeholder="Enter Longitude", 
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    html.H5("Address", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='address-input', type='text', placeholder="Enter Address", 
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=12),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    html.H5("Type of Function (Building)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='type-function-input', type='text', placeholder="Enter Building Function Type", 
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
                dbc.Col([
                    html.H5("Size", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Dropdown(
                        id='size-input',
                        options=[
                            {'label': 'Large', 'value': 'Large'},
                            {'label': 'Medium', 'value': 'Medium'},
                            {'label': 'Small', 'value': 'Small'}
                        ],
                        placeholder="Select Size",
                        style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}
                    ),
                ], width=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    html.H5("Number of Employees", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='employee-input', type='number', placeholder="Enter Number of Employees", 
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
                dbc.Col([
                    html.H5("Transportation (CO2 Emissions in kg)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='transportation-input', type='number', placeholder="Enter Transportation CO2 Emissions", 
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    html.H5("Gross Floor Area (GFA in m²)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='gfa-input', type='number', placeholder="Enter GFA", 
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
                dbc.Col([
                    html.H5("Energy (in kWh)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='energy-input', type='number', placeholder="Enter Energy Consumption", 
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    html.H5("Waste (in kg)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='waste-input', type='number', placeholder="Enter Waste Generated", 
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
                dbc.Col([
                    html.H5("Water (in m³)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='water-input', type='number', placeholder="Enter Water Consumption", 
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    html.H5("Scope 1 Emissions", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='scope1-input', type='number', placeholder="Enter Scope 1 emissions", 
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                    dbc.Tooltip("Direct emissions from owned or controlled sources.", target='scope1-input')
                ], width=4),
                dbc.Col([
                    html.H5("Scope 2 Emissions", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='scope2-input', type='number', placeholder="Enter Scope 2 emissions", 
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                    dbc.Tooltip("Indirect emissions from the generation of purchased electricity.", target='scope2-input')
                ], width=4),
                dbc.Col([
                    html.H5("Scope 3 Emissions", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='scope3-input', type='number', placeholder="Enter Scope 3 emissions", 
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                    dbc.Tooltip("All other indirect emissions that occur in the value chain.", target='scope3-input')
                ], width=4),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Proceed to Data Quality Check", id="next-button", color="info", className="mr-2", 
                               style={'fontSize': '16px', 'padding': '10px 20px', 'width': '100%'}, href='page-2')
                ], width=3),
            ], justify="center")  # Center button
        ])
    ], className="mb-5", style={
        'backgroundColor': '#ffffff', 
        'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.1)',
        'padding': '20px'  # 内边距，避免紧贴边缘
    })
], fluid=True)  # 将Container设为流体布局，适配不同屏幕




# Define layout for Page 2 - Data Quality Check and EDA
page_2_layout = dbc.Container([
    dbc.NavbarSimple(
        brand="Data Quality Check and EDA",
        brand_href="/page-2",
        color="primary",
        dark=True,
        className="mb-5"
    ),
    dbc.Row([
        dbc.Col(html.H1("Data Quality Check and Exploratory Data Analysis", className="text-center"), className="mb-5 mt-5")
    ]),
    dbc.Row([
        dbc.Col(html.Div(id="eda-output", className="mt-4")),
    ]),
    dbc.Row([
        dbc.Col([
            html.H5("Visualization of Data Completeness"),
            dcc.Graph(id='completeness-graph'),
        ]),
    ], className="mt-5"),
    dbc.Row([
        dbc.Col([
            html.H5("Data Table Overview"),
            dash_table.DataTable(id='data-table', style_table={'overflowX': 'auto'})
        ])
    ], className="mt-4"),
    dbc.Row([
        dbc.Col([
            dbc.Button("Re-upload Data", id="reupload-button", color="warning", href='/page-1'),
            dbc.Button("Next: Model Running and Comparison", id="next-model-button", color="primary", href='/page-3', className="ml-2")
        ], width=6),
    ])
])



df = pd.read_csv('./merged_df1.csv', encoding="utf-8", encoding_errors='ignore')
df['YearDate'] = pd.to_datetime(df['Year'].astype('str') + '-01-01')


# Define layout for Page 3 - Model Running and Visualization
page_3_layout = dbc.Container([
    dbc.NavbarSimple(
        brand="Model Results and Benchmarking",
        brand_href="/page-3",
        color="primary",
        dark=True,
        className="mb-5"
    ),
    dbc.Row([
        dbc.Col(html.H1("Model Results and Benchmarking", className="text-center"), className="mb-5 mt-5")
    ]),
    dcc.Dropdown(id='dropdown-selection', options=[{'label': name, 'value': name} for name in df["Building Name"].unique()], value='Building Name'),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='award'),
        ], width=6),
        dbc.Col([
            dcc.Graph(id='year_trend_line'),
        ], width=6),
    ], className="mt-5"),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='violin'),
        ], width=6),
        dbc.Col([
            dcc.Graph(id='pie_1'),
        ], width=3),
        dbc.Col([
            dcc.Graph(id='pie_2'),
        ], width=3),
    ], className="mt-5"),
    dbc.Row([
        dbc.Col([
            dbc.Button("Next: Generate Report", id="next-report-button", color="primary", href='/page-4')
        ], width=4),
    ])
])


# Callbacks for the visualizations on Page 3

# Line Chart
@app.callback(
    Output('year_trend_line', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_line_chart(value):
    year_trend_df = df.groupby('YearDate').agg({'GHG_Intensity': 'mean'}).reset_index()
    fig = px.line(year_trend_df, x='YearDate', y='GHG_Intensity', title="Greenhouse Gas Emissions Intensity Over Time",
                  labels={"GHG_Intensity": "Greenhouse Gas Emissions Intensity"})
    fig.update_traces(line=dict(color="#365E32"))
    return fig

# Bubble Chart
@app.callback(
    Output('award', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_bubble_chart(value):
    bubble_data = df.groupby('Award').agg(unique_building_count=('Building Name', 'nunique')).reset_index()
    x = [0, 1, 2, 3]
    y = [2, 2, 2, 2]
    bubble_data['x'] = x
    bubble_data['y'] = y
    fig = go.Figure(data=[go.Scatter(
        x=x, y=y, mode='markers+text',
        marker=dict(size=bubble_data["unique_building_count"], opacity=0.6, color="#365E32"),
        text=bubble_data["Award"],
        textposition="top center",
        hovertext=bubble_data["unique_building_count"]
    )])
    fig.update_layout(title="Awards Distribution", showlegend=False,
                      xaxis=dict(showgrid=False, showline=False, zeroline=False, visible=False),
                      yaxis=dict(showgrid=False, showline=False, zeroline=False, visible=False))
    return fig

# Pie Chart - Scope Emissions
@app.callback(
    Output('pie_2', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_pie_scope(value):
    melt_cols = ['Building Name', "Scope1", "Scope2", "Scope3"]
    pie_data = pd.melt(df[melt_cols], id_vars='Building Name', var_name='key', value_name='value')
    pie_data = pie_data.groupby('key').agg({"value": 'sum'}).reset_index()
    fig = px.pie(pie_data, names='key', values='value', title="Scope Emissions Distribution",
                 color_discrete_map={'Scope1': '#365E32', 'Scope2': '#81A263', 'Scope3': '#E7D37F'})
    fig.update_traces(texttemplate='%{label}: %{percent:.2%}', textposition='outside')
    return fig

# Pie Chart - Water and Waste
@app.callback(
    Output('pie_1', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_pie_water_waste(value):
    melt_cols = ['Building Name', "Water", "Waste"]
    pie_data = pd.melt(df[melt_cols], id_vars='Building Name', var_name='key', value_name='value')
    pie_data = pie_data.groupby('key').agg({"value": 'sum'}).reset_index()
    fig = px.pie(pie_data, names='key', values='value', title="Water and Waste Distribution",
                 color_discrete_map={'Water': '#365E32', 'Waste': '#81A263'})
    fig.update_traces(texttemplate='%{label}: %{percent:.2%}', textposition='outside')
    return fig

# Violin Chart - GHG Intensity
@app.callback(
    Output('violin', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_violin_chart(value):
    melt_cols = ['Building Name', "GHG_Intensity"]
    h_data = df[melt_cols]
    fig = px.violin(h_data, x="GHG_Intensity", box=True, points='all', title="GHG Intensity Violin Plot",
                    labels={"GHG_Intensity": "Greenhouse Gas Emissions Intensity"})
    fig.update_traces(marker=dict(color="green"))
    return fig



# Define layout for Page 4 - Report Generation and Chatbot
page_4_layout = dbc.Container([
    dbc.NavbarSimple(
        brand="Generate Report and Chat Assistance",
        brand_href="/page-4",
        color="primary",
        dark=True,
        className="mb-5"
    ),
    dbc.Row([
        dbc.Col(html.H1("Generate Report and Chat Assistance", className="text-center"), className="mb-5 mt-5")
    ]),
    dbc.Row([
    dbc.Col([
        html.H5("Generate HTML Report"),
        dbc.Button("Download HTML Report", id="report-button", color="secondary"),
        dcc.Download(id="download-report")
        ], width=4),
    ], className="mb-5"),
    dbc.Row([
        dbc.Col([
            html.H5("Chatbot Assistance"),
            dcc.Input(id='chatbot-input', type='text', placeholder="Ask a question about the report...", style={'width': '100%'}),
            html.Div(id='chatbot-response', className="mt-3")
        ], width=6),
    ])
])



# Combine callback to handle both navigation and method switching
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/page-2':
        return page_2_layout
    elif pathname == '/page-3':
        return page_3_layout
    elif pathname == '/page-4':
        return page_4_layout
    elif pathname == '/page-5':
        return page_5_layout
    else:
        return html.Div([
            dcc.RadioItems(
                id='input-method',
                options=[
                    {'label': 'Upload File', 'value': 'file'},
                    {'label': 'Manual Input', 'value': 'manual'}
                ],
                value='file',
                labelStyle={
                    'display': 'inline-block',
                    'margin-right': '50px',
                    'fontSize': '18px',
                    'fontWeight': '600',
                    'color': '#3a3a3a',
                    'cursor': 'pointer',
                    'padding': '10px 20px',
                    'backgroundColor': '#ffffff',
                    'borderRadius': '25px',
                    'border': '2px solid #dedede',
                    'transition': 'all 0.3s ease',
                },
                inputStyle={
                    'margin-right': '10px',
                    'transform': 'scale(1.1)',
                    'verticalAlign': 'middle',
                },
                style={
                    'textAlign': 'center',
                    'marginTop': '30px',
                    'marginBottom': '30px',
                    'padding': '20px',
                    'borderRadius': '15px',
                }
            ),
            html.Div(id='input-section')
        ])



# Callback to switch between file upload and manual input
@app.callback(
    Output('input-section', 'children'),
    [Input('input-method', 'value')]
)
def display_input_method(selected_method):
    if selected_method == 'file':
        return file_upload_layout
    elif selected_method == 'manual':
        return manual_input_layout

# Callback for generating the HTML report on Page 4
@app.callback(
    Output('download-report', 'data'),
    Input('report-button', 'n_clicks')
)
def generate_report(n_clicks):
    if n_clicks:
        try:
            # Static title for the report
            report_title = "ESG Performance Analysis Report"

            # Title section for HTML/PDF
            title_section = f"<h1 style='text-align:center;'>{report_title}</h1>"

            # Content for each report section
            executive_summary = """
            <h2>Executive Summary</h2>
            <p>This report provides a comprehensive analysis of greenhouse gas (GHG) emissions data, resource usage, and benchmarking based on the dataset uploaded to our platform. Key findings highlight patterns in emissions intensity over time, the breakdown of emissions by scope, and comparative benchmarking based on recognized certification levels.</p>
            """

            introduction = """
            <h2>Introduction to ESG Reporting Analysis</h2>
            <p><strong>Purpose of the Analysis</strong></p>
            <p>ESG reporting is increasingly critical for understanding the environmental impact and sustainability performance of organizations. This report leverages our platform’s analytics to provide a data-driven view of the submitted dataset, focusing on GHG emissions and resource management metrics.</p>
            
            <h2>Methodology</h2>
            <p><strong>Data Processing and Visualization</strong></p>
            <p>The uploaded dataset underwent several stages of processing, including data quality checks, normalization, and segmentation by relevant categories (e.g., certification levels, emissions scopes). For commuting data in Scope 3, we have regional factors to adjust your value.</p>
            
            <p><strong>Automated Analysis and Model Selection</strong></p>
            <p>This analysis was conducted through our platform’s advanced analytics, which includes an automated model selection process to identify the best statistical or machine learning model for your data type. By evaluating multiple models based on their fit and predictive accuracy, the platform ensures that each analysis component—such as trend detection, emissions distribution, and resource usage breakdown—is optimized for accuracy and relevance.</p>
            """

            scope_of_reporting = """
            <h2>Scope of Reporting</h2>
            <p><strong>Reporting Period</strong></p>
            <p>The analysis covers data entries from January 1, 2023, to December 31, 2023. All findings are based on the data within this timeframe, as provided in the uploaded dataset.</p>
            
            <p><strong>Data Boundaries</strong></p>
            <p>The dataset includes various entities, each contributing to the total emissions and resource metrics. This report reflects the aggregated and segmented data as processed by our platform, without further boundary restrictions or exclusions.</p>
            """

            performance_data_intro = """
            <h2>Performance Data</h2>
            <p>This section provides detailed insights derived from the GHG emissions and resource usage data.</p>
            """

            benchmark_intro = """
            <h2>Benchmark</h2>
            <p>The benchmarking section compares the entities based on certification or award levels to highlight how the dataset aligns with established standards.</p>
            """

            future_outlook = """
            <h2>Future Insights and Recommendations</h2>
            <p>Based on the analysis conducted through our platform, the following insights and recommendations can guide future actions:</p>
            <ul>
                <li><strong>Focus on High Emission Scopes</strong>: Entities or operations with high Scope 1, Scope 2, or Scope 3 emissions should be prioritized for reduction strategies, as identified in the scope distribution analysis.</li>
                <li><strong>Enhance Resource Efficiency</strong>: The water and waste distribution insights suggest potential areas for improving resource efficiency. Reducing waste generation and optimizing water usage can directly contribute to better sustainability outcomes.</li>
                <li><strong>Targeted Certification Improvement</strong>: For entities with lower certification levels, consider strategies to meet higher certification standards. This can enhance overall ESG performance and align with sustainability benchmarks.</li>
                <li><strong>Emissions Intensity Management</strong>: The observed GHG intensity trend over time highlights areas where emissions management may be improved. Continuous monitoring and mitigation efforts during high-intensity periods could further reduce the overall environmental footprint.</li>
            </ul>
            """

            # Generate and aggregate plots
            # Awards Distribution plot
            benchmark_data = df.groupby('Award').agg(unique_building_count=('Building Name', 'nunique')).reset_index()
            fig_awards = go.Figure(data=[go.Scatter(
                x=[0, 1, 2, 3], y=[2, 2, 2, 2], mode='markers+text',
                marker=dict(size=benchmark_data["unique_building_count"], opacity=0.6, color="#365E32"),
                text=benchmark_data["Award"],
                textposition="top center",
                hovertext=benchmark_data["unique_building_count"]
            )])
            fig_awards.update_layout(title="Awards Distribution", showlegend=False,
                                     xaxis=dict(showgrid=False, showline=False, zeroline=False, visible=False),
                                     yaxis=dict(showgrid=False, showline=False, zeroline=False, visible=False))
            awards_plot_html = fig_awards.to_html(full_html=False, include_plotlyjs='cdn')

            # Performance Data plot (Aggregated GHG Intensity over time)
            year_trend_df = df.groupby('YearDate').agg({'GHG_Intensity': 'mean'}).reset_index()
            fig_performance = px.line(
                year_trend_df,
                x='YearDate',
                y='GHG_Intensity',
                title="Average Greenhouse Gas Emissions Intensity Over Time",
                labels={"GHG_Intensity": "Average GHG Intensity"}
            )
            fig_performance.update_traces(line=dict(color="#365E32"))
            performance_plot_html = fig_performance.to_html(full_html=False, include_plotlyjs='cdn')

            # GHG Intensity Violin Plot (under Benchmark)
            fig_violin = px.violin(df, x="GHG_Intensity", box=True, points='all', title="GHG Intensity Violin Plot",
                                   labels={"GHG_Intensity": "Greenhouse Gas Emissions Intensity"})
            fig_violin.update_traces(marker=dict(color="green"))
            violin_plot_html = fig_violin.to_html(full_html=False, include_plotlyjs='cdn')

            # Water and Waste Distribution Plot (under Performance Data)
            pie_data_ww = pd.melt(df[['Building Name', 'Water', 'Waste']], id_vars='Building Name', var_name='key', value_name='value')
            pie_data_ww = pie_data_ww.groupby('key').agg({"value": 'sum'}).reset_index()
            fig_water_waste = px.pie(pie_data_ww, names='key', values='value', title="Water and Waste Distribution")
            fig_water_waste.update_traces(texttemplate='%{label}: %{percent:.2%}', textposition='outside')
            water_waste_plot_html = fig_water_waste.to_html(full_html=False, include_plotlyjs='cdn')

            # Scope Emissions Distribution Plot (under Performance Data)
            pie_data_scope = pd.melt(df[['Building Name', 'Scope1', 'Scope2', 'Scope3']], id_vars='Building Name', var_name='key', value_name='value')
            pie_data_scope = pie_data_scope.groupby('key').agg({"value": 'sum'}).reset_index()
            fig_scope_emissions = px.pie(pie_data_scope, names='key', values='value', title="Scope Emissions Distribution")
            fig_scope_emissions.update_traces(texttemplate='%{label}: %{percent:.2%}', textposition='outside')
            scope_emissions_plot_html = fig_scope_emissions.to_html(full_html=False, include_plotlyjs='cdn')

            # Generate report based on the selected format
            report_html = f"""
            <html>
                    <body>
                    <!-- Logo at the top of the report -->
                    <div style="text-align: center; margin-bottom: 20px;">
                    <img src="./assets/teamlogo.png" alt="Company Logo" style="width: 200px; height: auto;">
                    </div>
                        {title_section}
                        {executive_summary}
                        {introduction}
                        {scope_of_reporting}
                        {performance_data_intro}
                        {performance_plot_html}
                        {water_waste_plot_html}
                        {scope_emissions_plot_html}
                        {benchmark_intro}
                        {awards_plot_html}
                        {violin_plot_html}
                        {future_outlook}
                    </body>
                </html>
                """
            with open('report.html', 'w') as f:
                f.write(report_html)
            return dcc.send_file('report.html')
        except Exception as e:
            print(f"Error during report generation: {e}")
            return None
            


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
