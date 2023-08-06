#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Example on how to use TMVA_Adapter to load the weight file,
and return the mva-response weight from the input tree.

>>> main()
<ROOT.TTree object ("weights") at ...

"""

import ROOT
from PyrootCK.tmvautils import TMVA_Adapter

## List of training variables: (branchname, label)
## corresponds to weight file
PARAMS = [
  ('TMath::Log10(mu_P)'       , 'p(#tau_{1})'    ),
  ('TMath::Log10(mu_PT)'      , 'p_{T}(#tau_{1})'),
  ('TMath::Log10(mu_BPVIP)'   , 'IP(#tau_{1})'   ),
  ('mu_0.50_cc_IT'            , 'Iso(#tau_{1})'  ),
  ('TMath::Log10(pi_P)'       , 'p(#tau_{2})'    ),
  ('TMath::Log10(pi_PT)'      , 'p_{T}(#tau_{2})'),
  ('TMath::Log10(pi_BPVIP)'   , 'IP(#tau_{2})'   ),
  ('pi_0.50_cc_IT'            , 'Iso(#tau_{2})'  ),
  ('DPHI'                     , '#Delta#phi'     ),
  ('APT'                      , 'A_{PT}'         ),
  ('TMath::Log10(DOCACHI2)'   , 'DOCA #chi^{2}'  ),
]

def main():

  ## Create adapter with a knowledge of list of variables.
  adapter = TMVA_Adapter(PARAMS)
  adapter.reader = ROOT.TMVA.Reader()

  ## Load weights xml into the reader
  wdir = 'res/weights'
  adapter.book_reader_dir(wdir)

  ## The adapter is ready to mva-evaluate given input tree.
  fin = ROOT.TFile('res/ditau.root')
  tree = fin.Get('DitauCandTupleWriter/h1_mu')
  weights = adapter.make_weights(tree)
  print weights
  fin.Close()

if __name__ == '__main__':
  main()
