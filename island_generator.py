import random
import math
import Image
import tiles


def update_info(text, libtcod):
    libtcod.console_print(0, 1, 1, text)

    libtcod.console_flush()


# generate voroni diagramm
def generate_voronoi_diagram(size, libtcod):
    global start_x, start_y
    start_x = 12
    start_y = 12
    global new_map
    new_map = [[tiles.Tile(0, False)
                for y in range(size)]
               for x in range(size)]
    tilemap = [[0
                for y in range(size)]
               for x in range(size)]

    num_cells = size / 3
    nx = []
    ny = []
    nt = []
    for i in range(num_cells):
        rx = random.randrange(size)
        ry = random.randrange(size)
        nx.append(rx)
        ny.append(ry)

        distance = math.sqrt((rx - size / 2) ** 2 + (ry - size / 2) ** 2)
        if distance > size / 2.5:
            nt.append(0)


        elif size / 2.5 > distance > size / 3.2:
            r = random.randrange(4)
            if r == 0:
                nt.append(0)
            else:
                nt.append(2)
        else:
            nt.append(2)

    for y in range(size):
        for x in range(size):
            dmin = math.hypot(size - 1, size - 1)
            j = -1
            for i in range(num_cells):
                d = math.hypot(nx[i] - x, ny[i] - y)
                if d < dmin:
                    dmin = d
                    j = i
            tilemap[x][y] = nt[j]

        update_text = "generating terrain: " + str(((y * 1.0) / size) * 100) + "%"

        print(update_text)

        # update_info("test",libtcod)

    #prevent island from colliding with wall
    for y in range(size):
        for x in range(size):
            dist = math.sqrt((size/2 -x)**2+(size/2 -y)**2)
            if dist > (size/2 - 6):
                tilemap[x][y] = 0


    # add sand in grass
    for x in range(4, size - 4):
        for y in range(4, size - 4):

            val = tilemap[x][y]

            if val == 0:
                for xs in range(-3, 3):
                    for ys in range(-3, 3):
                        xt = x + xs
                        yt = y + ys
                        if tilemap[xt][yt] == 2:
                            r = random.randrange(5)
                            if r == 0:
                                tilemap[xt][yt] = 1

        update_text = "adding sand: " + str(((x * 1.0) / (size - 9)) * 100) + "%"

        print(update_text)

    # add sand in water
    for x in range(9, size - 9):
        for y in range(9, size - 9):

            val = tilemap[x][y]

            if val == 2:
                for xs in range(-9, 9):
                    for ys in range(-9, 9):
                        xt = x + xs
                        yt = y + ys
                        if tilemap[xt][yt] == 0:
                            r = random.randrange(5)
                            if r == 0:
                                tilemap[xt][yt] = 1
        update_text = "removing water: " + str(((x * 1.0) / (size - 19)) * 100) + "%"

        print(update_text)

    # smooth sand
    for x in range(4, size - 4):
        for y in range(4, size - 4):

            counter = 0

            if tilemap[x + 1][y] == 0:
                counter += 1
            if tilemap[x - 1][y] == 0:
                counter += 1
            if tilemap[x][y + 1] == 0:
                counter += 1
            if tilemap[x][y - 1] == 0:
                counter += 1

            if counter > 2:
                tilemap[x][y] = 0
        update_text = "smoothing sand: " + str(((x * 1.0) / (size - 9)) * 100) + "%"

        print(update_text)

    for i in range(5):
        x = random.randrange(size / 3, size - size / 3)
        y = random.randrange(size / 3, size - size / 3)
        # create river
        while 1 == 1:
            test_x_pos = 0
            test_y_pos = 0

            test_x_neg = 0
            test_y_neg = 0

            test_x = 0
            test_y = 0

            while not tilemap[x + test_x_pos][y] == 0:
                test_x_pos += 1
            print("xpos: " + str(test_x_pos))

            while not tilemap[x][y + test_y_pos] == 0:
                test_y_pos += 1
            print("ypos: " + str(test_y_pos))

            while not tilemap[x + test_x_neg][y] == 0:
                test_x_neg -= 1
            print("xneg: " + str(test_x_neg))

            while not tilemap[x][y + test_y_neg] == 0:
                test_y_neg -= 1
            print("yneg: " + str(test_y_neg))

            #r = random.randrange(0, 2)
            #if r == 1:
                #test_x_neg, test_y_pos = test_y_pos, test_x_neg
                #test_x_pos, test_y_neg = test_x_neg, test_y_pos

            if test_x_pos < math.fabs(test_x_neg):
                test_x = test_x_pos
                print("xpos < xneg ==> xpos")
            else:
                test_x = test_x_neg
                print("xneg < xpos==> xneg")

            if test_y_pos < math.fabs(test_y_neg):
                test_y = test_y_pos
                print("ypos < yneg ==> ypos")
            else:
                test_y = test_y_neg
                print("yneg < ypos==> yneg")

            if math.fabs(test_x) < math.fabs(test_y):
                x += test_x / math.fabs(test_x)
                print("x < y ==> x")
            else:
                y += test_y / math.fabs(test_y)
                print("y < x ==> y")

            x += random.randrange(-1,1)
            y += random.randrange(-1,1)

            x = int(x)
            y = int(y)

            print(x)
            print(y)

            if tilemap[x][y]== 0:
                break

            tilemap[x + 1][y] = 3
            tilemap[x - 1][y] = 3
            tilemap[x][y + 1] = 3
            tilemap[x][y - 1] = 3
            tilemap[x][y] = 3

    for x in range(size):
        for y in range(size):

            tile_value = tilemap[x][y]

            new_map[x][y].id = tile_value

            if tile_value == 1:
                start_x = x
                start_y = y

    img = Image.new('RGB', (size, size), "white")
    pixels = img.load()  # create the pixel map

    for x in range(size):  # for every pixel:
        for y in range(size):
            if tilemap[x][y] == 0:
                pixels[x, y] = (0, 0, 255)
            elif tilemap[x][y] == 1:
                pixels[x, y] = (255, 255, 0)
            elif tilemap[x][y] == 2:
                pixels[x, y] = (0, 255, 0)
            elif tilemap[x][y] == 3:
                pixels[x, y] = (63, 63, 255)

    img.save('tile_map.png')

    return new_map


def get_start_position():
    return [start_x, start_y]
