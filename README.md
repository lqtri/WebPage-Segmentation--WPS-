# WebPage-Segmentation--WPS-

## Introduction
This is WPS-DB, our webpage segmentation method, different from other method like VIPS, Block-o-matic, we use DB-SCAN instead of K-mean for clustering our data.

Testing for Stack Overflow (Questions tab): https://stackoverflow.com/questions
![](https://github.com/lqtri/WebPage-Segmentation--WPS-/blob/dev-xmldiff/images/stackoverflow.png?raw=true)
![](https://github.com/lqtri/WebPage-Segmentation--WPS-/blob/dev-xmldiff/images/stackoverflow.com_compared.png?raw=true)

Testing for Stack Exchange: https://stackexchange.com
![](https://github.com/lqtri/WebPage-Segmentation--WPS-/blob/dev-xmldiff/images/stackexchange.com.png?raw=true)
![](https://github.com/lqtri/WebPage-Segmentation--WPS-/blob/dev-xmldiff/images/stackexchange.com_compared.png?raw=true)

### Testing on more pages (using Block-O-Matic's dataset)
Please visit this site to view the results:

https://drive.google.com/drive/folders/1uEAfsyFiR82Vejc26fgoWBLR1VpSaI-b?usp=sharing

### Usage
- Install independencies: 
`pip install -r requirments.txt`

- Run WPS-DB: 
    - Download our Jupyter Notebook and run your testing
    - Use commmand: 'python3 WPS_DB_Test.py <your webpage's url>'
