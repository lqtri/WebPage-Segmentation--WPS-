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
        self.diff_ratio = self.similar()

    def similar(self):
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
            print(ratio)
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
    cd = ChangeDetector("content1.json", "content2.json")
    cd.changesVisualizing()

if __name__ == "__main__":
    main()


