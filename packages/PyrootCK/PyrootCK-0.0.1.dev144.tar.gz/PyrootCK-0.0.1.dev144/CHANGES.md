> Q: In case of 2-pages pdf image, what's the behavior in latex addfig?
  - If okay, this means the debug canvas can freely go to the second page.




> 170223: Import hook, for RooFit patch
  - http://xion.org.pl/2012/05/06/hacking-python-imports/
  - Not so straight-forward, RooFit is more like a "pseudo-module".

- 170101: Patch `postprocessors.fraction_roofit` to detect more failing fit. 

- 161109: TTree.sliced_header now support list,dict renaming, jsut like DF.

- 161108: Gaud for nasty bug in TTree.sliced which required TTree::SetEstimate 
  to be called first in case the draw results in more than 1E6 entries.

> 161025: Provide gROOT['h'] for gROOT.FindObject('h')

- 160907: New experimental context object ROOT.TFile.open_metadata to allow 
  writing of metadata into TFile. The object should be simple (i.e, str, dict)

> 160907: Use TRatioPlot

> 160821: move up the pull histo to be right next to xaxis

> 160803: fix roofit patcher to use lazy deco.
  > I'll need a testcase for this first.


> 160316 Use TMathTex instead of TLatex?


> 160120: Support save PDF to subdirectory, without conflicting with autoname 
  (autoname replace backslash with '_over_')

> 160120: Same patch for RooAbsArg, base abstractclass of RooFit.
  The getter/setter at lower case, unfortunately, so seperate patch is needed.

> 160113: Support for 'appending' +h plot

> 160110: Hardcode some fitting info of fraction_fit on canvas

### 151229 Bug in TProfile ylog
- If there's TProfile plot with ylog=True, these will produce false result.
  In essense, TProfile produces y-mean in each bin, but mean-of-log is NOT
  the same as log-of-mean. NEED CAREFUL INTERPRETATION
- This case is found in BPVIP:PT plot.
- Long term solution: Provide a wrap around this use case
  1. Validation: Check for dim==2, prof in options, and ylog==True.
  2. Wrapped y-param under TMath::Log10. check and raise if conflict.
  3. Draw TProfile of that wrapped y-param.
  4. Extract bin val/err, do the exponential manually, then put into (new) histo.
  5. Return that histo for stacking.
- 160105 WAIT. Actually, when I think about it further. It's already correct.
  I should not do the average of quantity in logarithmic space, since the TProfile's
  average of these quantities result in geometric mean (sum of log = log of product).
- It's all cool, forget me.



> Ratio plot

> Wrapper around options to check attribute?
  - e.g., Option(val).prof to boolean-check for profile

> Async draw!?
  - For the case of many QHist instance in a single file, not within instance.

- Repackage PyROOT and QHist into one sub-package under MyPythonLib. 
  - Rewire the `import ROOT` statement. (inspired by golang)



### TProfile
hfin.GetXaxis().SetTitleOffset( 1.1 ) ## Space of text label and h 
hfin.GetYaxis().SetTitleOffset( 0.9 ) ## Space of text label and h 
hfin.SetLabelOffset( 0., 'X' ) ## This is space between numeric value and h
### TH2F
qhist.upperPad.SetRightMargin(0.12)  # For z-axis gradient
hfin.GetYaxis().SetTitleOffset( 0.7 ) ## Space of text label and h 
hfin.SetLabelOffset( 0., 'X' ) ## This is space between numeric value and h


