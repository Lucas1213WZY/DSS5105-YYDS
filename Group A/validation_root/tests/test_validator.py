import unittest
import pandas as pd
from src.validator import GreenMarkValidator
from src.viz_helpers import ValidationVisualizer
from src.feedback import FeedbackCollector

class TestGreenMarkValidation(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.validator = GreenMarkValidator()
        self.visualizer = ValidationVisualizer()
        self.feedback_collector = FeedbackCollector()
        
        # Sample building data
        self.test_building = {
            'scope1': 82.74,
            'scope2': 1852.64,
            'scope3': 1989.55,
            'gfa': 35218.0
        }
    
    def test_complete_validation_workflow(self):
        """Test entire validation workflow"""
        # 1. Validate building data
        result = self.validator.predict_green_mark(**self.test_building)
        
        # Check basic validation results
        self.assertTrue(result['success'])
        self.assertIn('ghg_results', result)
        self.assertIn('green_mark', result)
        
        # 2. Test visualization generation
        try:
            self.visualizer.plot_ghg_results(result)
            self.visualizer.plot_emissions_breakdown(result)
            self.visualizer.plot_benchmarks(result)
        except Exception as e:
            self.fail(f"Visualization generation failed: {str(e)}")
    
    def test_batch_processing(self):
        """Test processing multiple buildings"""
        test_df = pd.DataFrame({
            'scope1': [82.74, 100],
            'scope2': [1852.64, 2000],
            'scope3': [1989.55, 2000],
            'gfa': [35218.0, 40000]
        })
        
        for idx, row in test_df.iterrows():
            result = self.validator.predict_green_mark(
                scope1=row['scope1'],
                scope2=row['scope2'],
                scope3=row['scope3'],
                gfa=row['gfa']
            )
            self.assertTrue(result['success'])
    
    def test_feedback_collection(self):
        """Test feedback collection and analysis"""
        feedback = self.feedback_collector.collect_feedback(
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
                'Comparison with similar buildings'
            ],
            overall_satisfaction=3
        )
        
        self.assertIsNotNone(feedback)
        
        # Test feedback analysis
        analysis = self.feedback_collector.analyze_feedback()
        self.assertIsNotNone(analysis)
    
    def test_error_handling(self):
        """Test error handling in validation workflow"""
        # Test invalid input
        invalid_building = {
            'scope1': -100,  # Invalid negative value
            'scope2': 2000,
            'scope3': 2000,
            'gfa': 1000
        }
        
        result = self.validator.predict_green_mark(**invalid_building)
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_visualization_error_handling(self):
        """Test visualization error handling"""
        invalid_result = {'success': False, 'error': 'Invalid data'}
        
        with self.assertRaises(Exception):
            self.visualizer.plot_ghg_results(invalid_result)

if __name__ == '__main__':
    unittest.main()