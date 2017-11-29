#!/usr/bin/python3

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

        print('Names of \"matrix\" experts: {}'.format(str(authors)))
        
        authors = []
        for avg, aid in nlargest(3, avg_title_length, key=(lambda x: x[0])):
            authors.append(self.db.aid2authorname[aid])

        print('Names of \"long-title\" authors: {}'.format(str(authors)))

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

if __name__ == "__main__":
    sb = SciBot()
#    sb.stats()
#    sb.extract_entities_absolute_support()
    sb.extract_entities_lexical_features()
    
