#! /usr/bin/env python
from __future__ import division, print_function
from collections import defaultdict
from itertools import izip
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
            try: r, g, b = image[x,y]
            except:
                print(type(image))
                print(image.dtype)
                raise
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


def overlappingComponents(img1, img2, i, j):

    if i is 0 and j is 0 :
        yield img1, img2
    elif i is 0:
        yield img1[i:, j:], img2[:, : -j]
        yield img1[i:, :-j], img2[:, j: ]
        yield img1[:, j:], img2[i:, :-j]
        yield img1[:, :-j], img2[i:, j: ]
    elif j is 0:
        yield img1[i:, j:], img2[:-i, : ]
        yield img1[i:, :], img2[:-i, j: ]
        yield img1[:-i, j:], img2[i:, :]
        yield img1[:-i, :], img2[i:, j: ]
    else:
        yield img1[i:, j:], img2[:-i, : -j]
        yield img1[i:, :-j], img2[:-i, j: ]
        yield img1[:-i, j:], img2[i:, :-j]
        yield img1[:-i, :-j], img2[i:, j: ]


def compareImageColors(im1, im2):
    
    hist = defaultdict(int)
    for row1, row2 in izip(im1, im2):
        for val1, val2 in izip(row1, row2):
            r1, g1, b1 = val1
            r2, g2, b2 = val2
            hist[((r1, g1, b1), (r2, g2, b2))] += 1

    return hist

def jointEntropy(im1, im2, offset=None):
    if offset is None:
        offset=20

    # Hold im1 in place and slide im2

    scores = {}
    for i in xrange(offset):
        print("i is %d" % i)
        for j in xrange(offset):
            print("j is %d" % j)
            #Iterate over the four possible ways to overlap with this offset and yield the cropped images
            for img1, img2 in overlappingComponents(im1, im2, i, j):
                #Check to make sure that neither cropped image has zero length or zero width
                #If so, skip this combination
                skip = False
                for cropped in (img1, img2):
                    if len(cropped.shape) is not 3:
                        raise Exception("Shape should have three components: " + str(cropped.shape))
                    if cropped.shape[0] == 0 or cropped.shape[1] == 0:
                        print("Skipping with dimensions %s " % str(cropped.shape))
                        skip = True
                    elif cropped.shape[2] is not 3:
                        raise Exception("Should have 3 (RGB) values, not %s" % cropped.shape)
                if skip:
                    continue
                else:
                    print("NOT skipping")
                #Generate the histogram for the entire overlapping region
                img1hist = histogram(img1)
                img2hist = histogram(img2)

               
                score = histCompare(img1hist, img2hist)
                scores[(i,j)] = score

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
