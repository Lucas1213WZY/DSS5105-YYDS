# DSS5105-YYDS [Your Yielding partner in sustainable Development Solutions]

**We are a company that provides GHG Emission Calculations and Estimations for Buildings in Singapore. This is an easy-to-use, interactive and customizable calculator and dashboard with all-in-one functionality:**
* Automatic Data Validation and Cleaning, Data Analysis, Machine Learning Model and Indicator Combined Prediction, Data Visualizations
* Benchmarking & Ratings with Green Mark Incentive Schemes, Customizable GHG Reduction Recommendations
* AI-Powered GHG Emission Chatbot Assistant

```plaintext
    "Project Assessment: for the openai API Key please find attached the key in the email Group YYDS sent to you, thank you!"
```

**To install and use this Calculator:**
*1.Clone the repository
    ```bash
    git clone https://github.com/Lucas1213WZY/DSS5105-YYDS.git
    ```
*2.After that use pip install or conda install to install all required libraries

    ```bash
    pip/conda install requirements.txt
    ```
*3.Change directory from the root to Group B to run the yydsCalculator
    ```bash
    cd Group\ B
    python yydsCalculator.py
    ```
*4.Once it's running, please go to your browser and use the link below to access the application on your ease
    ```plaintext
    http://127.0.0.1:8050/
    ```
    


# Directory / Path Structure

The following is the directory structure for the project:

```plaintext
DSS5105-YYDS/
├── Group A/
│   ├── Geospatial_Analysis/
│   ├── business travel & procurement factor/
│   ├── commuting factors/
│   ├── datasets/
│   ├── prediction models/
│   ├── scripts/
│   ├── validation_initial_analysis/
│   ├── validation_root/
│   ├── Business Travel & Procurement.xlsx
│   ├── Commuting Factor
│   └── README.md
├── Group B/
│   ├── assets/
│   ├── datasets/
│   ├── Dash/
│   ├── yydsCalculator.py
│   ├── src_historical_versions/
│   ├── structured_feedback_handler.py
│   ├── CompleteDataset.csv
│   └── README.md
```


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


**Requirements**

Ensure Python is installed on your system. Required libraries are all stored in the ***requirements.txt***

Data Setup:
Place the CSV file, merged_df.csv, in the same directory as plotlt.py. The file should include:
Year column: Numeric values for years

Building Name column: Categorical data for building names


**Project Structure**

plotlt.py: Main application file for the Dash app.

merged_df.csv: CSV data source file.

**Troubleshooting**

Encoding Errors: If the CSV file has encoding issues, the app attempts to resolve these by setting encoding="utf-8" or "latin-1" and encoding_errors="ignore".
Graph Display Issues: Ensure the dataset has required columns (Year, Building Name) and values are correctly formatted.
