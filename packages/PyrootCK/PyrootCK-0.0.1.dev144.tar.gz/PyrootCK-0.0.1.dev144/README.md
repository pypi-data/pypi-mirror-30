PyrootCK
========

PyrootCK module, for better PyROOT than the native one.

It helps me get through my PhD.

## Disclaimer

This packacge was written and used during my PhD in 2013-2017 at EPFL (Lausanne) and LHCb collaboration (CERN),
for the work in *Z->tau tau* cross-section measurement and *H->mu tau* searches at LHCb (8TeV).
I hope it can be of a good use for future analysis...


TODO: no more features from pyrootzen, QHist

- Fast `TTree` import:
```python
  ## Loading trees from multiple Ganga jobs using their job IDs
  tree = import_tree( 'somename', 1234, 1235, 1236, 1239 )
```

- Convert to/from `pandas.DataFrame`:
```python
  ## Convert from `ROOT` objects
  df = th2f.dataframe()
  df = ttree.dataframe()
  df = tntuple.dataframe()
  df = tgraphsymmerrors.dataframe()

  ## Convert to `ROOT` objects from `pandas.DataFrame`:
  obj = ROOT.TH2.from_uframe( df )
  obj = ROOT.TGraphs.from_pair_ufloats( df )
```

- Last but not least, the quick drawer `QHist`:
```python
  h = QHist()
  h.trees   = t1, t2, t3
  h.params  = 'mu_PT'
  h.draw()
```

Dependencies on 3rd-party libraries
-----------------------------------

- `ROOT`: Of source this is mandatory. A build with python (`PyROOT`) is needed.
- `uncertainties`: I use this lightweight-package a lot. So this is required at
  the installation-level.
- `root_numpy`, `pandas`: 



Usage with `pandas`, `uncertainties`, `root_numpy`
--------------------------------------------------

I tend to use `uncertainties`, `pandas` package a lot, 
so I provide several method to convert to/from ROOT's object and 
`DataFrame` in `pandas`. 
These are usually invoked with `obj.dataframe()` instance method.
The nickname `uframe` is for the dataframe-of-ufloat.

Of course, these methods will fail if `pandas`, `root_numpy`, `uncertainties` 
package is not installed. Package `uncertainties` is required at the installation level, whilst `pandas`, `root_numpy` is not.

List of supported classes

- `TTree`
- `TH2`
- `TGraphAsymmErrors`
- `TGraphErrors`

