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
import dash_leaflet as dl
import base64
import plotly.graph_objects as go
from datetime import datetime
from structured_feedback_handler import StructuredFeedbackHandler  # Import the feedback handler class
import json

# import chatbot libraries
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

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

UPLOAD_DIRECTORY = "./datasets"
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




# Page 2 layout addition for Data Quality Action Options
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
            html.H5("Missing Data Summary"),
            dash_table.DataTable(id='missing-data-table', style_table={'overflowX': 'auto'})
        ])
    ], className="mt-5"),
    dbc.Row([
        dbc.Col([
            html.H5("Visualization of Data Completeness"),
            dcc.Graph(id='completeness-graph'),
        ]),
    ], className="mt-5"),
    dbc.Row([
        dbc.Col(html.Div(id='action-prompt'), className="mt-5")  # Placeholder for user actions
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button("Re-upload Data", id="reupload-button", color="warning", href='/page-1'),
            dbc.Button("Next: Model Running and Comparison", id="next-model-button", color="primary", href='/page-3', className="ml-2")
        ], width=6),
    ])
])


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
        missing_data['% Missing'] = (missing_data['Missing Values'] / len(df)) * 100
        
        # Convert missing data summary to dict for dash_table
        table_data = missing_data.to_dict('records')
        
        # Plot missing data as a bar chart
        fig = px.bar(missing_data, x='Column', y='% Missing', title='Missing Data Percentage by Column')
        
        return table_data, fig
    
    return [], go.Figure()  # Empty output if data is not available

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
                        dbc.Button("Fill Out Missing Values and Re-upload", id="reupload-prompt-button", color="primary", className="ml-2", href='/page-1')
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


model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
chatbot = pipeline("text-generation", model=model, tokenizer=tokenizer)

# Create the chatbot pipeline
chatbot = pipeline("text-generation", model="microsoft/DialoGPT-medium", device =0)

# Define the chatbot layout
# Define layout for Page 4 - Generate Report and Chat Assistance
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
            dcc.Textarea(
                id='chat-history',
                value='',
                style={'width': '100%', 'height': 300, 'whiteSpace': 'pre-line'},
                readOnly=True,
                placeholder="Chat history will appear here..."
            ),
            dcc.Input(
                id='chatbot-input',
                type='text',
                placeholder="Ask a question about the report...",
                style={'width': '100%', 'margin-top': '10px'}
            ),
            dbc.Button(
                "Send",
                id="chatbot-send-button",
                color="primary",
                style={'margin-top': '10px'}
            ),
            html.Div(id='chatbot-response', className="mt-3")
        ], width=6),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button("Next: Feedback Survey", id="next-feedback-button", color="primary", href='/page-5', className="mt-4")
        ], width=4)
    ], className="mb-5")
])


# Define callback for chatbot interaction
@app.callback(
    Output("chat-history", "value"),
    Input("chatbot-send-button", "n_clicks"),
    State("chatbot-input", "value"),
    State("chat-history", "value"),
    prevent_initial_call=True
)
def update_chat_history(n_clicks, user_input, chat_history):
    if not user_input:
        return chat_history

    # Tokenize user input and generate a response
    inputs = tokenizer(user_input, return_tensors="pt")
    outputs = model.generate(inputs['input_ids'], max_length=150, pad_token_id=tokenizer.eos_token_id)
    bot_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Update chat history with user and bot messages
    updated_history = f"{chat_history}\nUser: {user_input}\nChatbot: {bot_response}\n"
    return updated_history


page_5_layout = dbc.Container([
    html.H2("Feedback Survey", className="mt-4 mb-4", style={'fontSize': '32px'}),
    
    dbc.Row([
        dbc.Col([
            dbc.Input(id="building_name", placeholder="Building Name", type="text", className="mb-3", style={'fontSize': '18px'}),
            dbc.Input(id="predicted_level", placeholder="Predicted Level", type="text", className="mb-3", style={'fontSize': '18px'}),
            dbc.Label("Prediction Accuracy", style={'fontSize': '20px'}),
            dcc.Slider(id="prediction_accuracy", min=1, max=5, step=1, value=3, marks={i: str(i) for i in range(1, 6)}),
            dbc.Label("Calculation Clarity", style={'fontSize': '20px'}),
            dcc.Slider(id="calculation_clarity", min=1, max=5, step=1, value=3, marks={i: str(i) for i in range(1, 6)}),
            dbc.Label("Visualization Helpfulness", style={'fontSize': '20px'}),
            dcc.Slider(id="visualization_helpfulness", min=1, max=5, step=1, value=3, marks={i: str(i) for i in range(1, 6)}),
            dbc.Label("GHG Intensity Rating", style={'fontSize': '20px'}),
            dcc.Slider(id="ghg_intensity_rating", min=1, max=5, step=1, value=3, marks={i: str(i) for i in range(1, 6)}),
            dbc.Label("Emissions Breakdown Rating", style={'fontSize': '20px'}),
            dcc.Slider(id="emissions_breakdown_rating", min=1, max=5, step=1, value=3, marks={i: str(i) for i in range(1, 6)}),
            dbc.Label("Benchmark Comparison Rating", style={'fontSize': '20px'}),
            dcc.Slider(id="benchmark_comparison_rating", min=1, max=5, step=1, value=3, marks={i: str(i) for i in range(1, 6)}),
            dbc.Textarea(id="improvement_priorities", placeholder="Improvement Priorities (comma-separated)", className="mb-3", style={'fontSize': '18px'}),
            dbc.Label("Overall Satisfaction", style={'fontSize': '20px'}),
            dcc.Slider(id="overall_satisfaction", min=1, max=5, step=1, value=3, marks={i: str(i) for i in range(1, 6)}),
            dbc.Button("Submit Feedback", id="submit_feedback", color="primary", className="mt-3"),
            dcc.Download(id="download_excel")
        ], md=6)
    ])
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
        # If improvement_priorities is None or empty, set it to an empty list
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

        # Store feedback in SQLite database
        feedback_handler.store_feedback(feedback_data)

        # Export feedback to Excel
        excel_path = feedback_handler.export_feedback_to_excel()

        # Provide Excel download
        return dcc.send_file(excel_path)
    
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
