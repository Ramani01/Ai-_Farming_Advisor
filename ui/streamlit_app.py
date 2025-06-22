"""
Streamlit Web Interface for the Farming Agent
User-friendly interface for farmers to get crop recommendations
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import asyncio
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_agent import FarmingAgent

# Page configuration
st.set_page_config(
    page_title="🌾 AI Farming Advisor",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #4CAF50, #45a049);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
        margin: 0.5rem 0;
    }
    .crop-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #4CAF50;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = FarmingAgent()

if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌾 AI Farming Advisor</h1>
        <p>Get personalized crop recommendations based on your location, soil, and market conditions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("📍 Farm Information")
        
        # Location input
        st.subheader("Location")
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input(
                "Latitude", 
                min_value=-90.0, 
                max_value=90.0, 
                value=41.8781,
                format="%.6f",
                help="Enter the latitude of your farm"
            )
        with col2:
            longitude = st.number_input(
                "Longitude", 
                min_value=-180.0, 
                max_value=180.0, 
                value=-93.0977,
                format="%.6f",
                help="Enter the longitude of your farm"
            )
        
        # Land area
        land_area = st.number_input(
            "Land Area (hectares)", 
            min_value=0.1, 
            max_value=10000.0, 
            value=1.0,
            step=0.1,
            help="Size of your farmland in hectares"
        )
        
        # Analysis options
        st.subheader("Analysis Options")
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Comprehensive Analysis", "Quick Assessment", "Specific Crops Only"]
        )
        
        if analysis_type == "Specific Crops Only":
            available_crops = ['wheat', 'corn', 'rice', 'soybeans', 'cotton', 'tomatoes', 'potatoes', 'carrots']
            selected_crops = st.multiselect(
                "Select Crops to Analyze",
                available_crops,
                default=['wheat', 'corn', 'soybeans']
            )
        else:
            selected_crops = None
        
        # Action button
        if st.button("🔍 Analyze Farm Conditions", type="primary"):
            with st.spinner("Analyzing your farm conditions... This may take a moment."):
                try:
                    # Run the analysis
                    recommendations = asyncio.run(
                        st.session_state.agent.get_comprehensive_recommendations(
                            latitude, longitude, land_area, selected_crops
                        )
                    )
                    st.session_state.recommendations = recommendations
                    st.success("Analysis complete! Check the results below.")
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
    
    # Main content area
    if st.session_state.recommendations is None:
        # Welcome screen
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            ## Welcome to AI Farming Advisor! 👋
            
            Get data-driven recommendations for your farm:
            
            🌤️ **Weather Analysis** - Real-time weather and climate data  
            🌱 **Soil Assessment** - Soil type and quality analysis  
            💰 **Market Intelligence** - Current prices and profit potential  
            📊 **Crop Recommendations** - Personalized suggestions for your location  
            📅 **Planting Calendar** - Optimal timing for each crop  
            
            ### How to Use:
            1. Enter your farm coordinates in the sidebar
            2. Specify your land area
            3. Choose analysis type
            4. Click "Analyze Farm Conditions"
            
            ### Sample Locations to Try:
            - **Iowa, USA**: 41.8781, -93.0977 (Major corn/soybean region)
            - **Punjab, India**: 31.1471, 75.3412 (Wheat/rice region)
            - **São Paulo, Brazil**: -23.5505, -46.6333 (Diverse agriculture)
            
            Start by entering your farm location in the sidebar! 👈
            """)
    
    else:
        # Display results
        display_results(st.session_state.recommendations)

