# structured_feedback_handler.py

import sqlite3
import pandas as pd
import json

class StructuredFeedbackHandler:
    def __init__(self):
        # Allow the SQLite connection to be accessed across different threads
        self.conn = sqlite3.connect('feedback.db', check_same_thread=False)
        self.create_feedback_table()
    
    def create_feedback_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS structured_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                building_name TEXT,
                predicted_level TEXT,
                prediction_accuracy INTEGER,
                calculation_clarity INTEGER,
                visualization_helpfulness INTEGER,
                ghg_intensity_rating INTEGER,
                emissions_breakdown_rating INTEGER,
                benchmark_comparison_rating INTEGER,
                improvement_priorities TEXT,
                overall_satisfaction INTEGER,
                timestamp DATETIME
            )
        ''')
        self.conn.commit()
    
    def store_feedback(self, feedback_data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO structured_feedback (
                building_name, predicted_level, prediction_accuracy, calculation_clarity, 
                visualization_helpfulness, ghg_intensity_rating, emissions_breakdown_rating, 
                benchmark_comparison_rating, improvement_priorities, overall_satisfaction, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            feedback_data['building_name'],
            feedback_data['predicted_level'],
            feedback_data['prediction_accuracy'],
            feedback_data['calculation_clarity'],
            feedback_data['visualization_helpfulness'],
            feedback_data['feature_ratings']['ghg_intensity'],
            feedback_data['feature_ratings']['emissions_breakdown'],
            feedback_data['feature_ratings']['benchmark_comparison'],
            json.dumps(feedback_data['improvement_priorities']),
            feedback_data['overall_satisfaction'],
            feedback_data['timestamp']
        ))
        self.conn.commit()
    
    def export_feedback_to_excel(self):
        df = pd.read_sql_query("SELECT * FROM structured_feedback", self.conn)
        excel_path = 'feedback_data.xlsx'
        df.to_excel(excel_path, index=False)
        return excel_path
