"""
A Graphical Abstract program to satisfy very specific needs in converting photos
into "genome-like" illustration and artistic projects.

Designed and coded by Peiling Jiang, in Boston, MA.
Started at Oct. 19, 2018.
"""

from PIL import Image
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time


def get_file(filename):
    """
    Use the given file name to find the absolute path and load the image.
    :param filename:
    :return the image file:
    """
    file_path = os.path.abspath(filename)
    file = open(file_path, 'rb')
    origin_image = Image.open(file, mode="r")
    return origin_image

def helper_crop(image, g):
    """
    Always make the original photo the golden ratio to suit the graph.
    :param image:
    :param g:
    :return:
    """
    w, h = image.size
    if h == w*g:
        return image
    elif h > w*g:
        im = image.crop((0, round((h - w*g)/2),
                         w, round((h + w*g)/2)))
        return im
    else:
        im = image.crop((round((w - h/g)/2), 0,
                         round((w + h/g)/2), h))
        return im

def helper_resize(image, width):
    w, h = image.size
    percent = width / w
    height = round(h * percent)
    new_image = image.resize((width, height), Image.ANTIALIAS)
    return new_image

def set_color_tuple(brick):
    """
    Set up the color dict in which
    (R, G, B): (the approximate half (for efficiency) number of the color, int)
    :param brick, a list of tuples of RGB:
    :return a tuple in which the first element is a dict and the second is an int:
    """
    colors = {}
    color_num = 0
    for i in range(0, len(brick), 2):
        b = brick[i]
        if b not in colors:
            color_num += 1
            colors[b] = 1
        else:
            colors[b] += 1
    return colors, color_num

def get_least_color(image_color_tuple):
    """
    Go through the image and find the least color of the whole image.
    :param image_color_tuple:
    :return a tuple of RGB of the least color:
    """
    assert image_color_tuple[1] > 0
    if image_color_tuple[1] < 2:
        least_color = list(image_color_tuple[0].keys())[0]
        return least_color
    else:
        im_colors = image_color_tuple[0]
        first = max(im_colors, key = im_colors.get)
        im_colors[first] = 0
        least_color = max(im_colors, key = im_colors.get)
        return least_color

def get_main_color(brick, image_color_tuple, least_color):
    """
    Get the max color of a brick.
    Get the the least color of image and max color of brick first, however, when in this brick the max color is more than
    one third of the max color, then the main color is the least color.
    :param brick:
    :param image_color_tuple:
    :param least_color:
    :return a tuple of RGB of the main color:
    """
    brick_color_dict = set_color_tuple(brick) # a tuple
    # Read the colors dict and color number
    b_colors = brick_color_dict[0] # a dict
    b_color_num = brick_color_dict[1] # an int
    im_colors = image_color_tuple[0] # a dict
    im_color_num = image_color_tuple[1] # an int

    if im_color_num == 1:
        return list(im_colors.keys())[0]
    elif b_color_num == 1:
        return list(b_colors.keys())[0]
    else:
        if least_color in b_colors:
            lst = b_colors[least_color]
        else:
            lst = 0
        # get max color
        max_num = 0 # the num of max_color
        max_color = []
        for i in b_colors:
            temp_num = b_colors[i]
            if temp_num > max_num:
                max_color = list(i)
                max_num = temp_num

        if lst < (max_num//3):
            main_color = max_color
        else:
            main_color = least_color
    return main_color

def helper_get_position(i, j, delta_x, delta_y):
    left = j*delta_x
    top = i*delta_y
    right = (j+1)*delta_x
    bottom = (i+1)*delta_y
    return left, top, right, bottom

def helper_bricks_matrix(width, height):
    """
    Get the position and size of bricks.
    Lines (|) and rows (-).
    :param width:
    :return a list of tuples of (left, top, right, bottom) position of bricks:
    """
    matrix = []
    scale = width//1000
    assert scale >= 1

    if scale%2 == 1:
        lines = 51 * scale
        rows = 3 * scale
    else:
        lines = 51*scale + 1
        rows = 3*scale + 1

    delta_x = width/lines
    delta_y = height/rows
    for i in range(rows):
        if i%2 == 0: # line_even
            for j in range(1, lines, 2):
                matrix.append(helper_get_position(i, j, delta_x, delta_y))
        elif i%2 == 1: # line_b
            for j in range(0, lines, 2):
                matrix.append(helper_get_position(i, j, delta_x, delta_y))
    return matrix

def cut(image, matrix):
    """
    Cut resized image into small pieces.
    :param image:
    :param matrix:
    :return a list of lists of tuples of RGB:
    """
    bricks_list = []
    for i in matrix:
        temp_brick = image.crop(i)
        temp = temp_brick.getdata()
        bricks_list.append(list(temp))
    return bricks_list

def helper_fill(brick_num, bricks_list, image_color_tuple, least_color):
    brick = bricks_list[brick_num]
    main_color = get_main_color(brick, image_color_tuple, least_color)
    rgb = []
    for i in main_color:
        rgb.append(i/255) # in plt rgba only supports range of 0 to 1
    return tuple(rgb)

def helper_set_rec_start(i):
    return i[0], i[1]

def get_illustration(width, height, matrix, bricks_list, image_color_tuple, least_color):
    """
    Plot the final illustration.
    :param x:
    :param y:
    :return:
    """
    illustration = plt.figure()
    ax = illustration.add_subplot(111, aspect = 'equal')
    ax.set_xlim([0, width])
    ax.set_ylim([height, 0])

    for i in range(len(matrix)):
        xy = (matrix[i][0], matrix[i][1])
        w = (matrix[i][2]) - (matrix[i][0])
        h = (matrix[i][3]) - (matrix[i][1])
        ax.add_patch(patches.Rectangle(xy, w, h, linewidth = 0, color = helper_fill(i, bricks_list, image_color_tuple, least_color)))
    plt.axis('off')
    plt.show()
    x = input("Save eps(E), png(P), jpg(J)?")
    if x == 'E':
        illustration.savefig(time.ctime()+'.eps', format = 'eps', bbox_inches = 'tight')
    elif x == 'P':
        illustration.savefig(time.ctime() + '.png', format='png', bbox_inches='tight')
    elif x == 'J':
        illustration.savefig(time.ctime() + '.jpg', format='jpg', bbox_inches='tight')
    else:
        pass

if __name__ == 'main':
    # The following parameters are editable for particular usages
    filename = "earth.jpg" # the image to abstract
    width = 6000 # pixels
    """
    The relationship between width and graph complexity:
    It's not about the resolution of the illustration that you want because they will all be vector graphs at last,
    you should change the width only when you want to change the complexity of it to meet needs of different scale of
    the identity in display.
    The complexity will change when width increase every 1000, otherwise only size will change and they will look alike.
    The minimum of width is 1000 to make the illustration at the scale of logo.
    """
    #
    g = 0.618
    height = width * g
    origin_image = get_file(filename)
    # origin_image.show()
    image = helper_resize(helper_crop(origin_image, g), width)

    image_list = list(image.getdata())
    image_color_tuple = set_color_tuple(image_list)
    least_color = get_least_color(image_color_tuple)

    matrix = helper_bricks_matrix(width, height)
    bricks_list = cut(image, matrix) # cut image into pieces based on its size
    get_illustration(width, height, matrix, bricks_list, image_color_tuple, least_color)
