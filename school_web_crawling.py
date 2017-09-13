#!/usr/bin/python
#coding:utf-8

import pandas as pd
import numpy as np
import urllib,urllib2,requests
from bs4 import BeautifulSoup
import datetime,time
import random
import json
import sys
import re
import lxml
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)



class ConfigInfo(object):

    def __init__(self,dict_p_district={}):
        self.dict_p_district=dict_p_district

    #省份列表
    def get_dict_provinces(self):
        dict_provinces={
        u'北京':1000
        }
        '''
        dict_provinces={
        u'北京':1000,u'上海':1160,u'天津':1180,u'广东':1019,u'湖南':3206,u'广西':3343,u'江西':3467,u'贵州':3578,
        u'云南':3676,u'西藏':3822,u'海南':3903,u'甘肃':3911,u'宁夏':4013,u'青海':4040,u'新疆':4092,u'香港':4188,
        u'澳门':4207,u'福建':3111,u'浙江':3009,u'安徽':2886,u'重庆':1199,u'辽宁':1240,u'江苏':1355,u'湖北':1475,
        u'四川':1587,u'陕西':1790,u'河北':1908,u'山西':2092,u'河南':2223,u'吉林':2401,u'黑龙江':2471,u'内蒙古':2614,
        u'山东':2728,u'台湾':4216
        }
        '''
        return dict_provinces

    #区域列表
    def get_dict_p_district(self):
        return self.dict_p_district

    #设定省份对应区域
    def set_dict_p_district(self,main_key,temp_id,temp_value):
        try:
            self.dict_p_district[main_key][temp_id]=temp_value
        except Exception as e:
            self.dict_p_district[main_key]={temp_id:temp_value}


    #获取当前时间
    def get_time(self):
        x =  time.localtime(time.time())
        timenow=time.strftime('%Y-%m-%d_%H_%M_%S',x)
        return timenow
    #获取文件名
    def get_file_name(self):
        timenow = self.get_time()
        return 'school_%s.csv' % timenow

    def get_outformat(self):
        #行政区，标题内容，小区，户型，大小，楼层，位置，总价，单价
        return 'school_id,province,district,school_name,school_type,address'+'\n'



class WebDownloadInfo(object):
    __user_agent = 'Mozilla/5.0 (compatible; MSIE 5.5; Windows NT)'
    #user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    __headers = { 'User-Agent' : __user_agent }

    def __init__(self,province=0,districts=0):
        self.province=province
        self.districts=districts

    def get_total_pages(self):
        pass

    #获取学校列表页面url地址
    def get_list_url(sefl,temp_province=0,temp_district=None,page=1):
        base_url='http://school.zhongkao.com/province/'
        if page == 1:
            if temp_district:
                return base_url+str(temp_province)+'/'+str(temp_district)
            else:
                return base_url+str(temp_province)
        elif page > 1:
            return base_url+str(temp_province)+'/'+str(temp_district)+'/pg'+str(page)

    #获取详细学校信息页面url
    def get_school_url(self,school_id):
        base_url='http://school.zhongkao.com/school/'
        return base_url+str(school_id)

    #获取web页面内容content
    def get_web_content(self,url,headers=__headers):
        request = urllib2.Request(url,headers = headers)
        response = urllib2.urlopen(request)
        #获取网页的文本内容content
        return response.read().decode('utf-8')

    #学校列表页面正则
    #获取：学校id，学校名，学校类别
    def list_crawling_pattern(self):
        pattern = re.compile('<dt><a.*?school/(\d+)/" target.*?<h3><a.*?_blank">(.*?)</a>.*?ipt">(.*?)</span>',re.S)
        return pattern

    #学校详情页面正则
    #获取：学校地址
    def school_crawling_pattern(self):
        pattern = re.compile('class="clearfix".*?<tr>.*?<tr>.*?<tr>.*?<tr>.*?<tr>.*?<td>.*?<td>(.*?)</td>',re.S)
        return pattern


    #学校列表页面正则2
    #获取：省份对应区域列表
    def list_pro2dis_pattern(self,temp_url):
        pattern = re.compile('<a.*?'+temp_url+'/(.*?)/">(.*?)</a>',re.S)
        return pattern

    #过滤器
    #筛选出所有省份下，对应区域这部分代码，以便再次筛选
    def districts_filter_pattern(self):
        pattern = re.compile('"filtarea clearfix">.*?<span.*?<span.*?<a.*?</a>.*?(.*?)</p>',re.S)
        return pattern

    def get_re_items(self,url,pattern):
        web_content=self.get_web_content(url)
        return re.findall(pattern,web_content)

    def get_soup_items(self):
        pass



