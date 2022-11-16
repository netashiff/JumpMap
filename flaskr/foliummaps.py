import folium
from pymongo import MongoClient
from flaskr.auth import USERNAME
client = MongoClient('mongodb://localhost:27017')

JumpMapDB = client['JumpMap']

def printUsername():
    print(USERNAME)
def create_map_html(start_coords):
    printUsername()
    m = folium.Map(location=start_coords, zoom_start=14)
    return m._repr_html_()