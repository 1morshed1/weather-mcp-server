import asyncio
import os
import streamlit as st
import asyncio
from fastmcp import Client, FastMCP
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq client
groq_client = Groq(api_key=groq_api_key)

# Streamlit UI Configuration
st.set_page_config(
    page_title="US Weather Assistant", 
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ US Weather Assistant with GPT OSS 120B")
st.markdown("Get weather alerts and forecasts for US locations using AI!")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    server_url = st.text_input("MCP Server URL", "http://localhost:8000/mcp")
    
    st.header("Weather Query Options")
    query_type = st.radio(
        "Select query type:",
        ["US State Alerts", "US Coordinates Forecast", "Chat with AI"]
    )
    
    if query_type == "US State Alerts":
        state = st.text_input("US State Code", "CA", help="Two-letter state code (e.g., CA, NY, TX)")
    elif query_type == "US Coordinates Forecast":
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude", value=40.7128, format="%.4f", help="US coordinates only")
        with col2:
            longitude = st.number_input("Longitude", value=-74.0060, format="%.4f", help="US coordinates only")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    if query_type == "Chat with AI":
        st.header("🤖 Chat with GPT OSS 120B about Weather")
        user_prompt = st.text_area(
            "Ask me anything about US weather!", 
            "What are the current weather alerts for California? Also get me the forecast for New York City coordinates.",
            height=100
        )
        
        if st.button("Ask GPT OSS 120B 🚀", type="primary"):
            with st.spinner("Getting weather data and generating response..."):
                async def get_weather_and_chat():
                    try:
                        # First, let's try to get weather data based on the user's question
                        weather_data = ""
                        
                        # Simple keyword detection for weather requests
                        prompt_lower = user_prompt.lower()
                        
                        # Check if user is asking about specific states for alerts
                        state_keywords = {
                            'california': 'CA', 'ca': 'CA',
                            'new york': 'NY', 'ny': 'NY', 
                            'texas': 'TX', 'tx': 'TX',
                            'florida': 'FL', 'fl': 'FL',
                            'illinois': 'IL', 'il': 'IL',
                            'pennsylvania': 'PA', 'pa': 'PA',
                            'ohio': 'OH', 'oh': 'OH',
                            'georgia': 'GA', 'ga': 'GA',
                            'north carolina': 'NC', 'nc': 'NC',
                            'michigan': 'MI', 'mi': 'MI'
                        }
                        
                        # Location coordinates for major cities
                        city_coords = {
                            'new york city': (40.7128, -74.0060),
                            'nyc': (40.7128, -74.0060),
                            'los angeles': (34.0522, -118.2437),
                            'la': (34.0522, -118.2437),
                            'chicago': (41.8781, -87.6298),
                            'houston': (29.7604, -95.3698),
                            'phoenix': (33.4484, -112.0740),
                            'philadelphia': (39.9526, -75.1652),
                            'san antonio': (29.4241, -98.4936),
                            'san diego': (32.7157, -117.1611),
                            'dallas': (32.7767, -96.7970),
                            'san jose': (37.3382, -121.8863),
                            'austin': (30.2672, -97.7431),
                            'miami': (25.7617, -80.1918)
                        }
                        
                        # Try to connect to MCP and get weather data
                        try:
                            async with Client(server_url) as client:
                                # Look for state alerts
                                if 'alert' in prompt_lower or 'warning' in prompt_lower:
                                    for location, state_code in state_keywords.items():
                                        if location in prompt_lower:
                                            try:
                                                result = await client.call_tool("get_alerts", {"state": state_code})
                                                content = None
                                                if hasattr(result, 'data'):
                                                    content = result.data
                                                elif hasattr(result, 'content') and result.content:
                                                    if isinstance(result.content, list) and len(result.content) > 0:
                                                        content = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
                                                
                                                if content:
                                                    weather_data += f"\n\n=== Weather Alerts for {location.title()} ({state_code}) ===\n{content}\n"
                                                break
                                            except Exception as e:
                                                weather_data += f"\n\nCould not fetch alerts for {location.title()}: {str(e)}\n"
                                
                                # Look for forecast requests
                                if 'forecast' in prompt_lower or 'weather' in prompt_lower:
                                    for city, (lat, lon) in city_coords.items():
                                        if city in prompt_lower:
                                            try:
                                                result = await client.call_tool("get_forecast", {"latitude": lat, "longitude": lon})
                                                content = None
                                                if hasattr(result, 'data'):
                                                    content = result.data
                                                elif hasattr(result, 'content') and result.content:
                                                    if isinstance(result.content, list) and len(result.content) > 0:
                                                        content = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
                                                
                                                if content:
                                                    weather_data += f"\n\n=== Weather Forecast for {city.title()} ===\n{content}\n"
                                                break
                                            except Exception as e:
                                                weather_data += f"\n\nCould not fetch forecast for {city.title()}: {str(e)}\n"
                        
                        except Exception as e:
                            weather_data = f"\n\nNote: Could not connect to weather service: {str(e)}\n"
                        
                        # Enhanced system prompt for weather assistant
                        system_prompt = f"""You are a helpful weather assistant for US weather data. You can provide information about weather alerts and forecasts.

Here is current weather data that was retrieved:{weather_data}

Based on this weather data and the user's question, provide a helpful response. If weather data was retrieved, use it to give specific, accurate information. If no specific weather data was retrieved, provide general guidance about weather and mention that you can get alerts for US states (using 2-letter codes) and forecasts for major US cities.

Always provide practical advice based on weather conditions (e.g., umbrella for rain, layers for cold weather, emergency preparations for severe weather, etc.).

Available capabilities:
- Weather alerts for US states (CA, NY, TX, FL, etc.)  
- Weather forecasts for major US cities
- General weather advice and safety tips

Note: This service only covers the United States through the National Weather Service API."""

                        # Get response from GPT OSS 120B WITHOUT tool calling
                        response = groq_client.chat.completions.create(
                            model="openai/gpt-oss-120b",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt},
                            ],
                            temperature=0.7,
                            max_tokens=1024
                        )
                        
                        return response.choices[0].message.content
                
                    except Exception as e:
                        return f"Error with AI response: {str(e)}"
                
                response_text = asyncio.run(get_weather_and_chat())
                st.write("###  GPT OSS 120B Response")
                st.info(response_text)
    
    else:
        st.header("🇺🇸 US Weather Tools")
        
        # Tool selection based on query type
        if query_type == "US State Alerts":
            tool_choice = "get_alerts"
            st.info(f"Getting weather alerts for state: {state}")
        elif query_type == "US Coordinates Forecast":
            tool_choice = "get_forecast"
            st.info(f"Getting forecast for coordinates: {latitude}, {longitude}")

