import zlib
import struct


def load_map():
    data_compressed = open('world.sav', 'rb').read()
    data = zlib.decompress(data_compressed)

    values = []
    map_num = 0
    idx = 0
    map = None
    for i in range(0, len(data)):
        if idx and i < idx:
            continue
        if data[idx] == "~":
            if data[idx + 1] == "[":
                values.append("")
                idx += 2
                while data[idx] != "]":
                    values[len(values) - 1] += data[idx]
                    idx += 1
                idx += 1
        else:
            if map is None:
                size = int(get_value("size", values))
                map = [None] * size ** 2

            map[map_num] = struct.unpack("b", data[idx])[0]
            map_num += 1
            idx += 1

    print("Map Loaded!")
    return map


def get_value(wanted, values):
    for value in values:
        word = value.rpartition(':')[0]
        if word == wanted:
            result = value.rpartition(':')[2]
            print ("result: " + str(result))
            return result
