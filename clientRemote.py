import socket
from zlib import decompress
import pyautogui as pya
import pygame
from time import sleep as sl
from pynput.mouse import Listener
from threading import Thread
import threading
import win32api
import tkinter as tk
from win10toast import ToastNotifier
import tkinter.messagebox as mess
import os
import sys
local = sys.argv[0]
local = local.split("\\")
filename = local[len(local)-1]
# filename = "python.exe"
pygame.init()
class App:
    def __init__(self,host,port):
        self.my_host = self.get_ip_address()
        self.your_host = host
        self.port = port
        self.check_on_windown = False
        self.WIDTH,self.HEIGHT = 0,0
        self.client_control = None
        self.check_equal_screen = False
        self.keys = []
    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    #send myhost to server
    def send_host_to_server(self):
        try:
            client_myhost = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            client_myhost.connect((self.your_host,self.port))
            client_myhost.send(self.my_host.encode('utf-8'))
            client_myhost.close()
        except:
            mess.showerror(title="Lỗi",
                             message="Kết nối thất bại!")
            os.system("taskkill /f /im "+filename)
    ################# recv size display
    def recv_size_display(self):
        try:
            client_display = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            client_display.bind((self.my_host, self.port))
            datagram = ""
            while datagram == "":
                try:
                    datagram = client_display.recv(1024)
                except:
                    pass
                if datagram == "":
                    continue
                datagram = datagram.decode("utf-8").split(",")
            self.WIDTH,self.HEIGHT = int(datagram[0]),int(datagram[1])
            if self.WIDTH == int(pya.size()[0])-1 and self.HEIGHT == int(pya.size()[1])-1:
                self.check_equal_screen = True
            client_display.close()
        except:
            mess.showerror(title="Lỗi",
                             message="Kết nối thất bại!")
            os.system("taskkill /f /im "+filename)
    #####
    def recvall(self,conn,length):
        """ Retreive all pixels. """
        buf = b''
        while len(buf) < length:
            data = conn.recv(length - len(buf))
            if not data:
                return data
            buf += data
        return buf

    # receive display from server
    def recvDisplay(self):
        ''' machine lhost'''
        sock = socket.socket()
        sock.bind((self.my_host, self.port))
        sock.listen(5)
        conn, addr = sock.accept()

        # pygame.init()
        screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        clock = pygame.time.Clock()
        #pygame.mouse.set_visible(0)
        button_hide = pygame.Rect(self.WIDTH/2-20,0,40,20)
        watching = True

        try:
            while watching:

                for event in pygame.event.get():
                    ### multi press key
                    if event.type == pygame.KEYDOWN:
                        if event.key not in self.keys:
                            self.keys.append(pygame.key.name(event.key))
                    if event.type == pygame.KEYUP:
                        if len(self.keys) > 0:
                            if pygame.key.name(event.key) in self.keys:
                                self.multiKeypress(self.get_key(self.keys)) # send key to server
                                self.keys = []
                    #####
                    if (event.type == pygame.ACTIVEEVENT):
                        if (event.gain == 1):  # mouse enter the window
                            self.check_on_windown = True
                        else:  # mouse leave the window
                            self.check_on_windown = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos=event.pos
                        if button_hide.collidepoint(mouse_pos):
                            pya.hotkey("win","down")
                    if event.type == pygame.DROPFILE:
                        t = threading.Thread(target=self.send_file,args=(event.file,))
                        t.start()

                # Retreive the size of the pixels length, the pixels length and pixels
                try:
                    size_len = int.from_bytes(conn.recv(1), byteorder='big') 
                except:
                    mess.showerror(title="Thông Báo",
                             message="Đã ngắt kết nối!")
                    os.system("taskkill /f /im "+filename)

                size = int.from_bytes(conn.recv(size_len), byteorder='big')
                pixels = decompress(self.recvall(conn, size))
                # Create the Surface from raw pixels
                img = pygame.image.fromstring(pixels, (self.WIDTH, self.HEIGHT), 'RGB')

                # Display the picture
                screen.blit(img, (0, 0))

                # create btn hide
                pygame.draw.rect(screen,[0,0,0],button_hide,4)
                pygame.draw.line(screen,[255,0,0],(self.WIDTH/2-10,10),(self.WIDTH/2-20+30,10),4)
                ###
                pygame.display.flip()
                clock.tick(60)
                
        finally:
            sock.close()
    # send file to server
    def send_file(self,filename_send):
        string = "file,"+filename_send
        self.client_control.send(string.encode('utf-8'))

        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        client.bind((self.my_host,self.port%2+9))
        client.listen(1)
        (conn,(ip,port)) = client.accept()
        size_file = os.path.getsize(filename_send)
        conn.send(str(size_file).encode('utf-8'))
        f = open(filename_send,"rb")
        while True:
            l = f.read(1024)
            while(l):
                conn.send(l)
                l = f.read(1024)
            if not l:
                f.close()
                conn.close()
                break
    # send control to server
    def create_client_control(self):
        self.client_control = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_control.connect((self.your_host, self.port))

    def on_move(self,x,y):
        if self.check_on_windown:
            if not self.check_equal_screen:
                x,y = pygame.mouse.get_pos()
            string = "move,"+str(x)+","+str(y)
            self.client_control.send(string.encode('utf-8'))
    def on_scroll(self,x, y, dx, dy):
        if self.check_on_windown:
            string = "scroll,"+str(dx)+","+str(dy)
            self.client_control.send(string.encode('utf-8'))
    def on_click(self,x,y,button,pressed):
        pressed = str(pressed)
        button = str(button)
        button = button[7:len(button)]
        if pressed == "True" and button == "right" and self.check_on_windown == True:
            string = "click,right,True"
            self.client_control.send(string.encode('utf-8'))
    def pressingMouse(self):
        check_times_press = False
        check_times_release = False
        while True:
            if self.check_on_windown:
                a = win32api.GetKeyState(0x01)
                if a < 0:
                    if check_times_press == False:
                        string = "pressingMouse,"+"True,"+"True"
                        self.client_control.send(string.encode('utf-8'))
                        check_times_press = True
                        check_times_release = False
                else:
                    if check_times_release == False:
                        string = "releaseMouse,"+"True,"+"True"
                        self.client_control.send(string.encode('utf-8'))
                        check_times_press = False
                        check_times_release = True
            sl(0.01)
    def get_key(self,keys):
        list_key = []
        for key in keys:
            if key == "caps lock" :
                k = "capslock"
            elif key == "left shift" or key == "right shift":
                k = "shift"
            elif key == "left ctrl" or key == "right ctrl":
                k = "ctrl"
            elif key == "left alt" or key == "right alt":
                k = "alt"
            elif key == "left meta" or key == "right meta":
                k = "win"
            elif key == "print screen":
                k = "printscreen"
            elif key == "page up":
                k = "pgup"
            elif key == "page down":
                k = "pgdn"
            elif key == "scroll lock":
                k = "scrolllock"
            elif key[0] == "[" and key[2] == "]":
                k = key[1]
            elif key == "compose":
                k = "apps"
            else:
                k = key
            list_key.append(k)
        return list_key
    def multiKeypress(self,keys):
        try:
            string = "space_key".join(keys)
            if self.check_on_windown:
                string = "multikey,"+string
                self.client_control.send(string.encode('utf-8'))
        except:
            pass
    #multi thread
    def sendMouse(self):
        with Listener(on_scroll=self.on_scroll,on_move=self.on_move,on_click=self.on_click) as listener:
            listener.join()
    def runApp(self):
        self.send_host_to_server()
        self.recv_size_display()
        self.create_client_control()
        t1 = threading.Thread(target=self.sendMouse)
        t2 = threading.Thread(target=self.recvDisplay)
        t3 = threading.Thread(target=self.pressingMouse)
        t1.start()
        t2.start()
        t3.start()
        t1.join()
        t2.join()
        t3.join()