from datetime import date
from glob import glob

import branca.colormap as cm
import gpxpy
import folium
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from folium.plugins import HeatMap
from scipy.linalg import norm


def load_gpx(file_path):
    with open(file_path, "r") as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append(tuple([point.latitude, point.longitude]))
        return points


def compute_intensity(pos, pos_list, radius):
    return (norm(np.array(pos_list) - np.array(pos), axis=1) < radius).sum()


def load_all_routes():
    all_pos = []
    break_points = []
    for file in glob("gpx/*.gpx"):
        route = load_gpx(file)
        all_pos.extend(route)
        break_points.append(len(route))
    break_points = np.insert(np.cumsum(break_points), 0, 0)
    return all_pos, break_points


def compute_colours(all_pos):
    colours = [compute_intensity(pos, all_pos, 1e-4) for pos in all_pos]
    colours /= max(colours)
    return colours


def save_all_data(all_pos, colours):
    all_pos = np.array(all_pos)
    lat = all_pos[:, 0]
    lon = all_pos[:, 1]
    all_data = pd.DataFrame({"lat": lat, "long": lon, "color": colours})
    all_data.to_csv(f"output/{str(date.today())}.csv")


def update_html_style_and_title():

    with open("index.html", "r") as f:
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
        "body {background-color: #090909; color: white; font-size: 7vw; text-align: center;}"
    )

    new_div = soup.new_tag("div")
    new_div.string = "Keep Exploring."
    soup.body.insert(0, new_div)

    with open("index.html", "w") as file:
        file.write(str(soup))


m = folium.Map(
    location=[51.2412, -0.5744],
    zoom_start=14,
    tiles="https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png",
    attr="""&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors
            &copy; <a href="https://carto.com/attributions">CARTO</a>""",
)

all_pos, break_points = load_all_routes()
colours = compute_colours(all_pos)

print(break_points)

for idx in range(len(break_points) - 1):
    print(idx)
    print(all_pos[break_points[idx] : break_points[idx + 1]])
    folium.ColorLine(
        all_pos[break_points[idx] : break_points[idx + 1]],
        colors=colours,
        colormap=["white", "red"],
        weight=2,
    ).add_to(m)

m.save("index.html")
save_all_data(all_pos, colours)
update_html_style_and_title()
