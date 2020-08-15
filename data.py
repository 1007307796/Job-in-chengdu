#coding:utf-8

import requests
from lxml import etree
import pandas as pd
from retrying import retry
import openpyxl
import sqlalchemy as sqla
import pymysql

class LaGou():
    def __init__(self,job,pages):
        self.job = job
        self.file_name = '拉钩_%s.xlsx' % job
        self.pages = pages
        self.page = 1
        self.id = ''
        self.headers = {
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'User-Agent': 'ozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3704.400 QQBrowser/10.4.3587.400'
        }

    def GetCookie(self):
        url = 'https://www.lagou.com/jobs/list_/p-city_252?&cl=false&fromSearch=true&labelWords=&suginput='
        # 注意如果url中有中文，需要把中文字符编码后才可以正常运行
        response = requests.get(url=url,headers=self.headers,allow_redirects=False)
        return response.cookies

    def getdata(self):
        url = 'https://www.lagou.com/jobs/positionAjax.json?&city=%E6%88%90%E9%83%BD&needAddtionalResult=false'
        self.headers['Referer'] = 'https://www.lagou.com/jobs/list_/p-city_252?&cl=false&fromSearch=true&labelWords=&suginput='
        data = {
            'first': 'false',
            'pn': str(self.page),
            'kd': str(self.job),
            'sid': self.id,
        }
        if self.page == 1:
            data['first'] = 'true'
            if 'sid' in data.keys():
                data.pop('sid')
        response = requests.post(url = url,data=data,headers = self.headers,cookies = self.GetCookie())
        # 这里的请求是post且获取的内容是json格式，因此使用json=data的方式才能获取到数据
        response.encoding = response.apparent_encoding  # 根据网页内容分析出的编码方式。
        # print(response.json())
        # exit()
        return response.json()

    data_list = []
    miss_list = []
    def savedata(self):
        data_json = self.getdata()
        table_Lables = ['数据来源', '详情页面', '岗位行业', '公司名称', '公司轮次', '公司人数', '公司行业', '公司地址', '岗位', '学历', '工作年限', '岗位薪资', '发布时间', '工作内容']
        showid = data_json['content']['showId']
        self.id = showid
        for i in data_json['content']['positionResult']['result']:
            position_id = i['positionId']
            positionId = 'https://www.lagou.com/jobs/{}.html'.format(i['positionId'])
            keyContent,addr = self.detail_parse(position_id, showid)
            try:
                self.data_list.append(
                    ['拉勾网', positionId, i['firstType'], i['companyFullName'], i['financeStage'],
                    i['companySize'], i['industryField'], addr, i['positionName'], i['education'], i['workYear'],
                    i['salary'], i['createTime'], keyContent
                    ])
            except:
                self.miss_list.append(positionId)
                continue
        data_write = pd.DataFrame(columns=table_Lables, data=self.data_list)
        if self.job == None:
            self.job = '所有职位'
        return data_write.to_excel(self.file_name, index=False, encoding='utf_8_sig')

    @retry(stop_max_attempt_number=10)
    def detail_parse(self,positionid,showid):
        # 解析详情页数据
        url = 'https://www.lagou.com/jobs/{}.html?show={}'.format(positionid,showid)
        print(url)
        response = requests.get(url,headers = self.headers,cookies = self.GetCookie())
        tree = etree.HTML(response.content)
        job_detail = tree.xpath('//div[@class="job-detail"]//text()')
        job_detail = ''.join(job_detail).strip()
        work_addr = tree.xpath('//div[@class="work_addr"]//text()')
        work_addr = list(map(lambda x :x.replace('-','').strip(),work_addr))
        for i in work_addr:
            if i in ['查看地图','-'] or i == '':
                work_addr.remove(i)
        work_addr = ''.join(work_addr)
        return job_detail,work_addr
    def generate_map_data(self):
        db = sqla.create_engine('mysql+pymysql://root:@localhost:3306/jobs?charset=utf8')
        database_names = ['work_addr', 'job_name','detail_url','data_from','company_name']
        excel_names = ['公司地址','岗位','详情页面','数据来源','公司名称']
        df = pd.read_excel(self.file_name,usecols=excel_names)
        df = df[excel_names]
        df.columns = database_names
        df.to_sql(name='lagou',con=db,index=False,if_exists='append')
    def main(self):
        for i in range(1,self.pages+1):
            print('第%s页正在爬取' % (i))
            self.savedata()
            self.page += 1
        print('*' * 100)
        if self.miss_list == []:
            print('全部数据爬取完毕!')
        else:
            print('数据爬取完毕,以下数据未能正常解析:\n')
            for i in self.miss_list:
                print(i,'\n')
        print('正在写入数据库...\n')
        self.generate_map_data()
        print('已完成')

    def maxPage(self):
        data = self.getdata()
        totalCount = data['content']['positionResult']['totalCount']
        # print(totalCount)
        return totalCount//15+1


if __name__ == '__main__':
    job_input = input('请输入你要查询的职位，不输入则不限职位：').strip()   #strip()去除头尾空格
    getMaxPage = LaGou(job_input,1)
    totalPage = getMaxPage.maxPage()
    page_input = int(input('请输入你要爬取的页数____(成都市该职位共有{}页)：'.format(totalPage)))
    lagou = LaGou(job_input,page_input)
    lagou.main()