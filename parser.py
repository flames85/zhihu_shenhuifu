#!encoding=utf-8
from __future__ import division
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
#from PIL import Image
import os
import commands

reload(sys)
sys.setdefaultencoding("utf-8")

# 0 : 不显示图片
# 1 : 以Preview显示图片(mac)
# 2 : 以img2txt.py显示图片
PREVIEW_MODE = 2

def getPage(url):
    try:
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
    # title
    title = formatStr(title)
    # all answers
    item = pageSoup.find_all('div',{'class':'zm-item-answer'})
    # if no answer
    if item is None or len(item) == 0:
        return None

    max_score = 0.0
    max_score_index = 0

    for i in xrange(len(item)):
        one_item = item[i]
        # answer
        tmp = one_item.find('div',{'class':'zm-editable-content clearfix'})
        answer = tmp.get_text().strip()
        answer = formatStr(answer)
        ans_len = len(answer) 

        # img
        tmp = tmp.find('img')
        imgUrl = ''
        if tmp != None:
            imgUrl = tmp['src']

        # vote
        tmp = one_item.find('div',{'class':'zm-votebar'})
        tmp = tmp.find('button',{'class':'up '})
        vote = tmp.find('span',{'class':'count'}).get_text().strip()
        # score
        i_vote = int(vote);
        if i_vote <= 1: # 可更改处:点赞数小于2我们就不看了
            continue
        score = (i_vote) / (5 + ans_len*ans_len/10) # 可更改处:分数计算公式
        if max_score < score:
            max_score = score
            max_score_index = i
            out = [title, answer, str(ans_len), vote, url, imgUrl]

    if max_score == 0.0:
        return None

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
#"User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36",
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/601.1.56 (KHTML, like Gecko) Version/9.0 Safari/601.1.56",
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
    exitCode,output = commands.getstatusoutput('date')
    print "开始阅读:",output
    # 1st flag
    bFirst = True
    # load last-id
    try:
        wf_last = open('lastid.txt', 'r')
        lastId = wf_last.read()
        wf_last.close()
    except:
        lastId = '776465144'

    if PREVIEW_MODE == 1:
        bPreview = False

    wf = open('zhihu.txt','a+')
    domain = 'http://www.zhihu.com/question/'
    for i in xrange(10000):
        # save last-id
        wf_last = open('lastid.txt', 'w')
        wf_last.write(lastId)
        wf_last.close()
        ques,lastId = getQuestions(lastId)
        # loop
        for q in ques:
            try:
                out = getArticle(domain+q)
                if out == None:
                    continue
            except:
                continue
            # write zhihu.txt
            wf.write(lastId)
            wf.write('\t')
            for j in xrange(len(out)):
                each = out[j]
                wf.write(each)
                wf.write('\t')
            wf.write('\n')

            # show
            if bFirst == True:
                print ">"
                bFirst = False
            else:
                raw_input(">")

            print "question:",out[0]
            print "answer  :",out[1]
            imgUrl = out[5]
            if len(imgUrl) != 0:
                # img: save&preview file
                urlFile = urllib2.urlopen(imgUrl)  
                imgData = urlFile.read()
                imgFile = file('preview.jpg',"wb")  
                imgFile.write(imgData)
                imgFile.close() 
                
                if PREVIEW_MODE == 1:
                    os.system('open -a Preview preview.jpg&')
                    bPreview = True
                elif PREVIEW_MODE == 2:
                    os.system('python img2txt.py preview.jpg --ansi')
                print "vote    :",out[3]
                print "url     :",out[4],"(",imgUrl,")"
            else:
                # img: 杀掉之前Preview
                if PREVIEW_MODE == 1:
                    if bPreview == True:
                        os.system('killall Preview')
                        bPreview = False
                print "vote    :",out[3]
                print "url     :",out[4]

    wf.close()
if __name__ == '__main__':
    craw()
