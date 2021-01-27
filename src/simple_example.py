from matplotlib import pyplot as plt
import numpy as np
import hjortevilt
import pandas as pd
import sys
df = hjortevilt.get_hjortevilt_dataframe()

dager = df.loc[:, 'elg sett antall jegerdager']
sett = df.loc[:, 'elg sett sum sette elg']
felt = df.loc[:, 'elg felt sum felte']
jaktår = df.loc[:, 'jaktår']
plt.scatter(dager, sett, alpha=0.1)
plt.show()
