import requests
from bs4 import BeautifulSoup
import random
import re
import sqlite3
import traceback
import sys

def databaseOpning():
	try:
		conn=sqlite3.connect('database/history.db') #create database
		c=conn.cursor()
	except:
		print("error opning database")
		exit()	
	return c,conn


def databaseClosing(conn,c):
	conn.commit()
	c.close
	conn.close()
 
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

def getresult(match):
	sc=match.find("td",{"class","score"})
	sc=sc.find("a")
	return int(sc.findAll("em")[0].text)-int(sc.findAll("em")[1].text)



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
		self.gain=self.win-self.loss
	def getRank(self):
		try:
			source=requests.get(self.link,headers=random_headers()).text
			page=BeautifulSoup(source,"html.parser")
			ligne=page.find("tr",{"class","selected"})
			rank=ligne.find("td",{"calss","left"})
			rank=rank.text
			return int(rank)
		except:
			return 0	
	
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
		return wins/allH2H,loss/allH2H,equal/allH2H
	except:
		return 1,1,1



c,conn=databaseOpning()
source=requests.get("https://www.soccerbase.com/results/home.sd?type=3&group_by=tournament&comp_ids=66x4x59x69x9x12x93x58x13x64x63x14x1x60x15x2x70x62x3x61x68x98x103x83x173x104x73x84x311x134x194x116x132x137x171x19x205x25x138x122x133x76x113x127x306x118x117x48x47x112x206x96x23x124x92x208x24x101x22x123x91x310x111x170x20x264x207x281x126x114x21x78x80x77x226x75x225x56",headers=random_headers()).text
page=BeautifulSoup(source,"html.parser")
leagues=page.findAll("tbody")
for league in leagues:
	try:
		s=league.find("tr",{"class","headlineBlock"})
		link=s.find("a")
		print("***** "+link.text+" *******")
		matches=league.findAll("tr",{"class":"match"})
		for match in matches:
			teamH=match.find("td",{"class","team homeTeam"})
			teamA=match.find("td",{"class","team awayTeam"})
			H=teamH.find("a")
			A=teamA.find("a")
			teamH=teams(H.text,H["href"])
			teamA=teams(A.text,A["href"])
			result=getresult(match)
			try:
				pw,pe,pl=history(teamH,teamA)
				c.execute("insert into matches values("+match["id"][3:]+","+str(teamH.win)+","+str(teamH.equal)+","+str(teamH.loss)+","+str(teamH.getRank())+","+str(round(pw,5))+","+str(round(pe,5))+","+str(round(pl,5))+","+str(teamA.win)+","+str(teamA.equal)+","+str(teamA.loss)+","+str(teamA.getRank())+","+str(result)+",'"+link.text+"');")
				print(teamH.name+" - "+teamA.name)
				print(str(teamH.win)+" "+str(teamH.equal)+" "+str(teamA.loss)+" "+str(teamH.getRank()))	
			except:
				print(sys.exc_info())	
	except:
		print(sys.exc_info())
		
databaseClosing(conn,c)