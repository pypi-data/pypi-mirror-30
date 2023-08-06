#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Example of drawing "brazillian" (yellow-green) upper limit plot.

>>> main()

"""

import ROOT
import pandas as pd
from uncertainties import ufloat

def main():
  data = pd.DataFrame({
    45 : [27.0178,  ufloat(  29, 10 ), ufloat(34,20),   21.774],
    55 : [ 20.338,  ufloat(  22, 7  ), ufloat(25,15),  23.7543],
    65 : [17.1956,  ufloat(  18, 7  ), ufloat(22,14),  15.9618],
    75 : [12.9139,  ufloat(  14, 5  ), ufloat(16,10),  15.9601],
    85 : [11.4286,  ufloat(  12, 4  ), ufloat(14,9 ),  19.9864],
    95 : [12.2059,  ufloat(  13, 4  ), ufloat(15,9 ),  15.7593],
    105: [10.1051,  ufloat(10.7, 3.5), ufloat(12,7 ),  9.79102],
    115: [ 8.6772,  ufloat( 9.3, 3.1), ufloat(11,6 ),  7.59801],
    125: [7.02719,  ufloat( 7.5, 2.6), ufloat( 9,5 ),   6.2737],
    135: [5.94634,  ufloat( 6.4, 2.3), ufloat( 8,5 ),  5.63194],
    145: [5.07231,  ufloat( 5.5, 2.1), ufloat( 7,4 ),  4.75521],
    155: [4.70217,  ufloat( 5.1, 2.0), ufloat( 6,4 ),  4.48759],
    165: [4.20999,  ufloat( 4.6, 1.8), ufloat( 6,4 ),  4.20613],
    175: [3.86749,  ufloat( 4.3, 1.7), ufloat( 5,4 ),  3.99316],
    185: [3.79318,  ufloat( 4.2, 1.7), ufloat( 5,4 ),  3.87183],
    195: [3.61905,  ufloat( 4.0, 1.7), ufloat( 5,4 ),   3.5046],
  }, index=['exp', 'exp1', 'exp2', 'obs']).T

  g = ROOT.TMultiGraph.brazillian(data)
  c = ROOT.TCanvas('brazillian', 'brazillian')
  g.Draw('AP')
  c.SaveAs('samples/brazillian.pdf')


if __name__ == '__main__':
  main()