import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_bin_data():
    postcode = "SG17 5SE"
    url = "https://www.centralbedfordshire.gov.uk/info/163/bins_and_waste_collections_-_check_bin_collection_days"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Origin': 'https://www.centralbedfordshire.gov.uk',
        'Referer': url
    }

    try:
        session = requests.Session()
        # 1. Get the page to establish a session
        session.get(url, headers=headers)
        
        # 2. Post the postcode to get the results
        # Central Beds expects a 'postcode' field in the body
        response = session.post(url, data={'postcode': postcode}, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        bin_collections = []
        
        # The UKBinCollectionData logic looks for the 'bin-result' class
        # within the Jadu platform layout
        results = soup.find_all('div', class_='bin-result')
        
        for res in results:
            # Each div usually contains an <h3> for the bin type and a <p> for the date
            bin_type = res.find('h3').get_text(strip=True) if res.find('h3') else "Unknown"
            bin_date = res.find('p').get_text(strip=True) if res.find('p') else "Unknown"
            
            bin_collections.append({
                "type": bin_type,
                "date": bin_date
            })

        return bin_collections

    except Exception as e:
        return [{"type": "Error", "date": str(e)}]

def main():
    bins = get_bin_data()
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "collections": bins
    }
    
    with open('bin_data.json', 'w') as f:
        json.dump(output, f, indent=4)
    print(f"Scraped {len(bins)} bin collections.")

if __name__ == "__main__":
    main()
