import random

from PIL import Image


VINTAGE_COLOR_LEVELS = {
    'r': [0, 0, 0, 1, 1, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 7, 7, 7, 7, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 12, 12, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 17, 18, 19, 19, 20, 21, 22, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 39, 40, 41, 42, 44, 45, 47, 48, 49, 52, 54, 55, 57, 59, 60, 62, 65, 67, 69, 70, 72, 74, 77, 79, 81, 83, 86, 88, 90, 92, 94, 97, 99, 101, 103, 107, 109, 111, 112, 116, 118, 120, 124, 126, 127, 129, 133, 135, 136, 140, 142, 143, 145, 149, 150, 152, 155, 157, 159, 162, 163, 165, 167, 170, 171, 173, 176, 177, 178, 180, 183, 184, 185, 188, 189, 190, 192, 194, 195, 196, 198, 200, 201, 202, 203, 204, 206, 207, 208, 209, 211, 212, 213, 214, 215, 216, 218, 219, 219, 220, 221, 222, 223, 224, 225, 226, 227, 227, 228, 229, 229, 230, 231, 232, 232, 233, 234, 234, 235, 236, 236, 237, 238, 238, 239, 239, 240, 241, 241, 242, 242, 243, 244, 244, 245, 245, 245, 246, 247, 247, 248, 248, 249, 249, 249, 250, 251, 251, 252, 252, 252, 253, 254, 254, 254, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255],
    'g' : [0, 0, 1, 2, 2, 3, 5, 5, 6, 7, 8, 8, 10, 11, 11, 12, 13, 15, 15, 16, 17, 18, 18, 19, 21, 22, 22, 23, 24, 26, 26, 27, 28, 29, 31, 31, 32, 33, 34, 35, 35, 37, 38, 39, 40, 41, 43, 44, 44, 45, 46, 47, 48, 50, 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 63, 64, 65, 66, 67, 68, 69, 71, 72, 73, 74, 75, 76, 77, 79, 80, 81, 83, 84, 85, 86, 88, 89, 90, 92, 93, 94, 95, 96, 97, 100, 101, 102, 103, 105, 106, 107, 108, 109, 111, 113, 114, 115, 117, 118, 119, 120, 122, 123, 124, 126, 127, 128, 129, 131, 132, 133, 135, 136, 137, 138, 140, 141, 142, 144, 145, 146, 148, 149, 150, 151, 153, 154, 155, 157, 158, 159, 160, 162, 163, 164, 166, 167, 168, 169, 171, 172, 173, 174, 175, 176, 177, 178, 179, 181, 182, 183, 184, 186, 186, 187, 188, 189, 190, 192, 193, 194, 195, 195, 196, 197, 199, 200, 201, 202, 202, 203, 204, 205, 206, 207, 208, 208, 209, 210, 211, 212, 213, 214, 214, 215, 216, 217, 218, 219, 219, 220, 221, 222, 223, 223, 224, 225, 226, 226, 227, 228, 228, 229, 230, 231, 232, 232, 232, 233, 234, 235, 235, 236, 236, 237, 238, 238, 239, 239, 240, 240, 241, 242, 242, 242, 243, 244, 245, 245, 246, 246, 247, 247, 248, 249, 249, 249, 250, 251, 251, 252, 252, 252, 253, 254, 255],
    'b' : [53, 53, 53, 54, 54, 54, 55, 55, 55, 56, 57, 57, 57, 58, 58, 58, 59, 59, 59, 60, 61, 61, 61, 62, 62, 63, 63, 63, 64, 65, 65, 65, 66, 66, 67, 67, 67, 68, 69, 69, 69, 70, 70, 71, 71, 72, 73, 73, 73, 74, 74, 75, 75, 76, 77, 77, 78, 78, 79, 79, 80, 81, 81, 82, 82, 83, 83, 84, 85, 85, 86, 86, 87, 87, 88, 89, 89, 90, 90, 91, 91, 93, 93, 94, 94, 95, 95, 96, 97, 98, 98, 99, 99, 100, 101, 102, 102, 103, 104, 105, 105, 106, 106, 107, 108, 109, 109, 110, 111, 111, 112, 113, 114, 114, 115, 116, 117, 117, 118, 119, 119, 121, 121, 122, 122, 123, 124, 125, 126, 126, 127, 128, 129, 129, 130, 131, 132, 132, 133, 134, 134, 135, 136, 137, 137, 138, 139, 140, 140, 141, 142, 142, 143, 144, 145, 145, 146, 146, 148, 148, 149, 149, 150, 151, 152, 152, 153, 153, 154, 155, 156, 156, 157, 157, 158, 159, 160, 160, 161, 161, 162, 162, 163, 164, 164, 165, 165, 166, 166, 167, 168, 168, 169, 169, 170, 170, 171, 172, 172, 173, 173, 174, 174, 175, 176, 176, 177, 177, 177, 178, 178, 179, 180, 180, 181, 181, 181, 182, 182, 183, 184, 184, 184, 185, 185, 186, 186, 186, 187, 188, 188, 188, 189, 189, 189, 190, 190, 191, 191, 192, 192, 193, 193, 193, 194, 194, 194, 195, 196, 196, 196, 197, 197, 197, 198, 199]
    }


