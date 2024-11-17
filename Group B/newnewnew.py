import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import io
import os
import dash_bootstrap_components as dbc
from dash import dash_table
import folium
from dash_extensions import BeforeAfter
from dash import callback_context
import dash_leaflet as dl
import base64
import plotly.graph_objects as go
import re
import folium
from dash.exceptions import PreventUpdate
from datetime import datetime
from structured_feedback_handler import StructuredFeedbackHandler  # Import the feedback handler class

import json
import openai
import numpy as np
from plotly.subplots import make_subplots
import pickle
from utils.validator_final import GreenMarkValidator

#from utils.helper_functions import calculate_business_emissions
from pathlib import Path

# Load the commuting factors JSON file from the assets directory
assets_path = Path('./assets/commuting_factors.json')
with open(assets_path) as f:
    commuting_factors = json.load(f)

business_path = Path('./assets/BusinessTravelNProcurement.json')
with open(business_path) as f:
    business_travel_procurement_factors = json.load(f)
# Define a global variable for storing selected commuting factors
selected_commuting_factors = {}


openai.api_key = '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'
# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY, "https://use.fontawesome.com/releases/v5.8.1/css/all.css"], suppress_callback_exceptions=True)
server = app.server
#Sidebar Layout
sidebar = html.Div(
    [
        # Main navigation links
        html.Div([
            dcc.Link([
                html.I(className="fas fa-database"),  # Icon for Data Input
                html.Span(" Data Input", style={"marginLeft": "10px"})
            ], href="/page-1", style={
                "display": "flex",
                "alignItems": "center",
                "color": "white",
                "padding": "12px 20px",
                "textDecoration": "none",
                "fontSize": "18px",
                "fontWeight": "bold",
                "borderRadius": "5px",
            }),
            dcc.Link([
                html.I(className="fas fa-chart-line"),  # Icon for Data Quality Check
                html.Span(" Data Quality Check and Exploratory Data Analysis", style={"marginLeft": "10px"})
            ], href="/page-2", style={
                "display": "flex",
                "alignItems": "center",
                "color": "white",
                "padding": "12px 20px",
                "textDecoration": "none",
                "fontSize": "18px",
                "fontWeight": "bold",
                "borderRadius": "5px",
            }),
            dcc.Link([
                html.I(className="fas fa-trophy"),  # Icon for Model Results
                html.Span(" Model Results and Benchmarking", style={"marginLeft": "10px"})
            ], href="/page-3", style={
                "display": "flex",
                "alignItems": "center",
                "color": "white",
                "padding": "12px 20px",
                "textDecoration": "none",
                "fontSize": "18px",
                "fontWeight": "bold",
                "borderRadius": "5px",
            }),
            dcc.Link([
                html.I(className="fas fa-comments"),  # Icon for Report and Chatbox
                html.Span(" Report and Chatbox", style={"marginLeft": "10px"})
            ], href="/page-4", style={
                "display": "flex",
                "alignItems": "center",
                "color": "white",
                "padding": "12px 20px",
                "textDecoration": "none",
                "fontSize": "18px",
                "fontWeight": "bold",
                "borderRadius": "5px",
            }),
            dcc.Link([
                html.I(className="fas fa-envelope"),  # Icon for Feedback
                html.Span(" Feedback", style={"marginLeft": "10px"})
            ], href="/page-5", style={
                "display": "flex",
                "alignItems": "center",
                "color": "white",
                "padding": "12px 20px",
                "textDecoration": "none",
                "fontSize": "18px",
                "fontWeight": "bold",
                "borderRadius": "5px",
            }),
        ], style={"marginBottom": "auto"}),  # Ensures other links are pushed to the bottom

        # Additional links at the bottom
        html.Div([
            dcc.Link([
                html.I(className="fas fa-question-circle"),  # Icon for Q&A
                html.Span(" Q&A", style={"marginLeft": "10px"})
            ], href="/qa", style={
                "display": "flex",
                "alignItems": "center",
                "color": "white",
                "padding": "12px 20px",
                "textDecoration": "none",
                "fontSize": "18px",
                "fontWeight": "bold",
                "borderRadius": "5px",
            }),
            dcc.Link([
                html.I(className="fas fa-info-circle"),  # Icon for About Us
                html.Span(" About Us", style={"marginLeft": "10px"})
            ], href="/about", style={
                "display": "flex",
                "alignItems": "center",
                "color": "white",
                "padding": "12px 20px",
                "textDecoration": "none",
                "fontSize": "18px",
                "fontWeight": "bold",
                "borderRadius": "5px",
            }),
        ], style={"paddingTop": "20px"}),  # Add spacing above the bottom links
    ],
    id="sidebar",
    style={
        "padding": "15px",
        "backgroundColor": "#333",
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
        "boxShadow": "2px 0 8px rgba(0, 0, 0, 0.3)",
        "borderRadius": "0 8px 8px 0",
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
                dcc.Store(id='selected-building-store'),
                html.Div(id="page-content"),
                dcc.Store(id="user-data", storage_type="session")
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

UPLOAD_DIRECTORY = "./datasets"
#if not os.path.exists(UPLOAD_DIRECTORY):
#   os.makedirs(UPLOAD_DIRECTORY)
global_data = {}

@app.callback(
    Output('file-upload-status', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('upload-data', 'last_modified')
)
def update_output(contents, filename, last_modified):
    global global_data
    if contents is not None:
        content_type, content_string = contents.split(',')
        
        decoded = base64.b64decode(content_string)
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(io.StringIO(decoded.decode('latin-1')))
                file_path = os.path.join(UPLOAD_DIRECTORY, filename)
                df.to_csv(file_path, index=False)
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(io.BytesIO(decoded))
                file_path = os.path.join(UPLOAD_DIRECTORY, filename)
                df.to_excel(file_path, index=False)
            else:
                return html.Div(['File format not supported. Please upload a CSV or XLSX file.'])

            # Store the DataFrame in a global dictionary
            global_data['uploaded_df'] = df
            
            return html.Div([
                html.H5(f"File {filename} uploaded successfully!"),
                html.P(f"Saved to: {file_path}"),
                dash_table.DataTable(
                    data=df.head().to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in df.columns],
                    style_table={'overflowX': 'auto'}
                )
            ])
        except Exception as e:
            print(f"Error reading file: {e}")
            return html.Div(['File read failed. Please check the file format.'])
    
    return html.Div(['No file uploaded.'])

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
    dcc.Store(id='commuting-factors-store'),
    dcc.Store(id="manual-data-store", data={}),
    dcc.Store(id="commuting-emission-results-store", data={}),
    dcc.Store(id='business-travel-store'),
    dcc.Store(id='business-procurement-store'),
    dcc.Store(id='total-transportation-emissions-store'),
    dcc.Store(id="stored-form-data"),
    dcc.Store(id='output-calculation'),
    dcc.Store(id='output-ghg-prediction'),
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
                        ),
                        dbc.Col([
                            html.Div([
                                html.H5("Size (m squared)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
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
                        )
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H5("Office Area (%)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="office-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='office-input', type='number', placeholder="Enter Building Office Area",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='office-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'}) 
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the percentage (%) of the building area used as office space. (e.g., if 50% of the building is used as office space, enter 50).",
                            target="office-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        ),
                        dbc.Col([
                            html.Div([
                                html.H5("Retail Area(%)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="retail-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='retail-input', type='number', placeholder="Enter Building Retail Area",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='retail-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'}) 
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the percentage (%) of the building area used as retail space. (e.g., if 50% of the building is used as retail space, enter 50).",
                            target="retail-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        )
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H5("Parking Area (%)", style={'fontWeight': '600', 'fontSize': '18px', 'color': '#343a40'}),
                                html.I(className="fas fa-info-circle", id="parking-info-icon",
                                       style={'position': 'absolute', 'top': '5px', 'right': '5px', 'color': 'gray', 'cursor': 'pointer'})
                            ], style={'position': 'relative'}),
                            dcc.Input(id='parking-input', type='number', placeholder="Enter Building Parking Area",
                                      style={'width': '100%', 'padding': '10px', 'borderRadius': '10px', 'border': '1px solid #ced4da'}),
                            html.Div(id='parking-error', style={'color': 'red', 'fontSize': '14px', 'marginTop': '5px'}) 
                        ], width=6),
                        dbc.Tooltip(
                            "Enter the percentage (%) of the building area used as parking space. (e.g., if 50% of the building is used as parking space, enter 50).",
                            target="parking-info-icon",
                            placement="top",
                            delay={"show": 1000, "hide": 100}
                        )
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

@app.callback(
    [
        Output("form-error", "children"),
        Output("url", "href"),
        Output("stored-form-data", "data")  # New output for dcc.Store
    ] + [
        Output(f"{input_id}", "style") for input_id in [
            "region-dropdown", "building-input", "zip-input", "year-input", "size-input", "employee-input",
            "office-input", "retail-input", "parking-input",
            "energy-input", "water-input", "waste-input", "subway-commute-input", "bus-commute-input",
            "taxi-commute-input", "business-travel-flight-input", "business-travel-hotel-input",
            "business-procurement-air-freight-input", "business-procurement-diesel-truck-input",
            "business-procurement-electric-truck-input"
        ]
    ],
    Input("next-button", "n_clicks"),
    [
        State("region-dropdown", "value"),
        State("building-input", "value"),
        State("zip-input", "value"),
        State("year-input", "value"),
        State("size-input", "value"),
        State("employee-input", "value"),
        State("office-input", "value"),
        State("retail-input", "value"),
        State("parking-input", "value"),
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
def validate_and_store_form(n_clicks, *input_values):
    if n_clicks is None:
        raise PreventUpdate

    # Define the names of the fields to match input values
    field_names = [
        "Region", "Building Name", "Zip Code", "Year", "Size", "Number of Employees",
        "Office Area", "Retail Area", "Parking Area",
        "Energy", "Water", "Waste", "Subway Commute", "Bus Commute", "Taxi Commute",
        "Business Travel Flight", "Business Travel Hotel", "Air Freight", "Diesel Truck Freight",
        "Electric Truck Freight"
    ]
    
    # Initialize error handling and storage variables
    error_messages = []
    styles = []
    global stored_data  # Dictionary to store input values
    stored_data = {}
    # Validate each field and assign the appropriate style
    for idx, value in enumerate(input_values):
        if value is None or value == "":
            error_messages.append(f"Field '{field_names[idx]}' is missing. Please fill out all required fields.")
            styles.append({"border": "1px solid red"})  # Show error style
        else:
            styles.append({"border": "1px solid #ced4da"})  # Valid style
            stored_data[field_names[idx]] = value  # Store valid values in dictionary
    print(stored_data)
    # Check for errors and set navigation URL only if all fields are valid
    error_message = error_messages[0] if error_messages else ""
    href = "/page-3-manual" if n_clicks and not error_message else None
    global_data['user_data'] = stored_data
    # Return values with stored_data added for dcc.Store
    return [error_message, href, stored_data] + styles


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

# Office Area Validation
@app.callback(
    Output('office-error', 'children'),
    Input('office-input', 'value')
)
def validate_office_area(office_area):
    if office_area is None:
        return ""  # No error if no input
    if office_area < 0 or office_area > 100:
        return "Invalid percentage. Please enter a realistic percentage (0-100)."
    return ""  # No error if within the range

# Retail Area Validation
@app.callback(
    Output('retail-error', 'children'),
    Input('retail-input', 'value')
)
def validate_retail_area(retail_area):
    if retail_area is None:
        return ""  # No error if no input
    if retail_area < 0 or retail_area > 100:
        return "Invalid percentage. Please enter a realistic percentage (0-100)."
    return ""  # No error if within the range

# Parking Area Validation
@app.callback(
    Output('parking-error', 'children'),
    Input('parking-input', 'value')
)
def validate_parking_area(parking_area):
    if parking_area is None:
        return ""  # No error if no input
    if parking_area < 0 or parking_area > 100:
        return "Invalid percentage. Please enter a realistic percentage (0-100)."
    return ""  # No error if within the range

# 5. Energy Consumption Validation (1–100,000,000 kWh)
@app.callback(
    Output('energy-error', 'children'),
    Input('energy-input', 'value')
)
def validate_energy(energy):
    if energy is None:
        return ""  # No error if no input
    if energy < 1 or energy > 10000000000000:
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
    if water < 1 or water > 10000000000:
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
    if waste < 0.1 or waste > 1000000000:
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
        if distance < 1 or distance > 1500000:
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
        if expense < 0 or expense > 100000000000:
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
        if distance < 1 or distance > 100000000000:
            return f"Invalid value for {field_name}. Enter a realistic freight transport distance (1–1,000,000 t * km)."
        return ""  # No error if within the range
    return validate_freight

freight_validation_callback('business-procurement-air-freight-input', 'air-freight-error', 'Air Freight')
freight_validation_callback('business-procurement-diesel-truck-input', 'diesel-truck-error', 'Diesel Truck Freight')
freight_validation_callback('business-procurement-electric-truck-input', 'electric-truck-error', 'Electric Truck Freight')

# indicator calculations and predictions

@app.callback(
    Output("some-output", "children"),  # Replace with the actual output(s) you need
    Input("form-data-store", "data")
)
def use_stored_data(stored_data):
    # Check if stored_data is available
    if stored_data is None:
        return "No data stored yet."
    
    # Use stored_data directly as a dictionary
    # For example, here we just format and display the entire dictionary
    global_data['manual_data'] = stored_data
    print("Stored data updated:", global_data['manual_data'])
    
    # Now you have access to the entire dictionary and can use it as needed
    return f"Stored Data: {global_data['manual_data']}"

# Acess regional factors and calculate commuting emissions
@app.callback(
    Output('commuting-factors-store', 'data'),
    Input('region-dropdown', 'value')
)
def update_commuting_factors(region):
    # Fetch the commuting factors for the selected region
    if region in commuting_factors:
        print("Commuting factors for region:", commuting_factors[region])
        return commuting_factors[region]
    
    return None  # Return None if no valid region is selected

@app.callback(
    Output('commuting-emission-results-store', 'data'),
    [
        Input('subway-commute-input', 'value'),
        Input('bus-commute-input', 'value'),
        Input('taxi-commute-input', 'value')
    ],
    State('commuting-factors-store', 'data')
)
def calculate_commuting_emissions(subway_value, bus_value, taxi_value, commuting_factors):
    if not commuting_factors:
        return {"error": "Commuting factors not loaded."}

    if subway_value is None or bus_value is None or taxi_value is None:
        return {"error": "Please fill in all commute distances."}

    # Calculate emissions
    subway_emission = subway_value * commuting_factors.get("Commuting Factor_Subway", 0)
    bus_emission = bus_value * commuting_factors.get("Commuting Factor_Bus", 0)
    taxi_emission = taxi_value * commuting_factors.get("Commuting Factor_Taxi", 0)
    total_emission = subway_emission + bus_emission + taxi_emission
    # Return as a dictionary to store in dcc.Store
    global_data['commuting'] = {"Subway Emission": subway_emission,
                                "Bus Emission": bus_emission,
                                "Taxi Emission": taxi_emission,
                                "Total Emission": total_emission}
    print("Commuting emissions calculated:", global_data['commuting'])
    return {
        "Subway Emission": subway_emission,
        "Bus Emission": bus_emission,
        "Taxi Emission": taxi_emission,
        "Total Emission": total_emission
    }
if 'manual_data' in global_data:
    print("manual_data after commuting",global_data['manual_data'])
@app.callback(
    Output('output-calculation', 'children'),
    Input('commuting-emission-results-store', 'data')
)
def display_emissions(emissions_data):
    if emissions_data is None or "error" in emissions_data:
        return emissions_data.get("error", "No emissions data calculated.")

    # Format the result
    return html.Div([
        html.P(f"Subway Emission: {emissions_data['Subway Emission']:.2f} units"),
        html.P(f"Bus Emission: {emissions_data['Bus Emission']:.2f} units"),
        html.P(f"Taxi Emission: {emissions_data['Taxi Emission']:.2f} units"),
        html.P(f"Total Emission: {emissions_data['Total Emission']:.2f} units"),
    ])

# Business Travel and Procurement Emissions Calculation
def calculate_business_emissions(travel_hotel, travel_flight, airline_km, diesel_truck_km, electric_truck_km):
    hotel_factor = business_travel_procurement_factors["Business Travel"]["Business Travel-Hotel"]
    flight_factor = business_travel_procurement_factors["Business Travel"]["Business Travel-Flight"]
    airline_factor = business_travel_procurement_factors["Business Procurement"]["Airline"]
    diesel_truck_factor = business_travel_procurement_factors["Business Procurement"]["Diesel Truck"]
    electric_truck_factor = business_travel_procurement_factors["Business Procurement"]["Electric Truck"]

    # Calculate emissions for each category
    hotel_emission = travel_hotel * hotel_factor if travel_hotel else 0
    flight_emission = travel_flight * flight_factor if travel_flight else 0
    airline_emission = airline_km * airline_factor * 1000 if airline_km else 0
    diesel_truck_emission = diesel_truck_km * diesel_truck_factor * 1000 if diesel_truck_km else 0
    electric_truck_emission = electric_truck_km * electric_truck_factor * 1000 if electric_truck_km else 0

    # Total emissions
    total_emission_travel = hotel_emission + flight_emission
    total_emission_procurement = airline_emission + diesel_truck_emission + electric_truck_emission

    # Return individual emissions and totals for each category
    return {
        "Business Travel": {
            "Hotel Emission": hotel_emission,
            "Flight Emission": flight_emission,
            "Total Emission": total_emission_travel
        },
        "Business Procurement": {
            "Airline Emission": airline_emission,
            "Diesel Truck Emission": diesel_truck_emission,
            "Electric Truck Emission": electric_truck_emission,
            "Total Emission": total_emission_procurement
        }
    }

@app.callback(
    Output('business-travel-store', 'data'),
    Output('business-procurement-store', 'data'),
    [
        Input('business-travel-flight-input', 'value'),
        Input('business-travel-hotel-input', 'value'),
        Input('business-procurement-air-freight-input', 'value'),
        Input('business-procurement-diesel-truck-input', 'value'),
        Input('business-procurement-electric-truck-input', 'value')
    ]
)
def store_and_calculate_emissions(travel_flight, travel_hotel, airline_km, diesel_truck_km, electric_truck_km):
    # Calculate emissions based on inputs
    emissions = calculate_business_emissions(
        travel_hotel=travel_hotel,
        travel_flight=travel_flight,
        airline_km=airline_km,
        diesel_truck_km=diesel_truck_km,
        electric_truck_km=electric_truck_km
    )
    
    # Separate data for business travel and procurement
    travel_emissions = emissions["Business Travel"]
    procurement_emissions = emissions["Business Procurement"]
    global_data['business_travel'] = travel_emissions
    global_data['business_procurement'] = procurement_emissions
    print("Business travel emissions calculated:", travel_emissions)
    print("Business procurement emissions calculated:", procurement_emissions)
    return travel_emissions, procurement_emissions


@app.callback(
    Output('total-transportation-emissions-store', 'data'),
    [
        Input('commuting-emission-results-store', 'data'),
        Input('business-travel-store', 'data'),
        Input('business-procurement-store', 'data')
    ]
)
def calculate_total_transportation_emissions(commuting_data, business_travel_data, business_procurement_data):
    # Ensure data is available in all inputs
    if not commuting_data or not business_travel_data or not business_procurement_data:
        return {"error": "Emission data is missing for one or more categories."}
    
    # Extract total emissions from each data dictionary
    commuting_total = commuting_data.get("Total Emission", 0)
    business_travel_total = business_travel_data.get("Total Emission", 0)
    business_procurement_total = business_procurement_data.get("Total Emission", 0)

    # Calculate the total transportation emissions
    total_transportation_emission = commuting_total + business_travel_total + business_procurement_total
    global_data['total_transportation'] = total_transportation_emission
    print("Total transportation emissions calculated:", total_transportation_emission)
    return {
        "Commuting Emission": commuting_total,
        "Business Travel Emission": business_travel_total,
        "Business Procurement Emission": business_procurement_total,
        "Total Transportation Emission": total_transportation_emission
    }

def ghg_predictions(data):
    with open('../Group A/prediction models/scaler_xgb.pkl', 'rb') as scaler_file:
        scaler = pickle.load(scaler_file)

    with open('../Group A/prediction models/tuned_xgb_model.pkl', 'rb') as model_file:
        tuned_xgb_model = pickle.load(model_file)

    # Step 2: Apply log transformation to match training preprocessing
    new_data_df= np.log1p(data[['Energy', 'Waste', 'Water', 'Transportation']])
    # Step 3: Standardize the new data using the scaler
    new_data_scaled = scaler.transform(new_data_df)

    # Step 6: Predict GHG_Total using the trained model
    predicted_ghg_log = tuned_xgb_model.predict(new_data_scaled)

    # Step 7: Inverse log transform to get the original GHG_Total value
    predicted_ghg_total = np.expm1(predicted_ghg_log)
    data['total_ghg'] = predicted_ghg_total
    data['ghg_intensity_predicted'] = data['total_ghg'] / data['GFA']
    # Create an instance of the validator
    validator = GreenMarkValidator()

    # Predict Green Mark levels for the 'ghg_intensity' column
    if 'ghg_intensity_predicted' not in data.columns:
        raise KeyError("Column 'ghg_intensity' not found in the DataFrame.")
    results_df = validator.predict_green_mark(data['ghg_intensity_predicted'])

    # Add the results as new columns in the original DataFrame
    data[['predicted_greenmarks', 'threshold']] = results_df[['predicted_level', 'threshold']]
    return data
    # Step 8: Output the prediction results

'''
# Ensure all required keys are present in the dictionaries
required_keys_manual = ['Water', 'Waste', 'Energy', 'Size']
required_keys_transportation = ['Total Transportation Emission']
data_manual = global_data.get('manual_data', {})
print("data_manual before predictions", data_manual)
if data_manual and all(key in data_manual for key in required_keys_manual) and all(key in data_transportation for key in required_keys_transportation):
    
    data_commute = global_data.get('commuting', {})
    data_travel = global_data.get('business_travel', {})
    data_procurement = global_data.get('business_procurement', {})
    data_transportation = global_data.get('transportation', {})
    data_for_predictions = {
        'Water': data_manual['Water'],
        'Waste': data_manual['Waste'],
        'Energy': data_manual['Energy'],
        'Transportation': data_transportation['Total Transportation Emission'],
        'GFA': data_manual['Size']
    }
    
else:
    data_for_predictions = {}
# Define layout for the new page - Model Visualization with Highlights

if data_for_predictions:
    # Convert data_for_predictions to a DataFrame
    data_for_predictions_df = pd.DataFrame([data_for_predictions])

    # Now you can pass it to the function
    ghg_manual_prediction = ghg_predictions(data_for_predictions_df)


print(data_for_predictions)
# DATA FOR PREDICTIONS WILL CONTAIN water, waste, energy, transportation, ghg  
'''


global data_for_predictions
data_for_predictions = {}
# Gather data from various sources and check for required fields
# Add the `next-report-button` as Input and add a new Output for page navigation.


# Ensure "next-button" and "output-ghg-prediction" exist in the layout
@app.callback(
    [
        Output("output-ghg-prediction", "data"),  # Stores prediction results if calculation succeeds
        Output("next-button", "href"),            # Controls the navigation link based on success
    ],
    Input("next-button", "n_clicks"),
    [
        State('total-transportation-emissions-store', 'data'),
        State('manual-data-store', 'data')
    ]
)
def process_and_navigate(n_clicks, transport_data, manual_data):
    # Check if the next button has been clicked
    if not n_clicks:
        raise PreventUpdate  # Do nothing until the button is clicked

    # Verify that all input data sources are present
    if not (transport_data and manual_data):
        return {"error": "Some input data is missing."}, None

    # Construct data for predictions
    data_for_predictions = {
        'Water': manual_data.get('Water', 0),
        'Waste': manual_data.get('Waste', 0),
        'Energy': manual_data.get('Energy', 0),
        'Transportation': transport_data.get("Total Emission", 0),
        'GFA': manual_data.get('Size', 0)
    }
    
    # Check all required fields exist and are not None
    required_fields = ['Water', 'Waste', 'Energy', 'Transportation', 'GFA']
    if not all(data_for_predictions[field] is not None for field in required_fields):
        return {"error": "Some required fields are missing for GHG prediction."}, None

    # Run predictions
    try:
        data_for_predictions_df = pd.DataFrame([data_for_predictions])
        prediction_results = ghg_predictions(data_for_predictions_df)  # Call your prediction function
        print("Prediction results:", prediction_results)  # Debugging print

        # Set navigation link to proceed if calculation succeeds
        return prediction_results, "/page-3-manual"

    except Exception as e:
        # Log the error and do not navigate
        print(f"Prediction error: {e}")
        return {"error": f"Prediction error: {str(e)}"}, None



'''
if 'prediction_results' in global_data:
    global_data['prediction_results'].to_csv('./datasets/prediction_results.csv', index=False)
page_3_manual_layout = dbc.Container([
    # Logo and Header
    html.Div(
        html.Img(
            src='./assets/teamlogo.png',
            style={'width': '220px', 'height': 'auto'}
        ),
        id="new-page-logo-wrapper",
        style={'position': 'absolute', 'top': '55px', 'right': '40px', 'transition': 'right 0.3s ease'}
    ),

    dbc.Row([
        dbc.Col(html.H1("Model Visualization and Analysis",
                        className="text-center",
                        style={"fontWeight": "bold", "marginTop": "20px", "marginBottom": "40px"}))
    ]),

    # Award Circle
    dbc.Row([
        dbc.Col(html.Div([
            html.H4("Total GHG", className="award-circle-header"),
            html.Div(f"{data_for_predictions.get('total_ghg', 0.0):.2f}", className="award-circle-value"),
        ], className="award-circle", style={
            "borderRadius": "50%",
            "minWidth": "100px", "minHeight": "100px",  # Minimum size
            "padding": "10px 20px",  # Padding for dynamic resizing
            "display": "flex", "alignItems": "center", "justifyContent": "center",
            "fontWeight": "bold", "fontSize": "20px", "backgroundColor": "#a8d08d",
            "color": "#333", "margin": "auto"
        }), width="auto"),
        
        dbc.Col(html.Div([
            html.H4("GHG Intensity", className="award-circle-header"),
            html.Div(f"{data_for_predictions.get('ghg_intensity_predicted', 0.0):.2f}", className="award-circle-value"),
        ], className="award-circle", style={
            "borderRadius": "50%",
            "minWidth": "100px", "minHeight": "100px",
            "padding": "10px 20px",
            "display": "flex", "alignItems": "center", "justifyContent": "center",
            "fontWeight": "bold", "fontSize": "20px", "backgroundColor": "#9ACD32",
            "color": "#333", "margin": "auto"
        }), width="auto"),

        dbc.Col(html.Div([
            html.H4("Green Mark", className="award-circle-header"),
            html.Div(f"{data_for_predictions.get('predicted_greenmarks', 0.0):.2f}", className="award-circle-value"),
        ], className="award-circle", style={
            "borderRadius": "50%",
            "minWidth": "100px", "minHeight": "100px",
            "padding": "10px 20px",
            "display": "flex", "alignItems": "center", "justifyContent": "center",
            "fontWeight": "bold", "fontSize": "20px", "backgroundColor": "#87CEEB",
            "color": "#333", "margin": "auto"
        }), width="auto"),
    ], justify="center", className="mb-5"),

    # GHG Intensity Cloud Shape
    dbc.Row([
        dbc.Col(html.Div("GHG Intensity", className="ghg-cloud",
                         style={
                             "borderRadius": "50%",
                             "width": "200px",
                             "height": "100px",
                             "backgroundColor": "#9ACD32",  # Example color for cloud
                             "display": "flex",
                             "alignItems": "center",
                             "justifyContent": "center",
                             "fontSize": "20px",
                             "fontWeight": "bold",
                             "color": "white",
                             "padding": "10px"
                         }), width="auto")
    ], justify="center", className="mb-5"),

    # Violin Plot Section
    dbc.Row([
        dbc.Col(dcc.Graph(id='violin-plot'), width=6),
    ], justify="center", className="mb-5"),

    # Doughnut Plots for Emissions
    dbc.Row([
        dbc.Col(dcc.Graph(id='commuting-emission-donut'), width=4),
        dbc.Col(dcc.Graph(id='business-travel-donut'), width=4),
        dbc.Col(dcc.Graph(id='business-procurement-donut'), width=4),
    ], className="mb-5"),

    # Button to navigate to the next page
    dbc.Row([
        dbc.Col([
            dbc.Button("Next: Generate Report", id="next-report-button", color="success", href='/page-4',
                       style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'fontWeight': 'bold'}),
        ], width=3),
    ], justify="center", className="mt-4 mb-5"),
], fluid=True)

# Violin Plot Callback with Manual Predicted GHG Highlight
@app.callback(
    Output('violin-plot', 'figure'),
    Input('total-transportation-emissions-store', 'data')
)
def update_violin_plot(predicted_ghg_value):
    # Use the dataset to generate the violin plot
    df['GHG_Total_Log'] = np.log(df['GHG_Total'] + 1)

    fig = go.Figure()
    fig.add_trace(go.Violin(
        x=df['GHG_Total_Log'],
        name='GHG Emissions (Log Transformed)',
        box_visible=True,
        meanline_visible=True,
        fillcolor='lightblue',
        line_color='darkblue',
        opacity=0.6,
        orientation='h'
    ))
    fig.add_trace(go.Scatter(
        y=['GHG Emissions (Log Transformed)'] * len(df),
        x=df['GHG_Total_Log'],
        mode='markers',
        marker=dict(size=6, color='rgba(0, 128, 0, 0.5)', symbol='circle')
    ))

    # Highlight manual predicted GHG
    fig.add_trace(go.Scatter(
        y=['GHG Emissions (Log Transformed)'],
        x=[np.log(predicted_ghg_value + 1)],  # Log transform of the predicted value
        mode='markers',
        marker=dict(size=14, color='orange', symbol='diamond'),
        name="Manual Predicted GHG"
    ))

    fig.update_layout(
        title="GHG Emissions (Log Transformed) with Manual Prediction Highlight",
        yaxis_title='Building',
        xaxis_title='Log of Total GHG Emissions (ton)',
        plot_bgcolor='rgba(240, 240, 240, 1)',
        showlegend=False
    )
    return fig

# Doughnut Plot Callbacks

@app.callback(
    Output('commuting-emission-donut', 'figure'),
    Input('commuting-emission-results-store', 'data')
)
def update_commuting_donut(data):
    fig = px.pie(
        names=["Subway", "Bus", "Taxi"],
        values=[data.get('Subway Emission', 0), data.get('Bus Emission', 0), data.get('Taxi Emission', 0)],
        title="Commuting Emission Breakdown",
        hole=0.4
    )
    return fig

@app.callback(
    Output('business-travel-donut', 'figure'),
    Input('business-travel-store', 'data')
)
def update_business_travel_donut(data):
    fig = px.pie(
        names=["Hotel", "Flight"],
        values=[data.get('Hotel Emission', 0), data.get('Flight Emission', 0)],
        title="Business Travel Emission Breakdown",
        hole=0.4
    )
    return fig

@app.callback(
    Output('business-procurement-donut', 'figure'),
    Input('business-procurement-store', 'data')
)
def update_business_procurement_donut(data):
    fig = px.pie(
        names=["Airline", "Diesel Truck", "Electric Truck"],
        values=[data.get('Airline Emission', 0), data.get('Diesel Truck Emission', 0), data.get('Electric Truck Emission', 0)],
        title="Business Procurement Emission Breakdown",
        hole=0.4
    )
    return fig

'''

building_data = {
    'Building Name': 'EQUINIX SG3 DATA CENTRE',
    'Postcode': 139963,
    'Year': 2021,
    'Address': '26A AYER RAJAH CRESCENT, SINGAPORE 139963',
    'Employee': 3349,
    'Transportation': 20294264.86,
    'GFA': 35218,
    'Energy': 156833001,
    'Waste': 303.36,
    'Water': 96114.60,
    'GHG_Total': 3924.95,
    'GHG_Intensity': 0.11,
    'Award': 'platinum',
}

scope_data = {'Scope 1': 82.33,
              'Scope 2': 1884.79,
              'Scope 3': 1868.68
}
# Create a bar plot for scope data using Plotly Express
fig_scope_bar = px.bar(
    x=list(scope_data.keys()),
    y=list(scope_data.values()),
    title="Proportion of Emissions by Scope",
    labels={'x': 'Scope', 'y': 'Emissions (tCO2e)'},
    color=list(scope_data.keys()),
    color_discrete_sequence=px.colors.qualitative.Pastel
)

# Customize the layout
fig_scope_bar.update_layout(
    xaxis_title="Scope",
    yaxis_title="Emissions (tCO2e)",
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(size=14),
    showlegend=False
)

# Add the graph beside the table
dbc.Row([
    dbc.Col(dbc.Table(
        [
            html.Thead(html.Tr([html.Th("Attribute"), html.Th("Value")])),
            html.Tbody([
                html.Tr([html.Td("Postcode"), html.Td(building_data['Postcode'])]),
                html.Tr([html.Td("Year"), html.Td(building_data['Year'])]),
                html.Tr([html.Td("Address"), html.Td(building_data['Address'])]),
                html.Tr([html.Td("Employee Count"), html.Td(building_data['Employee'])]),
                html.Tr([html.Td("Transportation Emissions"), html.Td(f"{building_data['Transportation']:.2f}")]),
                html.Tr([html.Td("Gross Floor Area (GFA)"), html.Td(building_data['GFA'])]),
                html.Tr([html.Td("Energy Consumption"), html.Td(building_data['Energy'])]),
                html.Tr([html.Td("Waste"), html.Td(f"{building_data['Waste']:.2f}")]),
                html.Tr([html.Td("Water Usage"), html.Td(f"{building_data['Water']:.2f}")]),
                html.Tr([html.Td("GHG Total"), html.Td(f"{building_data['GHG_Total']:.2f}")]),
                html.Tr([html.Td("GHG Intensity"), html.Td(f"{building_data['GHG_Intensity']:.5f}")]),
                html.Tr([html.Td("Award"), html.Td(building_data['Award'].capitalize())]),
            ])
        ],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True
    ), width=6),
    dbc.Col(dcc.Graph(figure=fig_scope_bar), width=6)
], justify='center', className="mb-4")
# Synthetic Doughnut Data
commuting_emission_data = {
    'Subway Emission': 400,
    'Bus Emission': 1000,
    'Taxi Emission': 250
}

business_travel_data = {
    'Hotel Emission': 1500,
    'Flight Emission': 12000
}

business_procurement_data = {
    'Airline Emission': 5000,
    'Diesel Truck Emission': 200,
    'Electric Truck Emission': 30
}

space_distribution_data = {
    'Office': 70,
    'Retail': 20,
    'Parking': 10
}

# Bar Chart for Space Distribution with darker and more distinctive green shades
fig_space_distribution_bar = px.bar(
    x=list(space_distribution_data.keys()),
    y=list(space_distribution_data.values()),
    title="Building Space Distribution",
    labels={'x': 'Space Type', 'y': 'Percentage (%)'},
    color=list(space_distribution_data.keys()),
    color_discrete_sequence=['#006400', '#228B22', '#2E8B57', '#32CD32']  # Darker distinctive greens
)

# Customize the layout for Space Distribution Bar Chart
fig_space_distribution_bar.update_layout(
    xaxis_title="Space Type",
    yaxis_title="Percentage (%)",
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(size=14),
    showlegend=False
)

# Doughnut Charts with darker and more distinctive green shades
fig_commuting_donut = px.pie(
    names=list(commuting_emission_data.keys()),
    values=list(commuting_emission_data.values()),
    title="Commuting Emission Breakdown",
    hole=0.4,
    color_discrete_sequence=['#006400', '#228B22', '#2E8B57', '#32CD32']  # Darker distinctive greens
)

fig_business_travel_donut = px.pie(
    names=list(business_travel_data.keys()),
    values=list(business_travel_data.values()),
    title="Business Travel Emission Breakdown",
    hole=0.4,
    color_discrete_sequence=['#9ACD32', '#3CB371', '#2E8B57', '#32CD32']
)


fig_business_procurement_donut = px.pie(
    names=list(business_procurement_data.keys()),
    values=list(business_procurement_data.values()),
    title="Business Procurement Emission Breakdown",
    hole=0.4,
    color_discrete_sequence=['#9ACD32', '#3CB371', '#2E8B57', '#32CD32']
)

benchmarks = {
    'Platinum': 0.1,
    'GoldPLUS': 0.12,
    'Gold': 0.15,
    'Certified': 0.2
}
current = building_data['GHG_Intensity']

# Create bar chart data
x = ['Current'] + list(benchmarks.keys())
y = [current] + list(benchmarks.values())
#colors = ['#28a745'] + ['#007bff'] * len(benchmarks)
# Green Mark Benchmarks with darker and more distinctive green shades
fig = go.Figure(data=[
    go.Bar(
        x=x,
        y=y,
        marker_color=['#9ACD32', '#3CB371', '#2E8B57', '#32CD32', '#013220']  # Darker distinctive greens
    )
])

# Customize layout
fig.update_layout(
    title='Green Mark Benchmarks',
    yaxis_title='GHG Intensity (tCO2e/m²)',
    xaxis_title='',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(size=14),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor='lightgrey')
)
# Add performance analysis
current_level = building_data['Award']
next_level = 'GoldPLUS' if current_level == 'Gold' else 'Gold' if current_level == 'Certified' else None
# Add performance analysis
if next_level:
    next_threshold = benchmarks[next_level]
    improvement = ((current - next_threshold) / current) * 100
    analysis_text = f"Below threshold by {abs(improvement):.2f}%\nNext Level: {next_level}"
    fig.add_annotation(
        text=analysis_text,
        xref="paper", yref="paper",
        x=0.5, y=-0.2,
        showarrow=False,
        font=dict(size=12, color='#006400')  # Dark green for annotation
    )
# Add the graph beside the table
dbc.Row([
    dbc.Col(dbc.Table(
        [
            html.Thead(html.Tr([html.Th("Attribute"), html.Th("Value")])),
            html.Tbody([
                html.Tr([html.Td("Postcode"), html.Td(building_data['Postcode'])]),
                html.Tr([html.Td("Year"), html.Td(building_data['Year'])]),
                html.Tr([html.Td("Address"), html.Td(building_data['Address'])]),
                html.Tr([html.Td("Employee Count"), html.Td(building_data['Employee'])]),
                html.Tr([html.Td("Transportation Emissions"), html.Td(f"{building_data['Transportation']:.2f}")]),
                html.Tr([html.Td("Gross Floor Area (GFA)"), html.Td(building_data['GFA'])]),
                html.Tr([html.Td("Energy Consumption"), html.Td(building_data['Energy'])]),
                html.Tr([html.Td("Waste"), html.Td(f"{building_data['Waste']:.2f}")]),
                html.Tr([html.Td("Water Usage"), html.Td(f"{building_data['Water']:.2f}")]),
                html.Tr([html.Td("GHG Total"), html.Td(f"{building_data['GHG_Total']:.2f}")]),
                html.Tr([html.Td("GHG Intensity"), html.Td(f"{building_data['GHG_Intensity']:.5f}")]),
                html.Tr([html.Td("Award"), html.Td(building_data['Award'].capitalize())]),
            ])
        ],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True
    ), width=6),
    
], justify='center', className="mb-4")

page_3_manual_layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2(building_data['Building Name'], className="text-center mb-4"))
    ]),

    # Building Information Table
    dbc.Row([
        dbc.Col(dbc.Table(
            [
                html.Thead(html.Tr([html.Th("Attribute"), html.Th("Value")])),
                html.Tbody([
                    html.Tr([html.Td("Postcode"), html.Td(building_data['Postcode'])]),
                    html.Tr([html.Td("Year"), html.Td(building_data['Year'])]),
                    html.Tr([html.Td("Address"), html.Td(building_data['Address'])]),
                    html.Tr([html.Td("Employee Count"), html.Td(building_data['Employee'])]),
                    html.Tr([html.Td("Transportation Emissions"), html.Td(f"{building_data['Transportation']:.2f}")]),
                    html.Tr([html.Td("Gross Floor Area (GFA)"), html.Td(building_data['GFA'])]),
                    html.Tr([html.Td("Energy Consumption"), html.Td(building_data['Energy'])]),
                    html.Tr([html.Td("Waste"), html.Td(f"{building_data['Waste']:.2f}")]),
                    html.Tr([html.Td("Water Usage"), html.Td(f"{building_data['Water']:.2f}")]),
                    html.Tr([html.Td("GHG Total"), html.Td(f"{building_data['GHG_Total']:.2f}")]),
                    html.Tr([html.Td("GHG Intensity"), html.Td(f"{building_data['GHG_Intensity']:.5f}")]),
                    html.Tr([html.Td("Award"), html.Td(building_data['Award'].capitalize())]),
                ])
            ],
            bordered=True,
            hover=True,
            responsive=True,
            striped=True
        ), width=6),
        dbc.Col(dcc.Graph(figure=fig), width=6)
    ], justify = 'center', className="mb-4"),

    # Key Metrics Cards
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Total GHG", className="text-center font-weight-bold"),
            dbc.CardBody(html.Div(f"{building_data['GHG_Total']:.2f}", className="text-center", style={"fontSize": "24px"}))
        ], style={
            "width": "150px", "margin": "auto", "backgroundColor": "#a8d08d",
            "color": "#333", "borderRadius": "8px"
        }), width="auto"),

    dbc.Col(dbc.Card([
        dbc.CardHeader("GHG Intensity", className="text-center font-weight-bold"),
        dbc.CardBody(html.Div(f"{building_data['GHG_Intensity']:.5f}", className="text-center", style={"fontSize": "24px"}))
    ], style={
        "width": "150px", "margin": "auto", "backgroundColor": "#9ACD32",
        "color": "#333", "borderRadius": "8px"
    }), width="auto"),

    dbc.Col(dbc.Card([
        dbc.CardHeader("Award", className="text-center font-weight-bold"),
        dbc.CardBody(html.Div(building_data['Award'].capitalize(), className="text-center", style={"fontSize": "24px"}))
    ], style={
        "width": "150px", "margin": "auto", "backgroundColor": "#87CEEB",
        "color": "#333", "borderRadius": "8px"
    }), width="auto"),
    ], justify="center", className="mb-5"),


    # Doughnut Plots Section
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_commuting_donut), width=4),
        dbc.Col(dcc.Graph(figure=fig_business_travel_donut), width=4),
        dbc.Col(dcc.Graph(figure=fig_business_procurement_donut), width=4),
        dbc.Col(dcc.Graph(figure=fig_space_distribution_bar), width=4),
        dbc.Col(dcc.Graph(figure=fig_scope_bar), width=4)
    ], className="mb-5")
], fluid=True)

