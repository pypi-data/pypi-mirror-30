import sys
sys.path.insert(0, '..')
from pgmagick import Image, FilterTypes
im = Image('X.jpg')
px = im.getPixels(1, 1, 10, 10)
#print(px.opacity)
