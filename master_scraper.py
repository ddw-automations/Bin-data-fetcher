import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# --- CONFIGURATION ---
POSTCODE = "SG17 5SE"
BIN_URL = "https://www.centralbedfordshire.gov.uk/info/163/bins_and_waste_collections_-_check_bin_collection_days"
ELEC_URL = "https://api.octopus.energy/v1/products/SILVER-23-12-06/electricity-tariffs/E-1R-SILVER-23-12-06-A/standard-unit-rates/"
GAS_URL = "https://api.octopus.energy/v1/products/SILVER-23-12-06/gas-tariffs/G-1R-SILVER-23-12-06-A/standard-unit-rates/"

def get_bin_data():
    try:
        # Currently using the confirmed Wednesday logic for SG17 5SE
        # (This can be swapped for full BeautifulSoup scraping logic as needed)
        return [
            {"type": "Domestic (Black)", "date": "Wed 11th Feb"},
            {"type": "Recycling (Orange)", "date": "Wed 18th Feb"}
        ]
    except:
        return "Error"

def get_octopus_price(url):
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        params = {'period_from': f"{today}T00:00:00Z", 'period_to': f"{today}T23:59:59Z"}
        response = requests.get(url, params=params)
        data = response.json()
        if data['results']:
            return round(data['results'][0]['value_inc_vat'], 2)
        return "N/A"
    except:
        return "Error"

def main():
    # Gather all data
    elec = get_octopus_price(ELEC_URL)
    gas = get_octopus_price(GAS_URL)
    bins = get_bin_data()

    # Combine into one clean dictionary
    home_data = {
        "metadata": {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "postcode": POSTCODE
        },
        "energy": {
            "elec": f"{elec}p",
            "gas": f"{gas}p",
            "unit": "p/kWh"
        },
        "bins": bins
    }

    # Save to one file
    with open('home_data.json', 'w') as f:
        json.dump(home_data, f, indent=4)
    
    print("Master record updated successfully.")

if __name__ == "__main__":
    main()
