## Keep Exploring

![example](https://user-images.githubusercontent.com/4785303/82208753-fb66ee80-9903-11ea-8800-af0aa7a3c120.gif)

This repository powers the following website where I keep track of all the streets I have walked and cycled around where I live: http://alvarop.me/keep-exploring/

This project was inspired by [Matt Green](https://imjustwalkin.com/) and [Davis Vilums](http://davis.vilums.me/all-the-streets/#) who walked every street in New York and cycled every street in London, respectively.

You can use this repo as a template for keeping track of your own explorations.

## Instructions

1. Choose your favourite GPS tracking website (Komoot, Strava, etc.)
2. Keep track of your routes using your choice from (1). Although you don't need to use a third-party website if you have a dedicated GPS unit, it does help a lot producing a neat map, given that the website will _map match_ your routes for you (that is, it will snap your wobbly GPS signal to known ways producing much cleaner route lines in your map).
3. Download the .gpx files of all your routes and put them in the `gpx/` folder.
4. Run `src/mapping.py` to produce an `index.html` file which contains the map and all your routes.
  * If you want to show the boundary of the area that your want to explore, find a suitable geoJSON file that describes it (these are easy to find online) and add it to `src/mapping.py`.
  * You can change the theme of your map—there is a lot of [free options](https://leaflet-extras.github.io/leaflet-providers/preview/) to choose from.
  * You can change the look of your `index.html` website as you please
5. This website with the map can be easily hosted in GitHub pages or elsewhere.
6. Go explore!


## Make the route progress animation

This can be done with `exploration/test_map_animation.ipynb`.

## Producing a heat map

This is a prototype and doesn't work 100% as it should, but it does produce interesting—and relatively accurate—plots. Have a play with it in `exploration/test_heat_map.ipynb`.
