import time
from concurrent.futures import ThreadPoolExecutor

from urllib import request


executor = ThreadPoolExecutor(10)


def downloader(url,path):
    executor.submit(lambda : request.urlretrieve(url,path))
    # request.urlretrieve(url,path)

def multi_downloader(files):
    for url,path in files:
        downloader(url,path)

if __name__=="__main__":
    l=[("http://www.freepngimg.com/download/beach_ball/8-2-beach-ball-png-image.png","ball.png")]

    for url,path in l:
        downloader(url,path)