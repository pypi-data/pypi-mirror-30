import time
from concurrent.futures.thread import ThreadPoolExecutor
from urllib import request

executor = ThreadPoolExecutor(10)

def downloader(url, path):
    executor.submit(lambda : request.urlretrieve(url, path))

if __name__ == "__main__":

    l = [("https://s.yimg.com/fz/api/res/1.2/hPzIdpFqPTYtITzLJzmg0A--~C/YXBwaWQ9c3JjaGRkO2g9NTEyO3E9ODA7dz01MTI-/http://files.softicons.com/download/tv-movie-icons/poke-balls-icons-by-davi-andrade/png/512x512/Poke%20Ball.png.cf.jpg", "ball.jpg")]

    for url, path in l:
        downloader(url, path)