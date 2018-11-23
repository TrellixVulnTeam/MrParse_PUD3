'''
Created on 16 Nov 2018

@author: jmht
'''

from mrparse.mr_sequence import CC_SYMBOL, TM_SYMBOL, HELIX_SYMBOL, BSHEET_SYMBOL

import colorsys

def get_N_HexCol(N=5):
    HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in xrange(N)]
    hex_out = []
    for rgb in HSV_tuples:
        rgb = map(lambda x: int(x*255),colorsys.hsv_to_rgb(*rgb))
        hex_out.append("".join(map(lambda x: chr(x).encode('hex'), rgb)))
    return ['#' + h for h in hex_out]

    
def pfam_region_dict(regions, seqlen):
    assert len(regions)
    region_colors = get_N_HexCol(len(regions))
    region_data = []
    for idx_region, region in enumerate(regions):
        for idx_range, rrange in enumerate(region.ranges):
            start, stop = map(int, rrange.split('-'))
            name = region.matches[idx_range]
            d = { 'startStyle': "curved",
                  'endStyle': "curved",
                  'start': start,
                  'end': stop,
                  'aliStart': start,
                  'aliEnd': stop,
                  'colour': region_colors[idx_region],
#                       'text': str(region.ID)}
                  'text': name,
                  'metadata' : { "description" : "Domain #%s" % region.ID,
                                 "database" : "PHMMER search",
                                 "start" : start,
                                 "end" : stop,
                                  }
                  }            
            jdict = {'length' : seqlen,
                     'regions' : [d]}
            region_data.append(jdict)
    return region_data

def pfam_classification_dict(chunk_data, seqlen):
    regions = []
    for i, chunk in enumerate(chunk_data):
        idx = i + 1
        if chunk.stype == CC_SYMBOL:
            colour = "#00ff00"
            text = 'CC'
            meta_desc = "Coiled-coil region #%d" % idx
        elif chunk.stype == TM_SYMBOL:
            colour = "#aaaaaa"
            text = 'TM'
            meta_desc = "Transmembrane region #%d" % idx
        elif chunk.stype ==  HELIX_SYMBOL:
            colour = "#ff0000"
            text = 'helix'
            meta_desc = "Helix region #%d" % idx
        elif chunk.stype == BSHEET_SYMBOL:
            print("GOT BSNEET")
            colour = "#0000ff"
            text = 'bsheet'
            meta_desc = "Beta sheet region #%d" % idx
        d = { 'startStyle': "straight",
              'endStyle': "straight",
              'start': chunk.start,
              'end': chunk.end,
              'aliStart': chunk.start,
              'aliEnd': chunk.end,
              'colour': colour,
              'text': text,
              'metadata' : { "description" : meta_desc,
                             "database" : chunk.source,
                             "start" : chunk.start,
                             "end" : chunk.end,
                              }
              }
        regions.append(d)       
    vis_data = {'length' : seqlen,
                'regions' :regions}
    return vis_data

def pfam_data(self):
    assert self.classification and self.sspred
    classification_chunks = get_sequence_chunks(self.classification, markers=[CC_SYMBOL, TM_SYMBOL], source='Deepcoil')
    sspred_chunks = get_sequence_chunks(self.sspred, markers=[HELIX_SYMBOL, BSHEET_SYMBOL], source='Jpred')
    classification_dict = mr_pfam.pfam_classification_dict(classification_chunks, self.seqlen)
    sspred_dict = mr_pfam.pfam_classification_dict(sspred_chunks, self.seqlen)
    return {'classification' : classification_dict,
            'ss_pred' : sspred_dict} 