selected_columns = ['Employee', 'Transportation', 'Water', 'Waste', 'Energy', 'GFA', 'EUI']

# Define layout for Page 2 - Data Quality Check and EDA
page_2_layout = dbc.Container([
    # Logo and Header
    html.Div(
        html.Img(
            src='./assets/teamlogo.png',
            style={
                'width': '220px',
                'height': 'auto',
                'marginTop': '10px'
            }
        ),
        id="page-2-logo-wrapper",
        style={
            'position': 'absolute',
            'top': '40px',
            'right': '55px',
            'transition': 'right 0.3s ease'
        }
    ),
    
    # Title Section
    dbc.Row([
        dbc.Col(html.H1("Data Quality Check and Exploratory Data Analysis",
                        style={"fontWeight": "bold", "marginTop": "80px", "marginBottom": "30px", "color": "#333", "fontFamily": "Montserrat, sans-serif", "fontSize": "32px"}))
    ]),

    # Missing Data Summary Section
    dbc.Card([
        dbc.CardHeader("Missing Data Summary", style={
            "backgroundColor": "#A8D5BA", "color": "#2F4F4F",
            "fontWeight": "600", "fontSize": "24px", "textAlign": "left"}),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(dash_table.DataTable(id='missing-data-table', style_table={'overflowX': 'auto'}), width=12),
            ])
        ])
    ], className="mt-4 mb-4"),

    # Visualization of Data Completeness
    dbc.Card([
        dbc.CardHeader("Visualization of Data Completeness", style={
            "backgroundColor": "#A8D5BA", "color": "#2F4F4F",
            "fontWeight": "600", "fontSize": "24px", "textAlign": "left"}),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(dcc.Graph(id='completeness-graph', style={"height": "400px"}), width=12),
            ]),
        ])
    ], className="mb-4"),
