#!/usr/bin/python3

import collections
import os

class Database(object):

    def __init__(self):
        self.pid2text = collections.defaultdict(lambda: ('', ''))
        self.pid2title_year_conf = collections.defaultdict(lambda: ('', '', '', ''))
        self.pid2keyword = collections.defaultdict(str)
        self.pid2authorseq = collections.defaultdict(lambda: ('', '', '', ''))
        self.aid2authorname = collections.defaultdict(str)

    def import_data(self, data_root, text_root):
        self.data_root = os.path.abspath(data_root)
        self.text_root = os.path.abspath(text_root)
        
        for line in open(os.path.join(self.data_root, 'index.txt')):
            line = line.split('\t')
            with open(os.path.join(self.text_root, line[0], line[1] + '.txt')) as f:
                self.pid2text[line[2]] = (line[1], f.read().replace('\n', ' '))

        for line in open(os.path.join(self.data_root, 'Papers.txt')):
            line = line.split('\t')
            self.pid2title_year_conf[line[0]] = (line[1], line[3], line[7])

        for line in open(os.path.join(self.data_root, 'PaperKeywords.txt')):
            line = line.split('\t')
            self.pid2keyword[line[0]] = line[1]

        for line in open(os.path.join(self.data_root, 'PaperAuthorAffiliations.txt')):
            line = line.split('\t')
            self.pid2authorseq[line[0]] = (line[1], line[2], line[4], line[5])

        for line in open(os.path.join(self.data_root, 'Authors.txt')):
            line = line.split('\t')
            self.aid2authorname[line[0]] = line[1]

    def get_pids(self):
        return list(self.pid2keyword.keys())

    def get_aids(self):
        return list(self.aid2authorname.keys())

if __name__ == '__main__':
    db = Database()
    db.import_data('./data/microsoft', './data/text')

    print('Number of unique papers: {}'.format(len(db.get_pids())))
    print('Number of unique authors: {}'.format(len(db.get_aids())))
