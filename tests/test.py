import sys
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 
from lib import nokaut

xml = nokaut.nokaut(product_name='Sony nex-7',  nokaut_key='a8839b1180ea00fa1cf7c6b74ca01bb5')


