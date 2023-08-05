# -*- coding: utf-8 -*-
"""
Copyright 2018 Michael Yourshaw. All rights reserved.

myourshaw@gmail.com

Licensed under the MIT license.

A GATKReport is simply a text document that contains well-formatted, easy to read representation of some tabular data.
Many GATK tools output their results as GATKReports. A report contains one or more individual GATK report tables.
Every table begins with a header for its metadata and then a header for its name and description.
The next row contains the column names followed by the data.

The Broad provides an R library called gsalib that allows you to load GATKReport files into R for further analysis.

https://gatkforums.broadinstitute.org/gatk/discussion/1244/what-is-the-gatkreport-file-format

This package allows you to load GATKReport files into Python/pandas for further analysis.

Report versions:
https://github.com/broadinstitute/gatk/blob/master/src/main/java/org/broadinstitute/hellbender/utils/report/GATKReportVersion.java
"""

from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

from collections import Counter, namedtuple
from io import StringIO
import os
import re
import sys

import pandas as pd
from warnings import warn

if sys.version_info > (3, 0):
    from collections.abc import MutableMapping
else:
    from collections import MutableMapping

# if sys.version_info > (3, 0):
#     from collections import UserDict
# else:
#     from UserDict import UserDict


class GsalibException(Exception):
    pass


