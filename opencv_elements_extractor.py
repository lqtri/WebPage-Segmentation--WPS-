import os
import cv2
import numpy
from PIL import Image, ImageDraw

def calculate_contour_distance(contour1, contour2): 
    x1, y1, w1, h1 = cv2.boundingRect(contour1)
    c_x1 = x1 + w1/2
    c_y1 = y1 + h1/2

    x2, y2, w2, h2 = cv2.boundingRect(contour2)
    c_x2 = x2 + w2/2
    c_y2 = y2 + h2/2

    return max(abs(c_x1 - c_x2) - (w1 + w2)/2, abs(c_y1 - c_y2) - (h1 + h2)/2)

def merge_contours(contour1, contour2):
    return numpy.concatenate((contour1, contour2), axis=0)

def agglomerative_cluster(contours, threshold_distance=20.0):
    current_contours = contours
    while len(current_contours) > 1:
        min_distance = None
        min_coordinate = None

        for x in range(len(current_contours)-1):
            for y in range(x+1, len(current_contours)):
                distance = calculate_contour_distance(current_contours[x], current_contours[y])
                if min_distance is None:
                    min_distance = distance
                    min_coordinate = (x, y)
                elif distance < min_distance:
                    min_distance = distance
                    min_coordinate = (x, y)

        if min_distance < threshold_distance:
            index1, index2 = min_coordinate
            current_contours[index1] = merge_contours(current_contours[index1], current_contours[index2])
            del current_contours[index2]
        else: 
            break

    return current_contours

def isSimilar(block1, block2):
    if abs(block1[0] - block2[0]) < 100 and \
        abs(block1[1] - block2[1]) < 100 and \
        abs(block1[2] - block2[2]) < 100 and \
        abs(block1[3] - block2[3]) < 100:
            return True
    return False


class Extractor:
    def __init__(self, img_path, DOM_blocks):
        self.img_path = img_path
        self.img_hid_blocks_path = None
        self.img = None
        self.DOM_blocks = DOM_blocks

        self.hideRegions(self.DOM_blocks)
        self.regions = self.detectRegions()

    def hideRegions(self, blocks):
        img = Image.open(self.img_path)
        img_draw = ImageDraw.Draw(img)

        for block in blocks:
            img_draw.rectangle([block.x, block.y, block.x+block.width, block.y+block.height], fill = '#000000', outline = 'black')
        
        i = self.img_path.rfind('/')
        save_path = self.img_path[:(i+1)]
        img_name = self.img_path[(i+1):].split('.png')[0]
        self.img_hid_blocks_path = save_path + img_name + '_hid.png'
        img.save(self.img_hid_blocks_path)

    def detectRegions(self):
        mser = cv2.MSER_create()

        self.img = cv2.imread(self.img_hid_blocks_path)
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        regions, _ = mser.detectRegions(gray)
        hulls = [cv2.convexHull(p.reshape(-1, 1, 2)) for p in regions]
        print('Number of contours: ', len(hulls))

        filtered_contour = []
        number_of_exists = 0
        for contour in hulls:
            x1,y1 = contour[0][0]
            approx = cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour, True), True)
            if len(approx) == 4:
                exist = False
                for block in self.DOM_blocks:
                    if isSimilar([block.x, block.y, block.width, block.height], cv2.boundingRect(contour)):
                        exist = True
                        break
                if not exist:
                    filtered_contour.append(contour)
                else:
                    number_of_exists += 1
            else: 
                filtered_contour.append(contour)

        print('Number of contours that are DOM blocks: ', number_of_exists)

        height, width, _ = self.img.shape
        min_x, min_y = width, height
        max_x = max_y = 0

        # computes the bounding box for the contour
        print('New contours found: ', len(filtered_contour))

        final_contours = agglomerative_cluster(filtered_contour)
        print('New blocks found: ', len(final_contours))

        return [cv2.boundingRect(contour) for contour in final_contours]

    def visualize(self):
        for region in self.regions:
            x,y,w,h = region
            cv2.rectangle(self.img, (x,y), (x+w,y+h), (0, 0, 255), 3)
        cv2.imshow('img', self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def main():
    e = Extractor('/Users/tri.qle/Documents/Web Segmentation/source/WebPage-Segmentation--WPS-/Screenshots/stackoverflow.com_2023_03_23_14_19_12/stackoverflow.com_hid.png')
    e.visualize()

if __name__ == "__main__":
    main()