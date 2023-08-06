from threading import Thread


import time

def downloader(url):
    time.sleep(5)
    print(url,"Download complete")

l=["rwthj","rethy","wrgehtj6e5"]

for item in l:
    Thread(target=lambda :downloader(item)).start()


# Thread(target=downloader).start()
# Thread(target=downloader).start()
# Thread(target=downloader).start()
# Thread(target=downloader).start()
# Thread(target=downloader).start()

# t= Thread(target=downloader)

# t.start()

