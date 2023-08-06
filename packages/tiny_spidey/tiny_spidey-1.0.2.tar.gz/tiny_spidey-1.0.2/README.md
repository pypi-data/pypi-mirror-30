# tiny_spidey
A rather basic web crawler using BeautifulSoup. A whopping 36 lines.

## How to use
You will first be prompted to enter the full URL of your website to crawl from (including any http://).

Then, enter the length of the random walk. Depending on which weird websites the program hits, the walk might terminate early.

Finally, enter the total number of walks you want to do. Usually you'd just put 1 here. 

## Example output
```
~ Tiny Spidey 1.0 ~
(Full) start URL to crawl: http://mit.edu 
Number of (max) iterations: 10
Number of walks: 1
Commencing traversal number 0.

Traveling to: http://mitstory.mit.edu/
Traveling to: http://web.mit.edu
Traveling to: http://www.youtube.com/mit
Traveling to: http://www.youtube.com/yt/policyandsafety/
Traveling to: https://support.google.com/youtube/answer/2802245?ref_topic=2803240&hl=en
Traveling to: https://www.google.com/intl/en/options/
Traveling to: https://www.google.com/search/about/
Traveling to: https://www.google.com/about/
Traveling to: https://www.blog.google/press/
Traveling to: https://www.linkedin.com/company/google
Traversal complete.
```
