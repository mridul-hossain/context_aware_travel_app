# 🧭 Context-Aware Travel Companion App

A simple **Python-based mobile app** (built using **Kivy**) that acts as a **context-aware travel companion**.  
It dynamically suggests travel activities based on your **current location**, **weather**, and **knowledge from an ontology** created using **Protégé**.

---

## 📱 Features

- 🌍 **Dynamic Context Awareness**  
  Retrieves current location and live temperature.

- 🌤 **Weather Integration**  
  Uses the [OpenWeather API](https://openweathermap.org/api) to fetch real-time weather data.

- 🧠 **Ontology Reasoning**  
  Loads an ontology (`.owl` file) built with Protégé using **Owlready2** for activity recommendations.

- 🗃️ **Local Storage (SQLite)**  
  Saves travel context and recommendations locally without needing an external server.

- 💻 **Cross-Platform (Kivy)**  
  Runs on Windows PC and can be deployed on Android using Buildozer.

---

## 🧩 Technologies Used

| Component | Library / Tool | Purpose |
|------------|----------------|----------|
| UI | [Kivy](https://kivy.org/) | Cross-platform GUI |
| Database | SQLite (built-in) | Local data storage |
| Weather API | [OpenWeather](https://openweathermap.org/) | Live weather info |
| Ontology | [Protégé](https://protege.stanford.edu/) + [Owlready2](https://pypi.org/project/Owlready2/) | Knowledge modeling |
| Location | [Geopy](https://pypi.org/project/geopy/) | Get location info |
| Environment | Python 3.10+ | Core programming language |
