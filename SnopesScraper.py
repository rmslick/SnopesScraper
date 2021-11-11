from bs4 import BeautifulSoup
import requests
import json 
from lxml import html
import os

import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
class BoxLayoutApp(App):
	def __init__(self):
		App.__init__(self)
		self.selections = set([]) 
		self.scrapeInSession = False
		self.dirPath = ""
		self.dirInput = TextInput(multiline=False)
	'''
		Can programatically acquire.
		Some will not work.
	'''
	def GetCategories(self):
		return ['technology','science','computers','medical']
	def selection(self, instance, *args):
		if instance.text in self.selections:
			self.selections.remove(instance.text)
		else:
			self.selections.add(instance.text)
		#print(self.selections)

	def CollectFullCategory(self,category,totalDocs=10):
		articleIndex = 1
		while articleIndex < totalDocs:

			articleIndex += 1
	def StartScrapeTrue(self):
		
		if not self.scrapeInSession:
			print('Starting scrape true...')
			self.scrapeInSession = True
			# scrape for each category
			for category in self.selections:
				# get all documents that are true for each category
				pageNumIndex = 1
				articleIndex = 1
				articleDict = {}
				# read all pages in category
				while(True):

					url = "https://www.snopes.com/fact-check/category/"+category+"/page/"+str(pageNumIndex)+"/"
					req = requests.get(url)
					soup = BeautifulSoup(req.text, "html.parser")
					
					print("[INFO] Scraping ",category," page ",pageNumIndex,'...')
					#print("Total articles: ",len(soup.find_all('article')))
					if len(soup.find_all('article')) == 0:
						print("[INFO] Finished scraping category:",category)
						break
					for tag in soup.find_all('article'):
						articleURL = ""
						for anchor in tag.find_all('a', {'class' :'stretched-link'}):
							# collect only if false
							articleURL = anchor['href']
						spans = tag.find_all('span', {'class' : 'small font-weight-bold rating-label-true'},recursive=True)
						if len(spans) >0:
							print('[INFO] Article: ',articleURL," is true.")
							page = requests.get(articleURL)
							soupPage = BeautifulSoup(page.content, 'html.parser')
							articleDict[articleIndex] = {}
							articleDict[articleIndex]["url"] = articleURL
							# Get title
							title = soupPage.find_all('h1',{'class':'title'},recursive=True)
							#print(len(title))
							for t in title:
								articleDict[articleIndex]["title"] = str(t.text.strip('\n'))
							# Get subtitle
							subTitle = soupPage.find_all('h2',{'class':'subtitle'},recursive=True)
							for t in subTitle:
								articleDict[articleIndex]["subtitle"] = str(t.text.strip('\n'))
			                # Get Author
							authors = soupPage.find_all('ul',{'class':'list-unstyled authors list-unstyled d-flex flex-wrap comma-separated'},recursive=True)
							articleDict[articleIndex]["authors"] = []
							for auth in authors:
								for a in auth.find_all('a',recursive=True):
									articleDict[articleIndex]["authors"].append(a.text)
		                	# Get Date
							publishedDate = soupPage.find_all('time',recursive=True)
							articleDict[articleIndex]["publish-date"] = set([])
							for dates in publishedDate:
								articleDict[articleIndex]["publish-date"].add(dates.text)
							articleDict[articleIndex]["publish-date"] = list(articleDict[articleIndex]["publish-date"])
							# Get feature figure
							articleDict[articleIndex]["main-figure"] = ""
							mainFigure = soupPage.find_all('img',{'class':"figure-image embed-responsive-item object-fit-cover"},recursive=True)
							for image in mainFigure:
								articleDict[articleIndex]["main-figure"] = image['src']
								break
							# Get claim
							articleDict[articleIndex]["claim"] = ""
							claimTag = soupPage.find_all('div',{'class':"claim-text card-body"},recursive=True)            
							
							for c in claimTag:
								articleDict[articleIndex]["claim"] += c.text
		                	# Get body
							article_text = ''
							article = soupPage.find("div", {"class":"single-body card card-body rich-text"}).findAll(['p','blockquote'])
							for element in article:
								article_text += '\n' + ''.join(element.findAll(text = True))
							articleDict[articleIndex]["fullArticle"] = article_text
							articleIndex += 1
					pageNumIndex += 1
				# Save off entire category of true documents
				truthPath = self.dirPath+"/"+category+"_true.json"
				print('Category',category, " written to ", truthPath)
				with open(truthPath, "w") as outfile:
					json.dump(articleDict, outfile)
			# end scrape	
			self.scrapeInSession = False
			# write out data
			
	def StartScrapeFalse(self):
		
		if not self.scrapeInSession:
			print('Starting scrape false...')
			self.scrapeInSession = True
			# scrape for each category
			for category in self.selections:
				# get all documents that are true for each category
				pageNumIndex = 1
				articleIndex = 1
				articleDict = {}
				# read all pages in category
				while(True):

					url = "https://www.snopes.com/fact-check/category/"+category+"/page/"+str(pageNumIndex)+"/"
					req = requests.get(url)
					soup = BeautifulSoup(req.text, "html.parser")
					
					print("Scraping ",category," page ",pageNumIndex,'...')
					#print("Total articles: ",len(soup.find_all('article')))
					if len(soup.find_all('article')) == 0:
						print("[INFO] Finished scraping category:",category)
						break
					for tag in soup.find_all('article'):
						articleURL = ""
						for anchor in tag.find_all('a', {'class' :'stretched-link'}):
							# collect only if false
							articleURL = anchor['href']
						spans = tag.find_all('span', {'class' : 'small font-weight-bold rating-label-false'},recursive=True)
						if len(spans) >0:
							print('[INFO] Article: ',articleURL," is true.")
							page = requests.get(articleURL)
							soupPage = BeautifulSoup(page.content, 'html.parser')
							articleDict[articleIndex] = {}
							articleDict[articleIndex]["url"] = articleURL
							# Get title
							title = soupPage.find_all('h1',{'class':'title'},recursive=True)
							#print(len(title))
							for t in title:
								articleDict[articleIndex]["title"] = str(t.text.strip('\n'))
							# Get subtitle
							subTitle = soupPage.find_all('h2',{'class':'subtitle'},recursive=True)
							for t in subTitle:
								articleDict[articleIndex]["subtitle"] = str(t.text.strip('\n'))
			                # Get Author
							authors = soupPage.find_all('ul',{'class':'list-unstyled authors list-unstyled d-flex flex-wrap comma-separated'},recursive=True)
							articleDict[articleIndex]["authors"] = []
							for auth in authors:
								for a in auth.find_all('a',recursive=True):
									articleDict[articleIndex]["authors"].append(a.text)
		                	# Get Date
							publishedDate = soupPage.find_all('time',recursive=True)
							articleDict[articleIndex]["publish-date"] = set([])
							for dates in publishedDate:
								articleDict[articleIndex]["publish-date"].add(dates.text)
							articleDict[articleIndex]["publish-date"] = list(articleDict[articleIndex]["publish-date"])
							# Get feature figure
							articleDict[articleIndex]["main-figure"] = ""
							mainFigure = soupPage.find_all('img',{'class':"figure-image embed-responsive-item object-fit-cover"},recursive=True)
							for image in mainFigure:
								articleDict[articleIndex]["main-figure"] = image['src']
								break
							# Get claim
							articleDict[articleIndex]["claim"] = ""
							claimTag = soupPage.find_all('div',{'class':"claim-text card-body"},recursive=True)            
							
							for c in claimTag:
								articleDict[articleIndex]["claim"] += c.text
		                	# Get body
							article_text = ''
							article = soupPage.find("div", {"class":"single-body card card-body rich-text"}).findAll(['p','blockquote'])
							for element in article:
								article_text += '\n' + ''.join(element.findAll(text = True))
							articleDict[articleIndex]["fullArticle"] = article_text
							articleIndex += 1
					pageNumIndex += 1
				# Save off entire category of true documents
				truthPath = self.dirPath+"/"+category+"_false.json"
				print('Category',category, " written to ", truthPath)
				with open(truthPath, "w") as outfile:
					json.dump(articleDict, outfile)
			# end scrape	
			self.scrapeInSession = False
			# write out data
	def StartScrape(self,instance):
		# Validate filepath exists
		self.dirPath = self.dirInput.text
		if self.dirPath[len(self.dirPath)-1] == "/":
			self.dirPath = self.dirPath[0:len(self.dirPath)-1]
			print('Trimmed to: ', self.dirPath) 
		print('Dirpath:',self.dirPath)
		self.StartScrapeTrue()
		self.StartScrapeFalse()
	def build(self):
		
		layout = GridLayout(cols = 1)
		
		layout.add_widget(self.dirInput)

		categories = self.GetCategories()
		
		for i in range(len(categories)):
			b1 = BoxLayout(orientation='horizontal')
			b1.add_widget(Label(text= str(categories[i])))
			cb = CheckBox(active = False)
			cb.text = str(categories[i])
			b1.add_widget(cb)
			cb.bind(active = self.selection)
			layout.add_widget(b1)
		layout.add_widget(Button(text="Scrape!",on_press=self.StartScrape))
		return layout

root = BoxLayoutApp()


root.run()
