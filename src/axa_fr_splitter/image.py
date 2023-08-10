import cv2
import numpy as np


def set_horizontal(image):
    (h, w) = image.shape[:2]
    if h > w:
        return rotate_bound(image, 90), 90
    return image, 0


def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (c_x, c_y) = (w // 2, h // 2)
    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    matrix = cv2.getRotationMatrix2D((c_x, c_y), -angle, 1.0)
    cos = np.abs(matrix[0, 0])
    sin = np.abs(matrix[0, 1])
    # compute the new bounding dimensions of the image
    dim_with = int((h * sin) + (w * cos))
    dim_height = int((h * cos) + (w * sin))
    # adjust the rotation matrix to take into account translation
    matrix[0, 2] += (dim_with / 2) - c_x
    matrix[1, 2] += (dim_height / 2) - c_y
    # perform the actual rotation and return the image
    return cv2.warpAffine(image, matrix, (dim_with, dim_height))


def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image, 1

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        ratio = height / float(h)
        dim = (int(w * ratio), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        ratio = width / float(w)
        dim = (width, int(h * ratio))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized, ratio


def normalize_size(target_img, max_size):
    ratio = 1
    if target_img.shape[1] > target_img.shape[0] and target_img.shape[1] > max_size:
        target_img, ratio = image_resize(target_img, width=max_size)

    if target_img.shape[0] >= target_img.shape[1] or target_img.shape[0] > max_size:
        target_img, ratio = image_resize(target_img, height=max_size)

    return target_img, ratio
