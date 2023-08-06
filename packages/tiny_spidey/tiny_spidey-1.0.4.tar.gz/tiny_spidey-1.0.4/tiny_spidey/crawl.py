import random
from urllib.request import urlopen
from urllib.parse import urljoin, urlparse
from urllib.error import URLError
from bs4 import BeautifulSoup		# I love BeautifulSoup and I only discovered it 20 minutes ago.
import webbrowser

def crawl(start, iters, picky=True, backtrack=True): 
	"""
	Starts at a URL and executes a random walk with uniform distribution on outgoing edges.
	Returns the list of vertices making up the walk. 

	@param start: set of full URLs from where to start random walk
	@param iters: set of number of iterations/timesteps in the random walk
	@param picky: if True, only walk to neighbor sites with different base URL than current site
	@param backtrack: if True, always attempts to fill walk by retreating to last viable link
	@returns: list of URLs the walk visited, including start URL
	"""
	link = start		# initialize link
	last_link = start	# useful pointer to fall back to
	output = [start]	# initialize output list, including start URL

	for _ in range(iters): 
		try:						# if opening link is troublesome, revert to last link
			file = urlopen(link)	# open link, get html file
		except:
			output.pop()		# link we added last iteration should be removed
			link = last_link	# continue from last link
			continue
		soup = BeautifulSoup(file, 'html.parser')				# get soup
		links = [l.get('href') for l in soup.find_all('a')]		# get list of links in page
		if len(links) == 0:	
			if backtrack:
				output.pop()									
				link = last_link								# try again from previous link
				continue
			break
		if picky:	# reduce links to those that have different netloc
			links = [l for l in links if urlparse(l).netloc != urlparse(link).netloc]
		url = random.choice(links)								# pick next URL u.a.r
		link = urljoin(link, url)								# make accessible to future iterations
		output.append(link)

	return output

def live_crawl(start, iters, picky=True, backtrack=True):
	"""
	Same as crawl(), but gives a console interface for actually opening the default browser to show the walk.
	"""
	print("\nGenerating walk...\n")
	walk = crawl(start, iters, picky, backtrack)	# generate the list of vertices to travel
	print("Walk generated. Successively press ENTER to go through the walk live.")

	for site in walk:
		input("\nNow visiting "+site+". \nGo? ")
		webbrowser.open_new_tab(site)

	print("\nWalk complete.")

