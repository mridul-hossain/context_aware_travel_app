from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDRectangleFlatButton, MDRaisedButton
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.clock import mainthread
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivy.properties import BooleanProperty 
from kivy.graphics import Color, Rectangle

# Import your modules
from context_module import get_location, get_weather, get_google_places
from ontology_module import load_ontology, suggest_activity
from auth_module import google_login_flow
import sqlite3
from pathlib import Path
import threading
from datetime import datetime

DB_PATH = Path(__file__).parent / "database" / "travel_companion.db"
SELECTED_ATTRACTIONS = []
SELECTED_ACTIVITIES = []
SELECTED_CUISINES = []

class run_query():
    def update_preference(attraction_preference, activity_preference, cuisine_preference, email):
        conn = sqlite3.connect(DB_PATH.as_posix())
        c = conn.cursor()

        # Check if user exists
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        exists = c.fetchone()

        if not exists:
            print("No user found")
        else:
            # Update info
            c.execute("UPDATE users SET attraction_preference=?, activity_preference=?, cuisine_preference=? WHERE email=?", 
                    (attraction_preference, activity_preference, cuisine_preference, email))

        conn.commit()
        conn.close()

class LoginScreen(MDScreen):
    def do_login(self):
        self.ids.status_label.text = "Waiting for browser login..."
        self.ids.google_button.disabled = True
        # Run in a thread so UI doesn't freeze while browser is open
        threading.Thread(target=self._run_login_thread).start()

    def _run_login_thread(self):
        user_info = google_login_flow()
        if user_info:
            # Switch to dashboard on main thread logic
            app = MDApp.get_running_app()
            app.current_user_email = user_info['email']
            app.current_user_name = user_info['name']
            
            # Trigger screen switch
            self.on_login_success(user_info)
        else:
            self.ids.status_label.text = "Login Failed. Try again."

    def get_icon_map(self, condition):
        condition = condition.lower()
        # Format: (Icon Name, Color Tuple RGBA)
        if "clear" in condition:
            return "weather-sunny", (1, 0.8, 0.3, 1) # Yellow/Orange
        elif "few clouds" in condition:
            return "weather-partly-cloudy", (1, 0.8, 0.3, 1)
        elif "scattered clouds" in condition or "broken clouds" in condition:
            return "weather-cloudy", (0.6, 0.6, 0.6, 1) # Grey
        elif "shower rain" in condition or "rain" in condition:
            return "weather-rainy", (0.3, 0.3, 0.5, 1) # Blue-grey
        elif "thunderstorm" in condition:
            return "weather-lightning", (0.2, 0.2, 0.4, 1) # Dark blue
        elif "snow" in condition:
            return "weather-snowy", (0.8, 0.9, 1, 1) # Light blue/white
        elif "mist" in condition or "fog" in condition:
            return "weather-fog", (0.7, 0.7, 0.7, 1) # Light grey
        else:
            # Default backup
            return "weather-cloudy", (0.6, 0.6, 0.6, 1)

    @mainthread
    def on_login_success(self, user_info):
        # This runs on the MAIN UI THREAD (Safe for UI updates, Ex: Picture)
        dashboard = self.manager.get_screen("dashboard")

        dashboard.ids.user_name.text = user_info['name']
        dashboard.ids.profile_image.source = user_info['picture']
        
        # Configuring login button based on successful login attempt 
        self.ids.status_label.text = ""
        self.ids.google_button.disabled = False

        # Location and Weather Information
        lat, lon, address = get_location()
        temp, condition = get_weather(lat, lon)

        # Update labels
        dashboard.ids.weather_temp_label.text = f"{int(round(temp))}°C"
        # Shorten address to just city if possible, roughly
        city_name = address.split(",")[0] if "," in address else address
        dashboard.ids.weather_loc_label.text = city_name

        # Determine icon and color based on condition
        icon_name, icon_color = self.get_icon_map(condition)

        # Update icon widget
        dashboard.ids.weather_icon.icon = icon_name
        dashboard.ids.weather_icon.text_color = icon_color

        self.manager.current = "attractions_selection"

