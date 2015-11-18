import libtcodpy as libtcod
import tiles
import math
import Image


def make_map(size):
    global start_x, start_y
    global new_map
    new_map = [[tiles.Tile(0,False)
                for y in range(size)]
               for x in range(size)]
    heightmap = [[0
                  for y in range(size)]
                 for x in range(size)]
    tilemap = [[0
                for y in range(size)]
                for x in range(size)]

    random_x = libtcod.random_get_int(0,0,99999999)
    random_y = random_x / 2

    for x in range(size):
        for y in range(size):

            # create map
            height_value = math.sqrt((x - size / 2) ** 2 + (y - size / 2) ** 2)

            # strand zerfransen klein
            height_value -= math.fabs(math.sin((x + random_x) / 3) * 2)

            height_value -= math.fabs(math.cos((y + random_y) / 4) * 2)

            #invert heightmap
            height_value = size/1.1 - height_value

            print random_x

            # strand zerfransen gross
            height_value -= math.sin((x + random_x)/9) * 4

            height_value -= math.sin((y + random_y**1.2) / 10) * 4


            heightmap[x][y] = height_value


    #extra bay
    for x in range(int(size/2.4)):
        for y in range(int(size/2.4)):

            height_value = math.sqrt((x - size / 4.8) ** 2 + (y - size / 4.8) ** 2)

            height_value = size/5.2 - height_value

            if height_value < 0:
                height_value = 0

            heightmap[x][y] -= height_value*1.5

    #extra island
    for x in range(size/3):
        for y in range(size/3):

            height_value = math.sqrt((x - size / 6) ** 2 + (y - size / 6) ** 2)

            height_value = size/7 - height_value

            if height_value < 0:
                height_value = 0

            heightmap[x][y] += height_value*3

    modulo_2 = random_x % 2

    modulo_5 = random_x % 5

    #schlucht 1
    for y in range(size/(2 + modulo_2)):
        y_size = y/14
        if y_size < 0:
            y_size = 0
        for x in range(-7 + y_size ,7 - y_size):
            extra_x = int(math.sin(y/5)*4)+int(math.cos(y/11)*4)
            heightmap[size/(2 + modulo_5) - x + extra_x][size - y -1] = 0#-= (8 - math.fabs(x))*2;

    #schlucht 2
    for y in range(size/(2+modulo_2)):
        y_size = y/14
        if y_size < 0:
            y_size = 0
        for x in range(-7 + y_size ,7 - y_size):
            extra_x = int(math.sin(y/5)*4)+int(math.cos(y/11)*4)
            heightmap[size - y -1][size/(2 + modulo_5) - x + extra_x] = 0#-= (8 - math.fabs(x))*2;


###################
#Print height to png
###################

    img = Image.new( 'RGB', (size,size), "white")
    pixels = img.load() # create the pixel map

    for x in range(size):    # for every pixel:
        for y in range(size):
            pixels[x,y] = (int(heightmap[x][y]),int(heightmap[x][y])/2,255 - int(heightmap[x][y]))

    img.save('height_map.png')

###################
#Calculate tiles
###################

    for x in range(size):
        for y in range(size):

            height_value = heightmap[x][y]

            if height_value < size / 2.2:
                tilemap[x][y] = 0
            elif size /2.2 <= height_value < size/2.1:
                tilemap[x][y] = 1
            else:
                tilemap[x][y] = 2


    #dreckige sandteile entfernen
    for x in range(1,size-1):
        for y in range(1,size-1):
            counter = 0
            if tilemap[x][y] == 1:
                if tilemap[x + 1][y] == 0:
                    counter += 1
                if tilemap[x - 1][y] == 0:
                    counter += 1
                if tilemap[x][y + 1] == 0:
                    counter += 1
                if tilemap[x][y + 1] == 0:
                    counter += 1

                if counter >= 3:
                    tilemap[x][y] = 0



###################
#Print tiles to png
###################

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



    for x in range(size):
        for y in range(size):

            tile_value = tilemap[x][y]

            new_map[x][y].id = tile_value

            if tile_value == 2:
                start_x = x
                start_y = y

    return new_map


def get_start_position():
    return [start_x, start_y]
