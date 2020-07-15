import socket
import threading
import queue
import json  # json.dumps(some)打包   json.loads(some)解包
import time
import os
import os.path
import requests
import sys
import math
import sqlite3
IP = '192.168.43.244'
PORT =5000
url = 'http://192.168.43.244:8003/wp'
que = queue.Queue()                             # 用于存放客户端发送的信息的队列
users = []                                      # 用于存放在线用户的信息  [conn, user, addr]
lock = threading.Lock()                         # 创建锁, 防止多个线程写入数据的顺序打乱

def connect(url, user,key,name):
    data = {
        'Type': 1,
        'id': user,
        'name': name,
        'key': key
    }
    #print("////")
    headers = {'content-type': 'application/json'}  # 必须是json
    r=requests.post(url, data=data)
    return True

def back(url, user):
    data = {
        'Type': 3,
        'id': user
    }
    headers = {'content-type': 'application/json'}  # 必须是json
    r=requests.post(url, data=data)
    return True

def survey(url,Sname,Dname,content,sort):
    data = {
        'Type': 2,
        'Sname':Sname,
        'Dname':Dname,
        'content':content,
        'sort':sort
    }
    headers = {'content-type': 'application/json'}  # 必须是json
    r=requests.post(url, data=data)
    return True
#处理登录请求
#创建数据库存储登录信息
def create_sql():
    print("------------------------------------------------------------")
    conn=sqlite3.connect("data.db")
    cur=conn.cursor()
    #创建表
    cur.execute("""CREATE TABLE IF NOT EXISTS
                %s(
                %s integer primary key ,
                %s varchar(128),
                %s varchar(128))"""
                %('test',
                'user',
                'key',
                'name'))
    conn.close()
create_sql()
#查找用户名是否存在
def showdata(username):
    sql=sqlite3.connect('C:\\Users\\Administrator\\Desktop\\chat\\python\\data.db')
    #print("/////")
    data=sql.execute("select * from test where user='%s'" % username).fetchone()
    sql.close()
    return data
# 检查用户名密码是否正确
def check_user(user, key):
    print("login: user: " + user + ", key: " + key)
    data= showdata(user)
    print("data:",data)
    if data:
        if data[1]==key:
            print("验证成功")
            return True
        else:
            print("验证失败")
            return False
    else:
        print("用户未注册")
        return False
def add_user(user, key,name):
    try:
        print("register: user: " + user + ", key: " + key+",name:"+name)
        data=showdata(user)
        if data:
            print("用户已存在")
            return "1"
        else:
            sql = sqlite3.connect("data.db")
            sql.execute("insert into test(user,key,name) values(?,?,?)", (user, key,name))
            sql.commit()
            print("添加成功")
            sql.close()
            return "0"
    except Exception as e:
        print("添加用户数据出错：" + str(e))
        return "2"

    # 获取变长字符串
def recv_all_string(_conn):
        # 获取消息长度
        length = int.from_bytes(_conn.recv(4), byteorder='big')
        b_size = 3 * 1024  # 注意utf8编码中汉字占3字节，英文占1字节
        times = math.ceil(length / b_size)
        content = ''
        for i in range(times):
            if i == times - 1:
                seg_b = _conn.recv(length % b_size)
            else:
                seg_b = _conn.recv(b_size)
            content += str(seg_b, encoding='utf-8')
        return content


def send_string_with_length(_conn,content):
    # 先发送内容的长度
    _conn.sendall(bytes(content, encoding='utf-8').__len__().to_bytes(4, byteorder='big'))
    # 再发送内容
    _conn.sendall(bytes(content, encoding='utf-8'))

def handle_login(_conn, addr):
        user = recv_all_string(_conn)
        key = recv_all_string(_conn)
        check_result = check_user(user, key)
        print(check_result)
        if check_result:
            _conn.sendall(bytes("1", "utf-8"))
            data = showdata(user)
            name = data[2]
            print("name:", name)
            connect(url, user, key, name)
            send_string_with_length(_conn, name)
            return False
        else:
            _conn.sendall(bytes("0", "utf-8"))
            send_string_with_length(_conn, "no")

        return True
# 处理注册请求
def handle_register(_conn, addr):
    name = recv_all_string(_conn)
    user = recv_all_string(_conn)
    key = recv_all_string(_conn)
    _conn.sendall(bytes(add_user(user, key,name), "utf-8"))
    return True

# 处理请求线程的执行方法
def handle(_conn, addr):
    try:
        while True:
            # 获取请求类型
            _type = str(_conn.recv(1), "utf-8")
            # 是否继续处理
            _goon = True
            if _type == "1":  # 登录请求
                print("开始处理登录请求")
                _goon = handle_login(_conn, addr)
            elif _type == "2":  # 注册请求
                print("开始处理注册请求")
                _goon = handle_register(_conn, addr)
            if not _goon:
                break
    except Exception as e:
        print(str(addr) + " 连接异常，准备断开: " + str(e))




