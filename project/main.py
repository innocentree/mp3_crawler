import os
import codecs
import requests
from bs4 import BeautifulSoup

torrent_site_root = "https://torrentkim5.net"
torrent_name = "transmission-remote.exe "
torrent_option = "-w K:\\Files\\torrent\\mp3 "

def openMagnet(magnet_url, file_name):
    os.system(torrent_name + torrent_option + "-a " + magnet_url + " --torrent-done-script " + file_name)


def getMagnet(url):
    full_magnet = ""
    raw_source = requests.get(url)
    soup = BeautifulSoup(raw_source.text, 'lxml')
    for b in soup.select('input'):
        value = str(b.get('value'))
        if value.startswith('magnet'):
            full_magnet = value
    return full_magnet


def search(find_word):
    src = requests.get('https://torrentkim5.net/bbs/s.php?k=' + find_word + '&b=&q=')
    soup = BeautifulSoup(src.text, 'lxml')

    for b in soup.select('a'):
        if str(b.get('href')).find('/torrent_song/') > 0:
            if str(b).find(find_word) > 0:
                return str(b.get('href'))
                break
    return ''


def makeRemoveScript(local_magnet):
    file_name = "arc.txt"
    fp = open(file_name, mode='w', encoding='utf=8')
    fp.write("transmission-remote.exe -t " + magnet.rsplit(':', 1)[1] + " -r")
    return file_name


sub_url = search('멜론')

# url 에 .. 이 잘못된 위치에 있으면
# UnicodeError: encoding with 'idna' codec failed (UnicodeError: label empty or too long)
# 같은 에러 발생..
total_str = str(torrent_site_root + sub_url).replace('..', '')
magnet = getMagnet(total_str)
script_name = makeRemoveScript(magnet)
openMagnet(magnet, script_name)



#fs = codecs.open('C:\\Users\\JYLee\\AppData\\Roaming\\uTorrent\\' + 'resume.dat', 'rb', 'utf-8', errors='ignore')
#lines = fs.readlines()
#for i in lines:
#    print(i)
#fs.close()