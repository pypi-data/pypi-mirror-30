from threading import Thread
import time

def downloader():
    time.sleep(5)
    print("Download compleat")

l=["Satyam","Amit","Abhijeet"]
for item in l:
# t = Thread(target=downloader).start()
   t = Thread(target=lambda :downloader(item)).start()