#####################################################################################


# 将在线用户存入online列表并返回
def onlines():
    online = []
    for i in range(len(users)):
        online.append(users[i][1])
    return online


class ChatServer(threading.Thread):
    global users, que, lock

    def __init__(self, port):
        threading.Thread.__init__(self)

        self.ADDR = ('', port)

        os.chdir(sys.path[0])
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    # 用于接收所有客户端发送信息的函数
    def tcp_connect(self, conn, addr):
       while True:
        handle(conn,addr)
        # 连接后将用户信息添加到users列表
        user = conn.recv(1024)                                    # 接收用户名
        user = user.decode()

        for i in range(len(users)):
            if user == users[i][1]:
                print('User already exist')
                user = '' + user + '_2'

        if user == 'no':
            user = addr[0] + ':' + str(addr[1])
        users.append((conn, user, addr))
        print(' New connection:', addr, ':', user, end='')         # 打印用户名
        d = onlines()                                                   # 有新连接则刷新客户端的在线用户显示
        self.recv(d, addr)
        try:
            while True:
                data = conn.recv(1024)
                data = data.decode()
                self.recv(data, addr)                         # 保存信息到队列
            conn.close()
        except:
            print(user + ' Connection lose')
            back(url, user)
            self.delUsers(conn, addr)                             # 将断开用户移出users
            conn.close()

    # 判断断开用户在users中是第几位并移出列表, 刷新客户端的在线用户显示
    def delUsers(self, conn, addr):
        a = 0
        for i in users:
            if i[0] == conn:
                users.pop(a)
                print(' Remaining online users: ', end='')         # 打印剩余在线用户(conn)
                d = onlines()
                self.recv(d, addr)
                print(d)
                break
            a += 1

    # 将接收到的信息(ip,端口以及发送的信息)存入que队列
    def recv(self, data, addr):
        lock.acquire()
        try:
            que.put((addr, data))
        finally:
            lock.release()

    # 将队列que中的消息发送给所有连接到的用户
    def sendData(self):
        while True:
            if not que.empty():
                message = que.get()                               # 取出队列第一个元素
                x=0
                if isinstance(message[1], str):                   # 如果data是str则返回Ture
                    for i in range(len(users)):
                        # user[i][1]是用户名, users[i][2]是addr, 将message[0]改为用户名
                        for j in range(len(users)):
                            if message[0] == users[j][2]:
                                print(' this: message is from user[{}]'.format(j))
                                data4 = ' ' + users[j][1] + '：' + message[1]
                                if x==0:
                                    data =data4.split(':;')
                                    data1 = data[0].strip()  # 消息
                                    data2 = data[1]  # 发送信息的用户名
                                    data3 = data[2]  # 聊天对象
                                    markk = data1.split('：')[1]
                                    print("data1:",markk,"data2:",data2,"data3:",data3)
                                    # 判断是不是图片
                                    pic = markk.split('#')
                                    # 判断是不是表情
                                    # 如果字典里有则贴图
                                    if pic[0] == '``':
                                        survey(url,data2, data3, markk, 2)    #发送图片消息到web,    群聊对象这里为“------Group chat-------”！！！！！！
                                        x=x+1
                                    elif pic[0] == '||':
                                        survey(url, data2, data3, markk, 3)
                                        x = x + 1
                                    else:
                                        survey(url, data2, data3, markk, 1)  #1,2,3分别指消息，图片和文件，忘了，可以稍作修改
                                        x = x + 1
                                    print(data4)
                                break
                        users[i][0].send(data4.encode())
                # data = data.split(':;')[0]
                if isinstance(message[1], list):  # 同上
                    # 如果是list则打包后直接发送  
                    data4 = json.dumps(message[1])
                    for i in range(len(users)):
                        try:
                            users[i][0].send(data4.encode())
                        except:
                            pass

    def run(self):

        self.s.bind(self.ADDR)
        self.s.listen(5)
        print('Chat server starts running...')
        q = threading.Thread(target=self.sendData)
        q.start()
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()
        self.s.close()

################################################################


