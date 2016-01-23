import random
import math
import Image
import csv
import ConfigParser
import struct
import zlib
from opensimplex import OpenSimplex
from multiprocessing import Process, Value, Array
import multiprocessing
from ctypes import c_int
import time

multiprocessing.freeze_support()
shared_var = Value(c_int)
shared_tilemap = None

processor_num = 0


def noise(nx, ny):
    # Rescale from -1.0:+1.0 to 0.0:1.0
    return gen.noise2d(nx, ny) / 2.0 + 0.5


def initialize(map_size, info):
    global shared_tilemap
    shared_tilemap = Array('l', map_size * map_size)

    global size
    size = map_size

    global info_text
    info_text = info

    global gen
    gen = OpenSimplex()

    # read cfg
    # generic attributes
    config = ConfigParser.ConfigParser()
    config.read('data/configurations/generator.cfg')
    global CELL_DIVISION
    CELL_DIVISION = int(config.get("GenericAttributes", "CellDivision"))
    global BORDER_WATER
    BORDER_WATER = float(config.get("GenericAttributes", "BorderWater"))
    global BORDER_GRASS
    BORDER_GRASS = float(config.get("GenericAttributes", "BorderGrass"))
    global BORDER_JUNGLE
    BORDER_JUNGLE = float(config.get("GenericAttributes", "BorderJungle"))
    global BORDER_TO_WALL
    BORDER_TO_WALL = int(config.get("GenericAttributes", "BorderWall"))
    global SAND_IN_GRASS_RANGE
    SAND_IN_GRASS_RANGE = int(config.get("GenericAttributes", "SandInGrassRange"))
    global SAND_IN_WATER_RANGE
    SAND_IN_WATER_RANGE = int(config.get("GenericAttributes", "SandInWaterRange"))
    global RIVER_DIVISION
    RIVER_DIVISION = int(config.get("GenericAttributes", "RiverDivision"))
    global RIVER_RANGE
    RIVER_RANGE = int(config.get("GenericAttributes", "RiverRange"))
    global RIVER_LAKE_SIZE
    RIVER_LAKE_SIZE = int(config.get("GenericAttributes", "RiverLakeSize"))
    global BUILDING_PROBABILITY
    BUILDING_PROBABILITY = int(config.get("BiomeAttributes", "BuildingProbability"))
    global POND_PROBABILITY
    POND_PROBABILITY = int(config.get("BiomeAttributes", "PondProbability"))
    global POND_MIN_SIZE
    POND_MIN_SIZE = int(config.get("BiomeAttributes", "PondMinSize"))
    global POND_MAX_SIZE
    POND_MAX_SIZE = int(config.get("BiomeAttributes", "PondMaxSize"))
    global TREE_PROBABILITY_BEACH
    TREE_PROBABILITY_BEACH = int(config.get("BiomeAttributes", "TreeProbabilityBeach"))
    global TREE_PROBABILITY_PLAIN
    TREE_PROBABILITY_PLAIN = int(config.get("BiomeAttributes", "TreeProbabilityPlain"))
    global TREE_PROBABILITY_FOREST
    TREE_PROBABILITY_FOREST = int(config.get("BiomeAttributes", "TreeProbabilityForest"))
    global TREE_PROBABILITY_JUNGLE
    TREE_PROBABILITY_JUNGLE = int(config.get("BiomeAttributes", "TreeProbabilityJungle"))
    global MUSHROOM_PROBABILITY
    MUSHROOM_PROBABILITY = int(config.get("BiomeAttributes", "MushroomProbability"))
    global MUSHROOM_CELLULAR_ITERATIONS
    MUSHROOM_CELLULAR_ITERATIONS = int(config.get("BiomeAttributes", "MushroomCellularIterations"))

    # update_text = "initialized"
    # info_text.set(update_text)


