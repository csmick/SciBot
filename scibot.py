#!/usr/bin/python3

import itertools
from collections import Counter
from database import Database
from heapq import *

class SciBot(object):

    def __init__(self):
        self.data_base_dir = './data/text'
        self.cleaned_data_base_dir = './cleaned_data'
        self.db = Database()
        self.db.clean_data(self.data_base_dir, self.cleaned_data_base_dir)
        self.db.import_data('./data/microsoft', self.cleaned_data_base_dir)

    def stats(self):
        print('Number of unique papers: {}'.format(len(self.db.get_pids())))
        print('Number of unique authors: {}'.format(len(self.db.get_aids())))
        print('Number of venues: {}'.format(len(self.db.conferences)))

        matrix_avg = []
        avg_title_length = []
        for aid, pids in self.db.aid2pids.items():
            num_publications = len(pids)
            if num_publications >= 3:
                matrix_count = 0
                total_title_length = 0
                for pid in pids:
                    # count the number of times matrix appears in the document
                    text = self.db.pid2text[pid][1]
                    matrix_count += text.count('matrix')
                    # calculate the length of the title of the document
                    total_title_length += len(self.db.pid2title_year_conf[pid][0])
                heappush(matrix_avg, (matrix_count/num_publications, aid))
                heappush(avg_title_length, (total_title_length/num_publications, aid))

        authors = []
        for avg, aid in nlargest(3, matrix_avg, key=(lambda x: x[0])):
            authors.append(self.db.aid2authorname[aid])

        print('Names of \"matrix\" experts: {}'.format(', '.join(authors)))
        
        authors = []
        for avg, aid in nlargest(3, avg_title_length, key=(lambda x: x[0])):
            authors.append(self.db.aid2authorname[aid])

        print('Names of \"long-title\" authors: {}'.format(', '.join(authors)))

    def extract_entities_absolute_support(self):
        # count named entities
        entity_counts = Counter()
        keywords = self.db.get_keywords()
        for pid in self.db.get_pids():
            text = self.db.pid2text[pid][1]
            for keyword in keywords:
                entity_counts[keyword] += text.count(keyword)

        # print five most mentioned entities
        for index, (entity, count) in enumerate(sorted(entity_counts.items(), key=(lambda x: x[1]), reverse=True)):
            print(entity, count)
            if index > 4:
                break

    def extract_entities_lexical_features(self):
        # count named entities
        entity_counts = {}
        for paperid in self.db.get_pids():
            path = '{}/{}/{}.txt'.format(self.data_base_dir, self.db.pid2text[paperid][0].split('-', 1)[0], self.db.pid2text[paperid][0])
            with open(path,'rb') as fr:
                for line in fr:
                    line = line.decode('utf-8')
                    arr = line.strip('\r\n').split(' ')
                    n = len(arr)
                    if n < 5: continue
                    for i in range(0,n-2):
                        if arr[i] == '(' and arr[i+2] == ')':
                            abbr = arr[i+1]
                            l = len(abbr)
                            if l > 1 and abbr.isalpha():
                                if i >= l and abbr.isupper():
                                    isvalid = True
                                    for j in range(0,l):
                                        if not abbr[l-1-j].lower() == arr[i-1-j][0].lower():
                                            isvalid = False
                                    if isvalid:
                                        phrase = ''
                                        for j in range(0,l):
                                            phrase = arr[i-1-j]+' '+phrase
                                        phrase = phrase[0:-1].lower()
                                        if not phrase in entity_counts:
                                            entity_counts[phrase] = 0
                                        entity_counts[phrase] += 1
                                if i >= l-1 and abbr[-1] == 's' and arr[i-1][-1] == 's' and abbr[0:-1].isupper():
                                    isvalid = True
                                    for j in range(1,l):
                                        if not abbr[l-1-j].lower() == arr[i-j][0].lower():
                                            isvalid = False
                                    if isvalid:
                                        phrase = ''
                                        for j in range(1,l):
                                            phrase = arr[i-j]+' '+phrase
                                        phrase = phrase[0:-1].lower()
                                        if not phrase in entity_counts:
                                            entity_counts[phrase] = 0
                                        entity_counts[phrase] += 1
                                        
        # print five most mentioned entities
        for index, (entity, count) in enumerate(sorted(entity_counts.items(), key=(lambda x: x[1]), reverse=True)):
            print(entity, count)
            if index > 4:
                break 

    def apriori_fpm(self, data, min_sup):
        '''
        Input Arguments:
            data - list of sets
            min_sup - minimum support for frequent patterns
        '''

        # Generate frequent pattern candidates
        def generate_candidates(d, itemsets, k):
            s = set()
            for pattern in d.keys():
                for itemset in itemsets:
                    if not itemset[0] in pattern:
                        s.add(tuple(sorted(pattern+itemset)))
            return s

        # Generate support for pattern candidates
        def generate_frequent_patterns(candidates, data, min_sup):
            c = Counter()
            # Generate support values
            for itemset in data:
                for candidate in candidates:
                    if set(candidate).issubset(itemset):
                        c[candidate] += 1
            # Prune non-frequent patterns
            c = prune(c, min_sup)
            return c

        # Prune patterns that do not meet the minimum support
        def prune(d, min_sup):
            new_d = {}
            for k, sup in d.items():
                if sup >= min_sup:
                    new_d[k] = sup
            return new_d

        k = 1
        f = Counter()

        # Populate f with 1-itemset candidates
        for itemset in data:
            for item in itemset:
                f[(item,)] += 1
        
        # Find frequent 1-itemsets
        f = generate_frequent_patterns(f, data, min_sup)

        # Create list of frequet 1-itemsets for candidate generation
        freq_one_itemsets = f.keys()

        # Generate and prune candidates
        while True:
            print('Frequent {}-itemsets: {}\n'.format(k, ', '.join(map(lambda x: str(set(x)), sorted(f)))))
            candidates = generate_candidates(f, freq_one_itemsets, k+1)
            f = generate_frequent_patterns(candidates, data, min_sup)
            k += 1
            if not f:
                break

if __name__ == "__main__":
    sb = SciBot()
#    sb.stats()
#    sb.extract_entities_absolute_support()
#    sb.extract_entities_lexical_features()
    
    author_sets = []
    for pid, aids in sb.db.pid2aids.items():
        authors = set()
        for aid in aids:
            authors.add(sb.db.aid2authorname[aid])
        author_sets.append(authors)
    sb.apriori_fpm(author_sets, min_sup=2)
    
