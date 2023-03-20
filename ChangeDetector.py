import os
import json
import numpy as np
from urllib.parse import urlparse
from difflib import SequenceMatcher
from PIL import Image, ImageDraw

class ChangeDetector:
    def __init__(self, contentFile1, contentFile2):
        self.content1 = json.load(open(contentFile1))
        self.content2 = json.load(open(contentFile2))
        self.diff_ratio = self.contentSimilarity()

    def overlappingArea(self, bl1, tr1, bl2, tr2):
        x = 0
        y = 1

        xDist = (min(tr1[x], tr2[x]) - max(bl1[x], bl2[x]))
        yDist = (min(tr1[y], tr2[y]) - max(bl1[y], bl2[y]))
        print(xDist, yDist)

        area = 0    
        if xDist > 0 and yDist > 0:
            area = xDist * yDist
        return area

    def getOverlappingRegions(self):
        regions_v1 = [region['position'] for region in self.content1['page_content']]
        regions_v2 = [region['position'] for region in self.content1['page_content']]
        
        for region in self.content2['page_content']:
            # bl1 = [region['position'][0], region['position'][1] + region['position'][3]]
            # tr1 = [region['position'][0] + region['position'][2], region['position'][1]]            
            bl1 = [region['position'][0], region['position'][1]]
            tr1 = [region['position'][0] + region['position'][2], region['position'][1] + region['position'][3]]

            overlappingRegions = []
            area = []
            for i in range(len(regions_v1)):
                # bl2 = [regions_v1[i][0], regions_v1[i][1] + regions_v1[i][3]]
                # tr2 = [regions_v1[i][0] + regions_v1[i][2], regions_v1[i][1]]
                bl2 = [regions_v1[i][0], regions_v1[i][1]]
                tr2 = [regions_v1[i][0] + regions_v1[i][2], regions_v1[i][1] + regions_v1[i][3]]
                overlapArea = self.overlappingArea(bl1, tr1, bl2, tr2)
                print(bl1, tr1, bl2, tr2)
                if overlapArea != 0 and overlapArea not in area:
                    overlappingRegions.append(i)
                    area.append(overlapArea)

            region['overlapping_regions'] = {'id': overlappingRegions, 'area': area}
        
        data = json.dumps(self.content2, indent=4)
        with open("pageversion_2.json", "w") as file:
            file.write(data)
        file.close()

        return

    def contentSimilarity(self):
        n1 = len(self.content1['page_content'])
        n2 = len(self.content2['page_content'])

        diff_blocks_ratio = []
        for i in range(n2):
            ratio = 0.
            for j in range(n1): # means that we are executing comparison by epsilon = 5
                # cmp_block_id = i + j
                # if cmp_block_id < 0 or cmp_block_id >= n1: continue
                tmp_ratio = SequenceMatcher(None, self.content2['page_content'][i]['content'], self.content1['page_content'][j]['content']).ratio()
                if tmp_ratio > ratio:
                    ratio = tmp_ratio
            #xprint(ratio)
            diff_blocks_ratio.append(ratio)        
        return diff_blocks_ratio

    def changesVisualizing(self):
        short_url = urlparse(self.content2['url']).netloc
        folder_path = os.listdir("./Screenshots")[-1]
        image_path = "Screenshots/" + folder_path + "/" + short_url + "_Block_1.png"
        img = Image.open(image_path)
        img_draw = ImageDraw.Draw(img)

        for contentBlock, ratio in zip(self.content2['page_content'], self.diff_ratio):
            position = contentBlock['position']
            new_img = Image.new('RGBA', (int(position[2]), int(position[3])), "red")
            paste_mask = new_img.split()[3].point(lambda i: i * (1-ratio))
            img.paste(new_img, (int(position[0]), int(position[1])), mask = paste_mask)
            
        img.save(short_url + "_compared.png")


def main():
    cd = ChangeDetector("pageversion_1.json", "pageversion_2.json")
    cd.getOverlappingRegions()
    cd.changesVisualizing()

if __name__ == "__main__":
    main()


