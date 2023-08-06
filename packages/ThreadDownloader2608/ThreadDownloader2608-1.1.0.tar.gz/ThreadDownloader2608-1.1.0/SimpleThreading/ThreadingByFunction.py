from threading import Thread
import time

def downloader(url):
    time.sleep(2)
    print(url, "Download")

l=["daf","afaf","afafac"]

for item in l:
    Thread(target = lambda : downloader(item)).start()
