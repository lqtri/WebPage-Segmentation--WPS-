import math
import numpy as np
import copy as cp
from sklearn.cluster import DBSCAN

class Clustering:
    def __init__(self, blocks, pageWidth, pageHeight, domRoot):
        self.blocks = blocks
        self.outlier_blocks = self.cleanse()
        self.n = len(blocks)
        self.pageWidth = pageWidth
        self.pageHeight = pageHeight
        self.domRoot = domRoot
        self.alpha = (self.pageHeight) /self.find_depth_tree(self.domRoot)
        print('alpha: ',self.alpha)
    
    def cleanse(self):
        outlier_blocks = []
        for block in self.blocks:
            if block.width <= 1 or block.height <= 1:
                outlier_blocks.append(cp.deepcopy(block))
                self.blocks.remove(block)
        return outlier_blocks

    def visual_distance(self, b1, b2):
        x_cor = (b1.x-b2.x)*(b1.x+b1.width-b2.x-b2.width)
        y_cor = (b1.y-b2.y)*(b1.y+b1.height-b2.y-b2.height)
        dx = np.where(x_cor<=0,0,min(abs(b1.x-b2.x),abs(b1.x+b1.width-b2.x-b2.width)))
        dy = np.where(y_cor<=0,0,min(abs(b1.y-b2.y),abs(b1.y+b1.height-b2.y-b2.height)))
        return dx + dy

    def logic_distance(self, b1, b2):
        b1_path = []
        temp1 = b1.parent
        while temp1 != None:
            b1_path.append(temp1)
            temp1 = temp1.parent
        
        step = 0
        temp2 = b2.parent
        while temp2 not in b1_path:
            step += 1
            temp2 = temp2.parent
        
        idx = b1_path.index(temp2)
        return abs(step+idx-1)

    ### STAGE 1
    def find_depth_tree(self, root):
        if root == None:
            return 0
        max_depth = 0
        for child in root.childNodes:
            temp = self.find_depth_tree(child)
            if temp > max_depth: 
                max_depth = temp
        return max_depth + 1

    def isAlign(self, b1, b2):
        res =0
        if (abs(b2.x - b1.x) <= 2): res+= 0.8
        elif (abs(b2.x +b2.width- b1.x-b1.width) <= 2): res+= 0.8

        elif (abs(b2.y - b1.y) <= 2): res+= 0.8
        elif (abs(b2.y +b2.height- b1.y - b1.height) <= 2): res+= 0.8

        if res == 0.8:
          if b2.width == b1.width : res+=0.2
          if b2.height == b1.height: res+=0.2

        return res

    def similarity_distance_matrix(self, blocks):
        total_valid_distance = 0
        valid_distance_count = 0

        matrix = []
        for i in range(0, self.n):
            matrix.append([0]*self.n)
        matrix = np.array(matrix)

        for i in range(0,self.n):
            for j in range(i+1,self.n):
                visual_distance = self.visual_distance(blocks[i], blocks[j])* self.n/self.alpha
                logic_distance = self.logic_distance(blocks[i],blocks[j])
                if visual_distance < self.pageHeight/2:
                    valid_distance_count += 1
                    total_valid_distance += visual_distance
                    
                alignment_distance = self.isAlign(blocks[i],blocks[j])
                dist = visual_distance + self.alpha*(logic_distance *(2-alignment_distance)/2)
                
                matrix[i][j] = matrix[j][i] = np.where(dist>0, dist, 0)

        average_distance = total_valid_distance / (valid_distance_count+1)
        print('Epsilon: ', average_distance)
        return matrix, average_distance

    def get_indice(self, list, value):
        return [i for i,val in enumerate(list) if val==value]

    def get_elements(self, list, indices_list):
        return [list[i] for i in indices_list]

    def merge_blocks(self,blocks_list):
        x = min([block.x for block in blocks_list])
        y = min([block.y for block in blocks_list])
        width = max([block.width+block.x for block in blocks_list])
        height = max([block.height+block.y for block in blocks_list])
        blocks_list[0].x = x
        blocks_list[0].y = y
        blocks_list[0].width = width-x
        blocks_list[0].height = height-y
        return blocks_list[0]

    def DBSCAN(self):
        similarity_matrix, average_distance = self.similarity_distance_matrix(self.blocks)
        clustering = DBSCAN(eps = average_distance ,min_samples=2, algorithm='brute' ,metric='precomputed').fit(similarity_matrix)
        labels = clustering.labels_
        max_cluster_index = max(labels)

        #Add noise block
        noise_block_indice = self.get_indice(labels,-1)
        new_blocks_list = self.get_elements(self.blocks, noise_block_indice)

        #Add cluster candidate
        for i in range(max_cluster_index+1):
            element_indices = self.get_indice(labels, i)
            new_blocks_list.append(self.merge_blocks(self.get_elements(self.blocks, element_indices)))
            
        self.blocks = new_blocks_list