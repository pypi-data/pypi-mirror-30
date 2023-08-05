# -*- coding: utf-8 -*-

#
#    seqann Sequence Annotation
#    Copyright (c) 2017 Be The Match operated by National Marrow Donor Program. All Rights Reserved.
#
#    This library is free software; you can redistribute it and/or modify it
#    under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation; either version 3 of the License, or (at
#    your option) any later version.
#
#    This library is distributed in the hope that it will be useful, but WITHOUT
#    ANY WARRANTY; with out even the implied warranty of MERCHANTABILITY or
#    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
#    License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this library;  if not, write to the Free Software Foundation,
#    Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA.
#
#    > http://www.fsf.org/licensing/licenses/lgpl.html
#    > http://www.opensource.org/licenses/lgpl-license.php
#

# TODO: change file name to seq_annotation.py
#
import re
import sys

from Bio.Seq import Seq
from Bio.Alphabet import IUPAC
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature
from Bio.SeqFeature import ExactPosition
from Bio.SeqFeature import FeatureLocation

from seqann.models.reference_data import ReferenceData
from seqann.blast_cmd import blastn
from seqann.blast_cmd import get_locus
from seqann.seq_search import SeqSearch
from seqann.models.base_model_ import Model
from seqann.align import align_seqs
from seqann.util import randomid
from seqann.util import get_features

isexon = lambda f: True if re.search("exon", f) else False
isutr = lambda f: True if re.search("UTR", f) else False
isfive = lambda f: True if re.search("five", f) else False


def getblocks(coords):
    block = []
    blocks = []
    sorted_i = sorted(coords.keys())
    for i in range(0, len(sorted_i)-1):
        j = i+1
        if i == 0:
            block.append(sorted_i[i])
        if(j <= len(sorted_i)-1):
            if(sorted_i[i] == sorted_i[j]-1):
                block.append(sorted_i[j])
            else:
                blocks.append(block)
                block = []
                block.append(sorted_i[j])
        else:
            block.append(sorted_i[j])
    if len(block) >= 1:
        blocks.append(block)
    if len(sorted_i) == 1:
        return [sorted_i]
    return blocks


def get_features(seqrecord):
    # print("^^^^^^^^^^^^^^^^^^^^^^^^^^")
    # print("get_features")
    # print(seqrecord)
    # print(seqrecord.features)
    # print("^^^^^^^^^^^^^^^^^^^^^^^^^^")
    # TODO: Make sure UTR's have type of UTR
    fiveutr = [["five_prime_UTR", seqrecord.features[i].extract(seqrecord.seq)] for i in range(0, 3) if seqrecord.features[i].type != "source"
               and seqrecord.features[i].type != "CDS" and isinstance(seqrecord.features[i], SeqFeature)
               and not seqrecord.features[i].qualifiers]
    feats = [[str(feat.type + "_" + feat.qualifiers['number'][0]), feat.extract(seqrecord.seq)]
             for feat in seqrecord.features if feat.type != "source"
             and feat.type != "CDS" and isinstance(feat, SeqFeature)
             and 'number' in feat.qualifiers]
    threeutr = [["three_prime_UTR", seqrecord.features[i].extract(seqrecord.seq)] for i in range(len(seqrecord.features)-1, len(seqrecord.features)) if seqrecord.features[i].type != "source"
                and seqrecord.features[i].type != "CDS" and isinstance(seqrecord.features[i], SeqFeature)
                and not seqrecord.features[i].qualifiers]
    feat_list = fiveutr + feats + threeutr
    annotation = {k[0]: str(k[1]) for k in feat_list}
    #print(annotation)
    return(annotation)


def get_seqfeat(seqrecord):
    n = 3 if len(seqrecord.features) >= 3 else len(seqrecord.features)
    fiveutr = [["five_prime_UTR", seqrecord.features[i].location.start, seqrecord.features[i].location.end] for i in range(0, n) if seqrecord.features[i].type != "source"
               and seqrecord.features[i].type != "CDS" and isinstance(seqrecord.features[i], SeqFeature)
               and not seqrecord.features[i].qualifiers]
    feats = [[str(feat.type + "_" + feat.qualifiers['number'][0]), feat.location.start, feat.location.end]
             for feat in seqrecord.features if feat.type != "source"
             and feat.type != "CDS" and isinstance(feat, SeqFeature)
             and 'number' in feat.qualifiers]
    threeutr = [["three_prime_UTR", seqrecord.features[i].location.start, seqrecord.features[i].location.end] for i in range(len(seqrecord.features)-1, len(seqrecord.features)) if seqrecord.features[i].type != "source"
                and seqrecord.features[i].type != "CDS" and isinstance(seqrecord.features[i], SeqFeature)
                and not seqrecord.features[i].qualifiers]
    feat_list = fiveutr + feats + threeutr
    #annotation = {k[0]: k[1] for k in feat_list}
    feat_range = {}
    feat_coordinates = {}
    for feat in feat_list:
        for i in range(feat[1], feat[2]):
            feat_coordinates.update({i: feat[0]})
    for feat in feat_list:
        feat_range.update({feat[0]: [int(feat[1]), int(feat[2])]})
    return(feat_range, feat_coordinates)


