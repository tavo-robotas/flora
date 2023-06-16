import sys
import os
import numpy as np
from os import walk
import cv2

# python resize_images.py width height input_dir output_dir
width = int(sys.argv[1])
height = int(sys.argv[2])
input_dir = sys.argv[3]
out_dir = sys.argv[4]

if len(sys.argv) > 5:
    print("Too many arguments - " + str(len(sys.argv)) +
          " specify width, height, input directory and output directory.")
    sys.exit(0)

if len(sys.argv) < 5:
    print("Not enough arguments - " + str(len(sys.argv)) +
          " specify width, height, input directory and output directory.")
    sys.exit(0)

print("Working...")
images = []
ext = (".jpeg", ".jpg", ".png")

for (dirpath, dirnames, filenames) in walk(input_dir):
    for filename in filenames:
        if filename.endswith(ext):
            images.append(os.path.join(dirpath, filename))

for image in images:
    img = cv2.imread(image, cv2.IMREAD_UNCHANGED)

    h, w = img.shape[:2]
    pad_bottom, pad_right = 0, 0
    ratio = w / h

    if h > height or w > width:
        print('shrinking')
        interp = cv2.INTER_AREA
    else:
        print('stretching')
        interp = cv2.INTER_CUBIC

    w = width
    h = round(w / ratio)
    if h > height:
        h = height
        w = round(h * ratio)
    pad_bottom = abs(height - h)
    pad_right = abs(width - w)

    scaled_img = cv2.resize(img, (w, h), interpolation=interp)
    padded_img = cv2.copyMakeBorder(
        scaled_img, 0, pad_bottom, 0, pad_right, borderType=cv2.BORDER_CONSTANT, value=[0, 0, 0])

    if not cv2.imwrite(os.path.join(out_dir, os.path.basename(image)), padded_img):
        raise Exception("Could not write image")
    else:
        print('Written')

print("Completed!")
