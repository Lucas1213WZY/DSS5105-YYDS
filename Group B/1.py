import dash
from dash import dcc, html, Input, Output, State, callback, ctx
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
from dash import callback_context
import re
from dash.exceptions import PreventUpdate
from datetime import datetime

# Initialize the OpenAI client
openai.api_key = "sk-svcacct-yirqs5Y1sVriNR6qGBs7ZSSRhXZd-uvMQdebTequv5z2oAy6rjhnnSQ_B6740T3BlbkFJyk98lfvPOiui5GB-FMMIMLWA8UY4bkO30YxytnTW8X505TFJmXIgswzK0sFAA"


# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY, "https://use.fontawesome.com/releases/v5.8.1/css/all.css"], suppress_callback_exceptions=True)
server = app.server

# Sidebar layout
sidebar = html.Div(
    [
        # Main navigation links
        html.Div([
            dcc.Link("Data Input", href="/page-1", style={
                "display": "block",
                "color": "white",
                "padding": "12px 20px",
                "textDecoration": "none",
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
            dcc.Link("Feedback", href="/page-5", style={
                "display": "block",
                "color": "white",
                "padding": "12px 20px",
                "textDecoration": "none",
                "font-size": "18px",
                "font-weight": "bold",
                "border-radius": "5px",
            }),
        ], style={"marginBottom": "auto"}),  # Ensures other links are pushed to the bottom

        # Additional links at the bottom
        html.Div([
            dcc.Link("Q&A", href="/qa", style={
                "display": "block",
                "color": "white",
                "padding": "12px 20px",
                "textDecoration": "none",
                "font-size": "18px",
                "font-weight": "bold",
                "border-radius": "5px",
            }),
            dcc.Link("About Us", href="/about", style={
                "display": "block",
                "color": "white",
                "padding": "12px 20px",
                "textDecoration": "none",
                "font-size": "18px",
                "font-weight": "bold",
                "border-radius": "5px",
            }),
        ], style={"paddingTop": "20px"}),  # Add spacing above the bottom links
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
        "display": "flex",
        "flexDirection": "column",  # Enable column layout for vertical alignment
        "transform": "translateX(-100%)",
        "transition": "transform 0.3s ease",
        "box-shadow": "2px 0 8px rgba(0, 0, 0, 0.3)",
        "border-radius": "0 8px 8px 0",
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
                dcc.Location(id="url", refresh=True),
                html.Div(id="page-content"),
                dcc.Store(id="user-data", storage_type="session"),
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
                return html.Div(['File format not supported，please upload csv or xlsx file'], style={'color': 'red'})

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

style_with_error = {
    'width': '100%',
    'padding': '10px',
    'borderRadius': '10px',
    'borderColor': 'red',
    'borderStyle': 'solid',
    'borderWidth': '2px' 
}

style_without_error = {
    'width': '100%',
    'padding': '10px',
    'borderRadius': '10px',
    'border': '1px solid #ced4da'
}


manual_input_layout = dbc.Container([
    html.Div(
        html.Img(
            src='./assets/teamlogo.png',
            style={'width': '220px', 'height': 'auto'}
        ),
        id="manual-logo-wrapper",
        style={'position': 'absolute', 'top': '55px', 'right': '40px', 'transition': 'right 0.3s ease'}
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
                            html.Div([
                                html.H5("Region", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="region-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Dropdown(
                                id='region-dropdown',
                                options= singapore_regions,
                                placeholder="Select a Region",
                                style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}
                            )
                        ], width=6),
                        dbc.Tooltip(
                            "Select the region where your building is located.",
                            target="region-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        ),
                        dbc.Col([
                            html.Div([
                                html.H5("Building Name", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="building-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='building-input', type='text', placeholder="Enter Building Name",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'})
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the official name of your building.",
                            target="building-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        ),
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H5("Zip Code", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="zip-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='zip-input', type='number', placeholder="Enter Zip Code",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='zip-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'})  # Error message div
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the zip code/postal code of your building.",
                            target="zip-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        ),
                        dbc.Col([
                            html.Div([
                                html.H5("Year", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="year-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='year-input', type='number', placeholder="Enter Year",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='year-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'})  # Error message div
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the reference year for this data (e.g., 2022 for data collected in 2022).",
                            target="year-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        )
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H5("Size (sqft)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="size-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='size-input', type='number', placeholder="Enter Building Size",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='size-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'}) 
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the size of the building in sqft.",
                            target="size-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        ),
                        dbc.Col([
                            html.Div([
                                html.H5("Number of Employees", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="employees-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='employee-input', type='number', placeholder="Enter Number of Employees",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='employees-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'}) 
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the number of employees that work in the building.",
                            target="employees-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        )
                    ], className="mb-4")
                ])
            ], className="mb-4", style={'border': '1px solid #ced4da', 'borderRadius': '10px', "box-shadow": "2px 0 8px rgba(0, 0, 0, 0.3)"}),

            # Emission Info Section
           dbc.Card([
                dbc.CardHeader(html.H4("Emission Data", style={'fontWeight': 'bold', 'fontSize': '22px', 'color': '#343a40'}),
                               style={'backgroundColor': '#f5f5f5'}),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H5("Energy (in kWh)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="energy-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='energy-input', type='number', placeholder="Enter Energy Consumption",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='energy-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'}) 
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the total energy consumed by the building, measured in kilowatt-hours (kWh).",
                            target="energy-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        ),
                        dbc.Col([
                            html.Div([
                                html.H5("Water (in m³)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="water-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='water-input', type='number', placeholder="Enter Water Consumption",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='water-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'}) 
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the total water consumed by the building, measured in cubic meters (m³).",
                            target="water-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        ),
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H5("Waste (in t)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="waste-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='waste-input', type='number', placeholder="Enter Waste Generated",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='waste-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'}) 
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the total waste generated consumed the building, measuredin tons (t).",
                            target="waste-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        ),
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
                            html.Div([
                                html.H5("Subway/MRT Commute (km * people)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="subway-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='subway-commute-input', type='number', placeholder="Enter distance (km)",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='subway-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'}) 
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the total subway/MRT commute distance in km multiplied by the number of employees.",
                            target="subway-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        ),
                        dbc.Col([
                            html.Div([
                                html.H5("Bus Commute (km * people)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="bus-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='bus-commute-input', type='number', placeholder="Enter distance (km)",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='bus-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'}) 
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the total bus commute distance in km multiplied by the number of employees.",
                            target="bus-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        ),
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H5("Taxi/Private Car Commute (km * people)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="taxi-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='taxi-commute-input', type='number', placeholder="Enter distance (km)",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='taxi-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'}) 
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the total taxi/private car commute distance in km multiplied by the number of employees.",
                            target="taxi-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        ),
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H5("Business Travel (Flight, $SDG/year)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="flight-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='business-travel-flight-input', type='number', placeholder="Enter amount in $SDG",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='flight-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'}) 
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the annual amount spent on business flights in $SDG.",
                            target="flight-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        ),
                        dbc.Col([
                            html.Div([
                                html.H5("Business Travel (Hotel, $SDG/year)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="hotel-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='business-travel-hotel-input', type='number', placeholder="Enter amount in $SDG",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='hotel-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'}) 
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the annual amount spent on business hotel stays in $SDG.",
                            target="hotel-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        ),
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H5("Procurement with Air Freight (t * km)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="air-freight-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='business-procurement-air-freight-input', type='number', placeholder="Enter weight/volume",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='air-freight-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'}) 
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the total weight/volume transported in ton-kilometers (t * km) for air freight procurement.",
                            target="air-freight-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        ),
                        dbc.Col([
                            html.Div([
                                html.H5("Procurement with Diesel Truck Freight (t * km)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="diesel-truck-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='business-procurement-diesel-truck-input', type='number', placeholder="Enter weight/volume",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='diesel-truck-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'}) 
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the total weight/volume transported in ton-kilometers (t * km) for diesel truck freight procurement.",
                            target="diesel-truck-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        ),
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H5("Procurement with Electric Truck Freight (t * km)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="electric-truck-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='business-procurement-electric-truck-input', type='number', placeholder="Enter weight/volume",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='electric-truck-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'}) 
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the total weight/volume transported in ton-kilometers (t * km) for electric truck freight procurement.",
                            target="electric-truck-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        ),
                    ], className="mb-4"),
                ])
            ], className="mb-4", style={'border': '1px solid #ced4da', 'borderRadius': '10px', "box-shadow": "2px 0 8px rgba(0, 0, 0, 0.3)"}),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Button("Proceed to Data Quality Check", id="next-button", color="success", className="mt-4",
                           style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'fontWeight': 'bold'})
            ], width=3),
            html.Div(id="form-error", style={'color': 'red', 'fontSize': '14px', 'marginTop': '10px'})
        ], justify="center"),
    ], className="mb-5", style={
        'backgroundColor': '#ffffff',
        'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.1)',
        'padding': '20px'
    })
], fluid=True)

#Call back for missing data
@app.callback(
    [Output("form-error", "children")] + [
        Output("region-dropdown", "style"),
        Output("building-input", "style"),
        Output("zip-input", "style"),
        Output("year-input", "style"),
        Output("size-input", "style"),
        Output("employee-input", "style"),
        Output("energy-input", "style"),
        Output("water-input", "style"),
        Output("waste-input", "style"),
        Output("subway-commute-input", "style"),
        Output("bus-commute-input", "style"),
        Output("taxi-commute-input", "style"),
        Output("business-travel-flight-input", "style"),
        Output("business-travel-hotel-input", "style"),
        Output("business-procurement-air-freight-input", "style"),
        Output("business-procurement-diesel-truck-input", "style"),
        Output("business-procurement-electric-truck-input", "style"),
        Output("url", "href")  # For conditional navigation
    ],
    [Input("next-button", "n_clicks")],
    [
        State("region-dropdown", "value"),
        State("building-input", "value"),
        State("zip-input", "value"),
        State("year-input", "value"),
        State("size-input", "value"),
        State("employee-input", "value"),
        State("energy-input", "value"),
        State("water-input", "value"),
        State("waste-input", "value"),
        State("subway-commute-input", "value"),
        State("bus-commute-input", "value"),
        State("taxi-commute-input", "value"),
        State("business-travel-flight-input", "value"),
        State("business-travel-hotel-input", "value"),
        State("business-procurement-air-freight-input", "value"),
        State("business-procurement-diesel-truck-input", "value"),
        State("business-procurement-electric-truck-input", "value")
    ]
)
def validate_form(n_clicks, *input_values):
    if n_clicks is None:
        raise PreventUpdate

    error_messages = []
    styles = []

    # Validate each field and assign the appropriate style
    for value in input_values:
        if value is None or value == "":
            error_messages.append("Some fields are missing. Please fill out all required fields.")
            styles.append(style_with_error)
        else:
            styles.append(style_without_error)

    error_message = error_messages[0] if error_messages else ""
    
    # Set navigation URL only if all fields are valid
    href = "/page-2" if not error_message else None
    return [error_message] + styles + [href]



# Callback for input error data
# 1. Zip Code Validation (6-digit Singapore postal code)
@app.callback(
    Output('zip-error', 'children'),
    Input('zip-input', 'value')
)
def validate_zip(zip_code):
    if zip_code is None:
        return ""  # No error if no input
    zip_code = str(zip_code)  # Convert zip_code to string
    if not re.match(r'^\d{6}$', zip_code):  # Check if zip code is 6 digits
        return "Invalid format. Please enter a 6-digit Singapore postal code (e.g., 123456)."
    return ""  # No error if the format is correct


# 2. Year Validation (4-digit year, not exceeding current year + 1)
@app.callback(
    Output('year-error', 'children'),
    Input('year-input', 'value')
)
def validate_year(year):
    if year is None:
        return ""  # No error if no input
    
    current_year = datetime.now().year
    if not re.match(r'^\d{4}$', str(year)):  # Check if year is in 4-digit format
        return "Invalid format. Please enter a valid year."
    elif year > current_year + 1:
        return f"Invalid year. Please enter a year no later than {current_year + 1}."
    
    return ""  # No error if the format and range are correct


# 3. Size Validation (100–1,000,000 sqft)
@app.callback(
    Output('size-error', 'children'),
    Input('size-input', 'value')
)
def validate_size(size):
    if size is None:
        return ""  # No error if no input
    if size < 100 or size > 2000000:
        return "Invalid size. Please enter a realistic building size in square feet (100–2,000,000)."
    return ""  # No error if within the range

# 4. Number of Employees Validation (1–50,000)
@app.callback(
    Output('employees-error', 'children'),
    Input('employee-input', 'value')
)
def validate_employees(employees):
    if employees is None:
        return ""  # No error if no input
    if employees < 1 or employees > 50000:
        return "Invalid number. Please enter a realistic number of employees (1–50,000)."
    return ""  # No error if within the range

# 5. Energy Consumption Validation (1–100,000,000 kWh)
@app.callback(
    Output('energy-error', 'children'),
    Input('energy-input', 'value')
)
def validate_energy(energy):
    if energy is None:
        return ""  # No error if no input
    if energy < 1 or energy > 100000000:
        return "Invalid value. Please enter a realistic energy consumption (1–100,000,000 kWh)."
    return ""  # No error if within the range

# 6. Water Consumption Validation (1–1,000,000 m³)
@app.callback(
    Output('water-error', 'children'),
    Input('water-input', 'value')
)
def validate_water(water):
    if water is None:
        return ""  # No error if no input
    if water < 1 or water > 1000000:
        return "Invalid value. Please enter a realistic water consumption (1–1,000,000 m³)."
    return ""  # No error if within the range

# 7. Waste Generated Validation (0.1–10,000 tons)
@app.callback(
    Output('waste-error', 'children'),
    Input('waste-input', 'value')
)
def validate_waste(waste):
    if waste is None:
        return ""  # No error if no input
    if waste < 0.1 or waste > 1000000:
        return "Invalid value. Please enter a realistic waste amount (0.1–1,000,000 tons)."
    return ""  # No error if within the range

# 8. Commute Distances Validation (1–10,000 km * people)
def commute_validation_callback(input_id, output_id, field_name):
    @app.callback(
        Output(output_id, 'children'),
        Input(input_id, 'value')
    )
    def validate_commute(distance):
        if distance is None:
            return ""  # No error if no input
        if distance < 1 or distance > 15000:
            return f"Invalid value for {field_name} commute. Enter a realistic total distance (1–15,000 km * people)."
        return ""  # No error if within the range
    return validate_commute

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

commute_validation_callback('subway-commute-input', 'subway-error', 'Subway/MRT')
commute_validation_callback('bus-commute-input', 'bus-error', 'Bus')
commute_validation_callback('taxi-commute-input', 'taxi-error', 'Taxi/Private Car')

# 9. Business Travel Expenses Validation (0–1,000,000 SDG)
def travel_expense_validation_callback(input_id, output_id, field_name):
    @app.callback(
        Output(output_id, 'children'),
        Input(input_id, 'value')
    )
    def validate_travel_expense(expense):
        if expense is None:
            return ""  # No error if no input
        if expense < 0 or expense > 100000000:
            return f"Invalid {field_name} expense. Enter a realistic annual expense (0–100,000,000 SDG)."
        return ""  # No error if within the range
    return validate_travel_expense

travel_expense_validation_callback('business-travel-flight-input', 'flight-error', 'Flight')
travel_expense_validation_callback('business-travel-hotel-input', 'hotel-error', 'Hotel')

# 10. Freight Transport Distance Validation (1–1,000,000 t * km)
def freight_validation_callback(input_id, output_id, field_name):
    @app.callback(
        Output(output_id, 'children'),
        Input(input_id, 'value')
    )
    def validate_freight(distance):
        if distance is None:
            return ""  # No error if no input
        if distance < 1 or distance > 1000000:
            return f"Invalid value for {field_name}. Enter a realistic freight transport distance (1–1,000,000 t * km)."
        return ""  # No error if within the range
    return validate_freight

freight_validation_callback('business-procurement-air-freight-input', 'air-freight-error', 'Air Freight')
freight_validation_callback('business-procurement-diesel-truck-input', 'diesel-truck-error', 'Diesel Truck Freight')
freight_validation_callback('business-procurement-electric-truck-input', 'electric-truck-error', 'Electric Truck Freight')




# Define layout for Page 2 - Data Quality Check and EDA
page_2_layout = dbc.Container([
    html.Div(
        html.Img(
            src='./assets/teamlogo.png',
            style={
                'width': '220px',
                'height': 'auto',
            }
        ),
        id="page-2-logo-wrapper",
        style={
            'position': 'absolute',
            'top': '55px',
            'right': '40px',
            'transition': 'right 0.3s ease'
        }
    ),
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
            dbc.Button("Re-upload Data", id="reupload-button", color="warning",href='/page-1',
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

@app.callback(
    Output("page-2-logo-wrapper", "style"),
    [Input("toggle-button", "n_clicks")],
    [State("page-2-logo-wrapper", "style")]
)
def adjust_logo_position(n_clicks, current_style):
    if n_clicks and n_clicks % 2 != 0:  # Sidebar is visible
        # Shift logo further to the right
        current_style["right"] = "0px"  # Adjust to match sidebar width
    else:
        # Reset logo position when sidebar is hidden
        current_style["right"] = "40px"
    return current_style


# Define layout for Page 3 - Model Running and Visualization
page_3_layout = dbc.Container([
     html.Div(
        html.Img(
            src='./assets/teamlogo.png',
            style={
                'width': '220px',
                'height': 'auto',
            }
        ),
        id="page-3-logo-wrapper",
        style={
            'position': 'absolute',
            'top': '55px',
            'right': '40px',
            'transition': 'right 0.3s ease'
        }
    ),
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


@app.callback(
    Output("page-3-logo-wrapper", "style"),
    [Input("toggle-button", "n_clicks")],
    [State("page-3-logo-wrapper", "style")]
)
def adjust_logo_position(n_clicks, current_style):
    if n_clicks and n_clicks % 2 != 0:  # Sidebar is visible
        # Shift logo further to the right
        current_style["right"] = "0px"  # Adjust to match sidebar width
    else:
        # Reset logo position when sidebar is hidden
        current_style["right"] = "40px"
    return current_style


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
        html.Div(
        html.Img(
            src='./assets/teamlogo.png',
            style={
                'width': '220px',
                'height': 'auto',
            }
        ),
        id="page-4-logo-wrapper",
        style={
            'position': 'absolute',
            'top': '55px',
            'right': '40px',
            'transition': 'right 0.3s ease'
        }
    ),
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
            dbc.Button("Next: Feedback Survey", id="go-to-page-5", color="success", href='/page-5', className="mt-4", style={
                'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'fontWeight': 'bold'
            })
        ], width=3),
    ], className="mt-5 mb-5")  # Add 'mb-5' to create extra space at the bottom
])


@app.callback(
    Output("page-4-logo-wrapper", "style"),
    [Input("toggle-button", "n_clicks")],
    [State("page-4-logo-wrapper", "style")]
)
def adjust_logo_position(n_clicks, current_style):
    if n_clicks and n_clicks % 2 != 0:  # Sidebar is visible
        # Shift logo further to the right
        current_style["right"] = "0px"  # Adjust to match sidebar width
    else:
        # Reset logo position when sidebar is hidden
        current_style["right"] = "40px"
    return current_style


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

# Define layout for Page 5 - Feedback
page_5_layout = dbc.Container([
    html.Div(
        html.Img(
            src='./assets/teamlogo.png',
            style={
                'width': '220px',
                'height': 'auto',
            }
        ),
        id="page-5-logo-wrapper",
        style={
            'position': 'absolute',
            'top': '55px',
            'right': '40px',
            'transition': 'right 0.3s ease'
        }
    ),
    html.H2("Feedback Survey", className="mt-4 mb-4 text-center", style={'fontSize': '32px', 'fontWeight': 'bold'}),

    dbc.Row([
        dbc.Col([
            dbc.Input(id="building_name", placeholder="Building Name", type="text", className="mb-3", 
                      style={'fontSize': '18px', 'borderRadius': '5px', 'border': '1px solid #ced4da', 'padding': '10px'}),
            dbc.Input(id="predicted_level", placeholder="Predicted Level", type="text", className="mb-3", 
                      style={'fontSize': '18px', 'borderRadius': '5px', 'border': '1px solid #ced4da', 'padding': '10px'}),
            
            dbc.Label("Prediction Accuracy", style={'fontSize': '20px', 'fontWeight': 'bold'}),
            dcc.Slider(id="prediction_accuracy", min=1, max=5, step=1, value=3, 
                       marks={i: str(i) for i in range(1, 6)}, className="mb-4"),
            
            dbc.Label("Calculation Clarity", style={'fontSize': '20px', 'fontWeight': 'bold'}),
            dcc.Slider(id="calculation_clarity", min=1, max=5, step=1, value=3, 
                       marks={i: str(i) for i in range(1, 6)}, className="mb-4"),
            
            dbc.Label("Visualization Helpfulness", style={'fontSize': '20px', 'fontWeight': 'bold'}),
            dcc.Slider(id="visualization_helpfulness", min=1, max=5, step=1, value=3, 
                       marks={i: str(i) for i in range(1, 6)}, className="mb-4"),
            
            dbc.Label("GHG Intensity Rating", style={'fontSize': '20px', 'fontWeight': 'bold'}),
            dcc.Slider(id="ghg_intensity_rating", min=1, max=5, step=1, value=3, 
                       marks={i: str(i) for i in range(1, 6)}, className="mb-4"),
            
            dbc.Label("Emissions Breakdown Rating", style={'fontSize': '20px', 'fontWeight': 'bold'}),
            dcc.Slider(id="emissions_breakdown_rating", min=1, max=5, step=1, value=3, 
                       marks={i: str(i) for i in range(1, 6)}, className="mb-4"),
            
            dbc.Label("Benchmark Comparison Rating", style={'fontSize': '20px', 'fontWeight': 'bold'}),
            dcc.Slider(id="benchmark_comparison_rating", min=1, max=5, step=1, value=3, 
                       marks={i: str(i) for i in range(1, 6)}, className="mb-4"),
            
            dbc.Textarea(id="improvement_priorities", placeholder="Improvement Priorities (comma-separated)", 
                         className="mb-4", style={'fontSize': '18px', 'borderRadius': '5px', 
                                                   'border': '1px solid #ced4da', 'padding': '10px'}),
            
            dbc.Label("Overall Satisfaction", style={'fontSize': '20px', 'fontWeight': 'bold'}),
            dcc.Slider(id="overall_satisfaction", min=1, max=5, step=1, value=3, 
                       marks={i: str(i) for i in range(1, 6)}, className="mb-4"),
            
            dbc.Button("Submit Feedback", id="submit_feedback", color="success", className="mt-4 mb-3", 
                       style={'width': '100%', 'padding': '12px', 'borderRadius': '5px', 'fontSize': '18px', 
                              'fontWeight': 'bold'}),
            dcc.Download(id="download_excel")
        ], md=6, className="offset-md-3")  # Centers the form for better alignment
    ]),

    # Row for Back and Home buttons on the same line
    dbc.Row([
        dbc.Col([
            dbc.Button("Back", id="back-button", color="warning", style={
                'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'fontSize': 'bold', 'fontWeight': 'bold'
            })
        ], width=3),  # 6-column width for each button
        dbc.Col([
            dbc.Button("Home", id="home-button", color="success",
                       style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'fontSize': 'bold', 
                              'fontWeight': 'bold'})
        ], width=3)
    ], justify="center", className="mt-3 mb-5")
])

@app.callback(
    Output("download_excel", "data"),
    Input("submit_feedback", "n_clicks"),
    [
        State("building_name", "value"),
        State("predicted_level", "value"),
        State("prediction_accuracy", "value"),
        State("calculation_clarity", "value"),
        State("visualization_helpfulness", "value"),
        State("ghg_intensity_rating", "value"),
        State("emissions_breakdown_rating", "value"),
        State("benchmark_comparison_rating", "value"),
        State("improvement_priorities", "value"),
        State("overall_satisfaction", "value")
    ]
)
def handle_feedback_submission(n_clicks, building_name, predicted_level, prediction_accuracy,
                               calculation_clarity, visualization_helpfulness, ghg_intensity_rating,
                               emissions_breakdown_rating, benchmark_comparison_rating, improvement_priorities,
                               overall_satisfaction):
    if n_clicks:
        improvement_priorities_list = improvement_priorities.split(',') if improvement_priorities else []

        feedback_data = {
            "building_name": building_name,
            "predicted_level": predicted_level,
            "prediction_accuracy": prediction_accuracy,
            "calculation_clarity": calculation_clarity,
            "visualization_helpfulness": visualization_helpfulness,
            "feature_ratings": {
                "ghg_intensity": ghg_intensity_rating,
                "emissions_breakdown": emissions_breakdown_rating,
                "benchmark_comparison": benchmark_comparison_rating
            },
            "improvement_priorities": improvement_priorities_list,
            "overall_satisfaction": overall_satisfaction,
            "timestamp": datetime.now()
        }

        feedback_handler.store_feedback(feedback_data)
        excel_path = feedback_handler.export_feedback_to_excel()
        return dcc.send_file(excel_path)

    
@app.callback(
    Output("page-5-logo-wrapper", "style"),
    [Input("toggle-button", "n_clicks")],
    [State("page-5-logo-wrapper", "style")]
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
    Output("url", "pathname"),  # Single output for both buttons
    [Input("back-button", "n_clicks"), Input("home-button", "n_clicks")]
)
def navigate(n_clicks_back, n_clicks_home):
    # Get the context of the callback to identify which button triggered the callback
    ctx = callback_context

    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "back-button" and n_clicks_back:
        return "/page-4"  # Navigate to Page 4
    elif button_id == "home-button" and n_clicks_home:
        return "/"  # Navigate to Home

    return dash.no_update


# Sample Q&A content
qa_content = [
    {
        "question": "What is this dash for?",
        "answer": "This app helps with data input and validation for sustainability reporting. It assists users in inputting environmental data, performing data quality checks, and generating reports."
    },
    {
        "question": "What can use this dash?",
        "answer": "aThis app is intended for users responsible for reporting on environmental metrics. No special training is needed, but a basic understanding of emissions and sustainability reporting is helpful."
    },
    {
        "question": "Is there a file size limit for uploads?",
        "answer": "Yes, files should not exceed 10 MB. If your file is too large, consider splitting it or removing unnecessary data."
    },
    {
        "question": "How do I upload a file?",
        "answer": "To upload a file, go to the 'Data Input' section and drag-and-drop your file or click 'Browse' to select it. Make sure your file is in .csv or .xlsx format."
    },
    {
        "question": "What should I do if I see an error message?",
        "answer": "Error messages indicate that some of your data does not meet the expected format or range. Follow the instructions in the error message to correct the data and try again."
    },
    {
        "question": "What do the metrics in the report mean?",
        "answer": "The metrics provide insights into emissions, energy consumption, water usage, and more. You can find a detailed explanation of each metric in the report’s appendix section."
    },
    {
        "question": "Why is the page not loading correctly or page is not responding?",
        "answer": "Please ensure you are using an updated browser. If the problem persists, try clearing your cache or disabling browser extensions. Sometimes it takes time for the page to load, if the page is not responding, try refreshing the page."
    },
    {
        "question": "Who can I contact for support?",
        "answer": "For support, please contact our team at e1352233@u.nus.edu We’re here to help with any issues you may have."
    },
]

# Q&A layout with collapsible questions
page_qa_layout = dbc.Container([
    # Logo
    html.Div(
        html.Img(
            src='./assets/teamlogo.png',
            style={'width': '220px', 'height': 'auto'}
        ),
        id="page-5-logo-wrapper",
        style={
            'position': 'absolute',
            'top': '55px',
            'right': '40px',
            'transition': 'right 0.3s ease'
        }
    ),
    
        html.Div([
        html.H3("Frequently Asked Questions", style={
            'fontWeight': 'bold',
            'fontSize': '28px',
            'textAlign': 'center',
            'marginBottom': '30px',
            'color': '#333',
        }),
    ]),

# FAQ Accordion Section
    html.Div([
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    title=qa["question"],
                    children=html.P(qa["answer"], style={'padding': '10px', 'lineHeight': '1.6'}),
                    style={
                        'marginBottom': '10px',
                        'borderRadius': '8px',
                        'border': '1px solid #ddd',
                        'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                    }
                )
                for qa in qa_content
            ],
            start_collapsed=True,
            style={
                'backgroundColor': '#ffffff',
                'borderRadius': '8px',
                'padding': '10px'
            }
        ),
        
        # Contact information at the bottom
        html.P(
            "For more questions, please contact us at e1352233@u.nus.edu.",
            style={
                'marginTop': '20px',
                'fontSize': '16px',
                'color': '#555',
                'textAlign': 'center'
            }
        )
    ], style={
        'padding': '20px',
        'backgroundColor': '#f9f9f9',
        'borderRadius': '8px',
        'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)'
    })
], fluid=True, style={'padding': '40px 0', 'maxWidth': '800px', 'margin': 'auto'})




# About Us layout with core philosophy and GitHub link
page_about_layout = dbc.Container([
    # Header with Logo and Title
    html.Div(
        html.Img(
            src='./assets/teamlogo.png',
            style={'width': '220px', 'height': 'auto'}
        ),
        id="page-5-logo-wrapper",
        style={
            'position': 'absolute',
            'top': '55px',
            'right': '40px',
            'transition': 'right 0.3s ease'
        }
    ),
    
    # About YYDS Section
    html.Div([
        html.H3("Why YYDS?", className="my-4", style={'fontWeight': 'bold'}),
        html.P("""
            Our team is named "YYDS," a phrase that originates from Chinese internet culture, meaning "永远的神" (yǒng yuǎn de shén) 
            or "Eternal God." This term is used to describe something legendary, timeless, and worth admiring — the best of the best. 
            For us, it reflects our commitment to creating something enduring and impactful, particularly in the realm of sustainability.
        """, style={'lineHeight': '1.6'}),
        html.P("""
            In today's world, achieving true sustainability means creating systems, practices, and innovations that stand the test of time — 
            solutions that are not only effective today but will also continue to make a positive impact far into the future. This is what "YYDS" 
            represents to us: the aspiration to be a lasting force for good, to develop solutions that people can rely on, and to drive meaningful 
            change that is resilient over time.
        """, style={'lineHeight': '1.6'}),
        html.P("""
            Our team believes that sustainability is not just a goal but a journey toward a better, lasting world. By embracing the "YYDS" mindset, 
            we aim to be "forever impactful" — creating solutions, tools, and practices in the field of sustainability that are not only effective 
            but also resilient and adaptive to the challenges of tomorrow.
        """, style={'lineHeight': '1.6'}),
        html.P("""
            In essence, YYDS symbolizes our commitment to excellence and timeless impact in sustainability. We want our contributions to be seen 
            as YYDS: enduring, trustworthy, and legendary in the fight for a sustainable future.
        """, style={'lineHeight': '1.6'}),
        
        # GitHub Link Section
        html.Hr(),
        html.Div(
            [
                html.H4("Learn More About Our Project", style={'fontWeight': 'bold', 'marginBottom': '15px'}),
                html.A("View our GitHub Repository", href="https://github.com/Lucas1213WZY/DSS5105-YYDS", 
                       target="_blank", style={
                           'fontSize': '18px', 
                           'color': '#007bff', 
                           'textDecoration': 'none', 
                           'fontWeight': 'bold'
                       })
            ],
            style={
                'marginTop': '20px',
                'padding': '15px',
                'backgroundColor': '#f9f9f9',
                'borderRadius': '8px',
                'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)',
                'textAlign': 'center'
            }
        )
    ], style={
        'padding': '20px',
        'backgroundColor': '#ffffff',
        'borderRadius': '8px',
        'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)'
    })
], fluid=True, style={'padding': '40px 0', 'maxWidth': '800px', 'margin': 'auto'})



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
    elif pathname == "/qa":
        return page_qa_layout
    elif pathname == "/about":
        return page_about_layout
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
