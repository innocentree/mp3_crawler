import os
import codecs
import requests
from bs4 import BeautifulSoup
from tkinter import *
from tkinter.ttk import *
import time

# UI 참고
# https://github.com/jinsyu/pyto/blob/master/pyto.py

torrent_site_root = "https://torrentkim5.net"
torrent_name = "transmission-remote.exe "
torrent_option = " --download-dir /cygdrive/k/Files/torrent/mp3/ "
search_keyword = '멜론'


def openMagnet(parant, magnet_url):
    file_name = "last_torrent.txt"
    last_magnet = ""
    if os.path.exists(file_name):
        fp = open(file_name, mode='r', encoding='utf-8')
        last_magnet = fp.readline()
        fp.close()

    print(magnet_url)
    print(last_magnet)
    if magnet_url.find(last_magnet) >= 0:
        parant.print('new mp3s not found')
        return
    else:
        full_cmd = torrent_name + torrent_option + "-a " + magnet_url  # + " --torrent-done-script " + "/cygdrive/c/" + file_name
        os.system(full_cmd + "> LOG.TXT")
        parant.print(full_cmd)
        fp = open(file_name, mode='w', encoding='utf-8')
        fp.write(magnet_url)
        fp.close()


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

'''
def makeRemoveScript(local_magnet):
    file_name = "arc.sh"
    fp = open(file_name, mode='w', encoding='utf=8')
    fp.write("transmission-remote.exe -t " + local_magnet.rsplit(':', 1)[1] + " -r" + "> LOG2.TXT")
    return file_name
'''



check_time_h = 7  # 매일 7시마다 토렌트 다운
check_time_m = 0
download_flag = False

class Crawler:
    def __init__(self, root):
        self.root = root
        self.txt = Text(self.root)
        self.txt.pack(fill=X, padx=10, pady=10)
        os.system("call \"C:/Program Files (x86)/TransmissionD/bin/restart.exe\"")
        self.print("program start.")

    def __exit__(self):
        os.system("call \"C:/Program Files (x86)/TransmissionD/bin/stop.exe\"")

    def update(self):
        lst = time.localtime()
        global download_flag

        if download_flag is False:
            if lst.tm_hour is check_time_h and lst.tm_min is check_time_m:
                self.print("finding start.")
                download_flag = True

        if download_flag is True:
            if lst.tm_hour == check_time_h and lst.tm_min == (check_time_m+1):
                download_flag = False
                self.crawling()

        self.root.after(1, self.update)

    def crawling(self):
        sub_url = search(search_keyword)
# url 에 .. 이 잘못된 위치에 있으면
# UnicodeError: encoding with 'idna' codec failed (UnicodeError: label empty or too long)
# 같은 에러 발생..
        total_str = str(torrent_site_root + sub_url).replace('..', '')
        magnet = getMagnet(total_str)
        self.print("found magnet : " + magnet)
        if magnet != "":
           #script_name = makeRemoveScript(magnet)
           openMagnet(self, magnet)

    def print(self, txt):
        self.txt.insert(INSERT, txt)
        self.txt.insert(INSERT, '\n')

root = Tk()
root.title('mp3 crawler v1.0')
root.geometry('300x300+100+100')

crawler = Crawler(root)
crawler.update()
root.mainloop()


'''
위젯	설명
Button	단순한 버튼
Label	텍스트 혹은 이미지 표시
CheckButton	체크박스
Entry	단순한 한 라인 텍스트 박스
ListBox	리스트 박스
RadioButton	옵션 버튼
Message	Label과 비슷하게 텍스트 표시. Label과 달리 자동 래핑 기능이 있다.
Scale	슬라이스 바
Scrollbar	스크롤 바
Text	멀티 라인 텍스트 박스로서 일부 Rich Text 기능 제공
Menu	메뉴 Pane
Menubutton	메뉴 버튼
Toplevel	새 윈도우를 생성할 때 사용. Tk()는 윈도우를 자동으로 생성하지만 추가로 새 윈도우 혹은 다이얼로그를 만들 경우 Toplevel를 사용한다
Frame	컨테이너 위젯. 다른 위젯들을 그룹화할 때 사용
Canvas	그래프와 점들로 그림을 그릴 수 있으며, 커스텀 위젯을 만드는데 사용될 수도 있다
'''