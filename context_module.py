import requests
from geopy.geocoders import Nominatim

def get_location():
    try:
        # 1. Set a specific user_agent (helps avoid blocking)
        geolocator = Nominatim(user_agent="my_travel_companion_app_v1")
        
        # 2. Add 'timeout=10' (wait up to 10 seconds instead of 1)
        location = geolocator.geocode("Montreal", timeout=10) 
        
        if location:
            return (location.latitude, location.longitude, location.address)
        else:
            # Fallback if geocode returns None
            return (45.5017, -73.5673, "Montreal, QC, Canada (Fallback)")
            
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"Geocoding service failed: {e}")
        # 3. Return a default hardcoded location so the app doesn't crash
        return (45.5017, -73.5673, "Montreal, QC, Canada (Offline)")

def get_weather(lat, lon):
    API_KEY = "837192b3a612078fff67ddba758e61ec"
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
        response = requests.get(url, timeout=5) # Good practice to timeout here too
        data = response.json()
        
        if response.status_code == 200:
            temp = data['main']['temp']
            condition = data['weather'][0]['description']
            return temp, condition
        else:
            return 20, "Clear Sky (API Error)"
            
    except Exception as e:
        print(f"Weather API failed: {e}")
        return 20, "Clear Sky (Offline)"

def get_google_places(lat, lon, place_type="restaurant"):
    """
    Fetches places from Google Places API.
    place_type examples: 'restaurant', 'tourist_attraction', 'museum'
    """
    GOOGLE_API_KEY = "AIzaSyA66E6be5wsR3bz5dyliIXHNoZx4DP1W3c" 
    
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    params = {
        "location": f"{lat},{lon}",
        "radius": 2000,  # Search within 2km
        "type": place_type,
        "key": GOOGLE_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        results = response.json().get("results", [])
        
        places_data = []
        for place in results[:10]:  # Limit to 10 items to save API quota
            name = place.get("name")
            rating = place.get("rating", "N/A")
            
            # Get Photo URL if available
            photo_url = "https://upload.wikimedia.org/wikipedia/commons/1/14/No_Image_Available.jpg" # Default
            if "photos" in place:
                photo_ref = place["photos"][0]["photo_reference"]
                photo_url = (
                    f"https://maps.googleapis.com/maps/api/place/photo"
                    f"?maxwidth=400&photo_reference={photo_ref}&key={GOOGLE_API_KEY}"
                )
            
            places_data.append({
                "name": name,
                "rating": str(rating),
                "image": photo_url
            })
            
        return places_data
    except Exception as e:
        print(f"Error fetching places: {e}")
        return []

