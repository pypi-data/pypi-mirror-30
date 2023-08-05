from pgmagick import Pixels, Image

img = Image('X.jpg')
pxs = Pixels(img)
#pxs.sync()
print(pxs, pxs.x(), pxs.y(), pxs.columns(), pxs.rows())
