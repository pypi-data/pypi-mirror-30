from threading import Thread

import time


def downloader(url):
    time.sleep(5)
    print(url, "Download complete")

l = ["rwthyj", "rethy", "wrgehtj6e5"]

for item in l:
    Thread(target=lambda : downloader(item)).start()


