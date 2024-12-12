import requests
import random
import string

# URL of your API endpoint
url = "http://localhost:8080/api/v1/breeders/"


# Function to generate random dummy data
def generate_dummy_breeder():
    location_data = {
        "USA": ["New York", "Los Angeles", "Chicago", "Houston", "San Francisco"],
        "France": ["Paris", "Lyon", "Marseille", "Nice", "Toulouse"],
        "Germany": ["Berlin", "Munich", "Frankfurt", "Hamburg", "Cologne"],
        "Japan": ["Tokyo", "Osaka", "Nagoya", "Kyoto", "Hiroshima"],
        "Russia": ["Moscow", "Saint Petersburg", "Kazan", "Novosibirsk", "Sochi"],
        "India": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"],
        "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"],
        "Brazil": ["Rio de Janeiro", "São Paulo", "Brasília", "Salvador", "Fortaleza"],
        "South Africa": ["Cape Town", "Johannesburg", "Durban", "Pretoria", "Port Elizabeth"],
    }
    price_levels = ['low', 'medium', 'high']

    # Select a random country
    breeder_country = random.choice(list(location_data.keys()))

    # Select a random city from the chosen country
    breeder_city = random.choice(location_data[breeder_country])

    # Generate random name
    name = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=10))

    # Randomly select a price level
    price_level = random.choice(price_levels)

    # Generate a random breeder address
    breeder_address = f"{random.randint(1, 999)} {''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=10))} Street"

    # Generate a realistic email address
    breeder_email = f"{name.lower()}@example.com"

    return {
        "name": name,
        "breeder_city": breeder_city,
        "breeder_country": breeder_country,
        "price_level": price_level,
        "breeder_address": breeder_address,
        "email": breeder_email
    }


# Loop to add 20 dummy data
for _ in range(20):
    dummy_breeder = generate_dummy_breeder()

    # Sending the POST request
    response = requests.post(url, json=dummy_breeder)

    # Checking if the request was successful
    if response.status_code == 201:
        print(f"Successfully added breeder: {dummy_breeder['name']}")
    else:
        print(f"Failed to add breeder: {dummy_breeder['name']} - Status Code: {response.status_code}")
        try:
            # Log the response text for more details on the failure
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error while reading response text: {e}")
