import sqlite3
import numpy as np
from sklearn.naive_bayes import GaussianNB
import time

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
data_size=len(data)
training_data_size=(data_size*70)//100

data=np.array(data)
x=data[:,1:-2].astype(float)
y=data[:,-2].astype(int)

xt=x[:training_data_size]
yt=y[:training_data_size]
clf =GaussianNB()
clf=clf.fit(xt,yt)

exact=0
proch=0

for match in range(training_data_size,data_size):
	pre=clf.predict([x[match]])
	if(np.sign(int(y[match]))==np.sign(int(pre[0]))):
		proch+=1
		if(int(y[match])==int(pre[0])):
			exact+=1

proch=round(proch*100/(data_size-training_data_size),3)
exact=round(exact*100/(data_size-training_data_size),3)
date=int(time.time()/1000)

c.execute("insert into accuracy values("+str(date)+","+str(data_size)+","+str(exact)+","+str(proch)+")")
databaseClosing(conn,c)