def get_linedata(province,district,school_infos,address):
	#'school_id,province,district,school_name,school_type,address'
	linedata='''%s,"%s","%s","%s","%s","%s"\n''' % (str(school_infos[i][0].encode('gbk')),province,district,str(school_infos[i][2].encode('gbk')),str(school_infos[i][3].encode('gbk')),address)
	#print linedata
	return linedata



def main():

    #----------------------------------
    # 参数初始化
    #----------------------------------
    config=ConfigInfo()                #信息获取实例
    webdownload=WebDownloadInfo()      #爬取相关实例

    file_name=config.get_file_name()   #文件名
    file_titles=config.get_outformat() #表格表头名
    #f=open(file_name,'w')
    #f.write(file_titles)

    dict_provinces=config.get_dict_provinces()             #获取省份子列表字典

    list_pattern=webdownload.list_crawling_pattern()       #学校列表正则规则
    school_pattern=webdownload.school_crawling_pattern()   #学校详情正则规则
    filter_pattern=webdownload.districts_filter_pattern()  #学校列表页面，代码过滤器



    #按照省份，依次筛选爬取
    for prov in dict_provinces:
        list_base_url=webdownload.get_list_url(int(dict_provinces[prov]))       #依据prov，设置list_base_url
        list_districts_pattern=webdownload.list_pro2dis_pattern(list_base_url)  #依据list_base_url，设置正则规则
        filter_contents=webdownload.get_re_items(list_base_url,filter_pattern)  #过滤后只剩下包含<a>的所有区域


        districts_itemts=re.findall(list_districts_pattern,filter_contents[0])  #获取该省下所有区

        print list_base_url,str(prov)
        #print districts_itemts
        #按照区，依次筛选爬取
        for x_index in range(0,len(districts_itemts)):
            temp_district=districts_itemts[x_index][0]       #该省下的区
            temp_url=webdownload.get_list_url(int(dict_provinces[prov]),int(temp_district))
            #temp_soup=BeautifulSoup(webdownload.get_web_content(temp_url))

            temp_totalpage=1  #该区下，总页数（暂未获取）
            #返回列表
            #学校id,学校名,学校类别
            temp_list_items=webdownload.get_re_items(temp_url,list_pattern)


            #
            #写入数据
            #


            #for page in range(1,temp_totalpage):
            #    temp_url=webdownload.get_list_url(int(dict_provinces[prov]),int(temp_district),page+1)

            #print temp_url



    #list_url=webdownload.get_list_url(1000,1006)
    #list_base_url=webdownload.get_list_url(1000)



    #list_items=webdownload.get_re_items(list_url,list_pattern)

    #list_items=re.findall(list_districts_pattern,filter_contents[0])

    #print filter_contents[0]
    #print str(list_items[0][0])
    #print len(list_items)
    #print list_items
    #print list_items[0][2]

    #list_districts=webdownload.get_re_items(list_base_url,list_districts_pattern)

    #print list_districts



    '''
    for x in range(0,len(list_items)):

        school_url=webdownload.get_school_url(int(list_items[x][0]))
        school_items=webdownload.get_re_items(school_url,school_pattern)
        print school_url
        print school_items[0]
        time.sleep(1)


    for s in dict_provinces:
        x=dict_provinces[s]
        strS=u'一般'
        for intS in range(0,10):
            config.set_dict_p_district(x,intS,u'日常')
        #dict_p_district[x]={'value':intS,'name':strS}

        #print x
    dict_p_district=config.get_dict_p_district()
    #print dict_p_district
    '''

    #f.close()

if __name__ == "__main__":
    main()
