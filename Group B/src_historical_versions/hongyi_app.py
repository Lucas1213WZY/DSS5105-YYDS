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
import openai

# Initialize the OpenAI client
openai.api_key = "sk-svcacct-yirqs5Y1sVriNR6qGBs7ZSSRhXZd-uvMQdebTequv5z2oAy6rjhnnSQ_B6740T3BlbkFJyk98lfvPOiui5GB-FMMIMLWA8UY4bkO30YxytnTW8X505TFJmXIgswzK0sFAA"


# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY], suppress_callback_exceptions=True)
server = app.server

# Sidebar layout
sidebar = html.Div(
    [
        dcc.Link("Data Input", href="/page-1", style={
            "display": "block",
            "color": "white",
            "padding": "12px 20px",
            "textDecoration": "none",  # No underline
            "font-size": "18px",
            "font-weight": "bold",
            "border-radius": "5px",
        }),
        dcc.Link("Data Quality Check and Exploratory Data Analysis", href="/page-2", style={
            "display": "block",
            "color": "white",
            "padding": "12px 20px",
            "textDecoration": "none",
            "font-size": "18px",
            "font-weight": "bold",
            "border-radius": "5px",
        }),
        dcc.Link("Model Results and Benchmarking", href="/page-3", style={
            "display": "block",
            "color": "white",
            "padding": "12px 20px",
            "textDecoration": "none",
            "font-size": "18px",
            "font-weight": "bold",
            "border-radius": "5px",
        }),
        dcc.Link("Report and Chatbox", href="/page-4", style={
            "display": "block",
            "color": "white",
            "padding": "12px 20px",
            "textDecoration": "none",
            "font-size": "18px",
            "font-weight": "bold",
            "border-radius": "5px",
        }),
    ],
    id="sidebar",
    style={
        "padding": "15px",
        "background-color": "#333",
        "color": "white",
        "width": "220px",
        "height": "100vh",
        "position": "fixed",
        "left": "0",
        "top": "0",
        "overflow": "auto",
        "transform": "translateX(-100%)",  # Initially hidden
        "transition": "transform 0.3s ease",  # Smooth transition
        "box-shadow": "2px 0 8px rgba(0, 0, 0, 0.3)",  # Adds shadow for depth
        "border-radius": "0 8px 8px 0",  # Rounds right-side corners
    }
)


# Button to toggle the sidebar
toggle_button = html.Button("☰", id="toggle-button", style={
    "position": "absolute",
    "top": "40px",
    "left": "20px",
    "z-index": "1",
    "padding": "10px",
    "font-size": "24px",
    "background-color": "#2C7A7B",
    "color": "white",
    "border": "none",
    "border-radius": "8px",  # Rounded corners
    "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.2)",  # Subtle shadow
    "cursor": "pointer",
    "transition": "all 0.3s ease",  # Smooth hover transition
})

# Adding hover effect through inline CSS for a slightly darker background on hover
toggle_button_style_hover = {
    "background-color": "#285e5e",
}


# Callback to toggle the sidebar and adjust main content margin
@app.callback(
    [Output("sidebar", "style"), Output("main-content", "style"), Output("toggle-button", "style")],
    [Input("toggle-button", "n_clicks")],
    [State("sidebar", "style"), State("main-content", "style"), State("toggle-button", "style")]
)
def toggle_sidebar(n_clicks, sidebar_style, main_content_style, toggle_button_style):
    if n_clicks and sidebar_style["transform"] == "translateX(-100%)":
        # Show sidebar and adjust toggle button position to stay to the right of the sidebar
        sidebar_style["transform"] = "translateX(0)"
        main_content_style["margin-left"] = "200px"  # Adjust for sidebar width
        toggle_button_style["left"] = "220px"  # Place button to the right of the sidebar
    else:
        # Hide sidebar and reset toggle button position
        sidebar_style["transform"] = "translateX(-100%)"
        main_content_style["margin-left"] = "0px"
        toggle_button_style["left"] = "20px"  # Reset button to the original position
    return sidebar_style, main_content_style, toggle_button_style


