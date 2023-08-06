"""

Collections of misc functions for PyROOT framework related to Inputs/Outputs


Importing Tree & Ganga
----------------------

At the beginning of analysis session, sometime you just wanna get
a TTree/TNtuple, asap. Here is my way:

```python
tree = import_tree('dirname/Tuplename', './somepath/to/file.root')
```

There's a reason why the tuple's name is asked first, then the location to
TFile: Multiple files can be concatenate together via mechanism of TChain.
My motivation is that sometime I run over large dataset, so I split them into
several jobs and cumulatively process them. Only the tree that matches given
name will be collected:

```python
tree = import_tree('tname', 'file1.root', 'file2.root', 'file3.root' )
```

Using either relative path or absolute path for the input files is fine.
To aid this, you can optionally provide an environmental variable `TFILEPATH`
which add additional search paths for `import_tree`, just like how normal
`PATH` works for the executables, for example:

```bash
export TFILEPATH='$GANGADIR/workspace/$USER/LocalXML'
```
```python
# for $GANGADIR/workspace/$USER/LocalXML/1234/output/tuple.root
tree = import_tree('tname', '1234/output/tuple.root', '1235/output/tuple.root')
```

Remark that the relative path `.` is implied and always has the highest priority
dy default; you don't need to supply it again.

Because I also used Ganga a lot, which is one useful way to organize large
number of ROOT files instead of letting them floating around, the above
syntax is reduced to just integers:

```python
# for $GANGADIR/workspace/$USER/LocalXML/1234/output/tuple.root
tree = import_tree('tname', 1234, 1235)
```

where `1234`, `1235` are the ganga's job ID.
See doc of `import_tree` for more detail of the implicit search path.

"""

import os
import sys
import ROOT
import __main__
import subprocess
from glob import glob

from . import logger
from PythonCK.decorators import memorized
from PythonCK.itertools import flatten

__all__ = (
  'exit',
  'tfile_seeker',
  'import_file',
  'import_tree',
)

#==============================================================================

def exit(): # pragma: no cover
  """
  Custom exit method more suitable for semi-interactive script.
  Just put this at the point where you want the interactive script to pause.

  Features

  - Update GUI (gPad)
  - Wait, via raw_input()
  - Eventually sys.exit(), or keep going.

  """
  if ROOT.gPad:
    ROOT.gPad.Update()
  val = raw_input('\nPress [ENTER] to exit. Press [x] to keep going:\n')
  if val != 'x':
    sys.exit()

#==============================================================================

def contains(fpath, treename):
  """
  Return True if the target `TFile` contain requested treename.

  Unlike seek below which raise immediately if file does not exists,
  this only return boolean value since ther are case when I load list of files
  and interested only some trees inside.

  Note: no need to cache with `memorized`, not that helpful.

  >>> contains('res/ditau.root', 'DitauCandTupleWriter/h1_mu')
  True
  >>> contains('res/ditau.root', 'non_existent_name/h1mu')
  False
  >>> contains('non_existent_file', 'non_existent_name')
  False

  """

  ## Handle xrootd protocol
  # Note: I don't know how to mock this for pytest.
  if fpath.startswith('root://'):
    fin = ROOT.TFile.Open(fpath)
  else:
    ## Early exit
    if not os.path.exists(fpath):
      return False
    fin = ROOT.TFile(fpath)  # Guard local instance

  ## FindKey is fast, but not recursive
  dr = fin
  if len(treename.split('/')) > 1:
    for token in treename.split('/')[:-1]:
      dr = dr.GetDirectory(token)
      if not dr:
        dr = None
        break
  val = bool(dr and dr.FindKey(treename.split('/')[-1]))
  fin.Close()
  return val

#-------------------------------------------------------------------------------

