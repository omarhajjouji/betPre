import sqlite3
import numpy as np
from sklearn.naive_bayes import GaussianNB
import time
import matplotlib.pyplot as plt
import sys

# better classifier but not stable 
#from sklearn.ensemble import RandomForestClassifier
#clf = RandomForestClassifier(n_estimators=100)

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
c.execute("select * from matches group by League")
leagues=list(c)

exact=0
proch=0
final_data_size=0
final_training_data_size=0

for league in leagues:
	try:
		league_name=league[13]
		c.execute("select * from matches where League='"+league_name+"'")
		data=c.fetchall()

		data_size=len(data)
		final_data_size+=data_size
		training_data_size=(data_size*70)//100
		final_training_data_size+=training_data_size

		data=np.array(data)
		x=data[:,1:-2].astype(float)
		y=data[:,-2].astype(int)

		xt=x[:training_data_size]
		yt=y[:training_data_size]
		clf =GaussianNB()
		clf=clf.fit(xt,yt)


		for match in range(training_data_size,data_size):
			pre=clf.predict([x[match]])
			if(np.sign(int(y[match]))==np.sign(int(pre[0]))):
				proch+=1
				if(int(y[match])==int(pre[0])):
					exact+=1
	except:
		pass				

proch=round(proch*100/(final_data_size-final_training_data_size),3)
exact=round(exact*100/(final_data_size-final_training_data_size),3)
date=int(time.time()/1000)

try:
	c.execute("insert into accuracy values("+str(date)+","+str(final_data_size)+","+str(exact)+","+str(proch)+")")
except:
	print(sys.exc_info())

graph(c)
databaseClosing(conn,c)
print("data size: "+str(final_data_size)+" ,"+"exact: "+str(exact)+" ,"+"proch: "+str(proch))
