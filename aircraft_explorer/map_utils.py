import folium


def create_map(lat, lon, aircraft_data):

    my_map = folium.Map(
        location=[lat, lon],
        zoom_start=7
    )

    # City marker
    folium.Marker(
        [lat, lon],
        popup="Selected City",
        tooltip="City"
    ).add_to(my_map)

    # Aircraft markers
    for aircraft in aircraft_data:

        if aircraft["latitude"] and aircraft["longitude"]:

            popup_text = f"""
            Callsign: {aircraft['callsign']}<br>
            Altitude: {aircraft['altitude']}<br>
            Velocity: {aircraft['velocity']}
            """

            folium.Marker(
                [aircraft["latitude"], aircraft["longitude"]],
                popup=popup_text,
                icon=folium.Icon(color="red", icon="plane")
            ).add_to(my_map)

    return my_map._repr_html_()