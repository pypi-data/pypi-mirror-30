from threading import Thread
import time
def downloader(url):
    time.sleep(5)
    print(url,"download complete")
l=["lcwldk","dlk2jed","hkgkhg"]
# t=Thread(target=downloader)
# t.start()
# Thread(target=downloader).start()
# Thread(target=downloader).start()
# Thread(target=downloader).start()
for item in l:
    Thread(target=lambda :downloader(item)).start()