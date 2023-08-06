import random
from urllib.request import urlopen
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup		# I love BeautifulSoup and I only discovered it 20 minutes ago.

def crawl(start, iters): 
	"""
	@param start: full URL from where to start random walk
	@param iters: number of iterations/timesteps in the random walk
	@returns: list of URLs the walk visited, including start URL
	"""
	output = []
	link = start		# initialize link
	last_link = start	# useful pointer to fall back to

	for _ in range(iters): 
		try:						# if opening link is troublesome, revert to last link
			file = urlopen(link)	# open link, get html file
		except:
			link = last_link		# continue from last link
			continue
		soup = BeautifulSoup(file, 'html.parser')				# get soup
		links = [l.get('href') for l in soup.find_all('a')]		# get list of links in page
		if len(links) == 0:										# if there are no more links to go to:
			link = last_link									# try again from previous link
			continue
		links = [l for l in links if bool(urlparse(l).netloc)]	# reduce to only absolute links (more interesting)
		url = random.choice(links)								# pick next URL u.a.r
		link = urljoin(link, url)								# make accessible to future iterations
		output.append(link)

	return output