class GatkReport(MutableMapping):
    """
    A key-value collection of pandas DataFrames, each representing a table in a GATK report,
    where key is the (possibly uniquified) table name and value is the DataFrame.
    This is a substitute for .gsa.assignGATKTableToEnvironment in the R gsalib.
    """
    # private stuff
    _used_names = Counter()
    _n_tables = None
    _report_v0_rx = re.compile(
        r'^^##:GATKReport\.v(?P<version>0[0-9.]+)\s*(?P<table_name>[^: ]+)\s*:\s*(?P<table_description>[^:]+)', re.I)
    _report_rx = re.compile(
        r'^#:GATKReport\.v(?P<version>[[0-9.]+):(?P<n_tables>\d+)', re.IGNORECASE)
    _table_format_rx = re.compile(
        r'^##?:GATKTable(:[^:]+)?:(?P<n_cols>\d+):(?P<n_rows>\d+):(?P<col_formats>\S+):;', re.I)
    _table_id_rx = re.compile(
        r'^#:GATKTable:(?P<table_name>[^:]*):(?P<table_description>[^:]*)', re.I)
    _ReportId = namedtuple('ReportId', 'version, n_tables')
    _TableFormat = namedtuple('TableFormat', 'n_cols, n_rows, col_formats')
    _TableId = namedtuple('TableId', 'table_name, table_description')

    def __init__(self, filename, *args, **kwargs):
        """
        Initialize an instance of GatkReport
        :param filename: path to a GATKReport file
        :param args: args
        :param kwargs: kwargs
        """
        self.tables = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys
        # the path of the GATKReport file
        self.filename = filename
        # The name of the collection, typically the basename of the filename
        self.name = os.path.basename(self.filename)

        # Load all GATKReport tables from a file
        with open(self.filename,  'r') as fh:
            self.lines = [line.rstrip() for line in fh]

        # get first line, which must be a GATKReport record
        report_id = self._get_report_id(self.lines[0])

        if report_id is not None:
            # the version of the GATKReport
            self.version = report_id.version
            # assume that versions >=1 will be compatible with 1.2
            if self.version[0] >= 1:
                self._n_tables = report_id.n_tables
                self._read_gatkreportv1(self.lines)
            if self.version[0] == 0:
                self._read_gatkreportv0(self.lines)
        else:
            raise GsalibException("This isn't a GATK Report file or it's an unsupported version.")

    def __getitem__(self, key):
        return self.tables[key]

    def __setitem__(self, key, value):
        self.tables[key] = value

    def __delitem__(self, key):
        del self.tables[key]

    def __iter__(self):
        return iter(self.tables)

    def __len__(self):
        return len(self.tables)

    def __setitem__(self, dataframe):
        """
        Add a Dataframe to the report.
        :param dataframe: the dataframe to be added
        :return: None
        """
        # uniquify table name
        try:
            table_name = [dataframe.name]
        except AttributeError:
            table_name = dataframe.name = 'table'
        self._used_names[table_name] += 1
        if self._used_names[table_name] > 1:
            dataframe.name = table_name = '{}.{}'.format(table_name, str(self._used_names[table_name]))
        self.tables[table_name] = dataframe

    def _get_report_id(self, report_line):
        """
        Get the version of the GATK report. Fo versions >=1 also get the number of tables.
        :param report_line: report definition line
        :return: ReportId (version, n_tables,)
        """
        # first, try to match version >= 1.x
        m = self._report_rx.match(report_line)
        if m is not None:
            return self._ReportId(tuple(map(int, m.group('version').split('.'))), int(m.group('n_tables')))
        else:
            # try to match version 0.x
            m = self._report_v0_rx.match(report_line)
            if m is not None:
                return self._ReportId(tuple(map(int, m.group('version').split('.'))), None)
            else:
                return None

    def _get_table_format(self, table_format_line):
        """
        Get the format of a v1.x GATK table.
        :param table_format_line: table format definition line
        :return: TableFormat (n_cols, n_rows, col_formats,)
        """
        m = self._table_format_rx.match(table_format_line)
        if m is not None:
            return self._TableFormat(int(m.group('n_cols')) - 1,
                                     int(m.group('n_rows')),
                                     m.group('col_formats').split(':'))
        else:
            return None

    def _get_table_v0_id(self, table_id_line):
        """
        Get the name a v0.x GATK table.
        :param table_id_line: table id definition line
        :return: TableId (table_name, table_description,)
        """
        m = self._report_v0_rx.match(table_id_line)
        if m is not None:
            return self._TableId(m.group('table_name'), m.group('table_description'))
        else:
            return None

    def _get_table_id(self, table_id_line):
        """
        Get the name and description of a v1.x GATK table.
        :param table_id_line: table id definition line
        :return: TableId (table_name, table_description,)
        """
        m = self._table_id_rx.match(table_id_line)
        if m is not None:
            return self._TableId(m.group('table_name'), m.group('table_description'))
        else:
            return None

    # Old implementaton for v0.*
    def _read_gatkreportv0(self, lines):
        """
        Reads a v0.x GATK report into a GATKReport object
        :param lines: list of lines from report file
        :return: None
        """
        n_tables = 0
        table_id = None
        table_data = []

        for line in lines:
            # skip blank lines and uninformative comments
            # the GATKReport line will have been parsed by read_gatkreport
            if (line.strip() == ''
                    or (line.strip().startswith('#')
                        and not line.lower().startswith('##:gatkreport'))):
                continue

            # there will be a GATKReport record for each table
            elif line.lower().startswith('##:gatkreport'):
                # add the previous table (if any) to the GATKReport object
                if table_data:
                    table_str = StringIO('\n'.join(table_data))

                    if self.version == (0, 1):
                        # Read a table of whitespace delimited lines into DataFrame
                        df = pd.read_table(table_str, delim_whitespace=True, )
                    else:
                        # Read a table of fixed-width formatted lines into DataFrame
                        df = pd.read_fwf(table_str, )

                    df.name = table_id.table_name
                    self.tables[df.name] = df

                    # clear table data to start a new one
                    table_id = None
                    table_data = []

                if table_id is None:
                    # GATKReport record has table name
                    table_id = self._get_table_v0_id(line)
                    n_tables += 1
                continue

            elif table_id is not None:
                # within a table, the first record is the column names
                # and subsequent lines are data cells
                table_data.append(line)

        # check for last table
        if table_data:
            table_str = StringIO('\n'.join(table_data))

            if self.version == (0, 1):
                # Read a table of whitespace delimited lines into DataFrame
                df = pd.read_table(table_str, delim_whitespace=True, )
            else:
                # Read a table of fixed-width formatted lines into DataFrame
                df = pd.read_fwf(table_str, )

            df.name = table_id.table_name
            self.tables[df.name] = df

    # Load all GATKReport v1 tables from file
    def _read_gatkreportv1(self, lines):
        """
        Reads a v1.x GATK report into a GATKReport object
        :param lines: list of lines from report file
        :return: None
        """
        n_tables = 0
        table_format = None
        table_id = None
        table_data = []

        for line in lines:
            # skip blank lines and uninformative comments
            # the GATKReport line will have been parsed by read_gatkreport
            if (line.strip() == ''
                    or line.lower().startswith('#:gatkreport')
                    or (line.strip().startswith('#')
                        and not line.lower().startswith('#:gatktable'))):
                continue

            # there will be two GATKTable records, format and id
            elif line.lower().startswith('#:gatktable'):
                # add the previous table (if any) to the GATKReport object
                if table_data:
                    n_rows = len(table_data) - 1
                    if n_rows != table_format.n_rows:
                        warn('Table {} should have {} rows, but actually has {}.'.format(
                            table_id.table_name, table_format.n_rows, n_rows))
                    table_str = StringIO('\n'.join(table_data))

                    # Read a table of fixed-width formatted lines into DataFrame
                    df = pd.read_fwf(table_str, )
                    df.name = table_id.table_name
                    self.tables[df.name] = df

                    # clear table data to start a new one
                    table_format = None
                    table_id = None
                    table_data = []

                if table_format is None:
                    # first GATKTable record has column formats
                    table_format = self._get_table_format(line)
                else:
                    # second GATKTable record had table name
                    table_id = self._get_table_id(line)
                    n_tables += 1
                continue

            elif table_format is not None and table_id is not None:
                # within a table, the first record is the column names
                # and subsequent lines are data cells
                table_data.append(line)

        # check for last table
        if table_data:
            n_rows = len(table_data) - 1
            if n_rows != table_format.n_rows:
                warn('Table {} should have {} rows, but actually has {}.'.format(
                    table_id.table_name, table_format.n_rows, n_rows))
            table_str = StringIO('\n'.join(table_data))

            # Read a table of fixed-width formatted lines into DataFrame
            df = pd.read_fwf(table_str, )

            df.name = table_id.table_name
            self.tables[df.name] = df
        if n_tables != self._n_tables:
            warn('Table {} should have {} tables, but actually has {}.'.format(
                table_id.table_name, self._n_tables, n_tables))
