import time

from PIL import Image, ImageDraw, ImageFont

class ImageOut:
       
    def outImg(self, browser, url, screenshot_path="screenshot.png"):
        # Get dimensions
        print('[Getting Screenshot]')
        default_width=1920
        default_height=1080
        print('+ Getting dimensions...')
        browser.set_window_size(default_width, default_height)
        browser.get(url)
        total_height = browser.execute_script("return document.body.parentNode.scrollHeight")
    
        # Get screenshot
        print('+ Getting screenshot...')
        browser.set_window_size(default_width, total_height)
        browser.get(url)
        browser.save_screenshot(screenshot_path+'.png')
        print('Done')
    
    def outBlock(self, block, fileName, i=0):
        img = Image.open(fileName+'.png')
        dr = ImageDraw.Draw(img)

        for blockVo in block:
            if blockVo.isVisualBlock:               
                # Initialize rectangle
                cor = (blockVo.x,blockVo.y, blockVo.x + blockVo.width, blockVo.y + blockVo.height)
                line = (cor[0],cor[1],cor[0],cor[3])
                dr.line(line, fill="red", width=1)
                line = (cor[0],cor[1],cor[2],cor[1])
                dr.line(line, fill="red", width=1)
                line = (cor[0],cor[3],cor[2],cor[3])
                dr.line(line, fill="red", width=1)
                line = (cor[2],cor[1],cor[2],cor[3])
                dr.line(line, fill="red", width=1)
                
                # Set block ID font size 
                font = ImageFont.truetype("iosevka-ss18.ttc", 15)
                dr.text((blockVo.x,blockVo.y),blockVo.id,(255,0,0),font=font)
                
        saved_path = fileName + '_Block_' + str(i) + '.png'
        img.save(saved_path)