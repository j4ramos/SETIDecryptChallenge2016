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

import os
import re
import sys
import logging
import requests
import numpy as np
from PIL import Image
from collections import Counter
from pymongo import MongoClient

CONNECTION = MongoClient()
COLLECTION = CONNECTION.SETI2016.Images
FORMAT = '%(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO, stream=sys.stdout)

URL = 'http://www2.mps.mpg.de/homes/heller/downloads/files/SETI_message.txt'


def generate_matrix(url=URL):
    """
    Grabs the text file from the url provided, and converts it into a 5299 x 359 numpy.ndarray
    which is effectively a matrix.
    :return: numpy.ndarray
    """
    filename = './message.txt'
    if os.path.exists(filename):
        logging.info('%(f)s found.  Reading message from file...', {'f': filename})
        with open(filename) as f:
            text = f.read()
    else:
        print '{f} not found. Getting message from website...'.format(f=filename)
        text = requests.get(URL).text
        with open(filename, 'w') as f:
            f.write(text)
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


def save_matrices_to_individual_files(matrices):
    for i, matrix in enumerate(matrices):
        with open('./matrices/matrix{}.txt'.format(i), 'a') as f:
            l = [''.join(r) for r in matrix.astype(str)]
            [f.write(r + '\n') for r in l]


def convert_row_to_string(row):
    assert isinstance(row, (np.ndarray, np.array))
    _row = row/255
    return _row.astype(str)


def count_ones(row):
    counter = Counter(row)
    return counter['1']


def strip_surrounding_zeros_from_binary_number(string, regex):
    if count_ones(string) > 1:
        result = regex.match(string).group()
        return result


def update_img_in_mongo(img_dict):
    return COLLECTION.update({'_id': img_dict['_id']}, img_dict, upsert=True)


def create_img_info_dicts(num_images):
    image_info_dicts = list()
    for i in xrange(num_images):
        _img_dict = dict()
        _img_dict['_id'] = i
        _img_dict['name'] = 'Image{}'.format(i)
        _img_dict['width'] = 359
        _img_dict['height'] = 757
        image_info_dicts.append(_img_dict)
    return image_info_dicts


def print_headers(header_array, image_details):
    """
    Print out the first couple rows from each image.
    :param header_array: numpy array conisisting of two items.
    """
    # Each item in header_array is a list of binary strings.
    # The first item is a list containing the binary digits from each image's first row.
    # The second item is a list containing the binary digits from each image's second row.
    first_row_list, second_row_list = header_array[0], header_array[1]
    pattern = re.compile('\d.*1')
    count = 0
    for i, k in zip(first_row_list, second_row_list):
        print '--------------------------------------------------------------------------------'
        binary_string1, binary_string2 = ''.join(i), ''.join(k)
        logging.info('\n%(row1)s\n%(row2)s', {'row1': binary_string1, 'row2': binary_string2})
        print 'Binary numbers; stripped zeros'
        if '1' in binary_string1 and count_ones(binary_string1) > 1:
            first_one_idx = binary_string1.find('1')
            bn1 = pattern.match(binary_string1[first_one_idx:]).group()
            print 'Index: {idx}; {n1}'.format(idx=first_one_idx, n1=bn1)
            image_details[count]['row1Binary'] = bn1
            image_details[count]['row1BinaryIdx'] = first_one_idx
        if '1' in binary_string2 and count_ones(binary_string2) > 1:
            first_one_idx = binary_string2.find('1')
            bn2 = pattern.match(binary_string2[first_one_idx:]).group()
            print 'Index: {idx}; {n2}'.format(idx=first_one_idx, n2=bn2)
            image_details[count]['row2Binary'] = bn2
            image_details[count]['row2BinaryIdx'] = first_one_idx
        print
        count += 1


def main():
    matrix = generate_matrix()
    img_height = calculate_image_height(matrix)  # equals 757.0
    logging.info('Image height:     {}'.format(img_height))
    num_images = len(matrix) / float(img_height)  # equals 7.0 even
    num_images = int(num_images)
    logging.info('Number of images: {}'.format(num_images))

    # Split matrix into separate matrices based on img_height
    matrices = [matrix[i*img_height:img_height*(i+1)] for i in xrange(num_images)]

    # save_matrices_to_individual_files(matrices)

    img_matrices = [m*255 for m in matrices]
    raw_img_headers = np.array([
        [row[0].astype(str) for row in matrices],  # Seems like the first row is a code
        [row[1].astype(str) for row in matrices]   # Seems like the second row is a code
    ])

    image_dicts = create_img_info_dicts(num_images)
    print_headers(raw_img_headers, image_dicts)

    # Next line is for storing data into MongoDB.
    # map(update_img_in_mongo, image_dicts)

    images = [Image.fromarray(m) for m in img_matrices]
    for i, image in enumerate(images):
        image.save('./images/img{num}.png'.format(num=i))
        image.show()


if __name__ == '__main__':
    main()
