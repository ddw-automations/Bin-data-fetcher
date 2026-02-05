import requests
import json
from datetime import datetime

# CONFIGURATION
REGION = "A"
PRODUCT = "SILVER-24-12-31" # Reverted to the Dec 2024 code

def get_octopus_prices():
    today = datetime.now().strftime('%Y-%m-%d')
    
    # API URLs for unit rates
    elec_url = f"https://api.octopus.energy/v1/products/{PRODUCT}/electricity-tariffs/E-1R-{PRODUCT}-{REGION}/standard-unit-rates/?period_from={today}"
    gas_url = f"https://api.octopus.energy/v1/products/{PRODUCT}/gas-tariffs/G-1R-{PRODUCT}-{REGION}/standard-unit-rates/?period_from={today}"
    
    prices = {"elec": "N/A", "gas": "N/A"}
    
    try:
        e_res = requests.get(elec_url).json()
        if e_res.get('results'):
            prices["elec"] = f"{e_res['results'][0]['value_inc_vat']:.2f}p"
            
        g_res = requests.get(gas_url).json()
        if g_res.get('results'):
            prices["gas"] = f"{g_res['results'][0]['value_inc_vat']:.2f}p"
            
        return prices
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    rates = get_octopus_prices()
    output = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "display_line_1": f"Elec: {rates['elec'] if rates else 'N/A'}",
        "display_line_2": f"Gas: {rates['gas'] if rates else 'N/A'}"
    }

    with open('octopus_data.json', 'w') as f:
        json.dump(output, f, indent=4)
