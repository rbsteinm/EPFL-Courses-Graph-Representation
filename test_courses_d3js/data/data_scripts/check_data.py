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


# add aggregate courses to ISA
isa_codes_aggr_only = []
for x in isa_codes:
    if '(' in x:
        if x[0] is '(' and x[-1] is ')':
            x = x[1:-1]

        aggr = ''
        for char in x:
            if char is not '(':
                aggr = aggr + char
            else:
                break
        if aggr != '':
            isa_codes_aggr_only.append(aggr)

        #print('before: ' + x + ' after: ' + aggr)
isa_codes_aggr_only = set(isa_codes_aggr_only)
isa_codes_no_aggr = isa_codes
isa_codes = isa_codes_aggr_only.union(isa_codes)


# Max's courses and ISA's courses

max_codes = set(max_codes)
isa_codes = set(isa_codes)
print('Max has ' + str(len(max_codes)) + ' courses')
print('ISA has ' + str(len(isa_codes)) + ' courses')

inter = max_codes.intersection(isa_codes)
print('ISA and Max have ' + str(len(inter)) + ' courses in common')
print('Max has ' + str(len(max_codes.difference(isa_codes))) + ' that ISA has not')
print('ISA has ' + str(len(isa_codes.difference(max_codes))) + ' courses that Max has not')

ill_form_max = sum(1 for x in max_codes if len(x) > 10)
print('Max has ' + str(ill_form_max) + ' courses that seem ill-formated (len(code) > 10)')


# Max's edges and ISA's couses

edges_to_dump_obl = sum(1 for x in max_egdes_obl if (x[0] not in isa_codes or x[1] not in isa_codes))
edges_to_dump_ind = sum(1 for x in max_egdes_ind if (x[0] not in isa_codes or x[1] not in isa_codes))
total_dump = edges_to_dump_ind + edges_to_dump_obl
total_edges = len(max_egdes_obl) + len(max_egdes_ind)
print("If we use ISA courses and Max's edges, we would have to dump " + str(total_dump) + " out of " + str(total_edges) + " edges")
print('')

# Kshitij's edges and ISA's courses

names = ['plsa', 'lda', 'inf2', 'inf1', 'baseline']

for edges in [baseline, inf1, inf2, lda, plsa]:
    edges_to_dump = sum(1 for x in edges if (x[0] not in isa_codes or x[1] not in isa_codes))
    total_edges = len(edges)
    print("If we use ISA courses and Kshitij's "  + names.pop() + " edges, we would have to dump " + str(edges_to_dump) + " out of " + str(total_edges) + " edges.")

courses_k = set()
for x in plsa:
    courses_k.add(x[0])
    courses_k.add(x[1])
print('')

k_not_isa = courses_k.difference(isa_codes)
print('There are ' + str(len(k_not_isa)) + ' courses in khsitij but not in ISA: ')


max_and_isa = max_codes.union(isa_codes)

k_not_isa = courses_k.difference(max_and_isa)
print('There are ' + str(len(k_not_isa)) + ' courses in khsitij but not in Max U ISA: ')

# it seems that it could be fine if we merge Max and ISA courses
# let's check if the course that have same code also have same name between Max and ISA
not_same = 0
for code in max_codes.intersection(isa_codes).difference(isa_codes_aggr_only):
    #if(dict_max[code] != dict_isa[code]):
    if SM(None, dict_max[code], dict_isa[code]).ratio() < 0.5:
        not_same += 1
        #print(dict_max[code])
        #print(dict_isa[code])
print(not_same)
# when we count exact matching, it seems that there is a lot of differences, but in fact it's mostly small name changes or
# translations in french that cause them. It seems to be fine

'''
process to follow:
- take courses from ISA
- remove ill formated courses from Max
- add all courses from Max that are not existing in ISA (with descriptions)
- add aggregations
- maybe add a new field is_super and has_super
- check the proportion of edges that are matched



