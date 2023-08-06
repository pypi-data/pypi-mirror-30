from threading import Thread

import time

def downloader(url):
    time.sleep(5)
    print(url,"download complete")
l = ["bhbuyd", "drtydu", "ygghkfttrd4567"]
for item in l:
    Thread(target=lambda : downloader(item)).start()
# Thread(target=downloader).start()
# Thread(target=downloader).start()
# Thread(target=downloader).start()
# Thread(target=downloader).start()
# Thread(target=downloader).start()