with col2:
    st.header("Quick Actions")
    
    if query_type != "Chat with AI":
        if st.button(" Get Weather Data", type="primary"):
            async def fetch_weather_data():
                try:
                    # Connect to HTTP MCP server
                    async with Client(server_url) as client:
                        
                        # Call the appropriate tool with proper argument format
                        if tool_choice == "get_alerts":
                            # Try different argument formats based on FastMCP expectations
                            try:
                                # Method 1: Dictionary format
                                result = await client.call_tool("get_alerts", {"state": state.upper()})
                            except Exception as e1:
                                try:
                                    # Method 2: Named parameters in dict
                                    result = await client.call_tool("get_alerts", arguments={"state": state.upper()})
                                except Exception as e2:
                                    # Method 3: Direct parameter passing
                                    result = await client.call_tool("get_alerts", state.upper())
                                    
                        elif tool_choice == "get_forecast":
                            # Try different argument formats based on FastMCP expectations  
                            try:
                                # Method 1: Dictionary format
                                result = await client.call_tool("get_forecast", {
                                    "latitude": latitude, 
                                    "longitude": longitude
                                })
                            except Exception as e1:
                                try:
                                    # Method 2: Named parameters in dict
                                    result = await client.call_tool("get_forecast", arguments={
                                        "latitude": latitude, 
                                        "longitude": longitude
                                    })
                                except Exception as e2:
                                    # Method 3: Direct parameter passing
                                    result = await client.call_tool("get_forecast", latitude, longitude)
                        
                        st.write(f"### {tool_choice.replace('_', ' ').title()} Results")
                        
                        # Handle CallToolResult object from FastMCP
                        content = None
                        
                        if hasattr(result, 'data'):
                            # FastMCP CallToolResult has a 'data' attribute
                            content = result.data
                        elif hasattr(result, 'content') and result.content:
                            # Check if content is a list with TextContent objects
                            if isinstance(result.content, list) and len(result.content) > 0:
                                first_content = result.content[0]
                                if hasattr(first_content, 'text'):
                                    content = first_content.text
                                else:
                                    content = str(first_content)
                            else:
                                content = str(result.content)
                        elif hasattr(result, 'structured_content') and result.structured_content:
                            # Check structured_content for 'result' key
                            if isinstance(result.structured_content, dict) and 'result' in result.structured_content:
                                content = result.structured_content['result']
                            else:
                                content = str(result.structured_content)
                        elif isinstance(result, dict):
                            # Fallback to dictionary handling
                            if 'data' in result:
                                content = result['data']
                            elif 'content' in result:
                                content = result['content']
                            elif 'result' in result:
                                content = result['result']
                            else:
                                content = str(result)
                        elif isinstance(result, str):
                            content = result
                        else:
                            content = str(result)
                        
                        # Format the content properly
                        if content and content.strip():
                            # Split by the separator used in your server (---) 
                            sections = content.split('\n---\n')
                            
                            if len(sections) > 1:
                                # Multiple alerts or forecast periods
                                for i, section in enumerate(sections):
                                    if tool_choice == "get_alerts":
                                        st.error(f"🚨 Alert {i+1}")  # Red for alerts
                                    else:  # get_forecast
                                        st.info(f"📅 Forecast Period {i+1}")  # Blue for forecasts
                                    
                                    # Format the section content nicely
                                    formatted_section = section.strip()
                                    if formatted_section:
                                        # Use markdown for better formatting
                                        lines = formatted_section.split('\n')
                                        formatted_lines = []
                                        for line in lines:
                                            line = line.strip()
                                            if line.startswith('Event:'):
                                                formatted_lines.append(f"** {line}**")
                                            elif line.startswith('Area:'):
                                                formatted_lines.append(f"** {line}**")
                                            elif line.startswith('Severity:'):
                                                formatted_lines.append(f"** {line}**")
                                            elif line.startswith('Temperature:'):
                                                formatted_lines.append(f"** {line}**")
                                            elif line.startswith('Wind:'):
                                                formatted_lines.append(f"** {line}**")
                                            elif line.startswith('Forecast:'):
                                                formatted_lines.append(f"** {line}**")
                                            elif line.startswith('Description:'):
                                                formatted_lines.append(f"** Description:**")
                                            elif line.startswith('Instructions:'):
                                                formatted_lines.append(f"** Instructions:**")
                                            elif line.startswith('* WHAT'):
                                                formatted_lines.append(f"**What:** {line[7:]}")
                                            elif line.startswith('* WHERE'):
                                                formatted_lines.append(f"**Where:** {line[8:]}")
                                            elif line.startswith('* WHEN'):
                                                formatted_lines.append(f"**When:** {line[7:]}")
                                            elif line.startswith('* IMPACTS'):
                                                formatted_lines.append(f"**Impacts:** {line[10:]}")
                                            elif line:
                                                formatted_lines.append(line)
                                        
                                        st.markdown('\n'.join(formatted_lines))
                                    
                                    if i < len(sections) - 1:  # Add separator except for last item
                                        st.markdown("---")
                            else:
                                # Single result or no separator
                                if "No active alerts" in content or "Unable to fetch" in content:
                                    st.success(content)  # Green for "no alerts" messages
                                elif tool_choice == "get_alerts":
                                    st.error("🚨 Weather Alert")
                                    # Format single alert
                                    lines = content.strip().split('\n')
                                    formatted_lines = []
                                    for line in lines:
                                        line = line.strip()
                                        if line.startswith('Event:'):
                                            formatted_lines.append(f"** {line}**")
                                        elif line.startswith('Area:'):
                                            formatted_lines.append(f"** {line}**")
                                        elif line.startswith('Severity:'):
                                            formatted_lines.append(f"** {line}**")
                                        elif line.startswith('Description:'):
                                            formatted_lines.append(f"** Description:**")
                                        elif line.startswith('Instructions:'):
                                            formatted_lines.append(f"** Instructions:**")
                                        elif line.startswith('* WHAT'):
                                            formatted_lines.append(f"**What:** {line[7:]}")
                                        elif line.startswith('* WHERE'):
                                            formatted_lines.append(f"**Where:** {line[8:]}")
                                        elif line.startswith('* WHEN'):
                                            formatted_lines.append(f"**When:** {line[7:]}")
                                        elif line.startswith('* IMPACTS'):
                                            formatted_lines.append(f"**Impacts:** {line[10:]}")
                                        elif line:
                                            formatted_lines.append(line)
                                    
                                    st.markdown('\n'.join(formatted_lines))
                                else:
                                    st.info(" Weather Forecast")
                                    # Format single forecast
                                    lines = content.strip().split('\n')
                                    formatted_lines = []
                                    for line in lines:
                                        line = line.strip()
                                        if line.startswith('Temperature:'):
                                            formatted_lines.append(f"** {line}**")
                                        elif line.startswith('Wind:'):
                                            formatted_lines.append(f"** {line}**")
                                        elif line.startswith('Forecast:'):
                                            formatted_lines.append(f"** {line}**")
                                        elif line.endswith(':') and not line.startswith(' '):
                                            formatted_lines.append(f"** {line}**")
                                        elif line:
                                            formatted_lines.append(line)
                                    
                                    st.markdown('\n'.join(formatted_lines))
                        else:
                            st.warning("No data returned from the weather service.")
                            # Show debug info
                            st.write("**Debug - Raw result:**")
                            st.json(result.__dict__ if hasattr(result, '__dict__') else str(result))
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Make sure the MCP server is running: `python weather.py`")
                    
                    # Additional debugging information
                    st.markdown("### Troubleshooting:")
                    st.markdown("""
                    1. **Check MCP Server**: Ensure `python weather.py` is running
                    2. **Check URL**: Verify the MCP server URL is correct
                    3. **Check Arguments**: Ensure the tool arguments match server expectations
                    4. **Check Logs**: Look at the MCP server console for error messages
                    """)
            
            asyncio.run(fetch_weather_data())
    
    # Debug and testing section
    st.header("🔧 Debug & Testing")
    
    if st.button("🔍 Test MCP Connection"):
        async def test_connection():
            try:
                async with Client(server_url) as client:
                    # Test basic connection
                    st.success(" Successfully connected to MCP server")
                    
                    # List available tools
                    try:
                        tools = await client.list_tools()
                        st.write("### Available Tools:")
                        for tool in tools:
                            st.write(f"**{tool.get('name', 'Unknown')}**: {tool.get('description', 'No description')}")
                            if 'inputSchema' in tool:
                                st.json(tool['inputSchema'])
                    except Exception as e:
                        st.warning(f"Could not list tools: {e}")
                    
                    # Test a simple call
                    try:
                        st.write("### Testing get_alerts with CA...")
                        result = await client.call_tool("get_alerts", {"state": "CA"})
                        st.success("Tool call successful!")
                        st.write("**Result type:**", type(result).__name__)
                        
                        # Show the CallToolResult structure
                        st.write("**CallToolResult attributes:**")
                        if hasattr(result, '__dict__'):
                            attrs = {k: str(v)[:200] + "..." if len(str(v)) > 200 else str(v) 
                                   for k, v in result.__dict__.items()}
                            st.json(attrs)
                        
                        # Extract the actual content
                        content = None
                        if hasattr(result, 'data'):
                            content = result.data
                            st.write("**Using result.data:**")
                        elif hasattr(result, 'content') and result.content:
                            if isinstance(result.content, list) and len(result.content) > 0:
                                content = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
                            else:
                                content = str(result.content)
                            st.write("**Using result.content:**")
                        elif hasattr(result, 'structured_content') and result.structured_content:
                            if isinstance(result.structured_content, dict) and 'result' in result.structured_content:
                                content = result.structured_content['result']
                            else:
                                content = str(result.structured_content)
                            st.write("**Using result.structured_content:**")
                        
                        if content:
                            st.code(content[:500] + "..." if len(content) > 500 else content, language='text')
                        else:
                            st.error("Could not extract content from result")
                            
                    except Exception as e:
                        st.error(f"Tool call failed: {e}")
                        st.write("**Trying alternative formats...**")
                        
                        # Try alternative formats
                        try:
                            result = await client.call_tool("get_alerts", arguments={"state": "CA"})
                            st.success(" Alternative format worked!")
                            content = result.data if hasattr(result, 'data') else str(result)
                            st.code(content[:500] + "..." if len(str(content)) > 500 else str(content), language='text')
                        except Exception as e2:
                            try:
                                result = await client.call_tool("get_alerts", "CA")
                                st.success(" Direct parameter format worked!")
                                content = result.data if hasattr(result, 'data') else str(result)
                                st.code(content[:500] + "..." if len(str(content)) > 500 else str(content), language='text')
                            except Exception as e3:
                                st.error(f"All formats failed: {e3}")
                        
            except Exception as e:
                st.error(f"Connection failed: {e}")
        
        asyncio.run(test_connection())
    st.header(" Weather Tips")
    st.info(" Check alerts before traveling")
    st.info(" Layer clothing for temperature changes")
    st.info(" Stay safe during severe weather")
    st.info(" Be cautious of winter conditions")

