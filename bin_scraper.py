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
        
        if not collections_div:
            return []

        collections = []
        # Find all the date headers
        headers_found = collections_div.find_all("h3")
        
        for bin_header in headers_found:
            date_text = bin_header.get_text(strip=True)
            try:
                collection_date = datetime.strptime(date_text, "%A, %d %B %Y")
                
                # Now we look at everything BETWEEN this <h3> and the next <h3>
                current_node = bin_header.next_sibling
                while current_node and current_node.name != "h3":
                    # If it's a tag (like <p>) or a piece of text
                    text = ""
                    if hasattr(current_node, 'get_text'):
                        text = current_node.get_text(strip=True)
                    elif isinstance(current_node, str):
                        text = current_node.strip()
                    
                    # If we found text that isn't empty, it's a bin type
                    if text and len(text) > 3: # Ignore tiny fragments/artifacts
                        collections.append({
                            "type": text,
                            "collectionDate": collection_date.strftime("%Y-%m-%d")
                        })
                    
                    current_node = current_node.next_sibling
            except ValueError:
                # This handles cases where <h3> might be "Current collection dates..." 
                continue

        return collections

    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    data = get_bins()
    with open('bin_data.json', 'w') as f:
        json.dump({
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"), 
            "uprn": "100081251978",
            "bins": data
        }, f, indent=4)
    print(f"Scrape complete. Found {len(data)} bin entries.")
