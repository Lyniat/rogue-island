import random
import math
import Image
import tiles
import tmx

# generate voroni diagramm
def generate_voronoi_diagram(size, info_text, map):

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
        elif size / 3.2 > distance > size/4.2:
            nt.append(4)
        elif size/4.2 > distance:
            nt.append(5)
        else:
            nt.append(2)

    for y in range(size):
        for x in range(size):
            dmin = math.hypot(size - 1, size - 1)
            j = -1
            for i in range(num_cells):
                d = math.fabs(nx[i] - x) + math.fabs(ny[i] - y)#math.hypot(nx[i] - x, ny[i] - y)
                if d < dmin:
                    dmin = d
                    j = i
            tilemap[x][y] = nt[j]

        update_text = "generating terrain: " + str(to_percent((y * 1.0) / size)) + " percent"
        info_text.set(update_text)

    #prevent island from colliding with wall
    for y in range(size):
        for x in range(size):
            dist = math.sqrt((size/2 -x)**2+(size/2 -y)**2)
            if dist > (size/2 - 12):
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
                        if tilemap[xt][yt] == 2 or tilemap[xt][yt] == 4 or tilemap[xt][yt] == 5:
                            r = random.randrange(5)
                            if r == 0:
                                tilemap[xt][yt] = 1

        update_text = "adding sand: " + str(to_percent((x * 1.0) / (size - 9))) + " percent"
        info_text.set(update_text)

    # add sand in water
    for x in range(9, size - 9):
        for y in range(9, size - 9):

            val = tilemap[x][y]

            if val == 2 or val == 4 or val == 5:
                for xs in range(-9, 9):
                    for ys in range(-9, 9):
                        xt = x + xs
                        yt = y + ys
                        if tilemap[xt][yt] == 0:
                            r = random.randrange(5)
                            if r == 0:
                                tilemap[xt][yt] = 1

        update_text = "removing water: " + str(to_percent((x * 1.0) / (size - 19))) + " percent"
        info_text.set(update_text)

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
        update_text = "smoothing sand: " + str(to_percent((x * 1.0) / (size - 9))) + " percent"
        info_text.set(update_text)

    # create rivers
    river_num = size/128;
    for i in range(river_num):
        x = random.randrange(size / 3, size - size / 3)
        y = random.randrange(size / 3, size - size / 3)

        #create lakes for rivers
        lake_size = 4
        for m in range(-lake_size,lake_size):
            for n in range(-lake_size,lake_size):
                distance = math.sqrt(m**2+n**2);
                if distance <= lake_size:
                    tilemap[x+m][y+n] = 3;

        while 1 == 1:
            test_x_pos = 0
            test_y_pos = 0

            test_x_neg = 0
            test_y_neg = 0

            while not tilemap[x + test_x_pos][y] == 0:
                test_x_pos += 1

            while not tilemap[x][y + test_y_pos] == 0:
                test_y_pos += 1

            while not tilemap[x + test_x_neg][y] == 0:
                test_x_neg -= 1

            while not tilemap[x][y + test_y_neg] == 0:
                test_y_neg -= 1

            if test_x_pos < math.fabs(test_x_neg):
                test_x = test_x_pos
            else:
                test_x = test_x_neg

            if test_y_pos < math.fabs(test_y_neg):
                test_y = test_y_pos
            else:
                test_y = test_y_neg

            if math.fabs(test_x) < math.fabs(test_y):
                x += test_x / math.fabs(test_x)
            else:
                y += test_y / math.fabs(test_y)

            x += random.randrange(-1,1)
            y += random.randrange(-1,1)

            x = int(x)
            y = int(y)
            if tilemap[x][y]== 0:
                break

            tilemap[x + 1][y] = 3
            tilemap[x - 1][y] = 3
            tilemap[x][y + 1] = 3
            tilemap[x][y - 1] = 3
            tilemap[x][y] = 3

            update_text = "creating river: " + str(to_percent((i+1)/river_num)) + " percent"
            info_text.set(update_text)


    #image for tilemap
    img = Image.new('RGB', (size, size), "white")
    pixels = img.load()  # create the pixel map

    for x in range(size):  # for every pixel:
        for y in range(size):
            if tilemap[x][y] == 0:
                pixels[x, y] = (0, 0, 255)
            elif tilemap[x][y] == 1:
                pixels[x, y] = (255, 255, 0)
            elif tilemap[x][y] == 2:
                r = random.randrange(30);
                if r == 0:
                    pixels[x, y] = (0, 0, 0)
                else:
                    pixels[x, y] = (0, 255, 0)
            elif tilemap[x][y] == 3:
                pixels[x, y] = (63, 63, 255)
            elif tilemap[x][y] == 4:
                r = random.randrange(16);
                if r == 0:
                    pixels[x, y] = (0, 0, 0)
                else:
                    pixels[x, y] = (0, 200, 0)
            elif tilemap[x][y] == 5:
                r = random.randrange(8);
                if r == 0:
                    pixels[x, y] = (0, 0, 0)
                else:
                    pixels[x, y] = (0, 127, 0)


    img.save('tile_map.png')

    update_text = "terrain generation finished"
    info_text.set(update_text)

    map = new_map

    update_text = "generating biomes"
    info_text.set(update_text)
