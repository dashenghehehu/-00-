import socket
import threading
import json  # json.dumps(some)打包   json.loads(some)解包
import tkinter
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText  # 导入多行文本框用到的包
import time
import requests
from tkinter import filedialog
from RegisterPanel import RegisterPanel
from LoginPanel import LoginPanel
import math
from PIL import Image,ImageTk
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
global IP, PORT
IP = ''
PORT = ''
name = ''
listbox1 = ''  # 用于显示在线用户的列表框
ii = 0  # 用于判断是开还是关闭列表框
users = []  # 在线用户列表
chat = '------Group chat-------'  # 聊天对象, 默认为群聊



IP='192.168.43.244'
PORT=50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))
# 注册
def register_user( user, key,name):
    # 请求类型
    s.sendall(bytes("2", "utf-8"))
    # 依次发送用户名密码
    send_string_with_length(name)
    send_string_with_length(user)
    send_string_with_length(key)
    # 获取服务器的返回值，"0"代表通过，“1”代表已有用户名, "2"代表其他错误
    return recv_string_by_length(1)
# 提交注册表单
def register_submit():
    print("开始注册")
    name,user, key, confirm = reg_frame.get_input()
    if user == "" or key == "" or confirm == "" or name == "":
        tkinter.messagebox.showwarning("错误", "请完成注册表单")
        return
    if not key == confirm:
        tkinter.messagebox.showwarning("错误", "两次密码输入不一致")
        return
    # 发送注册请求
    result = register_user(user, key,name)
    if result == "0":
        # 注册成功，跳往登陆界面
        tkinter.messagebox.showinfo("成功", "注册成功")
        close_reg_window()
    elif result == "1":
        # 用户名重复
        tkinter.messagebox.showwarning("错误", "该用户名已被注册")
    elif result == "2":
        # 未知错误
        tkinter.messagebox.showerror("错误", "发生未知错误")

# 发送带长度的字符串
def send_string_with_length(content):
        # 先发送内容的长度
       s.sendall(bytes(content, encoding='utf-8').__len__().to_bytes(4, byteorder='big'))
        # 再发送内容
       s.sendall(bytes(content, encoding='utf-8'))

# 获取服务器传来的定长字符串
def recv_string_by_length(len):
        return str(s.recv(len), "utf-8")

    # 获取服务端传来的变长字符串，这种情况下服务器会先传一个长度值
def recv_all_string():
        # 获取消息长度
        length = int.from_bytes(s.recv(4), byteorder='big')
        b_size = 3 * 1024  # 注意utf8编码中汉字占3字节，英文占1字节
        times = math.ceil(length / b_size)
        content = ''
        for i in range(times):
            if i == times - 1:
                seg_b = s.recv(length % b_size)
            else:
                seg_b = s.recv(b_size)
            content += str(seg_b, encoding='utf-8')
        return content
def close_sk():
    print("尝试断开socket连接")
    s.close()

def login():
    print("点击登录按钮")
    user, key = login_frame.get_input()
    if user == "" or key == "":
        tkinter.messagebox.showwarning(title="提示", message="用户名或者密码为空")
        return
    print("user: " + user + ", key: " + key)
    if check_user(user, key):
        # 验证成功
        goto_main_frame(user)
    else:
        # 验证失败
        tkinter.messagebox.showwarning(title="错误", message="用户名或者密码错误")
# 验证登录
def check_user(user, key):
    # 请求类型
    s.sendall(bytes("1", "utf-8"))
    # 依次发送用户名密码
    send_string_with_length(user)
    send_string_with_length(key)
    # 获取服务器的返回值，"1"代表通过，“0”代表不通过
    check_result = recv_string_by_length(1)
    global name
    name=recv_all_string()
    print("name++:",name)
    return check_result == "1"

def close_login_window():
    close_sk()
    login_frame.login_frame.destroy()


# 关闭登陆界面前往主界面
def goto_main_frame(user):
    login_frame.close()


# 关闭注册界面并打开登陆界面
def close_reg_window():
    reg_frame.close()
    global login_frame
    login_frame = LoginPanel(login, register, close_login_window)
    login_frame.show()


