# DSS5105-YYDS [Your Yielding partner in sustainable Development Solutions]

# We are a company that provides GHG Emission Calculations and Estimations for Buildings in Singapore. This is an easy-to-use, interactive and customizable calculator and dashboard with all-in-one functionality:
* Automatic Data Validation and Cleaning, Data Analysis, Machine Learning Model and Indicator Combined Prediction, Data Visualizations
* Benchmarking & Ratings with Green Mark Incentive Schemes, Customizable GHG Reduction Recommendations
* AI-Powered GHG Emission Chatbot Assistant


**To install and use this Calculator:**




**Dashboard**

**Page 3:**

This Dash app visualizes data from a building dataset (merged_df.csv) using interactive Plotly graphs. It provides insights into building-related data over time, including trend lines, histograms, and pie charts.

**Features:**

Interactive Dropdown Selection: Choose a building to filter and view relevant data.

Dynamic Graphs: The app displays multiple graphs:

Trend Line: Shows trends over time.

Awards: Visualizes award-related data.

Histogram: Displays data distribution.

Pie Chart: Summarizes categorical data.

**Requirements**

Ensure Python is installed on your system. Required libraries:dash, plotly,pandas,numpy
Data Setup:

Place the CSV file, merged_df.csv, in the same directory as plotlt.py. The file should include:
Year column: Numeric values for years

Building Name column: Categorical data for building names

**How to Run**

Open a terminal in the directory containing plotlt.py.

run python plotlt.py

Access the app by navigating to http://127.0.0.1:8050 in a web browser.

**Project Structure**

plotlt.py: Main application file for the Dash app.

merged_df.csv: CSV data source file.

**Code Highlights**

Data Processing: The app processes Year into a datetime format to support time-based visualizations.

Dash Layout: HTML and Dash components are used to create a grid layout for interactive graphs.

Callbacks: Functions dynamically update each graph based on the selected building.

**Troubleshooting**

Encoding Errors: If the CSV file has encoding issues, the app attempts to resolve these by setting encoding="utf-8" and encoding_errors="ignore".
Graph Display Issues: Ensure the dataset has required columns (Year, Building Name) and values are correctly formatted.
