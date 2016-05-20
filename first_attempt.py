# Code from my initial attempt posted on Twitter
# https://twitter.com/ramojol/status/727965914746871809

import requests
import numpy as np
from PIL import Image

url = 'http://www2.mps.mpg.de/homes/heller/downloads/files/SETI_message.txt'
text = requests.get(url).text

# Create a numpy matrix from the binary string
char_vector = np.array([x for x in text])
mat = np.reshape(char_vector, (-1, 359)).astype(np.uint8)*255

# Create an image from the matrix
img = Image.fromarray(mat)
img.save('astro.png')
