import pandas as pd
import matplotlib.pyplot as plt

a = pd.DataFrame({"name":[1,2],"nic":[2,3]})
a.plot.bar("name","nic")
plt.show()