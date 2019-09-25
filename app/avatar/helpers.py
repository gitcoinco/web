def hex_to_rgb_array(_hex):
    return [int(_hex[0:2], 16), int(_hex[2:4], 16), int(_hex[4:6], 16)]


def rgb_array_to_hex(rgba): 
    arr = [hex(ele).replace('0x', '').zfill(2) for ele in rgba]
    ret = "".join(arr)
    return ret


def add_rgb_array(rgba1, rgba2,enforceminmax=False):
    new_array = [rgba1[0] + rgba2[0], rgba1[1] + rgba2[1], rgba1[2] + rgba2[2]]
    if enforceminmax:
        for i in range(0, 3):
            new_array[i] = max([0, new_array[i]])
            new_array[i] = min([255, new_array[i]])
    return new_array


def sub_rgb_array(rgba1, rgba2,enforceminmax=False):
    return add_rgb_array(rgba1, [-1 * ele for ele in rgba2],enforceminmax=enforceminmax)
