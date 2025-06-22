#!/usr/bin/env python3
"""
Quick demo script for the AI Farming Advisor
Run this to test the system with sample data
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main_agent import FarmingAgent
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def print_header():
    """Print welcome header"""
    print("🌾" * 50)
    print("         AI FARMING ADVISOR - DEMO")
    print("🌾" * 50)
    print()

def print_results_summary(recommendations):
    """Print a summary of recommendations"""
    if 'error' in recommendations:
        print(f"❌ Error: {recommendations['error']}")
        return
    
    print("📊 ANALYSIS RESULTS")
    print("=" * 40)
    
    # Summary
    summary = recommendations.get('summary', {})
    location = recommendations.get('location', {})
    
    print(f"📍 Location: {location.get('latitude', 0):.4f}, {location.get('longitude', 0):.4f}")
    print(f"🏞️  Land Area: {location.get('land_area_hectares', 0):.1f} hectares")
    print(f"🏆 Best Crop: {summary.get('best_crop', 'N/A').title()}")
    print(f"💰 Expected Profit: ${summary.get('expected_profit', 0):,.2f}")
    print(f"🎯 Confidence: {summary.get('confidence_score', 0):.1f}%")
    print()
    
    # Top 5 recommendations
    print("🏆 TOP 5 CROP RECOMMENDATIONS:")
    print("-" * 40)
    
    top_recs = recommendations.get('top_recommendations', [])
    for i, crop in enumerate(top_recs[:5], 1):
        profit = crop.get('profit_analysis', {})
        print(f"{i}. {crop['crop_name'].upper()}")
        print(f"   Suitability: {crop['suitability_score']:.1f}%")
        print(f"   Net Profit: ${profit.get('net_profit', 0):,.2f}")
        print(f"   ROI: {profit.get('roi_percentage', 0):.1f}%")
        print()
    
    # Environmental summary
    env_summary = recommendations.get('environmental_summary', {})
    weather = env_summary.get('weather', {})
    soil = env_summary.get('soil', {})
    
    print("🌍 ENVIRONMENTAL CONDITIONS:")
    print("-" * 40)
    print(f"🌡️  Temperature: {weather.get('average_temperature', 0):.1f}°C")
    print(f"🌧️  Recent Rainfall: {weather.get('total_rainfall_7days', 0):.1f}mm")
    print(f"🌱 Soil Type: {soil.get('soil_type', 'Unknown').title()}")
    print(f"🧪 Soil pH: {soil.get('soil_ph', 0):.1f}")
    print(f"⭐ Soil Quality: {soil.get('soil_quality_scores', {}).get('overall_score', 0):.1f}%")
    print()
    
    # Next steps
    next_steps = recommendations.get('next_steps', [])
    if next_steps:
        print("🎯 RECOMMENDED NEXT STEPS:")
        print("-" * 40)
        for i, step in enumerate(next_steps[:5], 1):
            print(f"{i}. {step}")
        print()

async def run_demo():
    """Run the farming agent demo"""
    
    print_header()
    
    print("🔧 Initializing AI Farming Advisor...")
    try:
        agent = FarmingAgent()
        print("✅ Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return
    
    # Demo locations
    demo_locations = [
        {
            'name': 'Iowa, USA (Corn Belt)',
            'latitude': 41.8781,
            'longitude': -93.0977,
            'land_area': 10.0,
            'description': 'Major corn and soybean production region'
        },
        {
            'name': 'Punjab, India',
            'latitude': 31.1471,
            'longitude': 75.3412,
            'land_area': 5.0,
            'description': 'Wheat and rice growing region'
        },
        {
            'name': 'São Paulo, Brazil',
            'latitude': -23.5505,
            'longitude': -46.6333,
            'land_area': 8.0,
            'description': 'Diverse agricultural region'
        }
    ]
    
    print("\n🌍 DEMO LOCATIONS:")
    for i, loc in enumerate(demo_locations, 1):
        print(f"{i}. {loc['name']} - {loc['description']}")
    
    print("\nChoose a location (1-3) or press Enter for all locations:")
    
    try:
        choice = input().strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 3:
            # Analyze single location
            selected_location = demo_locations[int(choice) - 1]
            await analyze_location(agent, selected_location)
        else:
            # Analyze all locations
            print("\n🔍 Analyzing all demo locations...")
            for i, location in enumerate(demo_locations, 1):
                print(f"\n{'='*60}")
                print(f"ANALYZING LOCATION {i}: {location['name'].upper()}")
                print(f"{'='*60}")
                await analyze_location(agent, location)
                
                if i < len(demo_locations):
                    print("\nPress Enter to continue to next location...")
                    input()
    
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Thank you for trying the AI Farming Advisor!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    
    print("\n🌾 Demo completed! Thank you for using the AI Farming Advisor!")
    print("\nTo run the full web interface: streamlit run ui/streamlit_app.py")
    print("To run interactive mode: python main_agent.py --interactive")

async def analyze_location(agent, location):
    """Analyze a specific location"""
    
    print(f"\n📍 Analyzing {location['name']}...")
    print(f"Coordinates: {location['latitude']:.4f}, {location['longitude']:.4f}")
    print(f"Land area: {location['land_area']} hectares")
    print(f"Description: {location['description']}")
    print("\n⏳ This may take a moment...")
    
    try:
        # Get recommendations
        recommendations = await agent.get_comprehensive_recommendations(
            latitude=location['latitude'],
            longitude=location['longitude'],
            land_area=location['land_area']
        )
        
        # Print results
        print_results_summary(recommendations)
        
        # Save results to file
        filename = f"demo_results_{location['name'].replace(' ', '_').replace(',', '')}.json"
        with open(filename, 'w') as f:
            json.dump(recommendations, f, indent=2)
        
        print(f"📄 Detailed results saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

def check_dependencies():
    """Check if required dependencies are available"""
    
    required_modules = [
        'google.adk',
        'requests',
        'numpy',
        'pandas',
        'geopy'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ Missing required dependencies:")
        for module in missing_modules:
            print(f"   - {module}")
        print("\nPlease install them with:")
        print("pip install -r requirements.txt")
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 Checking dependencies...")
    
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ All dependencies available!")
    
    # Run the demo
    asyncio.run(run_demo())
