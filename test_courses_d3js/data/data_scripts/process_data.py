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
#isa_U_max = isa_codes
print("Size of ISA union Max: " + str(len(isa_U_max)))

# Add aggregations (TODO add field that distinguishes if it's a supernode or not)
aggregations = []
for x in isa_U_max:
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
            aggregations.append(aggr)

codes_with_aggr = isa_U_max.union(set(aggregations))
print("Size of codes with aggregations: " + str(len(codes_with_aggr)))


# Max's edges and ISA's couses

edges_to_dump_obl = sum(1 for x in max_egdes_obl if (x[0] not in codes_with_aggr or x[1] not in codes_with_aggr))
edges_to_dump_ind = sum(1 for x in max_egdes_ind if (x[0] not in codes_with_aggr or x[1] not in codes_with_aggr))
total_dump = edges_to_dump_ind + edges_to_dump_obl
total_edges = len(max_egdes_obl) + len(max_egdes_ind)
print("If we use ISA_U_Max courses_ISA and Max's edges, we would have to dump " + str(total_dump) + " out of " + str(total_edges) + " edges")
print('')

# Kshitij's edges and ISA's courses

names = ['plsa', 'lda', 'inf2', 'inf1', 'baseline']

for edges in [baseline, inf1, inf2, lda, plsa]:
    edges_to_dump = sum(1 for x in edges if (x[0] not in codes_with_aggr or x[1] not in codes_with_aggr))
    total_edges = len(edges)
    print("If we use ISA_U_Max and Kshitij's "  + names.pop() + " edges, we would have to dump " + str(edges_to_dump) + " out of " + str(total_edges) + " edges.")
