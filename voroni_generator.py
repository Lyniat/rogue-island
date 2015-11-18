import random
import math
import Image
import tiles


def generate_voronoi_diagram(size):
    global start_x, start_y
    start_x = 12
    start_y = 12
    global new_map
    new_map = [[tiles.Tile(0,False)
                for y in range(size)]
               for x in range(size)]
    tilemap = [[0
                for y in range(size)]
                for x in range(size)]

    width = size
    height = size
    num_cells = size/3
    img = Image.new( 'RGB', (width,height), "white")
    pixels = img.load() # create the pixel map
    imgx, imgy = img.size
    nx = []
    ny = []
    nr = []
    ng = []
    nb = []
    nt = []
    for i in range(num_cells):
        rx = random.randrange(imgx)
        ry = random.randrange(imgy)
        nx.append(rx)
        ny.append(ry)

        distance = math.sqrt((rx - width / 2) ** 2 + (ry - height / 2) ** 2)
        if distance > size/2.5:
            nr.append(0)
            ng.append(0)
            nb.append(255)
            nt.append(0)


        elif size/2.5 > distance > size/3.2:
            r = random.randrange(4)
            if r == 0:
                nr.append(0)
                ng.append(0)
                nb.append(255)
                nt.append(0)
            else:
                nr.append(255)
                ng.append(0)
                nb.append(0)
                nt.append(2)
        else:
            nr.append(255)
            ng.append(0)
            nb.append(0)
            nt.append(2)


    for y in range(imgy):
        for x in range(imgx):
            dmin = math.hypot(imgx - 1, imgy - 1)
            j = -1
            for i in range(num_cells):
                d = math.hypot(nx[i] - x, ny[i] - y)
                if d < dmin:
                    dmin = d
                    j = i
            pixels[x,y] = (nt[j]*100, nt[j]*100, nt[j]*100)
            tilemap[x][y] = nt[j]
    img.save('voroni_map.png')

    #add sand in grass
    for x in range(4,size-4):
        for y in range(4,size-4):

            val = tilemap[x][y]

            if val == 0:
                for xs in range(-3,3):
                        for ys in range(-3,3):
                            xt = x+xs
                            yt = y+ys
                            if tilemap[xt][yt] == 2:
                                r = random.randrange(5)
                                if r == 0:
                                    tilemap[xt][yt] = 1
    #add sand in water
    for x in range(9,size-9):
        for y in range(9,size-9):

            val = tilemap[x][y]

            if val == 2:
                for xs in range(-9,9):
                        for ys in range(-9,9):
                            xt = x+xs
                            yt = y+ys
                            if tilemap[xt][yt] == 0:
                                r = random.randrange(5)
                                if r == 0:
                                    tilemap[xt][yt] = 1

    #smooth sand
    for x in range(4,size-4):
        for y in range(4,size-4):

            counter = 0

            if tilemap[x + 1][y] == 0:
                counter+= 1
            if tilemap[x -1][y] == 0:
                counter+= 1
            if tilemap[x][y + 1] == 0:
                counter+= 1
            if tilemap[x][y - 1] == 0:
                counter+= 1

            if counter > 2:
                tilemap[x][y] = 0


    for x in range(size):
        for y in range(size):

            tile_value = tilemap[x][y]

            new_map[x][y].id = tile_value

            if tile_value == 1:
                start_x = x
                start_y = y



    img = Image.new( 'RGB', (size,size), "white")
    pixels = img.load() # create the pixel map

    for x in range(size):    # for every pixel:
        for y in range(size):
            if tilemap[x][y] == 0:
                pixels[x,y] = (0,0,255)
            elif tilemap[x][y] == 1:
                pixels[x,y] = (255,255,0)
            elif tilemap[x][y] == 2:
                pixels[x,y] = (0,255,0)


    img.save('tile_map.png')

    return new_map

def get_start_position():
    return [start_x, start_y]