# Message Card for Missing Data Handling
    dbc.Card([
        dbc.CardBody([
            html.P(
                [
                    "Please be rest assured the missing data points are automatically treated.", 
                    html.Br(),
                    "You can find out more information in our extended summary and reupload."
                ],
                style={
                    "fontSize": "18px",  # Increased font size for better visibility
                    "color": "#2E8B57",  # Distinct green color for emphasis
                    "fontFamily": "Montserrat, sans-serif",
                    "marginBottom": "0px",
                    "textAlign": "left",
                    "fontWeight": "bold"  # Bold text for emphasis
                }
            )
        ])
    ], className="mb-4"),
    # EDA Section Header
    dbc.Card([
        dbc.CardHeader("Exploratory Data Analysis", style={
            "backgroundColor": "#A8D5BA", "color": "#2F4F4F",
            "fontWeight": "600", "fontSize": "24px", "textAlign": "left"}),
        dbc.CardBody([
        # Toggle Button
            dbc.Row([
                dbc.Col([
                    dbc.Button("Hide EDA Plots", id="toggle-eda-visibility", color="primary", style={"width": "100%", "marginBottom": "15px"})
                ], width=3)
            ]),

        # Container for the EDA Plots
            dbc.Collapse(
                dbc.Row([
                    dbc.Col(dcc.Graph(id='histograms', style={"height": "400px", "width": "100%"}), width=12),
                    dbc.Col(dcc.Graph(id='box-plots', style={"height": "400px", "width": "100%"}), width=12)
                ]),
                id="eda-collapse",
                is_open=False  # Default state is expanded
            ),
        ])
    ], className="mb-4"),

    # Missing Data Details Section
    dbc.Card([
            dbc.CardHeader("Missing Data Details (If you want to check and fill out the missing values)", style={
                "backgroundColor": "#A8D5BA", "color": "#2F4F4F",
                "fontWeight": "600", "fontSize": "24px", "textAlign": "left"}),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(
                        dbc.Button(
                            "Show Missing Data Table", id="toggle-missing-data", color="primary", style={"width": "100%"}
                        ), width=3
                    )
                ], className="mb-3"),
                dbc.Collapse(
                    dash_table.DataTable(
                        id='missing-data-details-table',
                        style_table={'overflowX': 'auto', 'marginTop': '20px'},
                        style_cell={
                            'textAlign': 'center',
                            'fontFamily': 'Montserrat, sans-serif',
                            'padding': '10px',
                            'fontSize': '14px'
                        },
                        style_header={
                            'backgroundColor': '#A8D5BA',
                            'fontWeight': 'bold',
                            'textAlign': 'center'
                    }
                    ),
                    id="missing-data-collapse",
                    is_open=False  # Default state is collapsed
                )
            ])
    ], className="mb-4"),


    # Navigation Buttons
    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.A("Next: Model Running and Comparison", href='/page-3', style={'width': '100%', 'padding': '10px', 'borderRadius': '8px', 'fontWeight': 'bold', 'fontFamily': 'Montserrat, sans-serif', 'fontSize': '16px'}),
                ]),
                style={'boxShadow': '0 4px 8px rgba(2, 8, 5, 7)', 'borderRadius': '8px'}
            ),
        ], width=3),
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.A("Reupload Data", href='/page-1', style={'width': '100%', 'padding': '10px', 'borderRadius': '8px', 'fontWeight': 'bold', 'fontFamily': 'Montserrat, sans-serif', 'fontSize': '16px'}),
                ]),
                style={'boxShadow': '0 4px 8px rgba(2, 8, 5, 7)', 'borderRadius': '8px'}
            ),
        ], width=3),
    ], justify="center", className="mt-4 mb-5")
], fluid=True)