> 151206 Rewiring THStack?
  - Motivation: 
    - It feels like there're 3 passes going on in current implementation
      of QHist. Is it possible to slim down to just 2 passes for speed?
    - THStack is advertised that it can automatically adjust the bound 
      for the merging histograms. How much can I leverage from this?
    - I want to rethink about the 'data+stack' style which expected to
      be more common in fitting with comparison between MC and data.
      Current implementation uses `st_code==2` flag, to trigger the generation 
      of new THStack containing all but first (data) histo, then the data histo
      is drawed on top using `same` flag. Is this the way to go?
    - I also got a hunch feeling that, if I wire things correctly, I don't even
      need the `QHist.wrappers` module. `TTree` is smart and doing this already.
  - Obsv: THist can superimpose 2 hists of different binsize together, BUT,
    the interpretation on y-axis is rubbish. 
  - Obsv: The order of THStack::Add doesn't matter quite much in 'nostack' mode,
    but it will tremendously be in the default mode.
    In other word, to have sensible result of merged histogram, the binsize has
    to be well-defined and consistent.
  - Obsv: TStack::Add only accept the histogram as argument, so there'll always
    be at least 2 passes, where the 1st-pass draw histo from tree, and 2nd-pass
    draw THstack from histo.
  - Obsv: THStack also supports TH2, nice! (haven't tried it though).
  - Obsv: TTree::Draw('goff') is not that slow. Using kernprof, I believe that 
    the graphics (TCanvas) is what slows down.
  > Tentative plan (with wrappers removed).
    - 1st-pass: The determination of range, affected by selection cuts, means
                that the starting point is at TTree::Draw anyway.
    - 2nd-pass: Use TTree::Draw again with corrected range from 1st-pass.
                Collect & own the cloned histogram.
    - 3nd-pass: Purge collected histos into THStack, with post-processor here.


- Refectored test_qhist into smaller files


> Stats: Embed the local log logic here.

> PyrootCK: Decouple needs on GangaCK for import_tree. Use bash-like PATH approach instead.

> ratio histogram, as postprocessors.




### QHist enchancement --> PyrootCK

- QHist: Bring 2D superimpose
  - Still under trial & error
- QHist: Height of legend+console to be more deterministic
- QHist.setattr should implcitly call ROOT.SetOwnerShip!
  - That simplify lots of codes
- Relocate to st_line, st_color, st_marker, st_grid
- Some bug with height_console which slows down tremendously
  - Found it! If I call list() on TChain instance, it'll inflate back to list
    of TTrees member. This is called when `_report_stats` needs to consult 
    default value from QHist()
- loop_first_pass wrongly determine nbin in plot with expansion. 
  It should check the number of event from all exp mmebers.
  - Fixed in QHistUtils.get_stats
- QHist not working properly in log if loop_first_pass not running
  - Fixed, move log-axis control out of loopfirstpass, to prepare_draw_base
- Fix axis report on console to scientific format instead.
- Try auto-log axis judging from magnitude between min/max
  - This is now possible once lfp is moved above pdb
- Depreciate `htemp` dict-like interface. It's a very poor protocol now that 
  I look from it now (I don't understand subclassing so much in the past ).
  We'll get back to this again if needed.
  - Oh, I still need it now after all. The 2nd-pass for superimposing hist 
    require list of hist. Okay, let's subclassing `list` then.
- veto = [ 1E-16 ] to kill some value in order to have better axis control
  Use with extremely care!
- Show filename that produce the plot in debug console.
- QHist: depreciate dir flag
- QHist: prefix flag also do subfoldering
- QHist: don't use prefix to populate subdir (just for name / title )
  But now statically-fixed the subdir population from script name.
- Guard for `import_tree` from null TChain



> QHist now raises `AttributeError` when unknown attr is set.
  > Delegate functionality to PythonCK. Let's call it `static_prop`

> Warn if same param is set twice.

> h.xbin = int, to handle the integer/boolean data... this is gonna be tricky.

> Stock the min-max of each exp-member to show at stats
  - Note: This will not be available if lfp is skipped... What now?


> Request: RootSQL: Sort final TTree output branch name
> RootSQL: RENAME should imply implicit SELECT
> qhist templater (generate the template plotting script from the 
  given uri to tree. Useful for profiling large amount of data).
> Refactor `_report_stats` to `__repr__`?
> import_tree: TChain looks to panasas as fallback
> QHist should count (without axis)/nvisible(with axis)
> Do __slots__ on qhist. Raise warning if non-flag is set



> qhist: repeat draw for progressive plot




--------------------------------------------------------------------------------

Version History
===============

Sort by newest first

### General
- 160715: Maintenance
  - Aim: provide a robust framework on syntax & utils without QHist framework
  - Correct bad pytest version (misalign against ROOT)
  - Isolate out the test of QHistV3 for now, not ready.
  - Fix ioutils to lower case
  > How to add README as entry-point to sphinx output?
  > Prepare README, as TOC to apidoc.
  > Recheck the markdown/rst syntax into output.
  > Let pytest coverage works on /scripts too


### PyROOT syntax reduction
- 160116: Making PyROOT less verbose with pythonic descriptor protocol.
  - e.g., h.GetXaxis().SetTile = h2.GetTitle() --> h.xaxis.title = h2.title
  - At first, it seems simple. I provide this patch directly to TObject class 
    which is the base class for every objects. It seems simple because it doesn't
    have the getattr/setattr. However, I found later that some class, like TTree,
    has custom getattr. So the patching needs some care...
- 160212: Simplified TObject_getattr
- 160526: Setattr to be more secure: dont allow attr set at all, only those
  available in the setters, i.e., disable monkeypatching.
- 160526: Adapter for [float] -> array('f'), used in TGraphAsymmErrors
- 160801: Making syntax-reduction patch works with gPad, gROOT, gStyle.
  - Huh, strange. I thought it didn't work before. Right now it works fine.
    Perhaps the patching order was incorrect before. Perhaps the new ROOT
    version compiled-against-brew-python works. 


### Linkage with `pandas`
- 160613: converter module: DataFrame <--> `TH2`
  - Also for `TGraphs`, `TGraphsAsymError`, `TTree`. That's all I needed.


### root_browse shell script
- 160803: Use native fileopen.C inside `root_browse`, more robust
  - Now I can remove my `tbrowser.C`.
- 160803: Now share the same code as `import_tree`. 
- 160214: guard for `root_browse` for CalledProcessError when EOS token is not
  available.


### ioutils
- 160803: Merging `root_browse` and `import_tree`
  - Think: `root_browse` and `import_tree` actually has the same functionality,
    having the `import_tree` as a function done after getting the correct file.
    So a better refactoring should be possible.
  - challenge: Can this be done such a way that I don't import ROOT package?
    Theoretically it should be possible.
    - Try wrapping the import with decorator lazy_instance
      - No can do: the patcher needs ROOT immediately.
    - what if now, delay the patching until ROOT is lazy imported too?
      - Okay, this works. The caveat is styling routine is disabled. It's okay,
        I need to fix that into better solution anyway.
  - Done! It now works beautifully for both functions!
  - 160210: Refactor `seek_eos` to ioutils.
    - also done as a consequence.
- New general-purpose `import_tree`
  - Now always based on TChain
  - Ask for treename first, then arbitary list of sources. The reason is that 
    by mechanism of TChain.Add, it reconcile the list of file by their posession 
    of tree of given name, thus I ask the treename first.
- Fix: Want QHist to show JID again ( for TTree from Ganga ), this was broken
  by the new implementation using TChain
  - Fix: Need to store ( possibly collection of ) integer representing JID
    inside a TTree. 
  - Natively, there's possibly `TTree->GetUserInfo->Add`
  - Actually, this is python, so I can always monkey-patch key-val as attribute
    arbitrarily to instances anyway... Use this, much simpler.
    - Note: This would introduce a coupling between `import_tree` (write), 
      and `QHist` (read). Which is not that robust...
  - Or even easier, just insert this info into tree's title. Voila!


### QHist
- Allow zero-plot, just give warning
- 150605 Note to self
  - `wrapper.new` feels more correct to exclude the name/title 
    from the signature. Initially, this will pose the problem 
    because wrapper.new is used in 2 places: In clones, and 
    in final mother. They need unique names. Let's think about 
    this and see whether this can be improved.
  - The only way I can think of to do superimpose + partial 
    stack properly, is to draw all (TH1) hists just like before,
    and right at the end of loop, partially collect those that
    need to be inside stack, and draw stack instead of those.
      This implementation will be in generic QHist._draw_wrapped
    area, but it feels strange since THStack is exclusively for
    collections of TH1F only (and thus should reside in Wrapper).
    Is there alternative approach?
- Separate _qhist.root by script name.
  - This is needed in the exporter script to be more managable.
- 160202: Experimental lambda-scale on TH1F (for comparing histogram).
  In this feature, instead of passing float as fixed area of integral required,
  a lambda function taking int is passed instead, where the current intg is to
  be passed into a function. First used in Zmumu background rescaling.


### QHistPdfExporter
- 160316 Bad news, TPolyLine is not so sompat with BuildLegend. It's not derived
  from TNamed in the first place. I cannot edit/store information at QHist level
  to be used to QHistPdfExporter. Thus, it seems that I have to provide flag 
  to exporter instead as a workaround.
  - new flag `--legends` accepting tripted is wired. Remain experimental.
- 160608: Attempt to have pull-histo as module in exporter
  - Motivation: Making pull-histogram has been implemented before inside the 
    TFractionFitter module. This should be possible to refactor into exporter
    script such the the pull-histo can be made for compatible-histo input.
  - First, factorize function to make pull histo from 2 histograms, independent
    of the qhist instance.
  - Then, try to use this from the persist TPad 
    - xlog is not propagated, hmm. --> Need to refer from upp beforehand.
    - Resize canvas to flat & long.
    - Provide assert to check qhist compat 
    - Have this as option to display below desired figure.
      - Change signature to (optionally) accept pad to draw on.
      - Prepare additional pad upon passing args to minipdf
        - Trick, don't forget to call parent.cd() before drawing new subpad
      - Link with makepull
    - Even cooler, insert pull right between parent histo and xaxis. 
      Basically, hide the parent's axis and show it in pull's instead.
      - Start by showing all necessary info in pull's xaxis.
        - also borrow xaxis test
      - pull histo axis of same font
    - less morelog? (too crowded in the 6789 region).
  - Finally, interface to the command-line script


