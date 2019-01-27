import requests
from bs4 import BeautifulSoup
import random
import re
import sqlite3
import numpy as np
from sklearn.naive_bayes import GaussianNB

 
desktop_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']
 
def random_headers():
    return {'User-Agent': random.choice(desktop_agents),'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}

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

def getClassifier():
	c,conn=databaseOpning()
	c.execute("select * from matches")
	data=c.fetchall()

	data=np.array(data)
	x=data[:,1:-2].astype(float)
	y=data[:,-2].astype(int)
	clf=GaussianNB()
	clf=clf.fit(x,y)
	databaseClosing(conn,c)
	return clf


clf=getClassifier()

def rocord(link):
	link=link+"&teamTabs=results"
	resultsBoardPage=requests.get(link,headers=random_headers()).text
	resultsBoardPage=BeautifulSoup(resultsBoardPage,"html.parser")
	wins=len(resultsBoardPage.findAll("span",{"class","w"}))
	equals=len(resultsBoardPage.findAll("span",{"class","d"}))
	loss=len(resultsBoardPage.findAll("span",{"class","l"}))
	return wins,equals,loss	

class teams():
	def __init__(self,name,link):
		self.name=name
		self.id=(re.search(r"(?i).*id=(.*)",link)).group(1)
		self.link="http://www.soccerbase.com"+link
		self.win,self.equal,self.loss=rocord(self.link)
	def getRank(self):
		source=requests.get(self.link,headers=random_headers()).text
		page=BeautifulSoup(source,"html.parser")
		ligne=page.find("tr",{"class","selected"})
		rank=ligne.find("td",{"calss","left"})
		rank=rank.text
		return int(rank)
	def __str__(self):
		return self.name+"  "+self.link+"  "+str(self.getRank())

def history(teamH,teamA): #head to head results
	link="http://www.soccerbase.com/teams/head_to_head.sd?team_id="+teamH.id+"&"+"team2_id="+teamA.id
	try:
		matches=requests.get(link,headers=random_headers()).text
		matches=BeautifulSoup(matches,"html.parser")
		tr=matches.find("tr",{"class","total"})
		results=tr.findAll("td")
		wins=int(results[1].text)
		equal=int(results[2].text)
		loss=int(results[3].text)
		allH2H=wins+equal+loss
		return round(wins/allH2H,5),round(loss/allH2H,5),round(equal/allH2H,5)
	except:
		return 1,1,1

def decide(teamH,teamA):
	return clf.predict([[teamH.win,teamH.equal,teamH.loss,teamH.getrank(),pw,pe,pl,teamA.win,teamA.equal,teamA.loss,teamA.getrank()]])

		

class games():
	def __init__(self,teamH,teamA,date,league):
		self.teamH=teamH
		self.teamA=teamA
		self.date=date
		self.pw,self.pe,self.pl=history(teamH,teamA)
		self.result=int(clf.predict([[self.teamH.win,self.teamH.equal,self.teamH.loss,self.teamH.getRank(),self.pw,self.pe,self.pl,self.teamA.win,self.teamA.equal,self.teamA.loss,self.teamA.getRank()]])[0])
		self.league=league
		
	def __str__(self):
		return self.date+"\n"+self.teamH.name+" - "+self.teamA.name+" : "+str(self.result)+"\n"
							
	


def getDate(match):
	date=match.find("td",{"class","dateTime"})
	time=date.find("span",{"class","time"})
	date=date.find("a")

	return date.text+" "+time.text





source=requests.get("http://www.soccerbase.com/matches/home.sd?type=3",headers=random_headers()).text
page=BeautifulSoup(source,"html.parser")
leagues=page.findAll("tbody")


for league in leagues:
	try:
		s=league.find("tr",{"class","headlineBlock"})
		link=s.find("a")
		print("***** "+link.text+" *******")
		matches=league.findAll("tr",{"class":"match"})
		for match in matches:
			dateMatch=getDate(match)
			if(dateMatch!=" ft"):   #re.search(r"(?i).*today.*",dateMatch)
				teamH=match.find("td",{"class","team homeTeam"})
				teamA=match.find("td",{"class","team awayTeam"})
				H=teamH.find("a")
				A=teamA.find("a")
				teamH=teams(H.text,H["href"])
				teamA=teams(A.text,A["href"])
				try:
					game=games(teamH,teamA,dateMatch,link.text)
					print(game)
				except:
					pass	
	except:
		pass


