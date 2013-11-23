#! /usr/bin/env python
from __future__ import division, print_function
from collections import defaultdict
import cv2

# translates im2 by (x, y) and overlays the result over im1
def overlay(im1, im2, x, y):
    result = im1.copy()
    lbx = 0
    ubx = im1.shape[0] - x
    if x < 0:
        lbx = -x
        ubx = im1.shape[0]
    lby = 0
    uby = im1.shape[1] - y
    if y < 0:
        lby = -y
        uby = im1.shape[1]
    result[lbx+x:ubx+x,lby+y:uby+y] = 0.5*im1[lbx+x:ubx+x,lby+y:uby+y] \
        + 0.5*im2[lbx:ubx,lby:uby]
    return result


def histogram(image):
    hist = defaultdict(int)
    for x in xrange(image.shape[0]):
        for y in xrange(image.shape[1]):
            r, g, b = image[x,y]
            hist[(r,g,b)]+=1
    return hist



def histCompare(hist1, hist2):
    h1keys = set(hist1.keys())
    h2keys = set(hist2.keys())

    error = 0
    #histograms are default dicts, so accessing non-existant values gives 0
    for key in h1keys.union(h2keys):
        error += abs(hist1[key] - hist2[key])
    return error



def jointEntropy(im1, im2):

    # Hold im1 in place and slide im2

    scores = {}
    for i in xrange(-20,20):
        for j in xrange(-20,20):

            #Identify the overlapping region

            img1 = im1[i:,j:]
            img2 = im2[:-i,:-j]

            #Generate the histogram for the entire overlapping region
            img1hist = histogram(img1)
            img2hist = histogram(img2)

           
            score = histCompare(img1hist, img2hist)
            scores[(i,j)] = score

        print("i is %d" % i)
    return scores



def main():
# read image pair, as grayscale (argument 0 to imread)
    im1 = cv2.imread('reg-1-1.jpg', 0)
    im2 = cv2.imread('reg-1-2.jpg', 0)

# Compute edge map
    e1 = cv2.Canny(im1, 100, 200)
    e2 = cv2.Canny(im2, 100, 200)

    cv2.imshow('imshow', e1)
    cv2.waitKey(0)
    cv2.imshow('imshow', e2)
    cv2.waitKey(0)

    color1 = cv2.imread('reg-1-1.jpg')
    color2 = cv2.imread('reg-1-2.jpg')
    out = overlay(color1, color2, 0, 0)
    cv2.imshow('imshow', out)
    cv2.waitKey(0)
    cv2.imwrite('reg-1.jpg', out)

if __name__ == '__main__':
    main()
