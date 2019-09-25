def hex_to_rgb_array(_hex):
    return [int(_hex[0:2], 16), int(_hex[2:4], 16), int(_hex[4:6], 16)]


def rgb_array_to_hex(rgba):
    return "".join([hex(rgba[0]).replace('0x', ''), hex(rgba[1]).replace('0x', ''), hex(rgba[2]).replace('0x', ''), ])


def add_rgb_array(rgba1, rgba2):
    new_array = [rgba1[0] + rgba2[0], rgba1[1] + rgba2[1], rgba1[2] + rgba2[2], ]
    for i in range(0, 2):
        item = new_array[i]
        new_array[i] = max(0, item)
        new_array[i] = min(255, item)
    return new_array


def sub_rgb_array(rgba1, rgba2):
    return add_rgb_array(rgba1, [-1 * ele for ele in rgba2])
