# -*- coding:utf-8 -*-

import csv
import pkg_resources

from os.path import join

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties

__copyright__ = 'Copyright 2017'
__author__ = u'Bsc. Manuel Aguado Martínez'


STYLES = ['s--', 'v--', 'o--', '^--', ',--', '<--', '>--', '1--', '2--'
          '3--', '4--', '.--', 'p--', '*--', 'h--', 'H--', '+--', 'x--'
          'd--', '|--', '---']


def generate_eer_report(stats, save_file):
    """ Generate a CSV file with the given statistics

    @param stats: An iterable with instances of the named tuple Stats
    @type stats: iterable
    @param save_file: The filename used to save the report
    @type save_file: str
    """
    with open(save_file, 'w') as sf:

        # Writing headers
        writer = csv.writer(sf)

        # Writing package version
        pkg_version = pkg_resources.require('pyeer')[0].version
        writer.writerow(['Generated using PyEER ' + pkg_version])

        row = ['Experiment ID', 'GMean', 'GSTD', 'IMean',
               'ISTD', "Sensitivity index (d')", 'AUC', 'J-Index',
               'J-Index (Threshold)', 'MCC', 'MCC (Threshold)', 'EERlow',
               'EERhigh', 'EER', 'FMR=0', 'FMR1000', 'FMR100', 'FMR20',
               'FMR10', 'FNMR0']
        writer.writerow(row)

        for st in stats:
            # Writing stats
            row = [st.exp_id.encode("utf-8"), st.gmean, st.gstd,
                   st.imean, st.istd, st.decidability, st.auc,
                   st.j_index, st.j_index_th, st.mccoef, st.mccoef_th,
                   st.eer_low, st.eer_high, st.eer, st.fmr0, st.fmr1000,
                   st.fmr100, st.fmr20, st.fmr10, st.fnmr0]
            writer.writerow(row)

        # Writing legend
        writer.writerow([])
        writer.writerow(['Legend:'])
        writer.writerow(['GMean: Genuine scores distribution mean'])
        writer.writerow(['GSTD: Genuine scores distribution '
                         'standard deviation'])
        writer.writerow(['IMean: Impostor scores distribution mean'])
        writer.writerow(['IVariance: Impostor scores distribution '
                         'standard deviation'])
        writer.writerow(["Sensitivity index (d'): See NICE:II protocol"
                         " evaluation"])
        writer.writerow(['AUC: Area under the ROC curve'])
        writer.writerow(["J-Index: Youden's J statistic (Youden's Index)"])
        writer.writerow(["MCC: Matthews Correlation Coefficient"])
        writer.writerow(['EER: Equal Error Rate'])
        writer.writerow(['EERlow, EERhigh: See FVC2000 protocol evaluation'])
        writer.writerow(['FMR: False Match Rate'])
        writer.writerow(['FNMR: False Non-Match Rate'])

        writer.writerow([])

        # Writing rates header
        headers = []
        max_nthrs = -1
        for st in stats:
            # Writing rate cruves
            headers += [' ', st.exp_id.encode("utf-8") + ' (FMR)',
                        st.exp_id.encode("utf-8") + ' (FNMR)']

            nthrs = len(st.thrs)
            if nthrs > max_nthrs:
                max_nthrs = nthrs
        writer.writerow(headers)

        # Writing rates
        for i in range(max_nthrs):
            row = []
            for st in stats:
                if i < len(st.thrs):
                    row += [' ', st.fmr[i], st.fnmr[i]]
                else:
                    row += [' ', ' ', ' ']
            writer.writerow(row)


def generate_cmc_report(stats, max_rank, save_file):
    """ Generate a CSV file with the given CMC rank values

    @param exps_cmc: A list of CMCstats instances
    @type exps_cmc: list
    @param max_rank: The maximum rank of the CMC curves
    @type max_rank: int
    @param save_file: The filename used to save the report
    @type save_file: str
    """
    with open(save_file, 'w') as sf:

        # Writing headers
        writer = csv.writer(sf)
        row = ['Rank-' + str(i) for i in range(1, max_rank + 1)]
        writer.writerow(['Experiment ID'] + row)

        for st in stats:
            # Writing rank values
            writer.writerow([st.exp_id] + st.ranks)


