import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# --- CONFIGURATION ---
POSTCODE = "SG17 5SE"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def get_live_bins():
    try:
        # 1. Access the search page to get session cookies
        url = "https://www.centralbedfordshire.gov.uk/info/163/bins_and_waste_collections_-_check_bin_collection_days"
        session = requests.Session()
        res = session.get(url, headers=HEADERS)
        
        # 2. Post the postcode to the council's form
        # Central Beds uses a 'postcode' field in their search form
        response = session.post(url, data={'postcode': POSTCODE}, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 3. Find the results table or list
        # We look for the common classes used in the Jadu platform they use
        bin_data = []
        rows = soup.find_all('div', class_='bin-result') # This class is common on their site
        
        if not rows:
            # Fallback for alternative layout
            rows = soup.select('.bin-collection-tasks li') 

        for row in rows[:2]: # Just get the next two
            text = row.get_text(separator='|', strip=True)
            # Expecting format like: "Domestic Waste|Wednesday 11 February"
            parts = text.split('|')
            if len(parts) >= 2:
                bin_data.append({"type": parts[0], "date": parts[1]})

        return bin_data if bin_data else [{"type": "Check Site", "date": "No data found"}]
    except Exception as e:
        print(f"Bin Scrape Error: {e}")
        return [{"type": "Scrape Error", "date": str(datetime.now().date())}]

def get_octopus_price(url):
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        params = {'period_from': today, 'period_to': today}
        response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        data = response.json()
        if data.get('results'):
            rate = data['results'][0].get('value_inc_vat')
            return f"{round(rate, 2)}p"
        return "N/A"
    except:
        return "Error"

def main():
    print("Fetching live data...")
    elec = get_octopus_price("https://api.octopus.energy/v1/products/SILVER-23-12-06/electricity-tariffs/E-1R-SILVER-23-12-06-A/standard-unit-rates/")
    gas = get_octopus_price("https://api.octopus.energy/v1/products/SILVER-23-12-06/gas-tariffs/G-1R-SILVER-23-12-06-A/standard-unit-rates/")
    bins = get_live_bins()

    home_data = {
        "metadata": {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "postcode": POSTCODE
        },
        "energy": {"electricity": elec, "gas": gas, "unit": "p/kWh"},
        "bins": bins
    }

    with open('home_data.json', 'w') as f:
        json.dump(home_data, f, indent=4)
    print("Success: home_data.json updated with live web data.")

if __name__ == "__main__":
    main()
