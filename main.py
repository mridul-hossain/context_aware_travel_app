from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from context_module import get_location, get_weather
from ontology_module import load_ontology, suggest_activity
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "travel_companion.db"

class TravelLayout(BoxLayout):
    def fetch_context(self):
        lat, lon, address = get_location()
        temp, condition = get_weather(lat, lon)

        ontology = load_ontology()
        recommended = suggest_activity(temp, ontology)

        self.ids.location_label.text = f"📍 Location: {address}"
        self.ids.weather_label.text = f"🌤 Temp: {temp}°C, {condition}"
        self.ids.activity_label.text = f"🎯 Suggestion: {recommended}"

        conn = sqlite3.connect(DB_PATH.as_posix())
        c = conn.cursor()
        c.execute("INSERT INTO user_context (location, temperature, recommended_activity) VALUES (?, ?, ?)",
                  (address, temp, recommended))
        conn.commit()
        conn.close()

class TravelApp(App):
    def build(self):
        return TravelLayout()

if __name__ == "__main__":
    TravelApp().run()