#def generate_biomes(size):
    biomemap = [[0
                for y in range(size)]
               for x in range(size)]

    nx = []
    ny = []
    nt = []
    biome_id = 0
    for i in range(size/12):
        rx = random.randrange(size/2)
        ry = random.randrange(size/2)

        nx.append(rx)
        ny.append(ry)

        nt.append(biome_id)

        biome_id += 1

        if biome_id > 4:
            biome_id = -1

    for y in range(size/2):
        for x in range(size/2):
            dmin = math.hypot(size - 1, size - 1)
            j = -1
            for i in range(size/12):
                d = math.hypot(nx[i] - x, ny[i] - y)
                if d < dmin:
                    dmin = d
                    j = i
            biomemap[x][y] = nt[j]

    #image for biomemap
    img = Image.new('RGB', (size/2, size/2), "white")
    pixels = img.load()  # create the pixel map

    for x in range(size/2):  # for every pixel:
        for y in range(size/2):
            if biomemap[x][y] <= 0: #normal
               pixels[x, y]=(255,255,255)
            if biomemap[x][y] == 1: #village
                pixels[x, y]=(255,255,0)
            if biomemap[x][y] == 2: #mushroom
                pixels[x, y]=(255,0,255)
            if biomemap[x][y] == 3: #unholy
                pixels[x, y]=(128,0,255)
            if biomemap[x][y] == 4: #burned
                pixels[x, y]=(255,0,0)


    img.save('biome_map.png')


     #image for complete map
    img = Image.new('RGB', (size, size), "white")
    pixels = img.load()  # create the pixel map

    for x in range(size):  # for every pixel:
        for y in range(size):
            if biomemap[x/2][y/2] <= 3:
                if tilemap[x][y] == 0:
                    pixels[x, y] = (0, 0, 255)
                elif tilemap[x][y] == 1:
                    pixels[x, y] = (255, 255, 0)
                elif tilemap[x][y] == 2:
                    r = random.randrange(30);
                    if r == 0:
                        pixels[x, y] = (0, 0, 0)
                    else:
                        pixels[x, y] = (0, 255, 0)
                elif tilemap[x][y] == 3:
                    pixels[x, y] = (63, 63, 255)
                elif tilemap[x][y] == 4:
                    r = random.randrange(16);
                    if r == 0:
                        pixels[x, y] = (0, 0, 0)
                    else:
                        pixels[x, y] = (0, 200, 0)
                elif tilemap[x][y] == 5:
                    r = random.randrange(8);
                    if r == 0:
                        pixels[x, y] = (0, 0, 0)
                    else:
                        pixels[x, y] = (0, 127, 0)

            if biomemap[x/2][y/2] == 3:
                if tilemap[x][y] == 0:
                    pixels[x, y] = (0, 0, 255)
                elif tilemap[x][y] == 1:
                    pixels[x, y] = (255, 255, 0)
                elif tilemap[x][y] == 2 or tilemap[x][y] == 4 or tilemap[x][y] == 5:
                    r = random.randrange(30);
                    if r == 0:
                        pixels[x, y] = (0, 0, 0)
                    else:
                        pixels[x, y] = (127, 0, 255)
                elif tilemap[x][y] == 3:
                    pixels[x, y] = (63, 63, 255)


            if biomemap[x/2][y/2] == 4:
                if tilemap[x][y] == 0:
                    pixels[x, y] = (0, 0, 255)
                elif tilemap[x][y] == 1:
                    pixels[x, y] = (255, 255, 0)
                elif tilemap[x][y] == 2 or tilemap[x][y] == 4 or tilemap[x][y] == 5:
                    r = random.randrange(30);
                    if r == 0:
                        pixels[x, y] = (0, 0, 0)
                    else:
                        pixels[x, y] = (127, 0, 0)
                elif tilemap[x][y] == 3:
                    pixels[x, y] = (63, 63, 255)

    img.save('complete_map.png')

    update_text = "complete generation finished"
    info_text.set(update_text)

def get_start_position():
    return [start_x, start_y]

def to_percent(value):
    value *= 100
    if value > 100:
        value = 100
    value = int(value)
    return value



