import sqlite3
import xlwt

import pickle
def save_variable(v, filename):
    f = open(filename, 'wb')
    pickle.dump(v, f)
    f.close()
    return filename


def load_variavle(filename):
    f = open(filename, 'rb')
    r = pickle.load(f)
    f.close()
    return r



dbpath = "pubmedsql"

conn = sqlite3.connect(dbpath)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
cursor.fetchall()

cursor.execute("SELECT * FROM pubmed20230418145958")
cursor.fetchall()
conn.commit()
cursor.close()


sys.path.append("/Users/hanxiangming/Library/CloudStorage/Dropbox/documents/Code/my_functions.py")
from my_functions import *



traverse(html)

save_variable(html, "html")
html = load_variavle("html")





import re
import pandas as pd

# 读取文件并将数据整理成列表
with open('J_Medline.txt', 'r') as f:
    data = f.read()

records = re.split('-{50,}\n', data.strip())
records = [r.strip().split('\n') for r in records]

# 将数据转换为DataFrame
columns = ['JrId', 'JournalTitle', 'MedAbbr', 'ISSN (Print)', 'ISSN (Online)', 'IsoAbbr', 'NlmId']
df = pd.DataFrame(records, columns=columns)

# 删除空格
df = df.apply(lambda x: x.str.strip())
df = df.apply(lambda x: x.str.replace(r'^.*?:\s*', '').str.strip())
df = df.iloc[1:]
print(df)

# 保存为csv文件
df.to_csv('J_Medline.csv', index=False)