def tfilepaths():
  """
  Helper method to yield list of searchpath influenced by TFILEPATH.
  Do nothing on the check of existence of files yet.

  Note: Local path ('.') is implicitly search first

  >>> getfixture('export_TFILEPATH')
  >>> tfilepaths()
  ['.', '/panfs/USER', '/home/USER/gangadir/workspace/USER/LocalXML']

  """
  paths   = ['.']  # default
  paths2  = os.environ.get('TFILEPATH', None) # Set by user
  if paths2:
    paths += paths2.split(':')
  return [os.path.expandvars(s) for s in paths]

#-------------------------------------------------------------------------------

@memorized
def assisted_seek_local(basepath, hint):
  """
  Given single base searchpath and a hint,
  return the first positive result(s).

  Multiple results can be returned (of unique filenames).
  The particular case is that, sometime there are hist.root file here and
  tuple.root file there. A priori, this function does not make a distinction
  about content yet, only seek matching files. So better return both.

  Existence is guaranteed by glob. The search queue is the following:

  - basepath/hint.root
  - basepath/*hint*.root
  - basepath/script_name/hint.root
  - basepath/script_name/*hint*.root
  - basepath/hint/*.root
  - basepath/hint/output/*.root
  - basepath/hint/*/*.root
  - basepath/hint/*/output/*.root

  Args:
    basepath (str): path to base directory to search.
    hint (str): text to hint the search.

  Usage:: 
  
    >>> tmpdir = getfixture('chtmpdir')

    ## Local one
    >>> tmpdir.join('test.root').write('hello')
    >>> assisted_seek_local('.', 'test')
    ['./test.root']

    ## Ganga-style 
    >>> tmpdir.mkdir('hint').mkdir('42').mkdir('output').join('tuple.root').write('hello')
    >>> assisted_seek_local('.', 'hint')
    ['./hint/42/output/tuple.root']
  
    ## Bad one    
    >>> assisted_seek_local('.', 'non_existent_file')
    []

  """
  ## let me handle .root suffix, don't double search ".root"
  if hint.endswith('.root'):
    hint = hint.replace('.root', '')

  ## include current script's dir into hint list too
  scrname = os.path.splitext(os.path.basename(__main__.__file__))[0]

  ## Prepare search queue
  globpaths = [
    os.path.join( basepath, hint+'.root' ),
    os.path.join( basepath, '*'+hint+'*.root' ),
    os.path.join( basepath, scrname, hint+'.root' ),
    os.path.join( basepath, scrname, '*'+hint+'*.root' ),
    os.path.join( basepath, hint, '*.root' ),
    os.path.join( basepath, hint, 'output', '*.root' ),
    os.path.join( basepath, hint, '*', '*.root' ),
    os.path.join( basepath, hint, '*', 'output', '*.root' ),
  ]
  for gpath in globpaths:
    logger.debug(gpath)
    res = glob(gpath)
    logger.debug(res)
    if res:
      return sorted(res)
  ## Return empty search otherwise.
  return []

#-------------------------------------------------------------------------------

@memorized
def assisted_seek_eos(hint):
  r"""
  Given the hint, return list of paths to relevant root files found on EOS.
  Assumed valid token, so that this method doesn't have to repeat
  the validation.

  Required: $EOS_HOME, $EOS_MGM_URL, `eos` binary.

  List of progressive search queue:

  - $EOS_HOME/<hint>.root
  - $EOS_HOME/<hint>/*.root
  - $EOS_HOME/ganga/<hint>/*.root

  ## Monkeypatching
  >>> mp = getfixture('monkeypatch')
  >>> mp.setenv('EOS_HOME', '/eos/lhcb/user/t/test')
  >>> mp.setenv('EOS_MGM_URL', 'root://eoslhcb.cern.ch')
  >>> mp.setattr('subprocess.Popen.communicate', lambda _: ('/eos/lhcb/user/t/test/ganga/154/\n/eos/lhcb/user/t/test/ganga/154/tuple.root',''))
  
  >>> assisted_seek_eos('154.root')
  ['root://eoslhcb.cern.ch//eos/lhcb/user/t/test/ganga/154/tuple.root']

  """
  ## let me handle .root suffix, don't double search ".root"
  if hint.endswith('.root'):
    hint = hint.replace('.root', '')

  ## Prepare search queue. Note that glob is not working here
  basepath = os.path.expandvars('$EOS_HOME')
  searchpaths = [
    os.path.join( basepath, hint+'.root' ), # a file
    os.path.join( basepath, hint ),         # a directory
    os.path.join( basepath, 'ganga', hint ),
  ]

  ## Loop progressively, return if some root files found
  url = os.environ['EOS_MGM_URL']
  for path in searchpaths:
    args = 'eos', 'find', path
    logger.debug(str(args))
    try:
      p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      stdout, stderr = p.communicate()
      if stdout and not stderr:
        files = sorted(stdout.strip().split('\n'))
      else:
        logger.debug(stderr)
        continue
    except Exception, e: # in case of invalid token
      logger.debug(e)
      continue
    res = [url+'/'+x for x in files if x.endswith('.root')]
    if res:
      return res
  ## finally, if fail in all paths, return empty result.
  return []

