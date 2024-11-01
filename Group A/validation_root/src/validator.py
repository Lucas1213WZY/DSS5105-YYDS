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

    def predict_green_mark(self, scope1, scope2, scope3, gfa):
        """
        Predict Green Mark level based on emissions and GFA
        
        Args:
            scope1 (float): Scope 1 emissions (tCO2e)
            scope2 (float): Scope 2 emissions (tCO2e)
            scope3 (float): Scope 3 emissions (tCO2e)
            gfa (float): Gross Floor Area (m²)
            
        Returns:
            dict: Prediction results including GHG intensity and Green Mark level
        """
        try:
            # Calculate total GHG and intensity
            total_ghg = scope1 + scope2 + scope3
            ghg_intensity = total_ghg / gfa
            
            # Determine Green Mark level
            predicted_level = 'Not Certified'
            for level, threshold in sorted(self.benchmarks.items(), 
                                        key=lambda x: x[1]):
                if ghg_intensity <= threshold:
                    predicted_level = level
                    break

            return {
                'success': True,
                'ghg_results': {
                    'total_ghg': round(total_ghg, 2),
                    'ghg_intensity': round(ghg_intensity, 4),
                    'breakdown': {
                        'scope1': round(scope1, 2),
                        'scope2': round(scope2, 2),
                        'scope3': round(scope3, 2),
                    }
                },
                'green_mark': {
                    'predicted_level': predicted_level,
                    'threshold': self.benchmarks.get(predicted_level, 'N/A'),
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }