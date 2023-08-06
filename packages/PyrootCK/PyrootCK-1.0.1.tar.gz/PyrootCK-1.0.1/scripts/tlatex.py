#!/usr/bin/env python

"""

Simple script to check the ROOT's custom LaTeX parser.
Write the string as argument, then it'll draw the respective result

Usage:
    >> ./latex.py '#eta'
"""

from ROOT import TCanvas, TLatex
import sys

def main():
  c = TCanvas()
  t = TLatex()
  t.SetTextFont(132)
  t.SetTextSize(0.1)
  t.DrawLatex( .2, .5, sys.argv[1])
  c.Update()
  raw_input()

if __name__ == '__main__':
  main()
