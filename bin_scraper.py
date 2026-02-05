import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_bins():
    url = "https://www.centralbedfordshire.gov.uk/info/163/bins_and_waste_collections_-_check_bin_collection_days"
    postcode = "SG17 5SE"
    
    # This logic mimics the UKBinCollectionData 'Jadu' parser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    session = requests.Session()
    
    try:
        # 1. Load the page to get session cookies
        response = session.get(url, headers=headers)
        
        # 2. Post the postcode
        # Central Beds expects the 'postcode' field in a POST request
        payload = {'postcode': postcode}
        response = session.post(url, data=payload, headers=headers)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        bin_data = []

        # This is the exact CSS selector logic the repo uses for this council
        results = soup.find_all('div', class_='bin-result')
        
        for res in results:
            bin_type = res.find('h3').get_text(strip=True) if res.find('h3') else "Unknown"
            # Get the text from the paragraph, removing the "Next collection:" prefix
            bin_date = res.find('p').get_text(strip=True).replace('Next collection:', '').strip() if res.find('p') else "Unknown"
            
            bin_data.append({
                "type": bin_type,
                "collectionDate": bin_date
            })

        return bin_data

    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    data = get_bins()
    output = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "bins": data
    }
    
    with open('bin_data.json', 'w') as f:
        json.dump(output, f, indent=4)
    
    if data:
        print(f"Success! Found {len(data)} bin types.")
    else:
        print("Failed to find any bin data. Check the postcode or site status.")

if __name__ == "__main__":
    main()
