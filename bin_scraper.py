import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# Configuration for mapping raw council text to display-friendly names
NAME_MAP = {
    "Refuse (black bin)": "Black bin",
    "Recycling": "Green bin",
    "Food waste": "Food waste",
    "Garden waste": "Garden waste"
}

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
            return None

        all_bins = []
        for bin_header in collections_div.find_all("h3"):
            date_text = bin_header.get_text(strip=True)
            try:
                collection_date = datetime.strptime(date_text, "%A, %d %B %Y")
                current_node = bin_header.next_sibling
                
                while current_node and current_node.name != "h3":
                    text = current_node.get_text(strip=True) if hasattr(current_node, 'get_text') else str(current_node).strip()
                    
                    if text and len(text) > 3 and "PDF" not in text and "Current" not in text:
                        clean_name = NAME_MAP.get(text, text)
                        all_bins.append({
                            "type": clean_name,
                            "date_obj": collection_date
                        })
                    current_node = current_node.next_sibling
            except ValueError:
                continue

        if not all_bins: 
            return None

        # 1. Get the earliest date
        first_date_obj = all_bins[0]['date_obj']
        
        # 2. Get bins for that date
        next_bins = [b['type'] for b in all_bins if b['date_obj'] == first_date_obj]
        
        # 3. Format with & (e.g., "Green bin, Food waste & Garden waste")
        if len(next_bins) > 1:
            bin_string = ", ".join(next_bins[:-1]) + " & " + next_bins[-1]
        else:
            bin_string = next_bins[0]

        return {
            "line1": f"Next collection: {first_date_obj.strftime('%d/%m/%y')}",
            "line2": f"Bins: {bin_string}"
        }

    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    result = get_bins()
    
    if result:
        output = {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "display_line_1": result["line1"],
            "display_line_2": result["line2"]
        }
    else:
        output = {"error": "Could not fetch data"}

    with open('bin_data.json', 'w') as f:
        json.dump(output, f, indent=4)
        
    print(f"Lines generated for E290:\n{output.get('display_line_1')}\n{output.get('display_line_2')}")
