import json
import os
from os import path

class ContentExtractor:
    def __init__(self, webdriver, blocks):
        self.webdriver = webdriver
        self.blocks = blocks

    def getContent(self, block):
        file = open("findAllElementsWithinRegion.js", 'r')
        get_content_js = file.read()
        jscript = get_content_js + "\n return getElementsInRegion("+str(block.x)+","+str(block.y)+","+str(block.width)+","+str(block.height)+")"
        elements = self.webdriver.execute_script(jscript)

        content = ""
        for element in elements:
            content += element.text
        return content
    
    def contentExtracting(self):
        data = {"page_content" : []}
        for i in range(len(self.blocks)):
            content = self.getContent(self.blocks[i])
            data["page_content"].append({"block_id" : i, "position" : (self.blocks[i].x, self.blocks[i].y, self.blocks[i].width, self.blocks[i].height), "content" : content})
        json_data = json.dumps(data, indent=4)
        
        if path.exists("content1.json") and path.exists("content2.json"):
            with open("content1.json", "w") as file:
                file.write(json_data)
            os.remove("content2.json")
        elif path.exists("content1.json"):
            with open("content2.json", "w") as file:
                file.write(json_data)
        else:
            with open("content1.json", "w") as file:
                file.write(json_data)


            

    