"""
Configuration file for the Farming Agent
Contains API keys, endpoints, and settings
"""

# API Configuration
WEATHER_API_CONFIG = {
    'open_meteo_url': 'https://api.open-meteo.com/v1/forecast',
    'weatherapi_url': 'https://api.weatherapi.com/v1',
    'weatherapi_key': 'YOUR_WEATHERAPI_KEY'  # Free tier available
}

SOIL_API_CONFIG = {
    'usda_soil_url': 'https://sdmdataaccess.sc.egov.usda.gov/tabular/post.rest',
    'ambee_url': 'https://api.ambeedata.com/soil/latest',
    'ambee_key': 'YOUR_AMBEE_KEY'
}

MARKET_API_CONFIG = {
    'usda_market_url': 'https://www.marketnews.usda.gov/mnp/fv-report',
    'commodities_api_url': 'https://api.commodities-api.com/v1',
    'commodities_key': 'YOUR_COMMODITIES_KEY'
}

GEOLOCATION_CONFIG = {
    'google_geolocation_url': 'https://www.googleapis.com/geolocation/v1/geolocate',
    'google_key': 'YOUR_GOOGLE_KEY',
    'ipapi_url': 'http://ip-api.com/json'
}

# Crop Database - Common crops with their requirements
CROP_DATABASE = {
    'wheat': {
        'optimal_temp_range': (15, 25),  # Celsius
        'rainfall_requirement': (450, 650),  # mm annually
        'soil_ph_range': (6.0, 7.5),
        'growing_season_days': 120,
        'soil_types': ['loam', 'clay loam', 'sandy loam'],
        'planting_months': [3, 4, 10, 11]  # March-April, Oct-Nov
    },
    'corn': {
        'optimal_temp_range': (20, 30),
        'rainfall_requirement': (500, 800),
        'soil_ph_range': (6.0, 6.8),
        'growing_season_days': 90,
        'soil_types': ['loam', 'sandy loam', 'silt loam'],
        'planting_months': [4, 5, 6]
    },
    'rice': {
        'optimal_temp_range': (20, 35),
        'rainfall_requirement': (1000, 2000),
        'soil_ph_range': (5.5, 7.0),
        'growing_season_days': 105,
        'soil_types': ['clay', 'clay loam'],
        'planting_months': [6, 7, 8]
    },
    'soybeans': {
        'optimal_temp_range': (20, 30),
        'rainfall_requirement': (450, 700),
        'soil_ph_range': (6.0, 7.0),
        'growing_season_days': 100,
        'soil_types': ['loam', 'sandy loam', 'silt loam'],
        'planting_months': [4, 5, 6]
    },
    'cotton': {
        'optimal_temp_range': (23, 32),
        'rainfall_requirement': (500, 1000),
        'soil_ph_range': (5.8, 8.0),
        'growing_season_days': 160,
        'soil_types': ['sandy loam', 'clay loam'],
        'planting_months': [4, 5, 6]
    },
    'tomatoes': {
        'optimal_temp_range': (18, 26),
        'rainfall_requirement': (400, 600),
        'soil_ph_range': (6.0, 6.8),
        'growing_season_days': 75,
        'soil_types': ['loam', 'sandy loam'],
        'planting_months': [3, 4, 5]
    },
    'potatoes': {
        'optimal_temp_range': (15, 20),
        'rainfall_requirement': (400, 600),
        'soil_ph_range': (5.0, 6.0),
        'growing_season_days': 90,
        'soil_types': ['sandy loam', 'loam'],
        'planting_months': [3, 4, 8, 9]
    },
    'carrots': {
        'optimal_temp_range': (16, 20),
        'rainfall_requirement': (350, 500),
        'soil_ph_range': (6.0, 7.0),
        'growing_season_days': 70,
        'soil_types': ['sandy loam', 'loam'],
        'planting_months': [3, 4, 7, 8]
    }
}

# Regional price multipliers (example for different regions)
REGIONAL_PRICE_FACTORS = {
    'north': 1.1,  # 10% higher prices
    'south': 0.95,  # 5% lower prices
    'east': 1.05,   # 5% higher prices
    'west': 1.0,    # Base prices
    'midwest': 0.9  # 10% lower prices
}

# Default settings
DEFAULT_SETTINGS = {
    'temperature_unit': 'celsius',
    'distance_unit': 'km',
    'currency': 'USD',
    'language': 'en'
}
