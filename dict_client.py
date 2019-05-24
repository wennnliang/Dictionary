from socket import *
import os,sys
import time
import getpass
def do_register(s):
    while True:
        name=input('请输入姓名：')
        passwd=getpass.getpass()
        passwd1=getpass.getpass('Again:')
        if (' 'in name) or (' 'in passwd):
            print('用户名和密码不许有空格')
            continue
        if passwd!=passwd1:
            print('两次密码不一致')
            continue
        msg='R {} {}'.format(name,passwd)
        s.send(msg.encode())
        data=s.recv(1024).decode()
        if data=='ok':
            return 0
        elif data=='Exist':
            return 1
        else:
            return 2
def do_login(s):
    while True:
        name=input('请输入姓名：')
        passwd=getpass.getpass()
        if (' 'in name) or (' 'in passwd):
            print('密码或姓名输入错误')
            continue
        msg='L {} {}'.format(name,passwd)
        s.send(msg.encode())
        data=s.recv(1024).decode()
        if data=='ok':
            return name #确保知道是谁登录的
        elif data=='not exsist':
            return 1
        elif data=='Fault':
            return 2
def login(s,name):
    while True:
        print('''===========查询界面===========
                  1.查词   2.历史记录    3.退出
                 ==============================''')
        try:
            com=int(input('输入选项>>>'))
        except Exception as e:
            print('命令错误')
            continue
        if com  not in[1,2,3]:
            print('请输入正确选项')
            sys.stdin.flush()#清楚标准输入
            continue
        elif com==1:
            do_query(s,name)
        elif com==2:
            do_hist(s,name)
        elif com==3:
            return
def do_query(s,name):
    while True:
        word=input('输入您要查询的单词：')
        if word=='##':
            break
        msg='Q {} {}'.format(name,word)
        s.send(msg.encode())
        data=s.recv(1024).decode()
        if data=='ok':
            data=s.recv(2048).decode()
            print(data)
        else:
            print('查不到这个单词')
def do_hist(s,name):
    msg='H {}'.format(name)
    s.send(msg.encode())
    data=s.recv(1024).decode()
    if data=='ok':
        time.sleep(0.1)
        while True:
            data=s.recv(2048).decode()
            if data=='##':
                break
            print(data)
    else:
        print('查不到历史记录')


def main():
    if len(sys.argv)<3:
        print('argv is wrong')
        return
    HOST=sys.argv[1]
    PORT=int(sys.argv[2])
    ADDR=(HOST,PORT)
    s=socket()
    try:
        s.connect(ADDR)
    except:
        print('服务器连接失败')
        return
    while True:
        print('''========Welcome=========
                  1.注册   2.登录    3.退出
                 ========================''')
        try:
            com=int(input('输入选项>>>'))
        except Exception as e:
            print('命令错误')
            continue
        if com  not in[1,2,3]:
            print('请输入正确选项')
            sys.stdin.flush()#清楚标准输入
            continue
        elif com==1:
            L=do_register(s)
            if L==0:
                print('注册成功')
            elif L==1:
                print('用户不存在')
            else:
                print('密码错误')
        elif com==2:
            L=do_login(s)
            if L==1:
                print('用户不存在')
            elif L==2:
                print('密码错误')
            else:
                print('登录成功')
                login(s,L)
        elif com==3:
            s.send(b'E')
            sys.exit('谢谢使用')
if __name__=='__main__':
    main()