# DSS5105-YYDS [Your Yielding partner in sustainable Development Solutions]

**We are a company that provides GHG Emission Calculations and Estimations for Buildings in Singapore. This is an easy-to-use, interactive and customizable calculator and dashboard with all-in-one functionality:**
* Automatic Data Validation and Cleaning, Data Analysis, Machine Learning Model and Indicator Combined Prediction, Data Visualizations
* Benchmarking & Ratings with Green Mark Incentive Schemes, Customizable GHG Reduction Recommendations
* AI-Powered GHG Emission Chatbot Assistant


**To install and use this Calculator:**


Directory / Path Structure
DSS5105-YYDS/
├── Group A/
│   ├── Geospatial_Analysis/
│   ├── business travel & procurement factor/    # Likely related to travel and procurement analysis
│   ├── commuting factors/                       # Contains files or scripts for commuting-related analysis
│   ├── datasets/                                # Directory for datasets
│   ├── prediction models/                       # Models and scalers for predictions
│   ├── scripts/                                 # General Python scripts or utilities
│   ├── validation_initial_analysis/             # Initial validation analysis files
│   ├── validation_root/                         # Root validation files
│   ├── Business Travel & Procurement.xlsx       # A spreadsheet likely related to travel and procurement
│   ├── Commuting Factor                         # Related document for commuting analysis
└── README.md               
├── Group B/
│   ├── assets
│   ├── datasets
│   ├── Dash
│   ├── yydsCalculator.py
│   ├── src_historical_versions
│   ├── structured_feedback_handler.py
│   ├── CompleteDataset.csv
└── README.md



# Tutorial: Create Conda and Python Virtual Environments

This guide provides quick instructions for setting up virtual environments using Conda or Python's `virtualenv`/`venv` to manage dependencies and ensure isolated environments.

---

## 1. Conda Environment from `myenv.yml`

1. **Install Conda**: Download from [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/).
2. **Create Environment**: 
    ```bash
    conda env create -f myenv.yml
    ```
3. **Activate Environment**: 
    ```bash
    conda activate <your_env_name>
    ```
4. **Verify Installation**: 
    ```bash
    conda list
    ```
5. **Update Environment**:
    ```bash
    conda env update --file myenv.yml --prune
    ```
6. **Deactivate Environment**: 
    ```bash
    conda deactivate
    ```

---

## 2. Python Virtual Environment

1. **Install `virtualenv` (if needed)**: 
    ```bash
    pip install virtualenv
    ```
2. **Create Environment**:
    ```bash
    python -m venv myenv  # or virtualenv myenv
    ```
3. **Activate Environment**:
    - **Windows**: `myenv\Scripts\activate`
    - **macOS/Linux**: `source myenv/bin/activate`
4. **Install Dependencies**: 
    ```bash
    pip install -r requirements.txt
    ```
5. **Verify Installation**: 
    ```bash
    pip list
    ```
6. **Deactivate Environment**: 
    ```bash
    deactivate
    ```

---

## Command Summary

### Conda
- Create: `conda env create -f myenv.yml`
- Activate: `conda activate <your_env_name>`
- Update: `conda env update --file myenv.yml --prune`
- Deactivate: `conda deactivate`

### Python Virtual Environment
- Create: `python -m venv myenv` or `virtualenv myenv`
- Activate:
  - Windows: `myenv\Scripts\activate`
  - macOS/Linux: `source myenv/bin/activate`
- Install: `pip install -r requirements.txt`
- Deactivate: `deactivate`


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