#-------------------------------------------------------------------------------

def tfile_seeker(*args):
  """
  Return list of paths to file requested in args, with assisted search.

  Search strategy:

  - If args is empty, grep locally.
  - Else, loop through each arg in args:
    - If it's some kind of absolute path, use it.
    - Else, consult $TFILEPATH variable, one path at a time:
      - At this point, it can be either string or int
      - TFILEPATH implicitly has '.' as first path, and EOS as last
        path, if the condition is correct.
      - Either way, search in this given path, over all assisted
        subpath. The search string is used in both subdir and filename.
      - Return single result found.

  Provide existence check where necessary.

  Usage::

    ## Default to local
    >>> tfile_seeker()
    []

    ## Relative path
    >>> tfile_seeker('res/ditau.root')
    ['./res/ditau.root']

    ## Absolute path
    >>> res = tfile_seeker(os.path.join(os.getcwd(), 'res/ditau.root'))
    >>> res[0].replace(os.getcwd(), '$CWD') # just to be platform-independent.
    '$CWD/res/ditau.root'
  
    ## xrootd is absolute
    >>> tfile_seeker('root://lhcb.cern.ch/tuple.root')
    ['root://lhcb.cern.ch/tuple.root']

    ## Globbing
    >>> tfile_seeker('res')
    ['./res/ditau.root', './res/tuple1.root', './res/upperlim.root']

    >>> tfile_seeker('/absolute/non-existent/file.root')
    Traceback (most recent call last):
    ...
    IOError: Requested file not existed: '/absolute/non-existent/file.root'

    >>> tfile_seeker('./relative/non-existent/file.root')
    Traceback (most recent call last):
    ...
    IOError: Cannot find any file matching the hint: './relative/non-existent/file.root'

  """
  ## Grep locally only
  if not args:
    return glob('*.root')

  ## flatten the args
  args = flatten(args)

  ## Cache whether EOS should be used or not.
  # don't put inside TFILEPATH but explicitly here so that I can
  # perform existence check, differently from TFILEPATH.
  use_eos = ('EOS_HOME' in os.environ) and ('EOS_MGM_URL' in os.environ)
  logger.debug('Use EOS?: %s'%use_eos)

  ## thorough search
  results = []
  for src in args:
    src = os.path.expandvars(str(src))
    ## If it's absolute path, don't seek.
    if os.path.isabs(src):
      if not os.path.exists(src):
        raise IOError('Requested file not existed: %r'%src)
      results.append(src)

    ## ROOT-accessURL is also treated as absolute. Skip existence check.
    elif src.startswith('root://'):
      results.append(src)

    else:
      hint  = src
      found = False
      ## Start using TFILEPATH
      for searchpath in tfilepaths():
        paths = assisted_seek_local(searchpath, hint)
        if paths:
          found = True
          results.extend(paths)
          break # use only one searchpath

      ## Use EOS as last resort.
      if not found and use_eos:
        paths = assisted_seek_eos(hint)
        if paths:
          found = True
          results.extend(paths)

      ## If it's still failed after search in ALL path,
      # better warn the user.
      if not found:
        raise IOError('Cannot find any file matching the hint: %r'%hint)

  ## Finally
  return results

