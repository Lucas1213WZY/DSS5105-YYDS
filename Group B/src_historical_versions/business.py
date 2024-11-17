import json
from pathlib import Path

# Load factors from the JSON file
business_path = Path('./assets/BusinessTravelNProcurement.json')
with open(business_path) as f:
    business_travel_procurement_factors = json.load(f)

# Define function to calculate emissions
def calculate_business_emissions(travel_hotel, travel_flight, airline_km, diesel_truck_km, electric_truck_km):
    # Extract factors from the loaded JSON
    hotel_factor = business_travel_procurement_factors["Business Travel"]["Business Travel-Hotel"]
    flight_factor = business_travel_procurement_factors["Business Travel"]["Business Travel - Flight"]
    airline_factor = business_travel_procurement_factors["Business Procurement"]["Airline"]
    diesel_truck_factor = business_travel_procurement_factors["Business Procurement"]["Diesel Truck"]
    electric_truck_factor = business_travel_procurement_factors["Business Procurement"]["Electric Truck"]

    # Calculate emissions for each category
    hotel_emission = travel_hotel * hotel_factor 
    flight_emission = travel_flight * flight_factor
    airline_emission = airline_km * airline_factor * 1000
    diesel_truck_emission = diesel_truck_km * diesel_truck_factor * 1000
    electric_truck_emission = electric_truck_km * electric_truck_factor * 1000

    # Sum all emissions to get the total
    total_emission = (hotel_emission + flight_emission + airline_emission +
                      diesel_truck_emission + electric_truck_emission)

    # Return detailed emissions and total for further use or display
    return {
        "Hotel Emission": hotel_emission,
        "Flight Emission": flight_emission,
        "Airline Emission": airline_emission,
        "Diesel Truck Emission": diesel_truck_emission,
        "Electric Truck Emission": electric_truck_emission,
        "Total Emission": total_emission
    }

# Example usage (replace these values with actual inputs)
travel_hotel_cost = 10000       # Example cost of hotel stays
travel_flight_cost = 20000      # Example cost of flights
airline_km = 5000               # Example kilometers for airline procurement
diesel_truck_km = 3000          # Example kilometers for diesel truck freight
electric_truck_km = 1000        # Example kilometers for electric truck freight

# Calculate emissions
emissions = calculate_business_emissions(travel_hotel_cost, travel_flight_cost, airline_km, diesel_truck_km, electric_truck_km)
print(emissions)
