def calculate_business_emissions(travel_hotel, travel_flight, airline_km, diesel_truck_km, electric_truck_km):
    hotel_factor = business_travel_procurement_factors["Business Travel"]["Business Travel-Hotel"]
    flight_factor = business_travel_procurement_factors["Business Travel"]["Business Travel - Flight"]
    airline_factor = business_travel_procurement_factors["Business Procurement"]["Airline"]
    diesel_truck_factor = business_travel_procurement_factors["Business Procurement"]["Diesel Truck"]
    electric_truck_factor = business_travel_procurement_factors["Business Procurement"]["Electric Truck"]

    # Calculate emissions for each category
    hotel_emission = travel_hotel * hotel_factor if travel_hotel else 0
    flight_emission = travel_flight * flight_factor if travel_flight else 0
    airline_emission = airline_km * airline_factor * 1000 if airline_km else 0
    diesel_truck_emission = diesel_truck_km * diesel_truck_factor * 1000 if diesel_truck_km else 0
    electric_truck_emission = electric_truck_km * electric_truck_factor * 1000 if electric_truck_km else 0

    # Total emissions
    total_emission_travel = hotel_emission + flight_emission
    total_emission_procurement = airline_emission + diesel_truck_emission + electric_truck_emission

    # Return individual emissions and totals for each category
    return {
        "Business Travel": {
            "Hotel Emission": hotel_emission,
            "Flight Emission": flight_emission,
            "Total Emission": total_emission_travel
        },
        "Business Procurement": {
            "Airline Emission": airline_emission,
            "Diesel Truck Emission": diesel_truck_emission,
            "Electric Truck Emission": electric_truck_emission,
            "Total Emission": total_emission_procurement
        }
    }