# --- Custom Button with Selection State and Solid Fill ---
class SelectableFlatButton(MDRectangleFlatButton):
    # A property to track the selection state
    is_selected = BooleanProperty(False)

    def on_press(self):
        # Toggle the selection state on press
        self.is_selected = not self.is_selected
        
        # Trigger the screen method to update the master list
        # We rely on the KV binding (see step 3) to call the screen's method

    def on_is_selected(self, instance, value):
        # Update button appearance when selection state changes
        self.update_canvas()
    
    def update_canvas(self, *args):
        # Ensure MDApp is available
        app = MDApp.get_running_app()
        if not app:
            return

        primary_color = app.theme_cls.primary_color
        
        # Remove old drawing instructions
        self.canvas.before.clear()

        with self.canvas.before:
            if self.is_selected:
                # When selected: Draw a solid rectangle
                Color(*primary_color)
                Rectangle(pos=self.pos, size=self.size)
                
                # Set text and line color to white
                self.theme_text_color = "Custom"
                self.text_color = 1, 1, 1, 1  # White
                self.line_color = primary_color 
            else:
                # When unselected: Default appearance (Black text and line)
                # Setting a transparent color to avoid canvas conflicts if needed, 
                # but MDRectangleFlatButton handles its non-fill state well.
                self.theme_text_color = "Custom"
                self.text_color = 0, 0, 0, 1  # Black
                self.line_color = 0, 0, 0, 1  # Black line color

    # Ensure the canvas updates when the button size/position changes
    def on_size(self, *args):
        self.update_canvas()

    def on_pos(self, *args):
        self.update_canvas()

class AttractionsSelectionScreen(MDScreen):

    def handle_selection(self, button_instance):
        button_text = button_instance.text
        
        if button_instance.is_selected:
            # If the button is now selected, add its text to the list
            if button_text not in SELECTED_ATTRACTIONS:
                SELECTED_ATTRACTIONS.append(button_text)
        else:
            # If the button is now unselected, remove its text from the list
            if button_text in self.selected_attractions:
                SELECTED_ATTRACTIONS.remove(button_text)
        
        print(f"Current selections: {SELECTED_ATTRACTIONS}") # For debugging

    def go_to_next_screen(self):
        # Simply switch to the dashboard screen after the survey is 'complete'
        self.manager.current = "activities_selection"

class ActivitiesSelectionScreen(MDScreen):

    def handle_selection(self, button_instance):
        button_text = button_instance.text
        
        if button_instance.is_selected:
            # If the button is now selected, add its text to the list
            if button_text not in SELECTED_ACTIVITIES:
                SELECTED_ACTIVITIES.append(button_text)
        else:
            # If the button is now unselected, remove its text from the list
            if button_text in self.selected_activities:
                SELECTED_ACTIVITIES.remove(button_text)
        
        print(f"Current selections: {SELECTED_ACTIVITIES}") # For debugging

    def go_to_next_screen(self):
        # Simply switch to the dashboard screen after the survey is 'complete'
        self.manager.current = "cuisines_selection"

class CuisinesSelectionScreen(MDScreen):

    def handle_selection(self, button_instance):
        button_text = button_instance.text
        
        if button_instance.is_selected:
            # If the button is now selected, add its text to the list
            if button_text not in SELECTED_CUISINES:
                SELECTED_CUISINES.append(button_text)
        else:
            # If the button is now unselected, remove its text from the list
            if button_text in SELECTED_CUISINES:
                SELECTED_CUISINES.remove(button_text)
        
        print(f"Current selections: {SELECTED_CUISINES}") # For debugging

    def go_to_dashboard(self):
        # Update user preference in DB
        app = MDApp.get_running_app()
        attraction_preference = ", ".join(SELECTED_ATTRACTIONS)
        activities_preference = ", ".join(SELECTED_ACTIVITIES)
        cuisine_preference = ", ".join(SELECTED_CUISINES)
        run_query.update_preference(attraction_preference, activities_preference, cuisine_preference, app.current_user_email)

        # Simply switch to the dashboard screen after the survey is 'complete'
        self.manager.current = "dashboard"

