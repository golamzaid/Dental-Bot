🦷 Dental Assistant Bot

An AI-powered dental health assistant that understands patient symptoms in multiple languages (English, Hindi, Bengali), identifies possible dental conditions, gives treatment advice, suggests specialists, shows urgency levels, and even finds nearby dentists/clinics on the map.

🚀 Features

🌐 Multilingual Support – Works in English, Hindi, Bengali.

🤖 NLP-based Condition Matching – Matches user symptoms to a knowledge base (dental_conditions.yaml).

🩺 Advice & Specialist Recommendation – Gives condition-specific guidance and refers to the right dental specialist.

⚡ Urgency Levels – Classifies cases into Immediate, Visit Soon, or Routine Check.

📍 Nearby Dentists – Finds dentists/clinics near a user-provided location (using OSM + dummy dataset fallback).

🎨 Colorful UI – Simple but interactive frontend built with Flask + HTML + CSS.

🛠️ Tech Stack

Backend: Python, Flask

Frontend: HTML, CSS, Vanilla JS

NLP: Custom YAML-based knowledge base

Maps: Geopy, OpenStreetMap (Overpass API)

Fallback Data: Dummy dataset for random clinics/doctors
