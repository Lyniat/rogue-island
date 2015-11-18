import random
import math
import Image


def generate_voronoi_diagram(size):
    width = size
    height = size
    num_cells = size/2
    img = Image.new( 'RGB', (width,height), "white")
    pixels = img.load() # create the pixel map
    imgx, imgy = img.size
    nx = []
    ny = []
    nr = []
    ng = []
    nb = []
    for i in range(num_cells):
        rx = random.randrange(imgx)
        ry = random.randrange(imgy)
        nx.append(rx)
        ny.append(ry)

        distance = math.sqrt((rx - width / 2) ** 2 + (ry - height / 2) ** 2)
        if size/2.0 > distance > size/2.5:
        #if 64 < rx < width -64  and 64 < ry < width -64:
            rb = random.randrange(5)
            if rb == 1:
                nr.append(0)
                ng.append(0)
                nb.append(255)
            else:
                nr.append(255)
                ng.append(255)
                nb.append(0)
        elif distance >= size/2.0:
                nr.append(0)
                ng.append(0)
                nb.append(255)

        else:
            nr.append(255)
            ng.append(0)
            nb.append(0)

    for y in range(imgy):
        for x in range(imgx):
            dmin = math.hypot(imgx - 1, imgy - 1)
            j = -1
            for i in range(num_cells):
                d = math.hypot(nx[i] - x, ny[i] - y)
                if d < dmin:
                    dmin = d
                    j = i
            #putpixel((x, y), (nr[j], ng[j], nb[j]))
            pixels[x,y] = (nr[j], ng[j], nb[j])
    img.save('voroni_map.png')
