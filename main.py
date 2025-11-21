from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.lang import Builder
from kivy.core.window import Window

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
            self.manager.current = "dashboard"
            self.manager.get_screen("dashboard").ids.welcome_label.text = f"Hello, {user_info['given_name']}"
        else:
            self.ids.status_label.text = "Login Failed. Try again."

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
        Window.size = (360, 640) # Mobile simulation
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_file("travel.kv")

    def logout(self):
        self.current_user_email = None
        self.root.current = "login"

if __name__ == "__main__":
    TravelApp().run()