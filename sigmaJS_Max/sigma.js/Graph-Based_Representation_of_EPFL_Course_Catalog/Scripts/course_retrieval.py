import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json
import pickle

def get_course(url):
    r = requests.get(url)
    courseCode = r.json()
    return courseCode

courses_ETE = get_course('https://isa.epfl.ch/services/courses/2016-2017/ETE')
courses_HIVER = get_course('https://isa.epfl.ch/services/courses/2016-2017/HIVER')

course_codes = []
code2course = {}
course2code = {}

for course in courses_ETE:
    if course['course']['courseCode'] != 'Unspecified Code':
        course_codes.append(course['course']['courseCode'])
        code2course[course['course']['courseCode']] = course['course']['subject']['name']
        for c in course['course']['subject']['name'].keys():
            course2code[course['course']['subject']['name'][c]] = course['course']['courseCode']
        
for course in courses_HIVER:
    if course['course']['courseCode'] != 'Unspecified Code':
        course_codes.append(course['course']['courseCode'])
        code2course[course['course']['courseCode']] = course['course']['subject']['name']
        for c in course['course']['subject']['name'].keys():
            course2code[course['course']['subject']['name'][c]] = course['course']['courseCode']
        
# pickle.dump(course2code, open("course2code.p", "wb"))


coursedf = pd.DataFrame(columns=('Code', 'Title' 'Contenu', 'Resume', 'Mot-clef', 'Prerequis-Obl', 'Prerequis-Ind', 'Language'))
for courseCode in course_codes:
    print(courseCode)
    course = get_course('https://isa.epfl.ch/services/books/2016-2017/course/' + courseCode)
    if course != []:
        for content in course[0]['paragraphs']:
            if content['type']['code'] == 'RUBRIQUE_CONTENU':
                soupCont = BeautifulSoup(content['content'], 'html.parser')
                lang = content['lang']
                if len(code2course[courseCode]) == 1:
                    title = list(code2course[courseCode].values())[0]
                else:
                    title = code2course[courseCode][lang]
                df = pd.DataFrame([[courseCode, title, soupCont.get_text(), lang]]
                                  ,columns=['Code', 'Title', 'Contenu', 'Language'])
                coursedf = pd.concat([coursedf,df])
            elif content['type']['code'] == 'RUBRIQUE_MOTS-CLES':
                soupMC = BeautifulSoup(content['content'], 'html.parser')
                lang = content['lang']
                if len(code2course[courseCode]) == 1:
                    title = list(code2course[courseCode].values())[0]
                else:
                    title = code2course[courseCode][lang]
                df = pd.DataFrame([[courseCode, title, soupMC.get_text(), lang]]
                                  ,columns=['Code', 'Title', 'Mot-clef', 'Language'])
                coursedf = pd.concat([coursedf,df])
            elif content['type']['code'] == 'RUBRIQUE_RESUME':
                soupRes = BeautifulSoup(content['content'], 'html.parser')
                lang = content['lang']
                if len(code2course[courseCode]) == 1:
                    title = list(code2course[courseCode].values())[0]
                else:
                    title = code2course[courseCode][lang]
                df = pd.DataFrame([[courseCode, title, soupRes.get_text(), lang]]
                                  ,columns=['Code', 'Title', 'Resume', 'Language'])
                coursedf = pd.concat([coursedf,df])
            elif content['type']['code'] == 'RUBRIQUE_COURS_PREREQUIS_OBL':
                soupPO = BeautifulSoup(content['content'], 'html.parser')
                lang = content['lang']
                if len(code2course[courseCode]) == 1:
                    title = list(code2course[courseCode].values())[0]
                else:
                    title = code2course[courseCode][lang]
                df = pd.DataFrame([[courseCode, title, soupPO.get_text(), lang]]
                                  ,columns=['Code', 'Title', 'Prerequis-Obl', 'Language'])
                coursedf = pd.concat([coursedf,df])
            elif content['type']['code'] == 'RUBRIQUE_COURS_PREREQUIS_IND':
                soupPI = BeautifulSoup(content['content'], 'html.parser')
                lang = content['lang']
                if len(code2course[courseCode]) == 1:
                    title = list(code2course[courseCode].values())[0]
                else:
                    title = code2course[courseCode][lang]
                df = pd.DataFrame([[courseCode, title, soupPI.get_text(), lang]]
                                  ,columns=['Code', 'Title', 'Prerequis-Ind', 'Language'])
                coursedf = pd.concat([coursedf,df])
        
coursedf = coursedf.groupby(['Code', 'Title', 'Language']).aggregate('first')

# coursedf.to_csv(path_or_buf="courses.csv") uncomment to recreate file