#-------------------------------------------------------------------------------

def import_file(src):
  """
  Wrapper around the tfile_seeker, return the single instance of TFile found.
  Raise if many files found.

  >>> import_file('res/ditau')
  <ROOT.TFile object ("./res/ditau.root") at ...>

  >>> import_file('res')
  Traceback (most recent call last):
  ...
  ValueError: Found multiple files: ...

  """
  res = tfile_seeker(src)
  if len(res)==0:
    raise ValueError('Cannot find: %s'%src)
  elif len(res)==1:
    return ROOT.TFile(res[0])
  else:
    raise ValueError('Found multiple files: %s'%res)

#-------------------------------------------------------------------------------

def import_tree( treename, *srcs ):
  """

  Helper method to simplify loading a tree from TFile.

  ### Simple usage

  In its simplest usage, put treename (inside file) and path to file as argument.

  >>> import_tree('CheckRefit2/h1mu', 'res/tuple1.root')
  <ROOT.TChain object ("CheckRefit2/h1mu") at ...>

  ### Auto-chain

  By feeding more filename arguments to `srcs`, they will be chained together
  (via TChain::Add). Of course, each file needs identical structure for desired
  tree to be loaded too.

  >> import_tree('CheckRefit2/h1mu', 'res/tuple1.root', 'res/tuple2.root')
  <ROOT.TChain object ("CheckRefit2/h1mu") at ...>

  >>> import_tree( 'CheckRefit2/h1mu', glob('res/tuple*.root'))
  <ROOT.TChain object ("CheckRefit2/h1mu") at ...>

  ### Search path `TFILEPATH`

  A priori, the filename is searched in current directory. If the environmental
  variable `TFILEPATH` is defined, then the filename will be searched in those
  paths too. The search is stop if some file is found, so path order matters,
  (just like normal bash `PATH` ).

  The default seachpath is '.:$HOME/gangadir/workspace/$USER/LocalXML', i.e.,
  local path, and CERN's Ganga workspace directory.

  ### Implicit Ganga-Style search.

  If filename given in `srcs` is an integer (<jid>), then this will trigger
  Ganga-style search with following search sequence for each path until positive
  result is obtained.

  1. Search directly
      ./<jid>.root

  2. Search in directory of that jid, on all root files that contain valid
     tree of requested name.

      ./<jid>/*.root

  3. Search in `output` subdirectory

      ./<jid>/output/*.root

  4. Search in further subdirectory (or arbitary name) like above, and repeat
     with `output` subdirectory. The recursion stops here.

      ./<jid>/*/*.root
      ./<jid>/*/output/*.root

  Args:
    treename: Specify the treename to be called from TFile::Get
    srcs    : Can be string represents absolute path, or int for Ganga's job id.

  """

  ## Prepare inputs
  srcs = sorted(flatten(srcs))

  ## Start searching, dig deep inside the file.
  chain = ROOT.TChain(treename)
  chain.ownership = False # caveat: This raise SegFault for TChain + EOS url
  for fpath in tfile_seeker(*srcs):
    if contains(fpath, treename):
      chain.Add(fpath)

  ## Validate result
  ntrees = chain.GetNtrees()  # don't use the shorthand version, unexpectedly buggy
  if not ntrees:  # None was add
    logger.warning('No tree (%s) retrieved. Please recheck the sources.'%treename)
    logger.warning('%r'%srcs) # Don't raise exception, keep going!
  else:
    logger.debug("Load TChain[%d] completed: %s " % (ntrees, treename))
    ## Prepare title (extra text for JID-based source)
    chain.title = '%s (%s)'%(treename,srcs)

  ## Finally, return
  # logger.warning('before atexit')
  # atexit.register(chain.Reset) # attempt to workaround EOS segfault. I don't understand it yet...
  return chain

#===============================================================================
