# -*- coding: utf-8 -*-
import re
import sqlite3
import urllib
import urllib.request
import bs4
from time import sleep
import random
from bs4 import BeautifulSoup
from timevar import savetime

# 爬取网页
def opensearch(parameter):
    #openurl是用于使用指定的搜索parameter进行检索，以get的方式获取pubmed的搜索结果页面，返回成html文件
    baseurl = "https://pubmed.ncbi.nlm.nih.gov/"
    url=baseurl+parameter
    header={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32"}
    request=urllib.request.Request(url,headers=header)
    html=""
    try:
        response=urllib.request.urlopen(request)
        html=response.read()
        return html
    # except urllib.error.URLError as e:
    #     if hasattr(e,"code"):
    #         print(e.code)
    #     if hasattr(e,"reason"):
    #         print(e.reason)
    except:
        print("获取检索页失败，请检查输入的参数\n")

# searchweb= opensearch(parameter).decode("utf-8")#使用Unicode8对二进制网页进行解码

#<span class="value">1,284</span>
#<label class="of-total-pages">of 26</label>

#这部分函数的功能主要是便利整个搜索页，后面可能做一个显示most recently结果的可选sort参数,默认每页50个结果
#解析网页
class ExceptionType:
    pass


def traverse(html):
    try:
        content = BeautifulSoup(html, "html.parser")  # 通过bs4解析网页的内容，查找到页面有关于各个项目的信息
        result_all = int(str(content.find_all("span", class_="value")[0])[20:-7].replace(',','')) # 这句话表示了最后的搜索结果的数量，一共多少条文献
        data = []
        # 这个是把内容拉出来。
        for item in content.find_all("article", class_="article-overview"):
            # print(item)
            # 文章名
            doctitle = item.find_next("h1",class_="heading-title").text.strip()
            #文章时间
            docdate = item.find_next("span",class_="cit").text.strip()
            # 摘要
            try:
                abstract = item.find_next("div",class_="abstract-content selected").text.strip()
            except:
                abstract = 'none'
            # 关键词,有的没有
            keyword0 = item.find_all("div",class_="abstract")
            try:
                keyword =str(keyword0).split("Keywords:")[1].split("</div>")[0].strip()
                keyword = re.sub('<[^<]+?>', '', keyword).strip()
            except:
                keyword = 'none'
            # 作者列表
            try:
                au = item.find("div",class_="authors-list").text.strip()
                authorlist = re.sub("\xa0|\n| ", "",au)
            except:
                authorlist = 'none'
            if authorlist == "none":
                continue
            # 作者地址
            try:
                authoraffli = item.find_next("ul",class_="item-list").text.strip()
            except:
                authoraffli = 'none'
            # 期刊
            journal = item.find_next("div",class_="journal-actions dropdown-block").text.split("\n")[1].strip()
            # doi号
            doi = item.find_next("a",class_="id-link").text.strip()
            # doi 网址
            doilink = item.find_next("a",class_="id-link")["href"]
            # PMID号
            PMID = item.find_next("strong",class_="current-id").text
            # PMCID号,只有免费文章有这个号
            PMCID0 = item.find_all("span",class_="identifier pmc")
            if PMCID0 == []:
                PMCID = 'none'
                freemark = '0'
            else:
                PMCID = PMCID0[0].find_next("a",class_="id-link").text.strip()
                freemark = '1'
            # 免费标签，1是可以下载的，0是不可以下载的

            reviewmark = item.find_next("span",class_="publication-type")
            # 下面是查找review标签，两种，空值或者有，即0或者1
            # print(reviewmark.group())
            if reviewmark == None:
                reviewmark = '0'
            else:
                reviewmark = '1'


            temp = []
            temp.append(doctitle)
            temp.append(docdate)
            temp.append(abstract)
            temp.append(keyword)
            temp.append(authorlist)
            temp.append(authoraffli)
            temp.append(journal)
            temp.append(doi)
            temp.append(doilink)
            temp.append(PMID)
            temp.append(PMCID)
            temp.append(freemark)
            temp.append(reviewmark)
            data.append(temp)
            # print(data)
            print('信息汇总完成\n')
        return data, result_all
    except ExceptionType as e:
        print('Error:', e)
        traceback.print_exc()
        




def createdb(dbpath):#创建一个数据库
    tablename = 'pubmed%s'%savetime
    print(tablename)

    sql='''
    create table %s
    (id  integer primary key autoincrement,
    doctitle text,docdate text,abstract text,keyword text,authorlist text,authoraffli text,journal text,doi text,
    doilink text,PMID numeric,PMCID numeric,freemark numeric,reviewmark numeric,savepath text)'''%tablename
    conn =sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()
    print("创建数据库成功 ID:\n", cursor.lastrowid)

def savedata2(datalist,dbpath):#构建一个保存检索数据的sqlite数据库
    tablename = 'pubmed%s'%savetime
    conn=sqlite3.connect(dbpath)
    cursor=conn.cursor()
    for data in datalist:
        try:
            sql="""
            insert into "{}"(
            doctitle ,docdate ,abstract ,keyword ,authorlist ,authoraffli ,journal ,doi ,doilink ,PMID ,PMCID ,freemark ,reviewmark)
            values("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")""".format(
                tablename,data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8],data[9],data[10],data[11],data[12])
            cursor.execute(sql)
            print("写入数据库成功\n")
        except:
            print("当前项目写入失败\n")
            continue
    conn.commit()
    cursor.close()


