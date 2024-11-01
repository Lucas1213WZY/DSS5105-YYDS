# Green Mark Validator - Integration Guide

## Table of Contents
1. Overview
2. Installation
3. Components
4. Usage
5. Visualization
6. Feedback Collection
7. Error Handling
8. Examples
9. FAQ

## 1. Overview
The validation system consists of three main components:
- GreenMarkValidator: Core validation logic
- ValidationVisualizer: Results visualization
- FeedbackCollector: User feedback handling

## 2. Installation
```python
# Import all required components
from src.validator import GreenMarkValidator
from src.viz_helpers import ValidationVisualizer
from src.feedback import FeedbackCollector
```

## 3. Components

### 3.1 GreenMarkValidator
Core validation component that processes emissions data and predicts Green Mark levels.

```python
validator = GreenMarkValidator()
result = validator.predict_green_mark(
    scope1=82.74,     # Direct emissions
    scope2=1852.64,   # Energy indirect emissions
    scope3=1989.55,   # Other indirect emissions
    gfa=35218.0       # Gross Floor Area
)
```

### 3.2 ValidationVisualizer
Generates visualization of validation results.

```python
visualizer = ValidationVisualizer()

# Generate visualizations
visualizer.plot_ghg_results(result)        # Shows emissions summary
visualizer.plot_emissions_breakdown(result) # Shows scope breakdown
visualizer.plot_benchmarks(result)         # Shows benchmark comparison
```

### 3.3 FeedbackCollector
Handles user feedback collection.

```python
feedback_collector = FeedbackCollector()

feedback = feedback_collector.collect_feedback(
    green_mark_accuracy=3,
    ghg_calculation_clarity=3,
    visualization_helpfulness=3,
    feature_ratings={...},
    requested_features=[...],
    overall_satisfaction=3
)
```

## 4. Usage

### 4.1 Single Building Validation
```python
result = validator.predict_green_mark(
    scope1=82.74,
    scope2=1852.64,
    scope3=1989.55,
    gfa=35218.0
)
```

### 4.2 Batch Processing
```python
import pandas as pd

buildings_df = pd.DataFrame({
    'scope1': [82.74, 100],
    'scope2': [1852.64, 2000],
    'scope3': [1989.55, 2000],
    'gfa': [35218.0, 40000]
})

for idx, row in buildings_df.iterrows():
    result = validator.predict_green_mark(**row)
```

## 5. Visualization
The ValidationVisualizer provides three types of visualizations:
1. GHG Results Display
   - Total GHG emissions
   - GHG intensity
   - Predicted Green Mark level

2. Emissions Breakdown
   - Pie chart showing scope distribution
   - Percentage breakdown

3. Benchmark Comparison
   - Current performance vs benchmarks
   - Performance analysis
   - Next level target

## 6. Feedback Collection
The feedback form collects:
- Accuracy rating
- Clarity rating
- Visualization helpfulness
- Feature usefulness
- Requested features
- Overall satisfaction

## 7. Error Handling
Handle validation errors:
```python
result = validator.predict_green_mark(**building_data)
if result['success']:
    # Process results
    visualizer.plot_ghg_results(result)
else:
    print(f"Error: {result['error']}")
```

## 8. Examples
See validation_testing.ipynb for complete examples including:
- Single building validation
- Batch processing
- Visualization generation
- Feedback collection

## 9. FAQ

Q: What units should I use?
- Emissions: tCO₂e (tonnes of CO₂ equivalent)
- GFA: square meters (m²)

Q: How accurate is the prediction?
- Uses official Green Mark benchmarks with 10% buffer
- Validation match rate of 36.60% with existing dataset

Q: What if I don't have all the emissions data?
- All three scopes are required for accurate prediction
- Can't skip any scope values

## Notes for Integration
1. Data Validation
   - Convert string inputs to float
   - Check for positive values
   - Validate data ranges

2. Visualization
   - Handle visualization window/display
   - Save plots if needed
   - Customize colors if needed

3. Feedback
   - Implement feedback form UI
   - Store feedback data
   - Handle feedback submission

4. Best Practices
   - Always validate input data
   - Handle all error cases
   - Round displayed values appropriately
   - Provide clear feedback to users