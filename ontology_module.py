from owlready2 import *
import os

# Define path
ONTO_PATH = "assets/travel_ontology.owl"

def load_ontology():
    """Loads the ontology file."""
    if not os.path.exists(ONTO_PATH):
        print("Ontology file not found! Please run create_ontology.py first.")
        return None
    
    onto = get_ontology(ONTO_PATH).load()
    return onto

def get_context_individuals(ontology, condition, hour):
    """Maps real-world data to Ontology Individuals."""
    
    # Map Weather
    condition = condition.lower()
    if "rain" in condition or "drizzle" in condition or "thunder" in condition:
        weather_ind = ontology.search_one(iri="*Rainy")
    elif "snow" in condition:
        weather_ind = ontology.search_one(iri="*Snowy")
    elif "cloud" in condition:
        weather_ind = ontology.search_one(iri="*Cloudy")
    else:
        weather_ind = ontology.search_one(iri="*Sunny")

    # Map Time
    if 5 <= hour < 12:
        time_ind = ontology.search_one(iri="*Morning")
    elif 12 <= hour < 17:
        time_ind = ontology.search_one(iri="*Afternoon")
    elif 17 <= hour < 21:
        time_ind = ontology.search_one(iri="*Evening")
    else:
        time_ind = ontology.search_one(iri="*Night")
        
    return weather_ind, time_ind

def get_smart_recommendation(ontology, weather_desc, current_hour, user_preferences):
    """
    1. Finds places compatible with Weather & Time.
    2. Filters them by User Preferences.
    3. Returns list of keywords for Google API.
    """
    if not ontology:
        return ["restaurant", "park", "museum"] # Fallback

    weather_ind, time_ind = get_context_individuals(ontology, weather_desc, current_hour)
    
    print(f"DEBUG: Context Detected -> {weather_ind.name} + {time_ind.name}")
    print(f"DEBUG: User Prefs -> {user_preferences}")

    valid_places = []

    # 1. REASONING: Find all places compatible with context
    for place in ontology.Place.instances():
        
        # Check Weather Compatibility
        # (If is_good_for_weather is defined, we check it. If empty, assume good for all)
        is_weather_ok = False
        if not place.is_good_for_weather: 
            is_weather_ok = True
        elif weather_ind in place.is_good_for_weather:
            is_weather_ok = True
            
        # Check Time Compatibility
        is_time_ok = False
        if not place.is_good_for_time:
            is_time_ok = True
        elif time_ind in place.is_good_for_time:
            is_time_ok = True

        if is_weather_ok and is_time_ok:
            valid_places.append(place)

    # 2. FILTERING: Match with User Preferences
    # user_preferences is a list like ["Hiking", "Italian", "Museum"]
    
    final_recommendations = []
    
    # Normalize prefs to lowercase for comparison
    user_prefs_lower = [p.lower() for p in user_preferences]

    for place in valid_places:
        # Check if place category matches ANY user preference
        # We look at the 'has_category' data property
        place_cats = [c.lower() for c in place.has_category]
        
        # Intersection check
        if any(pref in place_cats for pref in user_prefs_lower):
            # Get the search keyword for Google API
            if place.has_keyword:
                final_recommendations.append(place.has_keyword[0])
    
    # 3. FALLBACK: If logic is too strict and returns nothing, give generic contextual items
    if not final_recommendations:
        print("DEBUG: No direct preference match found. Returning general contextual suggestions.")
        for place in valid_places:
            if place.has_keyword:
                final_recommendations.append(place.has_keyword[0])

    # Return unique keywords, limited to top 3 to avoid API spam
    return list(set(final_recommendations))[:3]