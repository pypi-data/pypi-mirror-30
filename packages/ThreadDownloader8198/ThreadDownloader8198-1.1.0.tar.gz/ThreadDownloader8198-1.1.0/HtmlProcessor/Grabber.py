from urllib import request
from bs4 import BeautifulSoup
from SimpleThreading import ThreadPool

def url_to_string(url):
    return request.urlopen(url).read()

def find_links(url):
    data = url_to_string(url)
    soup = BeautifulSoup(data, "html.parser")
    anchors = soup.find_all('a', href=True)
    dirty = list(map(lambda item : item["href"], anchors))
    return list(filter(lambda link: link.startswith("http"), dirty))

def download_links(url, path):
    links = find_links(url)
    i = 0
    for link in links:
        ThreadPool.downloader(link, path + str(i) + ".html")
        i+=1

if __name__ == "__main__":
    download_links("https://pypi.org/project/ThreadDownloader8198/", "download/")