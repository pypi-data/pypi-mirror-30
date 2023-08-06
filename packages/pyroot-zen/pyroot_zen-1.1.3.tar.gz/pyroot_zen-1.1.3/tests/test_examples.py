#!/usr/bin/env python
"""

Test each example that it runs succesfully.

"""

from subprocess import check_output, STDOUT

def test_lhcb_z_csc(tmpdir):
  with tmpdir.as_cwd() as olddir:
    src = str(olddir.join('examples/lhcb_z_csc.py'))
    stdout = check_output(src, stderr=STDOUT)
    assert 'Info in <TCanvas::Print>: pdf file lhcb_z_csc.pdf has been created' in stdout

def test_poisson_likelihood(tmpdir):
  with tmpdir.as_cwd() as olddir:
    src = str(olddir.join('examples/poisson_likelihood.py'))
    stdout = check_output(src, stderr=STDOUT)
    assert '68% interval on s is : [0.57, 4.09]' in stdout
    assert 'Best fitted POI value = 2.00' in stdout
    assert 'The computed upper limit is: 6.225' in stdout
