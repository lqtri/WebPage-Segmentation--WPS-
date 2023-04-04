import sys
import WPS_DB as Wpsdb
import BlockVo
from ImageOut import ImageOut
from urllib.parse import unquote
from ElementsClustering import *
from opencv_elements_extractor import *


def main():
    num_of_arg = len(sys.argv)
    if num_of_arg < 2:
        print("Please paste the web page link at the second argument!")
        return
    elif num_of_arg > 2:
        print("Number of arguments is invalid!")
        return

    wpsdb = Wpsdb.Wpsdb(unquote(sys.argv[1], encoding="utf-8"))
    blocks = wpsdb.service()

    pageWidth = wpsdb.nodeList[0].visual_cues['bounds']['width']
    pageHeight = wpsdb.nodeList[0].visual_cues['bounds']['height']

    CV_Extractor = Extractor(wpsdb.fileName + '.png', blocks)
    CV_Extractor.visualize()
    CV_blocks = CV_Extractor.regions

    CV_BlockVo = []
    for CV_block in CV_blocks:
        new_block = BlockVo.BlockVo()
        new_block.x = CV_block[0]
        new_block.y = CV_block[1]
        new_block.width = CV_block[2]
        new_block.height = CV_block[3]
        CV_BlockVo.append(new_block)

    print("\nBlocks clustering...")
    cluster = Clustering(blocks, pageWidth, pageHeight, wpsdb.nodeList[0])
    print("+ Alpha: ", cluster.alpha)
    print("+ DBSCAN...")
    cluster.DBSCAN()
    print("Done!\n")

    print("Segmentation blocks\n")
    for i in range(len(cluster.blocks)):
        print(cluster.blocks[i].x, ", ", cluster.blocks[i].y, ", ", cluster.blocks[i].width, ", ",
              cluster.blocks[i].height)

    imgOut = ImageOut()
    imgOut.outBlock(cluster.blocks + CV_BlockVo, wpsdb.fileName, 1)
    print("Done!\n")


main()
