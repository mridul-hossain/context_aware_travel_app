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

# Import your modules
from context_module import get_location, get_weather
from ontology_module import load_ontology, suggest_activity
from auth_module import google_login_flow
import sqlite3
from pathlib import Path
import threading

DB_PATH = Path(__file__).parent / "database" / "travel_companion.db"

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

class AttractionsSelectionScreen(MDScreen):
    def go_to_dashboard(self):
        # Simply switch to the dashboard screen after the survey is 'complete'
        self.manager.current = "activities_selection"

class ActivitiesSelectionScreen(MDScreen):
    def go_to_dashboard(self):
        # Simply switch to the dashboard screen after the survey is 'complete'
        self.manager.current = "cuisines_selection"

class CuisinesSelectionScreen(MDScreen):
    def go_to_dashboard(self):
        # Simply switch to the dashboard screen after the survey is 'complete'
        self.manager.current = "dashboard"

class DashboardScreen(MDScreen):
    def fetch_context(self):
        # 1. Get Data
        lat, lon, address = get_location()
        temp, condition = get_weather(lat, lon)
        ontology = load_ontology()
        recommended = suggest_activity(temp, ontology)

        # 2. Update UI
        self.ids.location_label.text = f"Location: {address}"
        self.ids.weather_label.text = f"Temp: {temp}°C, {condition}"
        self.ids.activity_label.text = f"Suggestion: {recommended}"

        # 3. Save to DB with User Email
        app = MDApp.get_running_app()
        user_email = getattr(app, 'current_user_email', 'anonymous')

        conn = sqlite3.connect(DB_PATH.as_posix())
        c = conn.cursor()
        c.execute("""
            INSERT INTO user_context (user_email, location, temperature, recommended_activity) 
            VALUES (?, ?, ?, ?)
        """, (user_email, address, temp, recommended))
        conn.commit()
        conn.close()

class TravelApp(MDApp):
    current_user_email = None
    current_user_name = None

    def build(self):
        self.title = "Travel Companion"
        Window.size = (360, 640) # Mobile simulation
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_file("travel.kv")

    def logout(self):
        self.current_user_email = None
        self.root.current = "login"
        self.is_loggin_in = False

if __name__ == "__main__":
    TravelApp().run()