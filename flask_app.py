from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderInsufficientPrivileges, GeocoderUnavailable
from timezonefinder import TimezoneFinder
from datetime import datetime
import requests
import pytz
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def weather():
    city = request.form.get('city', '').strip() 

    if not city:
        error_message = "Please enter a city name."
        return render_template('index.html', error=error_message)

    try:
        geolocator = Nominatim(user_agent="flask_weather_app_sanjeev")
        location = geolocator.geocode(city)

        if not location:
            error_message = "Invalid city name. Please enter a valid city."
            return render_template('index.html', error=error_message)

        obj = TimezoneFinder()
        result = obj.timezone_at(lng=location.longitude, lat=location.latitude)

        home = pytz.timezone(result)
        local_time = datetime.now(home)
        current_time = local_time.strftime("%I:%M %p")

        api_key = "54c364373b2349f70f30533832b3713f" 
        api_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        response = requests.get(api_url)
        json_data = response.json()

        if json_data.get("cod") != 200:
            error_message = json_data.get("message", "Error fetching weather data. Please try again.")
            return render_template('index.html', error=error_message)

        condition = json_data['weather'][0]['main']
        description = json_data['weather'][0]['description']
        temp = int(json_data['main']['temp'] - 273.15) 
        pressure = json_data['main']['pressure']
        humidity = json_data['main']['humidity']
        wind = json_data['wind']['speed']

        weather_data = {
            'city': city,
            'current_time': current_time,
            'temp': temp,
            'condition': condition,
            'feels_like': temp,
            'wind': wind,
            'humidity': humidity,
            'description': description,
            'pressure': pressure
        }

        app.logger.debug(f"Weather data: {weather_data}")

        return render_template('weather.html', weather_data=weather_data)

    except GeocoderUnavailable:
        error_message = "Geocoder service is currently unavailable. Please try again later."
        app.logger.error(f"GeocoderUnavailable error for city: {city}")
        return render_template('index.html', error=error_message)
    except GeocoderInsufficientPrivileges:
        error_message = "Access denied to geocoding service. Please check your usage or try later."
        app.logger.error(f"GeocoderInsufficientPrivileges error for city: {city}")
        return render_template('index.html', error=error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        app.logger.error(f"Error: {e}")
        return render_template('index.html', error=error_message)

if __name__ == '__main__':
    app.run(debug=True, port=5001)