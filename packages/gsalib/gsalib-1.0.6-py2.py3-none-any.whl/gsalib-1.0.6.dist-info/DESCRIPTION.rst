gsalib: Python/pandas package of utility functions for GATK
=============================================================

``gsalib`` makes it easy for Python users to analyze metrics reports created by the Broad Institute's Genome Analysis Toolkit (GATK). The Broad provides an R library called gsalib that allows you to load GATKReport files into R for further analysis (https://gatkforums.broadinstitute.org/gatk/discussion/1244/what-is-the-gatkreport-file-format). Python ``gsalib`` is an adaptation of the R libray that allows you to load GATKReport files into Python/pandas DataFrames.

Neither the R nor Python versions of ``gsalib`` support the samtools.metrics reports created by `Picard Tools <https://broadinstitute.github.io/picard/picard-metric-definitions.html>`_. To analyze Picard reports with Python, consider using the ``picard.parse`` function in the `Crimson <https://pypi.python.org/pypi/Crimson>`_ module.

Features
--------

- Enables analysis of GATK reports with powerful pandas DataFrames and plotting
- Reads GATKReport versions 0.x and 1.x
- Compatible with Python >=2.7 and >=3.4

Installation
------------

Install ``gsalib`` by running ::

    pip install gsalib

Example
-------

Read a report and get a table's DataFrame::

    from gsalib import GatkReport

    report = GatkReport('/path/to/gsalib/test/test_v1.0_gatkreport.table')
    table = report.tables['ExampleTable']

Documentation
-------------

https://gsalib.readthedocs.io/en/latest/

Contribute
----------

- Issue Tracker: https://github.com/myourshaw/gsalib/issues
- Source Code: https://github.com/myourshaw/gsalib

License
-------

The project is licensed under the MIT license.


