import requests
import pandas as pd
import json

# Replace with your Neutrino API credentials
USER_ID = "Tohka"
API_KEY = "On2I9wPkS2aJYflMX99umTM0XfbTFL4LH3JoHpZVc0gxuV7n"

# API endpoint
url = "https://neutrinoapi.net/phone-validate"

# Get user input
number = input("Enter the phone number (e.g., +6495552000): ")
country_code = input("Enter the country code (leave blank if not applicable): ")
ip = input("Enter the IP address (leave blank if not applicable): ")

# Parameters
params = {
    "number": number,
    "country-code": country_code,
    "ip": ip
}

# Headers
headers = {
    "User-ID": USER_ID,
    "API-Key": API_KEY
}

# Make the POST request
response = requests.post(url, headers=headers, data=params)

if response.status_code == 200:
    data = response.json()
    country_name = data.get("country")
    country_code = data.get("country-code")

    # Rearrange the results
    rearranged_data = {
        "Valid": data.get("valid"),
        "Type": data.get("type"),
        "Country": data.get("country"),
        "Location": data.get("location"),
        "International Number": data.get("international-number"),
        "Local Number": data.get("local-number"),
        "Country Code": data.get("country-code"),
        "Currency Code": data.get("currency-code"),
        "International Calling Code": data.get("international-calling-code"),
        "Is Mobile": data.get("is-mobile"),
        "Prefix Network": data.get("prefix-network")
    }

    # Display rearranged data
    print("\nPhone Validation Results:")
    for key, value in rearranged_data.items():
        print(f"{key}: {value}")

    # Check additional country details from CSV
    csv_file = "countries/countries.csv"  # Replace with your actual CSV file path
    try:
        country_data = pd.read_csv(csv_file, delimiter=";")
        country_info = country_data[country_data['Country Name'] == country_name]

        if not country_info.empty:
            print("\nAdditional Country Details (CSV):")
            for col in country_info.columns:
                print(f"{col}: {country_info.iloc[0][col]}")
        else:
            print("\nNo additional details found for this country in the CSV file.")

    except FileNotFoundError:
        print("\nCountry details CSV file not found.")

else:
    print(f"Error {response.status_code}: {response.text}")