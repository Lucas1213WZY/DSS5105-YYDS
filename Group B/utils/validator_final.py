import pandas as pd

class GreenMarkValidator:
    """Simple validator that Subgroup B can use to predict Green Mark levels"""
    
    def __init__(self):
        # Green Mark benchmarks with 10% buffer
        self.buffer = 1.1
        self.benchmarks = {
            'platinum': 0.1 * self.buffer,
            'goldplus': 0.12 * self.buffer,
            'gold': 0.15 * self.buffer,
            'certified': 0.2 * self.buffer
        }

    def predict_green_mark(self, ghg_intensity_results):
        """
        Predict Green Mark level based on emissions and GFA
        
        Args:
            ghg_intensity_results: list or pd.Series of GHG intensity (tCO2e)
            
        Returns:
            pd.DataFrame: Prediction results including GHG intensity and Green Mark level
        """
        # If input is not a Series, convert it to a Series for consistency
        if not isinstance(ghg_intensity_results, pd.Series):
            ghg_intensity_results = pd.Series(ghg_intensity_results)
        
        # Initialize an empty list to store results
        results = []

        # Loop through each GHG intensity result
        for ghg_intensity in ghg_intensity_results:
            # Determine Green Mark level
            predicted_level = 'Not Certified'
            for level, threshold in sorted(self.benchmarks.items(), key=lambda x: x[1]):
                if ghg_intensity <= threshold:
                    predicted_level = level
                    break
            
            # Append the result for each GHG intensity
            results.append({
                'ghg_intensity': round(ghg_intensity, 4),
                'predicted_level': predicted_level,
                'threshold': self.benchmarks.get(predicted_level, 'N/A')
            })

        # Convert results to a DataFrame and return
        return pd.DataFrame(results)
