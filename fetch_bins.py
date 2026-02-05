import sys
import json
import importlib
from datetime import datetime

# The possible "internal" names the library uses
possible_paths = [
    "uk_bin_collection.uk_bin_collection.councils.CentralBedfordshireCouncil",
    "uk_bin_collection.councils.CentralBedfordshireCouncil",
    "CentralBedfordshireCouncil"
]

def run_fetch():
    council_module = None
    
    # Try to find the module in the mess of folders
    for path in possible_paths:
        try:
            council_module = importlib.import_module(path)
            print(f"Success! Found module at: {path}")
            break
        except ImportError:
            continue

    if not council_module:
        print("Error: Could not find the Council module in any expected folder.")
        sys.exit(1)

    # Execute the scraper logic
    try:
        # These are the standard parameters for Central Beds
        kwargs = {
            "postcode": "SG17 5SE",
            "url": "https://www.centralbedfordshire.gov.uk/info/163/bins_and_waste_collections_-_check_bin_collection_days"
        }
        
        # Initialize and run the scraper class
        scraper = council_module.CentralBedfordshireCouncil()
        data = scraper.fetch_data(**kwargs)
        
        # Save the result
        output = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "bins": data
        }
        
        with open('bin_data.json', 'w') as f:
            json.dump(output, f, indent=4)
        
        print("Successfully updated bin_data.json")

    except Exception as e:
        print(f"Scraper execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_fetch()
