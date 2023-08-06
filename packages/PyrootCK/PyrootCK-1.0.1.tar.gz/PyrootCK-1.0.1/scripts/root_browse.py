#!/usr/bin/env python

"""

Helper script to facilitate browsing tuples with ganga/eos regime.
Recommended to wired into shell's alias. It supercedes the vanilla exe.

## Add into the profile
alias root0='$ROOTSYS/bin/root -l'  # Vanilla version
alias root='$LPHE_OFFLINE/mylib/PyrootCK/scripts/root_browse.py'

"""

import os
import sys
from subprocess import call

def browse(queue=[]):
  """
  Execute the TBrowser macro, passing the list of files into inputs
  """
  args = [ os.path.expandvars('$ROOTSYS/bin/root'), '-l' ]
  if queue: # attach TBrowser on demand
    browser = os.path.expandvars('$ROOTSYS/share/root/macros/fileopen.C')
    ## fallback to old location
    if not os.path.exists(browser):
      browser = os.path.expandvars('$ROOTSYS/macros/fileopen.C')
    args += queue + [ browser ]
  call(args)
  sys.exit()

if __name__ == '__main__':
  from PyrootCK.ioutils import tfile_seeker
  browse(tfile_seeker(*sys.argv[1:]))