@app.callback(
    Output("logo-wrapper", "style"),
    [Input("toggle-button", "n_clicks")],
    [State("logo-wrapper", "style")]
)
def adjust_logo_position(n_clicks, current_style):
    if n_clicks and n_clicks % 2 != 0:  # Sidebar is visible
        # Shift logo further to the right
        current_style["right"] = "0px"  # Adjust to match sidebar width
    else:
        # Reset logo position when sidebar is hidden
        current_style["right"] = "40px"
    return current_style

@app.callback(
    Output("manual-logo-wrapper", "style"),
    [Input("toggle-button", "n_clicks")],
    [State("manual-logo-wrapper", "style")]
)
def adjust_logo_position(n_clicks, current_style):
    if n_clicks and n_clicks % 2 != 0:  # Sidebar is visible
        # Shift logo further to the right
        current_style["right"] = "0px"  # Adjust to match sidebar width
    else:
        # Reset logo position when sidebar is hidden
        current_style["right"] = "40px"
    return current_style


# Main layout
app.layout = html.Div([
        toggle_button,
        sidebar,
        html.Div(
            id="main-content",
            children=[
                html.Div(
                    dbc.Navbar(
                        [
                            dbc.NavbarBrand(
                                "GHG Emissions Calculator",
                                className="mx-auto",  # Center the title
                                style={
                                    "fontSize": "46px",
                                    "fontWeight": "bold",
                                    "color": "white",
                                    "padding": "10px",
                                },
                            ),
                        ],
                        color="success",
                        dark=True,
                        style={
                            "textAlign": "center",
                            "justifyContent": "center",
                            "padding": "20px",
                            "borderRadius": "8px",
                            "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.2)",
                        },
                    ),
                    style={
                        "textAlign": "center",
                        "marginTop": "20px",
                        "marginBottom": "30px",
                    },
                ),
                dcc.Location(id="url", refresh=False),
                html.Div(id="page-content"),
            ],
            style={"padding": "20px", "transition": "margin-left 0.3s ease"},  # Smooth transition for margin
        ),
    ]
)


