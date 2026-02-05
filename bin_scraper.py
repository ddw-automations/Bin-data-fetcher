import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_bins():
    user_postcode = "SG17 5SE"
    user_uprn = "100081251978" 

    s = requests.Session()
    # Disable warnings for their SSL setup
    requests.packages.urllib3.disable_warnings()

    headers = {
        "Origin": "https://www.centralbedfordshire.gov.uk",
        "Referer": "https://www.centralbedfordshire.gov.uk/info/163/bins_and_waste_collections_-_check_bin_collection_day",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    # Central Bedfordshire's specific multipart/form-data requirement
    files = {
        "postcode": (None, user_postcode),
        "address": (None, user_uprn),
    }

    try:
        # Note: We hit the #my_bin_collections anchor as per the council script
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
        # The site lists dates in <h3> and bin types in the text nodes following them
        for bin_header in collections_div.find_all("h3"):
            date_text = bin_header.get_text(strip=True)
            try:
                # Convert "Friday, 06 February 2026" to a standard date
                collection_date = datetime.strptime(date_text, "%A, %d %B %Y")
                
                # Find the bin type (usually the next text node)
                next_node = bin_header.next_sibling
                while next_node:
                    if next_node.name == "h3": break
                    text = next_node.get_text(strip=True) if hasattr(next_node, 'get_text') else str(next_node).strip()
                    if text and not text.isspace():
                        collections.append({
                            "type": text,
                            "collectionDate": collection_date.strftime("%Y-%m-%d")
                        })
                        break
                    next_node = next_node.next_sibling
            except ValueError:
                continue

        return collections

    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    data = get_bins()
    with open('bin_data.json', 'w') as f:
        json.dump({"last_update": datetime.now().strftime("%Y-%m-%d %H:%M"), "bins": data}, f, indent=4)
    print(f"Scrape complete. Found {len(data)} collections.")
