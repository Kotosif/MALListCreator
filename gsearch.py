import sys
import requests, socket, time
import gzip
from io import StringIO
import re, random, types

from bs4 import BeautifulSoup 

base_url = 'https://www.google.com.hk/'
results_per_page = 10

user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0 Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0."

class GoogleAPI:
    def __init__(self):
        timeout = 40
        socket.setdefaulttimeout(timeout)

    def randomSleep(self):
        sleeptime =  random.randint(60, 120)
        time.sleep(sleeptime)

    #extract the domain of a url
    def extractDomain(self, url):
        domain = ''
        pattern = re.compile(r'http[s]?://([^/]+)/', re.U | re.M)
        url_match = pattern.search(url)
        if(url_match and url_match.lastindex > 0):
            domain = url_match.group(1)

        return domain

    #extract a url from a link
    def extractUrl(self, href):
        url = ''
        pattern = re.compile(r'(http[s]?://[^&]+)&', re.U | re.M)
        url_match = pattern.search(href)
        if(url_match and url_match.lastindex > 0):
            url = url_match.group(1)

        return url 

    # extract serach results list from downloaded html file
    def extractSearchResults(self, html):
        results = list()
        soup = BeautifulSoup(html, 'html.parser')
        result_block = soup.find_all('div', attrs={'class': 'g'})
        for result in result_block:
            title = result.find('h3', attrs={'class': 'r'})
            if title:
                title = title.get_text()
                results.append(title)
        return results

    # search web
    # @param query -> query key words 
    # @param lang -> language of search results  
    # @param num -> number of search results to return 
    def search(self, query, site = '', lang='en', num=results_per_page):
        search_results = list()
        query = requests.utils.requote_uri(query)
        if(num % results_per_page == 0):
            pages = int(num / results_per_page)
        else:
            pages = int(num / results_per_page + 1)

        for p in range(0, pages):
            start = p * results_per_page
            siteFilter = '' if site == '' else "site:" + site
            url = '%s/search?hl=%s&num=%d&start=%s&q=%s' % (base_url, lang, results_per_page, start, query)
            url += siteFilter
            retry = 3
            while(retry > 0):
                try:
                    headers = { 'User-Agent': user_agent,
                                'connection':'keep-alive',
                                'Accept-Encoding': 'gzip',
                                'referer': base_url
                            }
                    response = requests.get(url, headers=headers)
                    html = response.text 
                    
                    results = self.extractSearchResults(html)
                    search_results.extend(results)
                    break
                except (requests.HTTPError, requests.RequestException) as e:
                    print( 'request error:', e)
                    self.randomSleep()
                    retry = retry - 1
                    continue
                
                except Exception as e:
                    print( 'error:', e)
                    retry = retry - 1
                    self.randomSleep()
                    continue
        return search_results 

def crawler():
    # Create a GoogleAPI instance
    api = GoogleAPI()
    results = []
    keyword = sys.argv[1]
    # check if site filter exists
    if len(sys.argv) >= 3:
        site = sys.argv[2]
        results = api.search(keyword, site = site)
    else:
        results = api.search(keyword, site = site)
    for r in results:
        print(r)
    return results

if __name__ == '__main__':
    crawler()