@app.callback(
    [Output("eda-collapse", "is_open"), Output("toggle-eda-visibility", "children")],
    Input("toggle-eda-visibility", "n_clicks"),
    State("eda-collapse", "is_open"),
)
def toggle_eda_plots(n_clicks, is_open):
    # Toggle the collapse state
    if n_clicks:
        is_open = not is_open

    # Update the button text based on the state
    button_text = "Show EDA Plots" if not is_open else "Hide EDA Plots"
    return is_open, button_text


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

@app.callback(
    [Output('missing-data-table', 'data'), Output('completeness-graph', 'figure')],
    Input('url', 'pathname')
)
def display_missing_data(pathname):
    if pathname == '/page-2' and 'uploaded_df' in global_data:
        df = global_data['uploaded_df']
        
        # Calculate missing data statistics
        missing_data = df.isnull().sum().reset_index()
        missing_data.columns = ['Column', 'Missing Values']
        # Filter only columns with missing values
        missing_data = missing_data[missing_data['Missing Values'] > 0]
        
        if not missing_data.empty:
            # Convert missing data summary to dict for dash_table
            table_data = missing_data.to_dict('records')
            
            # Plot missing data as a bar chart
            fig = px.bar(
                missing_data, x='Column', y='Missing Values',
                title='Missing Data Percentage by Column',
                labels={'Number of Missing Values'},
                color='Column'
            )
            
            return table_data, fig
        
        # No missing data case
        return [], go.Figure().update_layout(title="No missing data found, please proceed.")
    return [], go.Figure()

