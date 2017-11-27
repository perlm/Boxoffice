from bs4 import BeautifulSoup
import requests, re, time, csv, os

###############################3
# scrape historic data from boxofficemojo.
# starting from https://github.com/csredino/Box-Office-Mojo-Scrapper/blob/master/bom.py
##################################

def getSoup(url):
        # scraping
        while True:
                try:
                        r = requests.get(url)
                        return BeautifulSoup(r.text, 'html.parser')
                except requests.ConnectionError:time.sleep(1)
		except requests.exceptions.ChunkedEncodingError:return None 


def get_all_movies():
	current_url=("http://www.boxofficemojo.com/movies/alphabetical.htm?letter=NUM&p=.html")# starting point for search, can be any letter
	movie_links=[]#initialize as an empty list

	#soup = BeautifulSoup(urlopen(current_url).read())	#generate list of links for the letter indices
	soup = getSoup(current_url)
	letters = soup.findAll('a', href= re.compile('letter='))
	letter_index=[] #intialize as an empty list
	for t in letters:
		letter_index.append("http://www.boxofficemojo.com" + t['href'])
	
	for i in range(0,27): #loop through all letter indices for movies

		current_url=letter_index[i]
		#soup = BeautifulSoup(urlopen(current_url).read())
		soup = getSoup(current_url)
		navbar=soup.find('div', 'alpha-nav-holder')
		pages = navbar.findAll('a', href= re.compile('alphabetical'))
		page_list=[] # page_list is reset for each letter index

		for t in pages:
			page_list.append("http://www.boxofficemojo.com" + t['href'])

		#movietable=soup.find('div',{'id':'main'})
		#movietable=soup.find('tr')
		movies = soup.findAll('a', href= re.compile('id='))
		
		
		for t in movies:
			movie_links.append("http://www.boxofficemojo.com" + t['href'])

		if pages != None: #this only runs if there is a 2nd page for this letter				
			i=0	#page list starts at 2 (consequence of page layout)
			while i<len(page_list): #loop over multiple pages for each letter index
				current_url=page_list[i] 
				#soup = BeautifulSoup(urlopen(current_url).read())
				soup = getSoup(current_url)
				movietable=soup.find('div',{'id':'main'})
				movies = movietable.findAll('a', href= re.compile('id='))
				for t in movies:
					movie_links.append("http://www.boxofficemojo.com" + t['href'])
				i+=1
	return(movie_links)

