import requests
import json
from datetime import datetime

# --- CONFIGURATION ---
POSTCODE = "SG17 5SE"
# Using a 'User-Agent' makes the script look like a real web browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

ELEC_URL = "https://api.octopus.energy/v1/products/SILVER-23-12-06/electricity-tariffs/E-1R-SILVER-23-12-06-A/standard-unit-rates/"
GAS_URL = "https://api.octopus.energy/v1/products/SILVER-23-12-06/gas-tariffs/G-1R-SILVER-23-12-06-A/standard-unit-rates/"

def get_bin_data():
    # Placeholder for the Wednesday rotation logic
    return [
        {"type": "Domestic (Black)", "date": "Wed 11th Feb"},
        {"type": "Recycling (Orange)", "date": "Wed 18th Feb"}
    ]

def get_octopus_price(url):
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        params = {'period_from': f"{today}T00:00:00Z", 'period_to': f"{today}T23:59:59Z"}
        
        # Added headers=HEADERS here to bypass the 403 error
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status() # This will trigger the 'except' block if it's a 403
        
        data = response.json()
        if data.get('results'):
            return round(data['results'][0]['value_inc_vat'], 2)
        return "N/A"
    except Exception as e:
        print(f"Octopus API Error: {e}")
        return "Error"

def main():
    elec = get_octopus_price(ELEC_URL)
    gas = get_octopus_price(GAS_URL)
    bins = get_bin_data()

    home_data = {
        "metadata": {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "postcode": POSTCODE
        },
        "energy": {
            "elec": f"{elec}p" if elec != "Error" else "Error",
            "gas": f"{gas}p" if gas != "Error" else "Error",
            "unit": "p/kWh"
        },
        "bins": bins
    }

    with open('home_data.json', 'w') as f:
        json.dump(home_data, f, indent=4)
    
    print(f"Master record updated. Elec: {elec}, Gas: {gas}")

if __name__ == "__main__":
    main()
