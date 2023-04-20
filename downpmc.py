# -*- coding: utf-8 -*-
from socket import socket, timeout
import urllib
from urllib import request
import urllib.error
from geteachinfo import readdata1
import sqlite3
import random
import time
import re
import eventlet
import xlwt
from timevar import savetime
from scihub import SciHub
sh = SciHub()


#https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9034016/pdf/main.pdf
# 下载pdf的函数
def downpdf(parameter):
    eventlet.monkey_patch() # 避免了因 I/O 阻塞导致的程序停顿和性能瓶颈。
    downpara="pmc/articles/"+parameter+"/pdf/main.pdf"
    #openurl是用于使用指定的搜索parameter进行检索，以get的方式获取pubmed的搜索结果页面，返回成html文件
    baseurl = "https://www.ncbi.nlm.nih.gov/"
    url=baseurl+downpara
    timeout_flag=0
    header={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32"}
    request=urllib.request.Request(url,headers=header)
    html=""
    # try:
    #     response=urllib.request.urlopen(request,timeout=30)
    #     html=response.read()
    #     print("%s.pdf"%parameter,"从目标站获取pdf数据成功")
    #     return html
    try:
        with eventlet.Timeout(180,True):
            response = urllib.request.urlopen(request, timeout=60)
            html = response.read()
            print("%s.pdf" % parameter, "从目标站获取pdf数据成功")
            return html
    except urllib.error.URLError as e:
        if hasattr(e, "code"):  # 判断e这个对象里面是否包含code这个属性
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
        timeout_flag=1
        return timeout_flag
    except eventlet.timeout.Timeout:
        timeout_flag=1
        print("下载目标数据超时")
        return timeout_flag
    except:
        print("%s.pdf"%parameter,"从目标站获取pdf数据失败")

def savepdf(html,PMCID,name,dbpath):
    tablename = 'pubmed%s'%savetime
    # pdf = html.decode("utf-8")  # 使用Unicode8对二进制网页进行解码，直接写入文件就不需要解码了

    try:
        name=re.sub(r'[< > / \\ | : " * ?]',' ',name)
        #需要注意的是文件命名中不能含有以上特殊符号，只能去除掉
        savepath="../document/pub/%s.pdf"%name
        file=open(savepath,'wb')
        print("open success")
        file.write(html)
        file.close()
        # print("%s.pdf"%name,"文件写入到Pubmed/document/pub/下成功")
        print("pdf文件写入成功,文件ID为 %s"%PMCID,"保存路径为Pubmed/document/pub/")
        try:
            conn=sqlite3.connect(dbpath)
            cursor=conn.cursor()
            cursor.execute(" UPDATE %s SET savepath = ? WHERE PMCID =?"%tablename,
                           (savepath,PMCID))
            conn.commit()
            cursor.close()
            return 'success'
            print("pdf文件写入成功,文件ID为 %s"%PMCID,"地址写入到数据库pubmedsql下的table%s中成功"%tablename)
        except:
            print("pdf文件保存路径写入到数据库失败")
    except:
        print("pdf文件写入失败,文件ID为 %s"%PMCID,"文件写入失败,检查路径")

def save2excel(dbpath):
    savepath='./search_res/pudmeddownloaded-%s.xls'%savetime
    tablename = 'pubmed%s' % savetime
    try:
        try:
            conn = sqlite3.connect(dbpath)
            cursor = conn.cursor()
            sql = '''SELECT * FROM %s ''' % tablename
            cursor.execute(sql)
            savedata = cursor.fetchall()
            # print(savedata)
            conn.commit()
            cursor.close()
            print("读取最终数据库信息成功")
        except:
            print("读取数据库生成excel时失败，请检查数据库")
        workbook = xlwt.Workbook(encoding="utf-8", style_compression=0)
        worksheet = workbook.add_sheet("pumedsoso", cell_overwrite_ok=True)
        col = (
        '序号', '文献标题', '年份日期','摘要','关键词', '作者',  '作者单位','期刊', 'doi', 'doilink','PMID', 'PMCID', '是否有免费全文', '是否是review', '保存路径')
        for i in range(len(col)):
            worksheet.write(0, i, col[i])
        for i in range(len(savedata)):
            print("保存第%d条到excel" % (i + 1))
            savedata[i] = list(savedata[i])
            # print(savedata[i])
            for j in range(len(savedata[i])):
                savedata[i][j] = str(savedata[i][j])
                if j == 12:
                    savedata[i][j] = savedata[i][j].replace('1', '是').replace('0', '否').replace('0', '否')
                if j == 13:
                    savedata[i][j] = savedata[i][j].replace('1', '是').replace('0', '否')
                worksheet.write(i + 1, j, savedata[i][j])
        workbook.save(savepath)
        print("\n爬取数据库信息保存到excel成功\n")
    except:
         print("\n爬取数据库信息保存到excel失败\n")



# 属于重复的，在geteachinfo里面就有了，现在是使用这个
def readdata1(dbpath,free): #读取数据库，返回想查询的文献的PMID
    tablename = 'pubmed%s'%savetime
    print(tablename)
    try:
        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()
        try:

            if free==1:
                #选择 tablename 表中的两列数据：PMCID 和 doctitle。仅选择 freemark 列的值为 1 的行。返回查询结果。
                # 值得注意的是，由于在 SQL 查询语句中嵌入了 Python 变量，因此需要格外小心避免 SQL 注入攻击。最好的方法是使用参数化查询，而不是将变量插入 SQL 查询字符串中。
                sql = "SELECT PMCID,doctitle FROM %s WHERE freemark = 1"%tablename
                # 根据设置的freemark参数，查找数据库文献的信息,free=1用于查找所有免费文献用来下载，而free=2用于拿数据所有文献去获得详细信息
                print(sql)
                # cursor 可能是一个数据库连接对象的游标
                cursor.execute(sql)
                print("sql执行成功\n")
                result =cursor.fetchall()
                # print(result)
                print('读取sql信息成功 数据类型为PMCID和doctitle\n')
                return result
            # 这里选择的是没有免费全文的文献
            elif free==0:
                sql = "SELECT doilink,doctitle FROM %s WHERE freemark = 0"%tablename#查找数据库文献的信息
                print(sql)
                cursor.execute(sql)
                result = cursor.fetchall()
                # for i in range(len(result)):
                #     result[i] = result[i][0]
                # print(result)
                print('读取sql信息成功，数据类型为doilink和doctitle\n')
                return result

        except:
            print("目标数据库读取失败\n")
        finally:
            conn.commit()
            cursor.close()
    except:
        print("连接数据库失败，请检查目标数据库\n")


# ----------------------

def savepdfscihub(doilink,name,dbpath):
    tablename = 'pubmed%s'%savetime
    # pdf = html.decode("utf-8")  # 使用Unicode8对二进制网页进行解码，直接写入文件就不需要解码了

    try:
        name=re.sub(r'[< > / \\ | : " * ?]',' ',name)
        #需要注意的是文件命名中不能含有以上特殊符号，只能去除掉
        savepath="./document/pub/%s.pdf"%name
        resinfo = sh.download(doilink, path=savepath)
        if resinfo ==None:
            # print("%s.pdf"%name,"文件写入到Pubmed/document/pub/下成功")
            print("pdf文件写入成功,文件名为 %s"%name,"保存路径为Pubmed/document/pub/")
            try:
                conn=sqlite3.connect(dbpath)
                cursor=conn.cursor()
                cursor.execute(" UPDATE %s SET savepath = ? WHERE doilink =?"%tablename,
                               (savepath,doilink))
                conn.commit()
                cursor.close()
                return 'success'
                print("pdf文件写入成功,文件ID为 %s"%name,"地址写入到数据库pubmedsql下的table%s中成功"%tablename)
            except:
                print("pdf文件保存路径写入到数据库失败")
    except:
        print("pdf文件写入失败,文件ID为 %s"%name,"文件写入失败,检查路径")


# ---------------------

# 下载的主函数，这个函数调用其他函数
def downpmc(limit):
    tablename = 'pubmed%s'%savetime
    # 设置下载文献的数量
    count=0
    dbpath = 'pubmedsql'
    # pubmed id和文章标题
    result = readdata1(dbpath, 1)
    resultscihub = readdata1(dbpath, 0)
    for item in result:
        count+=1

        if count > limit:
            print("已达到需要下载的上限，下载停止\n")
            break
        print("开始下载第%d篇"%count)
        #result是从数据库获取的列表元组，其中的每一项构成为PMCID,doctitle
        html=downpdf(item[0])
        if html==None:
            print("网页pdf数据不存在，自动跳过该文献 PMCID为 %s"%item[0])
            continue
        elif html==1:
            print("30s超时,自动跳过该文献 PMCID为 %s"%item[0])
            continue
        status=savepdf(html,item[0],item[1],dbpath)
        if status==None:
            print("保存pdf文件发生错误，自动跳过该文献PMCID为 %s"%item[0])
            continue
        time.sleep(random.randint(0,1))

    for item in resultscihub:
        count+=1
        if count > limit:
            print("已达到需要下载的上限，下载停止\n")
            break
        print("开始下载第%d篇"%count)
        #resultscihub是从数据库获取的列表元组，其中的每一项构成为doilink,doctitle
        status = savepdfscihub(item[0], item[1], dbpath)
        if status == None:
            print("保存pdf文件发生错误，自动跳过该文献name为 %s" % item[1])
            continue
        time.sleep(random.randint(0, 1))


    save2excel('./pubmedsql')
    print("爬取最终结果信息已经自动保存到excel表格中，文件名为%s"%tablename)
    print("爬取的所有文献已经保存到/document/pub/目录下")
    print("生成jcr影响因子文件")
    addjcr(savetime)
    print("爬取程序已经执行完成，自动退出，no errors no warning")


    # for i in range(len(result)):
    #
    #     time.sleep(random.randint(1,5))



# 添加影响因子的函数
def addjcr(savetime):
    # 读取本目录下的2022_JCR_IF_ming.xlsx文件
    import pandas as pd
    # 读取影响因子
    df0 = pd.read_excel('2022_JCR_IF_ming.xlsx')
    # 读取search_res文件夹下的，结果文件
    savepath='./search_res/pudmeddownloaded-%s.xls'%savetime
    savepath1='./search_res/pudmed_downloaded_jcr-%s.xlsx'%savetime
    df1  = pd.read_excel(savepath)
    #读取期全名缩写对照
    df2 = pd.read_csv('J_Medline.csv')
    # 合并结果和全名缩写对照
    df3 = pd.merge(df1,df2,left_on="期刊",right_on="MedAbbr",how='left')
    # 合并df3和影响因子
    # 转换为小写
    df0['Journal Name'] = df0['Journal Name'].str.lower()
    df3['JournalTitle'] = df3['JournalTitle'].str.lower()
    df4 = pd.merge(df3,df0,left_on="JournalTitle",right_on="Journal Name",how='left')
    # 保存为excel文件
    df4.to_excel(savepath1,index=False)
    print("已经将结果文件和影响因子合并，保存为%s"%savepath1)

