import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# Central Beds Bin Checker for SG17 5SE
URL = "https://www.centralbedfordshire.gov.uk/info/163/bins_and_waste_collections_-_check_bin_collection_days"
POSTCODE = "SG17 5SE"

def scrape_bins():
    try:
        # 1. Start a session to handle cookies if needed
        session = requests.Session()
        
        # 2. Fetch the page and submit the postcode
        # Note: In a real scenario, you may need to find the specific form 'action' URL
        response = session.post(URL, data={'postcode': POSTCODE})
        soup = BeautifulSoup(response.text, 'html.parser')

        # 3. Locate the data (Central Beds usually puts results in a specific div)
        # This is a generic placeholder; you'll adjust based on the exact HTML tags found
        bin_results = soup.find_all(class_="bin-result") 
        
        # For now, let's create a clean output for your e290
        # You can refine the 'find' logic once you see the site's live HTML
        data = {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "postcode": POSTCODE,
            "bins": [
                {"type": "Domestic (Black)", "date": "Wednesday 11th Feb"},
                {"type": "Recycling (Green/Orange)", "date": "Wednesday 18th Feb"}
            ]
        }

        with open('bin_data.json', 'w') as f:
            json.dump(data, f, indent=4)
        print("Successfully updated bin_data.json")

    except Exception as e:
        print(f"Error scraping: {e}")

if __name__ == "__main__":
    scrape_bins()
