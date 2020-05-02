from datetime import date
from glob import glob
from os.path import join

import branca.colormap as cm
import gpxpy
import folium
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from folium.plugins import HeatMap
from scipy.linalg import norm


def load_gpx(path):
    with open(path, "r") as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append(tuple([point.latitude, point.longitude]))
        return points


def generate_map(route_path, output_path):
    m = folium.Map(
        location=[51.2412, -0.5744],
        zoom_start=11,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="""Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ""",
    )

    # Add Guildford Borough
    folium.GeoJson(
        "https://findthatpostcode.uk/areas/E07000209.geojson",
        name="geojson",
        style_function=lambda x: {
            "fillColor": "#00000000",
            "color": "black",
            "weight": 3,
        },
    ).add_to(m)

    # Add each route
    all_routes = sorted(glob(join(route_path, "*.gpx")))
    for route in all_routes:
        points = load_gpx(route)
        folium.PolyLine(points, color="black", weight=1).add_to(m)

    # Save and add heading to map
    m.save(join(output_path, "index.html"))
    update_html_style_and_title(output_path)


def update_html_style_and_title(path):
    with open(join(path, "index.html"), "r") as f:
        soup = BeautifulSoup(f, "html.parser")

    new_div = soup.new_tag("div")
    new_div.string = "Keep Exploring."

    new_style = soup.new_tag("style")

    new_style.string = (
        f"#{soup.find('div', {'class': 'folium-map'})['id']}"
        + """{
                position: relative;
                width: 100.0%;
                height: 80.0%;
                left: 0.0%;
                top: 0.0%;
            }
        """
    )
    soup.head.append(new_style)

    soup.head.style.append(
        "body {background-color: #efefef; color: black; font-size: 7vw; text-align: center;}"
    )

    new_div = soup.new_tag("div")
    new_div.string = "Keep Exploring."
    soup.body.insert(0, new_div)

    with open(join(path, "index.html"), "w") as file:
        file.write(str(soup))


if __name__ == "__main__":
    route_path = "../gpx/"
    output_path = "../"
    generate_map(route_path, output_path)
