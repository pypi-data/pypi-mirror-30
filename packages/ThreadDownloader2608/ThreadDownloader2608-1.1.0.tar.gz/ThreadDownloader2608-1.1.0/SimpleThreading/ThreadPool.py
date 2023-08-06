import time
from concurrent.futures import ThreadPoolExecutor
from urllib import request

executor = ThreadPoolExecutor(10)

def downloader(url, path):
    executor.submit(lambda : request.urlretrieve(url, path))

def multi_Downloader(files):
    for url,path in files:
        downloader(url,path)

if __name__ == "__main__":
    l=[("https://www.w3.org/TR/PNG/iso_8859-1.txt","sample.txt")]
    for url,path in l:
        downloader(url,path)