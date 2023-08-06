from threading import Thread

import time

def downloader(url):
    time.sleep(5)
    print(url,"download complete")

l = ["right","wrong","correct"]

for item in l:
    Thread(target=lambda :downloader(item)).start()

