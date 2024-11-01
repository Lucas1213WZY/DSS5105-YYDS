# Green Mark Calculator Project

## Overview
A validation system for predicting Green Mark certification levels for Singapore's office buildings based on GHG emissions data.

## Features
- GHG intensity calculation and validation
- Green Mark level prediction
- Emissions breakdown analysis with visualizations
- Benchmark comparisons
- User feedback collection

## Project Structure
```
validation_root/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── validator.py         # Core validation logic
│   ├── viz_helpers.py       # Visualization functions
│   └── feedback.py          # User feedback collection
├── notebooks/
│   └── validation_testing.ipynb  # Testing notebook
├── tests/
│   ├── __init__.py
│   └── test_validator.py    # Unit tests
└── docs/
    ├── README.md           # This file
    └── integration_guide.md # Integration guide
```

## Installation
1. Clone the repository
2. Install requirements:
```bash
pip install -r requirements.txt
```

## Required Dependencies
- pandas
- numpy
- matplotlib
- seaborn

## Quick Start
```python
from src.validator import GreenMarkValidator
from src.viz_helpers import ValidationVisualizer
from src.feedback import FeedbackCollector

# Initialize components
validator = GreenMarkValidator()
visualizer = ValidationVisualizer()
feedback_collector = FeedbackCollector()

# Make prediction
result = validator.predict_green_mark(
    scope1=82.74,
    scope2=1852.64,
    scope3=1989.55,
    gfa=35218.0
)

# Generate visualizations
visualizer.plot_ghg_results(result)
visualizer.plot_emissions_breakdown(result)
visualizer.plot_benchmarks(result)

# Collect user feedback
feedback_collector.collect_feedback(...)
```

## Documentation
- See integration_guide.md for detailed integration instructions
- See notebooks/validation_testing.ipynb for usage examples

## Team
- Subgroup A: Validation System
- Subgroup B: Frontend Integration