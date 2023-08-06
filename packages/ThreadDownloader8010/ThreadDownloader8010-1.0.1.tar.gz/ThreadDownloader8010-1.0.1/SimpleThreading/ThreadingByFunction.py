from threading import Thread
import time

def downloader(url):
    time.sleep(5)
    print(url,"download complete")

l = ["KEVIN","PIETERSEN","ENGLAND"]

for item in l:
    Thread(target=lambda : downloader(item)).start()

# t = Thread(target=downloader).start()
# t = Thread(target=downloader).start()
# t = Thread(target=downloader).start()
# t = Thread(target=downloader).start()
# t = Thread(target=downloader).start()