import os
import requests
from bs4 import BeautifulSoup
from tkinter import *
from tkinter import scrolledtext
import time
import subprocess
import psutil

# UI 참고
# https://github.com/jinsyu/pyto/blob/master/pyto.py

torrent_site_root = "https://torrentkim5.net"
torrent_name = "transmission-remote.exe "
torrent_option = " --download-dir /cygdrive/k/Files/torrent/mp3/ "
downloaded_folder = "k:\\Files\\torrent\\mp3\\"
search_keyword = '멜론'

down_time = time.strptime("07:00", "%H:%M")
# 매일 7시마다 토렌트 다운

# remove_time = time.strptime("14:00", "%H:%M")
# 매일 14시마다 토렌트 제거
remove_term_m = 30
# 30분마다 토렌트 제거 로직 수행


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
        full_cmd = torrent_name + torrent_option + "-a " + magnet_url
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


def checkTime(time1, time2):
    if time1.tm_hour is time2.tm_hour and time1.tm_min is time2.tm_min:
        return True
    return False


class Crawler:
    def __init__(self, in_root):
        self.root = in_root

        frame1 = Frame(self.root)
        frame1.pack(side=TOP, fill=X)

        label1 = Label(frame1, text="down_flag")
        label1.pack(side=LEFT)

        self.df_txt = StringVar()
        self.down_state_flag = Entry(frame1, textvariable=self.df_txt)
        self.down_state_flag.config(width=5, state='readonly')
        self.down_state_flag.pack(side=LEFT)

        label2 = Label(frame1, text="remove_flag")
        label2.pack(side=LEFT)

        self.rf_txt = StringVar()
        self.remove_state_flag = Entry(frame1, textvariable=self.rf_txt)
        self.remove_state_flag.config(width=5, state='readonly')
        self.remove_state_flag.pack(side=LEFT)

        removing_btn = Button(frame1, text="즉시제거", command=self.removing)
        removing_btn.pack(side=RIGHT, padx=10)
        crawling_btn = Button(frame1, text="즉시다운", command=self.crawling)
        crawling_btn.pack(side=RIGHT, padx=10)

        frame2 = Frame(self.root)
        frame2.pack(side=TOP)

        self.txt_box = scrolledtext.ScrolledText(frame2, width=100, height=10, padx=10, pady=10)
        self.txt_box.pack(side=LEFT)

        self.print("program start.")

        self.check_counter = time.time()

        if self.checkActiveProcess() is False:
            self.print(" - transmission-daemon will start soon")
            os.system("call \"C:/Program Files (x86)/TransmissionD/bin/start.exe\"")
        else:
            self.print(" - transmission-daemon already started")

    def __del__(self):
        count = 0
        while self.checkActiveProcess() is True:
            count += 1
            print("stop transmission-daemon[" + str(count) + "]")
            os.system("call \"C:/Program Files (x86)/TransmissionD/bin/stop.exe\"")

    def update(self):
        lst = time.localtime()
        self.rf_txt.set(str(self.remove_flag))
        self.df_txt.set(str(self.download_flag))

        if self.download_flag is False:
            if checkTime(lst, down_time):
                self.print("finding start.")
                self.download_flag = True

        if self.download_flag is True:
            temp_time = time.strptime(str(down_time.tm_hour)+":"+str(down_time.tm_min + 1), "%H:%M")
            if checkTime(lst, temp_time):
                self.download_flag = False
                self.crawling()

        if time.time() - self.check_counter >= remove_term_m * 60:
            self.check_counter = time.time()
        # if self.remove_flag is False:
        #    if checkTime(lst, remove_time):
            self.print("removing start.")
        # self.remove_flag = True

        # if self.remove_flag is True:
        #    temp_time = remove_time
        #    temp_time.tm_min += 1
        #    if checkTime(lst, temp_time):
        #        self.remove_flag = False
            self.removing()

        self.root.after(1, self.update)

    def removing(self):
        ret = subprocess.check_output("transmission-remote.exe -l", shell=True)
        self.print(ret)
        remove_id = -1

        for line in str(ret).split(sep='\\n'):
            if line.find("100%") > -1:
                remove_id = int(line.strip().split(maxsplit=1)[0])
                self.print("REMOVE ID : " + str(remove_id))
                remove_ret = subprocess.check_output("transmission-remote.exe -t " + str(remove_id) + " -r", shell=True)
                self.print(remove_ret)

        if remove_id is -1:
            self.print("finished torrent not found.")

    def crawling(self):
        sub_url = search(search_keyword)
# url 에 .. 이 잘못된 위치에 있으면
# UnicodeError: encoding with 'idna' codec failed (UnicodeError: label empty or too long)
# 같은 에러 발생..
        total_str = str(torrent_site_root + sub_url).replace('..', '')
        magnet = getMagnet(total_str)
        self.print("found magnet : " + magnet)
        if magnet != "":
           openMagnet(self, magnet)
           self.eraseDuplicatedFiles()

    def checkActiveProcess(self):
        print("check active transmission process...")
        pids = psutil.process_iter()
        found = False
        for pid in pids:
            if pid.name().upper().lower().find("transmission-daemon.exe") > -1:
                print(pid.name().upper().lower() + " is started")
                found = True
        return found

    def eraseDuplicatedFiles(self):
        latest_path = ""
        all_path = []
        latest_time = 0

        for e in os.listdir(downloaded_folder):
            all_path.append(e)

        for dirs in all_path:
            #print("folder name : " + downloaded_folder + dirs)
            #print("create time : " + str(datetime.datetime.fromtimestamp(os.path.getctime(downloaded_folder + dirs))))
            if latest_time < os.path.getctime(downloaded_folder + dirs):
                latest_time = os.path.getctime(downloaded_folder + dirs)
                latest_path = downloaded_folder + dirs

        print("latest folder : " + latest_path)
        if latest_path is "":
            return

        check_path = []
        print("----------------------------")
        for e in all_path:
            if downloaded_folder + e != latest_path:
                check_path.append(e)
                print("check list path : " + e)
        print("----------------------------")

        latest_file_list = []
        for file in os.listdir(latest_path):
            latest_file_list.append(latest_path + "\\" + file)

        for path in check_path:
            print("checking path : " + path)
            old_files = os.listdir(downloaded_folder + path)
            for file in old_files:
                real_path = os.path.realpath(file)
                for new_file in latest_file_list:
                    f1 = open(new_file, 'rb')
                    old_filename = downloaded_folder + path + "\\" + file
                    f2 = open(old_filename, 'rb')
                    if f1.read() == f2.read():
                        f1.close()
                        f2.close()
                        print("new: " + new_file)
                        print("old: " + old_filename)
                        os.remove(old_filename)
                        break
                    else:
                        f1.close()
                        f2.close()

    def print(self, txt):
        print(txt)
        self.txt_box.insert(INSERT, txt)
        self.txt_box.insert(INSERT, '\n')
        self.txt_box.insert(INSERT, '\n')

    download_flag = False
    df_txt = ''
    remove_flag = False
    rf_txt = ''
    check_counter = 0


root = Tk()
root.title('mp3 crawler v1.0')
root.resizable(0, 0)


crawler = Crawler(root)
crawler.eraseDuplicatedFiles()
'''
f1 = open("c:\\1.mp3", 'rb')
f2 = open("c:\\3.mp3", 'rb')
if f1.read() == f2.read():
    print("1")
else:
    print("2")

f1.close()
f2.close()
'''
#print(str(subprocess.getoutput("comp 1.mp3 2.mp3")))
#crawler.update()
#root.mainloop()


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