def start(map_size, shared_percent):
    start_time = time.clock()
    initialize(map_size, shared_percent)

    global processor_num
    processor_num = multiprocessing.cpu_count();

    print processor_num

    '''
    if processor_num == 1:
        p1 = Process(target=generate_noise, args=(0, shared_var, shared_tilemap, shared_percent, 1))
        p1.start()
    if processor_num == 2:
        p1 = Process(target=generate_noise, args=(0, shared_var, shared_tilemap, shared_percent, 2))
        p2 = Process(target=generate_noise, args=(1, shared_var, shared_tilemap, shared_percent, 2))
        p1.start()
        p2.start()
    '''
    p1 = None
    p2 = None
    p3 = None
    p4 = None

    if processor_num >= 4:
        p1 = Process(target=generate_noise, args=(0, shared_var, shared_tilemap, shared_percent, 4))
        p2 = Process(target=generate_noise, args=(1, shared_var, shared_tilemap, shared_percent, 4))
        p3 = Process(target=generate_noise, args=(2, shared_var, shared_tilemap, shared_percent, 4))
        p4 = Process(target=generate_noise, args=(3, shared_var, shared_tilemap, shared_percent, 4))
        p1.start()
        p2.start()
        p3.start()
        p4.start()

    print "create started"

    while shared_var.value != processor_num:
        pass

    p1.terminate()
    p2.terminate()
    p3.terminate()
    p4.terminate()

    print "create finished"

    shared_var.value = 0
    shared_percent.value = 0

    create_border(shared_tilemap)

    if processor_num >= 4:
        p1 = Process(target=add_sand, args=(0, shared_var, shared_tilemap, shared_percent, 4))
        p2 = Process(target=add_sand, args=(1, shared_var, shared_tilemap, shared_percent, 4))
        p3 = Process(target=add_sand, args=(2, shared_var, shared_tilemap, shared_percent, 4))
        p4 = Process(target=add_sand, args=(3, shared_var, shared_tilemap, shared_percent, 4))
        p1.start()
        p2.start()
        p3.start()
        p4.start()

    print "add_sand started"

    while shared_var.value != processor_num:
        pass

    p1.terminate()
    p2.terminate()
    p3.terminate()
    p4.terminate()

    print "add_sand finished"

    shared_var.value = 0
    shared_percent.value = 0

    if processor_num >= 4:
        p1 = Process(target=remove_water, args=(0, shared_var, shared_tilemap, shared_percent, 4))
        p2 = Process(target=remove_water, args=(1, shared_var, shared_tilemap, shared_percent, 4))
        p3 = Process(target=remove_water, args=(2, shared_var, shared_tilemap, shared_percent, 4))
        p4 = Process(target=remove_water, args=(3, shared_var, shared_tilemap, shared_percent, 4))
        p1.start()
        p2.start()
        p3.start()
        p4.start()

    print "remove_water started"

    while shared_var.value != processor_num:
        pass

    p1.terminate()
    p2.terminate()
    p3.terminate()
    p4.terminate()

    print "remove_water finished"

    shared_var.value = 0
    shared_percent.value = 0

    smooth_sand(shared_tilemap)

    #create_rivers(shared_tilemap)

    create_tilemap_image(shared_tilemap)

    generate_biomes(shared_tilemap)

    end_time = time.clock()
    difference_time = end_time - start_time

    write_map_file(size, shared_tilemap, difference_time)

    print("generation took " + str(difference_time) + " seconds")


def generate_noise(process_id, processes, tilemap, percent, steps):
    # image for noise map
    # img = Image.new('RGB', (size, size), "white")
    # pixels = img.load()  # create the pixel map

    side_distance = math.sqrt((size / 2) ** 2 + (size / 2) ** 2)

    for x in range(process_id, size, steps):
        for y in range(size):

            nx = x / float(size) - 0.5
            ny = y / float(size) - 0.5
            value = (noise(nx * 20, ny * 20) + 1) / 2

            distance = 1 - (math.sqrt((x - size / 2) ** 2 + (y - size / 2) ** 2) / side_distance)

            distance += value

            distance **= 1.25

            value = distance - 1

            if value < 0:
                value = 0

            if value < 0.2:
                tilemap[x * size + y] = 0
            if 0.2 <= value < 0.4:
                tilemap[x * size + y] = 2
            if 0.4 <= value < 0.6:
                tilemap[x * size + y] = 4
            if value >= 0.6:
                tilemap[x * size + y] = 5

            color = int(value * 255)

            red = int((gen.noise3d(x, y, 0) + 1) * 127)
            green = int((gen.noise3d(x, y, 0) + 1) * 127)
            blue = int((gen.noise3d(x, y, 0) + 1) * 127)

            # print value

            # pixels[x, y] = (color, color, color)

            percent.value += 1

            # update_text = "generating noise: " + str(to_percent((x * 1.0) / size)) + "%%"
            # info_text.set(update_text)

    # img.save('noise_map.png')

    global start_x, start_y
    start_x = 12
    start_y = 12

    processes.value += 1
    print "finished"
    print processes


