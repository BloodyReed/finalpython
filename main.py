from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
search_history = set()

# Replace value in '' with your actual OpenWeatherMap API key
API_KEY = '5070fda7b16657292aace62a406489c9'
BASE_URL = 'http://api.openweathermap.org/data/2.5/forecast'

def get_weather_and_forecast(city):
    params = {'q': city, 'appid': API_KEY}
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    print(f"API Response for {city}: {data}")  # Print the entire API response

    if response.status_code == 200:
        weather_info = {
            'city': data['city']['name'],
            'temperature': round(data['list'][0]['main']['temp'] - 273.15, 2),
            'description': data['list'][0]['weather'][0]['description'],
            'humidity': data['list'][0]['main']['humidity'],
            'wind_speed': data['list'][0]['wind']['speed'],
            'max_temperature': round(data['list'][0]['main']['temp_max'] - 273.15, 2),
            'min_temperature': round(data['list'][0]['main']['temp_min'] - 273.15, 2),
            'pressure': data['list'][0]['main']['pressure'],
        }

        hourly_forecast = []
        daily_forecast = []

        # Get today's date
        today_date = datetime.utcnow().strftime('%Y-%m-%d')

        for hour_data in data['list']:
            # Filter hourly forecast for today
            if hour_data['dt_txt'].startswith(today_date):
                hour_info = {
                    'date': hour_data['dt_txt'].split()[0],
                    'time': hour_data['dt_txt'].split()[1],
                    'temperature': round(hour_data['main']['temp'] - 273.15, 2),
                    'description': hour_data['weather'][0]['description'],
                }
                hourly_forecast.append(hour_info)

        # Get daily forecast for the next 5 days
        for day_data in data['list']:
            forecast_date = day_data['dt_txt'].split()[0]
            if forecast_date not in [entry['date'] for entry in daily_forecast]:
                daily_info = {
                    'date': forecast_date,
                    'max_temperature': round(day_data['main']['temp_max'] - 273.15, 2),
                    'min_temperature': round(day_data['main']['temp_min'] - 273.15, 2),
                    'description': day_data['weather'][0]['description'],
                    'icon_class': determine_icon_class(day_data['weather'][0]['description']),
                }
                daily_forecast.append(daily_info)

        return weather_info, hourly_forecast, daily_forecast
    else:
        print(f"API Error: {data}")
        return None, None, None
def determine_icon_class(weather_description):
    if 'cloud' in weather_description.lower():
        return 'bi bi-cloud-fog2'
    elif 'sun' in weather_description.lower() or 'clear' in weather_description.lower():
        return 'fas fa-sun'
    elif 'rain' in weather_description.lower():
        return 'fas fa-cloud-showers-heavy'
    elif 'snow' in weather_description.lower():
        return 'fas fa-snowflake'
    else:
        return 'fas fa-question'
@app.route('/', methods=['GET', 'POST'])
def index():
    weather_info = None
    hourly_forecast = []  # Initialize an empty list for hourly forecast
    daily_forecast = []  # Initialize an empty list for daily forecast

    if request.method == 'POST':
        city = request.form['city']
        search_history.add(city)

        weather_info, hourly_forecast, daily_forecast = get_weather_and_forecast(city)

    return render_template('index.html', weather_info=weather_info, search_history=search_history,
                           hourly_forecast=hourly_forecast, daily_forecast=daily_forecast)


if __name__ == '__main__':
    app.run(debug=True)
