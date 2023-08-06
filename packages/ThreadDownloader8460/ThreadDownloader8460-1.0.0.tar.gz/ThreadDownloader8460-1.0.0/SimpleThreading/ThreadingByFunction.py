import time
from threading import Thread

def downloader(url):
    time.sleep(2);
    print(url, "Download complete")

l = ["scsadc", "sad", "afrac"]

for item in l:
    Thread(target=lambda : downloader(item)).start()