def plot_eer_stats(stats, line_width=3, hist_format=True, bins=100,
                   lgf_size=15, log_plot=True, save_plots=False,
                   dpi=None, save_path='', ext='.png'):
    """Plot a series of graphs from the given stats

    @param stats: An iterable with instances of the named tuple Stats
    @type stats: iterable
    @param line_width: The width of the plotted curves (default=3)
    @type line_width: int
    @param hist_format: Indicates whether the impostor scores are in
                        histogram format
    @type hist_format: bool
    @param bins: The number of bins to compute scores distribution
                 It will be ignored if the hist_format=True
    @type bins: int
    @param lgf_size: The size of the legend font (default=15)
    @type lgf_size: int
    @param log_plot: Indicates whether to plot the DET curves in a
                     log-log scale
    @type log_plot: bool
    @param save_plots: Indicates whether to save the plots instead
                       of showing them
    @type save_plots: bool
    @param dpi: Plots resolution (dots per inch) used when save_plots=True.
                If not given it will default to the value of savefig.dpi
                in the matplotlibrc file
    @type dpi: int
    @param save_path: Path to save the plots (if save_plots=True)
                      and stats report
    @type save_path: str
    @param ext: Format to save the plots if save_plots=True. Valid
                formats are: (.png, .pdf, .ps, .eps and .svg)
                (default='.png')
    @type ext: str
    """
    # Preparing plots
    det_fig = plt.figure()
    det_plot = det_fig.add_subplot(111)
    det_plot.set_title('DET Curves')
    det_plot.set_ylabel('FNMR')
    det_plot.set_xlabel('FMR')

    if log_plot:
        det_plot.set_yscale('log')
        det_plot.set_xscale('log')
        det_plot.grid(True, which='both', ls='--')
    else:
        det_plot.grid(True)

    roc_fig = plt.figure()
    roc_plot = roc_fig.add_subplot(111)
    roc_plot.set_title('ROC Curves')
    roc_plot.grid(True)
    roc_plot.set_ylabel('1 - FNMR')
    roc_plot.set_xlabel('FMR')

    if log_plot:
        # roc_plot.set_yscale('log')
        roc_plot.set_xscale('log')
        roc_plot.grid(True, which='minor', ls='--')
    else:
        roc_plot.grid(True)

    if not log_plot:
        roc_plot.plot([0, 1], [0, 1], 'k--', linewidth=line_width)

    for st in stats:
        # Plotting score distributions
        title = 'Score distributions experiment: ' + st.exp_id
        dist_fig = plt.figure()
        dist_plot = dist_fig.add_subplot(111)
        dist_plot.grid(False)
        dist_plot.set_ylabel('Frequency')
        dist_plot.set_xlabel('Scores')
        dist_plot.set_title(title)

        if hist_format:
            m = max(st.gen_scores)
            x = np.arange(m)
            ghist = np.histogram(st.gen_scores, bins=np.arange(m + 1))[0]
            dist_plot.plot(x, ghist, color='g',
                           label='Genuine scores %d' % len(st.gen_scores))

            x = np.arange(len(st.imp_scores))
            dist_plot.plot(x, st.imp_scores, color='r',
                           label='Impostor scores %d' % sum(st.imp_scores))
        else:
            dist_plot.hist(st.gen_scores, bins=bins, color='g',
                           label='Genuine scores %d' % len(st.gen_scores))
            dist_plot.hist(st.imp_scores, bins=bins, alpha=0.5, color='r',
                           label='Impostor scores %d' % len(st.imp_scores))

        dist_plot.legend(loc='best', prop=FontProperties(size=lgf_size))

        if save_plots:
            fig_name = 'Distributions (%s)' % st.exp_id + ext
            dist_fig.savefig(join(save_path, fig_name), dpi=dpi)

        # Plotting FMR and FNMR curves
        eer_fig = plt.figure()
        eer_plot = eer_fig.add_subplot(111)
        eer_plot.grid(True)
        eer_plot.set_ylabel('Error')
        eer_plot.set_xlabel('Matching Scores')
        eer_plot.set_title('FMR and FNMR Curves')
        eer_plot.plot(st.thrs, st.fmr, linewidth=line_width,
                      label=st.exp_id + ' (FMR)')
        eer_plot.plot(st.thrs, st.fnmr, linewidth=line_width,
                      label=st.exp_id + ' (FNMR)')
        eer_plot.legend(loc='best', prop=FontProperties(size=lgf_size))

        if save_plots:
            fname = 'FMR and FNMR curves of experiment: (%s)' % st.exp_id + ext
            eer_fig.savefig(join(save_path, fname), dpi=dpi)

        # Plotting DET Curve
        det_plot.plot(st.fmr, st.fnmr, label=st.exp_id, linewidth=line_width)

        # Plotting ROC Curve
        label = st.exp_id + ' AUC = %f' % st.auc
        roc_plot.plot(st.fmr, 1 - st.fnmr, label=label, linewidth=line_width)

    # Finalizing plots
    det_plot.legend(loc='best', prop=FontProperties(size=lgf_size))
    roc_plot.legend(loc='best', prop=FontProperties(size=lgf_size))

    # Showing plots or saving plots
    if save_plots:
        # saving plots
        det_fig.savefig(join(save_path, 'DET' + ext), dpi=dpi)
        roc_fig.savefig(join(save_path, 'ROC' + ext), dpi=dpi)

        # closing plots
        plt.close()
    else:
        plt.show()


def plot_cmc_stats(stats, max_rank, line_width=3, lgf_size=15,
                   save_plots=False, dpi=None, save_path='', ext='.png'):
    """Plot a series of graphs from the given stats

    @param stats: An iterable with instances of the named tuple CMCstats
    @type stats: iterable
    @param max_rank: The maximum rank of the CMC curves
    @type max_rank: int
    @param line_width: The width of the plotted curves (default=3)
    @type line_width: int
    @param lgf_size: The size of the legend font (default=15)
    @type lgf_size: int
    @param save_plots: Indicates whether to save the plots instead
                       of showing them
    @type save_plots: bool
    @param dpi: Plots resolution (dots per inch) used when save_plots=True.
                If not given it will default to the value of savefig.dpi
                in the matplotlibrc file
    @type dpi: int
    @param save_path: Path to save the plots (if save_plots=True)
                      and stats report
    @type save_path: str
    @param ext: Format to save the plots if save_plots=True. Valid
                formats are: (.png, .pdf, .ps, .eps and .svg)
                (default='.png')
    @type ext: str
    """
    # Preparing plots
    plt.title('CMC Curves')
    plt.ylabel('Accuracy')
    plt.xlabel('Rank')
    plt.grid(True)
    plt.axis(xmin=1, xmax=max_rank)
    plt.xticks(range(1, max_rank))

    for i, st in enumerate(stats):
        plt.plot(range(1, len(st.ranks) + 1), st.ranks, STYLES[i],
                 label=st.exp_id, linewidth=line_width)

    # Finalizing plots
    plt.legend(loc='best', prop=FontProperties(size=lgf_size))

    # Showing plots or saving plots
    if save_plots:
        # saving plots
        plt.savefig(join(save_path, 'CMC' + ext), dpi=dpi)

        # closing plots
        plt.close()
    else:
        plt.show()
