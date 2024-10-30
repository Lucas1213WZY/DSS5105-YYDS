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
        src='/assets/teamlogo.png',
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
# Manual input section layout with logo image and added container for padding
manual_input_layout = dbc.Container([
    html.Img(
        src='/assets/teamlogo.png',
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
    dbc.Row([
        dbc.Col([
            html.H5("Model Results Visualization"),
            dcc.Graph(id='model-results-graph'),
        ]),
    ], className="mt-5"),
    dbc.Row([
        dbc.Col([
            html.H5("Scope 1 Emissions Breakdown"),
            dcc.Graph(id='scope1-pie-chart')
        ], width=4),
        dbc.Col([
            html.H5("Scope 2 Emissions Breakdown"),
            dcc.Graph(id='scope2-pie-chart')
        ], width=4),
        dbc.Col([
            html.H5("Scope 3 Emissions Breakdown"),
            dcc.Graph(id='scope3-pie-chart')
        ], width=4),
    ], className="mt-5"),
    dbc.Row([
        dbc.Col([
            html.H5("Benchmarking Visualization"),
            dcc.Graph(id='benchmarking-graph', figure=px.bar(pd.DataFrame({
                'Building': ['Building A', 'Building B', 'Building C'],
                'Emissions Intensity': [120, 150, 110]
            }), x='Building', y='Emissions Intensity', title="Emissions Intensity Benchmarking"))
        ])
    ], className="mt-5"),
    dbc.Row([
        dbc.Col([
            dbc.Button("Next: Generate Report", id="next-report-button", color="primary", href='/page-4')
        ], width=4),
    ])
])

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
            html.H5("Generate Report"),
            dbc.Button("Download Report", id="report-button", color="secondary"),
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

# Define layout for Page 5 - Geospatial Analysis
page_5_layout = dbc.Container([
    dbc.NavbarSimple(
        brand="Geospatial Analysis of Buildings",
        brand_href="/page-5",
        color="primary",
        dark=True,
        className="mb-5"
    ),
    dbc.Row([
        dbc.Col(html.H1("Geospatial Analysis of Buildings", className="text-center"), className="mb-5 mt-5")
    ]),
    dbc.Row([
        dbc.Col([
            html.H5("Building Locations on Map"),
            dl.Map(center=[1.3521, 103.8198], zoom=12, children=[
                dl.TileLayer(),
                dl.LayerGroup(id="layer-group")
            ], style={'width': '100%', 'height': '500px', 'margin': "auto", "display": "block"})
        ])
    ], className="mt-5"),
    dbc.Row([
        dbc.Col([
            dbc.Button("Back to Data Upload", id="back-upload-button", color="primary", href='/page-1')
        ], width=4),
    ])
])


# Combine callback to handle both navigation and method switching
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/page-2':
        return page_2_layout
    elif pathname == '/page-3':
        return page_3_layout
    else:
        # Default to file upload layout (with logo)
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


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