def modify_all_pixels(im, pixel_callback):
    width, height = im.size
    pxls = im.load()
    for x in range(width):
        for y in range(height):
            pxls[x,y] = pixel_callback(x, y, *pxls[x, y])


def vintage_colors(im, color_map=VINTAGE_COLOR_LEVELS):
    r_map = color_map['r']
    g_map = color_map['g']
    b_map = color_map['b']

    def adjust_levels(x, y, r, g, b, a):  # expect rgb; rgba will blow up
        return r_map[r], g_map[g], b_map[b]

    modify_all_pixels(im, adjust_levels)
    return im


def add_noise(im, noise_level=20):
    def pixel_noise(x, y, r, g, b):  # expect rgb; rgba will blow up
        noise = int(random.randint(0, noise_level) - noise_level / 2)
        return max(0, min(r + noise, 255)), max(0, min(g + noise, 255)), max(0, min(b + noise, 255))
    modify_all_pixels(im, pixel_noise)
    return im


# Open an Image
def open_image(path):
    newImage = Image.open(path)
    return newImage


# Save Image
def save_image(image, path):
    image.save(path, "png")


# Create a new image with the given size
def create_image(i, j):
    image = Image.new("RGB", (i, j), "white")
    return image


# Get the pixel from the given image
def get_my_pixel(image, i, j):
    # Inside image bounds?
    width, height = image.size
    if i > width or j > height:
        return None

    # Get Pixel
    pixel = image.getpixel((i, j))
    return pixel


# Sepia is a filter based on exagerating red, yellow and brown tones
# This implementation exagerates mainly yellow with a little brown

def get_sepia_pixel(red, green, blue, alpha):
    # This is a really popular implementation
    tRed = min(int((0.759 * red) + (0.398 * green) + (0.194 * blue)), 255)
    tGreen = min(int((0.676 * red) + (0.354 * green) + (0.173 * blue)), 255)
    tBlue = min(int((0.524 * red) + (0.277 * green) + (0.136 * blue)), 255)

    # Return sepia color
    return tRed, tGreen, tBlue, alpha


# Convert an image to sepia
def convert_sepia(image):
    # Get size
    width, height = image.size

    # Create new Image and a Pixel Map
    new_image = create_image(width, height)
    pixels = new_image.load()

    # Convert each pixel to sepia
    for i in range(0, width, 1):
        for j in range(0, height, 1):
            p = get_my_pixel(image, i, j)
            pixels[i, j] = get_sepia_pixel(p[0], p[1], p[2], 255)

    # Return new image
    return new_image

# VARIOUS FILTERS

def get_pixel(image, x, y):
    loc = x * image['width'] + y
    return image['pixels'][loc]


def set_pixel(image, x, y, c):
    loc = x * image['width'] + y
    image['pixels'][loc] = c

def apply_per_pixel(image, func):
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:],
    }
    for x in range(image['height']):
        for y in range(image['width']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)
    return result

def inverted(image):
    # invert a greyscale image
    return apply_per_pixel(image, lambda c: 255-c)

def color_inverted(image):
    # invert a color image
    return color_filter_from_greyscale_filter(inverted)(image)

