import numpy as np
import cv2

img_height, img_width = 64, 64
n_channels = 4
transparent_img = np.zeros((img_height, img_width, n_channels), dtype=np.uint8)

cv2.imwrite("./transparent_img.png", transparent_img)