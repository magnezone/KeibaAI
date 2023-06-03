import schedule
import time
from FTPtest import *
import pandas as pd

root = os.path.dirname(os.path.abspath(__file__))
table = pd.read_csv(root + "\\Dataset\\重賞データ.csv")

for i in table.index:
    print(i)