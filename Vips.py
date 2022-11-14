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


class Vips:
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
        self.imgOut = ImageOut()
        self.imgOut.outImg(self.browser, self.url, self.fileName)
        self.getDomTree()
        self.recList = []
               
    def service(self):
        print('-----------------------------Block Extraction------------------------------------')
        be = BlockExtraction()
        block = be.service(self.url, self.nodeList)
        blockList = be.blockList
        self.imgOut.outBlock(blockList, self.fileName, 0)
        return blockList
        '''
        i = 0
        while self.checkDoc(blockList) and i<self.Round:
            print ("blockList.size::", len(blockList))
            self.imgOut.outBlock(blockList, self.fileName,i)
            ImageOut.outText(self.fileName, blockList, i)                    
            print("-----------------------------Separator Detection---------------------------------"+str(i))
            sd = SeparatorDetection(self.browser.get_window_size()['width'], self.browser.get_window_size()['height'])
            verticalList = []
            verticalList.extend(sd.service(blockList, SeparatorVo.TYPE_VERTICAL))
            self.imgOut.outSeparator(verticalList, self.fileName, '_vertica_', i)
            
            horizList = []
            horizList.extend(sd.service(blockList, SeparatorVo.TYPE_HORIZ))
            self.imgOut.outSeparator(horizList, self.fileName,'_horizontal_', i)
            
            print("-----------------------Setting Weights for Separators----------------------------"+str(i))
            hrList = be.hrList
            sw = SeparatorWeight(self.nodeList)
            sw.service(horizList, hrList)
            sw.service(verticalList, hrList)
            
            print("-----------------------Content Structure Construction----------------------------"+str(i))
            sepList = []
            sepList.extend(horizList)
            sepList.extend(verticalList)
            sepList.sort(key=functools.cmp_to_key(Vips.sepCompare))
            tempList = blockList
            csc = ContentStructureConstruction()
            csc.service(sepList, block)
            BlockVo.refreshBlock(block)
            blockList.clear()
            be.filList(block)
            blockList = be.blockList
        
            for newBlock in blockList:
                for oldBlock in tempList:
                    if newBlock.id == oldBlock.id:
                        blockList.remove(newBlock)
                        break
            
            #ImageOut.outText(self.fileName, blockList , 'test')
            i+=1
              
        self.browser.quit()
        '''

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
        
    def getDomTree(self):
        self.browser.get(self.url) 
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