@app.callback(
    Output('action-prompt', 'children'),
    Input('missing-data-table', 'data')
)
def show_action_prompt(missing_data):
    if missing_data:
        # Check if there is any missing data
        missing_exists = any(row['Missing Values'] > 0 for row in missing_data)
        if missing_exists:
            return html.Div([
                html.P("Missing data detected. Please choose an action:"),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("Drop All Missing", id="drop-missing-button", color="danger", className="mr-2"),
                    ], width="auto"),
                    dbc.Col([
                        dbc.Button("Fill Out Missing Values and Re-upload", id="reupload-prompt-button", color="primary", className="ml-2", href='/')
                    ], width="auto"),
                ])
            ])
    return html.Div()  # Return empty if no missing data

@app.callback(
    Output('eda-output', 'children'),
    Input('drop-missing-button', 'n_clicks')
)
def drop_missing_data(n_clicks):
    if n_clicks:
        if 'uploaded_df' in global_data:
            global_data['uploaded_df'] = global_data['uploaded_df'].dropna()  # Drop rows with any missing values
            return html.Div([
                html.P("All rows with missing values have been dropped."),
                dash_table.DataTable(
                    data=global_data['uploaded_df'].head().to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in global_data['uploaded_df'].columns],
                    style_table={'overflowX': 'auto'}
                )
            ])
    return None

@app.callback(
    Output('summary-statistics-table', 'data'),
    Input('url', 'pathname')
)
def display_summary_statistics(pathname):
    if pathname == '/page-2' and 'uploaded_df' in global_data:
        df = global_data['uploaded_df'][selected_columns]
        
        # Calculate summary statistics
        summary_stats = df.describe().transpose().reset_index()
        summary_stats.columns = ['Column', 'Count', 'Mean', 'Std', 'Min', '25%', '50%', '75%', 'Max']
        
        # Convert summary statistics to dict for dash_table
        table_data = summary_stats.to_dict('records')
        
        return table_data
    
    return []


# eda histogram and 

@app.callback(
    [Output('histograms', 'figure'), Output('box-plots', 'figure')],
    Input('url', 'pathname')
)
def display_eda_visualizations(pathname):
    if pathname == '/page-2' and 'uploaded_df' in global_data:
        df = global_data['uploaded_df'][selected_columns]
        
        # Compact Histograms - two histograms per row
        num_columns = 2
        num_rows = (len(selected_columns) + 1) // num_columns
        histograms_fig = make_subplots(rows=num_rows, cols=num_columns, subplot_titles=selected_columns, vertical_spacing=0.05, horizontal_spacing=0.05)
        
        for i, col in enumerate(selected_columns):
            row = i // num_columns + 1
            col_pos = i % num_columns + 1
            histograms_fig.add_trace(
                go.Histogram(x=df[col], name=col),
                row=row, col=col_pos
            )
        
        # Set layout properties for compact view
        histograms_fig.update_layout(
            title='Histograms of Selected Columns',
            height=150 * num_rows,  # Reduce height per row for compactness
            margin=dict(l=10, r=10, t=40, b=10),  # Narrow margins
            showlegend=False
        )
        histograms_fig.update_xaxes(tickangle=45, tickfont=dict(size=8))  # Smaller, rotated x-axis labels
        histograms_fig.update_yaxes(tickfont=dict(size=8), showgrid=False)  # Smaller y-axis labels, no grid

        # Compact Horizontal Boxplots - two boxplots per row
        box_plots_fig = make_subplots(rows=num_rows, cols=num_columns, subplot_titles=selected_columns, vertical_spacing=0.05, horizontal_spacing=0.05)
        
        for i, col in enumerate(selected_columns):
            row = i // num_columns + 1
            col_pos = i % num_columns + 1
            box_plots_fig.add_trace(
                go.Box(x=df[col], name=col, orientation="h"),  # Set orientation to horizontal
                row=row, col=col_pos
            )
        
        # Set layout properties for compact view
        box_plots_fig.update_layout(
            title='Boxplots of Selected Columns',
            height=150 * num_rows,  # Reduce height per row for compactness
            margin=dict(l=10, r=10, t=40, b=10),  # Narrow margins
            showlegend=False,
            boxmode='group'
        )
        box_plots_fig.update_xaxes(tickfont=dict(size=8))  # Smaller x-axis labels for horizontal orientation
        box_plots_fig.update_yaxes(tickangle=0, tickfont=dict(size=8), showgrid=False)  # Smaller y-axis labels, no grid
        
        return histograms_fig, box_plots_fig
    
    return go.Figure(), go.Figure()

@app.callback(
    Output('missing-data-collapse', 'is_open'),
    Input('toggle-missing-data', 'n_clicks'),
    State('missing-data-collapse', 'is_open')
)
def toggle_missing_data_table(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

@app.callback(
    Output('missing-data-details-table', 'data'),
    Input('url', 'pathname')
)
def populate_missing_data_details(pathname):
    if pathname == '/page-2' and 'uploaded_df' in global_data:
        df = global_data['uploaded_df']
        
        # Identify missing data details
        missing_details = df[df.isnull().any(axis=1)]  # Rows with missing data
        missing_details['Missing Columns'] = missing_details.isnull().apply(
            lambda row: ', '.join(missing_details.columns[row]), axis=1
        )
        # Limit to first 5 rows
        limited_missing_details = missing_details.loc[:5, :]
        
        # Convert to dictionary format for Dash table
        table_data = limited_missing_details.reset_index().to_dict('records')
        return table_data
    
    return []  # Default empty data if no missing data

selected_commuting_factors = {}


# Function to retrieve commuting factors for a specific region and store them globally
def set_commuting_factors(region):
    global selected_commuting_factors
    if region in commuting_factors:
        selected_commuting_factors = commuting_factors[region]
    else:
        selected_commuting_factors = {
            "Commuting Factor_Subway": 0,
            "Commuting Factor_Bus": 0,
            "Commuting Factor_Taxi": 0
        }
    return selected_commuting_factors  # Optionally return for immediate use



# need to process the paths for the data
df = pd.read_csv('./datasets/merged_df1.csv', encoding="latin-1", encoding_errors='ignore') if not ('uploaded_df' in global_data) else global_data['uploaded_df']
df = df.dropna()


ghg_predictions(df)







# Updated layout for Page 3 - Model Running and Visualization with Heatmap
page_3_layout = dbc.Container([
    # Logo and Header
    html.Div(
        html.Img(
            src='./assets/teamlogo.png',
            style={'width': '220px', 'height': 'auto'}
        ),
        id="page-3-logo-wrapper",
        style={'position': 'absolute', 'top': '55px', 'right': '40px', 'transition': 'right 0.3s ease'}
    ),
    
    # Title Section
    dbc.Row([
        dbc.Col(html.H1("Model Results and Benchmarking",
                        className="text-center",
                        style={"fontWeight": "bold", "marginTop": "20px", "marginBottom": "40px", "fontSize": "32px"}))
    ]),

    # Dropdown for Building Selection Section
    dbc.Card([
        dbc.CardHeader("Building Selection", style={
            "backgroundColor": "#A8D5BA", "color": "#2F4F4F",
            "fontWeight": "600", "fontSize": "24px", "textAlign": "left"}),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(html.H5("Select Building Name", style={"fontWeight": "600"})),
                dbc.Col(html.Hr(style={"borderTop": "1px solid #aaa", "width": "100%"}), width=12),
            ], className="mt-3 mb-2"),
            
            dbc.Row([
                dbc.Col(dcc.Dropdown(
                    id='dropdown-selection',
                    options=[{'label': name, 'value': name} for name in df["Building Name"].unique()],
                    value=None,
                    style={"width": "100%"}
                ), width=6),
            ]),
        ])
    ], className="mb-4"),

    # Model Results Visualizations Section
    dbc.Card([
        dbc.CardHeader("Green Mark Scheme Benchmarking and Trends", style={
            "backgroundColor": "#A8D5BA", "color": "#2F4F4F",
            "fontWeight": "600", "fontSize": "24px", "textAlign": "left"}),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(dcc.Graph(id='award'), width=6),
                dbc.Col(dcc.Graph(id='year_trend_line'), width=6),
            ]),
        ])
    ], className="mb-4"),

    # Additional Analysis Section with side-by-side doughnut charts
    dbc.Card([
        dbc.CardHeader("Performance Analysis", style={
            "backgroundColor": "#A8D5BA", "color": "#2F4F4F",
            "fontWeight": "600", "fontSize": "24px", "textAlign": "left"}),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(dcc.Graph(id='violin'), width=6),
                dbc.Col(dcc.Graph(id='pie_1'), width=3),
                dbc.Col(dcc.Graph(id='pie_2'), width=3),
            ]),
        ])
    ], className="mb-4"),
    # Transportation Contribution by Region Section with row split
    dbc.Card([
        dbc.CardHeader(
            "Transportation Contribution by Region Heatmaps", 
            style={
                "backgroundColor": "#A8D5BA",
                "color": "#2F4F4F",
                "fontWeight": "600",
                "fontSize": "24px",
                "textAlign": "left"
            }
        ),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.Img(src="assets/2.png", style={"width": "100%", "height": "auto"}),
                        html.Div(
                            "Please be reminded if you're in the high emission central region. Government regulations may apply to higher level emissions.",
                            style={
                                "color": "red",
                                "fontSize": "40px",
                                "fontWeight": "bold",
                                "textAlign": "center",
                                "marginTop": "10px"
                            }
                        )
                    ]),
                    width=12
                ),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col(
                    html.Img(src="assets/1.png", style={"width": "100%", "height": "auto"}),
                    width=12
                ),
            ])
        ])
    ], className="mb-4"),


    # Heatmap Section
    dbc.Card([
        dbc.CardHeader("Key Metrics Heatmap", style={
            "backgroundColor": "#A8D5BA", "color": "#2F4F4F",
            "fontWeight": "600", "fontSize": "24px", "textAlign": "left"}),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(dcc.Graph(id='heatmap'), width=12),
            ])
        ])
    ], className="mb-4"),

    # Button to navigate to the next page
    dbc.Row([
        dbc.Col([
            dbc.Button("Next: Generate Report", id="next-report-button", color="success", href='/page-4',
                       style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'fontWeight': 'bold'}),
        ], width=3),
    ], justify="center", className="mt-4 mb-5"),
], fluid=True)

# Callback to update the store
@app.callback(
    Output('selected-building-store', 'data'),
    Input('dropdown-selection', 'value')
)
def update_selected_building_store(selected_building):
    return selected_building

# Sidebar adjustment callback
@app.callback(
    Output("page-3-logo-wrapper", "style"),
    Input("toggle-button", "n_clicks"),
    State("page-3-logo-wrapper", "style")
)
def adjust_logo_position(n_clicks, current_style):
    if n_clicks and n_clicks % 2 != 0:  # Sidebar is visible
        current_style["right"] = "0px"  # Adjust to match sidebar width
    else:
        current_style["right"] = "40px"
    return current_style