class TravelLocationCard(MDCard):
    source = StringProperty()
    text = StringProperty()
    sub_text = StringProperty()

class DashboardScreen(MDScreen):
    current_meal_phase = StringProperty("") # Tracks current phase to avoid unnecessary reloads
    auto_refresh_event = None # To store the clock schedule

    def on_enter(self):
        # Trigger data loading when screen is shown
        self.load_data()

        # 2. Schedule a check every 60 seconds to see if meal time changed
        self.auto_refresh_event = Clock.schedule_interval(self.check_time_and_refresh, 60)

    def on_leave(self):
        # Stop the clock when leaving dashboard to save resources
        if self.auto_refresh_event:
            Clock.unschedule(self.auto_refresh_event)

    def check_time_and_refresh(self, dt):
        # Calculate what the phase SHOULD be right now
        new_phase, _, _ = self.get_meal_context()
        
        # Only fetch new data if the phase has changed (e.g., switched from Lunch to Dinner)
        if new_phase != self.current_meal_phase:
            print(f"Time changed to {new_phase}. Refreshing data...")
            self.load_data()

    def get_meal_context(self):
        """Returns (Phase Name, Display Title, API Keyword)"""
        # hour = datetime.now().hour
        hour = 1 # right now its static for testing purpose
        
        if 5 <= hour < 11:
            return "Breakfast", "Morning Fuel", "breakfast"
        elif 11 <= hour < 15:
            return "Lunch", "Lunch Spots", "lunch"
        elif 15 <= hour < 18:
            return "Snacks", "Afternoon Snacks", "cafe"
        elif 18 <= hour < 22:
            return "Dinner", "Dinner Time", "dinner"
        else:
            return "LateNight", "Late Night Eats", "late night food"

    def load_data(self):
        # Run in thread to prevent UI freeze
        threading.Thread(target=self._fetch_all_data).start()

    def _fetch_all_data(self):
        # A. Context Data
        lat, lon, address = get_location()
        temp, condition = get_weather(lat, lon)
        ontology = load_ontology()
        recommended = suggest_activity(temp, ontology)
        
        # B. Time-Based Logic
        phase, title, keyword = self.get_meal_context()
        
        # Store current phase so we know when it changes later
        self.current_meal_phase = phase

        # C. Places Data - Pass the 'keyword' to Google
        # Make sure your get_google_places accepts the 4th argument!
        restaurants = get_google_places(lat, lon, "restaurant", keyword)
        attractions = get_google_places(lat, lon, "tourist_attraction", "")

        # Update UI on Main Thread
        Clock.schedule_once(lambda dt: self.update_ui(
            address, temp, condition, recommended, restaurants, attractions, title
        ))

    def update_ui(self, address, temp, condition, recommended, restaurants, attractions, meal_title):
        # Update the Header Text dynamically
        self.ids.restaurant_header.text = meal_title
        
        # Clear existing lists to avoid duplicates
        self.ids.restaurant_list.clear_widgets()
        self.ids.attraction_list.clear_widgets()

        # Populate Restaurants
        for place in restaurants:
            card = TravelLocationCard(
                source=place['image'],
                text=place['name'],
                sub_text=f"{place['rating']} Stars"
            )
            self.ids.restaurant_list.add_widget(card)

        # Populate Attractions
        for place in attractions:
            card = TravelLocationCard(
                source=place['image'],
                text=place['name'],
                sub_text=f"{place['rating']} Stars"
            )
            self.ids.attraction_list.add_widget(card)

class TravelApp(MDApp):
    current_user_email = None
    current_user_name = None

    def build(self):
        self.title = "Travel Companion"
        Window.size = (360, 640) # Mobile simulation
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_file("app_layout.kv")

    def logout(self):
        self.current_user_email = None
        self.root.current = "login"
        self.is_loggin_in = False

if __name__ == "__main__":
    TravelApp().run()