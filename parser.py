#!encoding=utf-8
import gzip
import cStringIO
import chardet
from bs4 import BeautifulSoup
import urllib
import urllib2
import time
from datetime import datetime
import math
import sys

reload(sys)
sys.setdefaultencoding("utf-8")


def getPage(url):
    try:
#time.sleep(1)
        web = urllib.urlopen(url)
        page = web.read().decode('UTF-8')
        web.close()
        return page
    except:
        return None

def formatStr(s):
    s = s.replace('\n',' ').replace('\t',' ')
    return s.strip()

def getArticle(url):
    page = getPage(url)
    pageSoup = BeautifulSoup(page, "html.parser")
    title = str(pageSoup.title).replace('<title>','').replace('</title>','').strip()
    item = pageSoup.find_all('div',{'class':'zm-item-answer'})
    if item is None or len(item) == 0:
        return None

    answer = item[0].find('div',{'class':'zh-summary summary clearfix'}).get_text().strip()
    
    tmp = item[0].find('div',{'class':'zm-votebar'})
    tmp = tmp.find('button',{'class':'up '})
    vote = tmp.find('span',{'class':'count'}).get_text().strip()

    answer = formatStr(answer)
    ans_len = len(answer)
    if ans_len > 100:
        answer = answer[0:100]
    title = formatStr(title)
    print "title:",title
    print "answer:",answer
    print "vote:",vote
    out = [title, answer, str(ans_len), vote, url]
    print "out:",out

    return out

def getQuestions(start,offset='20'):
    #cookies = urllib2.HTTPCookieProcessor()
    #opener = urllib2.build_opener(cookies)
    #urllib2.install_opener(opener)

    header = {"Accept":"*/*",
    "Accept-Encoding":"gbk,utf-8,gzip,deflate,sdch",
    "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6",
    "Connection":"keep-alive",
    "Content-Length":"64",
    "Content-Type":"application/x-www-form-urlencoded; charset=utf-8",
    "Cookie":"_xsrf=e4cce6987b3b8ed8efb0d08937f7dcdf; _za=d9d43b7c-a7ef-4cd4-ae9d-8ffbb45ff81f; __utma=51854390.1328087801.1447661802.1447820210.1447824146.5; __utmc=51854390; __utmv=51854390.100-1|2=registration_date=20130730=1^3=entry_date=20130730=1; __utmz=51854390.1447661802.1.1.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/explore; cap_id=\"ODU0YzQ3NGFmMWE5NDRkZDk3NjA5MjI1MWQ3NDBlZWM=|1447048958|396aa3785130e12bacdb3522b7f75d951d198406\"; q_c1=2bc3ba3a28ba4102b3361d57f30aa49a|1445242349000|1445242349000; z_c0=\"QUFCQURyTWNBQUFYQUFBQVlRSlZUUTdFWjFic1ZZMGNkVVNrN28zT1dINHdqY3ItRnJTNldnPT0=|1447048974|6aad3ced89104407ad4f313d4f6d1734504e574f\"",
    "Host":"www.zhihu.com",
    "Origin":"http://www.zhihu.com",
    "Referer":"http://www.zhihu.com/log/questions",
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36",
    "X-Requested-With":"XMLHttpRequest"
    }

    parms = {'start':start,
            'offset':offset,
            '_xsrf':'e4cce6987b3b8ed8efb0d08937f7dcdf'}
    url = 'http://www.zhihu.com/log/questions'
    req = urllib2.Request(url,headers=header,data=urllib.urlencode(parms))
    content = urllib2.urlopen( req ).read()
    html = gzip.GzipFile(fileobj = cStringIO.StringIO(content)).read()
    html = eval(html)['msg'][1]
    pageSoup = BeautifulSoup(html, "html.parser")
    questions = []
    items = pageSoup.find_all('div',{'class':'zm-item'})
    for item in items:
        url = item.find_all('a',{'target':'_blank'})[0].get('href').rsplit('/',1)[1]
        questions.append(url)
    lastId = items[-1].get('id').split('-')[1]
    return questions,lastId
    
def craw():
    wf = open('zhihu.txt','a+')
    domain = 'http://www.zhihu.com/question/'
    #lastId = '404659437'
    lastId = '389059437'
    for i in xrange(10000):
        print i,lastId
        ques,lastId = getQuestions(lastId)
        for q in ques:
            try:
                out = getArticle(domain+q)
            except:
                continue
            if out == None:
                continue
            for j in xrange(len(out)):
                each = out[j]
#if j == 1:
#               each = each.encode('utf-8')
                wf.write(each)
                wf.write('\t')
            wf.write('\n')
    wf.close()
if __name__ == '__main__':
    craw()
