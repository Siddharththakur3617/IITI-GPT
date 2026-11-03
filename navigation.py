import json
from difflib import get_close_matches
from urllib.request import Request, urlopen

import folium

# Free OSRM walking-route server on OpenStreetMap data (no API key)
OSRM = "https://routing.openstreetmap.de/routed-foot/route/v1/foot/{},{};{},{}?overview=full&geometries=geojson"

# IIT Indore campus places (lat, lon) by category, from github.com/Monik17/IITI-GPT
PLACES = {
    "🏠 Hostels": {
        "VSB Hostel": (22.531799, 75.923740),
        "HJB Hostel": (22.532027, 75.924920),
        "CVR Hostel": (22.532418, 75.924100),
        "DA Hostel": (22.531091, 75.923477),
        "APJ Hostel": (22.530649, 75.924293),
        "JCB Hostel": (22.527647, 75.925087),
        "Narmada Hall of Residence": (22.523546, 75.922418),
        "Kshipra Hall of Residence": (22.522986, 75.925342),
    },
    "🍔 Food & Shops": {
        "Central Dining Hall (Mess)": (22.528975, 75.925320),
        "Nescafe": (22.528662, 75.923880),
        "Dominos": (22.528717, 75.924604),
        "La Fresco": (22.530310, 75.922997),
        "Amul": (22.5296329, 75.9252789),
        "Jucilicious": (22.5294523, 75.9251020),
        "Shiru Cafe": (22.5298652, 75.9248066),
        "AS Canteen": (22.5305232, 75.9251028),
        "Village Cafe": (22.5301604, 75.9248613),
        "Zippy Cafe": (22.5302921, 75.9250271),
        "Ravechi": (22.528719, 75.922541),
        "Daily Needs": (22.529453, 75.925443),
        "Fruits Shop": (22.5302106, 75.9229220),
    },
    "🎓 Academic": {
        "Lecture Hall Complex (LHC)": (22.526413, 75.924341),
        "Nalanda Auditorium": (22.526413, 75.924341),
        "Takshila": (22.526413, 75.924341),
        "Vikramshila": (22.526413, 75.924341),
        "Learning Resource Centre (LRC)": (22.528980, 75.922651),
        "POD 1A": (22.529058, 75.924502),
        "POD 1B": (22.529405, 75.924169),
        "POD 1C": (22.529388, 75.923327),
        "POD 1D": (22.529091, 75.923440),
        "POD 1E": (22.528833, 75.923469),
        "SIC": (22.521581, 75.921275),
        "CITC": (22.525479, 75.921723),
        "Central Workshop": (22.525890, 75.921361),
        "Abhinandan Bhavan": (22.528392, 75.921498),
    },
    "🏛️ Campus & Services": {
        "Health Centre (Hospital)": (22.525538, 75.926304),
        "Bus Stop": (22.528980, 75.922651),
        "Sports Complex": (22.531766, 75.920570),
        "Shri Bal Hanuman Mandir": (22.531766, 75.920570),
        "Masjid": (22.531766, 75.920570),
        "Vindhyachal Guest House": (22.524173, 75.925806),
        "Kendriya Vidyalaya (KV)": (22.520518, 75.921179),
        "Director's Bungalow": (22.519991, 75.923220),
        "Canara Bank": (22.5303037, 75.9228661),
        "SBI ATM": (22.5253889, 75.9210500),
        "Maa Laundry": (22.535066, 75.929185),
        "Cycle Repair Shop": (22.532453, 75.921426),
        "HVAC Plant": (22.525479, 75.921723),
        "Sewage Treatment Plant": (22.535066, 75.929185),
    },
    "🚪 Gates": {
        "Gate 1A": (22.529529, 75.912679),
        "Gate 1B": (22.528566, 75.917104),
        "Gate 2": (22.51901, 75.91561),
    },
    "🅿️ Parking": {
        "Parking – Nalanda": (22.526581, 75.923558),
        "Parking – LRC": (22.528147, 75.922847),
        "Parking – POD": (22.528110, 75.924725),
        "Parking – Health Centre": (22.525630, 75.926060),
        "Parking – Sports Complex": (22.529906, 75.920111),
    },
}
COORDS = {name: point for group in PLACES.values() for name, point in group.items()}
PLACE_LIST = [(group, name) for group, names in PLACES.items() for name in names]  # for the dropdown

# Other names people type for the same place
ALIASES = {
    "vsb": "VSB Hostel", "hjb": "HJB Hostel", "cvr": "CVR Hostel", "da": "DA Hostel", "apj": "APJ Hostel",
    "jcb": "JCB Hostel", "narmada": "Narmada Hall of Residence", "kshipra": "Kshipra Hall of Residence",
    "mess": "Central Dining Hall (Mess)", "centraldinninghall": "Central Dining Hall (Mess)",
    "juicy": "Jucilicious", "dn": "Daily Needs", "lhc": "Lecture Hall Complex (LHC)",
    "lecturehallcomplex": "Lecture Hall Complex (LHC)", "takshilla": "Takshila",
    "lrc": "Learning Resource Centre (LRC)", "hospital": "Health Centre (Hospital)",
    "healthcentre": "Health Centre (Hospital)", "mandir": "Shri Bal Hanuman Mandir",
    "guesthouse": "Vindhyachal Guest House", "kv": "Kendriya Vidyalaya (KV)",
    "kendriyavidyalay": "Kendriya Vidyalaya (KV)", "laundry": "Maa Laundry", "parkinghc": "Parking – Health Centre",
}


def simplify(text):
    return "".join(ch for ch in text.lower() if ch.isalnum())


NAMES = {simplify(name): name for name in COORDS} | {simplify(a): name for a, name in ALIASES.items()}


def find(text):
    """Closest known place for what the user typed, e.g. 'health center' -> 'Health Centre (Hospital)'."""
    match = get_close_matches(simplify(text), NAMES, n=1, cutoff=0.5)
    if not match:
        raise ValueError(f"Unknown place: {text}")
    return NAMES[match[0]]


def walking_route(a, b):
    """Walking path between two (lat, lon) points; a straight line if the service fails."""
    try:
        url = OSRM.format(a[1], a[0], b[1], b[0])  # OSRM wants lon,lat
        with urlopen(Request(url, headers={"User-Agent": "iitigpt"}), timeout=10) as response:
            route = json.load(response)["routes"][0]
        path = [(lat, lon) for lon, lat in route["geometry"]["coordinates"]]
        return path, f"{round(route['distance'])} m · ~{round(route['duration'] / 60)} min walk"
    except (OSError, ValueError, KeyError, IndexError):
        return [a, b], "Walking route unavailable, showing a straight line"


def route_map(start, end):
    start, end = find(start), find(end)
    path, info = walking_route(COORDS[start], COORDS[end])
    m = folium.Map()
    folium.PolyLine(path, color="blue", weight=5).add_to(m)
    folium.Marker(COORDS[start], tooltip=f"Start: {start}", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(COORDS[end], tooltip=f"End: {end}", icon=folium.Icon(color="red")).add_to(m)
    m.fit_bounds(path + [COORDS[start], COORDS[end]])
    return start, end, info, m.get_root().render()
