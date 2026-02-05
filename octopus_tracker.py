import requests
import json
from datetime import datetime

# CONFIGURATION
# Region A = Eastern England (includes Shefford/Bedfordshire)
REGION = "A"
# Standard Tracker Product Code for 2026
PRODUCT = "SILVER-23-12-06"

def get_octopus_prices():
    today = datetime.now().strftime('%Y-%m-%d')
    
    # API URLs for unit rates (Unit rate includes VAT)
    elec_url = f"https://api.octopus.energy/v1/products/{PRODUCT}/electricity-tariffs/E-1R-{PRODUCT}-{REGION}/standard-unit-rates/?period_from={today}"
    gas_url = f"https://api.octopus.energy/v1/products/{PRODUCT}/gas-tariffs/G-1R-{PRODUCT}-{REGION}/standard-unit-rates/?period_from={today}"
    
    prices = {"elec": "N/A", "gas": "N/A"}
    
    try:
        # Fetch Electricity
        e_res = requests.get(elec_url).json()
        if e_res.get('results'):
            val = e_res['results'][0]['value_inc_vat']
            prices["elec"] = f"{val:.2f}p"
            
        # Fetch Gas
        g_res = requests.get(gas_url).json()
        if g_res.get('results'):
            val = g_res['results'][0]['value_inc_vat']
            prices["gas"] = f"{val:.2f}p"
            
        return prices
    except Exception as e:
        print(f"Error fetching Octopus prices: {e}")
        return None

if __name__ == "__main__":
    rates = get_octopus_prices()
    
    if rates:
        output = {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "display_line_1": f"Elec: {rates['elec']}",
            "display_line_2": f"Gas: {rates['gas']}"
        }
    else:
        output = {"error": "Could not fetch energy prices"}

    with open('octopus_data.json', 'w') as f:
        json.dump(output, f, indent=4)
        
    print(f"Octopus Update (Region {REGION}):\n{output.get('display_line_1')}\n{output.get('display_line_2')}")
