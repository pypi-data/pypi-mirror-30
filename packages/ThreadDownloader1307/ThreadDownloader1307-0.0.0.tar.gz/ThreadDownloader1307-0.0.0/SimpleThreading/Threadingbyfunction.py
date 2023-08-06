from threading import Thread

import time


def downloader(url):
    time.sleep(5)
    print(url,"download complete")


l=["akash","chaubey","cool"]

for item in l:
    Thread(target=lambda:downloader(item)).start()


