import sys
import Vips
from ImageOut import ImageOut
from urllib.parse import unquote
from ElementsClustering import Clustering
from sklearn.cluster import DBSCAN
import numpy as np

def main():
    num_of_arg = len(sys.argv)
    if num_of_arg < 2:
        print("PLease paste the web page link at the second argument!")
        return
    elif num_of_arg > 2:
        print("Number of arguments is invalid!")
        return

    vips = Vips.Vips(unquote(sys.argv[1], encoding="utf-8"))
    vips.setRound(10)
    blocks = vips.service()

    pageWidth = vips.nodeList[0].visual_cues['bounds']['width']
    pageHeight = vips.nodeList[0].visual_cues['bounds']['height']
    print('Page width: ', pageWidth, ', Page height: ', pageHeight,'\n')

    cluster = Clustering(blocks, 1, 1, pageWidth, pageHeight, vips.nodeList[0])
    cluster.DBSCAN()
    cluster.DBSCAN()
     
    imgOut = ImageOut()
    imgOut.outBlock(cluster.blocks, vips.fileName,1)
    print(len(blocks)," clusters ---> ",len(cluster.blocks), " clusters")

main()