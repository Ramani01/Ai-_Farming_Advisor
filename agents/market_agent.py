"""
Market Agent for collecting and analyzing crop prices and market data
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np

class MarketAgent:
    """Specialized agent for market data collection and price analysis"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.commodities_url = config['MARKET_API_CONFIG']['commodities_api_url']
        
        # Base prices for common crops (USD per ton) - simplified for demo
        self.base_prices = {
            'wheat': 250,
            'corn': 200,
            'rice': 400,
            'soybeans': 450,
            'cotton': 1600,  # per ton of cotton
            'tomatoes': 800,
            'potatoes': 300,
            'carrots': 350
        }
        
        # Production costs (USD per hectare) - simplified estimates
        self.production_costs = {
            'wheat': 400,
            'corn': 500,
            'rice': 800,
            'soybeans': 450,
            'cotton': 1200,
            'tomatoes': 2000,
            'potatoes': 1500,
            'carrots': 1200
        }
        
        # Typical yields (tons per hectare)
        self.typical_yields = {
            'wheat': 3.0,
            'corn': 9.0,
            'rice': 4.5,
            'soybeans': 2.8,
            'cotton': 1.5,
            'tomatoes': 50.0,
            'potatoes': 25.0,
            'carrots': 30.0
        }
    
    def get_current_prices(self, crops: List[str] = None) -> Dict:
        """
        Get current market prices for specified crops
        """
        try:
            if crops is None:
                crops = list(self.base_prices.keys())
            
            prices = {}
            
            for crop in crops:
                # In a real implementation, you would fetch from actual commodity APIs
                base_price = self.base_prices.get(crop, 0)
                
                # Add some market volatility (±10%)
                volatility = np.random.normal(1.0, 0.1)
                current_price = base_price * volatility
                
                prices[crop] = {
                    'current_price': round(current_price, 2),
                    'base_price': base_price,
                    'price_change_percent': round((volatility - 1) * 100, 2),
                    'currency': 'USD',
                    'unit': 'per_ton',
                    'last_updated': datetime.now().isoformat()
                }
            
            return {
                'prices': prices,
                'market_status': self._assess_market_status(),
                'data_source': 'Simulated Market Data',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error fetching market prices: {e}")
            return self._get_default_prices()
    
    def get_price_history(self, crop: str, days: int = 30) -> Dict:
        """
        Get historical price data for trend analysis
        """
        try:
            base_price = self.base_prices.get(crop, 0)
            if base_price == 0:
                return {'error': f'No price data available for {crop}'}
            
            # Generate simulated historical data
            dates = []
            prices = []
            
            for i in range(days):
                date = datetime.now() - timedelta(days=days-i)
                dates.append(date.strftime('%Y-%m-%d'))
                
                # Add trend and volatility
                trend_factor = 1 + (i / days) * 0.1  # Slight upward trend
                volatility = np.random.normal(1.0, 0.05)
                price = base_price * trend_factor * volatility
                prices.append(round(price, 2))
            
            # Calculate statistics
            avg_price = np.mean(prices)
            price_volatility = np.std(prices)
            trend = 'increasing' if prices[-1] > prices[0] else 'decreasing'
            
            return {
                'crop': crop,
                'dates': dates,
                'prices': prices,
                'statistics': {
                    'average_price': round(avg_price, 2),
                    'volatility': round(price_volatility, 2),
                    'trend': trend,
                    'min_price': min(prices),
                    'max_price': max(prices)
                }
            }
            
        except Exception as e:
            print(f"Error getting price history: {e}")
            return {'error': str(e)}
    
    def calculate_profit_analysis(
        self, 
        crop: str, 
        land_area: float = 1.0,
        custom_yield: Optional[float] = None
    ) -> Dict:
        """
        Calculate detailed profit analysis for a crop
        """
        try:
            # Get current price
            current_prices = self.get_current_prices([crop])
            crop_price = current_prices['prices'].get(crop, {}).get('current_price', 0)
            
            # Get costs and yields
            production_cost = self.production_costs.get(crop, 0)
            expected_yield = custom_yield or self.typical_yields.get(crop, 0)
            
            if crop_price == 0 or production_cost == 0 or expected_yield == 0:
                return {'error': f'Insufficient data for {crop} profit analysis'}
            
            # Calculate financials
            total_yield = expected_yield * land_area
            gross_revenue = total_yield * crop_price
            total_costs = production_cost * land_area
            net_profit = gross_revenue - total_costs
            
            # Calculate metrics
            profit_margin = (net_profit / gross_revenue * 100) if gross_revenue > 0 else 0
            roi = (net_profit / total_costs * 100) if total_costs > 0 else 0
            breakeven_price = total_costs / total_yield if total_yield > 0 else 0
            
            # Risk assessment
            risk_level = self._assess_price_risk(crop)
            
            return {
                'crop': crop,
                'land_area_hectares': land_area,
                'financial_analysis': {
                    'gross_revenue': round(gross_revenue, 2),
                    'total_costs': round(total_costs, 2),
                    'net_profit': round(net_profit, 2),
                    'profit_margin': round(profit_margin, 2),
                    'roi_percentage': round(roi, 2),
                    'profit_per_hectare': round(net_profit / land_area, 2)
                },
                'production_details': {
                    'expected_yield_tons': round(total_yield, 2),
                    'yield_per_hectare': expected_yield,
                    'current_price_per_ton': crop_price,
                    'production_cost_per_hectare': production_cost,
                    'breakeven_price': round(breakeven_price, 2)
                },
                'risk_assessment': risk_level,
                'recommendations': self._generate_profit_recommendations(
                    net_profit, roi, risk_level
                )
            }
            
        except Exception as e:
            print(f"Error calculating profit analysis: {e}")
            return {'error': str(e)}
    
    def find_best_markets(
        self, 
        crop: str, 
        farmer_location: Dict,
        max_distance: float = 100  # km
    ) -> Dict:
        """
        Find best markets and buyers for a crop
        """
        try:
            # Simulated market locations with different prices
            markets = [
                {
                    'name': 'Local Farmers Market',
                    'type': 'farmers_market',
                    'distance_km': 15,
                    'price_premium': 1.2,  # 20% premium
                    'contact': 'info@localmarket.com',
                    'requirements': 'Organic certification preferred'
                },
                {
                    'name': 'Regional Wholesale Market',
                    'type': 'wholesale',
                    'distance_km': 45,
                    'price_premium': 1.1,  # 10% premium
                    'contact': 'buyers@regionalwholesale.com',
                    'requirements': 'Minimum 5 tons'
                },
                {
                    'name': 'Processing Plant',
                    'type': 'processor',
                    'distance_km': 80,
                    'price_premium': 0.95,  # 5% discount
                    'contact': 'procurement@processor.com',
                    'requirements': 'Contract required, bulk quantities'
                },
                {
                    'name': 'Export Terminal',
                    'type': 'export',
                    'distance_km': 120,
                    'price_premium': 1.15,  # 15% premium
                    'contact': 'export@terminal.com',
                    'requirements': 'International quality standards'
                }
            ]
            
            # Filter by distance and calculate potential prices
            base_price = self.base_prices.get(crop, 0)
            available_markets = []
            
            for market in markets:
                if market['distance_km'] <= max_distance:
                    potential_price = base_price * market['price_premium']
                    transport_cost = market['distance_km'] * 0.5  # $0.5 per km
                    net_price = potential_price - transport_cost
                    
                    market_info = market.copy()
                    market_info.update({
                        'potential_price': round(potential_price, 2),
                        'transport_cost': round(transport_cost, 2),
                        'net_price': round(net_price, 2),
                        'profit_potential': 'high' if net_price > base_price * 1.05 else 'medium'
                    })
                    available_markets.append(market_info)
            
            # Sort by net price
            available_markets.sort(key=lambda x: x['net_price'], reverse=True)
            
            return {
                'crop': crop,
                'markets_found': len(available_markets),
                'best_markets': available_markets[:3],  # Top 3
                'all_markets': available_markets,
                'recommendations': self._generate_market_recommendations(available_markets)
            }
            
        except Exception as e:
            print(f"Error finding markets: {e}")
            return {'error': str(e)}
    
    def get_seasonal_price_forecast(self, crop: str, months_ahead: int = 6) -> Dict:
        """
        Forecast seasonal price trends
        """
        try:
            base_price = self.base_prices.get(crop, 0)
            if base_price == 0:
                return {'error': f'No price data for {crop}'}
            
            seasonal_patterns = {
                'wheat': [1.1, 1.05, 1.0, 0.95, 0.9, 0.95],  # Higher in early months
                'corn': [0.95, 1.0, 1.05, 1.1, 1.05, 1.0],   # Peak mid-year
                'rice': [1.0, 1.0, 1.05, 1.1, 1.05, 1.0],
                'tomatoes': [1.2, 1.1, 1.0, 0.9, 1.0, 1.1],  # Seasonal variation
                'potatoes': [1.0, 1.05, 1.1, 1.05, 1.0, 0.95]
            }
            
            pattern = seasonal_patterns.get(crop, [1.0] * 6)[:months_ahead]
            
            forecast = []
            for i, multiplier in enumerate(pattern):
                month_date = datetime.now() + timedelta(days=30*i)
                forecasted_price = base_price * multiplier * np.random.normal(1.0, 0.05)
                
                forecast.append({
                    'month': month_date.strftime('%Y-%m'),
                    'month_name': month_date.strftime('%B %Y'),
                    'forecasted_price': round(forecasted_price, 2),
                    'price_trend': 'up' if multiplier > 1.0 else 'down' if multiplier < 1.0 else 'stable'
                })
            
            return {
                'crop': crop,
                'forecast_months': months_ahead,
                'price_forecast': forecast,
                'best_selling_months': self._identify_best_selling_months(forecast)
            }
            
        except Exception as e:
            print(f"Error generating price forecast: {e}")
            return {'error': str(e)}
    
    def _assess_market_status(self) -> str:
        """Assess overall market conditions"""
        conditions = ['stable', 'volatile', 'bullish', 'bearish']
        return np.random.choice(conditions)
    
    def _assess_price_risk(self, crop: str) -> Dict:
        """Assess price risk for a crop"""
        # Simplified risk assessment
        risk_factors = {
            'wheat': 'medium',
            'corn': 'medium',
            'rice': 'low',
            'soybeans': 'high',
            'cotton': 'high',
            'tomatoes': 'high',
            'potatoes': 'medium',
            'carrots': 'medium'
        }
        
        risk_level = risk_factors.get(crop, 'medium')
        
        return {
            'risk_level': risk_level,
            'volatility': 'high' if risk_level == 'high' else 'moderate',
            'market_stability': 'unstable' if risk_level == 'high' else 'stable'
        }
    
    def _generate_profit_recommendations(
        self, 
        net_profit: float, 
        roi: float, 
        risk_assessment: Dict
    ) -> List[str]:
        """Generate profit-based recommendations"""
        recommendations = []
        
        if net_profit > 0:
            if roi > 20:
                recommendations.append("Excellent profit potential - consider this crop")
            elif roi > 10:
                recommendations.append("Good profit potential with acceptable returns")
            else:
                recommendations.append("Modest profits expected")
        else:
            recommendations.append("Consider alternative crops for better profitability")
        
        risk_level = risk_assessment.get('risk_level', 'medium')
        if risk_level == 'high':
            recommendations.append("Consider price hedging or forward contracts")
        
        return recommendations
    
    def _generate_market_recommendations(self, markets: List[Dict]) -> List[str]:
        """Generate market-based recommendations"""
        recommendations = []
        
        if not markets:
            recommendations.append("No suitable markets found within distance limit")
            return recommendations
        
        best_market = markets[0]
        recommendations.append(f"Best option: {best_market['name']} with net price ${best_market['net_price']}")
        
        if len(markets) > 1:
            recommendations.append("Consider multiple markets to spread risk")
        
        return recommendations
    
    def _identify_best_selling_months(self, forecast: List[Dict]) -> List[str]:
        """Identify best months to sell based on price forecast"""
        sorted_forecast = sorted(forecast, key=lambda x: x['forecasted_price'], reverse=True)
        return [month['month_name'] for month in sorted_forecast[:2]]
    
    def _get_default_prices(self) -> Dict:
        """Default price data when APIs fail"""
        default_prices = {}
        for crop, price in self.base_prices.items():
            default_prices[crop] = {
                'current_price': price,
                'base_price': price,
                'price_change_percent': 0,
                'currency': 'USD',
                'unit': 'per_ton',
                'last_updated': datetime.now().isoformat()
            }
        
        return {
            'prices': default_prices,
            'market_status': 'stable',
            'data_source': 'Default Data',
            'timestamp': datetime.now().isoformat()
        }