##################################################
# HELPER FUNCTIONS FOR color_filter_from_greyscale_filter
def split_rgb(image):
    # Given an color image
    # return a tuple of 3 greyscale images (one for each color component) (R, G, B)
    pixelsRGB = [[], [], []]
    for x in range(image['height']):
        for y in range(image['width']):
            for comp, color in zip(pixelsRGB, get_pixel(image, x, y)):
                comp.append(color)
    return ({
        'height': image['height'],
        'width': image['width'],
        'pixels': comp,} for comp in pixelsRGB)

def recombine_rgb(imR,imG,imB):
    # Given 3 greyscale images (one for each color component) (R, G, B)
    # return a color image, that is a combination of 3 greyscale
    pixels = []
    for x in range(imR['height']):
        for y in range(imR['width']):
            r,g,b = get_pixel(imR, x, y), get_pixel(imG, x, y), get_pixel(imB, x, y)
            pixels.append((r,g,b))
    return {'height': imR['height'],
            'width': imR['width'],
            'pixels': pixels,}
##################################################

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    i.e. split the given color image into its three components, apply the greyscale filter to each,
    and recombine them into a new color image.
    """
    def filter_color_image(im):
        imR, imG, imB = split_rgb(im)
        # apply greyscale filter to each component
        imR, imG, imB = filt(imR), filt(imG), filt(imB)
        return recombine_rgb(imR, imG, imB)
    return filter_color_image

################################################
# MORE HELPER FUNCTIONS FOR APLLYING FILTERS

def get_pixel_edge(image, x, y):
    if x < 0: x = 0
    elif x >= image['height']: x = image['height'] - 1
    if y < 0: y = 0
    elif y >= image['width']: y = image['width'] - 1
    loc = x * image['width'] + y
    return image['pixels'][loc]

def correlate(image, kernel):
    """
    KERNEL REPRESENTATION:
    kernel is a tuple with an int: size, and a tuple K contains (2*size+1)**2 elements.
    e.g. identity kernel 3x3 is rep as (1, (0, 0, 0, 0, 1, 0, 0, 0, 0))
    """
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [],
    }
    size, K = kernel
    for x in range(image['height']):
        for y in range(image['width']):
            #apply correlation/kernel to pixel (x,y)
            loc = newcolor = 0
            for ix in range(x-size, x+size+1):
                for iy in range(y-size, y+size+1):
                    newcolor += get_pixel_edge(image, ix, iy) * K[loc]
                    loc += 1
            #set_pixel(result, x, y, newcolor)
            result['pixels'].append(newcolor)
    return result

def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].
    """
    for i,color in enumerate(image['pixels']):
        if color < 0: color = 0
        if color > 255: color = 255
        image['pixels'][i] = round(color)

def make_blur_kernel(n):
    # box-blur HELPER FUNCTION
    cells = n*n
    size = n//2
    return (size, (1/cells,)*cells)

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.
    """
    kernel = make_blur_kernel(n)
    im = correlate(image, kernel)
    round_and_clip_image(im)
    return im

def sharpened(image, n):
    cells = n*n
    size = n//2
    K = (-1/cells,)*(cells//2) + (2-1/cells,) + (-1/cells,)*(cells//2)
    im = correlate(image, (size,K))
    round_and_clip_image(im)
    return im

def edges(image):
    kernel_x = (1, (-1 ,0, 1, -2, 0, 2, -1, 0, 1))
    kernel_y = (1, (-1, -2, -1, 0, 0, 0, 1, 2, 1))

    imx = correlate(image, kernel_x)
    imy = correlate(image, kernel_y)

    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [],
    }
    loc = 0
    for x in range(image['height']):
        for y in range(image['width']):
            newcolor = round((imx['pixels'][loc]**2 + imy['pixels'][loc]**2)**0.5)
            result['pixels'].append(newcolor)
            loc += 1
    round_and_clip_image(result)
    return result
################################################

def make_blur_filter(n):
    #returns a blur filter (which takes a single image as argument)
    return lambda image: blurred(image, n)

def make_sharpen_filter(n):
    return lambda image: sharpened(image, n)

def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def filter(image):
        for f in filters:
            image = f(image)
        return image
    return filter

# SEAM CARVING

# Main Seam Carving Implementation

def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image.
    """
    for _ in range(ncols):
        grey = greyscale_image_from_color_image(image) # this seems to be the only repeated work
        seam = minimum_energy_seam(cumulative_energy_map(compute_energy(grey)))
        image = image_without_seam(image, seam)
    return image


