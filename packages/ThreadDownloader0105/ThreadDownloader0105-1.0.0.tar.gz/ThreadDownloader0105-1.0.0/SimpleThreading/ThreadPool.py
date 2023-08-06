import time
from concurrent.futures import ThreadPoolExecutor
from urllib import request

executor=ThreadPoolExecutor(10)

def downloader(url,path):
    executor.submit(lambda : request.urlretrieve(url,path))
    # time.sleep(5)
    # print(url,"saved at",path)
    # request.urlretrieve(url,path)

if __name__=="__main__":

    l=[("http://devarea.com/wp-content/uploads/2017/11/python.png","python.png")]

    for url,path in l:
        downloader(url,path)
        # executor.submit(lambda : downloader(url,path))