@app.callback(
    Output('year_trend_line', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_line_chart(selected_building):
    # Check if a building is selected
    if not selected_building:
        raise dash.exceptions.PreventUpdate
    if selected_building and selected_building.strip() and selected_building in df['Building Name'].values:
        # Filter the DataFrame for the selected building
        building_data = df[df['Building Name'] == selected_building]
        
        # Group data by YearDate and calculate the mean total GHG for the selected building
        year_trend_df = building_data.groupby('Year').agg({'total_ghg': 'mean'}).reset_index()

        # Create the line chart
        fig = px.line(
            year_trend_df,
            x='Year',
            y='total_ghg',
            title=f"Greenhouse Gas Emissions Over Time for {selected_building}",
            labels={
                "total_ghg": "Total Greenhouse Gas Emissions (tCO₂e/m²)",
                "Year": "Year"
            }
        )
        # Customize line color and layout
        fig.update_traces(line=dict(color="#365E32"))
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            font=dict(size=14)
        )
    else:
        # If no valid building is selected, display a placeholder message
        fig = go.Figure()
        fig.add_annotation(
            text="Please select a valid building name to view its emissions trend.",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=16, color="red")
        )
        fig.update_layout(
            title="Greenhouse Gas Emissions Over Time",
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

    return fig


# Benchmarking Callback - Award Bar Chart

@app.callback(
    Output('award', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_combined_chart(selected_building):
    # Awards distribution plot
    bar_data = df.groupby('predicted_greenmarks').agg(unique_building_count=('Building Name', 'nunique')).reset_index()

    color_map = {
        'certified': '#a8d08d',   # Light Green
        'gold': '#ffd966',        # Yellow
        'goldplus': '#e6b800',    # Darker Yellow/Gold
        'platinum': '#4b830d'     # Dark Green
    }
    colors = [color_map.get(level.lower(), '#333333') for level in bar_data['predicted_greenmarks']]

    awards_fig = go.Figure(data=[go.Bar(
        x=bar_data['predicted_greenmarks'],
        y=bar_data['unique_building_count'],
        text=bar_data['unique_building_count'],
        textposition='auto',
        marker=dict(color=colors),
        hoverinfo='text',
        hovertext=[f"{level}: {count} buildings" for level, count in zip(bar_data['predicted_greenmarks'], bar_data['unique_building_count'])]
    )])

    awards_fig.update_layout(
        title=dict(
            text="Awards Distribution",
            font=dict(size=20, family="Arial, sans-serif", color="#333333"),
            x=0.5
        ),
        xaxis=dict(
            title="Green Mark Level",
            titlefont=dict(size=16, family="Arial, sans-serif", color="#333333"),
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=14, color="#333333"),
            tickangle=0
        ),
        yaxis=dict(
            title="Unique Building Count",
            titlefont=dict(size=16, family="Arial, sans-serif", color="#333333"),
            showgrid=True,
            gridcolor="rgba(200, 200, 200, 0.3)",
            zeroline=False,
            tickfont=dict(size=14, color="#333333"),
        ),
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#f9f9f9",
        showlegend=False,
        margin=dict(l=40, r=40, t=50, b=40)
    )

    # Building intensity vs benchmarks plot
    if selected_building and selected_building.strip() and selected_building in df['Building Name'].values:
        building_data = df[df['Building Name'] == selected_building]
        building_intensity = building_data['ghg_intensity_predicted'].values[0]
        benchmarks = {
            'Platinum': 0.1,
            'GoldPLUS': 0.12,
            'Gold': 0.15,
            'Certified': 0.2
        }

        intensity_data = pd.DataFrame({
            'Category': ['Selected Building'] + list(benchmarks.keys()),
            'Intensity': [building_intensity] + list(benchmarks.values())
        })
        colors = ['#FF5733'] + ['#007bff'] * len(benchmarks)

        benchmark_fig = go.Figure(data=[go.Bar(
            x=intensity_data['Category'],
            y=intensity_data['Intensity'],
            marker_color=colors,
            text=intensity_data['Intensity'].apply(lambda x: f"{x:.2f}"),
            textposition='auto',
            hoverinfo='text',
            hovertext=[f"{cat}: {val:.2f} tCO₂e/m²" for cat, val in zip(intensity_data['Category'], intensity_data['Intensity'])]
        )])

        benchmark_fig.update_layout(
            title=f"GHG Intensity for {selected_building} and Benchmarks",
            xaxis=dict(
                title="Category",
                titlefont=dict(size=16, family="Arial, sans-serif", color="#333333"),
                showgrid=False,
                zeroline=False,
                tickfont=dict(size=14, color="#333333"),
            ),
            yaxis=dict(
                title="GHG Intensity (tCO₂e/m²)",
                titlefont=dict(size=16, family="Arial, sans-serif", color="#333333"),
                showgrid=True,
                gridcolor="rgba(200, 200, 200, 0.3)",
                zeroline=False,
                tickfont=dict(size=14, color="#333333"),
            ),
            plot_bgcolor="#f9f9f9",
            paper_bgcolor="#f9f9f9",
            showlegend=False,
            margin=dict(l=40, r=40, t=50, b=40)
        )
    else:
        benchmark_fig = go.Figure()
        benchmark_fig.add_annotation(
            text="Please select a valid building name.",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=16, color="red")
        )
        benchmark_fig.update_layout(
            title="GHG Intensity and Benchmarks",
            plot_bgcolor="#f9f9f9",
            paper_bgcolor="#f9f9f9"
        )

    # Combine both charts into a single layout
    combined_fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Awards Distribution", "Building Intensity vs Benchmarks")
    )
    combined_fig.add_traces(awards_fig.data, rows=1, cols=1)
    combined_fig.add_traces(benchmark_fig.data, rows=1, cols=2)

    combined_fig.update_layout(
        title="Awards Distribution and Building Intensity Comparison",
        showlegend=False,
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#f9f9f9",
        font=dict(size=14),
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return combined_fig







@app.callback(
    Output('violin', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_violin_chart(selected_building):
    # Apply log transformation
    df['GHG_Total_Log'] = np.log(df['total_ghg'] + 1)
    
    # Calculate quantiles
    q25, q50, q75 = df['GHG_Total_Log'].quantile([0.25, 0.5, 0.75])
    
    # Create the violin plot
    fig = go.Figure()
    fig.add_trace(go.Violin(
        x=df['GHG_Total_Log'],
        name='GHG Emissions',
        box_visible=True,  # Enable boxplot stats
        meanline_visible=True,
        fillcolor='lightblue',
        line_color='darkblue',
        opacity=0.6,
        orientation='h'
    ))
    fig.add_trace(go.Scatter(
        y=['GHG Emissions'] * len(df),
        x=df['GHG_Total_Log'],
        mode='markers',
        marker=dict(size=6, color='rgba(0, 128, 0, 0.5)', symbol='circle')
    ))

    # Default status message
    status_message = "Select a building to view its status."
    annotation = None

    # Highlight selected building and determine its status
    if selected_building and selected_building.strip() and selected_building in df['Building Name'].values:
        building_data = df[df['Building Name'] == selected_building]
        building_log_ghg = building_data['GHG_Total_Log'].values[0]
        
        # Add marker for the selected building
        fig.add_trace(go.Scatter(
            y=['GHG Emissions'],
            x=[building_log_ghg],
            mode='markers',
            marker=dict(size=14, color='orange', symbol='diamond'),
            name="Selected Building"
        ))
        
        # Determine the status message
        if building_log_ghg < q25:
            status_message = "Your GHG emissions are on track and doing good."
        elif q25 <= building_log_ghg < q50:
            status_message = "Your GHG emissions are relatively okay."
        elif q50 <= building_log_ghg < q75:
            status_message = "Your GHG emissions are moderately high. Consider improving efficiency."
        else:
            status_message = (
                "You have a relatively high GHG emission level. "
                "You will need to paymore carbon tax"
            )
        
        # Add annotation to display the status message on the plot
        annotation = dict(
            x=building_log_ghg,
            y='GHG Emissions',
            xref='x',
            yref='y',
            text=status_message,
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1,
            ax=50,  # Horizontal offset for the annotation
            ay=-50,  # Vertical offset for the annotation
            font=dict(size=15, color='black'),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='black',
            borderwidth=1
        )

    # Add annotation if a building is selected
    if annotation:
        fig.update_layout(annotations=[annotation])

    # Customize plot layout
    fig.update_layout(
        title="GHG Emissions for All Buildings",
        yaxis_title='',
        xaxis_title='Total GHG Emissions (Log Transformed)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14),
        xaxis=dict(showgrid=True, gridcolor='lightgrey'),
        yaxis=dict(showgrid=False, visible=False),
        showlegend=False
    )
    
    return fig


# Donut Chart Callback - Scope Emissions
@app.callback(
    Output('pie_2', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_bar_scope(value):
    melt_cols = ['Building Name', "Scope1", "Scope2", "Scope3"]
    pie_data = pd.melt(df[melt_cols], id_vars='Building Name', var_name='key', value_name='value')
    pie_data = pie_data.groupby('key').agg({"value": 'sum'}).reset_index()
    
    # Calculate total emissions and percentages
    total_emissions = pie_data['value'].sum()
    pie_data['percentage'] = (pie_data['value'] / total_emissions) * 100
    
    # Define a more distinctive green color mapping for each Scope
    color_map = {
        'Scope1': '#006400',   # Dark Green
        'Scope2': '#32CD32',   # Lime Green
        'Scope3': '#ADFF2F'    # Green Yellow
    }
    
    # Map colors based on the 'key' column
    colors = [color_map.get(scope, '#333333') for scope in pie_data['key']]
    
    # Identify the largest percentage and its corresponding scope
    max_row = pie_data.loc[pie_data['percentage'].idxmax()]
    max_scope = max_row['key']
    max_percentage = max_row['percentage']

    # Create the bar plot
    fig = go.Figure(data=[
        go.Bar(
            x=pie_data['key'], 
            y=pie_data['percentage'],  # Use percentage for the y-axis
            marker=dict(color=colors),
            text=pie_data['percentage'].apply(lambda x: f'{x:.2f}%'),  # Show percentage as text
            textposition='auto'
        )
    ])

    # Add annotation for the highest percentage
    fig.add_annotation(
        x=max_scope,  # Scope with the highest percentage
        y=max_percentage,
        text="Highest, Room for Improvements & Reduction",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        ax=0,  # Horizontal offset for the annotation
        ay=-40,  # Vertical offset for the annotation
        font=dict(size=12, color='black'),
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor='black',
        borderwidth=1
    )

    # Customize the layout
    fig.update_layout(
        title="Scope Emissions Distribution (Percentage)",
        xaxis_title="Emission Scope",
        yaxis_title="Percentage of Total Emissions",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14),
        yaxis=dict(ticksuffix='%')  # Add percentage suffix to y-axis ticks
    )
    
    return fig



# Donut Chart Callback - Water and Waste
@app.callback(
    Output('pie_1', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_pie_water_waste(value):
    # Define columns to process and their emission factors
    melt_cols = ['Building Name', "Water", "Waste", "Energy", "Transportation"]
    emission_factors = {
        'Water': 0.344,          # kg CO2e per m³
        'Waste': 750,            # kg CO2e per ton
        'Energy': 0.5,           # kg CO2e per kWh
        'Transportation': 1      # kg CO2e per km (example value)
    }

    # Reshape data and calculate CO2e emissions
    pie_data = pd.melt(df[melt_cols], id_vars='Building Name', var_name='key', value_name='value')
    pie_data['CO2e'] = pie_data.apply(lambda row: row['value'] * emission_factors.get(row['key'], 1), axis=1)
    pie_data = pie_data.groupby('key').agg({"CO2e": 'sum'}).reset_index()

    # Define base color mapping for Water, Waste, Energy, and Transportation
    base_color_map = {
        'Water': '#9ACD32',       # Green Yellow
        'Waste': '#3CB371',       # Light Green
        'Energy': '#32CD32',      # Lime Green
        'Transportation': '#FF6347'  # Tomato
    }

    # Identify the category with the highest CO2e
    max_index = pie_data['CO2e'].idxmax()
    max_key = pie_data.iloc[max_index]['key']  # Get the key (category) with the highest CO2e

    # Highlight the maximum value with bright red
    highlight_color_map = {
        key: (base_color_map[key] if key != max_key else '#FF0000')  # Highlight with Bright Red
        for key in pie_data['key']
    }

    # Map colors and create pull-out effect
    colors = [highlight_color_map[item] for item in pie_data['key']]
    pull_values = [0.1 if i == max_index else 0 for i in range(len(pie_data))]

    # Create the donut chart
    fig = px.pie(
        pie_data,
        names='key',
        values='CO2e',
        title="CO2e Emissions Distribution: Water, Waste, Energy, Transportation",
        hole=0.4
    )
    fig.update_traces(
        marker=dict(colors=colors),
        pull=pull_values,  # Pull out the highest percentage slice
        texttemplate='%{label}: %{percent:.2%}',
        textposition='outside'
    )

    # Add an annotation to highlight the highest category explicitly
    fig.add_annotation(
        x=1,  # Place annotation outside the chart (adjust as necessary)
        y=1,
        text=f"Highest Emission: {max_key}",
        showarrow=False,
        font=dict(size=14, color='black'),
        bgcolor='rgba(255,0,0,0.3)',  # Highlight the annotation with transparent red
        bordercolor='red',
        borderwidth=1
    )

    return fig





# Callback to update the heatmap
@app.callback(
    Output('heatmap', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_heatmap(value):
    # Select relevant columns for the heatmap
    heatmap_data = df[['Water', 'Waste', 'Energy', 'Transportation', 'total_ghg']]
    
    # Calculate correlation for heatmap visualization
    correlation_matrix = heatmap_data.corr()
    
    # Create heatmap
    fig = px.imshow(
        correlation_matrix,
        text_auto=True,
        aspect="auto",
        title="Correlation Heatmap of Key Metrics",
        color_continuous_scale="Greens"
    )
    
    fig.update_layout(
        xaxis_title="Metrics",
        yaxis_title="Metrics",
        font=dict(size=12),
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot background
        paper_bgcolor='rgba(0,0,0,0)'  # Transparent paper background
    )
    
    return fig


# Define layout for Page 4 - Report Generation and Chatbot

# Open AI
def generate_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150, 
            temperature=0.7  
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"An error occurred: {e}"


# Function to create chat bubbles with typing effect
def create_chat_bubble(content, is_user=False, is_typing=False):
    if is_typing:
        # Display typing animation
        content = html.Div([
            html.Span(".", className="dot"),
            html.Span(".", className="dot"),
            html.Span(".", className="dot")
        ], className="typing-animation")
    return html.Div(
        content,
        style={
            'backgroundColor': '#d1e7f3' if is_user else '#ffffff',  # User bubble is light blue, bot bubble is white
            'color': '#333',
            'padding': '12px 18px',
            'borderRadius': '18px',
            'maxWidth': '70%',
            'alignSelf': 'flex-end' if is_user else 'flex-start',
            'marginBottom': '10px',
            'textAlign': 'left' if not is_user else 'right',
            'lineHeight': '1.6',
            'fontSize': '16px',
            'display': 'inline-block' if not is_typing else 'flex',
            'alignItems': 'center' if is_typing else 'initial',
            'border': '1.5px solid #b0d4e3',  # Slightly thicker border
            'boxShadow': '0 2px 8px rgba(0, 0, 0, 0.1)',  # Subtle shadow for depth
            'fontFamily': 'Montserrat, sans-serif'
        }
    )

page_4_layout = dbc.Container([
    dcc.Store(id='report-content-store', storage_type='memory'),
    
    # Title Section
    dbc.Row([
        dbc.Col(html.H1(
            "Report and Chatbot",
            className="text-center",
            style={"fontWeight": "bold", "marginTop": "20px", "marginBottom": "40px", "color": "#4A4A4A"}
        ))
    ]),

    # Report Generation Section
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Your report is ready for download...", style={"textAlign": "center", "marginBottom": "15px"}),
                dbc.Button(
                    [html.I(className="fas fa-file-download", style={"marginRight": "8px"}), "Download Report"],
                    id="report-button",
                    color="secondary",
                    style={
                        'width': '50%', 
                        'padding': '12px', 
                        'borderRadius': '5px', 
                        'fontSize': '16px', 
                        'fontWeight': 'bold', 
                        'margin': 'auto', 
                        'display': 'block',
                        'color': 'white',
                        'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.2)'
                    }
                ),
                dcc.Download(id="download-report")
            ], style={'textAlign': 'center'}),
        ], width=12, className="mb-5"),
    ]),

    # Chatbot Assistance Section
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5(
                    "Your Chat Assistance", 
                    className="mb-3", 
                    style={"textAlign": "center", "color": "#666", "fontFamily": "Montserrat, sans-serif"}
                ),
                html.Br(),  # Line break
                html.H5(
                    "Disclaimer: this is just for reference, AI chatbot commit mistakes, please check important info.",
                    className="mb-3", 
                    style={"textAlign": "center", "color": "#666", "fontFamily": "Montserrat, sans-serif"}
                ),
                dbc.Button(
                    [html.I(className="fas fa-lightbulb", style={"marginRight": "10px"}), "View Recommendations"],
                    id="recommendations-button",
                    n_clicks=0,
                    style={
                        'backgroundColor': '#28A745',  # Green for action
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '25px',  # Rounded button
                        'padding': '12px 30px',
                        'fontSize': '16px',
                        'fontWeight': 'bold',
                        'margin': '20px auto',
                        'cursor': 'pointer',
                        'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.2)',  # Add shadow
                        'display': 'inline-flex',
                        'alignItems': 'center',  # Align text with icon
                        'justifyContent': 'center',
                        'gap': '10px',  # Space between icon and text
                        'transition': 'all 0.3s ease'  # Smooth hover effect
                    },
                    className="recommendation-btn"
                ),
            ], style={'textAlign': 'center'}),
            
            # Chat Input Section
            html.Div([
                html.Div([
                    dcc.Input(
                        id='chatbot-input', 
                        type='text', 
                        placeholder="Ask a question about the report...", 
                        style={
                            'width': '85%',
                            'padding': '12px',
                            'borderRadius': '25px',
                            'border': '2px solid #ced4da',
                            'boxShadow': '0 1px 6px rgba(0, 0, 0, 0.1)',
                            'marginBottom': '10px',
                            'fontSize': '16px',
                            'fontFamily': 'Montserrat, sans-serif'
                        }
                    ),
                    html.Button(
                        html.I(className="fas fa-paper-plane"), 
                        id='send-button', 
                        n_clicks=0, 
                        style={
                            'backgroundColor': '#1E88E5',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '50%',
                            'padding': '10px',
                            'marginLeft': '10px',
                            'width': '40px',
                            'height': '40px',
                            'boxShadow': '0 1px 6px rgba(0, 0, 0, 0.2)',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'cursor': 'pointer'
                        }
                    ),
                    html.Button(
                        html.I(className="fas fa-redo-alt"), 
                        id="refresh-button",
                        n_clicks=0,
                        style={
                            'backgroundColor': '#17A2B8',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '50%',
                            'padding': '10px',
                            'marginLeft': '10px',
                            'width': '40px',
                            'height': '40px',
                            'boxShadow': '0 1px 6px rgba(0, 0, 0, 0.2)',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'cursor': 'pointer'
                        }
                    ),
                ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),

                # Chat Response Section
                html.Div(
                    id='chatbot-response',
                    className="mt-3",
                    style={
                        'color': '#4A4A4A',
                        'border': '1.5px solid #E9ECEF',
                        'borderRadius': '10px',
                        'padding': '20px',
                        'backgroundColor': '#F8F9FA',
                        'minHeight': '200px',
                        'fontSize': '16px',
                        'lineHeight': '1.6',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'gap': '10px',
                        'width': '80%',
                        'margin': 'auto',
                        'boxShadow': '0 2px 10px rgba(0, 0, 0, 0.1)'  # Add shadow
                    }
                ),

                # Typing animation intervals
                dcc.Interval(id="typing-interval-greeting", interval=3000, n_intervals=0, max_intervals=1),  # Greeting 3-second interval
                dcc.Interval(id="typing-interval-response", interval=3000, n_intervals=0, max_intervals=1),  # Response 3-second interval
                dcc.Interval(id="page-load-trigger", interval=1, n_intervals=0, max_intervals=1)  # Trigger on page load
            ])
        ], width=8, className="mb-5"),
    ], className="justify-content-center"),

    # Next Button
    dbc.Row([
        dbc.Col([
            dbc.Button(
                "Next: Feedback Survey", 
                id="go-to-page-5", 
                color="success", 
                href='/page-5', 
                className="mt-4",
                style={
                    'width': '100%', 
                    'padding': '10px', 
                    'borderRadius': '5px', 
                    'fontWeight': 'bold', 
                    'fontSize': '16px'
                }
            )
        ], width=3),
    ], justify="center", className="mt-5 mb-5"),
], fluid=True)



