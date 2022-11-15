import folium

def create_map_html(start_coords):
    m = folium.Map(location=start_coords, zoom_start=14)
    return m._repr_html_()