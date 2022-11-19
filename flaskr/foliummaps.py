import folium
from pymongo import MongoClient
from flaskr.auth import USERNAME
from flaskr.auth import *
client = MongoClient('mongodb://localhost:27017')

JumpMapDB = client['JumpMap']

def printUsername():
    print(USERNAME)

def create_points(map):
    logged_in = get_logged_in_user()
    user_collection = JumpMapDB[str(logged_in)]
    for document in user_collection.find():
        latitude = document["Latitude"]
        longtitude = document["Longtitude"]
        title = document["Name"]
        color = document["Color"]
        folium.Marker(location=[str(latitude),str(longtitude)], popup = str(title)).add_to(map)
def create_map_html(start_coords):
    printUsername()
    m = folium.Map(location=start_coords, zoom_start=14)
    create_points(m)
    return m._repr_html_()