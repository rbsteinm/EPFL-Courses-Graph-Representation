import pandas as pd
import csv
import numpy as np


course_list = pd.read_csv("course_list.csv")
course_with_desc = pd.read_csv("courses.csv")
course_with_desc.set_index(["Code", "Language"], inplace=True)


course_code = set(course_list["Code"].values)
df = pd.DataFrame(list(course_code))
df.columns = ["code"]
df.set_index(["code"], inplace=True)

df['title'] = [str(course_with_desc.loc[course, 'en']['Title']).replace('\n', ' ').replace('"', '') 
                if course_with_desc.loc[course]['Title'].count() == 2 
                else str(course_with_desc.loc[course]['Title']).replace('\n', ' ').replace('"', '') 
                for course in df.index.values]

df['resume'] = [str(course_with_desc.loc[course, 'en']['Resume']).replace('\n', ' ').replace('"', '') 
                if course_with_desc.loc[course]['Resume'].count() == 2 
                else str(course_with_desc.loc[course]['Resume']).replace('\n', ' ').replace('"', '') 
                for course in df.index.values]

df['content'] = [str(course_with_desc.loc[course, 'en']['Contenu']).replace('\n', ' ').replace('"', '') 
                if course_with_desc.loc[course]['Contenu'].count() == 2 
                else str(course_with_desc.loc[course]['Contenu']).replace('\n', ' ').replace('"', '') 
                for course in df.index.values]

df['keyword'] = [str(course_with_desc.loc[course, 'en']['Mot-clef']).replace('\n', ' ').replace('"', '') 
                if course_with_desc.loc[course]['Mot-clef'].count() == 2 
                else str(course_with_desc.loc[course]['Mot-clef']).replace('\n', ' ').replace('"', '') 
                for course in df.index.values]
df.reset_index(inplace=True)

df.to_csv("course_neo.csv")