###############################################
#
# This program will run a script that will 
# search for the age, gender, and year of the 
# earliest mention of a cell line. 
#
# @Author: Anthony Sciarini
# @Version: 5/31/2018
#
################################################

###############
#IMPORTED LIBS#
###############
import sys				#System commands lib
import unicodedata			#Unicode lib
import requests				#HTTP request lib
import re				#Regular Expression lib
import csv				#Comma seperated values lib
from bs4 import BeautifulSoup	        #Process HTML documents lib

##########################################################################################
#This class contains all the functions needed to scrap cell line info rom html documents.
##########################################################################################
class Cell_scraper:

	#############
	#Constructor# ~ This guy will take the http URL and grab the HTML page it leads to.
	#############
	def __init__(self, url):

		#Make HTTP request
		req = requests.request('GET', url)

		#Grab the HTML that contains the search results for the cell
		self.results_page = BeautifulSoup(req.content, 'html.parser')

		# ~ Find the first hyper link if it exists
		first_link = self.results_page.find('tr')

		if str(first_link) != 'None':				
			next_url = 'https://web.expasy.org/' + first_link.a['href']		
			# ~ Get HTML page that the first hyper link leads to.
			req = requests.request('GET', next_url)		
			self.page = BeautifulSoup(req.content, 'html.parser')
			self.connection = True
		else:
			self.connection = False

	#########				
	#Funtion# ~ Look up the content stored at a table row.
	#########
	def table_look_up(self, table_row):	
		if self.connection == True:	
			#Loop through each row in the page's table
			for row in self.page.find_all('tr'):
				if str(row.th) != 'None':
					if str(row.th.string) == table_row:
						return row.td.contents[0].string
			else:
				return 'NA'
		else:
			return 'NA'
 
	##########
	#Function# ~ Find min year in publication section.
	##########
	def min_pub_yr(self):	
		if self.connection == True:
			#Search for all years		
			yr_19 = re.findall('[ \( , ' ' ]19\d{2}[\) , ' ' , \.]' , str(self.page))
			yr_20 = re.findall('[ \( , ' ' ]20\d{2}[\) , ' ' , \.]' , str(self.page))
	
			#Concatinate lists together
			result = yr_19 + yr_20 
		
			#Convert list to string
			result = map(self.sub_str,result)
			result = map(int, result)
	
			#Return result
			if len(result) is 0:
				return 'NA'
			else:
				return str(min(result))
		else:
			return 'NA'
	##########
	#Function# ~ Sub string function used to remove the parentheses around the years in publication
	##########   refereneces.
	def sub_str(self,str):
		return str[1:len(str)-1]
	
	##########
	#Function# ~ Find the min year and ethnicity in cell line collections TODO
	##########
	def scrape_clc(self):
		
		if self.connection == True:		
			#Return message
			rtn = ''		
	
			#Grab cell line collections row from expasy page
			clc = ''
			for row in self.page.find_all('tr'):
				if str(row.th) != 'None':
					if str(row.th.string) == 'Cell line collections':
						clc = row
						break
			#If no cell pages return NA for min cell year and ethnicity	
			if clc == '':
				return 'NA,NA'
	
			#Append all the hyper links in cell line collections section
			links = []
			for link in clc.find_all('a'):
				#print link.string
				links.append(link['href'])
			
			#Grab min year from publication	
			rtn += self.grab_min_year_and_ethnicity(links) 
		
			return rtn
		else:
			return 'NA,NA'

	##########	
	#Function#				TODO FIGURE OUT WAY WE HAVE DUPLICATE YEARS
	##########
	def grab_years(self , tag_type , url_page):
		yrs = []
		for tag in url_page.find_all(tag_type):
			#Convert HTML to unicode then back to ascii form to filter out any unreadable characters				
			tag_str = unicodedata.normalize('NFKD', unicode(tag)).encode('ascii' , 'ignore')  	
			#Use regex to search through each HTML tag for years
		
			
			#Add \. to LHS
			
       			yrs += re.findall('[ ^ , \( , \s , \> ]19\d{2}[ \) , \s , \. , ; , $ , \< ]' , str(tag_str))
			yrs += re.findall('[ ^ , \( , \s , \> ]20\d{2}[ \) , \s , \. , ; , $ , \< ]' , str(tag_str))
			
		return yrs

	###########
	#Functions# ~ Scrape through HTML code for each cell line and grab the years 
	###########
	def grab_min_year_and_ethnicity(self,links):

		if self.connection == True:

			master_yr_list = []
			ethnicity = 'NA'
			for url in links:
			
				#Print url for testing	
				#print url
				
				#############################
				#Grab min year and Ethnicity#
				#############################
				#Create list to store years and a String to store the ethnicity#
				yrs = []
	
				#Skip Cell line collections that have no useful information
				bad_url = ['en.pasteur.ac' , 'clsgmbh' , 'ibvr.org' , 'kcb.kiz' , 'cellbank.snu.ac.kr' , 'coriell.org', 
					  'www.fli.de/en/services', 'dtp.cancer.gov']

	                        is_bad = False

				#Loop through list of bad urls
				for url_str in bad_url:
					#If this is a bad url then flip url flag
					if url_str in url:
						is_bad = True
						break

				#If bad url flag was tripped then skip to the end of the loop.
				if is_bad is True:
					continue
			
				#Prevents program from crashing if it opens up a private server.
				try:
			        	url_req = requests.request('GET', url)
				except requests.exceptions.SSLError:
					#'failed to connect to web page'
					continue			

				#Grab HTML from the page, prepare lists for years
       				url_page = BeautifulSoup(url_req.content,'html.parser')

				#Depending on the cell line collection, search ONLY in the tags where years amd ethnicity related to cell
				#line can be found.

				#Scrape for the cells ethnicity
				if 'brc.riken' in url:
					ethnicity = self.grab_ethnicity(url_page, ethnicity)

			        #Scrape years from <span> tags
				if 'www.phe-culturecollections.org' in url:
					#Search for years
					yrs += self.grab_years('span' , url_page)	
					
					#Search for ethnicity
					ethnicity = self.grab_ethnicity(url_page , ethnicity)
					
				#Scrape years from <dd> tags
				if 'dsmz.de/catalogues' in url:
					#Search for years
					yrs += self.grab_years('dd' , url_page)	
					
					#Search for ethnicity
					ethnicity = self.grab_ethnicity(url_page , ethnicity)
					
				#Scrape years from <p> tags	
				if 'www.atcc.org' in url or 'www.addexbio.com' in url:
					#Search for years
					yrs += self.grab_years('p' , url_page)	
					
					#Search for ethnicity
					ethnicity = self.grab_ethnicity(url_page , ethnicity)
					
				#scrape years from <td> tags
				if 'www.atcc.org' in url or 'catalog.bcrc.firdi.org' in url or 'iclc.it/details' in url or 'http://cellbank.nibiohn.go.jp' in url or 'idac.tohoku.ac' in url:	
					#Search for years
					yrs += self.grab_years('td' , url_page)	
					
					#Search for ethnicity
					ethnicity = self.grab_ethnicity(url_page , ethnicity)
					
				#scrape years from <div> tags
				if 'http://bcrj.org.br' in url:
					#Search for years
					yrs += self.grab_years('div' , url_page)	
					
					#Search for ethnicity
					ethnicity = self.grab_ethnicity(url_page, ethnicity)			
				
			        #Convert elements of list from string -> int
				yrs = map(self.sub_str, yrs)  			
				yrs = map(int, yrs)

				#Print years fro testing
				#print 'All of the years pulled from this page: '
				#print yrs

				#Append the minimum year if one exists
			        if len(yrs) is not 0 :
			                master_yr_list.append(min(yrs))
				
			#Print over all minimum year
			if len(master_yr_list) is not 0:
			        return str(min(master_yr_list)) + ',' + str(ethnicity)
			else:
				return 'NA' + ',' + str(ethnicity)	
		else:
			return 'NA,NA'	


	##########
	#Function# 
	##########
	def grab_ethnicity(self,url_page,cell_eth):
		#Types of possible ethinicites for cell lines.
		categories = ['Caucasian' , 'caucasian' , 'Chinese' ,'chinese' , 'Japanese' , 'japanese' , 
			      'Filipino' , 'filipino' , 'Korean' , 'korean' , 'Vietnamese', 'vietnamese',
			      'African American' , 'african american']
		
		#Search the entire HTML page for the ethnicity
		#Convert HTML to unicode then back to ascii form to filter out any unreadable characters
                page_str = unicodedata.normalize('NFKD', unicode(url_page)).encode('ascii' , 'ignore')			
		

		if cell_eth == 'NA':
			for ethnicity in categories:
				if ethnicity in str(page_str):
					return ethnicity
			else:
				return cell_eth
		else:
			return cell_eth
	
