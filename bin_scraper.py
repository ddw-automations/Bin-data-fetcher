import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_bins():
    user_postcode = "SG17 5SE"
    user_uprn = "100081251978" 

    s = requests.Session()
    requests.packages.urllib3.disable_warnings()

    headers = {
        "Origin": "https://www.centralbedfordshire.gov.uk",
        "Referer": "https://www.centralbedfordshire.gov.uk/info/163/bins_and_waste_collections_-_check_bin_collection_day",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    files = {
        "postcode": (None, user_postcode),
        "address": (None, user_uprn),
    }

    try:
        response = s.post(
            "https://www.centralbedfordshire.gov.uk/info/163/bins_and_waste_collections_-_check_bin_collection_day#my_bin_collections",
            headers=headers,
            files=files,
            verify=False
        )
        
        soup = BeautifulSoup(response.content, "html.parser")
        collections_div = soup.find(id="collections")
        if not collections_div: return []

        all_bins = []
        for bin_header in collections_div.find_all("h3"):
            date_text = bin_header.get_text(strip=True)
            try:
                collection_date = datetime.strptime(date_text, "%A, %d %B %Y")
                current_node = bin_header.next_sibling
                while current_node and current_node.name != "h3":
                    text = current_node.get_text(strip=True) if hasattr(current_node, 'get_text') else str(current_node).strip()
                    # Filter: Must be long enough, not the PDF link, and not "Current collection dates"
                    if text and len(text) > 3 and "PDF" not in text and "Current" not in text:
                        all_bins.append({
                            "type": text,
                            "collectionDate": collection_date.strftime("%Y-%m-%d")
                        })
                    current_node = current_node.next_sibling
            except ValueError:
                continue

        if not all_bins: return []

        # LOGIC: Find the soonest date and only return those bins
        first_date = all_bins[0]['collectionDate']
        next_collections = [b for b in all_bins if b['collectionDate'] == first_date]

        return next_collections

    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    data = get_bins()
    with open('bin_data.json', 'w') as f:
        json.dump({
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"), 
            "bins": data
        }, f, indent=4)
    print(f"Success! Next collection is {data[0]['collectionDate'] if data else 'N/A'}")
