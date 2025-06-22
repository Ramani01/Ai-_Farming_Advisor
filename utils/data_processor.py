"""
Data processing utilities for the farming agent
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json

class DataProcessor:
    """Handles data processing and analysis for farming recommendations"""
    
    def __init__(self):
        self.current_date = datetime.now()
    
    def calculate_crop_suitability_score(
        self, 
        crop_requirements: Dict, 
        environmental_conditions: Dict
    ) -> float:
        """
        Calculate suitability score for a crop based on environmental conditions
        Returns a score from 0-100
        """
        score = 0.0
        total_factors = 0
        
        # Temperature compatibility (30% weight)
        if 'temperature' in environmental_conditions:
            temp = environmental_conditions['temperature']
            temp_min, temp_max = crop_requirements['optimal_temp_range']
            
            if temp_min <= temp <= temp_max:
                temp_score = 100
            else:
                # Calculate penalty based on distance from optimal range
                if temp < temp_min:
                    temp_score = max(0, 100 - abs(temp - temp_min) * 5)
                else:
                    temp_score = max(0, 100 - abs(temp - temp_max) * 5)
            
            score += temp_score * 0.3
            total_factors += 0.3
        
        # Rainfall compatibility (25% weight)
        if 'rainfall' in environmental_conditions:
            rainfall = environmental_conditions['rainfall']
            rain_min, rain_max = crop_requirements['rainfall_requirement']
            
            if rain_min <= rainfall <= rain_max:
                rain_score = 100
            else:
                if rainfall < rain_min:
                    rain_score = max(0, 100 - abs(rainfall - rain_min) / rain_min * 50)
                else:
                    rain_score = max(0, 100 - abs(rainfall - rain_max) / rain_max * 30)
            
            score += rain_score * 0.25
            total_factors += 0.25
        
        # Soil pH compatibility (20% weight)
        if 'soil_ph' in environmental_conditions:
            ph = environmental_conditions['soil_ph']
            ph_min, ph_max = crop_requirements['soil_ph_range']
            
            if ph_min <= ph <= ph_max:
                ph_score = 100
            else:
                ph_score = max(0, 100 - abs(ph - (ph_min + ph_max) / 2) * 20)
            
            score += ph_score * 0.2
            total_factors += 0.2
        
        # Soil type compatibility (15% weight)
        if 'soil_type' in environmental_conditions:
            soil_type = environmental_conditions['soil_type'].lower()
            if soil_type in crop_requirements['soil_types']:
                soil_score = 100
            else:
                soil_score = 50  # Partial compatibility
            
            score += soil_score * 0.15
            total_factors += 0.15
        
        # Seasonal timing (10% weight)
        current_month = self.current_date.month
        if current_month in crop_requirements['planting_months']:
            seasonal_score = 100
        else:
            # Find closest planting month
            planting_months = crop_requirements['planting_months']
            distances = [min(abs(current_month - pm), 12 - abs(current_month - pm)) 
                        for pm in planting_months]
            closest_distance = min(distances)
            seasonal_score = max(0, 100 - closest_distance * 20)
        
        score += seasonal_score * 0.1
        total_factors += 0.1
        
        # Normalize score
        if total_factors > 0:
            return score / total_factors
        else:
            return 0.0
    
    def calculate_profit_potential(
        self, 
        crop_name: str, 
        market_prices: Dict, 
        production_costs: Dict,
        yield_estimate: float,
        land_area: float = 1.0  # in hectares
    ) -> Dict:
        """
        Calculate profit potential for a crop
        """
        crop_price = market_prices.get(crop_name, 0)
        base_cost = production_costs.get(crop_name, 0)
        
        # Calculate revenue
        total_yield = yield_estimate * land_area
        gross_revenue = total_yield * crop_price
        
        # Calculate costs
        total_costs = base_cost * land_area
        
        # Calculate profit
        net_profit = gross_revenue - total_costs
        profit_margin = (net_profit / gross_revenue * 100) if gross_revenue > 0 else 0
        
        return {
            'crop_name': crop_name,
            'gross_revenue': gross_revenue,
            'total_costs': total_costs,
            'net_profit': net_profit,
            'profit_margin': profit_margin,
            'yield_per_hectare': yield_estimate,
            'price_per_unit': crop_price,
            'roi_percentage': (net_profit / total_costs * 100) if total_costs > 0 else 0
        }
    
    def rank_crops_by_profitability(
        self, 
        crop_analyses: List[Dict]
    ) -> List[Dict]:
        """
        Rank crops by their profitability and suitability
        """
        # Combine suitability score and profit potential
        for analysis in crop_analyses:
            suitability = analysis.get('suitability_score', 0)
            roi = analysis.get('profit_analysis', {}).get('roi_percentage', 0)
            
            # Combined score: 60% suitability, 40% profitability
            combined_score = (suitability * 0.6) + (min(roi, 100) * 0.4)
            analysis['combined_score'] = combined_score
        
        # Sort by combined score
        ranked_crops = sorted(crop_analyses, key=lambda x: x['combined_score'], reverse=True)
        
        return ranked_crops
    
    def generate_planting_calendar(
        self, 
        recommended_crops: List[Dict],
        months_ahead: int = 12
    ) -> Dict:
        """
        Generate a planting calendar for recommended crops
        """
        calendar = {}
        
        for i in range(months_ahead):
            month_date = self.current_date + timedelta(days=30*i)
            month_key = month_date.strftime("%Y-%m")
            month_num = month_date.month
            
            calendar[month_key] = {
                'month_name': month_date.strftime("%B %Y"),
                'recommended_crops': []
            }
            
            for crop in recommended_crops:
                crop_name = crop.get('crop_name', '')
                planting_months = crop.get('planting_months', [])
                
                if month_num in planting_months:
                    calendar[month_key]['recommended_crops'].append({
                        'name': crop_name,
                        'suitability_score': crop.get('suitability_score', 0),
                        'expected_profit': crop.get('profit_analysis', {}).get('net_profit', 0)
                    })
        
        return calendar
    
    def calculate_risk_assessment(
        self, 
        crop_name: str, 
        environmental_data: Dict,
        historical_data: Optional[Dict] = None
    ) -> Dict:
        """
        Assess risks for crop cultivation
        """
        risks = {
            'weather_risk': 'low',
            'market_risk': 'medium',
            'pest_risk': 'low',
            'overall_risk': 'low'
        }
        
        risk_factors = []
        
        # Weather risk assessment
        if 'temperature_variance' in environmental_data:
            temp_var = environmental_data['temperature_variance']
            if temp_var > 5:
                risks['weather_risk'] = 'high'
                risk_factors.append("High temperature variability")
            elif temp_var > 3:
                risks['weather_risk'] = 'medium'
                risk_factors.append("Moderate temperature variability")
        
        # Rainfall risk
        if 'rainfall_uncertainty' in environmental_data:
            rain_uncert = environmental_data['rainfall_uncertainty']
            if rain_uncert > 30:
                risks['weather_risk'] = 'high'
                risk_factors.append("High rainfall uncertainty")
        
        # Market volatility (simplified)
        seasonal_crops = ['tomatoes', 'potatoes', 'carrots']
        if crop_name in seasonal_crops:
            risks['market_risk'] = 'high'
            risk_factors.append("Seasonal price volatility")
        
        # Overall risk calculation
        risk_levels = {'low': 1, 'medium': 2, 'high': 3}
        avg_risk = sum(risk_levels[risks[key]] for key in ['weather_risk', 'market_risk', 'pest_risk']) / 3
        
        if avg_risk >= 2.5:
            risks['overall_risk'] = 'high'
        elif avg_risk >= 1.5:
            risks['overall_risk'] = 'medium'
        
        return {
            'risk_levels': risks,
            'risk_factors': risk_factors,
            'risk_score': avg_risk * 33.33  # Convert to 0-100 scale
        }
    
    def format_recommendations(
        self, 
        ranked_crops: List[Dict],
        top_n: int = 5
    ) -> Dict:
        """
        Format crop recommendations for user display
        """
        top_crops = ranked_crops[:top_n]
        
        recommendations = {
            'timestamp': self.current_date.isoformat(),
            'total_crops_analyzed': len(ranked_crops),
            'top_recommendations': [],
            'summary': {
                'best_crop': top_crops[0]['crop_name'] if top_crops else 'None',
                'expected_profit': top_crops[0].get('profit_analysis', {}).get('net_profit', 0) if top_crops else 0,
                'confidence_score': top_crops[0].get('combined_score', 0) if top_crops else 0
            }
        }
        
        for i, crop in enumerate(top_crops):
            rec = {
                'rank': i + 1,
                'crop_name': crop['crop_name'],
                'suitability_score': round(crop.get('suitability_score', 0), 1),
                'combined_score': round(crop.get('combined_score', 0), 1),
                'profit_analysis': crop.get('profit_analysis', {}),
                'risk_assessment': crop.get('risk_assessment', {}),
                'planting_advice': self._generate_planting_advice(crop)
            }
            recommendations['top_recommendations'].append(rec)
        
        return recommendations
    
    def _generate_planting_advice(self, crop_data: Dict) -> Dict:
        """
        Generate specific planting advice for a crop
        """
        crop_name = crop_data.get('crop_name', '')
        
        advice = {
            'best_planting_time': 'Next suitable season',
            'land_preparation': f'Prepare land according to {crop_name} requirements',
            'irrigation_advice': 'Ensure adequate water supply',
            'fertilizer_recommendations': 'Use appropriate fertilizers for soil type'
        }
        
        # More specific advice can be added based on crop type and conditions
        return advice