@app.callback(
    Output('chatbot-response', 'children'),
    Output('typing-interval-greeting', 'n_intervals'),
    Output('typing-interval-response', 'n_intervals'),
    Input('page-load-trigger', 'n_intervals'),
    Input('send-button', 'n_clicks'),
    Input('recommendations-button', 'n_clicks'),
    Input('typing-interval-greeting', 'n_intervals'),
    Input('typing-interval-response', 'n_intervals'),
    Input('refresh-button', 'n_clicks'),
    State('chatbot-input', 'value'),
    State('chatbot-response', 'children')
)
def update_chatbot_response(page_load_trigger, send_clicks, recommendations_clicks,
                            greeting_typing_intervals, response_typing_intervals,
                            refresh_clicks, user_input, existing_chat):
    ctx = callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    # Identify the triggered component
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Handle Page Load Trigger
    if trigger_id == 'page-load-trigger' and page_load_trigger == 1:
        typing_animation = create_chat_bubble("", is_typing=True)
        return [typing_animation], 0, dash.no_update

    # Handle Greeting Typing Interval
    if trigger_id == 'typing-interval-greeting' and greeting_typing_intervals == 1:
        greeting_message = create_chat_bubble(
            "Hello! I’m here to help. Feel free to ask me anything about your report, emission calculations, modelling, or any questions about sustainability. Let’s dive in and find the answers you need!",
            is_user=False
        )
        return [greeting_message], dash.no_update, dash.no_update

    # Handle Refresh Button
    if trigger_id == 'refresh-button' and refresh_clicks > 0:
        greeting_message = create_chat_bubble(
            "Hello! I’m here to help. Feel free to ask me anything about your report, emission calculations, modelling, or any questions about sustainability. Let’s dive in and find the answers you need!",
            is_user=False
        )
        return [greeting_message], 0, 0

     # Recommendations Button
    if trigger_id == 'recommendations-button' and recommendations_clicks > 0:
        # Step 1: Add typing animation for recommendations
        typing_animation = create_chat_bubble("", is_typing=True)
        updated_chat = (existing_chat or []) + [typing_animation]
        return updated_chat, dash.no_update, 0  # Trigger typing interval for recommendations

    # Step 2: Show recommendations after typing animation ends
    if trigger_id == 'typing-interval-response' and response_typing_intervals == 1:
        try:
            # Recommendations as a Dash list
            recommendations = html.Div([
                html.H4("Recommendations Based on GHG Emissions Report"),
                html.P("Here are tailored recommendations for your building in Singapore:"),
                html.Ul([
                    html.Li(html.B("Overview:")),
                    html.Ul([
                        html.Li(f"Total GHG Emissions: 3924.95 CO2e"),
                        html.Li(f"Emission Intensity: 0.111 kg CO2e/m²"),
                        html.Li(f"Green Mark Certification Level: Platinum"),
                    ]),
                    html.Li(html.B("Primary Emission Drivers:")),
                    html.Ul([
                        html.Li("Transportation accounts for 78.25% of total emissions, making it the largest contributor."),
                    ]),
                    html.Li(html.B("Notifications and Warnings:")),
                    html.Ul([
                        html.Li("Nearly 80% of the building’s emissions come from transportation activities, likely due to business travel (flights and hotel stays) and freight transportation."),
                        html.Li("Be aware of Singapore's carbon tax, which is currently 25 SGD/ton and will increase to 45 SGD/ton in 2024. Reducing emissions will directly lower operational costs."),
                        html.Li("Your building’s emission intensity aligns well with the Green Mark Platinum standard, but regular audits and upgrades are recommended to stay ahead of stricter standards."),
                    ]),
                    html.Li(html.B("Actionable Steps for GHG Reduction:")),
                    html.Ul([
                        html.Li("Reduce long-distance travel, adopt electric or low-emission vehicles, and optimize logistics to significantly cut emissions."),
                        html.Li("Regularly monitor and track emissions to identify trends and areas for improvement."),
                        html.Li("Transition to low-emission or electric vehicles and optimize logistics routes."),
                    ]),
                    html.Li(html.B("Future Goals:")),
                    html.Ul([
                        html.Li("Set long-term carbon neutrality targets, such as a 50% reduction by 2030."),
                        html.Li("Leverage government incentives like the Building Retrofit Energy Efficiency Financing (BREEF)."),
                        html.Li("Automate emissions tracking and integrate with sustainability reporting frameworks."),
                    ]),
                ]),
            ])

            recommendations_response = create_chat_bubble(recommendations, is_user=False)
            return (existing_chat[:-1] or []) + [recommendations_response], dash.no_update, dash.no_update

        except Exception as e:
            print(f"Error generating recommendations: {e}")
            error_response = create_chat_bubble(
                "An error occurred while generating recommendations. Please try again.",
                is_user=False
            )
            return (existing_chat or []) + [error_response], dash.no_update, dash.no_update

    # Handle User-Submitted Questions
    if trigger_id == 'send-button' and send_clicks > 0 and user_input:
        user_bubble = create_chat_bubble(user_input, is_user=True)
        typing_animation = create_chat_bubble("", is_typing=True)
        existing_chat = (existing_chat or []) + [user_bubble, typing_animation]

        bot_response_content = generate_response(user_input)
        bot_response = create_chat_bubble(bot_response_content, is_user=False)

        return existing_chat[:-1] + [bot_response], dash.no_update, dash.no_update

    raise dash.exceptions.PreventUpdate