class FileServer(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        # self.setDaemon(True)
        self.ADDR = ('', port)
        # self.PORT = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.first = r'.\resources'
        os.chdir(self.first)                                     # 把first设为当前工作路径
        # self.conn = None

    def tcp_connect(self, conn, addr):
        print(' Connected by: ', addr)
        
        while True:
            data = conn.recv(1024)
            data = data.decode()
            if data == 'quit':
                print('Disconnected from {0}'.format(addr))
                break
            order = data.split(' ')[0]                             # 获取动作
            self.recv_func(order, data, conn)
                
        conn.close()

    # 传输当前目录列表
    def sendList(self, conn):
        listdir = os.listdir(os.getcwd())
        listdir = json.dumps(listdir)
        conn.sendall(listdir.encode())

    # 发送文件函数
    def sendFile(self, message, conn):
        name = message.split()[1]                               # 获取第二个参数(文件名)
        fileName = r'./' + name

        with open(fileName , 'rb') as f:
            while True:
                a = f.read(1024)
                if not a:
                    break
                conn.send(a)
        time.sleep(0.1)                                          # 延时确保文件发送完整
        conn.send('EOF'.encode())

    # 保存上传的文件到当前工作目录
    def recvFile(self, message, conn):
        name = message.split()[1]
        fileName = r'./' + name
        with open(fileName, 'wb') as f:
            while True:
                data = conn.recv(1024)
                if data == 'EOF'.encode():
                    break
                f.write(data)
        survey(url, 0, 0, name, 3)

    # 切换工作目录
    def cd(self, message, conn):
        message = message.split()[1]                          # 截取目录名
        # 如果是新连接或者下载上传文件后的发送则 不切换 只将当前工作目录发送过去
        if message != 'same':
            f = r'./' + message
            os.chdir(f)
        # path = ''
        path = os.getcwd().split('\\')                        # 当前工作目录
        for i in range(len(path)):
            if path[i] == 'resources':
                break
        pat = ''
        for j in range(i, len(path)):
            pat = pat + path[j] + ' '
        pat = '\\'.join(pat.split())
        if 'resources' not in path:
            f = r'./resources'
            os.chdir(f)
            pat = 'resources'
        conn.send(pat.encode())

    # 判断输入的命令并执行对应的函数
    def recv_func(self, order, message, conn):
        if order == 'get':
            return self.sendFile(message, conn)
        elif order == 'put':
            return self.recvFile(message, conn)
        elif order == 'dir':
            return self.sendList(conn)
        elif order == 'cd':
            return self.cd(message, conn)

    def run(self):
      #  print('File server starts running...')
        self.s.bind(self.ADDR)
        self.s.listen(3)
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()
        self.s.close()

#############################################################################


class PictureServer(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)
        # self.setDaemon(True)
        self.ADDR = ('', port)
        # self.PORT = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.conn = None
        os.chdir(sys.path[0])
        self.folder = '.\\Server_image_cache\\'  # 图片的保存文件夹

    def tcp_connect(self, conn, addr):
        while True:
            data = conn.recv(1024)
            data = data.decode()
            print('Received message from {0}: {1}'.format(addr, data))
            if data == 'quit':
                break
            order = data.split()[0]  # 获取动作
            self.recv_func(order, data, conn)
        conn.close()
        print('---')

    # 发送文件函数
    def sendFile(self, message, conn):
        print(message)
        name = message.split()[1]                   # 获取第二个参数(文件名)
        fileName = self.folder + name               # 将文件夹和图片名连接起来
        f = open(fileName, 'rb')
        while True:
            a = f.read(1024)
            if not a:
                break
            conn.send(a)
        time.sleep(0.1)                             # 延时确保文件发送完整
        conn.send('EOF'.encode())
        print('Image sent!')

    # 保存上传的文件到当前工作目录
    def recvFile(self, message, conn):
        print(message)
        name = message.split(' ')[1]                   # 获取文件名
        fileName = self.folder + name                  # 将文件夹和图片名连接起来
        print(fileName)
        print('Start saving!')
        f = open(fileName, 'wb+')
        while True:
            data = conn.recv(1024)
            if data == 'EOF'.encode():
                print('Saving completed!')
                break
            f.write(data)

    # 判断输入的命令并执行对应的函数
    def recv_func(self, order, message, conn):
        if order == 'get':
            return self.sendFile(message, conn)
        elif order == 'put':
            return self.recvFile(message, conn)

    def run(self):
        self.s.bind(self.ADDR)
        self.s.listen(5)
     #   print('Picture server starts running...')
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()
        self.s.close()

#####################################################################################

if __name__ == '__main__':
    cserver = ChatServer(PORT)
    fserver = FileServer(PORT + 1)
    pserver = PictureServer(PORT + 2)
    cserver.start()
    fserver.start()
    pserver.start()
    while True:
        time.sleep(1)
        if not cserver.isAlive():
            print("Chat connection lost...")
            sys.exit(0)
        if not fserver.isAlive():
            print("File connection lost...")
            sys.exit(0)
        if not pserver.isAlive():
            print("Picture connection lost...")
            sys.exit(0)
input("gogo")