# CREATIVE EXTENSION
def seam_filling(image, ncols):
    """ /TODO
    Opposite of seam_carving
    smart resizing to increase the size of an image by inserting appropriate rows
    at low-energy regions in the image.
    """
    pass


def image_with_new_seam(image,seam):
    pass


def greyscale_vignette(grey):
    height = grey['height']
    width = grey['width']
    import math
    # first, compute the Gaussian Kernel
    #https://docs.opencv.org/2.4/modules/imgproc/doc/filtering.html#Mat%20getGaussianKernel(int%20ksize,%20double%20sigma,%20int%20ktype)
    def getGaussianKernel(ksize):
        sigma = 0.4*((ksize-1)*0.5 - 1) + 0.8
        kernel = []
        scale_factor = 0
        for i in range(ksize):
            coeff = math.e**(-((i-(ksize-1)/2)**2) / (2 * sigma**2))
            kernel.append(coeff)
            scale_factor += coeff
        for i in range(ksize): kernel[i] /= (scale_factor // 5)
        return kernel
    Kx = getGaussianKernel(width)
    Ky = getGaussianKernel(height)
    K = [k1 * k2 for k1 in Ky for k2 in Kx]
    #http://mathworld.wolfram.com/FrobeniusNorm.html
    # compute the Frobenius matrix norm
    norm = sum(i ** 2 for i in K)
    norm = math.sqrt(norm)
    K = [i* 255/norm for i in K]
    # apply per pixel
    pixels = []
    for coeff, value in zip(K, grey['pixels']):
        pixels.append(coeff*value)
    im = {'height': height, 'width': width, 'pixels': pixels}
    round_and_clip_image(im)
    return im

# Optional Helper Functions for Seam Carving


def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    pixels = [round(.299 * r + .587 * g + .114 * b)
                      for r,g,b in image['pixels']]
    return  {'height': image['height'], 'width': image['width'], 'pixels': pixels,}


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy"// here: using
    the edges function from last week.
    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)


# HELPER FUNCTION FOR cumulative_energy_map and minimum_energy_seam
def get_min_adj(p, pixels, width):
    '''
    Find the min Energy, and its index, from the 3 "adjacent" pixels in the row above
    '''
    topIndex = p - width #location of the directly above pixel
    top = pixels[topIndex]
    topLeft = pixels[topIndex-1] if p % width != 0 else float('inf')
    topRight = pixels[topIndex+1] if (p+1) % width != 0 else float('inf')
    minIndex, minEnergy = None, float('inf')
    for adj, energy in [(topIndex-1, topLeft), (topIndex, top), (topIndex+1, topRight)]:
            if energy < minEnergy: #Ties is broken by preferring the left-most of the tied columns
                minIndex, minEnergy = adj, energy
    return (minIndex, minEnergy)


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy function),
    computes a "cumulative energy map".
    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    width, height, pixels = energy['width'], energy['height'], []
    for i in range(height):
        row = range(i * width, (i+1) * width)
        for p in row:
            value = energy['pixels'][p]
            if p >= width: # row 2 and below
                value += get_min_adj(p, pixels, width)[1]
            pixels.append(value)
    return {'height': height, 'width': width, 'pixels': pixels,}


def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam: backtracing from the bottom to the top of the cumulative energy map. F
    """
    w, h, pixels = cem['width'], cem['height'], cem['pixels']
    minIndex = min(range(w * (h-1), w * h), key=pixels.__getitem__) # index of min energy in bottom row
    seam = [minIndex]
    for _ in range(h-1):
        minIndex = get_min_adj(minIndex, pixels, w)[0]
        seam = [minIndex] + seam
    return seam


def image_without_seam(im, s):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    s = set(s)
    pixels = []
    for i,value in enumerate(im['pixels']):
        if i not in s: pixels.append(value)
    return  {'height': im['height'], 'width': im['width']-1, 'pixels': pixels,}


# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES
def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_greyscale_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def get_color_image(image):
    img_data = image.getdata()
    pixels = list(img_data)
    w, h = image.size
    return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()
