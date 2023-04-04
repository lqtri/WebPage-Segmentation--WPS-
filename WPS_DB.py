import os
import json

from urllib.parse import urlparse
from datetime import datetime
from selenium import webdriver
from BlockExtraction import BlockExtraction
from ImageOut import ImageOut
from DomNode import DomNode


def toHTMLFile(page_source):
    with open("page_source.html", "w") as file:
        file.write(str(page_source))
    file.close()


class Wpsdb:
    PDoc = 1
    Round = 1
    url = None
    fileName = None
    browser = None
    count = 0
    imgOut = None
    html = None
    cssBoxList = dict()
    nodeList = []
    count3 = 0

    def __init__(self, urlStr):
        self.setUrl(urlStr)

        print("Web driver setting...")
        self.setDriver()
        print("Done!\n")

        print("Web page image shooting...")
        self.imgOut = ImageOut()
        self.imgOut.outImg(self.browser, self.url, self.fileName)
        print("Done!\n")

        print("Web page DOM tree getting...")
        self.getDomTree()
        print("Done!\n")

        self.recList = []

    def service(self):
        print("Block extracting...")
        be = BlockExtraction()
        block = be.service(self.url, self.nodeList)
        blockList = be.blockList

        self.imgOut.outBlock(blockList, self.fileName, 0)
        return blockList

    def checkDoc(self, blocks):
        for blockVo in blocks:
            if blockVo.Doc < self.PDoc:
                return True
        return False

    def setUrl(self, urlStr):
        try:
            if urlStr.startswith('https://') or urlStr.startswith('http://'):
                self.url = urlStr
            else:
                self.url = 'http://' + urlStr
            parse_object = urlparse(self.url)
            newpath = r'Snapshots/' + parse_object.netloc + '_' + str(
                datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) + '/'
            self.fileName = newpath + parse_object.netloc
            os.makedirs(newpath)
        except (TypeError, AttributeError):
            print("Invalid address: " + str(urlStr))

    def setDriver(self):
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument('--headless')
        self.browser = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver', options=firefox_options)
        self.browser.implicitly_wait(1000)

    def toDOM(self, obj, parentNode=None):
        if isinstance(obj, str):
            json_obj = json.loads(obj)
        else:
            json_obj = obj
        nodeType = json_obj['nodeType']
        node = DomNode(nodeType)
        if nodeType == 1:  # ELEMENT NODE
            node.createElement(json_obj['tagName'])
            attributes = json_obj['attributes']
            if attributes is not None:
                node.setAttributes(attributes)
            visual_cues = json_obj['visual_cues']
            if visual_cues is not None:
                node.setVisual_cues(visual_cues)
        elif nodeType == 3:
            node.createTextNode(json_obj['nodeValue'], parentNode)
            if node.parentNode is not None:
                visual_cues = node.parentNode.visual_cues
                if visual_cues is not None:
                    node.setVisual_cues(visual_cues)
        else:
            return node

        self.nodeList.append(node)
        if nodeType == 1:
            childNodes = json_obj['childNodes']
            for i in range(0, len(childNodes)):
                if childNodes[i]['nodeType'] == 1:
                    node.appendChild(self.toDOM(childNodes[i], node))
                if childNodes[i]['nodeType'] == 3:
                    try:
                        if not childNodes[i]['nodeValue'].isspace():
                            node.appendChild(self.toDOM(childNodes[i], node))
                    except KeyError:
                        print('abnormal text node')

        return node

    def getDomTree(self):
        file = open("dom.js", 'r')
        jscript = file.read()
        file.close()

        jscript += '\nreturn JSON.stringify(toJSON(document.getElementsByTagName("BODY")[0]));'
        x = self.browser.execute_script(jscript)

        json_object = json.dumps(x, indent=4)
        with open(self.fileName + "_dom.json", "w") as file:
            file.write(json_object)
        file.close()

        # Kill driver
        self.browser.close()
        self.toDOM(x)
