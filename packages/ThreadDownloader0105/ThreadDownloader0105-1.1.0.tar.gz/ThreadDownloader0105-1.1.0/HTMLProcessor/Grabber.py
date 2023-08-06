from urllib import request
from SimpleThreading import ThreadPool

from bs4 import BeautifulSoup

# def download(url):
def url_to_string(url):
    return request.urlopen(url).read()

def find_links(url):
    data=url_to_string(url)
    soup=BeautifulSoup(data,"html.parser")
    anchors=soup.find_all('a', href=True)
    # return list(map(lambda item : item["href"],soup.find_all('a',href=True)))
    # return list(map(lambda item: item["href"], anchors))
    dirty= list(map(lambda item: item["href"], anchors))
    return list(filter(lambda link: link.startswith("http"),dirty))
    # return soup.find_all('a',href=True)

def download_links(url,path):
    links= find_links(url)
    i=0
    for link in links:
        ThreadPool.downloader(link,path+str(i)+".html")
        i+=1


if __name__=="__main__":
    # print(url_to_string("https://pypi.org/project/ThreadDownloader0105/"))
    # print(find_links("https://pypi.org/project/ThreadDownloader0105/"))
    download_links("https://pypi.org/project/ThreadDownloader0105/","download/")
