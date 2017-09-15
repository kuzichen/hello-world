#!/usr/bin/python
#coding:utf-8

import urllib,urllib2,requests
from bs4 import BeautifulSoup
import datetime,time
import random
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
        u'上海':1160,u'天津':1180,u'广东':1019,u'湖南':3206,u'江西':3467,u'贵州':3578,
        u'云南':3676,u'西藏':3822,u'海南':3903,u'宁夏':4013,u'青海':4040,u'新疆':4092,u'香港':4188,
        u'澳门':4207,u'福建':3111,u'浙江':3009,u'辽宁':1240,u'江苏':1355,u'湖北':1475,
        u'四川':1587,u'台湾':4216
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

    #获取学校列表页面url地址
    def get_list_url(sefl,temp_province=0,temp_district=None,page=1):
        base_url='http://school.zhongkao.com/province/'
        if page == 1:
            if temp_district:
                return base_url+str(temp_province)+'/'+str(temp_district)
            else:
                return base_url+str(temp_province)
        elif page > 1:
            return base_url+str(temp_province)+'/'+str(temp_district)+'/p'+str(page)

    #获取详细学校信息页面url
    def get_school_url(self,school_id):
        base_url='http://school.zhongkao.com/school/'
        return base_url+str(school_id)

    #获取web页面内容content
    def get_web_content(self,url,headers=__headers):
        MAX_NUM=6
        request = urllib2.Request(url,headers = headers)

        for i in range(0,MAX_NUM):
            try:
                response = urllib2.urlopen(request, timeout=10)
                break
            except Exception, e:
                if i<MAX_NUM-1:
                    continue
                else:
                    print 'URLError: <urlopen error time out> All times is failed '

        #获取网页的文本内容content
        return response.read().decode('utf-8')

    #学校列表页面正则
    #获取：学校id，学校名，学校类别
    def list_crawling_pattern(self):
        pattern = re.compile('<dt><a.*?school/(\d+)/" target.*?<h3><a.*?_blank">(.*?)</a>.*?<tr.*?<td.*?>(.*?)</td>',re.S)
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



def get_linedata(province,district,school_infos,i,address):
    #'school_id,province,district,school_name,school_type,address'
    linedata='''%s,"%s","%s","%s","%s","%s"\n''' % (str(school_infos[i][0].encode('gbk','ignore')),str(province.encode('gbk','ignore')),str(district.encode('gbk','ignore')),str(school_infos[i][1].encode('gbk','ignore')),str(school_infos[i][2].encode('gbk','ignore')),str(address.encode('gbk','ignore')))
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
    f=open(file_name,'w')
    f.write(file_titles)

    dict_provinces=config.get_dict_provinces()             #获取省份子列表字典

    list_pattern=webdownload.list_crawling_pattern()       #学校列表正则规则
    school_pattern=webdownload.school_crawling_pattern()   #学校详情正则规则
    filter_pattern=webdownload.districts_filter_pattern()  #学校列表页面，代码过滤器



    #按照省份，依次筛选爬取
    for prov in dict_provinces:
        list_base_url=webdownload.get_list_url(int(dict_provinces[prov]))       #依据prov，设置list_base_url
        list_districts_pattern=webdownload.list_pro2dis_pattern(list_base_url)  #依据list_base_url，设置正则规则
        filter_contents=webdownload.get_re_items(list_base_url,filter_pattern)  #过滤后只剩下包含<a>的所有区域


        districts_itemts=re.findall(list_districts_pattern,filter_contents[0])  #获取该省下所有区(0:id,1:name)

        print list_base_url,str(prov)
        print 'district number is ',len(districts_itemts)


        #按照区，依次筛选爬取
        for dis_index in range(0,len(districts_itemts)):
        #for dis_index in range(0,1):
            print 'district: ',districts_itemts[dis_index][1]
            temp_district=districts_itemts[dis_index][0]       #该省下的区id
            #print dis_index,temp_district
            temp_url=webdownload.get_list_url(int(dict_provinces[prov]),int(temp_district))
            temp_soup=BeautifulSoup(webdownload.get_web_content(temp_url),'lxml')

            try:
                #过滤查找翻页区域内容
                temp_ul=temp_soup.find('nav',{"class":"page_Box tc"})
                #倒数第二个<a>对应的为总页数
                temp_total_page = int(re.findall(re.compile('<a.*?">(.*?)</a>', re.S),str(temp_ul.find_all('a')[-2]))[0])
            except Exception, e:
                temp_total_page=0


            #print temp_ul
            print 'total_page:',temp_total_page

            #总页数大于0时，才继续下一步
            if temp_total_page:

                #temp_totalpage=1  #该区下，总页数（暂未获取）
                #返回列表
                #学校id,学校名,学校类别
                temp_list_items=webdownload.get_re_items(temp_url,list_pattern)
                #print len(temp_list_items),temp_list_items[0][2]

                #_________________________________________________________

                temp_school_address='-'
                for list_index in range(0,len(temp_list_items)):
                    print 'item: ',list_index

                    #school_url=webdownload.get_school_url(int(temp_list_items[list_index][0]))
                    #temp_school_address=webdownload.get_re_items(school_url,school_pattern)[0]
                    temp_linedata=get_linedata(prov,districts_itemts[dis_index][1],temp_list_items,list_index,temp_school_address)
                    f.write(temp_linedata)
                sleeptime=random.randint(2,4)
                time.sleep(sleeptime)
                print 'sleeptime:',sleeptime
                #(province,district,school_infos,address):
                if temp_total_page>1:
                    for page_index in range(2,temp_total_page+1):
                        temp_url=webdownload.get_list_url(int(dict_provinces[prov]),int(temp_district),page_index)
                        print temp_url

                        temp_list_items=webdownload.get_re_items(temp_url,list_pattern)

                        for list_index in range(0,len(temp_list_items)):
                            #school_url=webdownload.get_school_url(int(temp_list_items[list_index][0]))
                            #temp_school_address=webdownload.get_re_items(school_url,school_pattern)[0]
                            temp_linedata=get_linedata(prov,districts_itemts[dis_index][1],temp_list_items,list_index,temp_school_address)
                            f.write(temp_linedata)


                        sleeptime=random.randint(2,4)
                        time.sleep(sleeptime)
                        print 'sleeptime:',sleeptime

                print 'finish dis_index:',dis_index



    f.close()

if __name__ == "__main__":
    main()
