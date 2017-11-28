#!/usr/bin/python3

from database import Database
from heapq import *

class SciBot(object):

    def __init__(self):
        self.db = Database()
        self.db.clean_data('./data/text', './cleaned_data')
        self.db.import_data('./data/microsoft', './cleaned_data')

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

if __name__ == "__main__":
    sb = SciBot()
    sb.stats()
    
