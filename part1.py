#!/usr/bin/python3

from database import Database
from heapq import *
from operator import itemgetter

if __name__ == '__main__':
    db = Database()
    db.import_data('./data/microsoft', './data/text')

    print('Number of unique papers: {}'.format(len(db.get_pids())))
    print('Number of unique authors: {}'.format(len(db.get_aids())))

    matrix_avg = []
    avg_title_length = []
    for aid, pids in db.aid2pids.items():
        num_publications = len(pids)
        if num_publications >= 3:
            matrix_count = 0
            total_title_length = 0
            for pid in pids:
                # count the number of times matrix appears in the document
                text = db.pid2text[pid][1]
                matrix_count += text.count('matrix')
                # calculate the length of the title of the document
                total_title_length += len(db.pid2title_year_conf[pid][0])
            heappush(matrix_avg, (matrix_count/num_publications, aid))
            heappush(avg_title_length, (total_title_length/num_publications, aid))

    authors = []
    for avg, aid in nlargest(3, matrix_avg, key=itemgetter(0)):
        authors.append(db.aid2authorname[aid])

    print('Names of \"matrix\" experts: {}'.format(str(authors)))
    
    authors = []
    for avg, aid in nlargest(3, avg_title_length, key=itemgetter(0)):
        authors.append(db.aid2authorname[aid])

    print('Names of \"long-title\" authors: {}'.format(str(authors)))
