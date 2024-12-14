import socket
from zlib import compress
from mss import mss
import pyautogui as pya
import pygame
import os
from time import sleep as sl
from pynput.mouse import Button as but, Controller
import win32api
import threading
from threading import Thread
import tkinter as tk
import tkinter.messagebox as mess
from tkinter import *
from tkinter.ttk import Progressbar
import getpass
import sys
from win10toast import ToastNotifier
local = sys.argv[0]
local = local.split("\\")
filename = local[len(local)-1]
# filename = "python.exe"
class App:
    def __init__(self,port):
        self.mouse = Controller()
        self.WIDTH,self.HEIGHT = int(pya.size()[0]-1), int(pya.size()[1]-1)
        self.my_host = self.get_ip_address()
        self.your_host = ""
        self.port = port
        self.server_control = None
        self.id_client = ("",0)
        self.filename_recv = ""
        self.filename = ""
        self.percent = 0
    ###hàm giao diện thnah tiến trình
    def form_processing(self):
        self.ws = Tk()
        self.ws.title('Đang Nhận File '+self.filename)
        self.ws.geometry('380x60')
        self.ws.config(bg='#345')
        self.ws.resizable(0,0)
        self.pb = Progressbar(
        self.ws,
        orient = HORIZONTAL,
        length = 300,
        mode = 'determinate'
        )
        self.txt_percent = Label(
        self.ws,
        text = '0%',
        bg = '#345',
        fg = '#fff'
        )
        self.pb.place(x=20, y=20)
        self.txt_percent.place(x=325 ,y=20)
        self.ws.mainloop()
    def step(self):
        while self.percent < 100:
            try:
                self.ws.update_idletasks()
                self.pb['value'] = self.percent
                self.txt_percent['text']=self.pb['value'],'%'
            except:
                pass
            sl(0.5)
        
    def load_thread_processbar(self):
        t1 = threading.Thread(target=self.form_processing)
        t2 = threading.Thread(target=self.step)
        t1.start()
        sl(0.1)
        t2.start()
    # Hàm xử lý mạng
    def get_ip_address(self):
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80))
        return s.getsockname()[0]

    # Nhận IP từ máy khách:
    def recv_client_host(self):
        try:
            server_host = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            server_host.bind((self.my_host, self.port))
            self.your_host = server_host.recv(1024)
            self.your_host = str(self.your_host.decode("utf-8"))
            server_host.close()
        except:
            mess.showerror(title="Lỗi",
                             message="Kết nối thất bại!")
            os.system("taskkill /f /im "+filename)
    #Gửi kích thước màn hình:
    def send_size_display(self):
        string=str(self.WIDTH)+","+str(self.HEIGHT)
        server_display = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        server_display.connect((self.your_host,self.port))
        server_display.send(string.encode('utf-8'))
        server_display.close()

    # Gửi màn hình (screenshot):
    def retreive_screenshot(self,conn):
        with mss() as sct:
            # The region to capture
            rect = {'top': 0, 'left': 0, 'width': self.WIDTH, 'height': self.HEIGHT}
            while True:
                # Capture the screen
                img = sct.grab(rect)
                # Tweak the compression level here (0-9)
                pixels = compress(img.rgb, 2) #6
                # Send the size of the pixels length
                size = len(pixels)
                size_len = (size.bit_length() + 7) // 8
                try:
                    conn.send(bytes([size_len]))
                except:
                    mess.showinfo(title="Thông Báo",
                             message="Đã ngắt kết nối!")
                    os.system("taskkill /f /im "+filename)
                # Send the actual pixels length
                size_bytes = size.to_bytes(size_len, 'big')
                conn.send(size_bytes)
                # Send pixels
                conn.sendall(pixels)
    def sendDisplay(self):
        ''' connect back to attacker on port'''
        # sock = socket.socket()
        # sock.connect((self.your_host, self.port))

        try:
            sock = socket.socket()
            sock.connect((self.your_host, self.port))
            while True:
                thread = Thread(target=self.retreive_screenshot, args=(sock,))
                thread.start()
                thread.join()
        except Exception as e:
            sock.close()
            mess.showinfo(title="Thông Báo",
                             message="Đã ngắt kết nối, vì thời gian chờ quá lâu!")
            os.system("taskkill /f /im "+filename)
    # Nhận điều khiển từ xa:
    def recvControl(self):
        self.server_control = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.server_control.bind((self.my_host, self.port))
        while True:
            try:
                # datagram = self.server_control.recv(1024)
                #data = datagram.decode("utf-8").split(",")

                #######
                datagram = self.server_control.recvfrom(1024)
                data = datagram[0].decode("utf-8").split(",")
                #self.id_client = datagram[1]
                #######
                if len(data) == 3:
                    if data[0] == "move":
                        x,y = int(data[1]),int(data[2])
                        win32api.SetCursorPos((x,y))
                    elif data[0] == "scroll":
                        self.mouse.scroll(0,int(data[2]))
                    elif data[0] == "click":
                        if data[1] == "right":
                            pya.click(button='right')
                    elif data[0] == "pressingMouse":
                        self.mouse.press(but.left)   
                    elif data[0] == "releaseMouse":
                        self.mouse.release(but.left)
                elif len(data) == 2:
                    if data[0] == "multikey":
                        key=data[1].split("space_key")
                        pya.hotkey(*key)
                    elif data[0] == "file":
                        self.filename_recv = data[1]
                        t = threading.Thread(target=self.recv_file)
                        t.start()
            except:
                pass
    # Nhận tệp:
    def recv_file(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.your_host, self.port%2+9))
        self.filename_recv = self.filename_recv.split("\\")
        self.filename_recv = self.filename_recv[len(self.filename_recv)-1]
        self.filename = self.filename_recv
        self.filename_recv = "C:\\Users\\"+getpass.getuser()+"\\Downloads\\"+self.filename_recv
        size_file = s.recv(1024)
        size_file = int(size_file.decode("utf-8"))
        count_size = 0
        self.load_thread_processbar()
        with open(self.filename_recv, 'wb') as f:
            while True:
                data = s.recv(1024)
                count_size+=1024 #len(data)
                try:
                    self.percent = round((count_size/size_file) * 100, 2)
                except:
                    break
                if not data:
                    f.close()
                    break
                f.write(data)
        self.percent = 0
        self.ws.quit()
        t = ToastNotifier()
        t.show_toast("Thành Công","Tệp Mới Được Lưu Tại:\n"+self.filename_recv,duration=3)
        #Hàm chính để chạy ứng dụng
    def runApp(self):
        self.recv_client_host()
        self.send_size_display()
        t1 = threading.Thread(target=self.sendDisplay)
        t2 = threading.Thread(target=self.recvControl)
        t1.start()
        t2.start()
        t1.join()
        t2.join()