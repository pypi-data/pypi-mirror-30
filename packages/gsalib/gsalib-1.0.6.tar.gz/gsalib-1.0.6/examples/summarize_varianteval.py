"""
Copyright 2018 Michael Yourshaw. All rights reserved.

myourshaw@gmail.com

Licensed under the MIT license.

Summarize several tables produced by GATK VariantEval into a VariantEvalMetricsSummary table
as described in (howto) Evaluate a callset with VariantEval
https://software.broadinstitute.org/gatk/documentation/article?id=6211
"""

from argparse import ArgumentParser
import json
import pandas as pd
from pathlib import Path

from gsalib import GatkReport


def df_to_dict(df, orient='None'):
    """
    Replacement for pandas' to_dict which has trouble with
    upcasting ints to floats in the case of other floats being there.
    https://github.com/pandas-dev/pandas/issues/12859#issuecomment-208319535
    see also https://stackoverflow.com/questions/37897527/get-python-pandas-to-dict-with-orient-records-but-without-float-cast
    :param df: a pandas DataFrame
    :param orient: The format of the intermediate JSON string and resulting dict
    :return: dict
    """
    return json.loads(df.to_json(orient=orient))


def run(**kwargs):
    """
    Summarize several tables produced by GATK VariantEval into a VariantEvalMetricsSummary table
    as described in (howto) Evaluate a callset with VariantEval
    https://software.broadinstitute.org/gatk/documentation/article?id=6211
    :param kwargs: arguments from command line
    :return: None
    """
    report_file = kwargs['input']
    print(f'Reading report file : {report_file}')
    if kwargs['output']:
        summary_file = kwargs['output']
    else:
        summary_file = report_file + '.summary.grp'
    Path(summary_file).parent.mkdir(parents=True, exist_ok=True)

    # read report file
    report = GatkReport(report_file)
    tables = report.tables

    # reindex tables by CompRod, Novelty
    for k in report.keys():
        tables[k].reset_index(inplace=True)
    for k in report.keys():
        tables[k].set_index(['CompRod', 'Novelty'], inplace=True)

    # Create VariantEvalMetricsSummary table
    # See https://software.broadinstitute.org/gatk/documentation/article?id=6211

    # select interesting data from VariantEval tables
    compoverlap = tables['CompOverlap'].loc[:, ['concordantRate']]
    indelsummary = tables['IndelSummary'].loc[:, ['n_SNPs', 'n_indels', 'insertion_to_deletion_ratio']]
    titvvariantevaluator = tables['TiTvVariantEvaluator'].loc[:, ['tiTvRatio']]
    countvariants = tables['CountVariants'].loc[:, ['nSNPs', 'insertionDeletionRatio']]
    multiallelicsummary = tables['MultiallelicSummary'].loc[:, ['nSNPs', 'nIndels']]
    validationreport = tables['ValidationReport'].loc[:, ['nComp', 'TP', 'FP', 'FN', 'TN']]

    # create a concatenated DataFrame of the interesting data
    metrics_analysis = pd.concat([
        compoverlap,
        indelsummary,
        titvvariantevaluator,
        countvariants,
        multiallelicsummary,
        validationreport,
    ],
        axis=1)

    # TODO: dynamically compute formats
    col_formats = '%s:%s:%s:%.2f:%d:%d:%.2f:%.2f:%d:%.2f%d:%d:%d:%d:%d:%d:%d'

    # convert DataFrame to dict
    metrics_dict = df_to_dict(metrics_analysis, orient='split')

    # an extra VariantEvalMetricsSummary column and two indices will be added
    n_cols = len(metrics_dict['columns']) + 3
    n_rows = len(metrics_dict['data'])

    with open(summary_file, 'w') as sf:
        # report and table metadata
        sf.write('#:GATKReport.v1.1:1' + '\n')
        sf.write(f'#:GATKTable:{n_cols}:{n_rows}:{col_formats}:;' + '\n')
        sf.write(f'#:GATKTable:{kwargs["table_name"]}:Selected metrics from VariantEval' + '\n')
        # columns header
        rows = [[kwargs["table_name"]] + ['CompRod', 'Novelty'] + metrics_dict['columns']]
        # table data
        for i in range(len(metrics_dict['index'])):
            rows.append([kwargs["table_name"]]
                        + list(metrics_dict['index'][i])
                        + list(map(str, metrics_dict['data'][i])))

        # TODO: left justify strings
        # write header and data in fixed width format
        widths = [max(map(len, col)) for col in zip(*rows)]
        for row in rows:
            sf.write("  ".join((val.rjust(width) for val, width in zip(row, widths))) + '\n')

    print(f'Results saved to : {summary_file}')


def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input",
                        required=True,
                        help="GATK report file from VariantEval")
    parser.add_argument("-o", "--output",
                        help="output file (default: <input>.summary.grp)")
    parser.add_argument("--table_name",
                        default='VariantEvalMetricsSummary',
                        help="output table name (default: VariantEvalMetricsSummary)")

    args = parser.parse_args()

    run(**vars(args))


if __name__ == "__main__":
    main()
