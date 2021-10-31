# -*- coding: utf-8 -*-#
import pandas as pd
import datetime
import time
import os
import math
from functools import reduce
import gzip
import requests
import re
import calendar
from styleframe import StyleFrame, Styler, utils
from bs4 import BeautifulSoup


url_sg = 'http://bidding.ningbo.gov.cn/cms/gcjsjyptdjxx/index.htm'  #宁波市公共资源交易中心-交易平台登记信息
url = 'http://bidding.ningbo.gov.cn'
# 获取时间点 起始点：当月1日 至 当天
td = datetime.datetime.today() - datetime.timedelta(days=0)
t1 = td.date()
now_date = t1.strftime("%y-%m-%d")
t3 = datetime.date(year=td.year, month=td.month, day=1)
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'Referer': 'http://bidding.ningbo.gov.cn/cms/jyxxgcjs/index.htm',
    'Host': 'bidding.ningbo.gov.cn',
    'UA-CPU': 'AMD64',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
}
s = requests.Session()
path = os.path.abspath(__file__)[:os.path.abspath(__file__).rfind('\\')]
file = pd.ExcelWriter(os.path.join(path, '交易平台施工登记信息'+now_date+'.xlsx'), engine='openpyxl')
county_list = ['北仑','慈溪','奉化','海曙','江北','宁海','象山','鄞州','余姚','镇海']


def searchCounty(title):
    for county in county_list:
        if county in title:
            return county
    return '区县未匹配'

def downloadImg(data):
    for tag in data:
        tag_dic = tag.attrs
        title = tag_dic['title']

        # 判断是否施工进场
        if '施工' in title:
            url_piece = url + tag_dic['href']
            res_piece = s.get(url_piece, headers=headers)
            content_piece = res_piece.content.decode('utf-8')
            soup_piece = BeautifulSoup(content_piece.replace(u'&nbsp', u''), 'html.parser')
            sg_list = soup_piece.select('img.Wzimg')
            if len(sg_list)==0:
                print(title+'没有图片')
            for sg in sg_list:
                img_url = sg['src']
                img_res = s.get(img_url, headers=headers)
                county = searchCounty(title)
                save_path = os.path.join(path, '施工登记图片\\' + county)
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                img_path = os.path.join(save_path, title + '.jpeg')
                with open(img_path, 'wb') as f:
                    f.write(img_res.content)


#   数据爬取
try:
    res = s.get(url_sg,headers=headers)
    if res.status_code == 200:
        print('——————————————————————————数据获取成功——————————————————————————')
    else:
        print('——————————————————————————数据获取失败——————————————————————————')
    content = res.content.decode('utf-8')
    msg = re.findall('共\d+条记录',content)
    num = re.findall('\d+',msg[0])
    num = int(num[0])
    soup = BeautifulSoup(content.replace(u'&nbsp',u''),'html.parser')
    data = soup.select('div.c1-body li a')
    downloadImg(data)

    for page in range(2,math.ceil(num/20)+1):
        url_page = url_sg.replace('index','index_'+str(page))
        headers['Referer'] = url_page
        res  = s.get(url_page, headers=headers)
        content = res.content.decode('utf-8')
        #print(content)
        soup = BeautifulSoup(content.replace(u'&nbsp', u''), 'html.parser')
        data = soup.select('div.c1-body li a')
        #print(data)
        downloadImg(data)
    print('success')
except Exception as e:
    print('出现异常：', e)
    print('发生异常所在的行数：', e.__traceback__.tb_lineno)
finally:
    s.close()
time.sleep(10)