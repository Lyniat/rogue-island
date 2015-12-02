import random
import math
import Image
import tiles
import csv
import ConfigParser

# generate voroni diagramm
def generate_voronoi_diagram(size, info_text, map):

    #read cfg
    #generic attributes
    config = ConfigParser.ConfigParser()
    config.read('data/configurations/generator.cfg')
    CELL_DIVISION = int(config.get("GenericAttributes","CellDivision"))
    BORDER_WATER = float(config.get("GenericAttributes","BorderWater"))
    BORDER_GRASS = float(config.get("GenericAttributes","BorderGrass"))
    BORDER_JUNGLE = float(config.get("GenericAttributes","BorderJungle"))
    BORDER_TO_WALL = int(config.get("GenericAttributes","BorderWall"))
    SAND_IN_GRASS_RANGE = int(config.get("GenericAttributes","SandInGrassRange"))
    SAND_IN_WATER_RANGE = int(config.get("GenericAttributes","SandInWaterRange"))
    RIVER_DIVISION = int(config.get("GenericAttributes","RiverDivision"))
    RIVER_RANGE = int(config.get("GenericAttributes","RiverRange"))
    RIVER_LAKE_SIZE = int(config.get("GenericAttributes","RiverLakeSize"))


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

    num_cells = size / CELL_DIVISION
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


        elif size / BORDER_WATER > distance > size / BORDER_GRASS:
            r = random.randrange(4)
            if r == 0:
                nt.append(0)
            else:
                nt.append(2)
        elif size / BORDER_GRASS > distance > size/BORDER_JUNGLE:
            nt.append(4)
        elif size/BORDER_JUNGLE > distance:
            nt.append(5)
        else:
            nt.append(2)

    for y in range(size):
        for x in range(size):
            dmin = math.hypot(size - 1, size - 1)
            j = -1
            for i in range(num_cells):
                d = math.fabs(nx[i] - x) + math.fabs(ny[i] - y)#math.fabs(nx[i] - x) + math.fabs(ny[i] - y)#math.hypot(nx[i] - x, ny[i] - y)
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
            if dist > (size/2 - BORDER_TO_WALL):
                tilemap[x][y] = 0


    # add sand in grass
    for x in range(SAND_IN_GRASS_RANGE + 1, size - SAND_IN_GRASS_RANGE - 1):
        for y in range(SAND_IN_GRASS_RANGE + 1, size - SAND_IN_GRASS_RANGE - 1):

            val = tilemap[x][y]

            if val == 0:
                for xs in range(-SAND_IN_GRASS_RANGE, SAND_IN_GRASS_RANGE):
                    for ys in range(-SAND_IN_GRASS_RANGE, SAND_IN_GRASS_RANGE):
                        xt = x + xs
                        yt = y + ys
                        if tilemap[xt][yt] == 2 or tilemap[xt][yt] == 4 or tilemap[xt][yt] == 5:
                            r = random.randrange(5)
                            if r == 0:
                                tilemap[xt][yt] = 1

        update_text = "adding sand: " + str(to_percent((x * 1.0) / (size - 9))) + " percent"
        info_text.set(update_text)

    # add sand in water
    for x in range(SAND_IN_WATER_RANGE, size - SAND_IN_WATER_RANGE):
        for y in range(SAND_IN_WATER_RANGE, size - SAND_IN_WATER_RANGE):

            val = tilemap[x][y]

            if val == 2 or val == 4 or val == 5:
                for xs in range(-SAND_IN_WATER_RANGE, SAND_IN_WATER_RANGE):
                    for ys in range(-SAND_IN_WATER_RANGE, SAND_IN_WATER_RANGE):
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
    river_num = size/RIVER_DIVISION;
    for i in range(river_num):
        x = random.randrange(size / RIVER_RANGE, size - size / RIVER_RANGE)
        y = random.randrange(size / RIVER_RANGE, size - size / RIVER_RANGE)

        #create lakes for rivers
        for m in range(-RIVER_LAKE_SIZE,RIVER_LAKE_SIZE):
            for n in range(-RIVER_LAKE_SIZE,RIVER_LAKE_SIZE):
                distance = math.sqrt(m**2+n**2);
                if distance <= RIVER_LAKE_SIZE:
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
            if tilemap[x][y] == 1:
                pixels[x, y] = (255, 255, 0)
            elif tilemap[x][y] == 2:
                    pixels[x, y] = (0, 255, 0)
            elif tilemap[x][y] == 3:
                pixels[x, y] = (63, 63, 255)
            elif tilemap[x][y] == 4:
                    pixels[x, y] = (0, 200, 0)
            elif tilemap[x][y] == 5:
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

        if biome_id > 5:
            biome_id = 0

    for y in range(size/2):
        for x in range(size/2):
            dmin = math.hypot(size - 1, size - 1)
            j = -1
            for i in range(size/12):
                d = math.hypot(nx[i] - x, ny[i] - y)+math.fabs(nx[i] - x) + math.fabs(ny[i] - y)
                if d < dmin:
                    dmin = d
                    j = i
            biomemap[x][y] = nt[j]

    #combine technical and special biomes
    with open("data/configurations/biomes.csv", 'rb') as f:
        mycsv = csv.reader(f, delimiter=';')
        mycsv = list(mycsv)
        for x in range(size):
            for y in range(size):
                tech_value = tilemap[x][y]
                special_value = biomemap[x/2][y/2]
                text = mycsv[tech_value + 1][special_value + 1]
                new_value = text.split(",")

                tilemap[x][y] = int(new_value[0])

    #buildings
    for x in range(14,size-14):
        for y in range(14,size-14):
            tech_value = tilemap[x][y]
            special_value = biomemap[x/2][y/2]
            if (tech_value == 2 or tech_value == 4 or tech_value == 5) and special_value == 1:
                r = random.randrange(240)
                if r == 0:

                    max_value = 14

                    #check if space to build
                    free = 1
                    for m in range(-1,max_value + 1):
                        for n in range(-1,max_value + 1):
                            if tilemap[x+m][y+n] != 2 and tilemap[x+m][y+n] != 4 and tilemap[x+m][y+n] != 5 and tilemap[x+m][y+n] != 6:
                                free = 0

                    if free == 0:
                        continue

                    r = random.randrange(8)
                    file = open("data/structures/house_"+str(r)+".txt","r")

                    #build direction
                    r_line = random.randrange(2)
                    r_row = random.randrange(2)

                    row_increaser = 1
                    line_increaser = 1

                    if r_line == 0:
                        line = 0
                    else:
                        line = max_value
                        line_increaser = -1

                    if r_row == 0:
                        row_reset = 0
                        row = 0
                    else:
                        row_reset = max_value
                        row = max_value
                        row_increaser = -1

                    while 1:
                        char = file.read(1)
                        if not char: break
                        if char == "#":
                            tilemap[x+row][y+line] = 7
                        if char == "|":
                            tilemap[x+row][y+line] = 8
                        if char == ".":
                            tilemap[x+row][y+line] = 9
                        if char == "~":
                            tilemap[x+row][y+line] = 3
                        row += row_increaser
                        if char == "\n":
                            row = row_reset
                            line += line_increaser
                    file.close()

        update_text = "adding buildings: " + str(to_percent((x * 1.0) / (size - 28))) + " percent"
        info_text.set(update_text)

    #swamp lakes
    for x in range(8,size-8):
        for y in range(8,size-8):
            tech_value = tilemap[x][y]
            special_value = biomemap[x/2][y/2]
            if (tech_value == 12) and special_value == 3:
                r = random.randrange(100)
                if r == 0:
                    extra_size = random.randrange(0,4)

                    lake_size = 2 + extra_size
                    for m in range(-lake_size,lake_size):
                        for n in range(-lake_size,lake_size):
                            distance = math.sqrt(m**2+n**2)
                            if distance <= lake_size:
                                r = random.randrange(6)
                                if not r== 0:
                                    tilemap[x+m][y+n] = 3

        update_text = "adding ponds: " + str(to_percent((x * 1.0) / (size - 16))) + " percent"
        info_text.set(update_text)

    #generate objects
    #trees
    for x in range(size):
        for y in range(size):
            value = tilemap[x][y]
            if value == 2:
                r = random.randrange(20)
                if r == 0:
                    tilemap[x][y] = 6
            if value == 4 or value == 12:
                r = random.randrange(10)
                if r == 0:
                    tilemap[x][y] = 6
            if value == 5:
                r = random.randrange(5)
                if r == 0:
                    tilemap[x][y] = 6
            #fungi
            if value == 10:
                r = random.randrange(10)
                if r <= 4:
                    tilemap[x][y] = 11

            #beach/desert
            if value == 1:
                r = random.randrange(30)
                if r == 0:
                    tilemap[x][y] = 13

        update_text = "adding trees: " + str(to_percent((x * 1.0) / size)) + " percent"
        info_text.set(update_text)

    #cellular for mushroom
    for i in range(1):
        for x in range(1,size-1):
            for y in range(1,size-1):
                value = tilemap[x][y]
                trees_around = 0
                #if mushroom
                if value == 11:
                    if tilemap[x+1][y] == 11:
                        trees_around += 1
                    if tilemap[x-1][y] == 11:
                        trees_around += 1
                    if tilemap[x][y+1] == 11:
                        trees_around += 1
                    if tilemap[x][y-1] == 11:
                        trees_around += 1

                    if tilemap[x+1][y+1] == 11:
                        trees_around += 1
                    if tilemap[x+1][y-1] == 11:
                        trees_around += 1
                    if tilemap[x-1][y+1] == 11:
                        trees_around += 1
                    if tilemap[x-1][y-1] == 11:
                        trees_around += 1

                    if trees_around < 4:
                        tilemap[x][y] = 10

                #if no mushroom
                if value == 10:
                    if tilemap[x+1][y] == 11:
                        trees_around += 1
                    if tilemap[x-1][y] == 11:
                        trees_around += 1
                    if tilemap[x][y+1] == 11:
                        trees_around += 1
                    if tilemap[x][y-1] == 11:
                        trees_around += 1

                    if tilemap[x+1][y+1] == 11:
                        trees_around += 1
                    if tilemap[x+1][y-1] == 11:
                        trees_around += 1
                    if tilemap[x-1][y+1] == 11:
                        trees_around += 1
                    if tilemap[x-1][y-1] == 11:
                        trees_around += 1

                    if trees_around >= 5:
                        tilemap[x][y] = 11

            update_text = "coalescing mushrooms: " + str(to_percent((x * 1.0) / (size - 2))) + " percent"
            info_text.set(update_text)

    #castle for burned biome
    for x in range(1,size-1,8):
            for y in range(1,size-1,8):
                value = tilemap[x][y]
                #if burned ground
                if value == 14:
                   #check if space to build
                    free = 1
                    for m in range(8):
                        for n in range(8):
                            if tilemap == 13:
                                free = 0

                    if free == 0:
                        continue

                    r = random.randrange(7)
                    file = open("data/structures/castle_"+str(r)+".txt","r")

                    line = 0
                    row = 0

                    while 1:
                        char = file.read(1)
                        if not char: break
                        if not tilemap[x+row][y+line] == 3:
                            if char == "#":
                                tilemap[x+row][y+line] = 7
                            if char == "|":
                                tilemap[x+row][y+line] = 8
                            if char == ".":
                                tilemap[x+row][y+line] = 9
                            if char == "~":
                                tilemap[x+row][y+line] = 3
                            if char == "%":
                                tilemap[x+row][y+line] = 15
                        row += 1
                        if char == "\n":
                            row = 0
                            line += 1
                    file.close()

            update_text = "building up strongholds: " + str(to_percent((x * 1.0) / (size - 2))) + " percent"
            info_text.set(update_text)

    #remove invisible walls
    for x in range(1,size-1,8):
            for y in range(1,size-1,8):
                value = tilemap[x][y]
                #if value == 15:


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
            if biomemap[x][y] == 3: #swamp
                pixels[x, y]=(128,255,0)
            if biomemap[x][y] == 4: #desert
                pixels[x, y]=(255,0,0)
            if biomemap[x][y] == 5: #burned
                pixels[x, y]=(0,0,0)


    img.save('biome_map.png')

    #image for complete map
    img = Image.new('RGB', (size, size), "white")
    pixels = img.load()  # create the pixel map

    with open("data/configurations/tiles.csv", 'rb') as f:
        mycsv = csv.reader(f, delimiter=';')
        mycsv = list(mycsv)
        for x in range(size):
            for y in range(size):
                value = tilemap[x][y]
                red = int(mycsv[value+1][3])
                green = int(mycsv[value+1][4])
                blue = int(mycsv[value+1][5])

                pixels[x,y] =(red,green,blue)

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



