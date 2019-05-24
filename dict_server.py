from socket import *
import os,sys
import signal
import pymysql
import time

DICT_TEXT='./dict.txt'
HOST='0.0.0.0'
PORT=8888
ADDR=(HOST,PORT)
def do_child(c,db):
    #循环接收客户端请求
    while True:
        data=c.recv(1024).decode()
        if data[0]=='R':
            do_register(c,db,data)
        if data[0]=='L':
            do_login(c,db,data)
        if (not data) or data=='E':
            c.close()
            sys.exit(0)
        if data[0]=='Q':
            do_query(c,db,data)
        if data[0]=='H':
            do_hist(c,db,data)

def do_register(c,db,data):
    data=data.split()
    name=data[1]
    passwd=data[2]
    cur=db.cursor()
    sql="select * from user where name='%s';"%name
    cur.execute(sql)
    r=cur.fetchone()#获取查询结果
    if r !=None:
        c.send('Exist'.encode())
        return
    sql2="insert into user(name,passwd) values('%s','%s');"%(name,passwd)
    try:
        cur.execute(sql2)
        db.commit()
        c.send(b'ok')
    except:
        db.rollback()
        c.send(b'Fail')
    else:
        print('%s注册成功'%name)
def do_login(c,db,data):
    data=data.split()
    name=data[1]
    passwd=data[2]
    cur=db.cursor()
    sql1="select name from user where name='%s'"%name
    cur.execute(sql1)
    r=cur.fetchone()
    if r==None:
        c.send(b'not exsist')
        return
    sql2="select passwd from user where name='%s'"%name
    cur.execute(sql2)
    r=cur.fetchone()
    print(r)
    if r[0]!=passwd:
        c.send(b'Fault')
        return
    c.send(b'ok')

def do_query(c,db,data):
    data = data.split()
    name = data[1]
    word = data[2]
    cur=db.cursor()
    #内部定义函数可以不用再传参
    def insert_history():
        tm=time.ctime()
        sql="insert into hist(name,word,time) values('%s','%s','%s');"%(name,word,tm)
        try:
            cur.execute(sql)
            db.commit()
        except:
            db.rollback()

    #文本查询操作
    try:
        f=open(DICT_TEXT)
    except:
        c.send(b'Fail')
        return
    for line in f:
        tmp=line.split(' ')[0]
        if tmp > word:
            c.send(b'Fail')
            break
        if tmp==word:
            c.send(b'ok')
            time.sleep(0.1)
            c.send(line.encode())
            f.close()
            insert_history()
            return
    c.send(b'Fail')
    f.close()

def do_hist(c,db,data):
    data=data.split()
    name=data[1]
    cur=db.cursor()
    sql="select * from hist where name='%s'"%name
    cur.execute(sql)
    r=cur.fetchall()
    if not r:
        c.send(b'Fail')
        return
    else:
        c.send(b'ok')
        for i in r:
            time.sleep(0.1)
            msg='%s %s %s'%(i[1],i[2],i[3])#返回是一个元组
            c.send(msg.encode())
        time.sleep(0.1)
        c.send(b'##')

def main():
    #创建数据库连接
    db = pymysql.connect(host='localhost', user='root', \
                         passwd='liang1010', database='Dict', charset='utf8')
    cur=db.cursor()
    #创建套接字
    s=socket(AF_INET,SOCK_STREAM)
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen(5)
    print('进程%d等待客户端的连接'%os.getpid())
    #忽略子进程退出
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)
    while True:
        try:
            c,addr=s.accept()
        except KeyboardInterrupt:
            s.close()
            sys.exit('服务器退出')
        except Exception as e:
            print(e)
            continue
        print('已连接客户端:',addr)
        pid=os.fork()
        if pid==0:
            s.close()#在子进程中没有用
            print('正在处理子进程请求')
            do_child(c,db)

        else:
            c.close()#在父进程中没有用
            continue
if __name__=='__main__':
    main()