def save2xls(xlsfilename,dbpath):
    import xlwt
    import sqlite3
    tablename = 'pubmed%s' % savetime
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    # 执行查询语句，获取所有数据
    cursor.execute('SELECT * FROM  {}'.format(tablename))
    data = cursor.fetchall()
    # 创建一个工作簿对象
    workbook = xlwt.Workbook()
    # 创建一个工作表对象
    worksheet = workbook.add_sheet(tablename)

    # 写入表头
    for i, column in enumerate(cursor.description):
        worksheet.write(0, i, column[0])

    # 写入数据
    for row, row_data in enumerate(data, start=1):
        for col, cell_data in enumerate(row_data):
            worksheet.write(row, col, cell_data)

    # 保存工作簿到文件
    workbook.save(xlsfilename)

    # 关闭游标和连接
    cursor.close()
    conn.close()


def spiderpub(parameter,num1):
    # 这一步是每页显示数的替换
    size = re.search('&size=(\d{1,3})', parameter)
    if size == None:
        parameter += '&size=50'
    parameter = re.sub(r'&size=(\d{1,3})', '&size=50', parameter)
    page_count = 0
    datalist = []

    # 处理页数
    pagemax = 1
    for i in range(1, num1+1):
        #开始遍历每一页结果，一共num页最大pagemax页
        if i > pagemax:
            print("已遍历所有页\n")
            break
        parameter = parameter + "&page=" + str(i)
        try:
            # 搜索网页，返回相应的对象，看明白了。
            html = opensearch(parameter)
            if html==None:
                print("检索页获取出错，即将退出\n")
                break
            # 获取每篇文章的信息，最后输出到excel当中
            data, result_all = traverse(html)
            if data==None:
                print("遍历检索页信息出错，当前检索页为%d(每页50个结果)\n"%i)
            # extend() 方法会将 data 中的每个元素依次添加到 datalist 的末尾，使得 datalist 包含了原先的元素以及 data 中的所有元素。这个操作会修改 datalist 的值，但不会改变 data 的值。
            datalist.extend(data)
            pagemax = (result_all + 49) // 50
            sleep(random.randint(1, 5))
            print("已爬取完第%d页\n" % i)
            # print(datalist)
        except:
            print("spiderpub函数出错，请检查结果\n")
    dbpath = 'pubmedsql'
    # 建立数据库
    createdb(dbpath)
    # 把文章信息存入数据库
    savedata2(datalist, dbpath)
    # 把数据库存入excel
    xlsfilename="./search_res/pubmed%s.xls"%savetime
    save2xls(xlsfilename, dbpath)










