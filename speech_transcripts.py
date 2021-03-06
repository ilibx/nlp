#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2016 Guenter Bartsch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# transcripts.csv i/o
#

# quality: 0=not reviewed, 1=poor, 2=fair, 3=good

from speech_tokenizer import tokenize

class Transcripts(object):

    def __init__(self, lang='de'):

        self.lang = lang
        self.ts   = {}

        with open('data/src/speech/%s/transcripts.csv' % self.lang, 'r') as f:

            while True:

                line = f.readline().rstrip().decode('utf8')

                if not line:
                    break

                parts = line.split(';')
                # print repr(parts)

                if len(parts) != 6:
                    raise Exception("***ERROR in transcripts: %s" % line)
                    
                cfn     = parts[0]
                dirfn   = parts[1]
                audiofn = parts[2]
                prompt  = parts[3]
                ts      = parts[4]
                quality = int(parts[5])
                spk     = cfn.split('-')[0]

                v = { 'cfn'     : cfn,
                      'dirfn'   : dirfn,
                      'audiofn' : audiofn,
                      'prompt'  : prompt,
                      'ts'      : ts,
                      'quality' : quality,
                      'spk'     : spk}

                self.ts[cfn] = v

    def __len__(self):
        return len(self.ts)

    def __getitem__(self, key):
        return self.ts[key]

    def __iter__(self):
        return iter(sorted(self.ts))

    def __setitem__(self, key, v):
        self.ts[key] = v

    def __contains__(self, key):
        return key in self.ts

    def save(self):
        with open('data/src/speech/%s/transcripts.csv' % self.lang, 'w') as f:
            for cfn in sorted(self.ts):
                v = self.ts[cfn]
                f.write((u"%s;%s;%s;%s;%s;%d\n" % (cfn, v['dirfn'], v['audiofn'], v['prompt'], v['ts'], v['quality'])).encode('utf8'))

    def split(self, p_test=5, limit=0, min_quality=2, add_all=False):

        ts_all   = {}
        ts_train = {}
        ts_test  = {}

        cnt = 0

        for cfn in self.ts:

            v = self.ts[cfn]

            cnt += 1

            if limit>0 and cnt>limit:
                break

            if v['quality'] < min_quality:
                if ( v['quality'] != 0 ) or ( not add_all ):
                    continue

            if len(v['ts']) == 0:
                if add_all:
                    v['ts'] = ' '.join(tokenize(v['prompt']))
                else:
                    print "WARNING: %s transcript missing" % cfn
                    continue

            ts_all[cfn]  = v
            if len(ts_test) < (len(ts_all) * p_test / 100):
                ts_test[cfn]  = v
            else:
                ts_train[cfn] = v

        return ts_all, ts_train, ts_test