######	
#Main# ~ Main function.
######
def main():

	####################
	# Acquire URL List #
	####################
	
	# How to look up cell line data for cellosaurus by URL!!!
	# https://web.expasy.org/cgi-bin/cellosaurus/search?input=your_query	

	#Print out the column titles in csv format
	print 'Cell.line.name,Synonyms,Sex,Age,Minimun.pub.med.year,Minimum.cell.line.collection.year,Ethnicity'

	#Opening a the cell_lines xcell spread sheet
	with open('lunc_cells.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		
		#Query template
		query_url = 'https://web.expasy.org/cgi-bin/cellosaurus/search?input='
	
		#List to contain the queries
		query_list = []

		#Make a query for each cell line and add it to the query list
		for row in reader:
                	query_list.append(query_url + row['Cell line primary name'])

		#Print basic info for each cell
		iteration = 1
		for query in query_list:
			obj = Cell_scraper(query)
			#Print out in csv format
			print obj.table_look_up('Cell line name') + ',' + obj.table_look_up('Synonyms') + ',' + obj.table_look_up('Sex of cell') + ',' + obj.table_look_up('Age at sampling') + ',' + obj.min_pub_yr() + ',' + obj.scrape_clc() 
			
			#print '__________' + str(iteration) + '__________'
			#print obj.table_look_up('Cell line name')
			#print obj.table_look_up('Synonyms')
			#print obj.table_look_up('Sex of cell')
			#print obj.table_look_up('Age at sampling')
			#print obj.min_pub_yr()
			#print obj.scrape_clc()
			#iteration += 1	
#############
#Run Program#
#############				
if __name__ == '__main__':
	main()

#TEST - FIX IT SO WE CAN PULL FROM <TD> TAGS FROM ATTC PAGES

#TODO - Find a way to determine what cell line it came from.
	#Use a dictionary some how...
#UTLIMATE TODO! - Make sure we can retreive data from all cell line websites
	#Make a list of all cell lines and note what HTML tags the years are contained in.
	#Make sure to only search through those tags for that cell line. This will improve speed and reduce chances of
	#picking up a date unrealted to the cell line. 

##############
#TESTING ZONE#
##############                  
#req = requests.request('GET' , 'https://web.expasy.org/cgi-bin/cellosaurus/search?input=ABC-1')
#page = BeautifulSoup(req.content, 'html.parser')
#print page
#lst = []

#for tag in page.find_all('p'):
#	tag_str = unicodedata.normalize('NFKD', unicode(tag)).encode('ascii' , 'ignore')	
#	print tag_str

#	lst += re.findall('[ ^ , \( , \s , > ]19\d{2}[ \) , \s , \. , ; , \Z , <]' , str(tag_str))
#	lst += re.findall('[ ^ , \( , \s , > ]20\d{2}[ \) , \s , \. , ; , \Z , <]' , str(tag_str))


#print lst

'''
test_str = 'Baillie-Johnson H, Twentyman PR, Fox NE, Walls GA, Workman P, Watson JV, Johnson N, Reeve JG, Bleehen NM.1985. Establishment and characterisation of cell lines from patients with lung cancer (predominantly small cell carcinoma). Br J Cancer. 52(4):495-504 PMID: 2998422; Cancer Genet Cytogenet 1988;30:212'

lst = []
lst += re.findall('[ ^ , \( , \s , \. ,  >]19\d{2}[ \) , \s , \. , ; , \Z , <]' , test_str)

print test_str
print lst
'''



