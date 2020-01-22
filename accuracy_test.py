import sqlite3
import numpy as np
import time
import matplotlib.pyplot as plt
import sys


from sklearn.naive_bayes import GaussianNB
clf=GaussianNB()

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

def graph(c):
	c.execute("select * from accuracy")
	data=np.array(c.fetchall())
	data_size=data[:,1]
	exact=data[:,2]
	proch=data[:,3]

	#le graph
	plt.plot(data_size,exact,label="exact")
	plt.plot(data_size,proch,label="proch")
	plt.legend()
	plt.xlabel("Data set size")
	plt.ylabel("Accuracy percentage")
	plt.show()


c,conn=databaseOpning()


exact=0
proch=0



c.execute("select * from matches")
data=c.fetchall()

data_size=len(data)
training_data_size=(data_size*70)//100


data=np.array(data)
x=data[:,1:-2].astype(float)
y=data[:,-2].astype(int)

from sklearn.feature_selection import VarianceThreshold
sel=VarianceThreshold(threshold=(.8 * (1 - .8)))
x=sel.fit_transform(x)

xt=x[:training_data_size]
yt=y[:training_data_size]


clf=clf.fit(xt,yt)


for match in range(training_data_size,data_size):
	pre=clf.predict([x[match]])
	if(np.sign(int(y[match]))==np.sign(int(pre[0]))):
		proch+=1
		if(int(y[match])==int(pre[0])):
			exact+=1			

proch=round(proch*100/(data_size-training_data_size),3)
exact=round(exact*100/(data_size-training_data_size),3)
date=int(time.time()/1000)

try:
	c.execute("insert into accuracy values("+str(date)+","+str(data_size)+","+str(exact)+","+str(proch)+")")
except:
	print(sys.exc_info())


graph(c)
databaseClosing(conn,c)
print("data size: "+str(data_size)+" ,"+"exact: "+str(exact)+" ,"+"proch: "+str(proch))