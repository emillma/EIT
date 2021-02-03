from matplotlib import cm
from matplotlib import pyplot as plt
import json
import hjortevilt
import numpy as np


def plot_kommuner(color_dict={}):
    with open('../data/kommuner_geojson/Kommuner.geojson',
              'r', encoding='utf-8') as file:
        data = json.load(file)

    cmap = cm.get_cmap('jet')
    kommuner = data['features']
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    for kommune in kommuner:
        geometry = kommune['geometry']
        kommunenr = str(kommune['properties']['kommunenummer'])
        color = (cmap(color_dict[kommunenr]) if kommunenr in color_dict
                 else (.8, .8, .8, 1))
        for polygon in geometry['coordinates']:
            plt.fill(*zip(*polygon[0]),
                     color=color)

    return fig, ax


if __name__ == '__main__':
    df = hjortevilt.get_hjortevilt_dataframe()

    pivoted = df.pivot(index='kommunenr',
                       columns='jaktår',
                       values='elg felt antall jegerdager',
                       )

    kommuner = pivoted.index
    dager = np.mean(pivoted.values, axis=1)
    dager = dager/np.amax(dager)

    mydict = dict(zip([str(i) for i in kommuner], dager))
    plot_kommuner(mydict)
    plt.show()
