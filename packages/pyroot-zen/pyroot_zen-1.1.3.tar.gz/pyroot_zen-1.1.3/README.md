Pyroot_Zen
==========

`pyroot_zen` is a wrapper around `PyROOT` with better syntax simplification.
By design, it does NOT introduces any new APIs, in order to make its usage more
intuitive, as well as being compatible with other packages.

Why should you use this? as the Zen of Python says: "Readability counts".

Features at a glance:

- Pythonic property instead of Getter/Setter.
- Automatic (awkward `C++` to `python`) arguments conversion.
- Pythonic iterable as expected.

[![package version](https://img.shields.io/pypi/v/pyroot-zen.svg)](https://pypi.python.org/pypi/pyroot-zen)
[![pipeline status](https://gitlab.com/ckhurewa/pyroot-zen/badges/master/pipeline.svg)](https://gitlab.com/ckhurewa/pyroot-zen/commits/master)
[![coverage report](https://gitlab.com/ckhurewa/pyroot-zen/badges/master/coverage.svg)](https://ckhurewa.gitlab.io/pyroot-zen)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Documentation Status](https://readthedocs.org/projects/pyroot-zen/badge/?version=latest)](http://pyroot-zen.readthedocs.io/en/latest/?badge=latest)
[![python version](https://img.shields.io/pypi/pyversions/pyroot-zen.svg)](https://img.shields.io/pypi/pyversions/pyroot-zen.svg)
[![ROOT6 version](https://img.shields.io/github/tag/root-project/root.svg)](https://hub.docker.com/r/rootproject/root-ubuntu16)

Tested with: ROOT 6.08.06 (OSX homebrew), python 2.7.13, pytest 3.1.1.


Relationship with other packages
--------------------------------

- `ROOT`: This is required to be installed by the user, and `PyROOT` should also be available. In theory, it should work on arbitary version of `ROOT`.

- `RooFit`,`RooStats`: If this is installed, the features below will also be available automatically.

- `rootpy` : While on the surface it looks like they share a lot of similarity, the 2 packages usages are very different: `rootpy` requires the user to use the new classes/functions from its namespace to benefit from its functionality, whereas `pyroot_zen` injects the functionality into objects in `PyROOT` directly, and focusing only on syntaxes reduction.


Features / Usages in details
============================

You need only on line!

```python
## Import, before or after `ROOT` is fine.
import pyroot_zen

## This is the same ROOT handle as in `import ROOT`, but patched.
import ROOT

## No new class needed to be remembered.
from ROOT import TH1F
```

Pythonic property instead of Getter/Setter
------------------------------------------

All getters & setters nomenclature are more pythonic.
You can drop away the `Get` and `Set` prefix:

```python
## Some example on a histogram, nothing new here.
>>> c = ROOT.TCanvas()
>>> h = ROOT.TH1F('mass', 'Mass', 100, 80, 120)

## instead of h.GetXaxis().SetTitle("mass [GeV]")
>>> h.xaxis.title = 'mass [GeV]'

## First-character can be any case (upper,lower).
## It's up to you, just be consistent.
>>> h.markerSize = 20
>>> h.LineWidth  = 1

## Or for extreme pythonista, who hates camelCase.
>>> h.marker_color = ROOT.kRed

## Because it's now pythonic property, you can do one-liner read+write.
>>> h.xaxis.titleSize *= 2.0  # instead of h.GetXaxis().SetTitleSize(h.GetXaxis().GetTitleSize()*2.0)

## Guard against duck-typing, so you cannot read/write non-existent field.
>>> h.xxx = ROOT.kRed
Traceback (most recent call last):
  ...
AttributeError: 'TH1F' object has no attribute 'xxx'

## If multiple args, continue to supply as tuple.
>>> h.xaxis.rangeUser = 10, 80           # instead of h.GetXaxis().SetRangeUser(10, 80)
>>> h.fillColorAlpha  = ROOT.kRed, 0.5   # instead of h.SetFillColorAlpha(ROOT.kRed, 0.5)

## The same reduction applies to list getters (`GetListOfXXX`)
>>> ROOT.gROOT.files  # instead of `GetListOfFiles`
<ROOT.TList object ("Files") at ...>

## On the special pointer (gPad, gStyle, gROOT) also works.
>>> ROOT.gROOT.batch = True
>>> ROOT.gPad.logy = True
>>> ROOT.gPad.leftMargin = 0.05

## Default syntax still works, don't worry.
>>> h.SetBinContent(1, 2.0)

```


Automatic arguments conversion
------------------------------

Forget the `Double_t*` (C++ array of pointers) as argument, you can now supply
the native pythonic list of floats:

```python
## TPolyLine (Int_t n, Double_t *x, Double_t *y, Option_t *option="")
>>> ROOT.TPolyLine(3, [1,2,3], [1,4,9])
<ROOT.TPolyLine object ("TPolyLine") at ...>

```

This also applies to `RooFit.RooArgSet`, `RooFit.RooArgList`:

```python
## Use pythonic set {} instead of RooArgSet
>>> x = ROOT.RooRealVar('x', 'x', 1)
>>> ds = ROOT.RooDataSet('data', 'data', {x})
>>> ds
<ROOT.RooDataSet object ("data") at ...>

## Same for RooArgList, use pythonic list []
>>> y = ROOT.RooRealVar('y', 'y', 2)
>>> pdf1 = ROOT.RooGaussian()
>>> pdf2 = ROOT.RooGaussian()
>>> pdf = ROOT.RooAddPdf('pdf', 'pdf', [pdf1, pdf2], [x,y])
>>> pdf
<ROOT.RooAddPdf object ("pdf") at ...>

```

The `RooCmdArg` in the arguments is mapped onto the keyword-arguments:

```python
## Instead of x.frame(ROOT.RooFit.Name('hello'), ROOT.RooFit.Range(10, 20))
>>> frame = x.frame(name='hello', Range=(10, 20))
>>> frame
<ROOT.RooPlot object ("hello") at ...>

## Instead of ROOT.RooFit.LineColor, ...
>>> ds.plotOn(frame, lineColor=ROOT.kBlue, markerSize=4)
<ROOT.RooPlot object ("hello") at ...>

```


Pythonic iterable as expected
-----------------------------

The `RooArgSet` and `RooArgList`, and other container-like objects
now conform with the expected pythonic iterable protocol, for example:


```python
## Loop in TMultiGraph
>>> g1 = ROOT.TGraph()
>>> g2 = ROOT.TGraph()
>>> gr = ROOT.TMultiGraph()
>>> gr.Add(g1)
>>> gr.Add(g2)
>>> len(gr)
2
>>> for i, g in enumerate(gr):
...   g.markerStyle = i+1

```

```python
>>> for coeff in pdf.coefList():    # from above
...   print coeff.val, coeff.error  # instead of GetVal(), GetError()
1.0 0.0
2.0 0.0

```


Other syntax simplifications
----------------------------

`xxx.FindObject` behaves like a dictionary:

```python
## obj.FindObject('name')  -->  obj['name']
>>> h = ROOT.TH1F('htemp', 'htemp', 100, 0, 100)
>>> ROOT.gROOT['htemp']
<ROOT.TH1F object ("htemp") at ...>

```

`RooWorkspace.Import` to avoid python reserved-word `import`:

```python
>>> w = ROOT.RooWorkspace()
>>> w.Import(h)
False

```

Ownership can be set from the attribute, instead of `ROOT.SetOwnerShip(obj, False)`

```python
>>> h.ownership = False

```