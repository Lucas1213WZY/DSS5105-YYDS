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
            'width': '500px',  
            'height': 'auto'
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
    Output('file-upload-status', 'children'),  
    Input('upload-data', 'contents'),  
    State('upload-data', 'filename'),  
    State('upload-data', 'last_modified')  
)
def update_output(contents, filename, last_modified):
    if contents is not None:
        content_type, content_string = contents.split(',')
    
        decoded = base64.b64decode(content_string)
        
        try:
            
            if filename.endswith('.csv'):
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                return html.Div(['File format not supported，please upload csv or xlsx file'])
            
            return html.Div([
                html.H5(f"File {filename} uploaded！"),
                dash_table.DataTable(
                    data=df.head().to_dict('records'),  
                    columns=[{'name': i, 'id': i} for i in df.columns],
                    style_table={'overflowX': 'auto'}
                )
            ])
        except Exception as e:
            print(f"Error reading file: {e}")
            return html.Div(['File read failed，please check for the file format.'])
    
    return html.Div(['File not uploaded.'])


# Manual input section layout with logo image
manual_input_layout = dbc.Container([
    html.Img(
        src='./teamlogo.png',
        style={
            'position': 'absolute',
            'top': '10px',
            'right': '10px',
            'width': '100px',  
            'height': 'auto'   
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
                    html.H5("Subway/MRT Commute (km for 8 people)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='subway-commute-input', type='number', placeholder="Enter distance (km)",
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
                dbc.Col([
                    html.H5("Bus Commute (km for 8 people)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='bus-commute-input', type='number', placeholder="Enter distance (km)",
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    html.H5("Taxi/Private Car Commute (km for 8 people)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='taxi-commute-input', type='number', placeholder="Enter distance (km)",
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    html.H5("Business Travel (Flight, $SDG/year)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='business-travel-flight-input', type='number', placeholder="Enter amount in $SDG",
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
                dbc.Col([
                    html.H5("Business Travel (Hotel, $SDG/year)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='business-travel-hotel-input', type='number', placeholder="Enter amount in $SDG",
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    html.H5("Business Procurement (Air Freight)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='business-procurement-air-freight-input', type='number', placeholder="Enter weight/volume",
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
                dbc.Col([
                    html.H5("Business Procurement (Diesel Truck Freight)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='business-procurement-diesel-truck-input', type='number', placeholder="Enter weight/volume",
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    html.H5("Business Procurement (Electric Truck Freight)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                    dcc.Input(id='business-procurement-electric-truck-input', type='number', placeholder="Enter weight/volume",
                              style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                ], width=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Proceed to Data Quality Check", id="next-button", color="info", className="mr-2", 
                               style={'fontSize': '16px', 'padding': '10px 20px', 'width': '100%'}, href='page-2')
                ], width=3),
            ], justify="center")  
        ])
    ], className="mb-5", style={
        'backgroundColor': '#ffffff', 
        'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.1)',
        'padding': '20px'  
    })
], fluid=True) 




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
            html.H5("Generate Report"),
            # Dropdown for selecting report format
            dcc.Dropdown(
                id='report-format',
                options=[
                    {'label': 'HTML', 'value': 'html'},
                    {'label': 'PDF', 'value': 'pdf'},
                    {'label': 'Word (DOCX)', 'value': 'docx'}
                ],
                placeholder="Select Report Format",
                style={'width': '100%', 'margin-bottom': '20px'}
            ),
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

# generate report
@app.callback(
    Output('download-report', 'data'),
    [Input('report-button', 'n_clicks')],
    [State('report-format', 'value')]
)
def generate_report(n_clicks, report_format):
    if n_clicks:
        try:
            # Generate a blank HTML report
            if report_format == 'html':
                report_html = """
                <html>
                    <head><title>Blank Report</title></head>
                    <body><h1>Blank Report</h1><p>This is a placeholder for the report.</p></body>
                </html>
                """
                with open('report.html', 'w') as f:
                    f.write(report_html)
                return dcc.send_file('report.html')

            # Generate a blank PDF report
            elif report_format == 'pdf':
                report_html = """
                <html>
                    <head><title>Blank PDF Report</title></head>
                    <body><h1>Blank PDF Report</h1><p>This is a placeholder for the PDF report.</p></body>
                </html>
                """
                pdfkit.from_string(report_html, 'report.pdf')
                return dcc.send_file('report.pdf')

            # Generate a blank Word report
            elif report_format == 'docx':
                doc = docx.Document()
                doc.add_heading('Blank Word Report', 0)
                doc.add_paragraph("This is a placeholder for the Word report.")
                doc.save('report.docx')
                return dcc.send_file('report.docx')

        except Exception as e:
            print(f"Error during report generation: {e}")
            return None



# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
