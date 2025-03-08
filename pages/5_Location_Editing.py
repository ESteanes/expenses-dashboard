from typing import List, Dict

import pandas as pd
import streamlit as st
from geopy.geocoders import Nominatim
from streamlit.delta_generator import DeltaGenerator

import spending

# Initialize geolocator
geolocator = Nominatim(user_agent="streamlit-location-finder")


def add_new_coordinates(
    location: str,
    new_values: List[Dict],
    geolocator_tool: Nominatim,
    ui: DeltaGenerator,
    existing_lat=0.0,
    existing_long=0.0):
    ui.subheader(f"Add Coordinates for: {location}")
    # Free text input for geocoding (but we save the coordinates to `location`)
    search_location = ui.text_input(f"Search Location for {location}", location)
    # Geolocation button
    latitude = f"{location}_lat"
    longitude = f"{location}_lon"
    if latitude not in st.session_state:
        st.session_state[latitude] = existing_lat
    if longitude not in st.session_state:
        st.session_state[longitude] = existing_long
    if ui.button(f"Get Coordinates for {location}"):
        geo_location = geolocator_tool.geocode(search_location)
        if geo_location:
            st.session_state[latitude] = geo_location.latitude
            st.session_state[longitude] = geo_location.longitude
            ui.map(pd.DataFrame({"lat": [geo_location.latitude], "lon": [geo_location.longitude]}))
        else:
            ui.warning(f"Could not find coordinates for {search_location}")
    # Latitude & Longitude inputs (pre-filled with fetched data)
    lat = ui.number_input(
        f"Latitude for {location}",
        format="%.6f",
        value=st.session_state[latitude]
    )
    lon = ui.number_input(
        f"Longitude for {location}",
        format="%.6f",
        value=st.session_state[longitude]
    )
    # Save button
    if ui.button(f"Save {location}"):
        new_values.append({"Location": location, "Latitude": lat, "Longitude": lon})
        ui.success(f"Saved coordinates for {location}!")


def modify_existing_coordinates(
    spending_data: spending.SpendingData,
    location_to_modify: pd.DataFrame,
    index_modifying: int,
    geolocator_tool: Nominatim,
    ui: DeltaGenerator):
    location = location_to_modify['Location'][index_modifying]
    ui.subheader(f"Add Coordinates for: {location}")
    # Free text input for geocoding (but we save the coordinates to `location`)
    search_location = ui.text_input(f"Search Location for {location}", location)
    # Geolocation button
    if "latitude" not in st.session_state:
        st.session_state["latitude"] = None
    if not st.session_state.latitude:
        st.session_state["latitude"] = location_to_modify['Latitude'][index_modifying]
    if "longitude" not in st.session_state:
        st.session_state["longitude"] = None
    if not st.session_state.longitude:
        st.session_state["longitude"] = location_to_modify['Longitude'][index_modifying]
    if ui.button(f"Get Coordinates for {location} - searching for {search_location}"):
        geo_location = geolocator_tool.geocode(search_location)
        if geo_location:
            st.session_state["latitude"] = geo_location.latitude
            st.session_state["longitude"] = geo_location.longitude
            ui.map(pd.DataFrame({"lat": [geo_location.latitude], "lon": [geo_location.longitude]}))
        else:
            ui.warning(f"Could not find coordinates for {search_location}")
    # Latitude & Longitude inputs (pre-filled with fetched data)
    lat = ui.number_input(
        f"Latitude for {location}",
        format="%.6f",
        value=st.session_state["latitude"]
    )
    lon = ui.number_input(
        f"Longitude for {location}",
        format="%.6f",
        value=st.session_state["longitude"]
    )
    # Save button
    if ui.button(f"Update {location}"):
        spending_data.location.loc[index_modifying, ["Location", "Latitude", "Longitude"]] = [location, lat, lon]
        spending_data.save_location()
        spending_data.fetch_spending_data.clear()
        clear_session_state()
        ui.success(f"Saved coordinates for {location}!")
        st.rerun()


def clear_session_state():
    st.session_state.latitude = None
    st.session_state.longitude = None


# Load data
spending_data = spending.SpendingData().fetch_spending_data()
# Find unique locations from spending data that are missing in location_df
existing_locations = set(spending_data.location['Location'])
spending_locations = set(spending_data.spending['Location'].dropna())
missing_locations = spending_locations - existing_locations

st.title("Add Missing Locations with Coordinates")

new_location_entries = []
if not missing_locations:
    st.success("All locations are accounted for! ✅")
else:
    for missing_location in sorted(missing_locations):
        add_new_coordinates(missing_location, new_location_entries, geolocator, st)
    if new_location_entries:
        new_location_df = pd.DataFrame(new_location_entries)
        updated_location_df = pd.concat([spending_data.location, new_location_df], ignore_index=True)
        spending_data.location = updated_location_df
        spending_data.save_location()
        spending_data.fetch_spending_data.clear()
        st.rerun()
st.title("Manage existing locations")
col1, col2 = st.columns(2)
selected_location = col1.dataframe(
    spending_data.location,
    selection_mode="single-row",
    on_select=clear_session_state,
    use_container_width=True)
locations_to_display = spending_data.location
if selected_location.selection.rows:
    locations_to_display = locations_to_display.iloc[[selected_location.selection.rows[0]]]
    modify_existing_coordinates(spending_data, locations_to_display, selected_location.selection.rows[0], geolocator,
                                col2)
col2.map(locations_to_display.rename(columns={"Latitude": "latitude", "Longitude": "longitude"}))
# Save all new locations to the location DataFrame