# 登陆界面前往注册界面
def register():
    print("点击注册按钮")
    login_frame.close()
    global reg_frame
    reg_frame = RegisterPanel(close_reg_window, register_submit, close_reg_window)
    reg_frame.show()




login_frame = LoginPanel(login, register, close_login_window)
login_frame.show()




print("name+++++++++:",name)
if name:
    s.send(name.encode())  # 发送用户名
else:
    s.send('no'.encode())  # 没有输入用户名则标记no

# 聊天窗口
# 创建图形界面
root = tkinter.Tk()
root.title("聊天室")  # 窗口命名
root['height'] = 400
root['width'] = 580
root.resizable(0, 0)  # 限制窗口大小

# 创建多行文本框
listbox = ScrolledText(root)
listbox.place(x=5, y=0, width=570, height=320)
# 文本框使用的字体颜色
listbox.tag_config('red', foreground='red')
listbox.tag_config('blue', foreground='blue')
listbox.tag_config('green', foreground='green')
listbox.tag_config('pink', foreground='pink')
listbox.insert(tkinter.END, 'Welcome to the chat room!', 'blue')

# 表情功能代码部分
# 四个按钮, 使用全局变量, 方便创建和销毁
b1 = ''
b2 = ''
b3 = ''
b4 = ''
b5 = ''
b6 = ''
b7 = ''
b8 = ''
b9 = ''
p1 = tkinter.PhotoImage(file='./emoji/1.png')
p2 = tkinter.PhotoImage(file='./emoji/2.png')
p3 = tkinter.PhotoImage(file='./emoji/3.png')
p4 = tkinter.PhotoImage(file='./emoji/4.png')
p5 = tkinter.PhotoImage(file='./emoji/5.png')
p6 = tkinter.PhotoImage(file='./emoji/6.png')
p7 = tkinter.PhotoImage(file='./emoji/7.png')
p8 = tkinter.PhotoImage(file='./emoji/8.png')
p9 = tkinter.PhotoImage(file='./emoji/9.png')
dic = {'aa**': p1, 'bb**': p2, 'cc**': p3, 'dd**': p4,'jj**': p5, 'ff**': p6, 'gg**': p7, 'hh**': p8, 'ii**': p9}
ee = 0  # 判断表情面板开关的标志



def mark(exp):  # 参数是发的表情图标记, 发送后将按钮销毁
    global ee
    mes = exp + ':;' + name + ':;' + chat
    s.send(mes.encode())
    b1.destroy()
    b2.destroy()
    b3.destroy()
    b4.destroy()
    b5.destroy()
    b6.destroy()
    b7.destroy()
    b8.destroy()
    b9.destroy()
    ee = 0


# 四个对应的函数
def bb1():
    mark('aa**')


def bb2():
    mark('bb**')


def bb3():
    mark('cc**')


def bb4():
    mark('dd**')

def bb5():
    mark('jj**')


def bb6():
    mark('ff**')


def bb7():
    mark('gg**')


def bb8():
    mark('hh**')


def bb9():
    mark('ii**')

def express():
    global b1, b2, b3, b4,b5, b6, b7, b8,b9, ee
    if ee == 0:
        ee = 1
        b1 = tkinter.Button(root, command=bb1, image=p1,
                            relief=tkinter.FLAT, bd=0)
        b2 = tkinter.Button(root, command=bb2, image=p2,
                            relief=tkinter.FLAT, bd=0)
        b3 = tkinter.Button(root, command=bb3, image=p3,
                            relief=tkinter.FLAT, bd=0)
        b4 = tkinter.Button(root, command=bb4, image=p4,
                            relief=tkinter.FLAT, bd=0)
        b5 = tkinter.Button(root, command=bb5, image=p5,
                            relief=tkinter.FLAT, bd=0)
        b6 = tkinter.Button(root, command=bb6, image=p6,
                            relief=tkinter.FLAT, bd=0)
        b7 = tkinter.Button(root, command=bb7, image=p7,
                            relief=tkinter.FLAT, bd=0)
        b8 = tkinter.Button(root, command=bb8, image=p8,
                            relief=tkinter.FLAT, bd=0)
        b9 = tkinter.Button(root, command=bb9, image=p9,
                            relief=tkinter.FLAT, bd=0)

        b1.place(x=5, y=248)
        b2.place(x=75, y=248)
        b3.place(x=145, y=248)
        b4.place(x=215, y=248)
        b5.place(x=285, y=248)
        b6.place(x=355, y=248)
        b7.place(x=425, y=248)
        b8.place(x=495, y=248)
        b9.place(x=565, y=248)
    else:
        ee = 0
        b1.destroy()
        b2.destroy()
        b3.destroy()
        b4.destroy()
        b5.destroy()
        b6.destroy()
        b7.destroy()
        b8.destroy()
        b9.destroy()
