"""
Weather Agent for collecting and analyzing weather data
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np

class WeatherAgent:
    """Specialized agent for weather data collection and analysis"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.open_meteo_url = config['WEATHER_API_CONFIG']['open_meteo_url']
        
    def get_current_weather(self, latitude: float, longitude: float) -> Dict:
        """
        Get current weather conditions for a location
        """
        try:
            # Using Open-Meteo (free, no API key required)
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'current_weather': 'true',
                'hourly': 'temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m',
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum',
                'timezone': 'auto',
                'forecast_days': 7
            }
            
            response = requests.get(self.open_meteo_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return self._process_weather_data(data)
            
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return self._get_default_weather_data()
    
    def get_historical_weather(
        self, 
        latitude: float, 
        longitude: float, 
        days_back: int = 30
    ) -> Dict:
        """
        Get historical weather data for analysis
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Open-Meteo historical API
            historical_url = "https://archive-api.open-meteo.com/v1/archive"
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max',
                'timezone': 'auto'
            }
            
            response = requests.get(historical_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._process_historical_data(data)
            
        except Exception as e:
            print(f"Error fetching historical weather data: {e}")
            return self._get_default_historical_data()
    
    def calculate_growing_degree_days(
        self, 
        daily_temps: List[Tuple[float, float]], 
        base_temp: float = 10.0
    ) -> List[float]:
        """
        Calculate Growing Degree Days (GDD) for crop development
        """
        gdd_values = []
        
        for max_temp, min_temp in daily_temps:
            avg_temp = (max_temp + min_temp) / 2
            gdd = max(0, avg_temp - base_temp)
            gdd_values.append(gdd)
        
        return gdd_values
    
    def analyze_weather_suitability(
        self, 
        weather_data: Dict, 
        crop_requirements: Dict
    ) -> Dict:
        """
        Analyze weather suitability for specific crop
        """
        current_temp = weather_data.get('current_temperature', 20)
        avg_temp = weather_data.get('average_temperature', 20)
        total_rainfall = weather_data.get('total_rainfall_7days', 0)
        
        # Temperature suitability
        temp_min, temp_max = crop_requirements['optimal_temp_range']
        temp_suitable = temp_min <= avg_temp <= temp_max
        
        # Rainfall suitability (convert weekly to annual estimate)
        annual_rainfall_estimate = total_rainfall * 52  # rough estimate
        rain_min, rain_max = crop_requirements['rainfall_requirement']
        rain_suitable = rain_min <= annual_rainfall_estimate <= rain_max
        
        # Overall weather score
        temp_score = 100 if temp_suitable else max(0, 100 - abs(avg_temp - (temp_min + temp_max) / 2) * 10)
        rain_score = 100 if rain_suitable else max(0, 100 - abs(annual_rainfall_estimate - (rain_min + rain_max) / 2) / 100)
        
        weather_score = (temp_score * 0.6) + (rain_score * 0.4)
        
        return {
            'weather_score': weather_score,
            'temperature_suitable': temp_suitable,
            'rainfall_suitable': rain_suitable,
            'current_conditions': {
                'temperature': current_temp,
                'average_temperature': avg_temp,
                'recent_rainfall': total_rainfall,
                'estimated_annual_rainfall': annual_rainfall_estimate
            },
            'recommendations': self._generate_weather_recommendations(
                weather_score, temp_suitable, rain_suitable
            )
        }
    
    def get_weather_forecast(
        self, 
        latitude: float, 
        longitude: float, 
        days: int = 14
    ) -> Dict:
        """
        Get weather forecast for planning
        """
        try:
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max',
                'timezone': 'auto',
                'forecast_days': min(days, 16)  # Open-Meteo limit
            }
            
            response = requests.get(self.open_meteo_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._process_forecast_data(data)
            
        except Exception as e:
            print(f"Error fetching weather forecast: {e}")
            return self._get_default_forecast_data()
    
    def _process_weather_data(self, raw_data: Dict) -> Dict:
        """Process raw weather data from API"""
        try:
            current = raw_data.get('current_weather', {})
            hourly = raw_data.get('hourly', {})
            daily = raw_data.get('daily', {})
            
            # Current conditions
            current_temp = current.get('temperature', 20)
            
            # Calculate averages from daily data
            daily_max_temps = daily.get('temperature_2m_max', [])
            daily_min_temps = daily.get('temperature_2m_min', [])
            daily_precipitation = daily.get('precipitation_sum', [])
            
            avg_temp = np.mean(daily_max_temps + daily_min_temps) if daily_max_temps and daily_min_temps else current_temp
            total_rainfall = sum(daily_precipitation) if daily_precipitation else 0
            
            return {
                'current_temperature': current_temp,
                'average_temperature': avg_temp,
                'total_rainfall_7days': total_rainfall,
                'max_temperatures': daily_max_temps,
                'min_temperatures': daily_min_temps,
                'daily_rainfall': daily_precipitation,
                'wind_speed': current.get('windspeed', 0),
                'data_source': 'Open-Meteo',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error processing weather data: {e}")
            return self._get_default_weather_data()
    
    def _process_historical_data(self, raw_data: Dict) -> Dict:
        """Process historical weather data"""
        try:
            daily = raw_data.get('daily', {})
            
            max_temps = daily.get('temperature_2m_max', [])
            min_temps = daily.get('temperature_2m_min', [])
            precipitation = daily.get('precipitation_sum', [])
            
            return {
                'average_temperature': np.mean(max_temps + min_temps) if max_temps and min_temps else 20,
                'temperature_variance': np.std(max_temps + min_temps) if max_temps and min_temps else 2,
                'total_rainfall': sum(precipitation) if precipitation else 0,
                'rainfall_variance': np.std(precipitation) if precipitation else 5,
                'max_temperatures': max_temps,
                'min_temperatures': min_temps,
                'daily_precipitation': precipitation
            }
        except Exception as e:
            print(f"Error processing historical data: {e}")
            return self._get_default_historical_data()
    
    def _process_forecast_data(self, raw_data: Dict) -> Dict:
        """Process forecast data"""
        try:
            daily = raw_data.get('daily', {})
            
            return {
                'forecast_max_temps': daily.get('temperature_2m_max', []),
                'forecast_min_temps': daily.get('temperature_2m_min', []),
                'forecast_precipitation': daily.get('precipitation_sum', []),
                'forecast_dates': daily.get('time', []),
                'favorable_days': self._count_favorable_days(daily)
            }
        except Exception as e:
            print(f"Error processing forecast data: {e}")
            return self._get_default_forecast_data()
    
    def _count_favorable_days(self, daily_data: Dict) -> int:
        """Count favorable days for farming activities"""
        precipitation = daily_data.get('precipitation_sum', [])
        return sum(1 for rain in precipitation if rain < 5)  # Days with <5mm rain
    
    def _generate_weather_recommendations(
        self, 
        weather_score: float, 
        temp_suitable: bool, 
        rain_suitable: bool
    ) -> List[str]:
        """Generate weather-based recommendations"""
        recommendations = []
        
        if weather_score >= 80:
            recommendations.append("Excellent weather conditions for this crop")
        elif weather_score >= 60:
            recommendations.append("Good weather conditions with minor adjustments needed")
        else:
            recommendations.append("Weather conditions may be challenging for this crop")
        
        if not temp_suitable:
            recommendations.append("Consider temperature management techniques")
        
        if not rain_suitable:
            recommendations.append("Plan irrigation or drainage systems accordingly")
        
        return recommendations
    
    def _get_default_weather_data(self) -> Dict:
        """Default weather data when API fails"""
        return {
            'current_temperature': 22,
            'average_temperature': 20,
            'total_rainfall_7days': 10,
            'max_temperatures': [25] * 7,
            'min_temperatures': [15] * 7,
            'daily_rainfall': [1.5] * 7,
            'wind_speed': 5,
            'data_source': 'Default',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_default_historical_data(self) -> Dict:
        """Default historical data when API fails"""
        return {
            'average_temperature': 20,
            'temperature_variance': 3,
            'total_rainfall': 50,
            'rainfall_variance': 5,
            'max_temperatures': [22] * 30,
            'min_temperatures': [18] * 30,
            'daily_precipitation': [1.7] * 30
        }
    
    def _get_default_forecast_data(self) -> Dict:
        """Default forecast data when API fails"""
        return {
            'forecast_max_temps': [24] * 14,
            'forecast_min_temps': [16] * 14,
            'forecast_precipitation': [2] * 14,
            'forecast_dates': [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(14)],
            'favorable_days': 10
        }