# File upload section layout
file_upload_layout = html.Div([
    html.Div(
        html.Img(
            src='./assets/teamlogo.png',
            style={
                'width': '220px',  # Adjust width as necessary
                'height': 'auto',
            }
        ),
        id="logo-wrapper",  # Add an ID to the wrapper for callback targeting
        style={
            'position': 'absolute',
            'top': '55px',
            'right': '40px',  # Increased 'right' value to move it further right
            'transition': 'right 0.3s ease'  # Add transition for smooth effect
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
                    dbc.Button("Proceed to Data Quality Check", id="next-button-file", color="success", size="md", className="mt-4",
                               style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'fontWeight': 'bold'}, href='/page-2')
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
singapore_regions = [
    {'label': 'Geylang', 'value': 'Geylang'},
    {'label': 'Queenstown', 'value': 'Queenstown'},
    {'label': 'Museum', 'value': 'Museum'},
    {'label': 'Downtown Core', 'value': 'Downtown Core'},
    {'label': 'Outram', 'value': 'Outram'},
    {'label': 'Marine Parade', 'value': 'Marine Parade'},
    {'label': 'Ang Mo Kio', 'value': 'Ang Mo Kio'},
    {'label': 'Bukit Batok', 'value': 'Bukit Batok'},
    {'label': 'Jurong East', 'value': 'Jurong East'},
    {'label': 'Hougang', 'value': 'Hougang'},
    {'label': 'Woodlands', 'value': 'Woodlands'},
    {'label': 'Singapore River', 'value': 'Singapore River'},
    {'label': 'Tampines', 'value': 'Tampines'},
    {'label': 'Orchard', 'value': 'Orchard'},
    {'label': 'Western Water Catchment', 'value': 'Western Water Catchment'},
    {'label': 'Toa Payoh', 'value': 'Toa Payoh'},
    {'label': 'Jurong West', 'value': 'Jurong West'},
    {'label': 'Changi', 'value': 'Changi'},
    {'label': 'Bedok', 'value': 'Bedok'},
    {'label': 'Newton', 'value': 'Newton'},
    {'label': 'Kallang', 'value': 'Kallang'},
    {'label': 'Tanglin', 'value': 'Tanglin'},
    {'label': 'Rochor', 'value': 'Rochor'},
    {'label': 'Bukit Merah', 'value': 'Bukit Merah'},
    {'label': 'Bukit Timah', 'value': 'Bukit Timah'},
    {'label': 'Bishan', 'value': 'Bishan'},
    {'label': 'Choa Chu Kang', 'value': 'Choa Chu Kang'},
    {'label': 'Novena', 'value': 'Novena'},
    {'label': 'Bukit Panjang', 'value': 'Bukit Panjang'},
    {'label': 'River Valley', 'value': 'River Valley'},
    {'label': 'Clementi', 'value': 'Clementi'},
    {'label': 'Sengkang', 'value': 'Sengkang'},
    {'label': 'Southern Islands', 'value': 'Southern Islands'},
    {'label': 'Yishun', 'value': 'Yishun'}
]

manual_input_layout = dbc.Container([
    html.Div(
        html.Img(
            src='./assets/teamlogo.png',
            style={
                'width': '220px',
                'height': 'auto',
            }
        ),
        id="manual-logo-wrapper",
        style={
            'position': 'absolute',
            'top': '55px',
            'right': '40px',
            'transition': 'right 0.3s ease'
        }
    ),
    dbc.Card([
        dbc.CardHeader(html.H2("Manual Data Input", style={
            'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '28px', 'padding': '20px',
            'backgroundColor': '#f8f9fa', 'borderBottom': '2px solid #66A3C2'
        })),
        dbc.CardBody([
            # Building Info Section
            dbc.Card([
                dbc.CardHeader(html.H4("Building Info Data", style={'fontWeight': 'bold', 'fontSize': '22px', 'color': '#343a40'}),
                               style={'backgroundColor': '#f5f5f5'}),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H5("Region", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                            dcc.Dropdown(
                                id='region-dropdown',
                                options=singapore_regions,
                                placeholder="Select a Region",
                                style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}
                            )
                        ], width=6),
                        dbc.Col([
                            html.H5("Building Name", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                            dcc.Input(id='building-input', type='text', placeholder="Enter Building Name",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                        ], width=6),
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.H5("Zip Code", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                            dcc.Input(id='zip-input', type='number', placeholder="Enter Zip Code",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                        ], width=6),
                        dbc.Col([
                            html.H5("Year", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                            dcc.Input(id='year-input', type='number', placeholder="Enter Year",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                        ], width=6),
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.H5("Size (sqft)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                            dcc.Input(id='size-input', type='number', placeholder="Enter Building Size",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                        ], width=6),
                        dbc.Col([
                            html.H5("Number of Employees", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                            dcc.Input(id='employee-input', type='number', placeholder="Enter Number of Employees",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                        ], width=6),
                    ], className="mb-4"),
                ])
            ], className="mb-4", style={'border': '1px solid #ced4da', 'borderRadius': '10px', "box-shadow": "2px 0 8px rgba(0, 0, 0, 0.3)"}),

            # Emission Info Section
            dbc.Card([
                dbc.CardHeader(html.H4("Emission Data", style={'fontWeight': 'bold', 'fontSize': '22px', 'color': '#343a40'}),
                                style={'backgroundColor': '#f5f5f5'}),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H5("Energy (in kWh)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                            dcc.Input(id='energy-input', type='number', placeholder="Enter Energy Consumption",
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
                            html.H5("Waste (in t)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                            dcc.Input(id='waste-input', type='number', placeholder="Enter Waste Generated",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                        ], width=6),
                    ], className="mb-4"),
                ])
            ], className="mb-4", style={'border': '1px solid #ced4da', 'borderRadius': '10px', "box-shadow": "2px 0 8px rgba(0, 0, 0, 0.3)"}),

            # Transportation Section
            dbc.Card([
                dbc.CardHeader(html.H4("Transportation Data", style={'fontWeight': 'bold', 'fontSize': '22px', 'color': '#343a40'}),
                                style={'backgroundColor': '#f5f5f5'}),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H5("Subway/MRT Commute (km * people)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                            dcc.Input(id='subway-commute-input', type='number', placeholder="Enter distance (km)",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                        ], width=6),
                        dbc.Col([
                            html.H5("Bus Commute (km * people)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                            dcc.Input(id='bus-commute-input', type='number', placeholder="Enter distance (km)",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                        ], width=6),
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.H5("Taxi/Private Car Commute (km * people)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
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
                            html.H5("Procurement with Air Freight (t * km)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                            dcc.Input(id='business-procurement-air-freight-input', type='number', placeholder="Enter weight/volume",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                        ], width=6),
                        dbc.Col([
                            html.H5("Procurement with Diesel Truck Freight (t * km)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                            dcc.Input(id='business-procurement-diesel-truck-input', type='number', placeholder="Enter weight/volume",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                        ], width=6),
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.H5("Procurement with Electric Truck Freight (t * km)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                            dcc.Input(id='business-procurement-electric-truck-input', type='number', placeholder="Enter weight/volume",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                        ], width=6),
                    ], className="mb-4"),
                ])
            ], className="mb-4", style={'border': '1px solid #ced4da', 'borderRadius': '10px', "box-shadow": "2px 0 8px rgba(0, 0, 0, 0.3)"}),

            dbc.Row([
                dbc.Col([
                    dbc.Button("Proceed to Data Quality Check", id="next-button", color="success", className="mt-4",
                               style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'fontWeight': 'bold'}, href='page-2')
                ], width=3),
            ], justify="center")
        ])
    ], className="mb-5", style={
        'backgroundColor': '#ffffff',
        'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.1)',
        'padding': '20px'
    })
], fluid=True)


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


# Define layout for Page 2 - Data Quality Check and EDA
page_2_layout = dbc.Container([

    # Main title, centered and bold, with margin to add space from navbar
    dbc.Row([
        dbc.Col(html.H1("Data Quality Check and Exploratory Data Analysis",
                        className="text-center",
                        style={"fontWeight": "bold", "marginTop": "20px", "marginBottom": "40px"}))
    ]),

    # Data Completeness Visualization Section
    dbc.Row([
        dbc.Col(html.H5("Data Completeness Visualization", className="text-left", style={"fontWeight": "600"})),
        dbc.Col(html.Hr(style={"borderTop": "1px solid #aaa", "width": "100%"}), width=12),
    ], className="mt-3 mb-2"),
    dbc.Row([
        dbc.Col(dcc.Graph(id='completeness-graph'), width=12),
    ], className="mb-5"),

    # Data Table Overview Section
    dbc.Row([
        dbc.Col(html.H5("Data Overview Table", className="text-left", style={"fontWeight": "600"})),
        dbc.Col(html.Hr(style={"borderTop": "1px solid #aaa", "width": "100%"}), width=12),
    ], className="mt-3 mb-2"),
    dbc.Row([
        dbc.Col(dash_table.DataTable(id='data-table', style_table={'overflowX': 'auto'}), width=12),
    ], className="mb-5"),

    # Buttons for navigation with centered alignment
    dbc.Row([
        dbc.Col([
            dbc.Button("Re-upload Data", id="reupload-button", color="warning", href='/page-1',
                       style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'fontWeight': 'bold'}),
        ], width=3),
        dbc.Col([
            dbc.Button("Next: Model Running and Comparison", id="next-model-button", color="success", href='/page-3',
                       style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'fontWeight': 'bold'}),
        ], width=3),
    ], justify="center", className="mt-4 mb-5"),
], fluid=True)


df = pd.read_csv('./merged_df1.csv', encoding="utf-8", encoding_errors='ignore')
df['YearDate'] = pd.to_datetime(df['Year'].astype('str') + '-01-01')


# Define layout for Page 3 - Model Running and Visualization
page_3_layout = dbc.Container([
    # Main title for Model Results and Benchmarking
    dbc.Row([
        dbc.Col(html.H1("Model Results and Benchmarking",
                        className="text-center",
                        style={"fontWeight": "bold", "marginTop": "20px", "marginBottom": "40px"}))
    ]),

    # Dropdown for selecting building names
    dbc.Row([
        dbc.Col(html.H5("Select Building Name", style={"fontWeight": "600"})),
        dbc.Col(html.Hr(style={"borderTop": "1px solid #aaa", "width": "100%"}), width=12),
    ], className="mt-3 mb-2"),
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id='dropdown-selection',
            options=[{'label': name, 'value': name} for name in df["Building Name"].unique()],
            value='Building Name',
            style={"width": "100%"}
        ), width=6),
    ], className="mb-5"),

    # Section for Award and Year Trend Graphs
    dbc.Row([
        dbc.Col(html.H5("Model Results Visualizations", style={"fontWeight": "600"})),
        dbc.Col(html.Hr(style={"borderTop": "1px solid #aaa", "width": "100%"}), width=12),
    ], className="mt-3 mb-2"),
    dbc.Row([
        dbc.Col(dcc.Graph(id='award'), width=6),
        dbc.Col(dcc.Graph(id='year_trend_line'), width=6),
    ], className="mb-5"),

    # Section for Additional Graphs
    dbc.Row([
        dbc.Col(html.H5("Additional Analysis", style={"fontWeight": "600"})),
        dbc.Col(html.Hr(style={"borderTop": "1px solid #aaa", "width": "100%"}), width=12),
    ], className="mt-3 mb-2"),
    dbc.Row([
        dbc.Col(dcc.Graph(id='violin'), width=6),
        dbc.Col(dcc.Graph(id='pie_1'), width=3),
        dbc.Col(dcc.Graph(id='pie_2'), width=3),
    ], className="mb-5"),

    # Button to navigate to the next page
    dbc.Row([
        dbc.Col([
            dbc.Button("Next: Generate Report", id="next-report-button", color="success", href='/page-4',
                       style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'fontWeight': 'bold'}),
        ], width=3),
    ], justify="center", className="mt-4 mb-5"),
], fluid=True)

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
    dbc.Row([
        dbc.Col(html.H1("Generate Report and Chat Assistance",
                        className="text-center",
                        style={"fontWeight": "bold", "marginTop": "20px", "marginBottom": "40px"}))
    ]),
    dbc.Row([
        dbc.Col([
            html.H5("Generate Report"),
            dcc.Dropdown(
                id='report-format',
                options=[
                    {'label': 'HTML', 'value': 'html'},
                    {'label': 'PDF', 'value': 'pdf'},
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
            html.H5("Chatbot Assistance", className="mb-3"),
            html.Div([
                dcc.Input(id='chatbot-input', type='text', placeholder="Ask a question about the report...", style={
                    'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'border': '1px solid #ced4da', 'marginBottom': '10px'
                }),
                html.Button('Send', id='send-button', n_clicks=0, style={
                    'backgroundColor': '#17a2b8', 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'padding': '8px 16px', 'marginBottom': '10px'
                })
            ], style={'display': 'flex', 'gap': '10px', 'flexDirection': 'column'}),
            html.Div(id='chatbot-response', className="mt-3", style={
                'color': 'gray', 'border': '1px solid #e9ecef', 'borderRadius': '5px', 'padding': '15px', 'backgroundColor': '#f8f9fa'
            })
        ], width=6),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button("Home", id="home-button", color="success", href='/page-1', className="mt-4", style={
                'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'fontWeight': 'bold'
            })
        ], width=3),
    ], className="mt-5 mb-5")  # Add 'mb-5' to create extra space at the bottom
])


