import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json
import re
import pickle


courses = pd.DataFrame.from_csv('courses.csv')
courses = courses.reset_index()
courses = courses.set_index(['Code', 'Language'])
course2code = pickle.load(open("course2code.p", "rb"))

course_list = list(set(courses.index.get_level_values(0)))

for index, row in courses.iterrows():
    if not(pd.isnull(row['Prerequis-Ind'])):
        s = ", ".join([c for c in course_list if(c in row['Prerequis-Ind'])])
        if bool(s):
            courses.loc[index, 'Prerequis-Ind'] = s
    if not(pd.isnull(row['Prerequis-Obl'])):
        s = ", ".join([c for c in course_list if(c in row['Prerequis-Obl'])])
        if bool(s):
            courses.loc[index, 'Prerequis-Obl'] = s

course_title = courses['Title'].values

for index, row in courses.iterrows():
    if not(pd.isnull(row['Prerequis-Ind'])):
        s = set([c for c in course_title if(c in row['Prerequis-Ind'])])
        if bool(s):
            s1=[]
            for i in s:
                s1.append(course2code[i])
            courses.loc[index, 'Prerequis-Ind'] = ", ".join(s1)
            
    if not(pd.isnull(row['Prerequis-Obl'])):
        s = set([c for c in course_title if(c in row['Prerequis-Obl'])])
        if bool(s):
            s1=[]
            for i in s:
                s1.append(course2code[i])
            courses.loc[index, 'Prerequis-Obl'] = ", ".join(s1)

# courses.to_csv(path_or_buf="courses_Prerequis.csv") uncomment to recreate file