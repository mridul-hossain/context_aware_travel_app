import requests
from geopy.geocoders import Nominatim

def get_location():
    geolocator = Nominatim(user_agent="travel_app")
    location = geolocator.geocode("Montreal")  # Static for now
    return (location.latitude, location.longitude, location.address)

def get_weather(lat, lon):
    API_KEY = "837192b3a612078fff67ddba758e61ec"
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    data = requests.get(url).json()
    temp = data['main']['temp']
    condition = data['weather'][0]['description']
    return temp, condition

