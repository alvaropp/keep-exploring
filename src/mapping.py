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
from shapely.geometry import Point, Polygon


def load_gpx(path):
    with open(path, "r") as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append(tuple([point.latitude, point.longitude]))
        return points


def compute_segments_in_borough(all_points, borough_polygon):
    points_in_borough = [
        True if borough_polygon.contains(Point(point)) else False
        for point in all_points
    ]

    route_idxs = []
    start_idx = 0
    end_idx = 0
    for idx, in_borough in enumerate(points_in_borough[1:]):
        if in_borough:
            if start_idx < 0:
                start_idx = idx + 1
                end_idx = idx + 1
            else:
                end_idx += 1
        else:
            if start_idx >= 0:
                route_idxs.append([start_idx, end_idx + 1])
            start_idx = -1
    route_idxs.append([start_idx, end_idx + 1])

    routes = [all_points[route_idx[0] : route_idx[1]] for route_idx in route_idxs]
    return routes


def generate_map(route_path, output_path):
    m = folium.Map(
        location=[51.2412, -0.5744],
        zoom_start=11,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="""Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ""",
    )

    # Add Guildford Borough
    borough_json = folium.GeoJson(
        "https://findthatpostcode.uk/areas/E07000209.geojson",
        name="geojson",
        style_function=lambda x: {
            "fillColor": "#00000000",
            "color": "black",
            "weight": 3,
        },
    )
    borough_json.add_to(m)

    borough_polygon = Polygon(
        np.array(borough_json.data["features"][0]["geometry"]["coordinates"][0])[:, ::-1]
    )

    # Add each route
    all_routes = sorted(glob(join(route_path, "*.gpx")))
    for route in all_routes:
        points = load_gpx(route)
        segments = compute_segments_in_borough(points, borough_polygon)
        for segment in segments:
            folium.PolyLine(segment, color="black", weight=2).add_to(m)

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
