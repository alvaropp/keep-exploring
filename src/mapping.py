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


def compute_intensity(pos, pos_list, radius):
    return (norm(np.array(pos_list) - np.array(pos), axis=1) < radius).sum()


def load_all_routes(path):
    all_pos = []
    break_points = []
    for file in glob(join(path, "*.gpx")):
        route = load_gpx(file)
        all_pos.extend(route)
        break_points.append(len(route))
    break_points = np.insert(np.cumsum(break_points), 0, 0)
    return all_pos, break_points


def compute_colours(all_pos):
    colours = [compute_intensity(pos, all_pos, 1e-4) for pos in all_pos]
    colours /= max(colours)
    return colours


def save_all_data(all_pos, colours, path):
    all_pos = np.array(all_pos)
    lat = all_pos[:, 0]
    lon = all_pos[:, 1]
    all_data = pd.DataFrame({"lat": lat, "long": lon, "color": colours})
    all_data.to_csv(join(path, f"{str(date.today())}.csv"))


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
    output_path = "../output/"
    index_path = "../"

    # m = folium.Map(
    #     location=[51.2412, -0.5744],
    #     zoom_start=14,
    #     tiles="https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png",
    #     attr="""&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors
    #             &copy; <a href="https://carto.com/attributions">CARTO</a>""",
    # )

    m = folium.Map(
        location=[51.2412, -0.5744],
        zoom_start=11,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="""Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ""",
    )

    folium.GeoJson(
        "https://findthatpostcode.uk/areas/E07000209.geojson",
        name="geojson",
        style_function=lambda x: {
            "fillColor": "#00000000",
            "color": "black",
            "weight": 3,
        },
    ).add_to(m)

    all_pos, break_points = load_all_routes(route_path)
    colours = compute_colours(all_pos)

    for idx in range(len(break_points) - 1):
        folium.PolyLine(
            all_pos[break_points[idx] : break_points[idx + 1]], color="black", weight=1
        ).add_to(m)

    m.save(join(index_path, "index.html"))
    save_all_data(all_pos, colours, output_path)
    update_html_style_and_title(index_path)