def create_border(tilemap):
    # prevent island from colliding with wall
    for y in range(size):
        for x in range(size):
            dist = math.sqrt((size / 2 - x) ** 2 + (size / 2 - y) ** 2)
            if dist > (size / 2 - BORDER_TO_WALL):
                tilemap[x * size + y] = 0


def add_sand(process_id, processes, tilemap, percent, steps):
    for x in range(process_id * 2 + (SAND_IN_GRASS_RANGE + 1), size - (SAND_IN_GRASS_RANGE + 1), steps * 2):
        for y in range(SAND_IN_GRASS_RANGE + 1, size - SAND_IN_GRASS_RANGE - 1, 2):
            val = tilemap[x * size + y]

            if val == 0:
                for xs in range(-SAND_IN_GRASS_RANGE, SAND_IN_GRASS_RANGE):
                    for ys in range(-SAND_IN_GRASS_RANGE, SAND_IN_GRASS_RANGE):
                        xt = x + xs
                        yt = y + ys
                        if tilemap[xt * size + yt] == 2 or tilemap[xt * size + yt] == 4 or tilemap[xt * size + yt] == 5:
                            r = random.randrange(5)
                            if r == 0:
                                tilemap[xt * size + yt] = 1
        percent.value += 1

        # update_text = "adding sand: " + str(to_percent((x * 1.0) / (size - 9))) + "%%"
        # info_text.set(update_text)

    processes.value += 1
    print "finished"
    print processes


def remove_water(process_id, processes, tilemap, percent, steps):
    # add sand in water
    for x in range(process_id * 2 + SAND_IN_WATER_RANGE, size - SAND_IN_WATER_RANGE, steps * 2):
        for y in range(SAND_IN_WATER_RANGE, size - SAND_IN_WATER_RANGE, 2):

            val = tilemap[x * size + y]

            if val == 2 or val == 4 or val == 5:
                for xs in range(-SAND_IN_WATER_RANGE, SAND_IN_WATER_RANGE):
                    for ys in range(-SAND_IN_WATER_RANGE, SAND_IN_WATER_RANGE):
                        xt = x + xs
                        yt = y + ys
                        if tilemap[xt * size + yt] == 0:
                            r = random.randrange(5)
                            if r == 0:
                                tilemap[xt * size + yt] = 1

        percent.value += 1
        # update_text = "removing water: " + str(to_percent((x * 1.0) / (size - 19))) + "%%"
        # info_text.set(update_text)

    processes.value += 1
    print "finished"
    print processes


def smooth_sand(tilemap):
    for i in range(3):
        for x in range(1, size - 1):
            for y in range(1, size - 1):
                value = tilemap[x * size + y]
                trees_around = 0
                # if water
                if value == 0:
                    if tilemap[(x + 1) * size + y] == 1:
                        trees_around += 1
                    if tilemap[(x - 1) * size + y] == 1:
                        trees_around += 1
                    if tilemap[x * size + y + 1] == 1:
                        trees_around += 1
                    if tilemap[x * size + y - 1] == 1:
                        trees_around += 1

                    if tilemap[(x + 1) * size + y + 1] == 1:
                        trees_around += 1
                    if tilemap[(x + 1) * size + y - 1] == 1:
                        trees_around += 1
                    if tilemap[(x - 1) * size + y + 1] == 1:
                        trees_around += 1
                    if tilemap[(x - 1) * size + y - 1] == 1:
                        trees_around += 1

                    if trees_around >= 5:
                        tilemap[x * size + y] = 1


