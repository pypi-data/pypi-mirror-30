import time
from concurrent.futures.thread import ThreadPoolExecutor

from urllib import request


executor = ThreadPoolExecutor(10)
def downloader(url,path):
    executor.submit(lambda :request.urlretrieve(url,path))


def multi_downloader(files):
   for url,path in files:
       downloader(url,path)

if __name__ == "__main__":
    l = [("http://devarea.com/wp-content/uploads/2017/11/python.png","python.png")]

    for url,path in l:
        downloader(url,path)
