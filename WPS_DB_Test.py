import sys
import WPS_DB as Wpsdb
from ImageOut import ImageOut
from urllib.parse import unquote
from ElementsClustering import Clustering
from sklearn.cluster import DBSCAN
import numpy as np
from urllib.parse import urlparse
from datetime import datetime

import ContentExtractor as CE

def main():
    num_of_arg = len(sys.argv)
    if num_of_arg < 2:
        print("PLease paste the web page link at the second argument!")
        return
    elif num_of_arg > 2:
        print("Number of arguments is invalid!")
        return

    wpsdb = Wpsdb.Wpsdb(unquote(sys.argv[1], encoding="utf-8"))
    blocks = wpsdb.service()

    pageWidth = wpsdb.nodeList[0].visual_cues['bounds']['width']
    pageHeight = wpsdb.nodeList[0].visual_cues['bounds']['height']
    print('Page width: ', pageWidth, ', Page height: ', pageHeight,'\n')

    cluster = Clustering(blocks, pageWidth, pageHeight, wpsdb.nodeList[0])
    cluster.DBSCAN()
    
    imgOut = ImageOut()
    imgOut.outBlock(cluster.blocks, wpsdb.fileName, 1)

    ce = CE.ContentExtractor(sys.argv[1], wpsdb.browser, cluster.blocks)
    ce.contentExtracting();

main()