def create_rivers(tilemap):
    print "creating rivers"

    # create rivers
    river_num = size / RIVER_DIVISION
    for i in range(river_num):
        x = random.randrange(size / RIVER_RANGE, size - size / RIVER_RANGE)
        y = random.randrange(size / RIVER_RANGE, size - size / RIVER_RANGE)

        # create lakes for rivers
        for m in range(-RIVER_LAKE_SIZE, RIVER_LAKE_SIZE):
            for n in range(-RIVER_LAKE_SIZE, RIVER_LAKE_SIZE):
                distance = math.sqrt(m ** 2 + n ** 2)
                if distance <= RIVER_LAKE_SIZE:
                    tilemap[(x + m) * size + y + n] = 3

        extra_distance = 1
        x_position = 0
        y_position = 0
        value = 0
        while 1:
            for m in range(-extra_distance, extra_distance):
                for n in range(-extra_distance, extra_distance):
                    value = tilemap[(x + m) * size + y + n]
                    print(value)
                    if value == 0:
                        x_position = x + m
                        y_position = y + n
                        break
                if value == 0:
                    break
            extra_distance += 1
            if value == 0:
                    break

        print "river created ppart 1"

        while 1:
            x_distance = math.fabs(x - x_position)
            y_distance = math.fabs(y - y_position)

            print(x_distance)
            print(y_distance)

            if x_distance > y_distance:
                if x > x_position:
                    x_direction = -1
                else:
                    x_direction = 1
                y_direction = 0
            else:
                if y > y_position:
                    y_direction = -1
                else:
                    y_direction = 1
                x_direction = 0

            x += random.randrange(-1, 1)
            y += random.randrange(-1, 1)

            x += x_direction
            y += y_direction

            if tilemap[x * size + y] == 0:
                print "river created"
                break

            for m in range(-1, 1):
                for n in range(-1, 1):
                    tilemap[(x + m) * size + y + n] = 3

        '''
        water_tile = 0
        x_direction = 0
        y_direction = 0
        while 1 == 1:
            extra_size = 1
            while 1 == 1:
                m = -extra_size
                for o in range(2):
                    n = -extra_size
                    for p in range(2):
                        # distance = math.sqrt((x - m) ** 2 + (y - n) ** 2)
                        # if distance <= extra_size:
                        if tilemap[(x + m) * size + y + n] == 0:
                            x_distance = math.fabs(x - (m + x))
                            y_distance = math.fabs(y - (n + y))

                            if x_distance < y_distance:
                                if x > m + x:
                                    x_direction = -1
                                else:
                                    x_direction = 1
                                y_direction = 0
                            else:
                                if y > n + y:
                                    y_direction = -1
                                else:
                                    y_direction = 1
                                x_direction = 0

                        if x_direction != 0 or y_direction != 0:
                            break
                        n = extra_size
                    if x_direction != 0 or y_direction != 0:
                        break
                    m = extra_size
                if x_direction != 0 or y_direction != 0:
                    break
                else:
                    extra_size += 1

            x += x_direction
            y += y_direction

            x += random.randrange(-1, 1)
            y += random.randrange(-1, 1)

            x = int(x)
            y = int(y)

            x_direction = 0
            y_direction = 0

            print("x: " + str(x) + " y: " + str(y))

            if tilemap[x * size + y] == 0:
                print "river created"
                break

            for m in range(-1, 1):
                for n in range(-1, 1):
                    tilemap[(x + m) * size + y + n] = 3

            tilemap[x * size + y] = 3

            # update_text = "creating river: " + str(to_percent(river_num / (i + 1))) + "%%"
            # info_text.set(update_text)
        '''


def create_tilemap_image(tilemap):
    print "creating tilemap"
    # image for tilemap
    img = Image.new('RGB', (size, size), "white")
    pixels = img.load()  # create the pixel map

    for x in range(size):  # for every pixel:
        for y in range(size):
            if tilemap[x * size + y] == 1:
                pixels[x, y] = (255, 255, 0)
            elif tilemap[x * size + y] == 2:
                pixels[x, y] = (0, 255, 0)
            elif tilemap[x * size + y] == 3:
                pixels[x, y] = (63, 63, 255)
            elif tilemap[x * size + y] == 4:
                pixels[x, y] = (0, 200, 0)
            elif tilemap[x * size + y] == 5:
                pixels[x, y] = (0, 127, 0)

    img.save('debug/tile_map.png')

    # update_text = "terrain generation finished"
    # info_text.set(update_text)


