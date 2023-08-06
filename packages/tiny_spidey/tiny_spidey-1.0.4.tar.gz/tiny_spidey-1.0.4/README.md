# tiny_spidey
A rather basic web crawler using BeautifulSoup. A whopping 32 lines.

## How to install
``` pip install tiny_spidey ```

## How to use
```python
>>> import tiny_spidey
>>> tiny_spidey.crawl("http://mit.edu/",5) # crawl(source_url, number_of_iterations)
['https://giving.mit.edu/give/now ', 'https://plus.google.com/+mit', 'http://news.mit.edu/2018/student-profile-jasmin-joseph-0410?utm_source=&utm_medium=&utm_campaign=', 'http://campkesem.org/mit']
```
