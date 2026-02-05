import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_bins():
    # SETTINGS - Adjust these
    user_postcode = "SG17 5SE"
    user_uprn = "100081251978" # This is a sample UPRN for that postcode. 
                               # Update this with your specific one if needed.

    s = requests.Session()
    requests.packages.urllib3.disable_warnings()

    headers = {
        "Origin": "https://www.centralbedfordshire.gov.uk",
        "Referer": "https://www.centralbedfordshire.gov.uk/info/163/bins_and_waste_collections_-_check_bin_collection_day",
        "User-Agent": "Mozilla/5.0 (Linux; Android 8.0; Pixel 2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.7968.1811 Mobile Safari/537.36",
    }

    # This matches the council's specific 'multipart' requirement
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
            print("Could not find the 'collections' ID on the page.")
            return []

        collections = []
        # Their logic: find the date in <h3> and then the bin type in the text following it
        for bin_header in collections_div.find_all("h3"):
            collection_date_str = bin_header.text.strip()
            try:
                collection_date = datetime.strptime(collection_date_str, "%A, %d %B %Y")
                
                # Look for the bin type text following the <h3>
                next_node = bin_header.next_sibling
                while next_node:
                    if next_node.name == "h3": # Stop if we hit the next date
                        break
                    if isinstance(next_node, str) and next_node.strip():
                        bin_type = next_node.strip()
                        collections.append({
                            "type": bin_type,
                            "collectionDate": collection_date.strftime("%d/%m/%Y")
                        })
                        break
                    next_node = next_node.next_sibling
            except ValueError:
                continue

        # Sort by date
        return sorted(collections, key=lambda x: datetime.strptime(x['collectionDate'], "%d/%m/%Y"))

    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    bin_data = get_bins()
    output = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "bins": bin_data
    }
    with open('bin_data.json', 'w') as f:
        json.dump(output, f, indent=4)
    print(f"Done. Found {len(bin_data)} bins.")
