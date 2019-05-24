import  pymysql
import re
db=pymysql.connect(host='localhost',user='root',\
                   passwd='liang1010',database='Dict',charset='utf8')
cur=db.cursor()
f=open('dict.txt')
while True:
    data=f.readline()
    if not data:
        break
    L=re.findall(r'\S+',data)
    word=L[0]
    interpret=' '.join(L[1:])
    sql="insert into words (word,interpret)\
         values ('%s','%s');"%(word,interpret)
    try:
        cur.execute(sql)
        db.commit()
    except:
        db.rollback()
f.close()