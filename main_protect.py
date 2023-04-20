# -*- coding: utf-8 -*-
import os
# os.chdir("")
os.getcwd()
import sys
# sys.path.append("")
from spiderpub import spiderpub
from downpmc import downpmc
from geteachinfo import geteachinfo
import os
from time import sleep
print('--'*25,'\n')
print("程序已运行，开始检查数据储存目录\n\n")
print('--'*25)
sleep(1.5)
if os.path.exists('./document'):
    if os.path.exists('./document/pub'):
        print("文件储存目录检查正常，可以储存文件\n")
    else:
        os.makedirs('./document/pub')
        print("成功在当前目录下建立/document/pub文件夹\n")
else:
    os.makedirs('./document/pub')
    print("成功在当前目录下建立/document/pub文件夹\n")
print('--'*25,'\n')
print("document/pub目录检查完成，开始执行主程序\n")
print('--'*25,'\n')

if os.path.exists('./search_res'):
    print("文件储存目录检查正常，可以储存文件\n")
else:
    os.makedirs('./document')
    print("成功在当前目录下建立/search_res文件夹\n")

def main():
    # parameter = str(input("请在下面粘贴你构建的搜索结果的parameter\n"))
    parameter = url0
    sleep(1)
    if parameter == '':
        print("输入有误\n")
    # num1 = int(input("即将爬取所有文献的信息，请输入你想爬取信息的页数(每页50个）\n"))
    num1 = pagenums
    sleep(1)
    if type(num1) != int:
        print("输入有误\n")
    # limit = int(input("请输入爬取信息后你需要下载的文献数量\n"))
    limit = papernumber
    sleep(1)
    #这一步主要是解析网页生成每条文章对应的数据
    spiderpub(parameter, num1)
    # geteachinfo()
    downpmc(limit)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, default="?term=circRNA&format=abstract&sort=date&size=50",
                        help="PubMed search parameter")
    parser.add_argument("--pagenums", type=int, default=1, help="Number of pages to crawl")
    parser.add_argument("--papernumber", type=int, default=30000000, help="Number of papers to download")
    args = parser.parse_args()

    url0 = args.url
    pagenums = args.pagenums
    papernumber = args.papernumber

    main()

    # 删除数据库
    import os
    if os.path.exists("pubmedsql"):
        os.remove("pubmedsql")
        print("数据库文件删除成功")
    else:
        print("数据库文件不存在")














#?term=cell%2Bblood&filter=datesearch.y_1&size=20