# 创建表情按钮
eBut = tkinter.Button(root, text='emoji', command=express)
eBut.place(x=5, y=320, width=60, height=30)


# 图片功能代码部分
# 从图片服务端的缓存文件夹中下载图片到客户端缓存文件夹中
def fileGet(names):
    PORT3 = 50009
    ss2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss2.connect((IP, PORT3))
    message = 'get ' + names
    ss2.send(message.encode())
    fileName = '.\\Client_image_cache\\' + names
    print('Start downloading image!')
    print('Waiting.......')
    with open(fileName, 'wb') as f:
        while True:
            data = ss2.recv(1024)
            if data == 'EOF'.encode():
                print('Download completed!')
                break
            f.write(data)
    time.sleep(0.1)
    ss2.send('quit'.encode())


# 将图片上传到图片服务端的缓存文件夹中
def filePut(fileName):
    PORT3 = 50009
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.connect((IP, PORT3))
    # 截取文件名
    print(fileName)
    names = fileName.split('/')[-1]
    print(names)
    message = 'put ' + names
    ss.send(message.encode())
    time.sleep(0.1)
    print('Start uploading image!')
    print('Waiting.......')
    with open(fileName, 'rb') as f:
        while True:
            a = f.read(1024)
            if not a:
                break
            ss.send(a)
        time.sleep(0.1)  # 延时确保文件发送完整
        ss.send('EOF'.encode())
        print('Upload completed')
    ss.send('quit'.encode())
    time.sleep(0.1)
    # 上传成功后发一个信息给所有客户端
    mes = '``#' + names + ':;' + name + ':;' + chat
    s.send(mes.encode())


def picture():
    # 选择对话框
    fileName = tkinter.filedialog.askopenfilename(title='Select upload image')
    # 如果有选择文件才继续执行
    if fileName:
        # 调用发送图片函数
        filePut(fileName)

def resize(w, h, w_box, h_box, pil_image):
    f1 = 1.0*w_box/w # 1.0 forces float division in Python2
    f2 = 1.0*h_box/h
    factor = min([f1, f2])
    width = int(w*factor)
    height = int(h*factor)
    return pil_image.resize((width, height), Image.ANTIALIAS)
# 创建发送图片按钮
pBut = tkinter.Button(root, text='Image', command=picture)
pBut.place(x=65, y=320, width=60, height=30)



# 文件功能代码部分
# 将在文件功能窗口用到的组件名都列出来, 方便重新打开时会对面板进行更新
list2 = ''  # 列表框
label = ''  # 显示路径的标签
upload = ''  # 上传按钮
close = ''  # 关闭按钮


