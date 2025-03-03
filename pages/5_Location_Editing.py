import pandas as pd
import streamlit as st
from geopy.geocoders import Nominatim

import utils
from utils import save_data, SPENDING_PATH

# Initialize geolocator
geolocator = Nominatim(user_agent="streamlit-location-finder")

# Load data
spending_data = utils.fetch_spending_data()
# Find unique locations from spending data that are missing in location_df
existing_locations = set(spending_data.location['Location'])
spending_locations = set(spending_data.spending['Location'].dropna())
missing_locations = spending_locations - existing_locations

st.title("Add Missing Locations with Coordinates")

if not missing_locations:
    st.success("All locations are accounted for! ✅")
else:
    new_location_entries = []
    for location in sorted(missing_locations):
        st.subheader(f"Add Coordinates for: {location}")

        # Free text input for geocoding (but we save the coordinates to `location`)
        search_location = st.text_input(f"Search Location for {location}", location)

        # Geolocation button
        if st.button(f"Get Coordinates for {location}"):
            geo_location = geolocator.geocode(search_location)
            if geo_location:
                st.session_state[f"{location}_lat"] = geo_location.latitude
                st.session_state[f"{location}_lon"] = geo_location.longitude
                st.map(pd.DataFrame({"lat": [geo_location.latitude], "lon": [geo_location.longitude]}))
            else:
                st.warning(f"Could not find coordinates for {search_location}")

        # Latitude & Longitude inputs (pre-filled with fetched data)
        lat = st.number_input(
            f"Latitude for {location}",
            format="%.6f",
            value=st.session_state.get(f"{location}_lat", 0.0)
        )
        lon = st.number_input(
            f"Longitude for {location}",
            format="%.6f",
            value=st.session_state.get(f"{location}_lon", 0.0)
        )

        # Save button
        if st.button(f"Save {location}"):
            new_location_entries.append({"Location": location, "Latitude": lat, "Longitude": lon})
            st.success(f"Saved coordinates for {location}!")

    # Save all new locations to the location DataFrame
    if new_location_entries:
        new_location_df = pd.DataFrame(new_location_entries)
        updated_location_df = pd.concat([spending_data.location, new_location_df], ignore_index=True)
        save_data(updated_location_df, SPENDING_PATH, "Location")
        utils.fetch_spending_data.clear()
        st.rerun()
