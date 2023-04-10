import schedule
import time
from FTPtest import *

def a():
    raise Exception

try:
    a()
except:
    print("hi")
