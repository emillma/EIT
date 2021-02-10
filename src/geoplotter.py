import json
# import shapely
from matplotlib import pyplot as plt
from matplotlib import cm
import numpy as np


with open('../data/kommuner_geojson/Kommuner.geojson',
          'r', encoding='utf-8') as file:
    data = json.load(file)

cmap = cm.get_cmap('summer')
kommuner = data['features']


def plot_kommuner(color_dict={}):
    """
    Plotter fargekodet kommunekart.
    Keys = kommunenummer
    Items = float mellom 0 og 1
    """
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    for kommune in kommuner:
        geometry = kommune['geometry']
        kommunenr = kommune['properties']['kommunenummer']
        color = (cmap(color_dict[kommunenr]) if kommunenr in color_dict
                 else (.8, .8, .8, 1))
        for polygon in geometry['coordinates']:
            # plt.fill(*zip(*polygon), color=cmap(np.random.random()))
            plt.fill(*zip(*polygon[0]),
                     color=color)

    return fig, ax
