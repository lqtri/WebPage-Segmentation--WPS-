# Compare DOM Tree hierarchy
from DomNode import *
from difflib import SequenceMatcher
import cv2

def isSameBoundingBox(bb1, bb2):
    if abs(bb1['x'] - bb2['x']) > 5:
        return False
    if abs(bb1['y'] - bb2['y']) > 5:
        return False
    if abs(bb1['width'] - bb2['width']) > 500:
        return False
    if abs(bb1['height'] - bb2['height']) > 500:
        return False
    return True

def isSameBoxPoint(bb1, bb2):
    if abs(bb1['x'] - bb2['x']) > 5:
        return False
    if abs(bb1['y'] - bb2['y']) > 5:
        return False
    return False

def isSameAttributes(node1, node2):
    keys_2 = node2.attributes.keys()
    keys_1 = node1.attributes.keys()
    
    if len(keys_1) != len(keys_2):
        return False

    for key in keys_2:
        if key not in keys_1:
            return False
        elif SequenceMatcher(None, node2.attributes[key], node2.attributes[key]).ratio() < 0.7:
            return False
    return True


def isSimilar(node1, node2):
    if node1.nodeType != node2.nodeType or node1.nodeName != node2.nodeName:
        return False

    if node1.nodeType == 3 or node1.nodeType == 8:
        if node1.nodeValue != node2.nodeValue:
            return False
        
    if not isSameBoundingBox(node1.visual_cues['bounds'], node2.visual_cues['bounds']):
        return False
    
    if degreeOfSimilarityChildren(node1, node2) == 0:
        return False

    return True

def degreeOfSimilarityChildren(node1, node2):
    if not node1.childNodes and not node2.childNodes:
        return 1
    if not node1.childNodes or not node2.childNodes:
        return 0
    
    n = 0
    for child in node1.childNodes:
        mapList = mapChild(child, node2)
        if mapList:
            n += 1
    return n/len(node1.childNodes)
    
def mapChild(node, other):
    if not other.childNodes:
        return 
    
    mapList = []
    for child in other.childNodes:
        if isSimilar(node, child):
            mapList.append(child)
    if not mapList:
        return
    
    if len(mapList) > 1:
        max_DoS = degreeOfSimilarityChildren(node, mapList[0])
        k = 0
        for i in range(1,len(mapList)):
            DoS = degreeOfSimilarityChildren(node,mapList[i])
            if DoS > max_DoS:
                max_DoS = DoS
                k = i
        return mapList[k]
    return mapList[0]

class Comparator:
    def __init__(self):
        self.diff = []

    def domdiff(self, DomNode_1, DomNode_2):
        print(DomNode_1.nodeName, '---', DomNode_2.nodeName)
        if isSimilar(DomNode_1, DomNode_2):
            if not DomNode_2.childNodes and not DomNode_1.childNodes:
                return
    
            for child in DomNode_2.childNodes:
                other = mapChild(child, DomNode_1)
                if not other:
                    self.diff.append(child)
                else:
                    self.domdiff(child, other)
        else:
            self.diff.append(DomNode_2)
    
    def visualize(self, img_path):
        img = cv2.imread(img_path)
        for diffnode in self.diff:
            x = diffnode.visual_cues['bounds']['x']
            y = diffnode.visual_cues['bounds']['y']
            w = diffnode.visual_cues['bounds']['width']
            h = diffnode.visual_cues['bounds']['height']
            cv2.rectangle(img, (x,y), (x+w,y+h), (0, 0, 255), 3)
        cv2.imsave(img_path)