import os
import requests
from bs4 import BeautifulSoup
from tkinter import *
from tkinter import scrolledtext
import time
import subprocess
import psutil
from mutagen.mp3 import MP3

# UI 참고
# https://github.com/jinsyu/pyto/blob/master/pyto.py

torrent_site_root = "https://torrentkim5.net"
torrent_name = "transmission-remote.exe "
torrent_option = " --download-dir /cygdrive/k/Files/torrent/mp3/ "
downloaded_folder = "k:\\Files\\torrent\\mp3\\"
search_keyword = '멜론'

down_time = time.strptime("07:00", "%H:%M")
# 매일 7시마다 토렌트 다운

cleaning_time = time.strptime("04:00", "%H:%M")
# 매일 새벽 4시에 중복 파일 제거

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

        check_dup_btn = Button(frame1, text="중복파일정리", command=self.eraseDuplicatedFiles)
        check_dup_btn.pack(side=RIGHT, padx=10)
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

    def setEraseFlag (self):
        self.cleaning_flag = True

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

        if self.cleaning_flag is False:
            if checkTime(lst, cleaning_time):
                self.print("cleaning start.")
                self.cleaning_flag = True

        if self.cleaning_flag is True:
            temp_time = time.strptime(str(cleaning_time.tm_hour) + ":" + str(cleaning_time.tm_min + 1), "%H:%M")
            if checkTime(lst, temp_time):
                self.cleaning_flag = False
                new_path = self.eraseDuplicatedFiles()
                if new_path != "":
                    self.MoveFilesToNew(new_path)

        if time.time() - self.check_counter >= remove_term_m * 60:
            self.check_counter = time.time()
            self.print("removing start.")
            self.removing()

        self.root.after(1, self.update)

    def MoveFilesToNew (self, path):
        new_path = "\"" + path + "\\..\\..\\newest_mp3\\" + "\""
        del_ret = subprocess.check_output("del " + new_path + "*.*" + " /Q", shell=True)
        self.print(del_ret)
        copy_ret = subprocess.check_output("copy " + "\"" + path + "\\*.*" + "\" " + new_path, shell=True)
        self.print(copy_ret)
        self.print("copy completed.")

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
            if latest_time < os.path.getctime(downloaded_folder + dirs):
                latest_time = os.path.getctime(downloaded_folder + dirs)
                latest_path = downloaded_folder + dirs

        print("latest folder : " + latest_path)
        if latest_path is "":
            return ""

        check_path = []
        cneck_count = 0
        print("----------------------------")
        for e in all_path:
            if downloaded_folder + e != latest_path:
                cneck_count+=1
                check_path.append(e)
                print("check list path : " + e)
        print("----------------------------")

        if cneck_count == 0:
            self.print("checking path not found.")
            return latest_path

        latest_file_list = []
        for file in os.listdir(latest_path):
            latest_file_list.append(latest_path + "\\" + file)

        for new_file in latest_file_list:
            if new_file.find('.mp3') == -1:
                continue
            f2 = MP3(new_file)
            substr = self.getSubStr(f2)
            print("finding key : " + substr)
            for path in check_path:
                print("checking path : " + path)
                old_files = os.listdir(downloaded_folder + path)
                for file in old_files:
                    if file.find('.mp3') == -1:
                        continue
                    old_file = downloaded_folder + path + "\\" + file
                    f1 = MP3(old_file)
                    if abs(f1.info.length - f2.info.length) > 2:
                        continue
                    if str(f1).find(substr) > 0:
                        self.print("new: " + new_file)
                        self.print("old: " + old_file + "was deleted.")
                        os.remove(old_file)
                        break

        return latest_path

    def print(self, txt):
        print(txt)
        self.txt_box.insert(INSERT, txt)
        self.txt_box.insert(INSERT, '\n')
        self.txt_box.insert(INSERT, '\n')

    def getSubStr(self, text):
        str_len = int(len(str(text)) / 2)
        substr = ""
        for i in range(str_len, str_len + 1000):
            substr = substr + str(text)[i]
        return substr

    download_flag = False
    df_txt = ''
    remove_flag = False
    rf_txt = ''
    cleaning_flag = False
    check_counter = 0


root = Tk()
root.title('mp3 crawler v1.0')
root.resizable(0, 0)


crawler = Crawler(root)
crawler.update()
root.mainloop()
