import pandas as pd
from datetime import datetime
import json
import os

class FeedbackCollector:
    """Collect and store user feedback for the Green Mark Validator"""
    
    def __init__(self, storage_path='feedback_data.csv'):
        """
        Initialize feedback collector
        
        Args:
            storage_path (str): Path to store feedback data
        """
        self.storage_path = storage_path
        self.feedback_schema = {
            'timestamp': [],
            'green_mark_accuracy': [],
            'ghg_calculation_clarity': [],
            'visualization_helpfulness': [],
            'feature_ratings': {
                'ghg_intensity': [],
                'emissions_breakdown': [],
                'benchmark_comparison': []
            },
            'requested_features': [],
            'overall_satisfaction': []
        }
        
    def collect_feedback(self, 
                        green_mark_accuracy: int,
                        ghg_calculation_clarity: int,
                        visualization_helpfulness: int,
                        feature_ratings: dict,
                        requested_features: list,
                        overall_satisfaction: int) -> dict:
        """
        Collect user feedback
        
        Args:
            green_mark_accuracy (int): Rating 1-5
            ghg_calculation_clarity (int): Rating 1-5
            visualization_helpfulness (int): Rating 1-5
            feature_ratings (dict): Ratings for specific features
            requested_features (list): List of requested future features
            overall_satisfaction (int): Rating 1-5
            
        Returns:
            dict: Processed feedback data
        """
        # Validate ratings
        for rating in [green_mark_accuracy, ghg_calculation_clarity, 
                      visualization_helpfulness, overall_satisfaction]:
            if not 1 <= rating <= 5:
                raise ValueError("Ratings must be between 1 and 5")
                
        # Create feedback entry
        feedback_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'green_mark_accuracy': green_mark_accuracy,
            'ghg_calculation_clarity': ghg_calculation_clarity,
            'visualization_helpfulness': visualization_helpfulness,
            'feature_ratings': feature_ratings,
            'requested_features': requested_features,
            'overall_satisfaction': overall_satisfaction
        }
        
        # Store feedback
        self._store_feedback(feedback_entry)
        
        return feedback_entry
    
    def _store_feedback(self, feedback_entry: dict):
        """Store feedback in CSV file"""
        # Convert to flat structure for CSV
        flat_entry = {
            'timestamp': feedback_entry['timestamp'],
            'green_mark_accuracy': feedback_entry['green_mark_accuracy'],
            'ghg_calculation_clarity': feedback_entry['ghg_calculation_clarity'],
            'visualization_helpfulness': feedback_entry['visualization_helpfulness'],
            'ghg_intensity_rating': feedback_entry['feature_ratings']['ghg_intensity'],
            'emissions_breakdown_rating': feedback_entry['feature_ratings']['emissions_breakdown'],
            'benchmark_comparison_rating': feedback_entry['feature_ratings']['benchmark_comparison'],
            'requested_features': ','.join(feedback_entry['requested_features']),
            'overall_satisfaction': feedback_entry['overall_satisfaction']
        }
        
        # Create DataFrame
        df_entry = pd.DataFrame([flat_entry])
        
        # Append to CSV
        if os.path.exists(self.storage_path):
            df_entry.to_csv(self.storage_path, mode='a', header=False, index=False)
        else:
            df_entry.to_csv(self.storage_path, index=False)
    
    def analyze_feedback(self) -> dict:
        """
        Analyze collected feedback
        
        Returns:
            dict: Analysis results
        """
        if not os.path.exists(self.storage_path):
            return {"error": "No feedback data available"}
            
        df = pd.read_csv(self.storage_path)
        
        analysis = {
            'average_ratings': {
                'green_mark_accuracy': df['green_mark_accuracy'].mean(),
                'ghg_calculation_clarity': df['ghg_calculation_clarity'].mean(),
                'visualization_helpfulness': df['visualization_helpfulness'].mean(),
                'overall_satisfaction': df['overall_satisfaction'].mean()
            },
            'feature_ratings': {
                'ghg_intensity': df['ghg_intensity_rating'].mean(),
                'emissions_breakdown': df['emissions_breakdown_rating'].mean(),
                'benchmark_comparison': df['benchmark_comparison_rating'].mean()
            },
            'most_requested_features': self._analyze_requested_features(df),
            'total_responses': len(df)
        }
        
        return analysis
    
    def _analyze_requested_features(self, df: pd.DataFrame) -> dict:
        """Analyze requested features from feedback"""
        all_requests = []
        for requests in df['requested_features'].dropna():
            all_requests.extend(requests.split(','))
            
        feature_counts = pd.Series(all_requests).value_counts().to_dict()
        return feature_counts

# Example usage
if __name__ == "__main__":
    # Initialize feedback collector
    collector = FeedbackCollector()
    
    # Example feedback submission
    feedback = collector.collect_feedback(
        green_mark_accuracy=3,
        ghg_calculation_clarity=3,
        visualization_helpfulness=3,
        feature_ratings={
            'ghg_intensity': 3,
            'emissions_breakdown': 3,
            'benchmark_comparison': 3
        },
        requested_features=[
            'Historical data comparison',
            'Comparison with similar buildings',
            'Emission reduction recommendations'
        ],
        overall_satisfaction=3
    )
    
    # Example feedback analysis
    analysis = collector.analyze_feedback()
    print("\nFeedback Analysis:")
    print(json.dumps(analysis, indent=2))