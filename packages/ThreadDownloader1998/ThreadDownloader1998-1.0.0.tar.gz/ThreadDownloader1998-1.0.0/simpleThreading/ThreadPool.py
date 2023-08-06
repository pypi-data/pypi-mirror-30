import time
from concurrent.futures.thread import ThreadPoolExecutor
from urllib import request

executor = ThreadPoolExecutor(10)

def downloader(url,path):
    executor.submit(lambda:request.urlretrive(url,path))

    if __name__== "__main__":

        l = [("https://png.pngtree.com/element_origin_min_pic/17/07/30/b45af5e4533a4a5f2b8813ad7dfdfede.jpg","wishky.jpg")]

        for url,path in l:
            downloader(url,path)