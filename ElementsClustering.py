import math
import numpy as np
from sklearn.cluster import DBSCAN

class Clustering:
    def __init__(self, blocks, lim_v, lim_t, pageWidth, pageHeight, domRoot):
        self.blocks = blocks
        self.lim_v = lim_v  #the limit visual distance
        self.lim_t = lim_t  #the limit text density distance
        self.pageWidth = pageWidth
        self.pageHeight = pageHeight
        self.domRoot = domRoot

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
        return abs(step-idx)

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
        if (abs(b2.x - b1.x) <= 5): return 1
        elif (abs(b2.x+b2.width - b1.x) <= 5): return 1
        elif (abs(b2.x - b1.x-b1.width) <= 5): return 1
        elif (abs(b2.x +b2.width- b1.x-b1.width) <= 5): return 1

        elif (abs(b2.y - b1.y) <= 5): return 1
        elif (abs(b2.y + b2.height- b1.y) <= 5): return 1
        elif (abs(b2.y - b1.y-b1.height) <= 5): return 1
        elif (abs(b2.y +b2.height- b1.y - b1.height) <= 5): return 1
        return 0 

    def similarity_distance_matrix(self, blocks):
        n = len(blocks) 
        matrix = []
        alpha = (self.pageWidth+self.pageHeight)/2 / self.find_depth_tree(self.domRoot)
        total_distance = 0
        valid_distance_count = 0

        for i in range(0,n):
            tmp_vector = []
            for j in range(0,n):
                visual_distance = self.visual_distance(blocks[i], blocks[j])
                logic_distance = self.logic_distance(blocks[i],blocks[j])
                if visual_distance < self.pageWidth/2:
                    valid_distance_count += 1
                    total_distance += visual_distance
                    
                alignment_distance = self.isAlign(blocks[i],blocks[j])
                dist = visual_distance + alpha*(logic_distance - alignment_distance)
                if dist < 0:tmp_vector.append(0)
                else:tmp_vector.append(dist)
            matrix.append(tmp_vector)

        average_distance = total_distance / (valid_distance_count+1)

        return np.array(matrix), average_distance

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

        clustering = DBSCAN(eps = average_distance ,min_samples=1, algorithm='brute' ,metric='precomputed').fit(similarity_matrix)
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