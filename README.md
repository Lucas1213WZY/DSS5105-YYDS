<img src="https://github.com/Lucas1213WZY/DSS5105-YYDS/blob/main/Group%20B/assets/teamlogo.png" alt="Logo" width="150" align="left">

# DSS5105-YYDS [Your Yielding partner in sustainable Development Solutions]


**We are a company that provides GHG Emission Calculations and Estimations for Buildings in Singapore. This is an easy-to-use, interactive and customizable calculator and dashboard with all-in-one functionality:**
* Automatic Data Validation and Cleaning, Data Analysis, Machine Learning Model and Indicator Combined Prediction, Data Visualizations
* Benchmarking & Ratings with Green Mark Incentive Schemes, Customizable GHG Reduction Recommendations
* AI-Powered GHG Emission Chatbot Assistant

```
    "Project Assessment: for the openai API Key please find attached the key in the Group B/assets/openaiAPIkey.pdf, passwd: 5105yyds, thank you!"
```

**To install and use this Calculator:**

1.**Clone the repository**:

    git clone https://github.com/Lucas1213WZY/DSS5105-YYDS.git

    
2.**After that use pip install or conda install to install all required libraries**:


    pip/conda install requirements.txt

    
3.**Change directory from the root to Group B to run the yydsCalculator**:


    cd Group\ B
    python/run yydsCalculator.py

    
4.**Once it's running, please go to your browser and use the link below to access the application on your ease**:


    http://127.0.0.1:8050/
    
Tutorial Video

**Please visit this link for more detailed tutorials**: 
https://drive.google.com/file/d/1_aHJkNOm_8wIf8eiH5TUHi5JyQGWG6sc/view?usp=sharing

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
For Demo pls upload the CSV file : merged_df1.csv, from the "datasets" folder in Group B folder. For your own calculations, please follow the below data dictionary.
The file should include:
| Column Name          | Description                                                                                  | Data Type | Required |
|-----------------------|----------------------------------------------------------------------------------------------|-----------|----------|
| **Building Name**     | Name of the building                                                                        | String    | Yes      |
| **Postcode**          | Postal code of the building location                                                        | Integer   | Yes      |
| **Year**              | Year of data collection                                                                     | Integer   | Yes      |
| **Latitude**          | Latitude coordinate of the building                                                         | Integer   | Yes      |
| **Longitude**         | Longitude coordinate of the building                                                        | Integer   | Yes      |
| **Address**           | Full address of the building                                                                | String    | Yes      |
| **Type**              | Type of building (e.g., only applicable to office buildings)                                | String    | Yes      |
| **Function**          | Functionality of the building (e.g., office)                                                | String    | Yes      |
| **Size**              | Size of the building (e.g., area in square meters)                                          | Float     | Yes      |
| **Employee**          | Number of employees working in the building                                                 | Integer   | Yes      |
| **Transportation**    | Transportation-related data (e.g., parking spaces, public transit proximity)                | String    | Yes      |
| **GFA**               | Gross Floor Area of the building  (in m²)                                                   | Float     | Yes      |
| **Energy**            | Energy consumption data (e.g., kWh/year)                                                    | Float     | Yes      |
| **Waste**             | Waste production data (e.g., tons/year)                                                     | Float     | Yes      |
| **Water**             | Water consumption data (e.g., m³/year)                                                      | Float     | Yes      |
| **Scope1**            | Direct GHG emissions (Scope 1, t CO2e)                                                      | Float     | No       |
| **Scope2**            | Indirect GHG emissions from electricity (Scope 2, t CO2e)                                   | Float     | No       |
| **Scope3**            | Other indirect GHG emissions (Scope 3, t CO2e)                                              | Float     | No       |
| **GHG_Total**         | Total GHG emissions (t CO2e) [to be predicted/calculated]                                   | Float     | No       |
| **GHG_Intensity**     | GHG emissions per unit area or employee (e.g., t CO2e/m²)[to be predicted/calculated]       | Float     | No       |
| **Award**             | Awards or certifications (i.e., Green Mark Incentive Scheme) [to be predicted]              | String    | No       |

For manual input options: Transportation breakdowns are also needed : (commuting: Bus, MRT, Taxi; 
Business Travel: Flight & Hotel(Cost); Business Procurement: Air Freight, Electric Truck, Diesel Truck.)


**Troubleshooting**

Encoding Errors: If the CSV file has encoding issues, the app attempts to resolve these by setting encoding="utf-8" or "latin-1" and encoding_errors="ignore".
Graph Display Issues: Ensure the dataset has required columns (Year, Building Name) and values are correctly formatted.