# generate report
# Sample emission data for business travel and procurement

# Calculate the total emission from business travel and procurement transportation
total_emission = (business_travel_data['Hotel Emission'] + 
                  business_travel_data['Flight Emission'] + 
                  business_procurement_data['Airline Emission'] + 
                  business_procurement_data['Diesel Truck Emission'] + 
                  business_procurement_data['Electric Truck Emission'])


# Callback to generate the report
@app.callback(
    Output('download-report', 'data'),
    Input('report-button', 'n_clicks'),
    State('selected-building-store', 'data') 
)


def generate_report(n_clicks, selected_building):
    if n_clicks:
        try:
            if not selected_building:
                selected_building = "Default Building Name"

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
            
            emission_section = f"""
            <h2>Emission Breakdown</h2>
            <p>The following details summarize key emission and sustainability data for the selected building:</p>

            <p><strong>Total GHG Emissions:</strong> {building_data['GHG_Total']} CO2e</p>
            <p><strong>Predicted GHG Intensity:</strong> {building_data['GHG_Intensity']} kg CO2e/m²</p>
            <p><strong>Predicted Green Marks Certification:</strong> {building_data['Award']}</p>

            <p>The following table summarizes the emissions associated with different business activities:</p>
            <table border="1" cellpadding="5" cellspacing="0" style="width: 100%; text-align: left;">
                <tr>
                    <th>Emission Source</th>
                    <th>Emission (in CO2e)</th>
                </tr>
                <tr><td>Business Travel Hotel Emission</td><td>{business_travel_data['Hotel Emission']}</td></tr>
                <tr><td>Business Travel Flight Emission</td><td>{business_travel_data['Flight Emission']}</td></tr>
                <tr><td>Business Procurement Airline Emission</td><td>{business_procurement_data['Airline Emission']}</td></tr>
                <tr><td>Business Procurement Diesel Truck Emission</td><td>{business_procurement_data['Diesel Truck Emission']}</td></tr>
                <tr><td>Business Procurement Electric Truck Emission</td><td>{business_procurement_data['Electric Truck Emission']}</td></tr>
                <tr><td><strong>Total Emission from Business Travel and Procurement</strong></td><td><strong>{total_emission}</strong></td></tr>
            </table>
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

            # Generate Plots
            trend_plot = update_line_chart(selected_building)
            trend_plot_html = trend_plot.to_html(full_html=False, include_plotlyjs='cdn')

            benchmark_plot = update_combined_chart(selected_building)
            benchmark_plot_html = benchmark_plot.to_html(full_html=False, include_plotlyjs='cdn')

            violin_plot = update_violin_chart(selected_building)
            violin_plot_html = violin_plot.to_html(full_html=False, include_plotlyjs='cdn')

            scope_emissions_plot = update_bar_scope(None)
            scope_emissions_plot_html = scope_emissions_plot.to_html(full_html=False, include_plotlyjs='cdn')

            water_waste_plot = update_pie_water_waste(None)
            water_waste_plot_html = water_waste_plot.to_html(full_html=False, include_plotlyjs='cdn')

            heatmap_plot = update_heatmap(None)
            heatmap_plot_html = heatmap_plot.to_html(full_html=False, include_plotlyjs='cdn')

            # Generate report based on the selected format
            report_html = f"""
            <html>
                    <body>
                    <!-- Logo at the top of the report -->
                    <div style="text-align: center; margin-bottom: 20px;">
                    </div>
                        {title_section}
                        {executive_summary}
                        {introduction}
                        {scope_of_reporting}
                        {emission_section}
                        {performance_data_intro}
                        <!-- Resource Usage Section -->
                        <h2>Resource Usage: Water and Waste vs Scope Emissions Distribution</h2>
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 20px; margin-top: 20px;">
                           <!-- Water and Waste Pie Chart -->
                           <div style="flex-basis: 45%; padding: 10px; border: 1px solid #ccc; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); text-align: center;">
                               {water_waste_plot_html}
                           </div>
            
                           <!-- Scope Emissions Bar Plot -->
                           <div style="flex-basis: 45%; padding: 10px; border: 1px solid #ccc; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); text-align: center;">
                               {scope_emissions_plot_html}
                           </div>
                        </div>
                        
                        {benchmark_intro}
                        <!-- Benchmark and Trend Plots Section -->
                        <h2>Benchmarking and Emission Trends</h2>
                        <div style="display: flex; justify-content: center; align-items: flex-start; gap: 40px; margin-top: 20px;">
                            <!-- Benchmark Plot -->
                            <div style="flex-basis: 45%; padding: 10px; border: 1px solid #ccc; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); text-align: center;">
                                {benchmark_plot_html}
                            <p style="margin-top: 10px; font-size: 14px;">Benchmark Comparison: Building Intensity vs Award Levels</p>
                            </div>
            
                            <!-- Trend Plot -->
                            <div style="flex-basis: 45%; padding: 10px; border: 1px solid #ccc; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); text-align: center;">
                                {trend_plot_html} <!-- This should contain your Trend Plot -->
                            <p style="margin-top: 10px; font-size: 14px;">Greenhouse Gas Emissions Over Time</p>
                            </div>
                        </div>
                        {violin_plot_html}
                        {future_outlook}
                        {heatmap_plot_html}
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
        "answer": "This dash helps with data input and validation for sustainability reporting. It assists users in inputting environmental data, performing data quality checks, and generating reports."
    },
    {
        "question": "Who can use this dash?",
        "answer": "This app is intended for users responsible for reporting on environmental metrics. No special training is needed, but a basic understanding of emissions and sustainability reporting is helpful."
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
        "answer": "For support, please contact our team at yyds@u.nus.edu We’re here to help with any issues you may have."
    },
]



# Q&A layout with improved readability and icons
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

    # FAQ Section Title
    html.Div([
        html.H3("Frequently Asked Questions", style={
            'fontWeight': 'bold',
            'fontSize': '28px',
            'textAlign': 'center',
            'marginBottom': '30px',
            'color': '#333',
        }),
    ]),

    # FAQ Accordion with Icons
    html.Div([
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    title=html.Div([
                        html.Span(qa["question"], style={"color": "#4a4a4a", 'fontSize': '18px', 'fontWeight': 'bold'})
                    ]),
                    children=html.P(qa["answer"], style={"color": "#4a4a4a", 'padding': '10px', 'lineHeight': '1.6'}),
                    style={
                        'backgroundColor': '#f8f9fa',
                        'padding': '12px',
                        'borderRadius': '8px',
                        'marginBottom': '10px',
                        'boxShadow': '0 2px 6px rgba(0, 0, 0, 0.1)'
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
        
        # Contact Information
        html.Div(
            [
                html.P(
                    "For more questions, please contact us at yyds@u.nus.edu.",
                    style={'fontSize': '16px', 'color': '#555', 'textAlign': 'center', 'marginBottom': '5px'}
                ),
                html.I(className="fas fa-envelope", style={'fontSize': '20px', 'color': '#007bff'})
            ],
            style={
                'padding': '20px',
                'backgroundColor': '#e9ecef',
                'borderRadius': '8px',
                'marginTop': '20px',
                'textAlign': 'center'
            }
        )
    ], style={
        'padding': '20px',
        'backgroundColor': '#f9f9f9',
        'borderRadius': '8px',
        'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)'
    }),

    # Footer Message
    html.Div("Made with ❤️ by Team YYDS", style={
        'textAlign': 'center', 'color': '#4a4a4a', 'marginTop': '30px', 'fontSize': '16px'
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

    # About YYDS Section with Icons
    dbc.Card(
        dbc.CardBody([
            html.H3("Why YYDS?", className="my-4", style={"color": "#4a4a4a",'fontWeight': 'bold'}),
            html.Div(
                [
                    html.I(className="fas fa-seedling", style={"color": "#2e7d32", "marginRight": "10px"}),
                    html.H5("Our Mission", style={"color": "#4a4a4a", "display": "inline", "fontWeight": "bold"})
                ],
                style={"marginBottom": "10px"}
            ),
            html.P("""
                Our team is named "YYDS," a phrase that originates from Chinese internet culture, meaning "永远的神" (yǒng yuǎn de shén) 
                or "Eternal God." This term is used to describe something legendary, timeless, and worth admiring — the best of the best. 
                For us, it reflects our commitment to creating something enduring and impactful, particularly in the realm of sustainability.
            """, style={'lineHeight': '1.6'}),
            
            html.Div(
                [
                    html.I(className="fas fa-recycle", style={"color": "#00796b", "marginRight": "10px"}),
                    html.H5("Sustainability Goals", style={"color": "#4a4a4a", "display": "inline", "fontWeight": "bold"})
                ],
                style={"marginTop": "20px", "marginBottom": "10px"}
            ),
            html.P("""
                In today's world, achieving true sustainability means creating systems, practices, and innovations that stand the test of time — 
                solutions that are not only effective today but will also continue to make a positive impact far into the future. This is what "YYDS" 
                represents to us: the aspiration to be a lasting force for good, to develop solutions that people can rely on, and to drive meaningful 
                change that is resilient over time.
            """, style={'lineHeight': '1.6'}),
            
            html.Div(
                [
                    html.I(className="fas fa-hands-helping", style={"color": "#388e3c", "marginRight": "10px"}),
                    html.H5("Our Commitment", style={"color": "#4a4a4a", "display": "inline", "fontWeight": "bold"})
                ],
                style={"marginTop": "20px", "marginBottom": "10px"}
            ),
            html.P("""
                Our team believes that sustainability is not just a goal but a journey toward a better, lasting world. By embracing the "YYDS" mindset, 
                we aim to be "forever impactful" — creating solutions, tools, and practices in the field of sustainability that are not only effective 
                but also resilient and adaptive to the challenges of tomorrow.
            """, style={'lineHeight': '1.6'}),
            
            html.P("""
                In essence, YYDS symbolizes our commitment to excellence and timeless impact in sustainability. We want our contributions to be seen 
                as YYDS: enduring, trustworthy, and legendary in the fight for a sustainable future.
            """, style={'lineHeight': '1.6'}),
        ]),
        style={
            'padding': '20px',
            'backgroundColor': '#ffffff',
            'borderRadius': '8px',
            'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.1)'
        }
    ),

    # GitHub Link Section
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
    ),
    
    # Footer Message
    html.Div(
        "Made with ❤️ by Team YYDS",
        style={
            "textAlign": "center",
            "padding": "20px",
            "fontSize": "14px",
            "color": "gray",
            "marginTop": "20px"
        }
    )
], fluid=True, style={'padding': '40px 0', 'maxWidth': '800px', 'margin': 'auto'})


# Combine callback to handle both navigation and method switching
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/page-2':
        return page_2_layout
    elif pathname == '/page-3':
        return page_3_layout
    elif pathname == '/page-3-manual':
        return page_3_manual_layout  # New manual layout
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
