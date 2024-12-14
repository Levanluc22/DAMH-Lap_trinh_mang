import tkinter as tk
import tkinter.messagebox as mess
import socket
import serverRemote,clientRemote
import threading
from threading import Thread
import os
import sys
local = sys.argv[0]
local = local.split("\\")
filename = local[len(local)-1]
# filename = "python.exe"
class GUI:
    def __init__(self):
        self.form = tk.Tk()
        self.WIDTH = 850
        self.HEIGHT = 320
        self.form.title("Remote PC")
        self.entry_open_port = None
        self.button_open_connect = None
        self.entry_ip_remote = None
        self.entry_port_remote = None
        self.button_start_remote = None
        self.button_close_connect = None
        self.button_close_remote = None
        self.check_open_connect = False
        self.check_start_remote = False
    def open_connect(self):
        if not self.check_open_connect:
            check_bug = False
            try:
                port = int(self.entry_open_port.get())
            except:
                check_bug = True
                mess.showerror(title="Lỗi",
                             message="Port không hợp lệ!")
            if not check_bug:
                self.check_open_connect = True
                self.check_start_remote = True
                self.run_server(port)
                self.button_close_connect.place(x=0,y=0,width=self.WIDTH//2,height=self.HEIGHT)
        else:
            mess.showerror(title="Lỗi",
                             message="Bạn không thể mở connect vì đang remote.\nVui lòng đóng remote!")
    def start_remote(self):
        if not self.check_start_remote:
            check_bug = False
            try:
                ip = self.entry_ip_remote.get()
                checkip = ip.split(".")
                for i in checkip:
                    int(i)
            except:
                check_bug = True
                mess.showerror(title="Lỗi",
                             message="IP không hợp lệ!")

            try:
                port = int(self.entry_port_remote.get())
            except:
                check_bug = True
                mess.showerror(title="Lỗi",
                             message="Port không hợp lệ!")
            if not check_bug:
                self.check_start_remote = True
                self.check_open_connect = True
                self.run_client(ip,port)
                self.button_close_remote.place(x=0,y=0,width=self.WIDTH//2,height=self.HEIGHT)
        else:
            mess.showerror(title="Lỗi",
                             message="Bạn không thể remote vì đang mở connect.\nVui lòng đóng connect!")
    def close_connect(self):
        self.check_open_connect = False
        self.check_start_remote = False
        self.button_close_connect.place_forget()
        os.system("taskkill /f /im "+filename)

    def close_remote(self):
        self.check_open_connect = False
        self.check_start_remote = False
        self.button_close_remote.place_forget()
        os.system("taskkill /f /im "+filename)
    def thread_run_server(self,port):
        app = serverRemote.App(port)
        app.runApp()
    def run_server(self,port):
        t = threading.Thread(target=self.thread_run_server,args=(port,))
        t.start()

    def thread_run_client(self,ip,port):
        app = clientRemote.App(ip,port)
        app.runApp()

    def run_client(self,ip,port):
        t = threading.Thread(target=self.thread_run_client,args=(ip,port,))
        t.start()

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80))
        return s.getsockname()[0]

    def on_closing(self):
        os.system("taskkill /f /im "+filename)
    def create_form(self):
        scrW= self.form.winfo_screenwidth()
        scrH= self.form.winfo_screenheight()
        W = scrW/2-self.WIDTH//2
        H = scrH/2-self.HEIGHT//2
        self.form.geometry(str(self.WIDTH)+"x"+str(self.HEIGHT)+"+%d+%d" %(W,H))
        self.form.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.form.resizable(0,0)
        label_left = tk.Label(self.form,bg="#FF0066")
        label_left.place(x=0,y=0,width=self.WIDTH//2,height=self.HEIGHT)

        title_left = tk.Label(label_left,text="Cho Phép Điều Khiển",font = "Roboto-Bold 18",fg = "white",bg="#FF0066")
        title_left.place(x=95,y=30)

        label_ip = tk.Label(label_left,text="IP: "+str(self.get_ip_address()),font = "Roboto-Bold 20",fg = "white",bg="#FF0066")
        label_ip.place(x=115,y=90)

        label_port = tk.Label(label_left,text="Port: ",font = "Roboto-Bold 20",fg = "white",bg="#FF0066")
        label_port.place(x=30,y=150)

        self.entry_open_port = tk.Entry(label_left,font = "Roboto-Bold 20",fg = "#FF0066",bg="white",bd = 0)
        self.entry_open_port.place(x=100,y=152,width=240)

        self.button_open_connect = tk.Button(label_left,borderwidth=0, highlightthickness=0, text="Open Connect", 
            relief="flat",font = "Roboto-Bold 18",fg = "white",bg="#FF9900",command = self.open_connect)
        self.button_open_connect.place(x=130,y=220)

        self.button_close_connect = tk.Button(label_left,borderwidth=0, highlightthickness=0, text="Close Connect", 
            relief="flat",font = "Roboto-Bold 25",fg = "white",bg="#FF9900",command=self.close_connect)
        self.button_close_connect.place_forget()

        #####
        label_right = tk.Label(self.form,bg="white")
        label_right.place(x=self.WIDTH//2,y=0,width=self.WIDTH//2,height=self.HEIGHT)

        title_right = tk.Label(label_right,text="Điều Khiển Máy Tính",font = "Roboto-Bold 18",fg = "#0099FF",bg="white")
        title_right.place(x=95,y=30)

        label_ip = tk.Label(label_right,text="IP: ",font = "Roboto-Bold 20",fg = "#0099FF",bg="white")
        label_ip.place(x=20,y=90)

        self.entry_ip_remote = tk.Entry(label_right,font = "Roboto-Bold 20",fg = "#0099FF",bg="#EEEEEE",bd = 0)
        self.entry_ip_remote.place(x=90,y=90,width=300)

        label_port = tk.Label(label_right,text="Port: ",font = "Roboto-Bold 20",fg = "#0099FF",bg="white")
        label_port.place(x=20,y=150)

        self.entry_port_remote = tk.Entry(label_right,font = "Roboto-Bold 20",fg = "#0099FF",bg="#EEEEEE",bd = 0)
        self.entry_port_remote.place(x=90,y=152,width=300)

        self.button_start_remote = tk.Button(label_right,borderwidth=0, highlightthickness=0, text="Start Remote",
         relief="flat",font = "Roboto-Bold 18",fg = "white",bg="#0099FF",command = self.start_remote)
        self.button_start_remote.place(x=140,y=220)

        self.button_close_remote = tk.Button(label_right,borderwidth=0, highlightthickness=0, text="Close Remote", 
            relief="flat",font = "Roboto-Bold 25",fg = "white",bg="#FF9900",command=self.close_remote)
        self.button_close_remote.place_forget()

        self.form.mainloop()
if __name__ == '__main__':
    GUI().create_form()