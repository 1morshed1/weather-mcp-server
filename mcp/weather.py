from typing import Any
import os
import httpx
import uvicorn
from dotenv import load_dotenv
from fastmcp import FastMCP
from groq import Groq

# Load env variables (for Groq API key)
load_dotenv()

# Create an MCP server with HTTP support
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API request failed: {e}")
            return None


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # Get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data or "properties" not in points_data:
        return "Unable to fetch forecast data for this location."

    forecast_url = points_data["properties"].get("forecast")
    if not forecast_url:
        return "No forecast URL available."

    forecast_data = await make_nws_request(forecast_url)
    if not forecast_data or "properties" not in forecast_data:
        return "Unable to fetch detailed forecast."

    periods = forecast_data["properties"].get("periods", [])
    if not periods:
        return "No forecast periods available."

    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)



# Run the server with HTTP transport
if __name__ == "__main__":
    print("Starting weather MCP server with HTTP transport...")
    print("Available tools:")
    print("- get_alerts: Get weather alerts for US states")
    print("- get_forecast: Get detailed weather forecast for coordinates")
    
    
    print("Server will be available at:")
    print("- HTTP API: http://localhost:8000")
    print("- MCP over HTTP: http://localhost:8000/mcp")
    
    # Run with uvicorn for HTTP transport
    mcp.run(transport="http", host="127.0.0.1", port=8000)