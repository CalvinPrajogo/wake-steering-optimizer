"""
weather_forecast.py

Helper script to fetch forecasted weather data from OpenWeatherMap API.
Supports both current forecasts and multi-day forecasts for wind farm optimization.

Usage:
  - Provide coordinates with `--lat LAT --lon LON`.
  - Or pass a CSV with columns `lat,lon` using `--coords-file coords.csv`.
  - Use `--days N` to specify forecast days (default: 5, max: 16 for free tier).

The script fetches hourly forecast data including:
  - Wind speed (m/s)
  - Wind direction (degrees)
  - Temperature (°C)
  - Pressure (hPa)
  - Humidity (%)
  - Cloud coverage (%)

Notes:
  - Requires an OpenWeatherMap API key (free tier available at openweathermap.org)
  - Free tier allows up to 16 days of forecast data
  - Rate limits: 60 calls/minute for free tier
"""
import urllib.request
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define parameters
latitude = 41.119917
longitude = -71.516111
unit_group = 'us'
start_date = "2012-01-01"
end_date = "2012-01-01"
api_key = os.getenv('WEATHER_API_KEY')

# Set up output directory and filename
today_date = datetime.now().strftime('%Y-%m-%d')
output_dir = Path('data/raw')
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / f'forecast_data_{start_date}_{end_date}.json'

# Construct the URL
url = (
    f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
    f"{latitude},{longitude}/{start_date}/{end_date}?"
    f"unitGroup={unit_group}&"
    f"key={api_key}&"
    f"elements=datetime,datetimeEpoch,windspeed,windspeedmax,windspeedmean,windspeedmin,winddir&"
    f"contentType=json"
)

try:
    # Make the request
    response = urllib.request.urlopen(url)
    
    # Parse the response
    if response.status == 200:
        weather_data = json.loads(response.read().decode())
        
        # Save the full weather data to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(weather_data, f, indent=2, ensure_ascii=False)
        
        # Print summary information
        print(f"✓ Successfully fetched weather forecast data")
        print(f"  Location: {weather_data.get('resolvedAddress', f'{latitude}, {longitude}')}")
        print(f"  Forecast date: {start_date}")
        
        if 'days' in weather_data and len(weather_data['days']) > 0:
            day_data = weather_data['days'][0]
            if 'hours' in day_data:
                print(f"  Data type: Hourly forecast ({len(day_data['hours'])} hours)")
            elif 'minutes' in day_data:
                print(f"  Data type: Minute-level forecast ({len(day_data['minutes'])} minutes)")
        
        print(f"✓ Data saved to: {output_file}")
    else:
        print(f"HTTP error occurred: {response.status} - {response.reason}")

except urllib.error.HTTPError as e:
    print(f"HTTP error occurred: {e.code} - {e.reason}")
    # Read error response body for more details
    try:
        error_body = e.read().decode('utf-8')
        print(f"Error details: {error_body}")
    except Exception:
        pass
    
    if e.code == 401:
        print("\n401 UNAUTHORIZED - Possible causes:")
        print("1. Invalid or missing API key")
        print("2. Account/subscription issue")
        print("3. Feature not available on your plan")
except urllib.error.URLError as e:
    print(f"URL error occurred: {e.reason}")
except KeyError as e:
    print(f"KeyError: {e}")
    print("This usually means the API response structure is different than expected.")
except Exception as e:
    print(f"General error occurred: {e}")
    import traceback
    traceback.print_exc()

