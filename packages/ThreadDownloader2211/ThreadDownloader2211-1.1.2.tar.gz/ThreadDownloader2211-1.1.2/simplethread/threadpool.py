import time
from concurrent.futures import ThreadPoolExecutor
from urllib import request

executor=ThreadPoolExecutor(10)
def downloader(url,path):
    executor.submit(lambda:request.urlretrieve(url,path))
def multi_downloader(files):
    for url,path in files:
        downloader(url,path)


    #request.urlretrieve(url,path)

if __name__=="__main__":
    l=[("https://s7d2.scene7.com/is/image/dkscdn/16NIKUPTCHTRNBKBKSCB_Black_Black_Orange_is","ball.jpg")]

    #for url, path in l:
        #executor.submit(lambda: downloader(url,path))