def fileClient():
    PORT2 = 50008  # 聊天室的端口为50007
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, PORT2))
    root['height'] = 390
    root['width'] = 760
    list2 = tkinter.Listbox(root)
    list2.place(x=580, y=25, width=175, height=325)

    # 将接收到的目录文件列表打印出来
    def recvList(enter, lu):
        s.send(enter.encode())
        data = s.recv(4096)
        data = json.loads(data.decode())
        list2.delete(0, tkinter.END)  # 清空列表框
        lu = lu.split('\\')
        if len(lu) != 1:
            list2.insert(tkinter.END, 'Return to the previous dir')
            list2.itemconfig(0, fg='green')
        for i in range(len(data)):
            list2.insert(tkinter.END, ('' + data[i]))
            if '.' not in data[i]:
                list2.itemconfig(tkinter.END, fg='orange')
            else:
                list2.itemconfig(tkinter.END, fg='blue')

    # 创建标签显示服务端工作目录
    def lab():
        global label
        data = s.recv(1024)  # 接收目录
        lu = data.decode()
        try:
            label.destroy()
            label = tkinter.Label(root, text=lu)
            label.place(x=580, y=0, )
        except:
            label = tkinter.Label(root, text=lu)
            label.place(x=580, y=0, )
        recvList('dir', lu)

    # 进入指定目录(cd)
    def cd(message):
        s.send(message.encode())

    # 刚连接上服务端时进行一次面板刷新
    cd('cd same')
    lab()

    # 接收下载文件(get)
    def get(message):
        # print(message)
        names = message.split(' ')
        # print(names)
        names = names[1]  # 获取命令的第二个参数(文件名)
        # 选择对话框, 选择文件的保存路径
        fileName = tkinter.filedialog.asksaveasfilename(title='Save file to', initialfile=name)
        # 如果文件名非空才进行下载
        if fileName:
            s.send(message.encode())
            with open(fileName, 'wb') as f:
                while True:
                    data = s.recv(1024)
                    if data == 'EOF'.encode():
                        tkinter.messagebox.showinfo(title='Message',
                                                    message='Download completed!')
                        break
                    f.write(data)

    # 创建用于绑定在列表框上的函数
    def run(*args):
        indexs = list2.curselection()
        index = indexs[0]
        content = list2.get(index)
        # 如果有一个 . 则为文件
        if '.' in content:
            content = 'get ' + content
            get(content)
            cd('cd same')
        elif content == 'Return to the previous dir':
            content = 'cd ..'
            cd(content)
        else:
            content = 'cd ' + content
            cd(content)
        lab()  # 刷新显示页面

    # 在列表框上设置绑定事件
    list2.bind('<ButtonRelease-1>', run)

    # 上传客户端所在文件夹中指定的文件到服务端, 在函数中获取文件名, 不用传参数
    def put():
        # 选择对话框
        fileName = tkinter.filedialog.askopenfilename(title='Select upload file')
        # 如果有选择文件才继续执行
        if fileName:
            names = fileName.split('/')[-1]
            message = 'put ' + names
            s.send(message.encode())
            with open(fileName, 'rb') as f:
                while True:
                    a = f.read(1024)
                    if not a:
                        break
                    s.send(a)
                time.sleep(0.1)  # 延时确保文件发送完整
                s.send('EOF'.encode())
                tkinter.messagebox.showinfo(title='Message',
                                            message='Upload completed!')
        cd('cd same')
        lab()  # 上传成功后刷新显示页面

    # 创建上传按钮, 并绑定上传文件功能
    upload = tkinter.Button(root, text='Upload file', command=put)
    upload.place(x=600, y=353, height=30, width=80)

    # 关闭文件管理器
    def closeFile():
        root['height'] = 390
        root['width'] = 580
        # 关闭连接
        s.send('quit'.encode())
        s.close()

    # 创建关闭按钮
    close = tkinter.Button(root, text='Close', command=closeFile)
    close.place(x=685, y=353, height=30, width=70)


# 创建文件按钮
fBut = tkinter.Button(root, text='File', command=fileClient)
fBut.place(x=125, y=320, width=60, height=30)

# 创建多行文本框, 显示在线用户
listbox1 = tkinter.Listbox(root)
listbox1.place(x=445, y=0, width=130, height=320)


def users():
    global listbox1, ii
    if ii == 1:
        listbox1.place(x=445, y=0, width=130, height=320)
        ii = 0
    else:
        listbox1.place_forget()  # 隐藏控件
        ii = 1


# 查看在线用户按钮
button1 = tkinter.Button(root, text='Users online', command=users)
button1.place(x=485, y=320, width=90, height=30)

# 创建输入文本框和关联变量
a = tkinter.StringVar()
a.set('')
entry = tkinter.Entry(root, width=120, textvariable=a)
entry.place(x=5, y=350, width=570, height=40)



