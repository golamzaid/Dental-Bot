import requests, math, random
from geopy.geocoders import Nominatim

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
GEOCODER = Nominatim(user_agent="dental_bot_app")

# ---------------- MOCK DATA ----------------
CITIES = [
    {"city":"Delhi", "lat":28.6139, "lon":77.2090},
    {"city":"Mumbai", "lat":19.0760, "lon":72.8777},
    {"city":"Kolkata", "lat":22.5726, "lon":88.3639},
    {"city":"Bangalore", "lat":12.9716, "lon":77.5946},
    {"city":"Chennai", "lat":13.0827, "lon":80.2707}
]

DENTIST_NAMES = [
    "Smile Care Dental", "Happy Teeth Clinic", "Bright Smile Dental", 
    "Pearl Dental Care", "Oral Health Center", "Tooth Fairy Clinic"
]

USE_MOCK = True  # 🔹 toggle for testing

# ---------------- GEOCODE ----------------
def geocode_address(address):
    if USE_MOCK:
        c = random.choice(CITIES)
        return c["lat"], c["lon"]
    loc = GEOCODER.geocode(address, language="en")
    if loc:
        return float(loc.latitude), float(loc.longitude)
    return None

# ---------------- FIND DENTISTS ----------------
def find_dentists_near(lat, lon, radius=5000, limit=5):
    if USE_MOCK:
        dentists = []
        for _ in range(limit):
            name = random.choice(DENTIST_NAMES)
            d_lat = lat + random.uniform(-0.01, 0.01)
            d_lon = lon + random.uniform(-0.01, 0.01)
            dist = ((lat - d_lat)**2 + (lon - d_lon)**2)**0.5 * 111  # rough km
            city = random.choice([c["city"] for c in CITIES])
            dentists.append({
                "name": name,
                "city": city,
                "distance_km": round(dist,2)
            })
        return dentists

    # ---------------- REAL Overpass API ----------------
    q = f"""
    [out:json][timeout:25];
    (
      node["amenity"="dentist"](around:{radius},{lat},{lon});
      way["amenity"="dentist"](around:{radius},{lat},{lon});
      rel["amenity"="dentist"](around:{radius},{lat},{lon});
    );
    out center {limit};
    """
    r = requests.post(OVERPASS_URL, data={"data": q}, timeout=30)
    data = r.json()
    places = []
    for el in data.get("elements", []):
        name = el.get('tags', {}).get('name', 'Dentist')
        dist = haversine(lat, lon,
                         el.get('center',{}).get('lat', el.get('lat')),
                         el.get('center',{}).get('lon', el.get('lon')))
        city = el.get('tags', {}).get('addr:city', 'Unknown')
        places.append({
            "name": name,
            "city": city,
            "distance_km": round(dist,2)
        })
    places.sort(key=lambda x: x["distance_km"])
    return places[:limit]

# ---------------- HAVERSINE ----------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # km
    from math import radians, sin, cos, asin, sqrt
    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2*asin(sqrt(a))
    return R * c
