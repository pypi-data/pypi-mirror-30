import time
from concurrent.futures.thread import ThreadPoolExecutor

from urllib import request


executor = ThreadPoolExecutor(10)

def downloader(url,psth):
   request.urlretrieve(url,psth)

if __name__ == "__main__":
    l = [("http://devarea.com/wp-content/uploads/2017/11/python.png","python.png")]

for url,path in l:
    downloader(url,path)
