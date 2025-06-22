"""
Soil Agent for collecting and analyzing soil data
"""

import requests
import json
from typing import Dict, List, Optional
import numpy as np

class SoilAgent:
    """Specialized agent for soil data collection and analysis"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.usda_soil_url = config['SOIL_API_CONFIG']['usda_soil_url']
    
    def get_soil_data(self, latitude: float, longitude: float) -> Dict:
        """
        Get soil data for a specific location
        """
        try:
            # Try to get data from multiple sources
            soil_data = {}
            
            # Get basic soil information
            basic_soil = self._get_basic_soil_info(latitude, longitude)
            soil_data.update(basic_soil)
            
            # Add soil analysis
            soil_analysis = self._analyze_soil_quality(soil_data)
            soil_data.update(soil_analysis)
            
            return soil_data
            
        except Exception as e:
            print(f"Error fetching soil data: {e}")
            return self._get_default_soil_data()
    
    def _get_basic_soil_info(self, latitude: float, longitude: float) -> Dict:
        """
        Get basic soil information (simplified since USDA API requires complex queries)
        """
        try:
            # For demonstration, we'll use a simplified approach
            # In practice, you'd need to implement proper USDA Soil Data Access queries
            
            # Estimate soil type based on geographical patterns (simplified)
            soil_type = self._estimate_soil_type(latitude, longitude)
            ph_level = self._estimate_soil_ph(latitude, longitude)
            
            return {
                'soil_type': soil_type,
                'soil_ph': ph_level,
                'organic_matter': np.random.normal(2.5, 0.5),  # Typical range 1-4%
                'nitrogen_level': np.random.normal(25, 5),     # mg/kg
                'phosphorus_level': np.random.normal(15, 3),   # mg/kg
                'potassium_level': np.random.normal(120, 20),  # mg/kg
                'drainage': self._estimate_drainage(soil_type),
                'data_source': 'Estimated'
            }
            
        except Exception as e:
            print(f"Error getting basic soil info: {e}")
            return self._get_default_soil_data()
    
    def _estimate_soil_type(self, latitude: float, longitude: float) -> str:
        """
        Estimate soil type based on geographical location (simplified)
        """
        # This is a simplified estimation - in practice you'd use proper soil databases
        
        # General patterns for different regions
        if 25 <= latitude <= 35:  # Southern regions
            if -100 <= longitude <= -80:
                return 'clay loam'
            else:
                return 'sandy loam'
        elif 35 <= latitude <= 45:  # Midwest regions
            return 'loam'
        elif 45 <= latitude <= 50:  # Northern regions
            return 'silt loam'
        else:
            return 'loam'  # Default
    
    def _estimate_soil_ph(self, latitude: float, longitude: float) -> float:
        """
        Estimate soil pH based on geographical patterns
        """
        # Simplified estimation based on regional patterns
        if 25 <= latitude <= 35:  # Southern regions tend to be more acidic
            return np.random.normal(5.8, 0.3)
        elif 35 <= latitude <= 45:  # Midwest - neutral to slightly alkaline
            return np.random.normal(6.5, 0.4)
        else:  # Northern regions
            return np.random.normal(6.2, 0.3)
    
    def _estimate_drainage(self, soil_type: str) -> str:
        """
        Estimate drainage characteristics based on soil type
        """
        drainage_map = {
            'sandy loam': 'good',
            'loam': 'moderate',
            'clay loam': 'slow',
            'clay': 'poor',
            'silt loam': 'moderate'
        }
        return drainage_map.get(soil_type, 'moderate')
    
    def _analyze_soil_quality(self, soil_data: Dict) -> Dict:
        """
        Analyze soil quality and provide scores
        """
        try:
            ph = soil_data.get('soil_ph', 6.5)
            organic_matter = soil_data.get('organic_matter', 2.5)
            nitrogen = soil_data.get('nitrogen_level', 25)
            phosphorus = soil_data.get('phosphorus_level', 15)
            potassium = soil_data.get('potassium_level', 120)
            
            # Calculate quality scores (0-100)
            ph_score = self._calculate_ph_score(ph)
            nutrient_score = self._calculate_nutrient_score(nitrogen, phosphorus, potassium)
            organic_score = self._calculate_organic_score(organic_matter)
            
            overall_score = (ph_score + nutrient_score + organic_score) / 3
            
            return {
                'soil_quality_scores': {
                    'ph_score': ph_score,
                    'nutrient_score': nutrient_score,
                    'organic_matter_score': organic_score,
                    'overall_score': overall_score
                },
                'soil_recommendations': self._generate_soil_recommendations(
                    ph, organic_matter, nitrogen, phosphorus, potassium
                )
            }
            
        except Exception as e:
            print(f"Error analyzing soil quality: {e}")
            return {'soil_quality_scores': {'overall_score': 70}}
    
    def _calculate_ph_score(self, ph: float) -> float:
        """Calculate pH score (optimal range 6.0-7.0)"""
        if 6.0 <= ph <= 7.0:
            return 100
        elif 5.5 <= ph < 6.0 or 7.0 < ph <= 7.5:
            return 80
        elif 5.0 <= ph < 5.5 or 7.5 < ph <= 8.0:
            return 60
        else:
            return 40
    
    def _calculate_nutrient_score(self, n: float, p: float, k: float) -> float:
        """Calculate nutrient score based on NPK levels"""
        # Optimal ranges (simplified)
        n_score = 100 if 20 <= n <= 40 else max(0, 100 - abs(n - 30) * 3)
        p_score = 100 if 10 <= p <= 25 else max(0, 100 - abs(p - 17.5) * 4)
        k_score = 100 if 100 <= k <= 150 else max(0, 100 - abs(k - 125) * 1)
        
        return (n_score + p_score + k_score) / 3
    
    def _calculate_organic_score(self, organic_matter: float) -> float:
        """Calculate organic matter score"""
        if organic_matter >= 3.0:
            return 100
        elif organic_matter >= 2.0:
            return 80
        elif organic_matter >= 1.0:
            return 60
        else:
            return 40
    
    def _generate_soil_recommendations(
        self, 
        ph: float, 
        organic_matter: float, 
        nitrogen: float, 
        phosphorus: float, 
        potassium: float
    ) -> List[str]:
        """Generate soil improvement recommendations"""
        recommendations = []
        
        # pH recommendations
        if ph < 6.0:
            recommendations.append("Apply lime to increase soil pH")
        elif ph > 7.5:
            recommendations.append("Apply sulfur or organic matter to lower soil pH")
        
        # Organic matter recommendations
        if organic_matter < 2.0:
            recommendations.append("Add compost or organic matter to improve soil structure")
        
        # Nutrient recommendations
        if nitrogen < 20:
            recommendations.append("Apply nitrogen fertilizer or nitrogen-fixing cover crops")
        elif nitrogen > 40:
            recommendations.append("Reduce nitrogen inputs to prevent leaching")
        
        if phosphorus < 10:
            recommendations.append("Apply phosphorus fertilizer")
        
        if potassium < 100:
            recommendations.append("Apply potassium fertilizer or potash")
        
        if not recommendations:
            recommendations.append("Soil conditions are good for most crops")
        
        return recommendations
    
    def analyze_soil_crop_compatibility(
        self, 
        soil_data: Dict, 
        crop_requirements: Dict
    ) -> Dict:
        """
        Analyze how well soil conditions match crop requirements
        """
        try:
            soil_type = soil_data.get('soil_type', 'loam')
            soil_ph = soil_data.get('soil_ph', 6.5)
            drainage = soil_data.get('drainage', 'moderate')
            
            # Check soil type compatibility
            required_soil_types = crop_requirements.get('soil_types', [])
            soil_type_match = soil_type in required_soil_types
            
            # Check pH compatibility
            ph_min, ph_max = crop_requirements.get('soil_ph_range', (6.0, 7.0))
            ph_compatible = ph_min <= soil_ph <= ph_max
            
            # Calculate compatibility score
            type_score = 100 if soil_type_match else 60
            ph_score = 100 if ph_compatible else max(0, 100 - abs(soil_ph - (ph_min + ph_max) / 2) * 20)
            
            compatibility_score = (type_score + ph_score) / 2
            
            return {
                'compatibility_score': compatibility_score,
                'soil_type_match': soil_type_match,
                'ph_compatible': ph_compatible,
                'current_conditions': {
                    'soil_type': soil_type,
                    'soil_ph': soil_ph,
                    'drainage': drainage
                },
                'required_conditions': {
                    'soil_types': required_soil_types,
                    'ph_range': crop_requirements.get('soil_ph_range')
                },
                'adaptation_suggestions': self._generate_adaptation_suggestions(
                    soil_data, crop_requirements
                )
            }
            
        except Exception as e:
            print(f"Error analyzing soil-crop compatibility: {e}")
            return {'compatibility_score': 70}
    
    def _generate_adaptation_suggestions(
        self, 
        soil_data: Dict, 
        crop_requirements: Dict
    ) -> List[str]:
        """Generate suggestions to adapt soil for specific crop"""
        suggestions = []
        
        soil_ph = soil_data.get('soil_ph', 6.5)
        ph_range = crop_requirements.get('soil_ph_range', (6.0, 7.0))
        
        if soil_ph < ph_range[0]:
            suggestions.append(f"Apply lime to raise pH to {ph_range[0]}-{ph_range[1]}")
        elif soil_ph > ph_range[1]:
            suggestions.append(f"Apply sulfur to lower pH to {ph_range[0]}-{ph_range[1]}")
        
        soil_type = soil_data.get('soil_type', 'loam')
        required_types = crop_requirements.get('soil_types', [])
        
        if soil_type not in required_types:
            if 'sandy loam' in required_types and soil_type == 'clay':
                suggestions.append("Add sand and organic matter to improve drainage")
            elif 'clay loam' in required_types and soil_type == 'sandy loam':
                suggestions.append("Add clay and organic matter to improve water retention")
        
        return suggestions
    
    def get_soil_moisture_forecast(self, latitude: float, longitude: float) -> Dict:
        """
        Estimate soil moisture based on weather forecast
        """
        try:
            # Simplified soil moisture estimation
            # In practice, this would integrate with weather data and soil characteristics
            
            return {
                'current_moisture': np.random.normal(25, 5),  # % moisture
                'forecast_7days': [np.random.normal(25, 3) for _ in range(7)],
                'moisture_status': 'adequate',
                'irrigation_needed': False,
                'recommendations': ['Monitor soil moisture regularly']
            }
            
        except Exception as e:
            print(f"Error getting soil moisture forecast: {e}")
            return {
                'current_moisture': 25,
                'moisture_status': 'adequate',
                'irrigation_needed': False
            }
    
    def _get_default_soil_data(self) -> Dict:
        """Default soil data when APIs fail"""
        return {
            'soil_type': 'loam',
            'soil_ph': 6.5,
            'organic_matter': 2.5,
            'nitrogen_level': 25,
            'phosphorus_level': 15,
            'potassium_level': 120,
            'drainage': 'moderate',
            'data_source': 'Default',
            'soil_quality_scores': {
                'ph_score': 85,
                'nutrient_score': 80,
                'organic_matter_score': 75,
                'overall_score': 80
            },
            'soil_recommendations': ['Regular soil testing recommended']
        }
