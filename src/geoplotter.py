import json
# import shapely
from matplotlib import pyplot as plt
from matplotlib import cm
import numpy as np
from hjortevilt import get_hjortevillt_data
from preprocess_data import pre_process
import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable


"""
Data hentet fra
https://kartkatalog.geonorge.no/metadata/7408853f-eb7d-48dd-bb6c-80c7e80f7392
"""


def PolyArea(points):
    x, y = np.array(points[0]).T

    return 0.5*np.abs(np.dot(x, np.roll(y, 1))-np.dot(y, np.roll(x, 1)))


with open('../data/Kommuner.geojson',
          'r', encoding='utf-8') as file:
    data = json.load(file)

cmap = cm.get_cmap('jet')
kommuner = data['features']


def plot_kommuner(color_dict={}, namedict=None):
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
        if kommunenr not in color_dict and namedict is not None:
            kommunenr = namedict.get(kommune['properties']['navn'])

        color = (cmap(color_dict[kommunenr]) if kommunenr in color_dict
                 else (.8, .8, .8, 1))

        for polygon in sorted(geometry['coordinates'],
                              key=PolyArea, reverse=True)[:3]:
            plt.fill(*zip(*polygon[0]),
                     color=color)
    return fig, ax


if __name__ == '__main__':
    df, names = get_hjortevillt_data()
    namedict = dict((v, k) for k, v in names['kommune_names'].items())
    # df = pre_process(df)
    data = df.fillna(0).groupby(level=0).max()['elg sett antall jegerdager']
    ploitdict = dict(zip(data.index, data.values/data.max()))
    fig, ax = plot_kommuner(ploitdict, namedict)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad=0.05)

    norm = mpl.colors.Normalize(vmin=0, vmax=data.max())
    mpl.colorbar.ColorbarBase(
        cax, cmap=cmap, norm=norm, orientation='vertical')
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    ax.set_title('Jaktdager per kommune')
    plt.show()
