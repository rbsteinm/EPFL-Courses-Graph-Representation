#!/usr/bin/env python
import csv
import re
from difflib import SequenceMatcher as SM

# paths and imports
# ------------------------------------------------------------------------------------------

max_codes = []
isa_codes = []
max_egdes_obl = []
max_egdes_ind = []

path_max = '../Max/course_neo.csv'
path_max_edges_ind = '../Max/pre_ind.csv'
path_max_edges_obl = '../Max/pre_obl.csv'
path_isa = '../ISA/courses_ISA.csv'

# kshitij's edges
path_edges_baseline = '../Kshitij/edge_list_baseline.csv'
path_edges_inf1 = '../Kshitij/edge_list_inf1.csv'
path_edges_inf2 = '../Kshitij/edge_list_inf2.csv'
path_edges_lda = '../Kshitij/edge_list_inf1_lda.csv'
path_edges_plsa = '../Kshitij/edge_list_inf1_plsa.csv'

baseline = []
inf1 = []
inf2 = []
lda = []
plsa = []

dict_isa = {}
dict_max = {}

with open(path_max, 'rU') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        max_codes.append(row[1])
        dict_max[row[1]] = row[2]

with open(path_isa, 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        isa_codes.append(row[0])
        dict_isa[row[0]] = row[1]

with open(path_max_edges_obl, 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        max_egdes_obl.append([row[1], row[2]])

with open(path_edges_baseline, 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        baseline.append([row[0], row[2]])

with open(path_edges_inf1, 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        inf1.append([row[0], row[2]])

with open(path_edges_inf2, 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        inf2.append([row[0], row[2]])

with open(path_edges_lda, 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        lda.append([row[0], row[2]])

with open(path_edges_plsa, 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        try:
            plsa.append([row[0], row[2]])
        except IndexError:
            continue

# ------------------------------------------------------------------------------------------


'''
process to follow:
- take courses from ISA
- remove ill formated courses from Max
- add all courses from Max that are not existing in ISA (with descriptions)
- add aggregations
- maybe add a new field is_super and has_super
- check the proportion of edges that are matched
'''

max_codes = set(max_codes)
print("Size of Max before ill-removal: " + str(len(max_codes)))
max_codes = set([x for x in max_codes if len(x) <= 15])
print("Size of Max after ill-removal: " + str(len(max_codes)))

isa_codes = set(isa_codes)
print("Size of isa: " + str(len(isa_codes)))

isa_U_max = max_codes.union(isa_codes)
print("Size of ISA union Max: " + str(len(isa_U_max)))
