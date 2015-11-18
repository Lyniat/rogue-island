import libtcodpy as libtcod
import tiles
import math
import Image


def make_map(size):
    tilemap = [[3
                for y in range(size)]
                for x in range(size)]

    tilemap[libtcod.random_get_int(0,1,size -1)][libtcod.random_get_int(0,1,size -1)] = 0
    tilemap[libtcod.random_get_int(0,1,size -1)][libtcod.random_get_int(0,1,size -1)] = 1
    tilemap[libtcod.random_get_int(0,1,size -1)][libtcod.random_get_int(0,1,size -1)] = 2


    #dreckige sandteile entfernen
    for z in range(0,1000):
        actual_tile = 0
        for x in range(1,size-1):
            for y in range(1,size-1):
                if tilemap[x][y] == actual_tile:
                    tile = tilemap[x][y]
                    if tilemap[x + 1][y] == 3:
                        tilemap[x+1][y] = tile
                    if tilemap[x - 1][y] == 3:
                        tilemap[x-y][y]=tile
                    if tilemap[x][y + 1] == 3:
                        tilemap[x][y+1] = tile
                    if tilemap[x][y - 1] == 3:
                        tilemap[x][y-1] = tile
                    actual_tile += 1
                    if actual_tile >= 3:
                        actual_tile = 0

        for y in range(1,size-1):
            for x in range(1,size-1):
                if tilemap[x][y] == actual_tile:
                    tile = tilemap[x][y]
                    if tilemap[x + 1][y] == 3:
                        tilemap[x+1][y] = tile
                    if tilemap[x - 1][y] == 3:
                        tilemap[x-y][y]=tile
                    if tilemap[x][y + 1] == 3:
                        tilemap[x][y+1] = tile
                    if tilemap[x][y - 1] == 3:
                        tilemap[x][y-1] = tile
                    actual_tile += 1
                    if actual_tile >= 3:
                        actual_tile = 0


###################
#Print tiles to png
###################

    img = Image.new( 'RGB', (size,size), "red")
    pixels = img.load() # create the pixel map

    for x in range(size):    # for every pixel:
        for y in range(size):
            if tilemap[x][y] == 0:
                pixels[x,y] = (0,0,255)
            elif tilemap[x][y] == 1:
                pixels[x,y] = (255,255,0)
            elif tilemap[x][y] == 2:
                pixels[x,y] = (0,255,0)


    img.save('biome_map.png')
