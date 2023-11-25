import requests

def get_weather(api_key, city):
    base_url = "http://api.weatherstack.com/current"

    params = {
        "access_key": api_key,
        "query": city,
    }

    try:
        # Fetch current weather
        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code == 200:
            localtime = data["location"]["localtime"]
            temperature = data["current"]["temperature"]
            weather_description = data["current"]["weather_descriptions"][0]
            wind_speed = data["current"]["wind_speed"]
            wind_degree = data["current"]["wind_degree"]
            humidity = data["current"]["humidity"]
            

            print(f"Current temperature in {city}: {temperature}°C")
            print(f"Weather: {weather_description}")
            print(f"wind_speed: {wind_speed}")
            print(f"wind_degree: {wind_degree}")
            print(f"humidity: {humidity}")
            print(f"localtime: {localtime}")
        else:
            print(f"Error: {data['error']['info']}")

       
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Replace 'YOUR_API_KEY' with your actual Weatherstack API key
    api_key = "95747142ae542efed63858e9c0c8bb9e"

    # Replace 'CityName' with the name of the city for which you want to get the weather
    city_name = "Avignon"

    get_weather(api_key, city_name)
