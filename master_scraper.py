import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# --- CONFIGURATION ---
REGION = "A"
PRODUCT = "SILVER-24-12-31"
UPRN = "100081251978"
POSTCODE = "SG17 5SE"
LAT = "52.03"
LON = "-0.33"

NAME_MAP = {
    "Refuse (black bin)": "Black bin",
    "Recycling": "Green bin",
    "Food waste": "Food waste",
    "Garden waste": "Garden waste"
}

WMO_MAP = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️", 51: "🌦️", 61: "🌧️", 63: "🌧️",
    71: "❄️", 80: "🌦️", 95: "⛈️"
}

def get_bins(session):
    headers = {"User-Agent": "Mozilla/5.0"}
    files = {"postcode": (None, POSTCODE), "address": (None, UPRN)}
    try:
        url = "https://www.centralbedfordshire.gov.uk/info/163/bins_and_waste_collections_-_check_bin_collection_day#my_bin_collections"
        response = session.post(url, headers=headers, files=files, verify=False)
        soup = BeautifulSoup(response.content, "html.parser")
        collections_div = soup.find(id="collections")
        if not collections_div: return None
        all_bins = []
        for bin_header in collections_div.find_all("h3"):
            date_text = bin_header.get_text(strip=True)
            try:
                collection_date = datetime.strptime(date_text, "%A, %d %B %Y")
                current_node = bin_header.next_sibling
                while current_node and current_node.name != "h3":
                    text = current_node.get_text(strip=True) if hasattr(current_node, 'get_text') else str(current_node).strip()
                    if text and len(text) > 3 and "PDF" not in text and "Current" not in text:
                        all_bins.append({"type": NAME_MAP.get(text, text), "date_obj": collection_date})
                    current_node = current_node.next_sibling
            except ValueError: continue
        if not all_bins: return None
        first_date = all_bins[0]['date_obj']
        next_bins = [b['type'] for b in all_bins if b['date_obj'] == first_date]
        bin_string = ", ".join(next_bins[:-1]) + " & " + next_bins[-1] if len(next_bins) > 1 else next_bins[0]
        return {"line1": f"Next: {first_date.strftime('%d/%m/%y')}", "line2": f"Bins: {bin_string}"}
    except: return {"line1": "Bins: Error", "line2": "Bins: Error"}

def get_octopus():
    today = datetime.now().strftime('%Y-%m-%d')
    base_url = f"https://api.octopus.energy/v1/products/{PRODUCT}"
    elec_url = f"{base_url}/electricity-tariffs/E-1R-{PRODUCT}-{REGION}/standard-unit-rates/?period_from={today}"
    gas_url = f"{base_url}/gas-tariffs/G-1R-{PRODUCT}-{REGION}/standard-unit-rates/?period_from={today}"
    rates = {"e": "N/A", "g": "N/A"}
    try:
        e_data = requests.get(elec_url).json()
        if e_data.get('results'): rates["e"] = f"{e_data['results'][0]['value_inc_vat']:.2f}p"
        g_data = requests.get(gas_url).json()
        if g_data.get('results'): rates["g"] = f"{g_data['results'][0]['value_inc_vat']:.2f}p"
    except: pass
    return {"line3": f"Elec: {rates['e']}", "line4": f"Gas: {rates['g']}"}

def get_weather():
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=weathercode,temperature_2m&timezone=Europe%2FLondon&forecast_days=1"
        res = requests.get(url).json()
        hourly = res['hourly']
        current_hour = datetime.now().hour
        
        if current_hour < 11:
            times = [8, 9, 12, 15]
        elif current_hour < 14:
            times = [12, 14, 15, 16]
        elif current_hour < 18:
            times = [15, 16, 17, 18]
        else:
            times = [19, 20, 21, 22]
            
        forecast_parts = []
        for t in times:
            code = hourly['weathercode'][t]
            temp = round(hourly['temperature_2m'][t])
            icon = WMO_MAP.get(code, "☁️")
            # Format time to be 08:00 instead of 8h
            formatted_time = f"{t:02d}:00"
            forecast_parts.append(f"{formatted_time}:{icon}{temp}°")
        return {"line5": " ".join(forecast_parts)}
    except: return {"line5": "Weather: N/A"}

if __name__ == "__main__":
    session = requests.Session()
    requests.packages.urllib3.disable_warnings()
    bins = get_bins(session) or {"line1": "Bins: N/A", "line2": "Bins: N/A"}
    energy = get_octopus()
    weather = get_weather()
    output = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "display_line_1": bins["line1"],
        "display_line_2": bins["line2"],
        "display_line_3": energy["line3"],
        "display_line_4": energy["line4"],
        "display_line_5": weather["line5"]
    }
    with open('display.json', 'w') as f:
        json.dump(output, f, indent=4)
