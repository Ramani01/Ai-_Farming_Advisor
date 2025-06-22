"""
Main Farming Agent using Google Agent Development Kit
Orchestrates specialized agents to provide comprehensive farming recommendations
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import asyncio

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Google ADK components
try:
    from google.adk import Agent, Runner
    from google.adk.tools import FunctionTool, BaseTool
    ADK_AVAILABLE = True
except ImportError as e:
    print(f"Google ADK not fully available: {e}")
    print("Running in standalone mode")
    ADK_AVAILABLE = False
    Agent = None
    Runner = None
    FunctionTool = None
    BaseTool = None

# Import specialized agents
from agents.weather_agent import WeatherAgent
from agents.soil_agent import SoilAgent
from agents.market_agent import MarketAgent
from utils.data_processor import DataProcessor
from config import CROP_DATABASE, WEATHER_API_CONFIG, SOIL_API_CONFIG, MARKET_API_CONFIG, GEOLOCATION_CONFIG

class FarmingAgent:
    """
    Main farming agent that coordinates all specialized agents
    """
    
    def __init__(self):
        self.config = {
            'WEATHER_API_CONFIG': WEATHER_API_CONFIG,
            'SOIL_API_CONFIG': SOIL_API_CONFIG,
            'MARKET_API_CONFIG': MARKET_API_CONFIG,
            'GEOLOCATION_CONFIG': GEOLOCATION_CONFIG
        }
        
        # Initialize specialized agents
        self.weather_agent = WeatherAgent(self.config)
        self.soil_agent = SoilAgent(self.config)
        self.market_agent = MarketAgent(self.config)
        self.data_processor = DataProcessor()
        
        # Initialize Google ADK Agent
        self.adk_agent = None
        self._initialize_adk()
    
    def _initialize_adk(self):
        """Initialize Google Agent Development Kit"""
        if not ADK_AVAILABLE:
            print("Google ADK not available - running in standalone mode")
            return
            
        try:
            # Create tools for the agent
            tools = [
                self._create_crop_recommendation_tool(),
                self._create_weather_analysis_tool(),
                self._create_market_analysis_tool(),
                self._create_profit_calculator_tool()
            ]
            
            # Create the agent with available API
            self.adk_agent = Agent(
                name="farming-advisor",
                description="AI agent that provides crop recommendations and farming advice",
                tools=tools
            )
            
            print("Google ADK Farming Agent initialized successfully!")
            
        except Exception as e:
            print(f"Warning: Could not initialize Google ADK: {e}")
            print("Falling back to standalone mode")
            self.adk_agent = None
    
    def _create_crop_recommendation_tool(self):
        """Create crop recommendation tool for Google ADK"""
        if not ADK_AVAILABLE:
            return None
            
        return FunctionTool(
            name="get_crop_recommendations",
            description="Get crop recommendations based on location and conditions",
            func=self._get_crop_recommendations_tool
        )
    
    def _create_weather_analysis_tool(self):
        """Create weather analysis tool for Google ADK"""
        if not ADK_AVAILABLE:
            return None
            
        return FunctionTool(
            name="analyze_weather",
            description="Analyze weather conditions for farming",
            func=self._analyze_weather_tool
        )
    
    def _create_market_analysis_tool(self):
        """Create market analysis tool for Google ADK"""
        if not ADK_AVAILABLE:
            return None
            
        return FunctionTool(
            name="analyze_market",
            description="Analyze market prices and find best selling opportunities",
            func=self._analyze_market_tool
        )
    
    def _create_profit_calculator_tool(self):
        """Create profit calculator tool for Google ADK"""
        if not ADK_AVAILABLE:
            return None
            
        return FunctionTool(
            name="calculate_profit",
            description="Calculate profit potential for specific crops",
            func=self._calculate_profit_tool
        )
    
    async def _get_crop_recommendations_tool(self, latitude: float, longitude: float, land_area: float = 1.0) -> str:
        """Tool function for crop recommendations"""
        try:
            recommendations = await self.get_comprehensive_recommendations(latitude, longitude, land_area)
            return json.dumps(recommendations, indent=2)
        except Exception as e:
            return f"Error getting recommendations: {str(e)}"
    
    async def _analyze_weather_tool(self, latitude: float, longitude: float) -> str:
        """Tool function for weather analysis"""
        try:
            weather_data = self.weather_agent.get_current_weather(latitude, longitude)
            return json.dumps(weather_data, indent=2)
        except Exception as e:
            return f"Error analyzing weather: {str(e)}"
    
    async def _analyze_market_tool(self, crop: str, land_area: float = 1.0) -> str:
        """Tool function for market analysis"""
        try:
            market_data = self.market_agent.calculate_profit_analysis(crop, land_area)
            return json.dumps(market_data, indent=2)
        except Exception as e:
            return f"Error analyzing market: {str(e)}"
    
    async def _calculate_profit_tool(self, crops: List[str], land_area: float = 1.0) -> str:
        """Tool function for profit calculation"""
        try:
            profit_analyses = []
            for crop in crops:
                analysis = self.market_agent.calculate_profit_analysis(crop, land_area)
                profit_analyses.append(analysis)
            return json.dumps(profit_analyses, indent=2)
        except Exception as e:
            return f"Error calculating profits: {str(e)}"
    
    async def get_comprehensive_recommendations(
        self, 
        latitude: float, 
        longitude: float, 
        land_area: float = 1.0,
        target_crops: Optional[List[str]] = None
    ) -> Dict:
        """
        Get comprehensive farming recommendations for a location
        """
        try:
            print(f"Analyzing farming conditions for location: {latitude}, {longitude}")
            
            # Get environmental data
            print("Collecting weather data...")
            weather_data = self.weather_agent.get_current_weather(latitude, longitude)
            
            print("Collecting soil data...")
            soil_data = self.soil_agent.get_soil_data(latitude, longitude)
            
            print("Collecting market data...")
            market_data = self.market_agent.get_current_prices()
            
            # Determine crops to analyze
            crops_to_analyze = target_crops or list(CROP_DATABASE.keys())
            
            print(f"Analyzing {len(crops_to_analyze)} crops...")
            
            # Analyze each crop
            crop_analyses = []
            for crop_name in crops_to_analyze:
                print(f"  Analyzing {crop_name}...")
                
                crop_requirements = CROP_DATABASE[crop_name]
                
                # Environmental conditions for analysis
                environmental_conditions = {
                    'temperature': weather_data.get('average_temperature', 20),
                    'rainfall': weather_data.get('total_rainfall_7days', 0) * 52,  # Estimate annual
                    'soil_ph': soil_data.get('soil_ph', 6.5),
                    'soil_type': soil_data.get('soil_type', 'loam')
                }
                
                # Calculate suitability score
                suitability_score = self.data_processor.calculate_crop_suitability_score(
                    crop_requirements, environmental_conditions
                )
                
                # Calculate profit potential
                profit_analysis = self.market_agent.calculate_profit_analysis(
                    crop_name, land_area
                )
                
                # Weather suitability analysis
                weather_suitability = self.weather_agent.analyze_weather_suitability(
                    weather_data, crop_requirements
                )
                
                # Soil compatibility analysis
                soil_compatibility = self.soil_agent.analyze_soil_crop_compatibility(
                    soil_data, crop_requirements
                )
                
                # Risk assessment
                risk_assessment = self.data_processor.calculate_risk_assessment(
                    crop_name, environmental_conditions
                )
                
                crop_analysis = {
                    'crop_name': crop_name,
                    'suitability_score': suitability_score,
                    'profit_analysis': profit_analysis.get('financial_analysis', {}),
                    'weather_suitability': weather_suitability,
                    'soil_compatibility': soil_compatibility,
                    'risk_assessment': risk_assessment,
                    'planting_months': crop_requirements['planting_months'],
                    'growing_season_days': crop_requirements['growing_season_days']
                }
                
                crop_analyses.append(crop_analysis)
            
            # Rank crops by combined score
            print("Ranking crops by profitability and suitability...")
            ranked_crops = self.data_processor.rank_crops_by_profitability(crop_analyses)
            
            # Generate recommendations
            recommendations = self.data_processor.format_recommendations(ranked_crops)
            
            # Add additional information
            recommendations.update({
                'location': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'land_area_hectares': land_area
                },
                'environmental_summary': {
                    'weather': weather_data,
                    'soil': soil_data,
                    'market_conditions': market_data.get('market_status', 'unknown')
                },
                'planting_calendar': self.data_processor.generate_planting_calendar(ranked_crops[:5]),
                'next_steps': self._generate_next_steps(ranked_crops[:3])
            })
            
            print("Analysis complete!")
            return recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'message': 'Unable to generate recommendations. Please try again.'
            }
    
    async def get_weather_forecast_analysis(self, latitude: float, longitude: float) -> Dict:
        """Get detailed weather forecast analysis"""
        try:
            current_weather = self.weather_agent.get_current_weather(latitude, longitude)
            forecast = self.weather_agent.get_weather_forecast(latitude, longitude)
            historical = self.weather_agent.get_historical_weather(latitude, longitude)
            
            return {
                'current_weather': current_weather,
                'forecast': forecast,
                'historical_trends': historical,
                'farming_advice': self._generate_weather_farming_advice(current_weather, forecast)
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def find_best_markets_for_crop(
        self, 
        crop: str, 
        latitude: float, 
        longitude: float
    ) -> Dict:
        """Find best markets for selling a specific crop"""
        try:
            farmer_location = {'latitude': latitude, 'longitude': longitude}
            markets = self.market_agent.find_best_markets(crop, farmer_location)
            price_forecast = self.market_agent.get_seasonal_price_forecast(crop)
            
            return {
                'markets': markets,
                'price_forecast': price_forecast,
                'selling_strategy': self._generate_selling_strategy(markets, price_forecast)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_next_steps(self, top_crops: List[Dict]) -> List[str]:
        """Generate actionable next steps for farmers"""
        if not top_crops:
            return ["No suitable crops found for current conditions"]
        
        best_crop = top_crops[0]
        crop_name = best_crop['crop_name']
        
        next_steps = [
            f"Consider planting {crop_name} as your primary crop",
            f"Prepare land according to {crop_name} soil requirements",
            "Test soil pH and nutrients to confirm suitability",
            "Check local suppliers for quality seeds",
            "Plan irrigation system if needed",
            "Research local markets and establish buyer connections"
        ]
        
        # Add seasonal advice
        current_month = datetime.now().month
        planting_months = best_crop.get('planting_months', [])
        
        if current_month in planting_months:
            next_steps.insert(1, "Current month is optimal for planting - act quickly!")
        else:
            next_month = min(planting_months, key=lambda x: (x - current_month) % 12)
            next_steps.insert(1, f"Plan to plant in month {next_month} for optimal timing")
        
        return next_steps
    
    def _generate_weather_farming_advice(
        self, 
        current_weather: Dict, 
        forecast: Dict
    ) -> List[str]:
        """Generate weather-based farming advice"""
        advice = []
        
        favorable_days = forecast.get('favorable_days', 0)
        if favorable_days >= 10:
            advice.append("Good weather window for field activities")
        else:
            advice.append("Limited good weather days - plan activities carefully")
        
        avg_temp = current_weather.get('average_temperature', 20)
        if avg_temp > 30:
            advice.append("High temperatures - ensure adequate irrigation")
        elif avg_temp < 10:
            advice.append("Cold conditions - consider crop protection measures")
        
        return advice
    
    def _generate_selling_strategy(
        self, 
        markets: Dict, 
        price_forecast: Dict
    ) -> List[str]:
        """Generate selling strategy recommendations"""
        strategy = []
        
        best_markets = markets.get('best_markets', [])
        if best_markets:
            best_market = best_markets[0]
            strategy.append(f"Primary target: {best_market['name']}")
            strategy.append(f"Expected net price: ${best_market['net_price']}/ton")
        
        forecast_data = price_forecast.get('price_forecast', [])
        if forecast_data:
            best_months = price_forecast.get('best_selling_months', [])
            if best_months:
                strategy.append(f"Best selling months: {', '.join(best_months)}")
        
        strategy.append("Consider forward contracts for price security")
        
        return strategy
    
    async def run_interactive_session(self):
        """Run interactive session with the farmer"""
        print("🌾 Welcome to the AI Farming Advisor! 🌾")
        print("I'll help you make the best crop decisions for your farm.\n")
        
        try:
            # Get location
            print("First, I need to know your farm location:")
            latitude = float(input("Enter latitude (e.g., 40.7128): "))
            longitude = float(input("Enter longitude (e.g., -74.0060): "))
            
            # Get land area
            land_area = float(input("Enter your land area in hectares (default 1.0): ") or "1.0")
            
            print(f"\nAnalyzing conditions for your {land_area} hectare farm...")
            print("This may take a moment...\n")
            
            # Get recommendations
            recommendations = await self.get_comprehensive_recommendations(
                latitude, longitude, land_area
            )
            
            if 'error' in recommendations:
                print(f"❌ Error: {recommendations['error']}")
                return
            
            # Display results
            self._display_recommendations(recommendations)
            
            # Interactive follow-ups
            await self._interactive_followup(latitude, longitude, recommendations)
            
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
        except KeyboardInterrupt:
            print("\n👋 Thank you for using the AI Farming Advisor!")
        except Exception as e:
            print(f"❌ An error occurred: {e}")
    
    def _display_recommendations(self, recommendations: Dict):
        """Display recommendations in a user-friendly format"""
        print("🎯 CROP RECOMMENDATIONS")
        print("=" * 50)
        
        summary = recommendations.get('summary', {})
        print(f"Best recommended crop: {summary.get('best_crop', 'N/A')}")
        print(f"Expected profit: ${summary.get('expected_profit', 0):.2f}")
        print(f"Confidence score: {summary.get('confidence_score', 0):.1f}%\n")
        
        top_recs = recommendations.get('top_recommendations', [])
        print("TOP 5 CROP RECOMMENDATIONS:")
        print("-" * 30)
        
        for i, crop in enumerate(top_recs[:5], 1):
            print(f"{i}. {crop['crop_name'].upper()}")
            print(f"   Suitability: {crop['suitability_score']:.1f}%")
            profit = crop.get('profit_analysis', {})
            print(f"   Net profit: ${profit.get('net_profit', 0):.2f}")
            print(f"   ROI: {profit.get('roi_percentage', 0):.1f}%")
            print()
    
    async def _interactive_followup(
        self, 
        latitude: float, 
        longitude: float, 
        recommendations: Dict
    ):
        """Handle interactive follow-up questions"""
        while True:
            print("\n🔍 What would you like to know more about?")
            print("1. Weather forecast analysis")
            print("2. Market opportunities for a specific crop")
            print("3. Detailed soil recommendations")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                print("\n🌤️  WEATHER ANALYSIS")
                print("=" * 30)
                weather_analysis = await self.get_weather_forecast_analysis(latitude, longitude)
                if 'error' not in weather_analysis:
                    forecast = weather_analysis.get('forecast', {})
                    print(f"Favorable days ahead: {forecast.get('favorable_days', 0)}")
                    advice = weather_analysis.get('farming_advice', [])
                    for tip in advice:
                        print(f"• {tip}")
                
            elif choice == '2':
                crop = input("Enter crop name: ").strip().lower()
                print(f"\n💰 MARKET ANALYSIS FOR {crop.upper()}")
                print("=" * 30)
                market_analysis = await self.find_best_markets_for_crop(crop, latitude, longitude)
                if 'error' not in market_analysis:
                    strategy = market_analysis.get('selling_strategy', [])
                    for tip in strategy:
                        print(f"• {tip}")
                
            elif choice == '3':
                print("\n🌱 SOIL RECOMMENDATIONS")
                print("=" * 30)
                env_summary = recommendations.get('environmental_summary', {})
                soil_data = env_summary.get('soil', {})
                soil_recs = soil_data.get('soil_recommendations', [])
                for rec in soil_recs:
                    print(f"• {rec}")
                
            elif choice == '4':
                print("\n👋 Thank you for using the AI Farming Advisor!")
                print("Wishing you a successful farming season! 🌾")
                break
            
            else:
                print("Invalid choice. Please try again.")

# Main execution function
async def main():
    """Main function to run the farming agent"""
    agent = FarmingAgent()
    
    # Check if running in interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        await agent.run_interactive_session()
    else:
        # Demo mode with sample data
        print("🌾 Farming Agent Demo")
        print("=" * 30)
        
        # Sample coordinates (Iowa, USA - major farming region)
        latitude = 41.8781
        longitude = -93.0977
        land_area = 10.0  # 10 hectares
        
        print(f"Analyzing farm conditions for Iowa location...")
        print(f"Location: {latitude}, {longitude}")
        print(f"Land area: {land_area} hectares\n")
        
        recommendations = await agent.get_comprehensive_recommendations(
            latitude, longitude, land_area
        )
        
        if 'error' not in recommendations:
            agent._display_recommendations(recommendations)
            
            # Save results to file
            output_file = 'farming_recommendations.json'
            with open(output_file, 'w') as f:
                json.dump(recommendations, f, indent=2)
            print(f"\n📄 Full recommendations saved to: {output_file}")
        else:
            print(f"❌ Error: {recommendations['error']}")

if __name__ == "__main__":
    # Run the agent
    asyncio.run(main())
