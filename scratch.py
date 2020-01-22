import sqlite3
import numpy as np
from sklearn.naive_bayes import GaussianNB


def databaseOpning():
	try:
		conn=sqlite3.connect('database\\history.db') #create database
		c=conn.cursor()
	except:
		print("error opning database")
		exit()	
	return c,conn


def databaseClosing(conn,c):
	conn.commit()
	c.close
	conn.close()

c,conn=databaseOpning()
c.execute("select * from matches")
data=c.fetchall()

data=np.array(data)
x=data[:,1:-2].astype(float)
y=data[:,-2].astype(int)



xt=x[:80]
yt=y[:80]
clf =GaussianNB()
clf=clf.fit(xt,yt)

s=0
for i in range(32):
	pre=clf.predict([x[80+i]])
	if(int(y[80+i])==int(pre[0])):
		s+=1
print(s)


databaseClosing(conn,c)