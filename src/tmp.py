from hjortevilt import get_hjortevillt_data
from matplotlib import pyplot as plt

df, _ = get_hjortevillt_data()

x = df['elg sett antall jegerdager']
y = df['elg sett sum sette elg']

plt.scatter(x, y)