# Add tools demonstration section
st.header("🛠️ Available Weather Tools")

tool_col1, tool_col2 = st.columns(2)

with tool_col1:
    st.subheader(" Weather Alerts")
    st.markdown("""
    **get_alerts(state)**
    - Get active weather alerts for US states
    - Input: 2-letter state code (CA, NY, TX, etc.)
    - Returns: Current weather warnings and advisories
    
    **Examples:**
    - CA: California alerts
    - FL: Florida alerts  
    - TX: Texas alerts
    """)

with tool_col2:
    st.subheader(" Weather Forecast")
    st.markdown("""
    **get_forecast(latitude, longitude)**
    - Get detailed 5-day weather forecast
    - Input: US coordinates (lat, lon)
    - Returns: Temperature, wind, detailed conditions
    
    **Examples:**
    - 40.7128, -74.0060 (New York City)
    - 34.0522, -118.2437 (Los Angeles)
    - 41.8781, -87.6298 (Chicago)
    """)

# Footer with examples
st.markdown("---")
st.header(" Example Prompts for AI Chat")

example_col1, example_col2 = st.columns(2)

with example_col1:
    st.markdown("""
    **Weather Alerts Examples:**
    - "What weather alerts are active in California?"
    - "Are there any severe weather warnings in Florida?"
    - "Check alerts for Texas and tell me what to expect"
    - "Is there a tornado watch in Oklahoma?"
    """)

with example_col2:
    st.markdown("""
    **Forecast Examples:**
    - "What's the 5-day forecast for New York City?"
    - "Will it rain in Los Angeles this week?"
    - "Should I pack warm clothes for Chicago?"
    - "What's the weather going to be like in Miami?"
    """)

# Status indicators
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if groq_api_key:
        st.success(" Groq API Connected")
    else:
        st.error(" Groq API Key Missing")

with col2:
    st.info(" MCP Server: http://localhost:8000/mcp")

with col3:
    st.info(" Model: GPT OSS 120B")
