#!/usr/bin/python3

import collections
import re
import os

class Database(object):

    def __init__(self):
        self.pids = set()
        self.aids = set()
        self.pid2text = collections.defaultdict(lambda: ('', ''))                   # maps PID to (PDFID, text)
        self.pid2title_year_conf = collections.defaultdict(lambda: ('', '', ''))    # maps PID to (TITLE, YEAR, CONF)
        self.pid2keyword = collections.defaultdict(str)                             # maps PID to KEYWORD
        self.pid2authorseq = collections.defaultdict(lambda: ('', '', '', ''))      # maps PID to (AID, FID, AFF, SID)
        self.aid2authorname = collections.defaultdict(str)                          # maps AID to AUT
        self.aid2pids = collections.defaultdict(list)                               # maps AID to list of PIDS

    def import_data(self, data_root, text_root):
        self.data_root = os.path.abspath(data_root)
        self.text_root = os.path.abspath(text_root)
        conferences = set(['icdm', 'kdd', 'wsdm', 'www']) 
        
        reference_pattern = re.compile('^\[')
        for data_line in open(os.path.join(self.data_root, 'index.txt')):
            data_line = data_line.split('\t')
            self.pids.add(data_line[2])
            with open(os.path.join(self.text_root, data_line[0], data_line[1] + '.txt'), 'r') as f:
                text = ''
                for text_line in f:
                    if not reference_pattern.search(text_line):
                        text += text_line.replace('/n', ' ')
                self.pid2text[data_line[2]] = (data_line[1], text)

        for line in open(os.path.join(self.data_root, 'Papers.txt'), 'r'):
            line = line.split('\t')
            if line[0] in self.pids and line[7] in conferences:
                self.pid2title_year_conf[line[0]] = (line[1], line[3], line[7])
                self.pids.add(line[0])
        
        for line in open(os.path.join(self.data_root, 'PaperKeywords.txt'), 'r'):
            line = line.split('\t')
            if line[0] in self.pids:
                self.pid2keyword[line[0]] = line[1]

        for line in open(os.path.join(self.data_root, 'PaperAuthorAffiliations.txt'), 'r'):
            line = line.split('\t')
            if line[0] in self.pids:
                self.pid2authorseq[line[0]] = (line[1], line[2], line[4], line[5])
                self.aid2pids[line[1]].append(line[0])
                self.aids.add(line[1])

        for line in open(os.path.join(self.data_root, 'Authors.txt'), 'r'):
            line = line.split('\t')
            if line[0] in self.aids:
                self.aid2authorname[line[0]] = line[1].rstrip('\n')

    def get_pids(self):
        return list(self.pids)

    def get_aids(self):
        return list(self.aids)