def generate_biomes(tilemap):
    print "generating biomes"
    # def generate_biomes(size):
    biomemap = [[0
                 for y in range(size)]
                for x in range(size)]

    nx = []
    ny = []
    nt = []
    biome_id = 0

    for i in range(24):
        rx = random.randrange(size / 2)
        ry = random.randrange(size / 2)

        nx.append(rx)
        ny.append(ry)

        nt.append(biome_id)

        biome_id += 1

        if biome_id > 7:
            biome_id = 0

    for y in range(size / 2):
        for x in range(size / 2):
            dmin = math.hypot(size - 1, size - 1)
            j = -1
            for i in range(24):
                d = math.sqrt((nx[i] - x)**2 + (ny[i] - y)**2)#math.floor(math.fabs(nx[i] - x) + math.fabs(ny[i] - y) + 1)
                if d < dmin:
                    dmin = d
                    j = i
            biomemap[x][y] = nt[j]

            # update_text = "generating biomes: " + str(to_percent((y * 1.0) / size)) + "%%"
            # info_text.set(update_text)

    # combine technical and special biomes
    with open("data/configurations/biomes.csv", 'rb') as f:
        mycsv = csv.reader(f, delimiter=';')
        mycsv = list(mycsv)
        for x in range(size):
            for y in range(size):
                tech_value = tilemap[x * size + y]
                special_value = biomemap[x / 2][y / 2]
                text = mycsv[tech_value + 1][special_value + 1]
                new_value = text.split(",")

                tilemap[x * size + y] = int(new_value[0])

    print "generating buildings"
    # buildings
    for x in range(14, size - 14):
        for y in range(14, size - 14):
            tech_value = tilemap[x * size + y]
            special_value = biomemap[x / 2][y / 2]
            if (tech_value == 2 or tech_value == 4 or tech_value == 5) and special_value == 1:
                r = random.randrange(BUILDING_PROBABILITY)
                if r == 0:

                    max_value = 14

                    # check if space to build
                    free = 1
                    for m in range(-1, max_value + 1):
                        for n in range(-1, max_value + 1):
                            if tilemap[(x + m) * size + y + n] != 2 and tilemap[(x + m) * size + y + n] != 4 and \
                                            tilemap[(x + m) * size + y + n] != 5 and tilemap[
                                                        (x + m) * size + y + n] != 6:
                                free = 0

                    if free == 0:
                        continue

                    r = random.randrange(8)
                    file = open("data/structures/house_" + str(r) + ".struct", "r")

                    # build direction
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
                            tilemap[(x + row) * size + y + line] = 7
                        if char == "|":
                            tilemap[(x + row) * size + y + line] = 8
                        if char == ".":
                            tilemap[(x + row) * size + y + line] = 9
                        if char == "~":
                            tilemap[(x + row) * size + y + line] = 3
                        if char == ";":
                            tilemap[(x + row) * size + y + line] = 2
                        row += row_increaser
                        if char == "\n":
                            row = row_reset
                            line += line_increaser
                    file.close()

                    # update_text = "adding buildings: " + str(to_percent((x * 1.0) / (size - 28))) + "%%"
                    # info_text.set(update_text)

    print "creating swamps"
    # swamp lakes
    for x in range(8, size - 8):
        for y in range(8, size - 8):
            tech_value = tilemap[x * size + y]
            special_value = biomemap[x / 2][y / 2]
            if (tech_value == 12) and special_value == 3:
                r = random.randrange(POND_PROBABILITY)
                if r == 0:
                    lake_size = random.randrange(POND_MIN_SIZE, POND_MAX_SIZE)
                    for m in range(-lake_size, lake_size):
                        for n in range(-lake_size, lake_size):
                            distance = math.sqrt(m ** 2 + n ** 2)
                            if distance <= lake_size:
                                r = random.randrange(6)
                                if not r == 0:
                                    tilemap[(x + m) * size + y + n] = 3

                                    # update_text = "adding ponds: " + str(to_percent((x * 1.0) / (size - 16))) + "%%"
                                    # info_text.set(update_text)

    print "placing trees"
    # generate objects
    # trees
    for x in range(size):
        for y in range(size):
            value = tilemap[x * size + y]
            if value == 2:
                r = random.randrange(TREE_PROBABILITY_PLAIN)
                if r == 0:
                    tilemap[x * size + y] = 6
            if value == 4 or value == 12:
                r = random.randrange(TREE_PROBABILITY_FOREST)
                if r == 0:
                    tilemap[x * size + y] = 6
            if value == 5:
                r = random.randrange(TREE_PROBABILITY_JUNGLE)
                if r == 0:
                    tilemap[x * size + y] = 6
            # mushroom
            if value == 10:
                r = random.randrange(MUSHROOM_PROBABILITY)
                if r <= 4:
                    tilemap[x * size + y] = 11

            # beach/desert
            if value == 1:
                r = random.randrange(TREE_PROBABILITY_BEACH)
                if r == 0:
                    tilemap[x * size + y] = 13

                    # update_text = "adding trees: " + str(to_percent((x * 1.0) / size)) + "%%"
                    # info_text.set(update_text)

    print "creating mushrooms"
    # cellular for mushroom
    for i in range(MUSHROOM_CELLULAR_ITERATIONS):
        for x in range(1, size - 1):
            for y in range(1, size - 1):
                value = tilemap[x * size + y]
                trees_around = 0
                # if mushroom
                if value == 11:
                    if tilemap[(x + 1) * size + y] == 11:
                        trees_around += 1
                    if tilemap[(x - 1) * size + y] == 11:
                        trees_around += 1
                    if tilemap[x * size + y + 1] == 11:
                        trees_around += 1
                    if tilemap[x * size + y - 1] == 11:
                        trees_around += 1

                    if tilemap[(x + 1) * size + y + 1] == 11:
                        trees_around += 1
                    if tilemap[(x + 1) * size + y - 1] == 11:
                        trees_around += 1
                    if tilemap[(x - 1) * size + y + 1] == 11:
                        trees_around += 1
                    if tilemap[(x - 1) * size + y - 1] == 11:
                        trees_around += 1

                    if trees_around < 4:
                        tilemap[x * size + y] = 10

                # if no mushroom
                if value == 10:
                    if tilemap[(x + 1) * size + y] == 11:
                        trees_around += 1
                    if tilemap[(x - 1) * size + y] == 11:
                        trees_around += 1
                    if tilemap[x * size + y + 1] == 11:
                        trees_around += 1
                    if tilemap[x * size + y - 1] == 11:
                        trees_around += 1

                    if tilemap[(x + 1) * size + y + 1] == 11:
                        trees_around += 1
                    if tilemap[(x + 1) * size + y - 1] == 11:
                        trees_around += 1
                    if tilemap[(x - 1) * size + y + 1] == 11:
                        trees_around += 1
                    if tilemap[(x - 1) * size + y - 1] == 11:
                        trees_around += 1

                    if trees_around >= 5:
                        tilemap[x * size + y] = 11

                        # update_text = "coalescing mushrooms: " + str(to_percent((x * 1.0) / (size - 2))) + "%%"
                        # info_text.set(update_text)

    print "creating castle"
    # castle for burned biome
    for x in range(1, size - 1, 8):
        for y in range(1, size - 1, 8):
            value = tilemap[x * size + y]
            # if burned ground
            if value == 14:
                # check if space to build
                free = 1
                for m in range(8):
                    for n in range(8):
                        if not tilemap[(x + m) * size + y + n] == 14 and not tilemap[(x + m) * size + y + n] == 3:
                            free = 0

                if free == 0:
                    continue

                r = random.randrange(9)
                file = open("data/structures/castle_" + str(r) + ".struct", "r")

                line = 0
                row = 0

                while 1:
                    char = file.read(1)
                    if not char: break
                    if not tilemap[(x + row) * size + y + line] == 3:
                        if char == "#":
                            tilemap[(x + row) * size + y + line] = 7
                        if char == "|":
                            tilemap[(x + row) * size + y + line] = 8
                        if char == ".":
                            tilemap[(x + row) * size + y + line] = 9
                        if char == "~":
                            tilemap[(x + row) * size + y + line] = 3
                        if char == " ":
                            tilemap[(x + row) * size + y + line] = 14
                        if char == "%":
                            tilemap[(x + row) * size + y + line] = 15
                    row += 1
                    if char == "\n":
                        row = 0
                        line += 1
                file.close()

                # update_text = "building up strongholds: " + str(to_percent((x * 1.0) / (size - 2))) + "%%"
                # info_text.set(update_text)

    print "creating honeycombs"
    # honeycombs for bees
    for x in range(1, size - 26, 25):
        for y in range(1, size - 26, 10):
            value = tilemap[x * size + y]
            # if honey ground
            if 1:  # value == 16 or value == 17:

                file = open("data/structures/hexagon.struct", "r")

                line = 0
                row = 0

                while 1:
                    char = file.read(1)
                    if not char: break
                    if tilemap[(x + row) * size + y + line] == 16:
                        if char == "#":
                            r = random.randrange(7)
                            if not r == 0:
                                tilemap[(x + row) * size + y + line] = 17
                    row += 1
                    if char == "\n":
                        row = 0
                        line += 1
                file.close()

    # honeycombs for bees
    for x in range(13, size - 26, 25):
        for y in range(6, size - 26, 10):
            value = tilemap[x * size + y]
            # if honey ground
            if 1:  # value == 16:

                file = open("data/structures/hexagon.struct", "r")

                line = 0
                row = 0

                while 1:
                    char = file.read(1)
                    if not char: break
                    if tilemap[(x + row) * size + y + line] == 16:
                        if char == "#":
                            r = random.randrange(7)
                            if not r == 0:
                                tilemap[(x + row) * size + y + line] = 17
                    row += 1
                    if char == "\n":
                        row = 0
                        line += 1
                file.close()

                # update_text = "creating honeycombs: " + str(to_percent((x * 1.0) / (size - 2))) + "%%"
                # info_text.set(update_text)

    print "removing walls"
    # remove invisible walls
    wall_counter = 0
    for x in range(1, size - 1):
        for y in range(1, size - 1):
            value = tilemap[x * size + y]
            # if invisible wall
            if value == 15:
                if tilemap[(x + 1) * size + y] == 15 and tilemap[(x + 1) * size + y + 1] == 15 and tilemap[
                                            x * size + y + 1] == 15:
                    tilemap[x * size + y] = 9
                    tilemap[(x + 1) * size + y] = 9
                    tilemap[x * size + y + 1] = 9
                    tilemap[(x + 1) * size + y + 1] = 9
                else:
                    if wall_counter < 10:
                        tilemap[x * size + y] = 7
                        wall_counter += 1
                    else:
                        tilemap[x * size + y] = 9
                        wall_counter = 0


    # image for biomemap
    img = Image.new('RGB', (size / 2, size / 2), "white")
    pixels = img.load()  # create the pixel map

    for x in range(size / 2):  # for every pixel:
        for y in range(size / 2):
            if biomemap[x][y] <= 0:  # normal
                pixels[x, y] = (255, 255, 255)
            if biomemap[x][y] == 1:  # village
                pixels[x, y] = (255, 255, 0)
            if biomemap[x][y] == 2:  # mushroom
                pixels[x, y] = (255, 0, 255)
            if biomemap[x][y] == 3:  # swamp
                pixels[x, y] = (128, 255, 0)
            if biomemap[x][y] == 4:  # desert
                pixels[x, y] = (255, 0, 0)
            if biomemap[x][y] == 5:  # burned
                pixels[x, y] = (0, 0, 0)
            if biomemap[x][y] == 6:  # killer bees
                pixels[x, y] = (255, 100, 0)
            if biomemap[x][y] == 7:  # frozen
                pixels[x, y] = (120, 160, 210)

    img.save('debug/biome_map.png')

    # image for complete map
    img = Image.new('RGB', (size, size), "white")
    pixels = img.load()  # create the pixel map

    with open("data/configurations/tiles.csv", 'rb') as f:
        mycsv = csv.reader(f, delimiter=';')
        mycsv = list(mycsv)
        for x in range(size):
            for y in range(size):
                value = tilemap[x * size + y]
                red = int(mycsv[value + 1][3])
                green = int(mycsv[value + 1][4])
                blue = int(mycsv[value + 1][5])

                pixels[x, y] = (red, green, blue)

    img.save('debug/complete_map.png')

    # update_text = "complete generation finished"
    # info_text.set(update_text)

    # update_text = "saving world finished"
    # info_text.set(update_text)

    print "finished"


def get_start_position():
    return [start_x, start_y]


def to_percent(value):
    value *= 100
    if value > 100:
        value = 100
    value = int(value)
    return value


def write_map_file(size, map, time):
    version = "0.1"
    version_string = "~[version:" + version + "]"
    size_string = "~[size:" + str(size) + "]"
    time_string = "~[time:" + str(time) + "]"

    with open("world.sav", "wb") as savefile:
        savefile.seek(0)
        savefile.truncate()
        data = ""
        data += (version_string + size_string + time_string)
        for x in range(size):
            for y in range(0, size):
                format = "c"
                data += struct.pack(format, chr(map[x * size + y]))
        compressed = zlib.compress(data, 9)
        savefile.write(compressed)
