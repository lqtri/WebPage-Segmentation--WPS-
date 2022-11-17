import math
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.mixture import GaussianMixture

class Clustering:
    def __init__(self, blocks, lim_v, lim_t, pageWidth, pageHeight, domRoot):
        self.blocks = blocks
        self.lim_v = lim_v  #the limit visual distance
        self.lim_t = lim_t  #the limit text density distance
        self.pageWidth = pageWidth
        self.pageHeight = pageHeight
        self.domRoot = domRoot
        
    def visual_distance(self, b1, b2):
        c1_x = b1.x+b1.width/2
        c1_y = b1.y+b1.height/2
        c2_x = b2.x+b2.width/2
        c2_y = b2.y+b2.height/2
        
        clear_space = max(abs(c1_x-c2_x)-(b1.width+b2.width)/2, abs(c1_y-c2_y)-(b1.height+b2.height)/2)
        return np.where(clear_space>0, clear_space, 0)

    def logic_distance(self, b1, b2):
        b1_path = []
        temp1 = b1.parent
        while temp1 != None:
            b1_path.append(temp1)
            temp1 = temp1.parent
        
        step =       0
        temp2 = b2.parent
        while temp2 not in b1_path:
            step += 1
            temp2 = temp2.parent
        
        idx = b1_path.index(temp2)
        return abs(step-idx)


    def text_density_difference(b1, b2):
        return

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
        alpha = self.pageWidth / self.find_depth_tree(self.domRoot)
        total_distance = 0
        valid_distance_count = 0

        for i in range(0,n):
            tmp_vector = []
            for j in range(0,n):
                alignment_distance = 0
                visual_distance = self.visual_distance(blocks[i], blocks[j])
                logic_distance = self.logic_distance(blocks[i],blocks[j])
                if visual_distance < self.pageWidth/2:
                    valid_distance_count += 1
                    total_distance += visual_distance
                tmp_vector.append(visual_distance + alpha*logic_distance)
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

    ### STAGE 2
    def regrouping(self, blocks):
        while True:
            loop = True
            for i in range(len(blocks)):
                for j in range(i+1,len(blocks)):
                    if visual_distance(blocks[i], blocks[j]) < self.lim_v and text_density_difference(blocks[i], blocks[j]) < self.lim_t:
                        blocks[i] = merge_block(blocks[i], blocks[j])
                        loop = False
            if loop:
                break
        return 