def send(*args):
    # 没有添加的话发送信息时会提示没有聊天对象
    users.append('------Group chat-------')
    print(chat)
    if chat not in users:
        tkinter.messagebox.showerror('Send error', message='There is nobody to talk to!')
        return
    if chat == name:
        tkinter.messagebox.showerror('Send error', message='Cannot talk with yourself in private!')
        return
    mes = entry.get() + ':;' + name + ':;' + chat  # 添加聊天对象标记
    s.send(mes.encode())
    a.set('')  # 发送后清空文本框


# 创建发送按钮
button = tkinter.Button(root, text='Send', command=send)
button.place(x=515, y=353, width=60, height=30)
root.bind('<Return>', send)  # 绑定回车发送信息


# 私聊功能
def private(*args):
    global chat
    # 获取点击的索引然后得到内容(用户名)
    indexs = listbox1.curselection()
    index = indexs[0]
    if index > 0:
        chat = listbox1.get(index)
        # 修改客户端名称
        if chat == '------Group chat-------':
            root.title(name)
            return
        ti = name + '  -->  ' + chat
        root.title(ti)


# 在显示用户列表框上设置绑定事件
listbox1.bind('<ButtonRelease-1>', private)


# 用于时刻接收服务端发送的信息并打印
def recv():
    global users
    while True:
        data = s.recv(1024)
        data = data.decode()
        # 没有捕获到异常则表示接收到的是在线用户列表
        try:
            data = json.loads(data)
            users = data
            listbox1.delete(0, tkinter.END)  # 清空列表框
            number = ('   Users online: ' + str(len(data)))
            listbox1.insert(tkinter.END, number)
            listbox1.itemconfig(tkinter.END, fg='green', bg="#f0f0ff")
            listbox1.insert(tkinter.END, '------Group chat-------')
            listbox1.itemconfig(tkinter.END, fg='green')
            for i in range(len(data)):
                listbox1.insert(tkinter.END, (data[i]))
                listbox1.itemconfig(tkinter.END, fg='green')
        except:
            data = data.split(':;')
            data1 = data[0].strip()  # 消息
            data2 = data[1]  # 发送信息的用户名
            data3 = data[2]  # 聊天对象
            markk = data1.split('：')[1]
            # 判断是不是图片
            pic = markk.split('#')
            # 判断是不是表情
            # 如果字典里有则贴图
            if (markk in dic) or pic[0] == '``':
                data4 = '\n' + data2 + '：'  # 例:名字-> \n名字：
                if data3 == '------Group chat-------':
                    if data2 == name:  # 如果是自己则将则字体变为蓝色
                        listbox.insert(tkinter.END, data4, 'blue')
                    else:
                        listbox.insert(tkinter.END, data4, 'green')  # END将信息加在最后一行
                elif data2 == name or data3 == name:  # 显示私聊
                    listbox.insert(tkinter.END, data4, 'red')  # END将信息加在最后一行
                if pic[0] == '``':
                    # 从服务端下载发送的图片
                    fileGet(pic[1])
                    w_box = 100
                    h_box = 100
                    fileName1 = './Client_image_cache/' + pic[1]
                    fileName2 = Image.open(fileName1)
                    w, h = fileName2.size
                    fileName = resize(w, h, w_box, h_box, fileName2)
                    print(fileName)
                    imagego = ImageTk.PhotoImage(fileName)
                    listbox.image_create(tkinter.END, image=imagego)
                else:
                    # 将表情图贴到聊天框
                    listbox.image_create(tkinter.END, image=dic[markk])
            else:
                data1 = '\n' + data1
                if data3 == '------Group chat-------':
                    if data2 == name:  # 如果是自己则将则字体变为蓝色
                        listbox.insert(tkinter.END, data1, 'blue')
                    else:
                        listbox.insert(tkinter.END, data1, 'green')  # END将信息加在最后一行
                    if len(data) == 4:
                        listbox.insert(tkinter.END, '\n' + data[3], 'pink')
                elif data2 == name or data3 == name:  # 显示私聊
                    listbox.insert(tkinter.END, data1, 'red')  # END将信息加在最后一行
            listbox.see(tkinter.END)  # 显示在最后

r = threading.Thread(target=recv)
r.start()  # 开始线程接收信息
root.mainloop()
s.close()  # 关闭图形界面后关闭TCP连接
