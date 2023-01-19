import time
import functools
import os
import json

from urllib.parse import urlparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from BlockExtraction import BlockExtraction
from BlockVo import BlockVo

from ImageOut import ImageOut
from CssBox import CssBox
from DomNode import DomNode


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
        self.setDriver()
        # self.imgOut = ImageOut()
        # self.imgOut.outImg(self.browser, self.url, self.fileName)
        self.getDomTree()
        self.recList = []
               
    def service(self):
        print('\n[Block Extraction]')
        be = BlockExtraction()
        block = be.service(self.url, self.nodeList)
        blockList = be.blockList
        # self.imgOut.outBlock(blockList, self.fileName, 0)
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
            newpath = r'Screenshots/'+ parse_object.netloc +'_'+str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) +'/'
            self.fileName = newpath + parse_object.netloc
            os.makedirs(newpath)
        except (TypeError, AttributeError):
            print ("Invalid address: " + str(urlStr))
      
    def setDriver(self):
        CHROME_PATH = r"/usr/bin/google-chrome-stable"  # chrome path
        CHROMEDRIVER_PATH = r"/usr/lib/chromium-browser/chromedriver" # driver path
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
        

    def toDOM(self, obj, parentNode=None):
        if (isinstance(obj,str)):
            json_obj = json.loads(obj)  #use json lib to load our json string
        else:
            json_obj = obj
        nodeType = json_obj['nodeType']
        node = DomNode(nodeType)
        if nodeType == 1: #ELEMENT NODE
            node.createElement(json_obj['tagName'])
            attributes = json_obj['attributes']
            if attributes != None:
                node.setAttributes(attributes)
            visual_cues = json_obj['visual_cues']
            if visual_cues != None:
                node.setVisual_cues(visual_cues)
        elif nodeType == 3:
            node.createTextNode(json_obj['nodeValue'], parentNode)
            if node.parentNode != None:
                visual_cues = node.parentNode.visual_cues
                if visual_cues != None:
                    node.setVisual_cues(visual_cues)    
        else:
            return node
            
        self.nodeList.append(node)
        if nodeType == 1:
            childNodes = json_obj['childNodes']
            for i in range(0, len(childNodes)):
                if(childNodes[i]['nodeType'] == 1):
                    node.appendChild(self.toDOM(childNodes[i],node))
                if childNodes[i]['nodeType'] == 3:
                    try:
                        if not childNodes[i]['nodeValue'].isspace():
                            node.appendChild(self.toDOM(childNodes[i],node))
                    except KeyError:
                        print('abnormal text node')
                    
        return node
    
    def toHTMLFile(self, page_source):
        with open("page_source.html", "w") as file:
            file.write(str(page_source))
        
    def getDomTree(self):
        self.browser.get(self.url) 
        self.toHTMLFile(self.browser.page_source)
        time.sleep(3)      

        file = open("dom.js", 'r')
        jscript = file.read()
        jscript += '\nreturn JSON.stringify(toJSON(document.getElementsByTagName("BODY")[0]));'
        x = self.browser.execute_script(jscript)
        self.toDOM(x)
        
    def setRound(self,round):
        self.Round = round
        
    @staticmethod
    def sepCompare(sep1, sep2):
        if sep1.compareTo(sep2) < 0:
            return -1
        elif sep1.compareTo(sep2) > 0:
            return 1
        else: return 0