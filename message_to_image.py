# This is a call for a fun scientific challenge.

# Suppose a telescope on Earth receives a series of pulses from a fixed, unresolved source beyond the solar system.
# The source is a star about 50 light years from Earth. The pulses are in the form of short/long signals and they
# are received in a very narrow band around an electromagnetic frequency of 452.12919 MHz.
# A computer algorithm identifies the artificial nature of the pulses. It turns out the pulses carry a message.
# The pulses signify binary digits. Suppose further that you were, by whatsoever reason, put in charge of decoding
# this message.
#
# If you successfully decrypted the message, you should be able to answer the following questions:
#
# 1. What is the typical body height of our interstellar counterparts?
# 2. What is their typical lifetime?
# 3. What is the scale of the devices they used to submit their message?
# 4. Since when have they been communicating interstellar?
# 5. What kind of object do they live on?
# 6. How old is their stellar system?
#
# These are the rules.
#
# 1. No restrictions on collaborations.
# 2. Open discussion (social networks etc.) of possible solutions strongly encouraged.
# 3. 3 hints to the solutions can be offered as per request.
# 4. Send your solutions to me via e-mail (heller@mps.mpg.de), twitter (@DrReneHeller) or facebook (DrReneHeller).
#    Human-readable format and the format of the message are allowed.
# 5. On 3 June 2016, a list of the successful SETI crackers (in chronological order) will be released.

import requests
import numpy as np
from PIL import Image

URL = 'http://www2.mps.mpg.de/homes/heller/downloads/files/SETI_message.txt'


def generate_matrix(url=URL):
    """
    Grabs the text file from the url provided, and converts it into a 5299 x 359 numpy.ndarray
    which is effectively a matrix.
    :return: numpy.ndarray
    """
    text = requests.get(URL).text
    # Row-length determined by number of consecutive ones at the beginning, 359
    matrix = np.reshape(np.array([x for x in text]), (-1, 359)).astype(np.uint8)
    return matrix


def calculate_image_height(matrix):
    """
    Original message seems to be divided into 7 images.
    The first set of rows only have a 1 in the last position which seems to indicate
    the height of each image.
    This is overkill, but hey! Someone might want to learn about generators...
    :param matrix: numpy.ndarray created from message text
    :return: integer height in number of rows
    """
    def _generator():
        for row in matrix[1:]:  # skip first row
            _sum = sum(row)
            if _sum == 1:
                yield _sum
            else:
                break
    image_height = sum(x for x in _generator()) + 1  # add 1 for the skipped first row
    return image_height

if __name__ == '__main__':
    mtx = generate_matrix()
    img_height = calculate_image_height(mtx)  # equals 757.0
    num_images = len(mtx) / float(img_height)  # equals 7.0 even
    num_images = int(num_images)
    img_matrices = [mtx[i*img_height:img_height*(i+1)]*255 for i in xrange(num_images)]
    img_details = [m[0]/255 for m in img_matrices]  # Seems like the first row is a code
    for i in img_details:
        print i, sum(i)
    images = [Image.fromarray(m) for m in img_matrices]
    for i, image in enumerate(images):
        # image.save('./img{num}.png'.format(num=i))
        image.show()
