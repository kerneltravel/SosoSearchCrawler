#!/usr/bin/python  
#-*- coding: utf-8 -*-
#
# Create by Meibenjin. 
# Modified by kerneltravel
#
# Last updated: 2013-09-21
#
# soso.com search results crawler 

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import urllib2, socket, time
import re, random, types

from bs4 import BeautifulSoup 

base_url = 'http://www.soso.com'

user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0', \
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0', \
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533+ \
        (KHTML, like Gecko) Element Browser 5.0', \
        'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)', \
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)', \
        'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14', \
        'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) \
        Version/6.0 Mobile/10A5355d Safari/8536.25', \
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/28.0.1468.0 Safari/537.36', \
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)']

# results from the search engine
# basically include url, title,content
class SearchResult:
    def __init__(self):
        self.url= '' 
        self.title = '' 
        self.content = '' 

    def getURL(self):
        return self.url

    def setURL(self, url):
        self.url = url 

    def getTitle(self):
        return self.title

    def setTitle(self, title):
        self.title = title

    def getContent(self):
        return self.content

    def setContent(self, content):
        self.content = content

    def printIt(self, prefix = ''):
        print 'url\t->', self.url.decode('utf-8')
        print 'title\t->', self.title.decode('utf-8')
        print 'content\t->', self.content.decode('utf-8')
        print 

    def writeFile(self, filename):
        file = open(filename, 'a')
        try:
            file.write('url:' + self.url+ '\n')
            file.write('title:' + self.title + '\n')
            file.write('content:' + self.content + '\n\n')

        except IOError, e:
            print 'file error:', e
        finally:
            file.close()


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

    # extract serach results list from downloaded html file
    def extractSearchResults(self, html):
        results = list()
        soup = BeautifulSoup(html)
        div = soup.find('div', attrs={'id':'result', 'class':'result'} )
        if (type(div) != types.NoneType):
            lis = div.findAll('li')
            if(len(lis) > 0):
                for li in lis:
                    result = SearchResult()
                    h3 = li.find('h3')
                    if(type(h3) == types.NoneType):
                        continue

                    # extract domain and title from h3 object
                    link = h3.find('a')
                    if (type(link) == types.NoneType):
                        continue

                    url = link['href']
                    #url = self.extractDomain(url)
                    if(cmp(url, '') == 0):
                        continue
                    title = link.renderContents()
                    title = title.replace("<em>",'').replace("</em>",'')
                    result.setURL(url)
                    result.setTitle(title)

                    span = li.find('p', {'class': 'ds'})
                    if (type(span) != types.NoneType):
                        content = span.renderContents()
                        content = content.replace("<em>",'').replace("</em>",'').replace('...','')
                        result.setContent(content)
                    results.append(result)
        return results

    # search web of pageId page 
    # @param url of main search url 
    # @param pageId -> index of search results page
    def searchPerPage(self, urltmp, pageId):
        url = "%s%d"%(urltmp,pageId)
        #print 'url: %s'%url
        request = urllib2.Request(url)
        length = len(user_agents)
        index = random.randint(0, length-1)
        user_agent = user_agents[index] 
        request.add_header('User-agent', user_agent)
        request.add_header('connection','keep-alive')
        response = urllib2.urlopen(request)
        html = response.read() 
        results = self.extractSearchResults(html)
        return results

    # search web
    # @param query -> query key words 
    # @param lang -> language of search results  
    # @param num -> number of search results to return 
    def search(self, query, lang='en', num=10):
        query = urllib2.quote(query)
        #print 'query: %s, base:%s'%(query,base_url)
        search_results = list()
        pageId = 1
        #url = '%s/search?hl=%s&num=%d&q=%s' % (base_url, lang, num, query)
        url = '%s/q?w=%s%%20site%%3Apan.baidu.com&lr=&sc=web&ch=w.p&num=%d&gid=&cin=&site=&sf=0&sd=0&nf=&pg='%(base_url, query, num)
        #print 'url %s'%url
        str = ''
        retry = 3
        while(retry > 0):
            try:
                results = self.searchPerPage(url,pageId)
                while (len(results)>0):
                    pageId += 1
                    search_results += results
                    if len(results)<(num/2): #no need to search next page if curpage result less then half of num. cur page is the last page
                        break
                    results = list()
                    results = self.searchPerPage(url,pageId)
                    #print 'results len: %d,%d'%(len(results),pageId)
                return search_results
            except urllib2.URLError,e:
                print 'url error:', e
                self.randomSleep()
                retry = retry - 1
                continue
            
            except Exception, e:
                print 'error:', e
                retry = retry - 1
                self.randomSleep()
                continue
        return search_results
        
def test():
    if(len(sys.argv) < 2):
        print 'please enter search query.'
        return
    query = sys.argv[1]
    api = GoogleAPI()
    result = api.search(query)
    for r in result:
        r.printIt()
    print 'result len: %d'%len(result)
    #result_s = set(result)
    #print 'result len: %d'%len(result_s)

if __name__ == '__main__':
    test()
