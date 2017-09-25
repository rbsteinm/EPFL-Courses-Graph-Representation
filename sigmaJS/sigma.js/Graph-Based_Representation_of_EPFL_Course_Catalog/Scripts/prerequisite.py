import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json
import re
import pickle
import string
import csv

pre = pd.read_excel('courses_with_pre.xls')
course_code = set(pre["Code"].values)
pre.set_index('Code', inplace=True)
pre = pre[['Prerequis-Ind', 'Prerequis-Obl']]
pre.fillna('', inplace=True)
pre = pre.groupby(level=0).agg({'Prerequis-Ind':lambda x: ', '.join(x).strip(','), 'Prerequis-Obl':lambda x: ', '.join(x).strip(',')})

source_ind = []
target_ind = []
for i, s in pre.iterrows():
    print(s['Prerequis-Ind'])
    for p in s['Prerequis-Ind'].split():
        p = p.strip(',')
        if p and p in course_code:
            print(p)
            source_ind.append(i)
            target_ind.append(p)
pre_ind = pd.DataFrame({'Source': source_ind, 'Target': target_ind})
pre_ind.to_csv(path_or_buf="pre_ind.csv")

source_obl = []
target_obl = []
for i, s in pre.iterrows():
    for p in s['Prerequis-Obl'].split():
        p = p.strip()
        if p and p in course_code:
            print(p)
            source_obl.append(i)
            target_obl.append(p)
pre_obl = pd.DataFrame({'Source': source_obl, 'Target': target_obl})
pre_obl.to_csv(path_or_buf="pre_obl.csv")

