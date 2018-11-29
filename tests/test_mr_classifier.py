'''
Created on 17 Nov 2018

@author: jmht
'''
import set_mrparse_path
import conftest

from mrparse.mr_classify import get_annotation

def test_generate_local():
    seqin = '/opt/MrParse/data/Q13586.fasta'
    topcons_dir = "/opt/MrParse/data/Q13586/topcons"
    classification = get_annotation(seqin, topcons_dir=topcons_dir)
    s = '--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------MMMMMMMMMMMMMMMMMMMMM-------------CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC---------------C-CC--------CC-CC-----------------------------------------CCCCCCCCCCCCCCC----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'
    assert classification.annotation == s, classification.annotation