# Function to get chatbot response
def get_chatbot_response(user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"Error: {e}"


# Callback for chatbot response
@app.callback(
    Output('chatbot-response', 'children'),
    Input('send-button', 'n_clicks'),
    State('chatbot-input', 'value')
)
def update_chatbot_response(n_clicks, user_input):
    if n_clicks > 0 and user_input:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant specialized in GHG emissions."},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=150,
                temperature=0.7
            )
            generated_response = response.choices[0].message.content.strip()
            return html.Div(generated_response, style={
                'color': 'gray', 'border': '1px solid #e9ecef', 'borderRadius': '5px',
                'padding': '15px', 'backgroundColor': '#f8f9fa'
            })
        except Exception as e:
            return html.Div(f"Error: {str(e)}", style={
                'color': 'red', 'border': '1px solid #e9ecef', 'borderRadius': '5px',
                'padding': '15px', 'backgroundColor': '#f8f9fa'
            })
    return ""



# generate report
@app.callback(
    Output('download-report', 'data'),
    Input('report-button', 'n_clicks')
)


def generate_report(n_clicks):
    if n_clicks:
        try:
            # Static title for the report
            report_title = "ESG Performance Analysis Report"

            # Title section with logo for HTML/PDF
            logo_section = f"<div style='text-align:center;'><src='assests/teamlogo.png' style='width:220px;'></div>"
            title_section = f"{logo_section}<h1 style='text-align:center;'>ESG Performance Analysis Report</h1>"

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
                    <img src='/assets/teamlogo.png' alt="Company Logo" style="width: 220px; height: auto;">
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

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