server = BioSeqDatabase.open_database(driver="pymysql", user="root",
                                       passwd="my-secret-pw", host="localhost",
                                       db="bioseqdb")
db = server['3310_A']
seqrecord = db.lookup(name="HLA-A*01:01:01:01")
seqrange, seqfeats = get_seqfeat(seqrecord)

# record where gaps are in relation to sequence
from Bio import AlignIO
from collections import namedtuple

alignment = AlignIO.read(open("seqann/data/alignments/3310/A_gen.sth"), "stockholm")
aln_seq = str(alignment[0].seq)
coords = [pos for pos, char in enumerate(aln_seq) if char == '-']
coordinates = dict(map(lambda x: [x, 1],
                   [i for i in coords]))

blocks = getblocks(coordinates)
features = list(seqrange.keys())
seq_list = list(str(seqrecord.seq))
aln_list = list(str(alignment[0].seq))

for i in coords:
    if i in seqfeats:
        feat_name = seqfeats[i]
    else:
        max_i = max(seqfeats.keys())
        feat_name = seqfeats[max_i]
    seq_list.insert(i, '-')
    seqrange[feat_name][1] += 1
    ind = features.index(feat_name) + 1
    for j in range(ind, len(features)):
        feat_n = features[j]
        seqrange[feat_n][0] += 1
        seqrange[feat_n][1] += 1
    seqfeats = {}
    for feat in seqrange:
        for i in range(seqrange[feat][0], seqrange[feat][1]):
            seqfeats.update({i: feat})

aln_annotated = {}
for feat in features:
    aln = ''.join(aln_seq[seqrange[feat][0]:seqrange[feat][1]])
    coords = [pos for pos, char in enumerate(aln) if char == '-']
    coordinates = dict(map(lambda x: [x, 1],
                       [i for i in coords]))
    blocks = getblocks(coordinates)
    aln_annotated.update({feat: {"Seq": aln, "Gaps": blocks}})

seq_features = get_features(seqrecord)


for feat in features:
    seq = list(seq_features[feat])
    gaps = aln_annotated[feat]['Gaps']
    for i in range(0, len(gaps)):
        for j in gaps[i]:
            loc = j
            seq.insert(loc, '-')
    nseq = ''.join(seq)
    if not nseq == aln_annotated[feat]['Seq']:
        if feat == "exon_2":
            print(gaps)
            print("")
        #print(feat, "MATCH")
    #else:
            alns = aln_annotated[feat]['Seq']
            coords = [pos for pos, char in enumerate(alns) if char == '-']
            print(coords)
            print(feat, "MISMATCH")



#######################################################
#######################################################

from seqann.sequence_annotation import BioSeqAnn
from Bio import SeqIO
from BioSQL import BioSeqDatabase
server = BioSeqDatabase.open_database(driver="pymysql", user="root",
                                       passwd="my-secret-pw", host="localhost",
                                       db="bioseqdb")
seqann = BioSeqAnn(server=server, verbose=True)

input_seq = "tests/resources/ambig_seqs.fasta"
seqs = list(SeqIO.parse(input_seq, "fasta"))

annotation = seqann.annotate(seqs[0], "HLA-A")
annotation


# nvme
# 
for feat in annotation.annotation:
    print(feat, annotation.annotation[feat], sep="\t")


ref_feats = get_feats(seqrecord)

annoated_align = {}
for feat in seq_features:
    if len(str(annotation.annotation[feat].seq)) == len(seq_features[feat]):
        seq = list(annotation.annotation[feat].seq)
        gaps = aln_annotated[feat]['Gaps']
        for i in range(0, len(gaps)):
            for j in gaps[i]:
                loc = j
                seq.insert(loc, '-')
        nseq = ''.join(seq)
        annoated_align.update({feat: nseq})
        #if not nseq == aln_annotated[feat]['Seq']:
        #
    else:
        l1 = str(len(str(annotation.annotation[feat].seq)))
        l2 = str(len(seq_features[feat]))
        print("Not equal feats " + feat + " " + l1 + " " + l2)

