def scrape_movie(url):
	if "elizabeth" in url and "elizabethtown" not in url:#fixes an annoying encoding error in an inelegent way
		url='http://www.boxofficemojo.com/movies/?id=elizabeth%A0.htm'
	if "simpleplan" in url:
		url='http://www.boxofficemojo.com/movies/?id=simpleplan%A0.htm'

	# I'm going to use actuals.
	#current_url = (url + "&adjust_yr=2015&p=.htm")  #do all movies in 2015 dollars (done automatically by site with correct URL)
	
	#soup = BeautifulSoup(urlopen(current_url).read())
	soup = getSoup(url)

	#### DIRECTOR(S) - these are only capturing those with linked info. should be enough.
	directors=soup.findAll('a', href= re.compile('Director&id'))
	director_list=[]
	for t in directors:
		director_list.append(t.encode_contents())
	for i in range(0,2):
		if i>=len(director_list):
			director_list.append('N/A')#fill rest of list
	director = director_list[0]
	#director2=director_list[1]

	#### WRITER(S) 
	writers=soup.findAll('a', href= re.compile('Writer&id'))
	writer_list=[]
	for t in writers:
		writer_list.append(t.encode_contents())
	for i in range(0,2):
		if i>=len(writer_list):
			writer_list.append('N/A')
	writer=writer_list[0]
	#writer2=writer_list[1]

	#### COMPOSER(S)
	#composers=soup.findAll('a', href= re.compile('Composer&id'))
	#composer_list=[]
	#for t in composers:
	#	composer_list.append(t.encode_contents())
	#for i in range(0,2):
	#	if i>=len(composer_list):
	#		composer_list.append('N/A')
	#composer1=composer_list[0]
	#composer2=composer_list[1]

	#### ACTOR(S)
	actors=soup.findAll('a', href= re.compile('Actor&id'))
	actor_list=[]
	for t in actors:
		actor_list.append(t.encode_contents())
	for i in range(0,6):
		if i>=len(actor_list):
			actor_list.append('N/A')
	actor1=actor_list[0]
	actor2=actor_list[1]
	actor3=actor_list[2]
	#actor4=actor_list[3]
	#actor5=actor_list[4]
	#actor6=actor_list[5]
	
	#### PRODUCER(S)
	producers=soup.findAll('a', href= re.compile('Producer&id'))
	producer_list=[]
	for t in producers:
		producer_list.append(t.encode_contents())
	for i in range(0,6):
		if i>=len(producer_list):
			producer_list.append('N/A')
	producer=producer_list[0]
	#producer2=producer_list[1]
	#producer3=producer_list[2]
	#producer4=producer_list[3]
	#producer5=producer_list[4]
	#producer6=producer_list[5]

	weekend=soup.findAll('a', href= re.compile('wknd'))
	if weekend:
		l = weekend[0].get('href')
		years = re.search(r'yr=([0-9][0-9][0-9][0-9]).*wknd=([0-9]+)',l)
		year = years.group(1).encode("utf-8")
		wknd = years.group(2).encode("utf-8")
	else:    
		year = 'N/A'
		wknd = 'N/A'


	#I think I'll parse html with re cause I hear good things.
	openingWeekend='N/A'
	openingTheatres='N/A'
	opening=soup.findAll('div', attrs={"class":"mp_box_content"})
	if opening:
		for o in opening:
			openings = re.search(r'OpeningWeekend',o.encode("utf-8").decode('ascii','ignore'))
			if openings:
				openings1 = re.search(r'\$([0-9,]+)',o.encode("utf-8"))
				if openings1:
					openingWeekend = openings1.group(1)
				openings2 = re.search(r'([0-9,]+) theaters',o.encode("utf-8"))
				if openings2:
					openingTheatres = openings2.group(1)

	### OTHER INFO
	all_bs=soup.findAll('b')
	b_list=[] #lots of the information we want is in bold, and appears in the same order on each page
	for t in all_bs:
		if 'Domestic Lifetime' not in t.encode_contents():#want to ignore the lifetime box office
			b_list.append(t.encode_contents())
	if len(b_list)>=10:#avoids bad entries with no box office data
		if '$'in b_list[2] or 'n/a' in b_list[9]:#avoid movies w/o box office data, or unadjustable box office data, if not caught above
			if 'n/a' in b_list[9]:#has a foreign release only, order is shifted
				title=b_list[1]
				domestic='N/A'
				if 'N/A' not in b_list[2]:
					distributor=b_list[2].split('>')[1].split('<')[0]
				else:
					distributor=b_list[2]
				if len(b_list[3].split('>'))>3:#sometimes the release date is not in a hyperlink
					release=b_list[3].split('>')[2].split('<')[0]
				else:
					release=b_list[3].split('>')[1].split('<')[0]
				genre=b_list[4]
				runtime=b_list[5]
				rating=b_list[6]
				budget=b_list[7]
				worldwide=b_list[12]
			else:	#has a domestic release
				title=b_list[1]
				domestic=b_list[2]
				if 'n/a' not in b_list[3]:
					distributor=b_list[3].split('>')[1].split('<')[0]
				else:
					distributor=b_list[3]
				if len(b_list[4].split('>'))>3:#sometimes the release date is not in a hyperlink
					release=b_list[4].split('>')[2].split('<')[0]
				else:
					release=b_list[4].split('>')[1].split('<')[0]
				genre=b_list[5]
				runtime=b_list[6]
				rating=b_list[7]
				budget=b_list[8]
				if len(b_list)==11 or '%' not in b_list[11]:#this means it only has a domestic release
					worldwide='N/A'
				else:
					worldwide=b_list[13]


			return [url, title,director,domestic,distributor,release,genre,runtime,rating,budget,worldwide,actor1,actor2,actor3,producer,writer,year,wknd,openingTheatres,openingWeekend]



if __name__ == '__main__':

	# get all links
	linksCSV = '{0}/boxoffice/raw/links.csv'.format(os.path.expanduser("~"))
	if os.path.exists(linksCSV):
		movie_links = []
		with open(linksCSV,'r') as f1:
			for line in f1:
				movie_links.append(line.strip())
	else:
		movie_links = get_all_movies()
		f1 = open(linksCSV,'w')
		for l in movie_links:
			f1.write(l)
			f1.write("\n")

	# scrape each movie
	outputCSV = '{0}/boxoffice/raw/historic.csv'.format(os.path.expanduser("~"))
	if os.path.exists(outputCSV):
		with open(outputCSV,'r') as f1:
			for line in f1:
                                u=line.split(',')[0]
				#if u in movie_links:
				#	movie_links.remove(u)
				#	#print u, " removed"
		if u in movie_links:
			i = movie_links.index(u)
			print "starting from index ", i
			movie_links = movie_links[i+1:]
                f1 = open(outputCSV,'a+')
        else:
                f1 = open(outputCSV,'w')


	for url in movie_links:
		print url
		featureList = scrape_movie(url)
		if featureList is not None:
			for f in featureList:
				f = f.replace(',', '')
				f1.write(f+',')
			f1.write("\n")
		time.sleep(1)