def display_results(recommendations):
    """Display the analysis results"""
    
    if 'error' in recommendations:
        st.error(f"Analysis Error: {recommendations['error']}")
        return
    
    # Summary metrics
    st.header("📊 Analysis Summary")
    
    summary = recommendations.get('summary', {})
    location = recommendations.get('location', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Best Crop",
            summary.get('best_crop', 'N/A').title(),
            help="Highest scoring crop for your conditions"
        )
    
    with col2:
        expected_profit = summary.get('expected_profit', 0)
        st.metric(
            "Expected Profit",
            f"${expected_profit:,.2f}",
            help="Estimated net profit for best crop"
        )
    
    with col3:
        confidence = summary.get('confidence_score', 0)
        st.metric(
            "Confidence Score",
            f"{confidence:.1f}%",
            help="Confidence in recommendation based on data quality"
        )
    
    with col4:
        land_area = location.get('land_area_hectares', 0)
        st.metric(
            "Land Area",
            f"{land_area:.1f} ha",
            help="Farm area analyzed"
        )
    
    # Top Recommendations
    st.header("🏆 Top Crop Recommendations")
    
    top_recs = recommendations.get('top_recommendations', [])
    
    if top_recs:
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📋 Detailed List", "📊 Comparison Chart", "💰 Profit Analysis"])
        
        with tab1:
            display_detailed_recommendations(top_recs)
        
        with tab2:
            display_comparison_chart(top_recs)
        
        with tab3:
            display_profit_analysis(top_recs)
    
    # Environmental Conditions
    st.header("🌍 Environmental Conditions")
    display_environmental_summary(recommendations.get('environmental_summary', {}))
    
    # Planting Calendar
    st.header("📅 Planting Calendar")
    display_planting_calendar(recommendations.get('planting_calendar', {}))
    
    # Next Steps
    st.header("🎯 Recommended Next Steps")
    next_steps = recommendations.get('next_steps', [])
    for i, step in enumerate(next_steps, 1):
        st.markdown(f"**{i}.** {step}")
    
    # Download option
    st.header("💾 Download Results")
    col1, col2 = st.columns(2)
    
    with col1:
        # JSON download
        json_data = json.dumps(recommendations, indent=2)
        st.download_button(
            label="📄 Download as JSON",
            data=json_data,
            file_name=f"farming_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        # CSV download for top recommendations
        if top_recs:
            df = create_recommendations_dataframe(top_recs)
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📊 Download as CSV",
                data=csv_data,
                file_name=f"crop_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

def display_detailed_recommendations(top_recs):
    """Display detailed crop recommendations"""
    
    for i, crop in enumerate(top_recs, 1):
        with st.container():
            st.markdown(f"""
            <div class="crop-card">
                <h3>#{i} {crop['crop_name'].title()}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Suitability Score", f"{crop['suitability_score']:.1f}%")
            
            with col2:
                profit = crop.get('profit_analysis', {})
                net_profit = profit.get('net_profit', 0)
                st.metric("Net Profit", f"${net_profit:,.2f}")
            
            with col3:
                roi = profit.get('roi_percentage', 0)
                st.metric("ROI", f"{roi:.1f}%")
            
            with col4:
                combined_score = crop.get('combined_score', 0)
                st.metric("Overall Score", f"{combined_score:.1f}%")
            
            # Additional details
            with st.expander(f"Details for {crop['crop_name'].title()}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Financial Analysis")
                    profit_data = crop.get('profit_analysis', {})
                    for key, value in profit_data.items():
                        if isinstance(value, (int, float)):
                            st.write(f"**{key.replace('_', ' ').title()}:** ${value:,.2f}")
                        else:
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                
                with col2:
                    st.subheader("Risk Assessment")
                    risk_data = crop.get('risk_assessment', {})
                    risk_levels = risk_data.get('risk_levels', {})
                    for risk_type, level in risk_levels.items():
                        color = "🟢" if level == "low" else "🟡" if level == "medium" else "🔴"
                        st.write(f"{color} **{risk_type.replace('_', ' ').title()}:** {level.title()}")

def display_comparison_chart(top_recs):
    """Display comparison chart of top crops"""
    
    # Prepare data for chart
    crops = [crop['crop_name'].title() for crop in top_recs]
    suitability_scores = [crop['suitability_score'] for crop in top_recs]
    combined_scores = [crop.get('combined_score', 0) for crop in top_recs]
    profits = [crop.get('profit_analysis', {}).get('net_profit', 0) for crop in top_recs]
    
    # Create subplot
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Suitability Scores', 'Combined Scores', 'Net Profit', 'ROI Comparison'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Suitability scores
    fig.add_trace(
        go.Bar(x=crops, y=suitability_scores, name="Suitability", marker_color='lightgreen'),
        row=1, col=1
    )
    
    # Combined scores
    fig.add_trace(
        go.Bar(x=crops, y=combined_scores, name="Combined Score", marker_color='lightblue'),
        row=1, col=2
    )
    
    # Net profit
    fig.add_trace(
        go.Bar(x=crops, y=profits, name="Net Profit", marker_color='gold'),
        row=2, col=1
    )
    
    # ROI comparison
    roi_values = [crop.get('profit_analysis', {}).get('roi_percentage', 0) for crop in top_recs]
    fig.add_trace(
        go.Bar(x=crops, y=roi_values, name="ROI %", marker_color='salmon'),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False, title_text="Crop Comparison Dashboard")
    st.plotly_chart(fig, use_container_width=True)

def display_profit_analysis(top_recs):
    """Display detailed profit analysis"""
    
    # Create profit comparison dataframe
    profit_data = []
    for crop in top_recs:
        profit_analysis = crop.get('profit_analysis', {})
        profit_data.append({
            'Crop': crop['crop_name'].title(),
            'Gross Revenue': profit_analysis.get('gross_revenue', 0),
            'Total Costs': profit_analysis.get('total_costs', 0),
            'Net Profit': profit_analysis.get('net_profit', 0),
            'Profit Margin (%)': profit_analysis.get('profit_margin', 0),
            'ROI (%)': profit_analysis.get('roi_percentage', 0)
        })
    
    df = pd.DataFrame(profit_data)
    
    # Display table
    st.dataframe(df, use_container_width=True)
    
    # Profit vs Cost scatter plot
    fig = px.scatter(
        df, 
        x='Total Costs', 
        y='Net Profit',
        size='Gross Revenue',
        color='ROI (%)',
        hover_name='Crop',
        title="Profit vs Cost Analysis",
        labels={'Total Costs': 'Total Costs ($)', 'Net Profit': 'Net Profit ($)'}
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def display_environmental_summary(env_summary):
    """Display environmental conditions summary"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌤️ Weather Conditions")
        weather = env_summary.get('weather', {})
        
        if weather:
            st.metric("Current Temperature", f"{weather.get('current_temperature', 0):.1f}°C")
            st.metric("Average Temperature", f"{weather.get('average_temperature', 0):.1f}°C")
            st.metric("7-Day Rainfall", f"{weather.get('total_rainfall_7days', 0):.1f} mm")
            st.metric("Wind Speed", f"{weather.get('wind_speed', 0):.1f} km/h")
    
    with col2:
        st.subheader("🌱 Soil Conditions")
        soil = env_summary.get('soil', {})
        
        if soil:
            st.metric("Soil Type", soil.get('soil_type', 'Unknown').title())
            st.metric("Soil pH", f"{soil.get('soil_ph', 0):.1f}")
            st.metric("Organic Matter", f"{soil.get('organic_matter', 0):.1f}%")
            st.metric("Drainage", soil.get('drainage', 'Unknown').title())
            
            # Soil quality score
            quality_scores = soil.get('soil_quality_scores', {})
            overall_score = quality_scores.get('overall_score', 0)
            st.metric("Soil Quality Score", f"{overall_score:.1f}%")

def display_planting_calendar(planting_calendar):
    """Display planting calendar"""
    
    if not planting_calendar:
        st.info("No planting calendar data available.")
        return
    
    calendar_data = []
    for month_key, month_data in planting_calendar.items():
        month_name = month_data.get('month_name', month_key)
        crops = month_data.get('recommended_crops', [])
        
        for crop in crops:
            calendar_data.append({
                'Month': month_name,
                'Crop': crop.get('name', '').title(),
                'Suitability Score': crop.get('suitability_score', 0),
                'Expected Profit': crop.get('expected_profit', 0)
            })
    
    if calendar_data:
        df = pd.DataFrame(calendar_data)
        
        # Create calendar heatmap
        pivot_df = df.pivot_table(
            index='Crop', 
            columns='Month', 
            values='Suitability Score', 
            fill_value=0
        )
        
        fig = px.imshow(
            pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            color_continuous_scale='Greens',
            title="Planting Calendar - Suitability Scores by Month"
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display table
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No specific planting recommendations for the analyzed timeframe.")

def create_recommendations_dataframe(top_recs):
    """Create a DataFrame from recommendations for CSV export"""
    
    data = []
    for crop in top_recs:
        profit_analysis = crop.get('profit_analysis', {})
        data.append({
            'Rank': crop.get('rank', 0),
            'Crop Name': crop['crop_name'].title(),
            'Suitability Score (%)': crop['suitability_score'],
            'Combined Score (%)': crop.get('combined_score', 0),
            'Net Profit ($)': profit_analysis.get('net_profit', 0),
            'ROI (%)': profit_analysis.get('roi_percentage', 0),
            'Profit Margin (%)': profit_analysis.get('profit_margin', 0),
            'Gross Revenue ($)': profit_analysis.get('gross_revenue', 0),
            'Total Costs ($)': profit_analysis.get('total_costs', 0)
        })
    
    return pd.DataFrame(data)

# Additional features in sidebar
with st.sidebar:
    st.markdown("---")
    st.subheader("🔧 Tools")
    
    if st.button("🔄 Reset Analysis"):
        st.session_state.recommendations = None
        st.rerun()
    
    if st.button("ℹ️ About"):
        st.info("""
        **AI Farming Advisor v1.0**
        
        This tool analyzes:
        - Weather patterns
        - Soil conditions  
        - Market prices
        - Crop suitability
        
        Built with Google Agent Development Kit and powered by real-time data sources.
        """)

if __name__ == "__main__":
    main()
