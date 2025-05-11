# analysis/analyzer.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import re
import os

class BusinessAnalyzer:
    def __init__(self):
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
    
    def analyze_turnaround_potential(self, df):
        """
        Analyze businesses for turnaround potential
        Returns dataframe with turnaround scores
        """
        # Make a copy to avoid modifying the original
        analysis_df = df.copy()
        
        # Calculate basic financial metrics
        analysis_df['price_to_revenue_ratio'] = analysis_df.apply(
            lambda row: row['price'] / max(row['revenue'], 1), axis=1
        )
        
        # Identify distressed signals from description
        analysis_df['price_drop'] = analysis_df['description'].str.contains(
            'reduced|price drop|discount|motivated seller', case=False).astype(int)
        
        analysis_df['urgency_signal'] = analysis_df['description'].str.contains(
            'urgent|quick sale|must sell', case=False).astype(int)
        
        # Calculate historical performance indicators
        analysis_df['declining_revenue'] = analysis_df['description'].str.contains(
            'declining|decreasing|reduced revenue|downturn', case=False).astype(int)
        
        analysis_df['management_issues'] = analysis_df['description'].str.contains(
            'management issues|poorly managed|understaffed|absentee', case=False).astype(int)
        
        # Calculate location value
        analysis_df['prime_location'] = analysis_df['description'].str.contains(
            'prime location|high traffic|busy area|popular', case=False).astype(int)
        
        # Simple turnaround score calculation
        # Higher score = better turnaround opportunity
        analysis_df['raw_score'] = (
            (1 - np.clip(analysis_df['price_to_revenue_ratio'] / 2, 0, 1)) * 30 + 
            analysis_df['price_drop'] * 15 +
            analysis_df['urgency_signal'] * 10 +
            analysis_df['declining_revenue'] * 15 +
            analysis_df['management_issues'] * 20 +
            analysis_df['prime_location'] * 10
        )
        
        # Normalize scores to 0-100 scale
        if len(analysis_df) > 0:  # Check if dataframe is not empty
            scaler = MinMaxScaler(feature_range=(0, 100))
            analysis_df['turnaround_score'] = scaler.fit_transform(
                analysis_df['raw_score'].values.reshape(-1, 1)
            ).flatten()
        else:
            analysis_df['turnaround_score'] = []
        
        # Add difficulty rating (1-5, with 5 being most difficult)
        analysis_df['turnaround_difficulty'] = analysis_df.apply(
            self._calculate_difficulty, axis=1
        )
        
        # Save analyzed data
        analysis_df.to_csv('data/analyzed_listings.csv', index=False)
        
        return analysis_df
    
    def _calculate_difficulty(self, row):
        """Calculate turnaround difficulty on a scale of 1-5"""
        difficulty = 3  # Default moderate difficulty
        
        # Factors that increase difficulty
        if row['declining_revenue'] == 1:
            difficulty += 1
        
        if row['price'] > 500000:
            difficulty += 1
        
        # Factors that decrease difficulty
        if row['management_issues'] == 1:
            difficulty -= 1
            
        if row['price_drop'] == 1:
            difficulty -= 0.5
            
        if row['prime_location'] == 1:
            difficulty -= 0.5
        
        # Ensure within range 1-5
        return max(1, min(5, round(difficulty)))