.. Pandeia Engine Documentation documentation master file, created by
   sphinx-quickstart on Tue Jun  6 09:16:21 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Pandeia Engine Documentation's documentation!
========================================================

This is the beginning of the documentation

Basic Stuff
-----------

JWST Instruments
^^^^^^^^^^^^^^^^

There are four instruments for the JWST telescope.  They are listed in https://github.com/STScI-SSB/pandeia_data/blob/master/jwst/telescope/config.json
and are NIRCAM, NIRSPEC, MIRI and NIRISS.  Each instrument has numerous imaging and spectroscopic modes.  The
different modes are listed in the config.json file specific to the instrument and can be found by clicking on the
instrument directory from within https://github.com/STScI-SSB/pandeia_data/tree/master/jwst.

The instrument config.json files list the valid things, such as readmodes, filters, subarrays, apertures etc. There is
also a key for the defaults which lists the default setup for each mode for the instrument.  There is also information
in the `engine_input_api`_ and `engine_output_api`_ files.

.._engine_input_api: https://github.com/STScI-SSB/pandeia/blob/master/engine/doc/engine_input_api.rst
.._engine_output_api: https://github.com/STScI-SSB/pandeia/blob/master/engine/doc/engine_output_api.rst

Running Engine Code
^^^^^^^^^^^^^^^^^^^

The very basic method to run a calculation requires a json input and a Python script.  There are several places
 to get a json engine input script (a "jeng" file). The best way is to download the results of a calculation from our web client and modify the file `input.json` in the .zip file.

Once you have a jeng file, then you will need a python script, something like:

.. code-block:: python

   #!/usr/bin/env python
   import sys
   from pandeia.engine.io_utils import read_json
   from pandeia.engine.perform_calculation import perform_calculation

   # Read in the JSON engine information
   calc_input = read_json(sys.argv[1])

   # Run the input through the perform_calculation entry point
   report = perform_calculation(calc_input, webapp=True, dict_report=True)

   # Output some information
   for k, w in sorted(report['warnings'].items()):
       print("Warning: " + w)

   for k, v in sorted(report['scalar'].items()):
       print(k + ": " + repr(v))

This script will read in a JSON input file, run it using perform_calculation and then print some results
to the screen.  The actual output is a Python dict that has keys :code:`['sub_reports', 'information', 'warnings',
'transform', '2d', 'scalar', '1d', 'input', '3d']`

Generally a perform_calculation will do the following things...

1. Read in the calculation input JSON variable in order to determine the telescope and instrument setup.

2. Initialize the Instrument object from the class (in `jwst.py`_)
  This will use some data from the config.json file in the instrument's directory in https://github.com/STScI-SSB/pandeia_data/tree/master/jwst

3. Initialize the Strategy object (`strategy.py`_)

4. Start the signal and noise calculations (`etc3D.py`_)

5. Report on calculations (`report.py`_)

.. _jwst.py: https://github.com/STScI-SSB/pandeia/blob/master/engine/pandeia/engine/jwst.py
.. _strategy.py: https://github.com/STScI-SSB/pandeia/blob/master/engine/pandeia/engine/strategy.py
.. _etc3D.py: https://github.com/STScI-SSB/pandeia/blob/master/engine/pandeia/engine/etc3D.py
.. _report.py: https://github.com/STScI-SSB/pandeia/blob/master/engine/pandeia/engine/report.py


In-Depth Stuff
--------------

.. toctree::
   :maxdepth: 3


Gotcha's
^^^^^^^^

Platform Dependent Results
**************************

.. _here: https://github.com/STScI-SSB/pandeia/issues/2967

So, it seems the results can change depending on the machine (or at least type of machine) the software is run
on. There are to places in the code that call the function :code:`convolve_fft` (:code:`astropy.convolution`) which uses the
:code:`pyfftw` package.  The convolve_fft is called in :code:`astro_spectrum.py` and :code:`etc3D.py`.

The differences in the output values can be anywhere from 1e-5, or better, which we don't care much about to
larger differences which we do care about.  The larger differences typically happen in only a few engine tests.

This appears to be only to do with machine precision and roudning errors propagating through the system. There
is more information `here`_.

We did a bunch of testing and the AWS machines all produced the same output results, but were different than a Mac,
which was different than another linux machine locally.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

