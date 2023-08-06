__author__ = 'jlane'

from model import ComparisonDataSet
from model import ClonotypeSample
from model import ClonotypeSamples
from model import ClonotypesList

from time import asctime, localtime, time
from math import ceil, pow
from collections import Counter
from os import path, walk
from pandas import DataFrame, concat, read_csv, Series
from numpy import sqrt, isnan, where, setdiff1d, nan, intersect1d, arange, array, concatenate, percentile, median, mean, linspace, sum, random, prod, power, log10, mean
import matplotlib.pyplot as plt
from matplotlib import cm
from pylab import savefig
from scipy.stats import fisher_exact, spearmanr, pearsonr, percentileofscore
from sklearn.metrics import roc_curve, auc
from seaborn import heatmap
from sys import stdout
import matplotlib
import zipfile
matplotlib.use('Agg')

import venn

import matplotlib.ticker as ticker

# from rpy2 import robjects


def clonotype_distribution(output_path, sample1_id, counter_df1, sample1_df=None):
    fig, ax1 = plt.subplots()

    # print(list(df1.iloc[:,0]))
    # print(list(df1.index.astype(int)))

    ax1.scatter(list(counter_df1.index.astype(int)), list(counter_df1.iloc[:,0].astype(int)), clip_on=False)

    ylims = ax1.get_ylim()
    xlims = ax1.get_xlim()

    ax1.grid(color='gainsboro', linestyle='dashed')

    ax1.set_ylim(1, ylims[1])
    ax1.set_xlim(1, xlims[1])
    ax1.set_xscale('log', basex=10)

    # ax1.set_yscale('log', basey=10)

    # ax1.xaxis.set_minor_formatter(plt.FormatStrFormatter('%d'))
    # ax1.yaxis.set_minor_formatter(plt.FormatStrFormatter('%d'))

    for tick in ax1.xaxis.get_major_ticks():
        tick.label.set_fontsize(20)
    for tick in ax1.yaxis.get_major_ticks():
        tick.label.set_fontsize(20)

    # ax1.text(0.5, 0.04, '# clonotypes', fontsize=25, ha='center', va='center')

    ax1.set_ylabel('# clonotypes', fontsize=20)
    ax1.set_xlabel('# counts per clonotype', fontsize=20)

    fig.savefig(
        output_path + str(sample1_id) + '_scatter_distribution.pdf',dpi=300, format='pdf', bbox_inches='tight')

    if sample1_df is not None:
        # print("sample1_df: ", sample1_df)

        print("len index: ", len(sample1_df.index))
        print("max: ", sample1_df.max())

def plot_frequencies_distribution(output_path, sample):
    print("plot_frequencies")

    # sample1_seqid, sample2_seqid = sample.get_sample_id()

    s = sample.get_cell_counts_df()
    # print('s: ', s)
    # sample1_id = sample.ID
    # sample2_id = df.columns.values[1]

    # index_mod = where(s != 0)[0]
    # s = s.iloc[index_mod]

    # index_sp1 = where(s != 0)[0]
    # index_sp2 = where(df[sample2_id] != 0)[0]

    # mymin_x_line = min(array(s.iloc[index_sp1].values)) * 0.9
    # mymin_y_line = min(array(df[sample2_id].iloc[index_sp2].values)) * 0.9

    # mymin_exvivo = min(array(s.iloc[index_sp1].values)) * 0.6
    # mymin_invitro = min(array(df[sample2_id].iloc[index_sp2].values)) * 0.6

    intersect_index_mod = where(array(s) != 0)[0]

    if len(intersect_index_mod) > 0:
        # print("intersect_index_mod : ", intersect_index_mod)

        sample1_df_interct = s.iloc[intersect_index_mod]
        # sample2_df_interct = df[sample2_id].iloc[intersect_index_mod]

        # print('sample1_df_interct: ', sample1_df_interct)
        sample1_df_interct = sample1_df_interct.astype(int)
        sample1_df = sample1_df_interct.sort_values(ascending=True)


        cnt1 = Counter(sample1_df_interct.values.tolist())
        # cnt2 = Counter(sample2_df_interct)

        # print("sample 1:", dict(cnt1))
        # print("sample 2:", dict(cnt2))

        df1 = DataFrame.from_dict(dict(cnt1), orient="index")
        # print('df1:', df1)
        df1 = df1.sort_values(by=0, ascending=False)
        # print('df1:', df1)

        clonotype_distribution(output_path, sample.ID, df1, sample1_df)

        # df1 = DataFrame.from_dict(dict(cnt1), orient="index")

    # frequency_plot(output_path, [sample1_id, sample2_id], df, mymin_exvivo, mymin_invitro, mymin_x_line, mymin_y_line)

def frequency_plot(output_path,  samples, df, mymin_exvivo, mymin_invitro, mymin_x_line, mymin_y_line):

    f, [[ax_up_left, ax2_up_right], [ax3_down_left, ax4_down_right]] = plt.subplots(2, 2, gridspec_kw={ 'width_ratios': [1, 20], 'height_ratios': [20, 1]})

    ledg1, subplots_list, var1, var2 = insert_axis_info_frequency_plot(df, mymin_exvivo, mymin_invitro, mymin_x_line, mymin_y_line,
                                                                                       [ax_up_left, ax2_up_right, ax3_down_left, ax4_down_right],
                                                                                       color='silver', label=None, resize=True)

    f.text(0.5, 0.04,  samples[0], fontsize=25, ha='center', va='center')
    f.text(0.025, 0.5, samples[1], fontsize=25, ha='center', va='center', rotation='vertical')
    f.text(0.025, 0.5,  samples[1], fontsize=25, ha='center', va='center', rotation='vertical')

    print(str(samples[0]) + "_vs_" + str(samples[1]) + '_scatter.pdf')

    f.subplots_adjust(hspace=0.09, wspace=0.09, left=0.15, bottom=0.15, top=0.85, right=0.85)
    f.savefig(output_path + str(samples[0]) + "_vs_" + str(samples[1]) + '_scatter.pdf', dpi=300, format='pdf')




def set_logscale_manage_spine_frequency_plot(subplot_index, ax, spines_to_set_to_invisible, num_subplots, kwargs):
    # d = 0.015
    # how big to make the diagonal lines in axes coordinates
    # arguments to pass plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)

    for spine in spines_to_set_to_invisible:
        if "bottom" == spine:
            ax.xaxis.tick_top()
            ax.tick_params(labelbottom='off', which='both')
        if "top" == spine:
            ax.xaxis.tick_bottom()
            ax.tick_params(labeltop='off', which='both')
        if "left" == spine:
            ax.yaxis.tick_right()
            ax.tick_params(labelleft='off', which='both')
        if "right" == spine:
            ax.yaxis.tick_left()
            ax.tick_params(labelright='off', which='both')
        ax.spines[spine].set_visible(False)

    if num_subplots == 6:
        if subplot_index in [0, 1, 2, 3]:
            ax.tick_params(labeltop='off', which='both')
            ax.tick_params(labelbottom='off', which='both')
            ax.tick_params(bottom='off', which='both')
            ax.tick_params(top='off', which='both')

        if subplot_index in [4, 5]:
            ax.tick_params(labeltop='off', which='both')
            ax.tick_params(top='off', which='both')

        if subplot_index in [1, 3, 5]:
            ax.tick_params(labelright='off', which='both')
            ax.tick_params(right='off', which='both')

        if subplot_index == 4:
            ax.tick_params(labelbottom='off', which='both')
            ax.tick_params(bottom='off', which='both')
            ax.tick_params(labelleft='off', which='both')
            ax.tick_params(left='off', which='both')
    else:
        if subplot_index in [0, 1]:
            ax.tick_params(labeltop='off', which='both')
            ax.tick_params(labelbottom='off', which='both')
            ax.tick_params(bottom='off', which='both')
            ax.tick_params(top='off', which='both')

        if subplot_index in [2, 3]:
            ax.tick_params(labeltop='off', which='both')
            ax.tick_params(top='off', which='both')

        if subplot_index in [1, 3]:
            ax.tick_params(labelright='off', which='both')
            # ax.tick_params(labelbottom='off', which='minor')
            ax.tick_params(right='off', which='both')

        if subplot_index in [2]:
            ax.tick_params(labelbottom='off', which='both')
            ax.tick_params(bottom='off', which='both')
            ax.tick_params(labelleft='off', which='both')
            ax.tick_params(left='off', which='both')

    ax.set_yscale('log', basey=10)
    ax.set_xscale('log', basex=10)

    return ax, kwargs

def insert_axis_info_frequency_plot(df, mymin_exvivo, mymin_invitro,  mymin_x_line, mymin_y_line, subplots_list,
                                                    color='silver', label=None, resize=True):

    x_value = pow(10, (log10(mymin_x_line) - log10(mymin_exvivo)) / 2. + log10(mymin_exvivo))
    y_value = pow(10, (log10(mymin_y_line) - log10(mymin_invitro)) / 2. + log10(mymin_invitro))

    myfake_min = min(mymin_exvivo, mymin_invitro)
    myfake_max = 1e-2

    myfake_x_value = pow(10, (log10(myfake_max) - log10(myfake_min)) / 2. + log10(myfake_min))
    myfake_y_value = myfake_x_value

    df_exvivo_nafilled = df[df.columns.values[0]].fillna(x_value)
    df_stim_nafilled = df[df.columns.values[1]].fillna(y_value)

    df = concat([df_exvivo_nafilled, df_stim_nafilled], axis=1)

    counts_freq = Counter(zip(df[df.columns.values[0]], df[df.columns.values[1]]))
    points = counts_freq.keys()

    x, y = zip(*points)

    x = array(x)
    y = array(y)

    mycolors = []

    tups1 = zip(points)

    mymax_invitro = max(y)
    mymax_exvivo = max(x)

    myargs = []

    for subplot_index in range(len(subplots_list)):
        mysubplot = subplots_list[subplot_index]

        # top left
        if subplot_index == 0:
            xlim = [mymin_exvivo, mymin_x_line]
            ylim = [mymin_y_line, mymax_invitro]
            spines_to_set_to_invisible = ["bottom", "right"]

        # top right
        if subplot_index == 1:
            xlim = [mymin_x_line, mymax_exvivo]
            ylim = [mymin_y_line, mymax_invitro]
            spines_to_set_to_invisible = ["bottom", "left"]

        # bottom left
        if subplot_index == 2:
            xlim = [mymin_exvivo, mymin_x_line]
            ylim = [mymin_invitro, mymin_y_line]
            spines_to_set_to_invisible = ["top", "right"]

        # bottom right
        if subplot_index == 3:
            xlim = [mymin_x_line, mymax_exvivo]
            ylim = [mymin_invitro, mymin_y_line]
            spines_to_set_to_invisible = ["top", "left"]

        if resize:
            set_limits(mysubplot, xlim, ylim)

        x_index_mod = where((x >= xlim[0]) & (x <= xlim[1]))[0]
        y_index_mod = where((y >= ylim[0]) & (y <= ylim[1]))[0]

        intersect_index_mod = intersect1d(x_index_mod, y_index_mod)

        if len(intersect_index_mod) > 0:
            if subplot_index in [0, 2]:
                x_values = [myfake_x_value] * len(intersect_index_mod)

                if subplot_index == 2:
                    y_values = [myfake_y_value] * len(intersect_index_mod)

                    if resize:
                        set_limits(mysubplot, [myfake_min, myfake_max], [myfake_min, myfake_max])
                        # print("[xlim, ylim]: ", [mysubplot.get_xlim(), mysubplot.get_ylim()])
                else:
                    y_values = list(Series(y).iloc[intersect_index_mod])

                    if resize:
                        set_limits(mysubplot, [myfake_min, myfake_max], [1, ylim[1]])

                scat = mysubplot.scatter(x_values, y_values, facecolors=color,
                                         s=array(Series(map(sqrt, Series(list(counts_freq.values())).iloc[
                                             intersect_index_mod])) + 30),
                                         marker='o', linewidths=0.5, edgecolor='w', label=label, clip_on=False)
            elif subplot_index == 3:
                if resize:
                    set_limits(mysubplot, [1, xlim[1]], [myfake_min, myfake_max])

                scat = mysubplot.scatter(list(Series(x).iloc[intersect_index_mod]),
                                         [myfake_y_value] * len(intersect_index_mod),
                                         facecolors=color, s=array(
                        Series(map(sqrt, Series(list(counts_freq.values())).iloc[intersect_index_mod])) + 30),
                                         marker='o', linewidths=0.5, edgecolor='w', label=label, clip_on=False)

            else:
                if resize:
                    if subplot_index in [0]:
                        set_limits(mysubplot, xlim, [1, ylim[1]])
                    elif subplot_index in [3]:
                        set_limits(mysubplot, [1, xlim[1]], ylim)
                    else:
                        set_limits(mysubplot, xlim, ylim)

                scat = mysubplot.scatter(Series(x).iloc[intersect_index_mod], Series(y).iloc[intersect_index_mod],
                                         facecolors=color,
                                         s=array(Series(map(sqrt, Series(list(counts_freq.values())).iloc[
                                             intersect_index_mod])) + 30),
                                         marker='o', linewidths=0.5, edgecolor='w', label=label, clip_on=False)

            mysubplot, myargs = set_logscale_manage_spine_frequency_plot(subplot_index, mysubplot, spines_to_set_to_invisible,
                                                          len(subplots_list), myargs)
        else:
            if resize:
                if subplot_index in [0, 2, 4]:
                    if subplot_index == 4:
                        set_limits(mysubplot, [myfake_min, myfake_max], [myfake_min, myfake_max])
                        # print("[xlim, ylim]: ", [mysubplot.get_xlim(), mysubplot.get_ylim()])
                    else:
                        set_limits(mysubplot, [myfake_min, myfake_max], ylim)
                elif subplot_index == 5:
                    set_limits(mysubplot, xlim, [myfake_min, myfake_max])
                else:
                    set_limits(mysubplot, xlim, ylim)

                if subplot_index in [0]:
                    set_limits(mysubplot, xlim, [1, ylim[1]])
                elif subplot_index in [3]:
                    set_limits(mysubplot, [1, xlim[1]], ylim)


            myfakex = (xlim[1] - xlim[0]) / 2. + xlim[0]
            myfakey = (ylim[1] - ylim[0]) / 2. + ylim[0]

            myfakex2 = (xlim[1] - xlim[0]) / 3. + xlim[0]
            myfakey2 = (ylim[1] - ylim[0]) / 3. + ylim[0]

            scat = mysubplot.scatter([myfakex, myfakex2], [myfakey, myfakey2], alpha=0)

            mysubplot, myargs = set_logscale_manage_spine_frequency_plot(subplot_index, mysubplot, spines_to_set_to_invisible,
                                                          len(subplots_list), myargs)

        # for tick in mysubplot.get_xticklabels():
        #     tick.set_rotation(45)

        mysubplot.xaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
        mysubplot.yaxis.set_major_formatter(plt.FormatStrFormatter('%d'))

        for tick in mysubplot.xaxis.get_major_ticks():
            tick.label.set_fontsize(15)
        for tick in mysubplot.yaxis.get_major_ticks():
            tick.label.set_fontsize(15)

        mysubplot.xaxis.set_minor_formatter(plt.FormatStrFormatter('%d'))
        mysubplot.yaxis.set_minor_formatter(plt.FormatStrFormatter('%d'))

        for tick in mysubplot.xaxis.get_minor_ticks():
            tick.label.set_fontsize(8)
        for tick in mysubplot.yaxis.get_minor_ticks():
            tick.label.set_fontsize(8)

    return scat, subplots_list, (mymin_exvivo, max(x)), (mymin_invitro, max(y))

def redelimit_subplots(mymin_exvivo, mymax_exvivo, mymin_invitro, mymax_invitro, mymin_x_line, mymin_y_line,
                       ax_up_left, ax2_up_right, ax3_down_left, ax4_down_right):

    ax_up_left = subplots_managment_for_frequencies_compared_to_exvivo_plots(ax_up_left,
                                                                             [mymin_exvivo, mymin_x_line],
                                                                             [mymin_y_line, mymax_invitro],
                                                                             ["bottom", "right"])

    ax2_up_right = subplots_managment_for_frequencies_compared_to_exvivo_plots(ax2_up_right,
                                                                               [mymin_x_line, mymax_exvivo],
                                                                               [mymin_y_line, mymax_invitro],
                                                                               ["bottom", "left"])

    ax3_down_left = subplots_managment_for_frequencies_compared_to_exvivo_plots(ax3_down_left,
                                                                                [mymin_exvivo, mymin_x_line],
                                                                                [mymin_invitro, mymin_y_line],
                                                                                ["top", "right"])

    ax4_down_right = subplots_managment_for_frequencies_compared_to_exvivo_plots(ax4_down_right,
                                                                                 [mymin_x_line, mymax_exvivo],
                                                                                 [mymin_invitro, mymin_y_line],
                                                                                 ["top", "left"])
    return ax_up_left, ax2_up_right, ax3_down_left, ax4_down_right

def set_limits(ax, xlim, ylim):
    ax.set_xlim(xlim[0], xlim[1])
    ax.set_ylim(ylim[0], ylim[1])
    return ax

def set_logscale_manage_spine(subplot_index, ax, spines_to_set_to_invisible, num_subplots, kwargs):
    # d = 0.015
    # how big to make the diagonal lines in axes coordinates
    # arguments to pass plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)

    for spine in spines_to_set_to_invisible:
        if "bottom" == spine:
            ax.xaxis.tick_top()
            ax.tick_params(labelbottom='off', which='both')
        if "top" == spine:
            ax.xaxis.tick_bottom()
            ax.tick_params(labeltop='off', which='both')
        if "left" == spine:
            ax.yaxis.tick_right()
            ax.tick_params(labelleft='off', which='both')
        if "right" == spine:
            ax.yaxis.tick_left()
            ax.tick_params(labelright='off', which='both')
        ax.spines[spine].set_visible(False)

    if num_subplots == 6:
        if subplot_index in [0, 1, 2, 3]:
            ax.tick_params(labeltop='off', which='both')
            ax.tick_params(labelbottom='off', which='both')
            ax.tick_params(bottom='off', which='both')
            ax.tick_params(top='off', which='both')

        if subplot_index in [4, 5]:
            ax.tick_params(labeltop='off', which='both')
            ax.tick_params(top='off', which='both')

        if subplot_index in [1, 3, 5]:
            ax.tick_params(labelright='off', which='both')
            ax.tick_params(right='off', which='both')

        if subplot_index == 4:
            ax.tick_params(labelbottom='off', which='both')
            ax.tick_params(bottom='off', which='both')
            ax.tick_params(labelleft='off', which='both')
            ax.tick_params(left='off', which='both')
    else:
        if subplot_index in [0, 1]:
            ax.tick_params(labeltop='off', which='both')
            ax.tick_params(labelbottom='off', which='both')
            ax.tick_params(bottom='off', which='both')
            ax.tick_params(top='off', which='both')

        if subplot_index in [2, 3]:
            ax.tick_params(labeltop='off', which='both')
            ax.tick_params(top='off', which='both')

        if subplot_index in [1, 3]:
            ax.tick_params(labelright='off', which='both')
            ax.tick_params(right='off', which='both')

        if subplot_index in [2]:
            ax.tick_params(labelbottom='off', which='both')
            ax.tick_params(bottom='off', which='both')
            ax.tick_params(labelleft='off', which='both')
            ax.tick_params(left='off', which='both')


    # if (len(spines_to_set_to_invisible) == 3) & ("right" in spines_to_set_to_invisible):
    #     # ax.tick_params(labelleft='off')
    #
    #     ax.tick_params(labelright='off')
    #     ax.tick_params(labelbottom='off')
    #     ax.tick_params(labeltop='off')
    #
    #     ax.tick_params(right='off', which='both')
    #     ax.tick_params(bottom='off', which='both')
    #     ax.tick_params(top='off', which='both')
    #
    #     # myx = ax.get_xlim()[0]
    #     # myy = ax.get_ylim()[1]
    #     #
    #     # d = power(10, log10(myx) * 0.1)
    #     # myxp1 = myx - d
    #     # variation = log10(myx) - log10(myxp1)
    #     # myxp2 = power(10, log10(myx) + variation)
    #     #
    #     # d = power(10, log10(myy) * 0.1)
    #     # myyp1 = myy - d
    #     # variation = log10(myy) - log10(myyp1)
    #     # myyp2 = power(10, log10(myy) + variation)
    #     #
    #     # ax.plot((myxp1, myxp2), (myyp1, myyp2)) # top-left diagonal
    #
    # if (len(spines_to_set_to_invisible) == 3) & ("left" in spines_to_set_to_invisible):
    #
    #     ax.tick_params(labelright='off')
    #     ax.tick_params(labelleft='off')
    #     ax.tick_params(labelbottom='off')
    #     ax.tick_params(labeltop='off')
    #
    #     ax.tick_params(right='off', which='both')
    #     ax.tick_params(left='off', which='both')
    #     ax.tick_params(bottom='off', which='both')
    #     ax.tick_params(top='off', which='both')
    #
    #     ax.grid(color='gainsboro', linestyle='dashed')
    #
    #     myx = ax.get_xlim()[1]
    #     myy = ax.get_ylim()[1]
    #
    #     # d = power(10, log10(myx) * 0.1)
    #     # myxp1 = myx - d
    #     # variation = log10(myx) - log10(myxp1)
    #     # myxp2 = power(10, log10(myx) + variation)
    #     #
    #     # d = power(10, log10(myy) * 0.1)
    #     # myyp1 = myy - d
    #     # variation = log10(myy) - log10(myyp1)
    #     # myyp2 = power(10, log10(myy) + variation)
    #     #
    #     # ax.plot((myxp1, myxp2), (myyp1, myyp2)) # top-right diagonal
    #
    #
    # if (len(spines_to_set_to_invisible) == 2) & ("bottom" in spines_to_set_to_invisible) & ("left" in spines_to_set_to_invisible):
    #     ax.tick_params(labelleft='off')
    #     ax.tick_params(labelbottom='off')
    #     ax.tick_params(labeltop='off')
    #     ax.tick_params(labelright='off')
    #
    #     ax.tick_params(right='off', which='both')
    #     ax.tick_params(left='off', which='both')
    #     ax.tick_params(bottom='off', which='both')
    #     ax.tick_params(top='off', which='both')
    #
    #     ax.grid(color='gainsboro', linestyle='dashed')
    #
    #     # myx = ax.get_xlim()[1]
    #     # myy = ax.get_ylim()[0]
    #
    #     # d = power(10, log10(myx) * 0.1)
    #     # myxp1 = myx - d
    #     # variation = log10(myx) - log10(myxp1)
    #     # myxp2 = power(10, log10(myx) + variation)
    #     #
    #     # d = power(10, log10(myy) * 0.1)
    #     # myyp1 = myy - d
    #     # variation = log10(myy) - log10(myyp1)
    #     # myyp2 = power(10, log10(myy) + variation)
    #     #
    #     # ax.plot((myxp1, myxp2), (myyp1, myyp2))  # bottom-right diagonal
    #
    # if (len(spines_to_set_to_invisible) == 2) & ("bottom" in spines_to_set_to_invisible) & ("right" in spines_to_set_to_invisible):
    #     # ax.xaxis.tick_left()
    #     ax.xaxis.set_ticks([])
    #     labels = [item.get_text() for item in ax.get_xticklabels()]
    #
    #     empty_string_labels = [''] * len(labels)
    #     ax.set_xticklabels(empty_string_labels)
    #
    #     # ax.tick_params(labelbottom='off')
    #     # ax.tick_params(bottom='off', which='both')
    #
    #     ax.tick_params(labelright='off')
    #     ax.tick_params(labelbottom='off')
    #     ax.tick_params(labeltop='off')
    #
    #     ax.tick_params(right='off', which='both')
    #     ax.tick_params(bottom='off', which='both')
    #     ax.tick_params(top='off', which='both')
    #
    #     ax.grid(color='gainsboro', linestyle='dashed')
    #
    # if (len(spines_to_set_to_invisible) == 2) & ("top" in spines_to_set_to_invisible) & ("right" in spines_to_set_to_invisible):
    #     ax.tick_params(labelleft='off')
    #     ax.tick_params(labelbottom='off')
    #     ax.tick_params(labeltop='off')
    #     ax.tick_params(labelright='off')
    #
    #     ax.tick_params(right='off', which='both')
    #     ax.tick_params(left='off', which='both')
    #     ax.tick_params(bottom='off', which='both')
    #     ax.tick_params(top='off', which='both')
    #
    # if (len(spines_to_set_to_invisible) == 2) & ("top" in spines_to_set_to_invisible) & ("left" in spines_to_set_to_invisible):
    #     ax.tick_params(labelright='off')
    #     ax.tick_params(labelleft='off')
    #     ax.tick_params(labeltop='off')
    #
    #
    #     ax.tick_params(right='off', which='both')
    #     ax.tick_params(left='off', which='both')
    #     ax.tick_params(top='off', which='both')
    #
    # # if ("bottom" in spines_to_set_to_invisible) & ("right" in spines_to_set_to_invisible):
    # #     ax.tick_params(top='off', which='both')
    # #     ax.tick_params(labeltop='off')
    # #
    # #     myx = ax.get_xlim()[0]
    # #     myy = ax.get_ylim()[0]
    #
    #     # d = power(10, log10(myx) * 0.1)
    #     # myxp1 = myx - d
    #     # variation = log10(myx) - log10(myxp1)
    #     # myxp2 = power(10, log10(myx) + variation)
    #     #
    #     # d = power(10, log10(myy) * 0.1)
    #     # myyp1 = myy - d
    #     # variation = log10(myy) - log10(myyp1)
    #     # myyp2 = power(10, log10(myy) + variation)
    #
    #     # ax.plot((myxp1, myxp2), (myyp1, myyp2))  # bottom-left diagonal
    #
    #     # for tick in ax.get_xticklabels():
    #     #     tick.set_rotation(45)
    #     #
    #     # for tick in ax.xaxis.get_major_ticks():
    #     #     tick.label.set_fontsize(20)
    #     # for tick in ax.yaxis.get_major_ticks():
    #     #     tick.label.set_fontsize(20)

    ax.set_yscale('log', basey=10)
    ax.set_xscale('log', basex=10)

    return ax, kwargs

def subplots_managment_for_frequencies_compared_to_exvivo_plots(ax, xlim, ylim, spines_to_set_to_invisible):
    print("[xlim, ylim, spines_to_set_to_invisible]: ", [xlim, ylim, spines_to_set_to_invisible])

    ax.set_ylim(ylim[0], ylim[1])
    ax.set_xlim(xlim[0], xlim[1])

    for spine in spines_to_set_to_invisible:
        if "top" == spine:
            ax.xaxis.tick_bottom()
            # ax.tick_params(labelbottom='off')
        if "bottom" == spine:
            ax.xaxis.tick_top()
            ax.tick_params(labeltop='off')
        if "left" == spine:
            ax.yaxis.tick_right()
            ax.tick_params(labelright='off')
        if "right" == spine:
            ax.yaxis.tick_left()
            # ax.tick_params(labelleft='off')

        if ("top" in spines_to_set_to_invisible) & ("right" in spines_to_set_to_invisible):
            ax.tick_params(labelleft='off')
            ax.tick_params(labelbottom='off')

        if ("bottom" in spines_to_set_to_invisible) & ("left" in spines_to_set_to_invisible):
            ax.grid(color='gainsboro', linestyle='dashed')

        ax.spines[spine].set_visible(False)

    # d = .015  # how big to make the diagonal lines in axes coordinates
    # # arguments to pass plot, just so we don't keep repeating them
    # kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    # ax.plot((-d, +d), (-d, +d), **kwargs)  # top-left diagonal
    # ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal
    #
    # kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    # ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
    # ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal

    ax.set_yscale('log', basey=10)
    ax.set_xscale('log', basex=10)

    ax.set_axis_bgcolor('white')

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(20)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(20)

    return ax

def get_yticks_mod(ax, ylim):
    yticks_mod = []
    yticks_mod_temp = []

    major_tick_values = ax.get_yticks()

    major_tick_values = Series(major_tick_values).iloc[where((major_tick_values >= ylim[0]) & (major_tick_values <= ylim[1]))[0]]

    for major_tick_value in major_tick_values:
        # print("major_tick: ",major_tick_value)
        if major_tick_value != u'':
            yticks_mod_temp.append(major_tick_value)

    yticks_mod.append(yticks_mod_temp[0])

    if len(yticks_mod_temp) > 0:
        indexes = range(len(yticks_mod_temp))
        # yticks_mod.append(yticks_mod_temp[where(indexes >= percentile(indexes, 10))[0][0]])
        # yticks_mod.append(yticks_mod_temp[where(indexes >= percentile(indexes, 60))[0][0]])
        yticks_mod.append(yticks_mod_temp[where(indexes >= percentile(indexes, 55))[0][0]])

    return yticks_mod

def insert_axis_info_pvalue_vs_pvalue(df, mymin_x_values_on_axis, mymin_y_values_on_axis,
                                                      mymin_x_line, mymin_y_line_lower,
                                                      subplots_list, color='silver', label=None, resize=True,
                                                      yticks_mod=[]):

    x_value = pow(10, (log10(mymin_x_line) - log10(mymin_x_values_on_axis)) / 2. + log10(mymin_x_values_on_axis))
    y_value = pow(10, (log10(mymin_y_line_lower) - log10(mymin_y_values_on_axis)) / 2. + log10(mymin_y_values_on_axis))

    df_exvivo_nafilled = df[df.columns.values[0]].fillna(x_value)
    df_stim_nafilled = df[df.columns.values[1]].fillna(y_value)

    df = concat([df_exvivo_nafilled, df_stim_nafilled], axis=1)

    myfake_min=min(mymin_x_values_on_axis, mymin_y_values_on_axis)
    myfake_max=1e-2

    myfake_x_value = pow(10, (log10(myfake_max) - log10(myfake_min))/2. + log10(myfake_min))
    myfake_y_value = myfake_x_value

    # df[df.columns.values[0]].iloc[where(df[df.columns.values[0]] == 0)[0]] = mymin_x_values_on_axis
    # df[df.columns.values[1]].iloc[where(df[df.columns.values[1]] == 0)[0]] = mymin_y_values_on_axis

    counts_freq = Counter(zip(df[df.columns.values[0]], df[df.columns.values[1]]))
    points = counts_freq.keys()

    x, y = zip(*points)

    x = array(x)
    y = array(y)

    mymax_y_value = max(y)
    mymax_x_value = max(x)

    myargs = []

    if len(yticks_mod) > 0:
        yticks_mod = yticks_mod
    else:
        yticks_mod = []

    for subplot_index in range(len(subplots_list)):

        mysubplot = subplots_list[subplot_index]

        # top left
        if subplot_index == 0:
            xlim=[mymin_x_values_on_axis, mymin_x_line]
            ylim=[mymin_y_line_lower, mymax_y_value]
            spines_to_set_to_invisible=["bottom", "right"]

        # top right
        if subplot_index == 1:
            xlim=[mymin_x_line, mymax_x_value]
            ylim=[mymin_y_line_lower, mymax_y_value]
            spines_to_set_to_invisible=["bottom", "left"]

        # bottom left
        if subplot_index == 2:
            xlim = [mymin_x_values_on_axis, mymin_x_line]
            ylim = [mymin_y_values_on_axis, mymin_y_line_lower]
            spines_to_set_to_invisible = ["top", "right"]

        # bottom right
        if subplot_index == 3:
            xlim = [mymin_x_line, mymax_x_value]
            ylim = [mymin_y_values_on_axis, mymin_y_line_lower]
            spines_to_set_to_invisible = ["top", "left"]

        if resize:
            set_limits(mysubplot, xlim, ylim)

        x_index_mod = where((x >= xlim[0]) & (x <= xlim[1]))[0]
        y_index_mod = where((y >= ylim[0]) & (y <= ylim[1]))[0]

        intersect_index_mod = intersect1d(x_index_mod, y_index_mod)

        if len(intersect_index_mod) > 0:
            if subplot_index in [0, 2]:
                x_values = [myfake_x_value] * len(intersect_index_mod)

                if subplot_index == 2:
                    y_values = [myfake_y_value] * len(intersect_index_mod)

                    if resize:
                        set_limits(mysubplot, [myfake_min, myfake_max], [myfake_min, myfake_max])
                        # print("[xlim, ylim]: ", [mysubplot.get_xlim(), mysubplot.get_ylim()])
                else:
                    y_values = list(Series(y).iloc[intersect_index_mod])

                    if resize:
                        set_limits(mysubplot, [myfake_min, myfake_max], ylim)

                scat = mysubplot.scatter(x_values, y_values, facecolors=color,
                                         s=array(Series(map(sqrt, Series(list(counts_freq.values())).iloc[
                                             intersect_index_mod])) + 30),
                                         marker='o', linewidths=0.5, edgecolor='w', label=label, clip_on=False)
            elif subplot_index == 3:
                if resize:
                    set_limits(mysubplot, xlim, [myfake_min, myfake_max])

                scat = mysubplot.scatter(list(Series(x).iloc[intersect_index_mod]),
                                         [myfake_y_value] * len(intersect_index_mod),
                                         facecolors=color, s=array(
                        Series(map(sqrt, Series(list(counts_freq.values())).iloc[intersect_index_mod])) + 30),
                                         marker='o', linewidths=0.5, edgecolor='w', label=label, clip_on=False)

            else:
                if resize:
                    set_limits(mysubplot, xlim, ylim)

                array_seq=array(Series(map(sqrt, Series(list(counts_freq.values())).iloc[intersect_index_mod])) + 30)
                my_x=Series(x).iloc[intersect_index_mod]
                my_y=Series(y).iloc[intersect_index_mod]
                scat = mysubplot.scatter(my_x, my_y,
                                         facecolors=color,
                                         s=array_seq,
                                         marker='o', linewidths=0.5, edgecolor='w', label=label, clip_on=False)

            mysubplot, myargs = set_logscale_manage_spine(subplot_index, mysubplot, spines_to_set_to_invisible,
                                                          len(subplots_list), myargs)
        else:
            if resize:
                if subplot_index in [0, 2, 4]:
                    if subplot_index == 4:
                        set_limits(mysubplot, [myfake_min, myfake_max], [myfake_min, myfake_max])
                        # print("[xlim, ylim]: ", [mysubplot.get_xlim(), mysubplot.get_ylim()])
                    else:
                        set_limits(mysubplot, [myfake_min, myfake_max], ylim)
                elif subplot_index == 5:
                    set_limits(mysubplot, xlim, [myfake_min, myfake_max])
                else:
                    set_limits(mysubplot, xlim, ylim)

            myfakex = (xlim[1] - xlim[0]) / 2. + xlim[0]
            myfakey = (ylim[1] - ylim[0]) / 2. + ylim[0]

            myfakex2 = (xlim[1] - xlim[0]) / 3. + xlim[0]
            myfakey2 = (ylim[1] - ylim[0]) / 3. + ylim[0]

            scat = mysubplot.scatter([myfakex, myfakex2], [myfakey, myfakey2], alpha=0)

            mysubplot, myargs = set_logscale_manage_spine(subplot_index, mysubplot, spines_to_set_to_invisible,
                                                          len(subplots_list), myargs)

        mysubplot, myargs = set_logscale_manage_spine(subplot_index, mysubplot, spines_to_set_to_invisible, len(subplots_list), myargs)

        for tick in mysubplot.get_xticklabels():
            tick.set_rotation(45)

        for tick in mysubplot.xaxis.get_major_ticks():
            tick.label.set_fontsize(15)
        for tick in mysubplot.yaxis.get_major_ticks():
            tick.label.set_fontsize(15)

    return scat, subplots_list, (mymin_x_values_on_axis, max(x)), (mymin_y_values_on_axis, max(y)), yticks_mod



def insert_axis_info_relevantpept_compared_to_negctrl(df, df_tet_pval, mymax_x_value, mymax_y_value,
                                                      mymin_x_values_on_axis, mymin_y_values_on_axis,
                                                      mymin_x_line, mymin_y_line_upper, mymin_y_line_lower,
                                                      #mymax_x_line, mymax_y_line,
                                                      subplots_list, color='silver', label=None, resize=True,
                                                      yticks_mod=[],step=1):

    df = concat([df, df_tet_pval])

    x_value = pow(10, (log10(mymin_x_line) - log10(mymin_x_values_on_axis)) / 2. + log10(mymin_x_values_on_axis))
    y_value = pow(10, (log10(mymin_y_line_lower) - log10(mymin_y_values_on_axis)) / 2. + log10(mymin_y_values_on_axis))

    myfake_min=min(mymin_x_values_on_axis, mymin_y_values_on_axis)
    myfake_max=1e-2

    myfake_x_value = pow(10, (log10(myfake_max) - log10(myfake_min))/2. + log10(myfake_min))
    myfake_y_value = myfake_x_value

    df[df.columns.values[0]].iloc[where(df[df.columns.values[0]] == 0)[0]] = x_value
    df[df.columns.values[1]].iloc[where(df[df.columns.values[1]] == 0)[0]] = y_value

    # print("df 2: ", df)
    # df = concat([df_x_zero_conv, df_y_zero_conv], axis=1)

    counts_freq = Counter(zip(df[df.columns.values[0]], df[df.columns.values[1]]))
    points = counts_freq.keys()

    print("keys: ", points[1:5])

    x, y = zip(*points)

    x = array(x)



    y = array(y)

    df_tet_pval[df_tet_pval.columns.values[0]].iloc[where(df_tet_pval[df_tet_pval.columns.values[0]] == 0)[0]] = x_value
    df_tet_pval[df_tet_pval.columns.values[1]].iloc[where(df_tet_pval[df_tet_pval.columns.values[1]] == 0)[0]] = y_value

    counts_freq_tet = Counter(zip(df_tet_pval[df_tet_pval.columns.values[0]], df_tet_pval[df_tet_pval.columns.values[1]]))
    points_tet = counts_freq_tet.keys()

    mycolors=[]

    tups1=zip(points)
    tups2=zip(points_tet)


    comp1=[[list(myx)[0][0], list(myx)[0][1]] for myx in tups1]
    comp2=[[list(myx)[0][0], list(myx)[0][1]] for myx in tups2]



    # print(comp1)
    # print(comp2)

    for tup in comp1:
        if tup in comp2:
            mycolors.append(color[1])
        else:
            mycolors.append(color[0])

    # print("# elt in list: ", len(comp1))
    # print("# dots: ", len(mycolors))

    myargs = []

    if len(yticks_mod) > 0:
        yticks_mod = yticks_mod
    else:
        yticks_mod = []

    mylimits=[]

    for subplot_index in arange(0, len(subplots_list)):

        mysubplot = subplots_list[subplot_index]

        # top left
        if subplot_index == 0:
            xlim = [mymin_x_values_on_axis, mymin_x_line]
            ylim = [mymin_y_line_upper, mymax_y_value]
            spines_to_set_to_invisible = ["top", "bottom", "right"]

            # print("[xlim, ylim]: ", [xlim, ylim])

        # top center
        # if subplot_index == 1:
        #     xlim = [mymin_x_values_on_axis, mymin_x_line]
        #     ylim = [mymin_y_line, mymax_y_value]
        #     spines_to_set_to_invisible = ["left", "bottom", "right"]

        # top right
        if subplot_index == 1:
            xlim = [mymin_x_line, mymax_x_value]
            ylim = [mymin_y_line_upper, mymax_y_value]
            spines_to_set_to_invisible = ["top", "bottom", "left"]

        if len(subplots_list) == 6:

            # # center left
            # if subplot_index == 3:
            #     xlim = [mymin_x_values_on_axis, mymin_x_line]
            #     ylim = [mymin_y_values_on_axis, mymin_y_line]
            #     spines_to_set_to_invisible = ["top", "right", "bottom"]
            #
            # # center center
            # if subplot_index == 4:
            #     xlim = [mymin_x_values_on_axis, mymin_x_line]
            #     ylim = [mymin_y_values_on_axis, mymin_y_line]
            #     spines_to_set_to_invisible = ["top", "left", "right", "bottom"]
            #
            # # center right
            # if subplot_index == 5:
            #     xlim = [mymin_x_values_on_axis, mymin_x_line]
            #     ylim = [mymin_y_values_on_axis, mymin_y_line]
            #     spines_to_set_to_invisible = ["top", "left", "bottom"]

            # center left
            if subplot_index == 2:
                xlim = [mymin_x_values_on_axis, mymin_x_line]
                ylim = [mymin_y_line_lower, mymin_y_line_upper]

                # range_val = mymin_y_line_upper - mymin_y_line_lower
                # distance = range_val / 3
                # yticks_mod=[mymin_y_line_lower, mymin_y_line_lower + distance, mymin_y_line_upper]

                spines_to_set_to_invisible = ["top", "right", "bottom"]

            # center right
            if subplot_index == 3:
                xlim = [mymin_x_values_on_axis, mymax_x_value]
                ylim = [mymin_y_line_lower, mymin_y_line_upper]

                # range_val = mymin_y_line_upper - mymin_y_line_lower
                # distance = range_val / 3
                # yticks_mod = [mymin_y_line_lower, mymin_y_line_lower + distance, mymin_y_line_upper]

                spines_to_set_to_invisible = ["top", "left", "bottom"]

            # bottom left
            if subplot_index == 4:
                xlim = [mymin_x_values_on_axis, mymin_x_line]
                ylim = [mymin_y_values_on_axis, mymin_y_line_lower]
                spines_to_set_to_invisible = ["top", "right"]

            # bottom center
            # if subplot_index == 7:
            #     xlim = [mymin_x_values_on_axis, mymin_x_line]
            #     ylim = [mymin_y_values_on_axis, mymin_y_line]
            #     spines_to_set_to_invisible = ["top", "left", "right"]

            # bottom right
            if subplot_index == 5:
                xlim = [mymin_x_line, mymax_x_value]
                ylim = [mymin_y_values_on_axis, mymin_y_line_lower]
                spines_to_set_to_invisible = ["top", "left"]
        # else:
        #     # bottom left
        #     if subplot_index == 2:
        #         xlim = [mymin_x_values_on_axis, mymin_x_line]
        #         ylim = [mymin_y_values_on_axis, mymin_y_line_lower]
        #         spines_to_set_to_invisible = ["top", "right"]
        #
        #     # bottom right
        #     if subplot_index == 3:
        #         xlim = [mymin_x_line, mymax_x_value]
        #         ylim = [mymin_y_values_on_axis, mymin_y_line_lower]
        #         spines_to_set_to_invisible = ["top", "left"]

        if subplot_index in [3, 2, 4, 5]:
            y_index_mod = where((y >= ylim[0]) & (y < ylim[1]))[0]
        # elif subplot_index in [4, 5]:
        #     y_index_mod = where(y < ylim[1])[0]
        else:
            y_index_mod = where((y >= ylim[0]) & (y <= ylim[1]))[0]

        if subplot_index in [1, 3, 5]:
            x_index_mod = where((x >= xlim[0]) & (x <= xlim[1]))[0]
        # elif subplot_index in [0, 2, 4]:
        #     x_index_mod = where(x < xlim[1])[0]
        else:
            x_index_mod = where((x >= xlim[0]) & (x < xlim[1]))[0]

        intersect_index_mod = intersect1d(x_index_mod, y_index_mod)

        # print("spines to set invisible: ", spines_to_set_to_invisible)
        # print("intersect_index_mod: ", intersect_index_mod)

        if len(intersect_index_mod) > 0:
            if subplot_index in [0, 2, 4]:
                x_values = [myfake_x_value] * len(intersect_index_mod)

                if subplot_index == 4:
                    y_values= [myfake_y_value] * len(intersect_index_mod)

                    if resize:
                        set_limits(mysubplot, [myfake_min,myfake_max], [myfake_min,myfake_max])
                        # print("[xlim, ylim]: ", [mysubplot.get_xlim(), mysubplot.get_ylim()])
                else:
                    y_values = list(Series(y).iloc[intersect_index_mod])

                    if resize:
                        set_limits(mysubplot, [myfake_min, myfake_max], ylim)

                # if subplot_index == 0:
                #     print("x_values: ", x_values)
                #     print("y_values: ", y_values)
                #     print("subplot 0: ", [[myfake_min, myfake_max], ylim])

                # x_value =mymin_x_values_on_axis

                # print("myxvalues: ", x_value)
                # print("mymin_x_values_on_axis: ", mymin_x_values_on_axis)
                # print("mymin_x_line: ", mymin_x_line)
                #
                # print("-- log 10 --")
                #
                # print("myxvalues: ", log10(x_value))
                # print("mymin_x_values_on_axis: ", log10(mymin_x_values_on_axis))
                # print("mymin_x_line: ", log10(mymin_x_line))
                #
                # print([x_value] * len(intersect_index_mod))
                # print(Series(x).iloc[intersect_index_mod])

                scat = mysubplot.scatter(x_values, y_values, facecolors=Series(mycolors).iloc[intersect_index_mod],
                              s=array(Series(map(sqrt, Series(list(counts_freq.values())).iloc[intersect_index_mod]))+ 30),
                              marker='o', linewidths=0.5, edgecolor='w', label=label, clip_on=False)

            elif subplot_index == 5:
                if resize:
                    set_limits(mysubplot, xlim, [myfake_min, myfake_max])

                scat = mysubplot.scatter(list(Series(x).iloc[intersect_index_mod]), [myfake_y_value] * len(intersect_index_mod),
                                         facecolors=Series(mycolors).iloc[intersect_index_mod], s=array(Series( map(sqrt, Series(list(counts_freq.values())).iloc[intersect_index_mod])) + 30),
                                         marker='o', linewidths=0.5, edgecolor='w', label=label, clip_on=False)
            else:
                if resize:
                    set_limits(mysubplot, xlim, ylim)

                scat = mysubplot.scatter(list(Series(x).iloc[intersect_index_mod]), list(Series(y).iloc[intersect_index_mod]), facecolors=Series(mycolors).iloc[intersect_index_mod],
                              s=array(Series(map(sqrt, Series(list(counts_freq.values())).iloc[intersect_index_mod])) + 30),
                              marker='o', linewidths=0.5, edgecolor='w', label=label, clip_on=False)

            mysubplot, myargs = set_logscale_manage_spine(subplot_index, mysubplot, spines_to_set_to_invisible, len(subplots_list), myargs)
        else:
            if resize:
                if subplot_index in [0, 2, 4]:
                    if subplot_index == 4:
                        set_limits(mysubplot, [myfake_min,myfake_max], [myfake_min,myfake_max])
                        # print("[xlim, ylim]: ", [mysubplot.get_xlim(), mysubplot.get_ylim()])
                    else:
                        set_limits(mysubplot, [myfake_min, myfake_max], ylim)
                elif subplot_index == 5:
                    set_limits(mysubplot, xlim, [myfake_min, myfake_max])
                else:
                    set_limits(mysubplot, xlim, ylim)

            myfakex = (xlim[1] - xlim[0])/2. + xlim[0]
            myfakey = (ylim[1] - ylim[0]) / 2. + ylim[0]

            myfakex2 = (xlim[1] - xlim[0])/3. + xlim[0]
            myfakey2 = (ylim[1] - ylim[0]) / 3. + ylim[0]

            scat = mysubplot.scatter([myfakex, myfakex2], [myfakey, myfakey2], alpha=0)

            mysubplot, myargs = set_logscale_manage_spine(subplot_index, mysubplot, spines_to_set_to_invisible, len(subplots_list), myargs)

            # print("get_yticks_mod(mysubplot): ", get_yticks_mod(mysubplot))
            #
            # if subplot_index == 3:
            #     yticks_mod = get_yticks_mod(mysubplot)

    #     if (len(intersect_index_mod) > 0) & (len(yticks_mod) == 0):
    #         if subplot_index == 3:
    #             yticks_mod = get_yticks_mod(mysubplot, ylim)
    #
    # if len(yticks_mod) > 0:
    #     # print("yticks: ", yticks_mod)
    #     subplots_list[3].yaxis.set_ticks(yticks_mod)
    #     subplots_list[2].yaxis.set_ticks(yticks_mod)

        mylimits.append([xlim,ylim])

        for tick in mysubplot.get_xticklabels():
            tick.set_rotation(45)

        for tick in mysubplot.xaxis.get_major_ticks():
            tick.label.set_fontsize(15)
        for tick in mysubplot.yaxis.get_major_ticks():
            tick.label.set_fontsize(15)

        print("subplot_index: ", subplot_index)
        print("[xlim, x_value, ylim, y_value]: ", [xlim, x_value, ylim, y_value])

    return scat, subplots_list, mylimits, myfake_x_value, [myfake_min, myfake_max], (mymin_x_values_on_axis, max(x)), (mymin_y_values_on_axis, max(y)), yticks_mod

def insert_axis_info_frequencies_compared_to_exvivo(df, exp_df, mymin_exvivo, mymin_invitro,
                                                    mymin_x_line, mymin_y_line, subplots_list,
                                                    color='silver', label=None, resize=True):



    x_value = pow(10, (log10(mymin_x_line) - log10(mymin_exvivo)) / 2. + log10(mymin_exvivo))
    y_value = pow(10, (log10(mymin_y_line) - log10(mymin_invitro)) / 2. + log10(mymin_invitro))

    myfake_min = min(mymin_exvivo, mymin_invitro)
    myfake_max = 1e-2

    myfake_x_value = pow(10, (log10(myfake_max) - log10(myfake_min)) / 2. + log10(myfake_min))
    myfake_y_value = myfake_x_value

    df_exvivo_nafilled = df[df.columns.values[0]].fillna(x_value)
    df_stim_nafilled = df[df.columns.values[1]].fillna(y_value)

    df = concat([df_exvivo_nafilled, df_stim_nafilled], axis=1)

    exp_df_exvivo_nafilled = exp_df[exp_df.columns.values[0]].fillna(x_value)
    exp_df_stim_nafilled = exp_df[exp_df.columns.values[1]].fillna(y_value)

    exp_df = concat([exp_df_exvivo_nafilled, exp_df_stim_nafilled], axis=1)

    # print(exp_df)

    counts_freq = Counter(zip(df[df.columns.values[0]], df[df.columns.values[1]]))
    points = counts_freq.keys()

    # print('counts_freq',counts_freq)

    x1, y1 = zip(*points)
    # print('x1', x1)
    x2 = array(x1)

    y2 = array(y1)

    counts_freq_exp = Counter(zip(exp_df[exp_df.columns.values[0]], exp_df[exp_df.columns.values[1]]))

    points_exp = counts_freq_exp.keys()

    mycolors = []

    tups1 = zip(points)
    tups2 = zip(points_exp)

    comp1 = [[list(x)[0][0], list(x)[0][1]] for x in tups1]
    comp2 = [[list(x)[0][0], list(x)[0][1]] for x in tups2]

    for tup in comp1:
        if tup in comp2:
            mycolors.append(color[1])
        else:
            mycolors.append(color[0])

    mymax_invitro = max(y2)
    mymax_exvivo = max(x2)

    # print(x2)
    # print('mymax_exvivo: ', mymax_exvivo)

    myargs = []

    # print([mymin_exvivo,mymax_exvivo, mymin_x_line, mymin_y_line, mymin_invitro, mymax_invitro])
    for subplot_index in range(len(subplots_list)):
        mysubplot = subplots_list[subplot_index]

        # top left
        if subplot_index == 0:
            xlim = [mymin_exvivo, mymin_x_line]
            ylim = [mymin_y_line, mymax_invitro]
            spines_to_set_to_invisible = ["bottom", "right"]

        # top right
        if subplot_index == 1:
            xlim = [mymin_x_line, mymax_exvivo]
            ylim = [mymin_y_line, mymax_invitro]
            spines_to_set_to_invisible = ["bottom", "left"]

        # bottom left
        if subplot_index == 2:
            xlim = [mymin_exvivo, mymin_x_line]
            ylim = [mymin_invitro, mymin_y_line]
            spines_to_set_to_invisible = ["top", "right"]

        # bottom right
        if subplot_index == 3:
            xlim = [mymin_x_line, mymax_exvivo]
            ylim = [mymin_invitro, mymin_y_line]
            spines_to_set_to_invisible = ["top", "left"]

        # print([xlim, ylim])

        if resize:
            set_limits(mysubplot, xlim, ylim)

        x_index_mod = where((x2 >= xlim[0]) & (x2 <= xlim[1]))[0]
        y_index_mod = where((y2 >= ylim[0]) & (y2 <= ylim[1]))[0]

        intersect_index_mod = intersect1d(x_index_mod, y_index_mod)

        if len(intersect_index_mod) > 0:
            if subplot_index in [0, 2]:
                x_values = [myfake_x_value] * len(intersect_index_mod)

                if subplot_index == 2:
                    y_values = [myfake_y_value] * len(intersect_index_mod)

                    if resize:
                        set_limits(mysubplot, [myfake_min, myfake_max], [myfake_min, myfake_max])
                        # print("[xlim, ylim]: ", [mysubplot.get_xlim(), mysubplot.get_ylim()])
                else:
                    y_values = list(Series(y2).iloc[intersect_index_mod])

                    if resize:
                        set_limits(mysubplot, [myfake_min, myfake_max], ylim)

                scat = mysubplot.scatter(x_values, y_values, facecolors=Series(mycolors).iloc[intersect_index_mod],
                                         s=array(Series(map(sqrt, Series(list(counts_freq.values())).iloc[
                                             intersect_index_mod])) + 30),
                                         marker='o', linewidths=0.5, edgecolor='w', label=label, clip_on=False)
            elif subplot_index == 3:
                if resize:
                    set_limits(mysubplot, xlim, [myfake_min, myfake_max])

                scat = mysubplot.scatter(list(Series(x2).iloc[intersect_index_mod]),
                                         [myfake_y_value] * len(intersect_index_mod),
                                         facecolors=Series(mycolors).iloc[intersect_index_mod], s=array(
                        Series(map(sqrt, Series(list(counts_freq.values())).iloc[intersect_index_mod])) + 30),
                                         marker='o', linewidths=0.5, edgecolor='w', label=label, clip_on=False)

            else:
                if resize:
                    set_limits(mysubplot, xlim, ylim)

                scat = mysubplot.scatter(Series(x2).iloc[intersect_index_mod], Series(y2).iloc[intersect_index_mod],
                                         facecolors=Series(mycolors).iloc[intersect_index_mod],
                                         s=array(Series(map(sqrt, Series(list(counts_freq.values())).iloc[
                                             intersect_index_mod])) + 30),
                                         marker='o', linewidths=0.5, edgecolor='w', label=label, clip_on=False)

            mysubplot, myargs = set_logscale_manage_spine(subplot_index, mysubplot, spines_to_set_to_invisible,
                                                          len(subplots_list), myargs)
        else:
            if resize:
                if subplot_index in [0, 2, 4]:
                    if subplot_index == 4:
                        set_limits(mysubplot, [myfake_min, myfake_max], [myfake_min, myfake_max])
                        # print("[xlim, ylim]: ", [mysubplot.get_xlim(), mysubplot.get_ylim()])
                    else:
                        set_limits(mysubplot, [myfake_min, myfake_max], ylim)
                elif subplot_index == 5:
                    set_limits(mysubplot, xlim, [myfake_min, myfake_max])
                else:
                    set_limits(mysubplot, xlim, ylim)

            myfakex = (xlim[1] - xlim[0]) / 2. + xlim[0]
            myfakey = (ylim[1] - ylim[0]) / 2. + ylim[0]

            myfakex2 = (xlim[1] - xlim[0]) / 3. + xlim[0]
            myfakey2 = (ylim[1] - ylim[0]) / 3. + ylim[0]

            scat = mysubplot.scatter([myfakex, myfakex2], [myfakey, myfakey2], alpha=0)

            mysubplot, myargs = set_logscale_manage_spine(subplot_index, mysubplot, spines_to_set_to_invisible,
                                                          len(subplots_list), myargs)

        # for tick in mysubplot.get_xticklabels():
        #     tick.set_rotation(45)

        for tick in mysubplot.xaxis.get_major_ticks():
            tick.label.set_fontsize(15)
        for tick in mysubplot.yaxis.get_major_ticks():
            tick.label.set_fontsize(15)

    return scat, subplots_list, (mymin_exvivo, max(x2)), (mymin_invitro, max(y2))

def bonferroni_calculation(samples, clonotype_level='nucleotide', alpha=0.05):
    print("---- Bonferroni correction threshold calculation -----")
    exvivo = samples.get_exvivo()[0]
    #print(exvivo)
    #print(exvivo.nt_clonotypes)
    parameters_for_sample_selection = {'experiment_type_excluded':['exvivo']}
    selected_samples = samples.select(parameters_for_sample_selection)

    my_bonf_dict = {}
    if clonotype_level =='nucleotide':
        #exvivo_clonotypes = exvivo.get_nt_clonotypes_with_min_cells(1).clonotype_index
        exvivo_clonotypes = exvivo.nt_clonotypes.clonotype_index
        for sample in selected_samples:
            sample_clonotypes = sample.get_nt_clonotypes_with_min_cells(1).clonotype_index
            intersect = len(intersect1d(sample_clonotypes, exvivo_clonotypes))
            bonf = alpha/intersect
            my_bonf_dict[sample.ID] = bonf
    else:
        #exvivo_clonotypes = exvivo.get_aa_clonotypes_with_min_cells(1).aa_clonotype_ids
        exvivo_clonotypes = exvivo.aa_clonotypes.aa_clonotype_ids
        for sample in selected_samples:
            # print("bonferroni tetramer sample: ", sample)
            sample_clonotypes = sample.get_aa_clonotypes_with_min_cells(1).aa_clonotype_ids
            intersect = len(intersect1d(sample_clonotypes, exvivo_clonotypes))
            bonf = alpha/intersect
            my_bonf_dict[sample.ID] = bonf

    return my_bonf_dict

def plot_frequencies_compared_to_exvivo(output_path, samples, sample_id, clonotype_level='nucleotide', pvalue_threshold=0.001, bonferroni=True):
    print("plot_frequencies_compared_to_exvivo")

    exvivo = samples.get_exvivo()[0]

    # print('sample_id: ', sample_id)
    # print(samples)

    pep_stim = samples.get_samples_by_ids([sample_id])[0]

    exvivo_freq_df = exvivo.get_cell_counts_frequencies_by_clonotype_index()
    pep_stim_freq_df = pep_stim.get_cell_counts_frequencies_by_clonotype_index()

    # print(pep_stim)
    # print('pep_stim_freq_df: ', pep_stim_freq_df)

    # fig = plt.figure()

    #ax = plt.gca()

    df = concat([exvivo_freq_df, pep_stim_freq_df], axis=1)
    df.columns = [0, 1]

    #df = df.fillna(0)
    # print('bef: ', df)
    # print('pep_stim.pvalues: ', pep_stim.expansion_pvalues)

    index_mod = where((~isnan(array(df[df.columns.values[0]]))) | (~isnan(array(df[df.columns.values[1]]))))[0]

    df = df.iloc[index_mod]

    if bonferroni:
        pvalue_threshold = bonferroni_calculation(samples, clonotype_level=clonotype_level)[sample_id]

    exp_clonotype_ids = pep_stim.get_expanded_clonotypes_ids(threshold=pvalue_threshold)

    exp_exvivo_freq_df = exvivo_freq_df.ix[exp_clonotype_ids]
    exp_pep_stim_freq_df = pep_stim_freq_df.ix[exp_clonotype_ids]

    exp_df = concat([exp_exvivo_freq_df, exp_pep_stim_freq_df], axis=1)
    exp_df.columns = [0, 1]

    mymin_x_line = min(array(df[df.columns.values[0]].dropna().values)) * 0.9
    mymin_y_line = min(array(df[df.columns.values[1]].dropna().values)) * 0.9

    mymin_exvivo = min(array(df[df.columns.values[0]].dropna().values)) * 0.2
    mymin_invitro = min(array(df[df.columns.values[1]].dropna().values)) * 0.2

    label1='p-value $\geqslant$ {:.2e}'.format(pvalue_threshold) + ' (# = ' + str(len(df.index.values) - len(exp_df.index.values)) + ')'

    f, [[ax_up_left, ax2_up_right], [ax3_down_left, ax4_down_right]] = plt.subplots(2, 2, gridspec_kw = {'width_ratios':[1, 20], 'height_ratios':[20, 1]})#, sharex=True, sharey=True

    ledg1, subplots_list, var1, var2 = insert_axis_info_frequencies_compared_to_exvivo(df, exp_df, mymin_exvivo, mymin_invitro, mymin_x_line, mymin_y_line,
                                                                [ax_up_left, ax2_up_right, ax3_down_left, ax4_down_right],
                                                                color=['silver', 'k'], label=label1)

    label2='expanded with p-value < {:.2e}'.format(pvalue_threshold) +' (# = ' + str(len(exp_df.index.values)) + ') '

    sym1 = ax2_up_right.scatter([1, 2], [1, 2], marker='o', color='silver')
    sym2 = ax2_up_right.scatter([1, 2], [1, 2], marker='o', color='k')

    # legend = f.legend((sym1, sym2), ("tetramer+ from " + str(tetramer_sp[0] ).split(sep=",")[0], "tetramer-"), numpoints=1,
    #                              markerscale=2., bbox_to_anchor=(0, 1.02, 1, 0.2),
    #                              scatterpoints=1, fontsize=15, fancybox=True, shadow=False,
    #                              ncol=1, loc="upper center", mode="expand")

    legend = f.legend((sym1, sym2), (label1, label2), numpoints=1, markerscale=2., bbox_to_anchor=(0.5, 1),
                      scatterpoints=1, fontsize=15, loc='upper center', fancybox=True, shadow=False, ncol=1)

    legend.legendHandles[0]._sizes = [60]
    legend.legendHandles[1]._sizes = [60]






    f.text(0.5, 0.04, 'ex vivo', fontsize=25, style='italic', ha='center', va='center')
    f.text(0.025, 0.5, 'after peptide culture', fontsize=25, ha='center', va='center', rotation='vertical')

    f.subplots_adjust(hspace=0.09, wspace=0.09, left=0.15, bottom=0.15, top=0.85, right=0.85)

    f.savefig(output_path + sample_id + '_scatter_bc_ac_freq_' + clonotype_level + '.pdf', dpi=300, format='pdf')# , bbox_inches='tight'
    print(sample_id + '_scatter_bc_ac_freq_' + clonotype_level + '.pdf')

#write table with pvalues of any clonotypes with counts in either sample
def write_table(samplex, sampley, clonotype_level, output_path):
    sample_comparison_name = samplex.ID + '_vs_' + sampley.ID

    samples = ClonotypeSamples(samples=[samplex, sampley])

    if clonotype_level == 'nucleotide':
        clonotypeslist = samples.get_nt_clonotypesList_with_min_cells(1)
    else:
        clonotypeslist = samples.get_aa_clonotypesList_with_min_cells(1)

    print("clonotypeslist: ", clonotypeslist)

    pvalue_df = clonotypeslist.get_pvalues_df()

    if clonotype_level == 'nucleotide':
        nucleotide_sequences = samples.get_nucleotide_sequences_df(clonotypeslist.get_nt_clonotype_index())
        df = concat([nucleotide_sequences, pvalue_df], axis=1)
        df.to_csv(output_path + sample_comparison_name + '_' + clonotype_level +'_clonotypes_with_counts_in_either_sample.csv', index=False)

    else:
        df = pvalue_df
        df.to_csv(output_path + sample_comparison_name + '_' + clonotype_level +'_clonotypes_with_counts_in_either_sample.csv')


def write_zero_counts_in_both_samples(exvivo, samples, sample_comparison_name, clonotype_level, output_path):
    #sample_comparison_name = samplex.ID + '_vs_' + sampley.ID

    # print(samplex.ID + '_vs_' + sampley.ID)

    if clonotype_level == 'nucleotide':
        clonotype_index = samples.get_nt_clonotypesList_with_min_cells(1).get_nt_clonotype_index()
        exvivo_clonotypes = exvivo.get_nt_clonotypes_with_min_cells(1)

        # print('clonotype_index: ', clonotype_index[0:15])
        # print('exvivo_clonotypes.clonotype_index: ', exvivo_clonotypes.clonotype_index[0:15])

        clonotype_in_exvivo_not_in_stim = setdiff1d(exvivo_clonotypes.clonotype_index, clonotype_index)
    else:
        aa_clonotype_ids = samples.get_aa_clonotypesList_with_min_cells(1).get_aa_clonotype_ids()
        exvivo_clonotypes = exvivo.get_aa_clonotypes_with_min_cells(1)

        # print('exvivo_clonotypes: ', exvivo_clonotypes.aa_clonotype_ids[1:15])
        # print('stim clonotype_ids: ', aa_clonotype_ids[1:15])

        clonotype_in_exvivo_not_in_stim = setdiff1d(exvivo_clonotypes.aa_clonotype_ids, aa_clonotype_ids)

    # print(clonotype_level, clonotypeslist)

    db_zero_occurrences = str(len(clonotype_in_exvivo_not_in_stim))

    fname = output_path + clonotype_level + '_zero_counts_in_both_samples.csv'

    if path.isfile(fname):
        df = read_csv(fname)

        num_row = df.shape[0]
        df.loc[num_row + 1] = [sample_comparison_name, db_zero_occurrences]
        df.to_csv(fname, index=False)

    else:
        df = DataFrame(columns=['comparison', 'occurrences of zero cell counts in both samples'])
        df.loc[0] = [sample_comparison_name, db_zero_occurrences]
        df.to_csv(fname, index=False)

    print("[comparison, occurrences of zero cell counts in both samples]", [sample_comparison_name, db_zero_occurrences])


def plot_comparison_btw_2_sp_pvalues_v1(paths, df, sample_comparison_name, clonotype_level = 'nucleotide', xlabel = "replicate 1", ylabel = "replicate 2"):
    output_path = paths["path_tables_and_figures_folder"]
    col0 = df[df.columns.values[0]]
    col1 = df[df.columns.values[1]]

    index_mod_col0_not_zero = where(~(col0 == 0))[0]
    index_mod_col1_not_zero = where(~(col1 == 0))[0]

    col0_not_zero = array(df[df.columns.values[0]].iloc[index_mod_col0_not_zero].dropna().values)
    col1_not_zero = array(df[df.columns.values[1]].iloc[index_mod_col1_not_zero].dropna().values)

    if len(col0_not_zero) > 0:
        mymin_x_line = min(col0_not_zero) * 0.9
    else:
        mymin_x_line = 1E-300 * 0.9

    # mymin_y_line_upper = 1e-12  # min(col1_not_zero) * 0.9
    if len(col1_not_zero) > 0:
        mymin_y_line_lower = min(col1_not_zero) * 0.9
    else:
        mymin_y_line_lower = 1E-300 * 0.9

    # percentileofscore(col1_not_zero, mymin_y_line_upper)
    # y_20pct = percentile(col1_not_zero, 20)

    if len(col0_not_zero) > 0:
        mymin_x_values_on_axis = min(col0_not_zero) * 0.6
    else:
        mymin_x_values_on_axis = 1E-300 * 0.6

    # mymin_y_line_upper = 1e-12  # min(col1_not_zero) * 0.9
    if len(col1_not_zero) > 0:
        mymin_y_values_on_axis = min(col1_not_zero) * 0.6
    else:
        mymin_y_values_on_axis = 1E-300 * 0.6

    f, axs = plt.subplots(2, 2, gridspec_kw={'width_ratios': [4, 96], 'height_ratios': [96, 4]})# , sharex=True, sharey=True

    [[ax_up_left, ax2_up_right], [ax3_center_left, ax4_center_right] ] = axs

    print("limits: ", [mymin_x_values_on_axis, mymin_y_values_on_axis, mymin_x_line, mymin_y_line_lower])

    ledg1, subplots_list, var1, var2, yticks_mod = insert_axis_info_pvalue_vs_pvalue(df,
                                                                                     mymin_x_values_on_axis,
                                                                                     mymin_y_values_on_axis,
                                                                                     mymin_x_line,
                                                                                     mymin_y_line_lower,
                                                                                     [ax_up_left,
                                                                                      ax2_up_right,
                                                                                      ax3_center_left,
                                                                                      ax4_center_right],
                                                                                     color='k')

    f.text(0.5, 0.04, xlabel, fontsize=25,  ha='center', va='center')#style='italic',
    f.text(0.025, 0.5, ylabel, fontsize=25, ha='center', va='center', rotation='vertical')

    f.subplots_adjust(hspace=0.09, wspace=0.09, left=0.17, bottom=0.21, top=0.95, right=0.85)

    plt.savefig(output_path + sample_comparison_name + '_scatter_bc_ac_pvalues_' + clonotype_level + '.pdf', format='pdf')
    print(sample_comparison_name + '_scatter_bc_ac_pvalues_' + clonotype_level + '.pdf')


def plot_comparison_btw_2_sp_pvalues(output_path, exvivo, samplex, sampley, clonotype_level='nucleotide', bonferroni=True,
                                     xlabel="replicate 1", ylabel="replicate 2", level_of_output_detail="basic"):
    print("plot_comparison_btw_2_sp_pvalues")

    subject_id = samplex.get_subject_ids()[0]

    if isinstance(samplex, ClonotypeSamples):
        samplex_ID = str(samplex.get_sample_ids())

    if isinstance(sampley, ClonotypeSamples):
        sampley_ID = str(sampley.get_sample_ids())

    if isinstance(samplex, ClonotypeSample):
        samplex_ID = samplex.ID
        samplex = ClonotypeSamples(samples=[samplex], comparisonDataSet=exvivo.comparisonDataSet)

    if isinstance(sampley, ClonotypeSample):
        sampley_ID = sampley.ID
        sampley = ClonotypeSamples(samples=[sampley], comparisonDataSet=exvivo.comparisonDataSet)

    sample_comparison_name = str(subject_id) + "_" + samplex_ID + '_vs_' + sampley_ID

    if (len(samplex) == 1) & (len(sampley) == 1):

        samples = ClonotypeSamples(samples=[samplex[0], sampley[0]])

        if level_of_output_detail == "detailed":
            write_table(samplex[0], sampley[0], clonotype_level, output_path)
            write_zero_counts_in_both_samples(exvivo, samples, sample_comparison_name, clonotype_level, output_path)

    if bonferroni:

        bonf_thresholds_repx = bonferroni_calculation(ClonotypeSamples(samples=list(concatenate([[exvivo], samplex])),
                                                                  comparisonDataSet=exvivo.comparisonDataSet),
                                                 clonotype_level=clonotype_level)

        bonf_thresholds_repy = bonferroni_calculation(ClonotypeSamples(samples=list(concatenate([[exvivo], sampley])),
                                                                  comparisonDataSet=exvivo.comparisonDataSet),
                                                 clonotype_level=clonotype_level)

        if clonotype_level == "amino acid":
            repx_exp = samplex.get_expanded_aa_clonotypesList_with_sample_specific_threshold(bonf_thresholds_repx).get_pvalues_df()
            repy_exp = sampley.get_expanded_aa_clonotypesList_with_sample_specific_threshold(bonf_thresholds_repy).get_pvalues_df()

            repx_clns_ids = samplex.get_aa_clonotype_ids_list()
            repy_clns_ids = sampley.get_aa_clonotype_ids_list()

        else:
            repx_exp = samplex.get_expanded_nt_clonotypesList_with_sample_specific_threshold(bonf_thresholds_repx).get_pvalues_df()
            repy_exp = sampley.get_expanded_nt_clonotypesList_with_sample_specific_threshold(bonf_thresholds_repy).get_pvalues_df()

        repx_repy_clns_ids = intersect1d(repx_clns_ids, repy_clns_ids)

        num_repx_intersect_repy_clns = len(repx_repy_clns_ids)

        df = assign_min_pvals_for_medium_and_peptstim(samplex, sampley, clonotype_level=clonotype_level)

        repx = df["x cultures"]
        repy = df["y cultures"]

        samplex_ID = xlabel
        sampley_ID = ylabel

    # print("repx: ", repx)
    # print("repy: ", repy)
    # print("repx_exp: ", repx_exp)
    # print("repy_exp: ", repy_exp)

    repx_exp = repx.ix[repx_exp.index]
    repy_exp = repy.ix[repy_exp.index]
    exp_df = DataFrame([repx_exp, repy_exp])

    if clonotype_level == "amino acid":
        clnslistx = samplex.get_aa_clonotypesList()
        clnslisty = sampley.get_aa_clonotypesList()
    else:
        clnslistx = samplex.get_nt_clonotypesList()
        clnslisty = sampley.get_nt_clonotypesList()

    spx_cell_count_df = samplex[0].get_cell_counts_df()
    spy_cell_count_df = sampley[0].get_cell_counts_df()

    # print("spx_cell_count_df: ", spx_cell_count_df)

    spx_spy_cell_count_df = concat([spx_cell_count_df, spy_cell_count_df],axis=1)
    # print("spx_spy_cell_count_df: ", spx_spy_cell_count_df)

    spx_spy_cell_count_df = spx_spy_cell_count_df.dropna()

    # spx_sorted_cell_count_df = spx_spy_cell_count_df.sort_values(spx_spy_cell_count_df.columns.value[0], axis=0, ascending=False)
    # spy_sorted_cell_count_df = spx_spy_cell_count_df.sort_values(spx_spy_cell_count_df.columns.value[1], axis=1, ascending=False)
    #
    # spx_sorted_cell_count_indexes = spx_sorted_cell_count_df.index.values[0:10]
    # spy_sorted_cell_count_indexes = spy_sorted_cell_count_df.index.values[0:10]
    #
    # print(spx_spy_cell_count_df.ix[spx_sorted_cell_count_indexes])

    cor_coef_not_exp_cells, pval_not_exp_cells = spearmanr(spx_spy_cell_count_df)

    print("spearmanr (shared cells) => " + samplex_ID + "_vs_" + sampley_ID + " shared expanded clonotypes: ", [cor_coef_not_exp_cells, pval_not_exp_cells])

    spx_exp_cell_count = clnslistx.get_total_cells_per_clonotypes(clonotype_ids=repx_exp.index.values,
                                                                      clonotype_level=clonotype_level)
    spy_exp_cell_count = clnslisty.get_total_cells_per_clonotypes(clonotype_ids=repy_exp.index.values,
                                                                      clonotype_level=clonotype_level)

    # print("clnslistx: ", clnslistx)
    # print("spx_exp_cell_count: ", spx_exp_cell_count)

    exp_df = exp_df.T.dropna()
    cor_coef, pval = spearmanr(exp_df)

    top_10_x= [None,None]
    top_10_y = [None, None]

    if exp_df.shape[0] > 10:
        exp_df = exp_df.sort_values(by=exp_df.columns.values[0], axis=0, ascending=False)
        top_10_x = spearmanr(exp_df.iloc[0:10])
        exp_df = exp_df.sort_values(by=exp_df.columns.values[1], axis=0, ascending=False)
        top_10_y = spearmanr(exp_df.iloc[0:10])

        print("top 10 x : ", top_10_x)
        print("top 10 y : ", top_10_y)

    # if isinstance(samplex, ClonotypeSample) & isinstance(sampley, ClonotypeSample):
    #     spx_overlap_cell_count = sum(samplex.get_cell_counts(clonotype_index=exp_df.index.values))
    #     spy_overlap_cell_count = sum(sampley.get_cell_counts(clonotype_index=exp_df.index.values))
    #
    #     spx_cell_count = samplex.get_total_cell_count()
    #     spx_cln_count = samplex.get_total_clonotype_count()
    #
    #     spy_cell_count = sampley.get_total_cell_count()
    #     spy_cln_count = sampley.get_total_clonotype_count()
    # else:

    spx_overlap_cell_count = clnslistx.get_total_cells_per_clonotypes(clonotype_ids=exp_df.index.values, clonotype_level=clonotype_level)
    spy_overlap_cell_count = clnslisty.get_total_cells_per_clonotypes(clonotype_ids=exp_df.index.values, clonotype_level=clonotype_level)

    # spx_overlap_cell_count = sum(samplex.get_cell_counts(clonotype_index=exp_df.index.values))
    # spy_overlap_cell_count = sum(sampley.get_cell_counts(clonotype_index=exp_df.index.values))

    # spx_cell_count = clnslistx.get_total_cells_per_clonotypes(clonotype_level=clonotype_level)
    spx_cln_count = samplex.get_total_clonotype_count_per_clonotypes(clonotype_level=clonotype_level)

    # spy_cell_count = clnslisty.get_total_cells_per_clonotypes(clonotype_level=clonotype_level)
    spy_cln_count = sampley.get_total_clonotype_count_per_clonotypes(clonotype_level=clonotype_level)

    print("spearmanr (expanded p-values) => " + samplex_ID + "_vs_" + sampley_ID + " shared expanded clonotypes: ", [cor_coef, pval])

    # exvivo_clonotype_ids = exvivo.get_clonotype_ids()

    sample_comparison_name = sample_comparison_name + "_" + samplex_ID + '_vs_' + sampley_ID

    df = concat([repx, repy], axis=1)
    df.columns = [0, 1]

    # print("df.index.values: ", df.index.values)
    # print("exvivo_clonotype_ids: ", exvivo_clonotype_ids)

    # clonotype_ids_to_add = setdiff1d(exvivo_clonotype_ids, df.index.values)
    # clonotype_ids_in_df = intersect1d(df.index.values, clonotype_ids_to_add)
    #
    # if len(clonotype_ids_in_df) > 0:
    #     df.ix[clonotype_ids_in_df] = nan

    # print("spy_cln_count: ", spy_cln_count)

    df = df.fillna(1)

    df = df.iloc[where(~((df[0] == 1) & (df[1] == 1)))[0]]

    print(spx_overlap_cell_count[0])

    print("sum(spx_overlap_cell_count): ", sum(spx_overlap_cell_count))
    print("sum(spy_overlap_cell_count): ", sum(spy_overlap_cell_count))
    print("sum(spx_exp_cell_count): ", sum(spx_exp_cell_count))
    print("sum(spy_exp_cell_count): ", sum(spy_exp_cell_count))

    correlation_infos = [cor_coef, pval, cor_coef_not_exp_cells, pval_not_exp_cells, len(exp_df.index.values),  len(repx_exp.index.values), len(repy_exp.index.values),
                         sum(spx_overlap_cell_count), sum(spy_overlap_cell_count), sum(spx_exp_cell_count), sum(spy_exp_cell_count),
                         sum(num_repx_intersect_repy_clns), sum(spx_cln_count), sum(spy_cln_count),
                         samplex[0].get_total_cell_count(),  sampley[0].get_total_cell_count(), top_10_x[0], top_10_x[1], top_10_y[0], top_10_y[1]]

    # print('correlation_infos: ', correlation_infos)

    # if level_of_output_detail == "detailed":
    plot_comparison_btw_2_sp_pvalues_v1(output_path, df, sample_comparison_name, clonotype_level=clonotype_level, xlabel=xlabel, ylabel=ylabel)

    return correlation_infos

def plot_frequencies_compared_to_exvivo_by_filename(paths, filename, sequence_level, pvalue_threshold=0.001, bonferroni=True, level_of_output_detail="detailed"):
    path_tables_and_figures_folder = paths["path_tables_and_figures_folder"]
    parameters_for_sample_selection = {'experiment_type_excluded':['exvivo']}

    if path.isfile(filename):
        df = read_csv(filename, header=None)

        compdataset = ComparisonDataSet(df, clonotype_samples_info_file=paths['path_raw_data_folder'] + 'metadata/sample_info.csv')
        samples = compdataset.samples

        selected_samples = samples.select(parameters_for_sample_selection)

        for sample_id in selected_samples.get_sample_ids():
            plot_frequencies_compared_to_exvivo(path_tables_and_figures_folder, samples, sample_id, clonotype_level=sequence_level,
                                                pvalue_threshold=pvalue_threshold, bonferroni=bonferroni)
    else:
        print('WARN: ' + filename + ' does not exists.')

def plot_comparison_btw_2_sp_pvalues_and_get_correlation_infos(path_tables_and_figures_folder, exvivo, samplex, sampley,
                                                               mylist_of_list, subject_id, comparison_type, sequence_level, bonferroni,
                                                               xlabel="replicate 1", ylabel="replicate 2", level_of_output_detail="basic"):
    # if isinstance(samplex, ClonotypeSamples) & isinstance(sampley, ClonotypeSamples):
    if isinstance(samplex, ClonotypeSample):
        samplex_id = samplex.ID
    else:
        samplex_id = samplex.get_sample_ids()

    if isinstance(sampley, ClonotypeSample):
        sampley_id = sampley.ID
    else:
        sampley_id = sampley.get_sample_ids()

    complete_infos = [comparison_type, subject_id, sequence_level, samplex_id, sampley_id]

    correlation_infos = plot_comparison_btw_2_sp_pvalues(
        path_tables_and_figures_folder, exvivo, samplex, sampley,
        clonotype_level=sequence_level, bonferroni=bonferroni, xlabel=xlabel, ylabel=ylabel, level_of_output_detail=level_of_output_detail)

    complete_infos.extend(correlation_infos)
    mylist_of_list.append(complete_infos)

    return mylist_of_list

def write_expanded_summary(paths, filename, sequence_level, bonferroni=True, level_of_output_detail="detailed"):
    path_tables_and_figures_folder = paths["path_tables_and_figures_folder"]
    if path.isfile(filename):
        df = read_csv(filename, header=None)

        compdataset = ComparisonDataSet(df, clonotype_samples_info_file=paths['path_raw_data_folder'] + 'metadata/sample_info.csv')
        samples = compdataset.samples

        subject_id = samples.get_subject_ids()[0]

        exvivo = samples.select({'experiment':['exvivo']})[0]

        pep_samples = samples.get_samples_by_experiment_types(['peptide culture'])

        bonf_thresholds = []
        exp_clns_list = []
        for sample in pep_samples:
            print("ID: ", sample.ID)

            if bonferroni:
                bonf_thresholds_rep = bonferroni_calculation(ClonotypeSamples(samples=list(concatenate([[exvivo], [sample]])),
                                                                          comparisonDataSet=exvivo.comparisonDataSet),
                                                                            clonotype_level=sequence_level)
                if sequence_level == "amino acid":
                    temp_sample = ClonotypeSamples(samples=[sample])
                    rep_exp = temp_sample.get_expanded_aa_clonotypesList_with_sample_specific_threshold(bonf_thresholds_rep).get_pvalues_df()

                bonf_thresholds.append(bonf_thresholds_rep)
                exp_clns_list.append(rep_exp)

        print("Bonferroni thresholds")
        print(bonf_thresholds)

        exp_df = concat(exp_clns_list, axis=1)

        clns_aa_ids = samples.get_aa_clonotype_ids_df().ix[exp_df.index.values]

        exp_df.index = clns_aa_ids
        exp_df.to_csv(path_tables_and_figures_folder + str(subject_id) + "_summary_expanded_pval_aa_clns.csv")

def compress(folder_path, zipfilename, logger=None):
    try:
        ziph = zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED)
        # ziph is zipfile handle
        for root, dirs, files in walk(folder_path):
            for file in files:
                ziph.write(path.join(root, file))
        if logger is not None:
            logger("'%s' created successfully." % zipfilename)
    except IOError as e:
        print(e)
    except OSError as e:
        print(e)
    except zipfile.BadZipfile as e:
        print(e)
    finally:
        ziph.close()

def venn_diagram(path_tables_and_figures_folder, filename, sequence_level, bonferroni=True, level_of_output_detail="detailed", overlap=3):
    if path.isfile(filename):
        df = read_csv(filename, header=None)

        compdataset = ComparisonDataSet(df)
        samples = compdataset.samples

        subject_id = samples.get_subject_ids()[0]

        exvivo = samples.select({'experiment':['exvivo']})[0]

        pep_samples = samples.get_samples_by_experiment_types(['peptide culture'])

        bonf_thresholds = []
        exp_clns_list = []
        for sample in pep_samples:
            print("ID: ", sample.ID)

            if bonferroni:
                bonf_thresholds_rep = bonferroni_calculation(ClonotypeSamples(samples=list(concatenate([[exvivo], [sample]])),
                                                                          comparisonDataSet=exvivo.comparisonDataSet),
                                                                            clonotype_level=sequence_level)
                if sequence_level == "amino acid":
                    temp_sample = ClonotypeSamples(samples=[sample])
                    rep_exp = temp_sample.get_expanded_aa_clonotypesList_with_sample_specific_threshold(bonf_thresholds_rep).get_pvalues_df()

                bonf_thresholds.append(bonf_thresholds_rep)
                exp_clns_list.append(rep_exp)

        print("Bonferroni thresholds")
        print(bonf_thresholds)

        clns_aa_ids = samples.get_aa_clonotype_ids_df()

        for sample_index1 in arange(0,len(samples)):
            mysample = samples[sample_index1]
            for sample_index2 in arange(sample_index1 + 1, len(samples), overlap):
                last_sample_index=sample_index2+3
                mysamples = samples[sample_index2:last_sample_index]
                venn.get_labels(concatenate([[mysample], mysamples]))


def gene_usage(path_tables_and_figures_folder, filename):
    if path.isfile(filename):
        df = read_csv(filename, header=None)

        compdataset = ComparisonDataSet(df)
        samples = compdataset.samples
        subject_id = samples.get_subject_ids()[0]
        clns_gene_stats_df, clns_gene_counts_df, cell_gene_stats_df, cell_gene_counts_df = samples.get_gene_usage_stats_clns_cells()

        corr_df = concat([clns_gene_stats_df, cell_gene_stats_df], axis = 0)
        counts_df = concat([clns_gene_counts_df, cell_gene_counts_df], axis=1)

        # print(path_tables_and_figures_folder)

        corr_df.to_csv(path_tables_and_figures_folder + str(subject_id) + "_gene_usage_stats.csv", index=False)
        counts_df.to_csv(path_tables_and_figures_folder + str(subject_id) + "_gene_usage_counts.csv")


def plot_comparison_btw_2_sp_pvalues_by_filename(paths, filename, sequence_level, bonferroni=True, level_of_output_detail="basic"):
    if path.isfile(filename):
        df = read_csv(filename, header=None)

        compdataset = ComparisonDataSet(df, clonotype_samples_info_file=paths['path_raw_data_folder'] + 'metadata/sample_info.csv')
        samples = compdataset.samples

        subject_id = samples.get_subject_ids()[0]

        exvivo = samples.select({'experiment':['exvivo']})[0]

        medium = samples.get_samples_by_experiment_types(['medium culture'])

        pepts = samples.get_peptide_sequences()

        print("pepts: ",pepts)
        # samples_pepts = samples.get_samples_by_peptide_sequences(pepts, selection="or")

        mylist_of_list = []
        if len(pepts) > 0:
            repeatList = samples.get_repeatsList()
            if repeatList is not None:
                for repeats in repeatList:
                    for index in range(len(repeats) - 1):
                        samplex = ClonotypeSamples(samples=[repeats[index]])
                        sampley = ClonotypeSamples(samples=[repeats[index + 1]])

                        mylist_of_list = plot_comparison_btw_2_sp_pvalues_and_get_correlation_infos(
                            paths, exvivo,
                            samplex, sampley,
                            mylist_of_list, subject_id, "replicate",
                            sequence_level, bonferroni,
                            xlabel="replicate 1", ylabel="replicate 2",
                            level_of_output_detail=level_of_output_detail)
            else:
                print('WARN: no repeats found.')
        else:
            print('WARN: need at least 1 peptide.')

        if len(pepts) == 1:
            samples_pept1 = samples.get_samples_by_peptide_sequences([pepts[0]])
            for samplex_index in arange(0, len(samples_pept1) - 1):
                samplex = samples_pept1[samplex_index]

                samplex = ClonotypeSamples(samples=[samplex])
                for sampley_index in arange(samplex_index + 1, len(samples_pept1)):
                    sampley = samples_pept1[sampley_index]
                    sampley = ClonotypeSamples(samples=[sampley])

                    mylist_of_list = plot_comparison_btw_2_sp_pvalues_and_get_correlation_infos(
                        paths, exvivo, samplex, sampley, mylist_of_list, subject_id, "peptide",
                        sequence_level, bonferroni, xlabel="pep-" + pepts[0][:3].upper(),
                        ylabel="pep-" + pepts[0][:3].upper(), level_of_output_detail=level_of_output_detail)

        if len(pepts) > 1:
            samples_pept1 = samples.get_samples_by_peptide_sequences([pepts[0]])
            samples_pept2 = samples.get_samples_by_peptide_sequences([pepts[1]])

            # print("[x, y] axis: ", pepts)

            for samplex in samples_pept1:
                samplex = ClonotypeSamples(samples=[samplex])
                for sampley in samples_pept2:
                    sampley = ClonotypeSamples(samples=[sampley])

                    mylist_of_list = plot_comparison_btw_2_sp_pvalues_and_get_correlation_infos(
                        paths, exvivo,
                        samplex, sampley,
                        mylist_of_list, subject_id, "peptide",
                        sequence_level, bonferroni,
                        xlabel="pep-" + pepts[0][:3].upper(), ylabel="pep-" + pepts[1][:3].upper()
                        , level_of_output_detail=level_of_output_detail)

            if medium is not None:
                for med1 in medium:
                    med1 = ClonotypeSamples(samples=[med1])
                    for med2 in medium:
                        med2 = ClonotypeSamples(samples=[med2])
                        if med1 != med2:
                            mylist_of_list = plot_comparison_btw_2_sp_pvalues_and_get_correlation_infos(
                                paths, exvivo,
                                med1, med2,
                                mylist_of_list, subject_id, "medium",
                                sequence_level, bonferroni,
                                xlabel="medium-1", ylabel="medium-2", level_of_output_detail=level_of_output_detail )


                for med in medium:
                    for pept in samples_pept1:

                        pept = ClonotypeSamples(samples=[pept])

                        mylist_of_list = plot_comparison_btw_2_sp_pvalues_and_get_correlation_infos(
                            paths, exvivo,
                            med, pept,
                            mylist_of_list, subject_id, "medium vs peptide culture",
                            sequence_level, bonferroni,
                            xlabel="medium", ylabel="pep-" + pepts[0][:3].upper(), level_of_output_detail=level_of_output_detail)

                    for pept in samples_pept2:

                        pept = ClonotypeSamples(samples=[pept])

                        mylist_of_list = plot_comparison_btw_2_sp_pvalues_and_get_correlation_infos(
                            paths, exvivo,
                            med, pept,
                            mylist_of_list, subject_id, "medium vs peptide culture",
                            sequence_level, bonferroni,
                            xlabel="medium", ylabel="pep-" + pepts[1][:3].upper(), level_of_output_detail=level_of_output_detail)

                mylist_of_list = plot_comparison_btw_2_sp_pvalues_and_get_correlation_infos(
                    paths, exvivo,
                    medium, samples_pept1,
                    mylist_of_list, subject_id, "medium vs peptide cultures",
                    sequence_level, bonferroni,
                    xlabel="medium cultures", ylabel="pep-" + pepts[0][:3].upper(), level_of_output_detail=level_of_output_detail)

                mylist_of_list = plot_comparison_btw_2_sp_pvalues_and_get_correlation_infos(
                    paths, exvivo,
                    medium, samples_pept2,
                    mylist_of_list, subject_id, "medium vs peptide cultures",
                    sequence_level, bonferroni,
                    xlabel="medium cultures", ylabel="pep-" + pepts[1][:3].upper(), level_of_output_detail=level_of_output_detail)

                for sample_pept2 in samples_pept2:
                    sample_pept2 = ClonotypeSamples(samples=[sample_pept2])
                    mylist_of_list = plot_comparison_btw_2_sp_pvalues_and_get_correlation_infos(
                        paths, exvivo,
                        medium, sample_pept2,
                        mylist_of_list, subject_id, "medium vs peptide culture",
                        sequence_level, bonferroni,
                        xlabel="medium cultures", ylabel="pep-" + pepts[1][:3].upper(), level_of_output_detail=level_of_output_detail)

                for sample_pept1 in samples_pept1:
                    sample_pept1 = ClonotypeSamples(samples=[sample_pept1])
                    mylist_of_list = plot_comparison_btw_2_sp_pvalues_and_get_correlation_infos(
                        paths, exvivo,
                        medium, sample_pept1,
                        mylist_of_list, subject_id, "medium vs peptide culture",
                        sequence_level, bonferroni,
                        xlabel="medium cultures", ylabel="pep-" + pepts[0][:3].upper(), level_of_output_detail=level_of_output_detail)

        print("mylist_of_list: ", mylist_of_list)

        if len(mylist_of_list) > 0:
            df = DataFrame(mylist_of_list)
            df.columns = ["comparison type", "donors","sequence_level", "samplex", "sampley", "correlation (exp shared clns)", "p-value (exp shared clns)",
                          "correlation cells (all shared clns)", "p-value cells (all shared clns)",
                          "# exp clns shared", "# spx exp clns", "# spy exp clns", "# cells exp shared spx",
                          "# cells exp shared spy", "# cells exp spx",
                          "# cells exp spy","# clns shared",  "# clns spx", "# clns spy", "total cells spx", "total cells spy", "correlation top 10 spx (exp shared clns)", "p-value top 10 spx (exp shared clns)", "correlation top 10 spy (exp shared clns)", "p-value top 10 spy (exp shared clns)"]
            # print(df)

            return df
        else:
            return None


    else:
        print('WARN: ' + filename + ' does not exists.')

def get_2by2_exvivo_table(tet_pval_exp_clonotype_ids, rel_pep_stim_exp_clonotype_ids, rel_pep_stim_not_exp_clonotype_ids, exvivo):
    tetp_rel_pep_stim_exp_cln_ids = intersect1d(tet_pval_exp_clonotype_ids, rel_pep_stim_exp_clonotype_ids)
    tetn_rel_pep_stim_exp_cln_ids = setdiff1d(rel_pep_stim_exp_clonotype_ids, tet_pval_exp_clonotype_ids)
    tetp_rel_pep_stim_not_exp_cln_ids = intersect1d(tet_pval_exp_clonotype_ids, rel_pep_stim_not_exp_clonotype_ids)
    tetn_rel_pep_stim_not_exp_cln_ids = setdiff1d(rel_pep_stim_not_exp_clonotype_ids, tet_pval_exp_clonotype_ids)

    tetp_rel_pep_stim_exp_cln_ids_exvivo_freq_by_clonotypes = exvivo.aa_clonotypes.get_cell_frequencies_by_aa_clonotype_index(tetp_rel_pep_stim_exp_cln_ids)
    tetp_rel_pep_stim_exp_cln_ids_exvivo_freq = sum(tetp_rel_pep_stim_exp_cln_ids_exvivo_freq_by_clonotypes)

    tetn_rel_pep_stim_exp_cln_ids_exvivo_freq_by_clonotypes = exvivo.aa_clonotypes.get_cell_frequencies_by_aa_clonotype_index(tetn_rel_pep_stim_exp_cln_ids)
    tetn_rel_pep_stim_exp_cln_ids_exvivo_freq = sum(tetn_rel_pep_stim_exp_cln_ids_exvivo_freq_by_clonotypes)

    tetp_rel_pep_stim_not_exp_cln_ids_exvivo_freq_by_clonotypes = exvivo.aa_clonotypes.get_cell_frequencies_by_aa_clonotype_index(tetp_rel_pep_stim_not_exp_cln_ids)
    tetp_rel_pep_stim_not_exp_cln_ids_exvivo_freq = sum(tetp_rel_pep_stim_not_exp_cln_ids_exvivo_freq_by_clonotypes)

    tetn_rel_pep_stim_not_exp_cln_ids_exvivo_freq_by_clonotypes = exvivo.aa_clonotypes.get_cell_frequencies_by_aa_clonotype_index(tetn_rel_pep_stim_not_exp_cln_ids)
    tetn_rel_pep_stim_not_exp_cln_ids_exvivo_freq = sum(tetn_rel_pep_stim_not_exp_cln_ids_exvivo_freq_by_clonotypes)

    # print(tetn_rel_pep_stim_not_exp_cln_ids_exvivo_freq_by_clonotypes)
    # print(type(tetn_rel_pep_stim_not_exp_cln_ids_exvivo_freq))

    # cell_count_exvivo=sum(exvivo.get_amino_acid_cell_counts())

    cell_count_exvivo = sum(exvivo.get_total_cell_count())

    freq_tab = [[tetp_rel_pep_stim_exp_cln_ids_exvivo_freq[0], tetp_rel_pep_stim_not_exp_cln_ids_exvivo_freq[0]],[tetn_rel_pep_stim_exp_cln_ids_exvivo_freq[0],tetn_rel_pep_stim_not_exp_cln_ids_exvivo_freq[0]]]
    count_tab = [[freq_tab[0][0]*cell_count_exvivo, freq_tab[0][1]*cell_count_exvivo],[freq_tab[1][0]*cell_count_exvivo,freq_tab[1][1]*cell_count_exvivo]]
    tetp_count = sum([freq_tab[0][0], freq_tab[0][1]])*cell_count_exvivo
    exp_count =sum([freq_tab[0][0], freq_tab[1][0]])*cell_count_exvivo
    cmp_tet_exp_count = [[tetp_count, exp_count],[cell_count_exvivo-tetp_count, cell_count_exvivo-exp_count]]

    df_freq = DataFrame(freq_tab, columns=["exp+", "exp-"], index=["tet+", "tet-"])
    df_count = DataFrame(count_tab, columns=["exp+", "exp-"], index=["tet+", "tet-"]).astype(int)
    df_cmp_tet_exp_count = DataFrame(cmp_tet_exp_count, columns=["tet", "exp"], index=["+", "-"]).astype(int)

    print("----")
    print("2 by 2 ex vivo frequency table")
    print(df_freq)
    print("2 by 2 ex vivo cell count table")
    print(df_count)
    print('Fisher test [OR, pval]: ', fisher_exact(count_tab))
    print("2 by 2 for comparison between tet+ and exp+ ex vivo cell count table")
    print(df_cmp_tet_exp_count)
    print('Fisher test [OR, pval]: ', fisher_exact(df_cmp_tet_exp_count))
    print("----")

def fp_interpretation(path_tables_and_figures_folder, exposed_super_confident_clonotypes_freq_by_clonotypes, tet_pval_exp_clonotype_ids, tetramer):
    not_overlapping_clonotype_ids = setdiff1d(exposed_super_confident_clonotypes_freq_by_clonotypes.index.values, tet_pval_exp_clonotype_ids)
    not_over_cln_ex_freq_df = exposed_super_confident_clonotypes_freq_by_clonotypes.ix[not_overlapping_clonotype_ids]

    overlapping_clonotype_ids = intersect1d(exposed_super_confident_clonotypes_freq_by_clonotypes.index.values, tet_pval_exp_clonotype_ids)
    over_cln_ex_freq_df = exposed_super_confident_clonotypes_freq_by_clonotypes.ix[overlapping_clonotype_ids]

    fig = plt.figure()
    ax = fig.add_subplot(111)

    #bp = not_over_cln_ex_freq_df.boxplot()
    data=[not_over_cln_ex_freq_df, over_cln_ex_freq_df]
    plt.boxplot(data)
    plt.xticks([1, 2], ['FP', 'TP'])

    x = random.normal(1, 0.04, size=len(not_over_cln_ex_freq_df.index))
    plt.plot(x, not_over_cln_ex_freq_df, 'r.', alpha=0.2)

    #bp = over_cln_ex_freq_df.boxplot()
    x = random.normal(2, 0.04, size=len(over_cln_ex_freq_df.index))
    plt.plot(x, over_cln_ex_freq_df, 'r.', alpha=0.2)

    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(20)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(20)

    ax.grid(color='gainsboro', linestyle='dashed')

    ax.set_yscale('log', basey=10)
    subject_id = tetramer.get_subject_ids()[0]
    plt.savefig(path_tables_and_figures_folder + str(subject_id) + '_bp_not_ov_exp_clns.pdf', format='pdf', bbox_inches='tight')

    r = robjects.r
    v1 = robjects.FloatVector(not_over_cln_ex_freq_df.values)
    v2 = robjects.FloatVector(over_cln_ex_freq_df.values)
    wilcox_result =  r['wilcox.test'](v1, v2)
    print("Wilcox test p-value = {:.2e}".format(wilcox_result[2][0])) # the p-value

def cut_the_cake(df_before_selection, irrelevant_cult_exp_threshold, relevant_cult_exp_threshold, exvivo,
                 tet_pval_exp_clonotype_index, cell_count_exvivo, tetp_cell_count, total_exvivo_tetp_freq_by_clonotypes, inclusion=False,
                 verbose=False):

    if inclusion:
        df_after_selection = df_before_selection.iloc[where((df_before_selection["irrelevant"] >= irrelevant_cult_exp_threshold)
                                        & (df_before_selection["relevant"] <= relevant_cult_exp_threshold))[0]]
    else:
        df_after_selection = df_before_selection.iloc[where((df_before_selection["irrelevant"] > irrelevant_cult_exp_threshold)
                                        & (df_before_selection["relevant"] < relevant_cult_exp_threshold))[0]]

    # print("Thresholds [irrelevant, relevant]: ", [irrelevant_cult_exp_threshold, relevant_cult_exp_threshold])

    exposed_super_confident_clonotypes_freq_by_clonotypes = exvivo.aa_clonotypes.get_cell_frequencies_by_aa_clonotype_index(clonotype_index=df_after_selection.index.values)
    exposed_super_confident_clonotypes = sum(exposed_super_confident_clonotypes_freq_by_clonotypes)
    exposed_super_confident_clonotypes_cell_count = exposed_super_confident_clonotypes*cell_count_exvivo

    before_freq_by_clonotypes = exvivo.aa_clonotypes.get_cell_frequencies_by_aa_clonotype_index(clonotype_index=df_before_selection.index.values)
    before_clonotypes = sum(before_freq_by_clonotypes)
    before_cell_count = before_clonotypes * cell_count_exvivo

    if len(df_after_selection) > 0:
        # print("df_after_selection: ", df_after_selection.head(5))

        intersecting_cln_index= intersect1d(tet_pval_exp_clonotype_index, df_after_selection.index.values)
        overlap=len(intersecting_cln_index)

        notoverlap_cln_ids = setdiff1d(tet_pval_exp_clonotype_index, intersecting_cln_index)
        # exvivo_freq_by_clonotypes = exvivo.aa_clonotypes.get_cell_frequencies_by_aa_clonotype_ids(aa_clonotype_ids=notoverlap_cln_ids)

        print(notoverlap_cln_ids)
        print()

        exvivo_freq_by_clonotypes = exvivo.aa_clonotypes.get_cell_frequencies_by_aa_clonotype_index(notoverlap_cln_ids)

        tet_zeros_fn = len(where(exvivo_freq_by_clonotypes <= (2./cell_count_exvivo))[0])

        mylist=[int(overlap), int(len(tet_pval_exp_clonotype_index)), int(len(df_after_selection.index.values)),
                int(len(df_before_selection.index.values)),
                int((float(overlap)/len(tet_pval_exp_clonotype_index))*100.),
                int((float(overlap)/len(df_after_selection.index.values))*100.),
                tet_zeros_fn]

        #plot_comparison_negctrl_vs_pepstim_pvalues_final(path_tables_and_figures_folder, df_before_selection, tetramer, df_tet_pval, irrelevant_cult_exp_threshold, relevant_cult_exp_threshold)

        intersection_exvivo_cell_count = sum(exvivo.aa_clonotypes.get_cell_frequencies_by_aa_clonotype_index(clonotype_index=intersecting_cln_index))*cell_count_exvivo

        if exposed_super_confident_clonotypes_cell_count[0] > 0:
            pct_tep_exvivo = int((float(intersection_exvivo_cell_count[0])/tetp_cell_count[0])*100.)
        else:
            pct_tep_exvivo = 0

        if exposed_super_confident_clonotypes_cell_count[0] > 0:
            pct_exp_exvivo = int((float(intersection_exvivo_cell_count[0])/exposed_super_confident_clonotypes_cell_count[0])*100.)
        else:
            pct_exp_exvivo = 0

        mylist1=[int(intersection_exvivo_cell_count[0]), int(tetp_cell_count[0]), int(exposed_super_confident_clonotypes_cell_count[0]),
                 int(before_cell_count[0]),
                 pct_tep_exvivo, pct_exp_exvivo,
                 tet_zeros_fn]

        df_perf = DataFrame([mylist, mylist1], columns=["overlap", "tet", "exp", "pep stim", "%overlap with tet", "%overlap with exp", "tet less eq 2 cells FN"], index=["# clns","# exvivo cell count"])
    else:
        mylist=[0, 0, 0, 0, 0, 0, 0]
        df_perf = DataFrame([mylist, mylist],
                            columns=["overlap", "tet", "exp", "pep stim", "%overlap with tet", "%overlap with exp",
                                     "tet less eq 2 cells FN"], index=["# clns", "# exvivo cell count"])
    return df_perf

def get_pep_specificity_thresholds_to_test_by_subject(df_before_selection, tet_pval_exp_clonotype_index):
    tetp_clns_in_relev_pvalues = df_before_selection.ix[tet_pval_exp_clonotype_index]['relevant']
    tetp_clns_in_relev_pvalues = tetp_clns_in_relev_pvalues.dropna()
    tetp_clns_in_relev_pvalues.sort_values()

    irr_threshols=[]
    rel_threshols=[]

    # df_tet_pval_ids = tetramer.get_aa_clonotype_ids()
    # df_tet_pval = df_before_selection.ix[df_tet_pval_ids].fillna(1)
    #
    # print("pvalues tet df: ", df_tet_pval)
    # print("# clonotypes tet : ", len(df_tet_pval.index.values))

    # print("df_before_selection: ", df_before_selection)

    for tetp_cln_id in tetp_clns_in_relev_pvalues.index:

        # print("df_before_selection.ix[tetp_cln_id] : ", df_before_selection.ix[tetp_cln_id])

        irrelevant_cult_exp_threshold = df_before_selection.ix[tetp_cln_id].iloc[1]
        relevant_cult_exp_threshold = df_before_selection.ix[tetp_cln_id].iloc[0]

        irr_threshols.append(irrelevant_cult_exp_threshold)
        rel_threshols.append(relevant_cult_exp_threshold)

    threshold_df = concat([DataFrame(irr_threshols), DataFrame(rel_threshols)], axis=1)
    # print("threshold_df: ", threshold_df)

    threshold_df.columns = ["irrelevant", "relevant"]

    # print("threshold_df: ", threshold_df)

    return threshold_df


def determine_pep_specificity_thresholds_per_subject(df_before_selection, tet_pval_exp_clonotype_index, tetramer, exvivo, all_donor_thresholds_df):
    tetp_clns_in_relev_pvalues = df_before_selection.ix[tet_pval_exp_clonotype_index]["relevant"]
    tetp_clns_in_relev_pvalues = tetp_clns_in_relev_pvalues.dropna()
    tetp_clns_in_relev_pvalues.sort_values()

    # irrelevant_cult_exp_thresholds = df_before_selection.ix[tet_pval_exp_clonotype_index]["irrelevant"].drop_duplicates()
    # irrelevant_cult_exp_thresholds = irrelevant_cult_exp_thresholds.dropna()
    #
    # relevant_cult_exp_thresholds = df_before_selection.ix[tet_pval_exp_clonotype_index]["relevant"].drop_duplicates()
    # relevant_cult_exp_thresholds = relevant_cult_exp_thresholds.dropna()

    irr_thresholds = []
    rel_thresholds = []
    perfs = []

    total_exvivo_tetp_freq_by_clonotypes = exvivo.aa_clonotypes.get_cell_frequencies_by_aa_clonotype_index(clonotype_index=tet_pval_exp_clonotype_index)

    total_exvivo_tetp = sum(total_exvivo_tetp_freq_by_clonotypes)

    cell_count_exvivo = sum(exvivo.get_cell_counts_by_clonotype_index())
    tetp_cell_count = total_exvivo_tetp*cell_count_exvivo

    # irrelevant_cult_exp_thresholds = all_donor_thresholds_df["irrelevant"].drop_duplicates()
    # relevant_cult_exp_thresholds = all_donor_thresholds_df["relevant"].drop_duplicates()

    irrelevant_cult_exp_thresholds = all_donor_thresholds_df["irrelevant"]
    relevant_cult_exp_thresholds = all_donor_thresholds_df["relevant"]

    print("ex vivo freq for 2 cells: ", 2./cell_count_exvivo)

    # for threshold_irr in irrelevant_cult_exp_thresholds:
    for index in arange(len(irrelevant_cult_exp_thresholds)):
        threshold_irr = irrelevant_cult_exp_thresholds.iloc[index]
        thresholds_rel = relevant_cult_exp_thresholds.iloc[index]

        # for thresholds_rel in relevant_cult_exp_thresholds:
        # print("all_donor_thresholds_df.ix[thresholds_index] :", all_donor_thresholds_df.ix[thresholds_index])

        df_perf = cut_the_cake(df_before_selection, threshold_irr, thresholds_rel, exvivo,
                 tet_pval_exp_clonotype_index, cell_count_exvivo, tetp_cell_count, total_exvivo_tetp_freq_by_clonotypes, inclusion=True)

        irr_thresholds.append(threshold_irr)
        rel_thresholds.append(thresholds_rel)

        # print("perfs: ", df_perf)
        perfs.append(concatenate(df_perf.values.tolist()))

    df = concat([DataFrame(irr_thresholds), DataFrame(rel_thresholds), DataFrame(perfs)], axis=1)

    #df.columns = ["irrelevant", "relevant", "# clonotypes", "# exvivo cell count"]
    #"overlap (clns)", "tet (clns)", "exp (clns)", "%overlap with tet (clns)", "%overlap with exp (clns)", "overlap (cells)", "tet (cells)", "exp (cells)", "%overlap with tet (cells)", "%overlap with exp (cells)",

    df.columns = ["irrelevant", "relevant", "overlap (clns)", "tet (clns)", "exp (clns)", "pep stim (clns)",
                  "%overlap with tet (clns)", "%overlap with exp (clns)", "# clns tet less eq 2 cells FN",
                  "overlap (cells)", "tet (cells)",
                  "exp (cells)", "pep stim (cells)", "%overlap with tet (cells)", "%overlap with exp (cells)",
                  "# clns tet less eq 2 cells FN"]

    # print(df)

    sum_perf_clns = []
    sum_perf_exvivo = []
    prod_perf_clns = []
    prod_perf_exvivo = []
    for i in range(len(df.index)):
        sens_clns = df.iloc[i][6]
        sp_clns = df.iloc[i][7]

        sum_perf_clns.append(sum([sens_clns, sp_clns]))
        prod_perf_clns.append(prod([sens_clns, sp_clns]))

        sens_exvivo = df.iloc[i][13]
        sp_exvivo = df.iloc[i][14]

        sum_perf_exvivo.append(sum([sens_exvivo, sp_exvivo]))
        prod_perf_exvivo.append(prod([sens_exvivo, sp_exvivo]))

    summary_ranking_tab_df = concat([df, DataFrame(sum_perf_clns), DataFrame(sum_perf_exvivo), DataFrame(prod_perf_clns), DataFrame(prod_perf_exvivo)], axis=1)
    summary_ranking_tab_df.columns = concatenate([df.columns.values, ["sum perf clns", "sum perf ex vivo", "prod perf clns", "prod perf ex vivo"]])

    summary_ranking_tab_df.sort_values("sum perf ex vivo", ascending=False, inplace=True)
    summary_ranking_tab_df.sort_values("sum perf clns", ascending=False, inplace=True)

    return summary_ranking_tab_df

def auc_analysis(path_tables_and_figures_folder, all_donor_all_clns_data_for_auc):
    all_donor_all_clns_data_for_auc_df = concat([all_donor_all_clns_data_for_auc[0], all_donor_all_clns_data_for_auc[1]], axis=0)

    all_donor_all_clns_data_for_auc_df.to_csv(path_tables_and_figures_folder + "data_for_auc.csv")

    fpr, tpr, thresholds = roc_curve(array(all_donor_all_clns_data_for_auc_df["tetramer binding"]), array(all_donor_all_clns_data_for_auc_df["joint"]), pos_label=1)

    print("fpr, tpr, thresholds : ", [fpr, tpr, thresholds])

    roc_df = DataFrame([fpr, tpr, thresholds], index=["FP", "TP", "threshold"]).T
    roc_df.to_csv(path_tables_and_figures_folder + "roc_fp_tp_thres.csv")

    roc_auc = auc(fpr, tpr)
    color = "darkorange"
    lw=2
    fig = plt.figure()

    plt.plot(fpr, tpr, lw=lw, color=color, label='auc = %0.2f' % (roc_auc))

    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend(loc="lower right")

    plt.savefig(path_tables_and_figures_folder + 'auc_.pdf', format='pdf',  bbox_inches='tight')

def prepare_data_for_auc(df_before_selection, tet_pval_exp_clonotype_ids, subject_id, all_donor_all_clns_data_for_auc):
    joint_prob = []
    rel = df_before_selection['relevant']
    irrel = df_before_selection['irrelevant']

    for cln_id in df_before_selection.index:
        joint_prob.append((1.-rel.ix[cln_id])*irrel.ix[cln_id])

    #print("df_before_selection : ", df_before_selection)

    all_cln_ids = Series(0, index = df_before_selection.index)

    donors = Series(0, index = df_before_selection.index)

    #print("tet_pval_exp_clonotype_ids : ", tet_pval_exp_clonotype_ids)
    intersect_tet_ids = intersect1d(array(all_cln_ids.index.values), array(tet_pval_exp_clonotype_ids))
    #print("intersection tet_pval_exp_clonotype_ids : ", intersect1d(array(all_cln_ids.index.values), array(tet_pval_exp_clonotype_ids)))

    #print("all_cln_ids : ", all_cln_ids)

    all_cln_ids.ix[intersect_tet_ids] = 1

    donors.ix[donors.index.values] = subject_id

    data_for_auc_df = concat([DataFrame(donors),
            df_before_selection,
            DataFrame(joint_prob, index = df_before_selection.index.values),
            DataFrame(all_cln_ids)], axis=1)
    data_for_auc_df.columns = ["Donor", "relevant", "irrelevant", "joint", "tetramer binding" ]
    all_donor_all_clns_data_for_auc.append(data_for_auc_df.fillna(0))
    return all_donor_all_clns_data_for_auc


#Matthews correlation coefficient
def calculation_of_MCC(TP, TN, FP, FN):
    # TP=sum(TP)
    # TN=sum(TN)
    # FP=sum(FP)
    # FN=sum(FN)
    mcc= ((TP*TN)-(FP*FN)) / sqrt((TP+FP)*(TP+FN)*(TN+FP)*(TN+FN))
    return mcc

#Sp = TN / (TP + TN)
def calculation_of_Sp(TP, TN):
    Sp = float(TN) / (TP + TN)
    return Sp

#Sn = TP / (TP + FN)
def calculation_of_Sn(TP, FN):
    Sn = float(TP) / (TP + FN)
    return Sn

def partition_in_2_list(l):
    l1 = []
    l2 = []
    for i in range(len(l)):
        e = l[i]
        if i % 2 == 0:
            l1.append(e)
        else:
            l2.append(e)
    return [l1, l2]

def get_expanded_clonotypes_with_a_threshold(path_tables_and_figures_folder, processed_file_aa_pval_names, threshold_pval):
    for filename_aa in processed_file_aa_pval_names:
        if path.isfile(filename_aa):
            df = read_csv(filename_aa, header=None)

            compdataset = ComparisonDataSet(df)
            samples = compdataset.samples

            all_pept = samples.get_peptide_sequences()
            print(all_pept)
            subject_id = samples.get_subject_ids()[0]
            peptide_tp = "pk-megapool-11"
            peptide_fp ="tn-megapool-big"
            sp_with_pept_seq_tp = samples.get_samples_by_peptide_sequences([peptide_tp], selection="or")
            sp_with_pept_seq_fp = samples.get_samples_by_peptide_sequences([peptide_fp], selection="or")

            print("pvalue_thresholds: ", threshold_pval)

            # [exvivo, pept1_repeats, pept2_repeats] = prepare_samples_plot(samples)

            pept1_repeats_exp_clonotypeList = sp_with_pept_seq_tp.get_expanded_aa_clonotypesList_with_sample_a_specific_threshold(
                threshold_pval)
            pept2_repeats_exp_clonotypeList = sp_with_pept_seq_fp.get_expanded_aa_clonotypesList_with_sample_a_specific_threshold(
                threshold_pval)

            pept1_clns_ids = pept1_repeats_exp_clonotypeList.get_aa_clonotype_ids()
            pept2_clns_ids = pept2_repeats_exp_clonotypeList.get_aa_clonotype_ids()

            Positive_clonotypes_ids = list(set(pept1_clns_ids) - set(pept2_clns_ids))

            # pval_df = pept1_repeats_exp_clonotypeList.get_pvalues_df()
            pval_df = samples.get_pvalues_df()

            FP_index_loc = \
            where((pval_df[[0, 1]].min(axis=1) < threshold_pval) & (pval_df[[2, 3]].min(axis=1) < threshold_pval))[0]
            TP_index_loc = list(set(
                where((pval_df[[0, 1]].max(axis=1) < threshold_pval) | (pval_df[[2, 3]].max(axis=1) < threshold_pval))[
                    0]) - set(FP_index_loc))


            TP_clonotype_indexes = pval_df.index.values[TP_index_loc]

            TP_clns_ids = concatenate(samples.get_aa_clonotype_ids_df().ix[TP_clonotype_indexes].values.tolist())
            # print(TP_clns_ids)
            TP_PK_clns_ids = list(set(TP_clns_ids) & set(Positive_clonotypes_ids))

            cell_counts_df = samples.get_aa_clonotype_cell_count_df_by_samples()

            pvalue_df_cell_counts_merged_df = pval_df.merge(cell_counts_df, left_index=True, right_index=True)
            # print(pvalue_df_cell_counts_merged_df.head())
            # print("len pval_df.index.values: ", len(pval_df.index.values))
            # print(len(samples.get_aa_clonotype_ids_df()))

            clonotype_ids = samples.get_aa_clonotype_ids_df().ix[pval_df.index.values]
            # print(clonotype_ids.values.tolist()[1:10])
            pvalue_df_cell_counts_merged_df.index = concatenate(clonotype_ids.values.tolist())

            # print(pvalue_df_cell_counts_merged_df.head())
            pvalue_df_cell_counts_merged_df = pvalue_df_cell_counts_merged_df.ix[TP_PK_clns_ids]
            pvalue_df_cell_counts_merged_df.to_csv(path_tables_and_figures_folder + str(subject_id) + "_" + peptide_tp + "_pvalues_cell_counts_expanded_clonotypes.csv")


def provide_thresholds_negctrl(path_tables_and_figures_folder, filename_aa, pept_pool, bonferroni=True):
    if path.isfile(filename_aa):
        df = read_csv(filename_aa, header=None)

        compdataset = ComparisonDataSet(df)
        samples = compdataset.samples

        subject_id = samples.get_subject_ids()[0]

        [exvivo, pept1_repeats, pept2_repeats] = prepare_samples_plot(samples)

        if bonferroni:
            bonf_samples = []
            bonf_samples.extend(pept1_repeats)
            bonf_samples.extend(pept2_repeats)
            bonf_samples.append(exvivo)

            samples_to_process = ClonotypeSamples(samples=bonf_samples, comparisonDataSet=exvivo.comparisonDataSet)
            pvalue_thresholds = bonferroni_calculation(samples_to_process, clonotype_level="amino acid")

        print("pvalue_thresholds: ", pvalue_thresholds)

        pept1_repeats_exp_clonotypeList=pept1_repeats.get_expanded_aa_clonotypesList_with_sample_specific_threshold(pvalue_thresholds)
        pept2_repeats_exp_clonotypeList=pept2_repeats.get_expanded_aa_clonotypesList_with_sample_specific_threshold(pvalue_thresholds)

        pept1_clns_ids = pept1_repeats_exp_clonotypeList.get_aa_clonotype_ids()
        pept2_clns_ids = pept2_repeats_exp_clonotypeList.get_aa_clonotype_ids()

        if pept_pool == "TG":
            Positive_clonotypes_ids = list( set(pept2_clns_ids) - set(pept1_clns_ids) )

            print("Positive_clonotypes_ids: ",Positive_clonotypes_ids)
            print("# remove clonotypes: ", len(list(set(pept2_clns_ids) - set(Positive_clonotypes_ids))) )

            # pvalue_df=samples.get_aa_pvalues_df()
            # clnsList = samples.get_aa_clonotypesList()
            # pval_df = clnsList.get_pvalues_df()
            pval_df = pept2_repeats_exp_clonotypeList.get_pvalues_df()

            cell_counts_df = pept2_repeats.get_aa_clonotype_cell_count_df_with_aa_clonotype_ids_as_index_by_samples()
            pvalue_df_cell_counts_merged_df = pval_df.merge(cell_counts_df, left_index=True, right_index=True)

            clonotype_ids = pept2_repeats_exp_clonotypeList.get_aa_clonotype_ids_df_by_clonotype_index(pval_df.index.values)
            pvalue_df_cell_counts_merged_df.index = clonotype_ids
            pvalue_df_cell_counts_merged_df = pvalue_df_cell_counts_merged_df.ix[Positive_clonotypes_ids]
        else:


            Positive_clonotypes_ids = list(set(pept1_clns_ids) - set(pept2_clns_ids))

            print("Positive_clonotypes_ids: ", Positive_clonotypes_ids)
            print("# remove clonotypes: ", len(list(set(pept1_clns_ids) - set(Positive_clonotypes_ids))))

            pval_df = pept1_repeats_exp_clonotypeList.get_pvalues_df()

            cell_counts_df = pept1_repeats.get_aa_clonotype_cell_count_df_with_aa_clonotype_ids_as_index_by_samples()
            pvalue_df_cell_counts_merged_df = pval_df.merge(cell_counts_df, left_index=True, right_index=True)

            clonotype_ids = pept1_repeats_exp_clonotypeList.get_aa_clonotype_ids_df_by_clonotype_index(
                pval_df.index.values)
            pvalue_df_cell_counts_merged_df.index = clonotype_ids
            pvalue_df_cell_counts_merged_df = pvalue_df_cell_counts_merged_df.ix[Positive_clonotypes_ids]

        print("cell_counts_df: ", cell_counts_df)
        pvalue_df_cell_counts_merged_df.to_csv(path_tables_and_figures_folder + str(subject_id) + "_" + pept_pool + "_pvalues_cell_counts_expanded_clonotypes.csv")

    return pvalue_df_cell_counts_merged_df


def provide_thresholds_DbPos(filename_aa, data_type, bonferroni=True):
    if path.isfile(filename_aa):
        df = read_csv(filename_aa, header=None)

        compdataset = ComparisonDataSet(df)
        samples = compdataset.samples

        subject_id = samples.get_subject_ids()[0]

        [exvivo, pept1_repeats, pept2_repeats] = prepare_samples_plot(samples)

        if bonferroni:
            bonf_samples = []
            bonf_samples.extend(pept1_repeats)
            bonf_samples.extend(pept2_repeats)
            bonf_samples.append(exvivo)

            samples_to_process = ClonotypeSamples(samples=bonf_samples, comparisonDataSet=exvivo.comparisonDataSet)
            pvalue_thresholds = bonferroni_calculation(samples_to_process, clonotype_level="amino acid")

        expanded_repeats1 = []
        expanded_repeats2 = []

        for repeat1 in pept1_repeats:
            exp_pval_rep1 = pvalue_thresholds[repeat1.ID]
            repeat1_exp = repeat1.get_expanded_aa_clonotypes(exp_pval_rep1)
            expanded_repeats1.append(repeat1_exp)

        for repeat2 in pept2_repeats:
            exp_pval_rep2 = pvalue_thresholds[repeat2.ID]
            repeat2_exp = repeat2.get_expanded_aa_clonotypes(exp_pval_rep2)
            expanded_repeats2.append(repeat2_exp)


        # expanded_repeats1 = pept1_repeats.get_expanded_aa_clonotypes(0.05)
        #
        # expanded_repeats2 = pept2_repeats.get_expanded_aa_clonotypes(0.05)
        #
        # FP = expanded_repeats1.get_expanded_aa_clonotypes().get_pvalues_df()
        # TP =

        DP_clns_ids = list(
            set(concatenate([repeat2_exp.aa_clonotype_ids, repeat1_exp.aa_clonotype_ids])))


        T1P1_samples = ClonotypeSamples(samples=[pept1_repeats[0], pept2_repeats[0]],
                                        comparisonDataSet=exvivo.comparisonDataSet)
        T1P2_samples = ClonotypeSamples(samples=[pept1_repeats[0], pept2_repeats[1]],
                                        comparisonDataSet=exvivo.comparisonDataSet)
        T2P2_samples = ClonotypeSamples(samples=[pept1_repeats[1], pept2_repeats[1]],
                                        comparisonDataSet=exvivo.comparisonDataSet)
        T2P1_samples = ClonotypeSamples(samples=[pept1_repeats[1], pept2_repeats[0]],
                                        comparisonDataSet=exvivo.comparisonDataSet)


        T1P1_samples_exp_clonotypeList = T1P1_samples.get_expanded_aa_clonotypesList_with_sample_specific_threshold(
            pvalue_thresholds)
        T1P2_samples_exp_clonotypeList = T1P2_samples.get_expanded_aa_clonotypesList_with_sample_specific_threshold(
            pvalue_thresholds)
        T2P2_samples_exp_clonotypeList = T2P2_samples.get_expanded_aa_clonotypesList_with_sample_specific_threshold(
            pvalue_thresholds)
        T2P1_samples_exp_clonotypeList = T2P1_samples.get_expanded_aa_clonotypesList_with_sample_specific_threshold(
            pvalue_thresholds)

        T1P1dp_clns_ids = T1P1_samples_exp_clonotypeList.get_aa_shared_clonotypes().aa_clonotype_ids
        T1P2dp_clns_ids = T1P2_samples_exp_clonotypeList.get_aa_shared_clonotypes().aa_clonotype_ids
        T2P2dp_clns_ids = T2P2_samples_exp_clonotypeList.get_aa_shared_clonotypes().aa_clonotype_ids
        T2P1dp_clns_ids = T2P1_samples_exp_clonotypeList.get_aa_shared_clonotypes().aa_clonotype_ids

        SP_clns_ids = list(set(concatenate([T1P1dp_clns_ids, T1P2dp_clns_ids, T2P2dp_clns_ids, T2P1dp_clns_ids])))

        # print("# DP: ",len(set(DP_clns_ids)))

        Positive_clonotypes_ids = list(set(DP_clns_ids) - set(SP_clns_ids))

        # print("# DP after removal of unspecific",len(set(Positive_clonotypes_ids)))

        total_samples = []
        total_samples.extend(pept1_repeats)
        total_samples.extend(pept2_repeats)

        total_samples = ClonotypeSamples(samples=total_samples, comparisonDataSet=exvivo.comparisonDataSet)
        total_counts_clonotype_ids = list(set(concatenate([repeat2.aa_clonotype_ids , repeat1.aa_clonotype_ids])))

        all_expanded_clonotypes_list = ClonotypesList(list_of_clonotypes=concatenate([expanded_repeats1, expanded_repeats2]))

        # print("all_expanded_clonotypes_list.get_pvalues_df: ", all_expanded_clonotypes_list.get_pvalues_df())

        pvalues_universe_to_explore = concatenate(all_expanded_clonotypes_list.get_pvalues_df().drop_duplicates().values.tolist())
        pvalues_universe_to_explore = [x for x in pvalues_universe_to_explore if x != 1]


        pvalues_universe_to_explore = [x for x in pvalues_universe_to_explore if not isnan(x) ]

        print("max pval: ", max(pvalues_universe_to_explore))
        print(pvalues_universe_to_explore)

        list_of_list_sp_unsp = []

        chunk = 100
        print('# of threshold to analysed: ', str(len(pvalues_universe_to_explore)))
        total_iter = ceil(len(pvalues_universe_to_explore) / float(chunk))

        j = 0
        for thres_pval in pvalues_universe_to_explore:
            if (j % chunk) == 0:
                print("Threshold performance progress: %d%% \r" % ((float(j) / total_iter) ))
                stdout.flush()

            j = j + 1

            pept1_repeats_exp_clonotypeList = pept1_repeats.get_expanded_aa_clonotypesList_with_sample_a_specific_threshold(
                thres_pval)

            pept2_repeats_exp_clonotypeList = pept2_repeats.get_expanded_aa_clonotypesList_with_sample_a_specific_threshold(
                thres_pval)

            T1P1_samples_exp_clonotypeList = T1P1_samples.get_expanded_aa_clonotypesList_with_sample_a_specific_threshold(
                thres_pval)
            T1P2_samples_exp_clonotypeList = T1P2_samples.get_expanded_aa_clonotypesList_with_sample_a_specific_threshold(
                thres_pval)
            T2P2_samples_exp_clonotypeList = T2P2_samples.get_expanded_aa_clonotypesList_with_sample_a_specific_threshold(
                thres_pval)
            T2P1_samples_exp_clonotypeList = T2P1_samples.get_expanded_aa_clonotypesList_with_sample_a_specific_threshold(
                thres_pval)

            P1P2dp_clns_ids = pept1_repeats_exp_clonotypeList.get_aa_shared_clonotypes().aa_clonotype_ids
            T1T2dp_clns_ids = pept2_repeats_exp_clonotypeList.get_aa_shared_clonotypes().aa_clonotype_ids
            T1P1dp_clns_ids = T1P1_samples_exp_clonotypeList.get_aa_shared_clonotypes().aa_clonotype_ids
            T1P2dp_clns_ids = T1P2_samples_exp_clonotypeList.get_aa_shared_clonotypes().aa_clonotype_ids
            T2P2dp_clns_ids = T2P2_samples_exp_clonotypeList.get_aa_shared_clonotypes().aa_clonotype_ids
            T2P1dp_clns_ids = T2P1_samples_exp_clonotypeList.get_aa_shared_clonotypes().aa_clonotype_ids

            DP = list(set(concatenate([P1P2dp_clns_ids, T1T2dp_clns_ids])))
            SP = list(set(concatenate([T1P1dp_clns_ids, T1P2dp_clns_ids, T2P2dp_clns_ids, T2P1dp_clns_ids])))

            TP = list(set(DP) - set(SP))

            clonotype_ids_to_remove = list(set(DP) - set(TP))

            # print("TP: ", TP)
            # print("Positive_clonotypes_ids: ", Positive_clonotypes_ids)

            FN = list(set(Positive_clonotypes_ids) - set(TP))
            # print(len(FN))
            # print(FN)
            FP = [] #they are removed from DP

            # print("total_counts_clonotype_ids", total_counts_clonotype_ids)

            Negatives = set(total_counts_clonotype_ids) - (set(TP).union(set(FP)))

            TN = list(Negatives - set(FN))
            # print("TN: ", TN)

            if data_type == "clonotypes":
                P1P2dp = len(P1P2dp_clns_ids)
                T1T2dp = len(T1T2dp_clns_ids)

                T1P1dp = len(T1P1dp_clns_ids)
                T1P2dp = len(T1P2dp_clns_ids)
                T2P2dp = len(T2P2dp_clns_ids)
                T2P1dp = len(T2P1dp_clns_ids)

            else:
                # print("started getting cell counts")
                # print("--- cell counts: %s ---" % asctime(localtime(time())))
                pept1_repeats_cell_counts = pept1_repeats_exp_clonotypeList.get_aa_shared_clonotypes().get_cell_counts().values.tolist()
                pept2_repeats_cell_counts = pept2_repeats_exp_clonotypeList.get_aa_shared_clonotypes().get_cell_counts().values.tolist()
                T1P1_cell_counts = T1P1_samples_exp_clonotypeList.get_aa_shared_clonotypes().get_cell_counts().values.tolist()
                T1P2_cell_counts = T1P2_samples_exp_clonotypeList.get_aa_shared_clonotypes().get_cell_counts().values.tolist()
                T2P2_cell_counts = T2P2_samples_exp_clonotypeList.get_aa_shared_clonotypes().get_cell_counts().values.tolist()
                T2P1_cell_counts = T2P1_samples_exp_clonotypeList.get_aa_shared_clonotypes().get_cell_counts().values.tolist()
                # print("--- finished: %s ---" % asctime(localtime(time())))
                # print("T2P1_cell_counts", T2P1_cell_counts)

                if len(pept1_repeats_cell_counts) > 0 :
                    P1P2dp = sum(concatenate(pept1_repeats_cell_counts))
                else:
                    P1P2dp = 0

                if len(pept2_repeats_cell_counts) > 0 :
                    T1T2dp = sum(concatenate(pept2_repeats_cell_counts))
                else:
                    T1T2dp = 0

                if len(T1P1_cell_counts) > 0 :
                    T1P1dp = sum(concatenate(T1P1_cell_counts))
                else:
                    T1P1dp = 0

                if len(T1P2_cell_counts) > 0 :
                    T1P2dp = sum(concatenate(T1P2_cell_counts))
                else:
                    T1P2dp = 0

                if len(T2P2_cell_counts) > 0 :
                    T2P2dp = sum(concatenate(T2P2_cell_counts))
                else:
                    T2P2dp = 0

                if len(T2P1_cell_counts)> 0 :
                    T2P1dp = sum(concatenate(T2P1_cell_counts))
                else:
                    T2P1dp = 0

            specific = P1P2dp + T1T2dp
            unspecific = T1P1dp + T1P2dp + T2P2dp + T2P1dp

            if data_type == "clonotypes":
                MCC = calculation_of_MCC(len(TP),len(TN),len(FP),len(FN))
                Sn = calculation_of_Sn(len(TP),len(FN))
                Sp = calculation_of_Sp(len(TP),len(TN))

                if (specific + unspecific) == 0:
                    perf = 0.
                else:
                    specific = specific - len(clonotype_ids_to_remove)
                    perf = float(specific) / (specific + unspecific)

                list_of_list_sp_unsp.append(
                    [subject_id, thres_pval, P1P2dp, T1T2dp, T1P1dp, T1P2dp, T2P2dp, T2P1dp, specific, unspecific, perf,
                     len(TP), len(TN), len(FP), len(FN), Sn, Sp, MCC])
            else:
                # print("--- cell count by clonotype ids: %s ---" % asctime(localtime(time())))

                FP_cell_count = total_samples.get_total_cell_count_for_aa_clonotype_ids(aa_clonotype_ids=FP)
                FN_cell_count = total_samples.get_total_cell_count_for_aa_clonotype_ids(aa_clonotype_ids=FN)
                # print("TP", TP)
                TP_cell_count = total_samples.get_total_cell_count_for_aa_clonotype_ids(aa_clonotype_ids=TP)
                # print("TP_cell_count", TP_cell_count)
                TN_cell_count = total_samples.get_total_cell_count_for_aa_clonotype_ids(aa_clonotype_ids=TN)

                # print("--- finished %s ---" % asctime(localtime(time())))

                MCC = calculation_of_MCC(TP_cell_count, TN_cell_count, FP_cell_count, FN_cell_count)
                Sn = calculation_of_Sn(TP_cell_count,FN_cell_count)
                Sp = calculation_of_Sp(TP_cell_count, TN_cell_count)

                if (specific + unspecific) == 0:
                    perf = 0.
                else:

                    cell_count_to_remove = total_samples.get_total_cell_count_for_aa_clonotype_ids(aa_clonotype_ids=clonotype_ids_to_remove)

                    specific_bef = specific

                    specific = specific - cell_count_to_remove

                    specific_aft = specific

                    if specific < 0:
                        print("Warning negative number of cells")
                        print("cell_count_to_remove:", cell_count_to_remove)
                        print("specific bef:", specific_bef)
                        print("specific after:", specific_aft)

                        print("# clonotype_ids_to_remove: ", len(clonotype_ids_to_remove))
                        print("clonotype_ids_to_remove: ", clonotype_ids_to_remove)

                        print("#TP: ", len(TP))
                        print("TP ids: ", TP)
                        print("#TP_cells: ", TP_cell_count)
                        print("DP: ", len(DP))


                    perf = float(specific) / (specific + unspecific)

                list_of_list_sp_unsp.append(
                    [subject_id, thres_pval, P1P2dp, T1T2dp, T1P1dp, T1P2dp, T2P2dp, T2P1dp, specific, unspecific, perf,
                     TP_cell_count, TN_cell_count, FP_cell_count, FN_cell_count, Sn, Sp, MCC])

        df_to_return = DataFrame(list_of_list_sp_unsp,columns=["subject_id", "threshold_pvalue", "P1P2", "T1T2", "T1P1", "T1P2", "T2P2", "T2P1", "specific", "unspecific", "performance", "TP", "TN", "FP", "FN", "Sn", "Sp", "MCC"])
        return df_to_return
    return None


def plot_mixed_pure_frequencies(output_path, processed_file_aa_pval_names):
    for filename_aa in processed_file_aa_pval_names:
        if path.isfile(filename_aa):
            df = read_csv(filename_aa, header=None)
            # threshold = 0.05
            threshold = 1.23E-88
            compdataset = ComparisonDataSet(df)
            samples = compdataset.samples

            subject_id = samples.get_subject_ids()[0]

            [exvivo, pept1_repeats, pept2_repeats] = prepare_samples_plot(samples)

            total_samples = []
            total_samples.extend(pept1_repeats)
            total_samples.extend(pept2_repeats)

            total_samples = ClonotypeSamples(samples=total_samples, comparisonDataSet=exvivo.comparisonDataSet)

            pk_clonotype_ids = concatenate(pept2_repeats.get_aa_clonotype_ids_df().values.tolist())
            tn_clonotype_ids = concatenate(pept1_repeats.get_aa_clonotype_ids_df().values.tolist())

            [exvivo, pept1_repeats, pept2_repeats] = prepare_samples_plot(samples)
            pept1_repeats_exp_clonotypeList = pept1_repeats.get_expanded_aa_clonotypesList_with_sample_a_specific_threshold(threshold)

            pept2_repeats_exp_clonotypeList = pept2_repeats.get_expanded_aa_clonotypesList_with_sample_a_specific_threshold(threshold)

            pept1_exp_pval_df = pept1_repeats_exp_clonotypeList.get_pvalues_df()
            pept2_exp_pval_df = pept2_repeats_exp_clonotypeList.get_pvalues_df()

            all_pept_df = pept1_exp_pval_df.merge(pept2_exp_pval_df, how="outer", left_index=True, right_index=True)

            all_pept_df = all_pept_df.fillna(1)

            FP_index_loc = where((all_pept_df[[0, 1]].min(axis=1) < threshold) & (all_pept_df[[2, 3]].min(axis=1) < threshold))[0]
            TP_index_loc = list(set(
                where((all_pept_df[[0, 1]].max(axis=1) < threshold) | (all_pept_df[[2, 3]].max(axis=1) < threshold))[0]) - set(
                FP_index_loc))

            FP_clonotype_indexes = all_pept_df.index.values[FP_index_loc]
            TP_clonotype_indexes = all_pept_df.index.values[TP_index_loc]

            if len(FP_clonotype_indexes) >0:
                FP_clns_ids = concatenate(total_samples.get_aa_clonotype_ids_df().ix[FP_clonotype_indexes].values.tolist())
            else:
                FP_clns_ids = None

            TP_clns_ids = concatenate(total_samples.get_aa_clonotype_ids_df().ix[TP_clonotype_indexes].values.tolist())

            pk_clns_ids = pept2_repeats_exp_clonotypeList.get_aa_clonotype_ids()
            tt_clns_ids = pept1_repeats_exp_clonotypeList.get_aa_clonotype_ids()

            # print(TP_clns_ids[1:10])
            # print(pk_clns_ids[1:10])

            tn_tp_clns_ids = list(set(TP_clns_ids) - set(pk_clns_ids))
            pk_tp_clns_ids = list(set(TP_clns_ids) - set(tt_clns_ids))

            if FP_clns_ids is not None:
                mixed_pval_df_complete = samples.get_pvalues_df()
                clonotype_ids = samples.get_aa_clonotype_ids_df().ix[mixed_pval_df_complete.index.values]
                mixed_pval_df_complete.index = concatenate(clonotype_ids.values.tolist())
                mixed_pval_df = mixed_pval_df_complete.ix[FP_clns_ids]

                min_pk_pval = mixed_pval_df[[0, 1]].min(axis=1)
                min_tt_pval = mixed_pval_df[[2, 3]].min(axis=1)

                mixture_df_pval = DataFrame([min_pk_pval,min_tt_pval]).T
                print(mixture_df_pval)
                sample_comparison_name = str(subject_id) + "_Mixed_" + str(threshold)
                plot_comparison_btw_2_sp_pvalues_v1(output_path, mixture_df_pval, sample_comparison_name, clonotype_level='amino acid',
                                                    xlabel="Min(PK1, PK2)", ylabel="Min(TT1, TT2)")

            pk_pval_df_complete = pept2_repeats.get_pvalues_df()
            clonotype_ids = pept2_repeats.get_aa_clonotype_ids_df().ix[pk_pval_df_complete.index.values]
            pk_pval_df_complete.index = concatenate(clonotype_ids.values.tolist())
            pk_pval_df = pk_pval_df_complete.ix[pk_tp_clns_ids]

            tn_pval_df_complete = pept1_repeats.get_pvalues_df()
            clonotype_ids = pept1_repeats.get_aa_clonotype_ids_df().ix[tn_pval_df_complete.index.values]
            tn_pval_df_complete.index = concatenate(clonotype_ids.values.tolist())
            tn_pval_df = tn_pval_df_complete.ix[tn_tp_clns_ids]

            sample_comparison_name = str(subject_id) + "_Pure_Parkinson_" + str(threshold)
            plot_comparison_btw_2_sp_pvalues_v1(output_path, pk_pval_df, sample_comparison_name, clonotype_level='amino acid',
                                                xlabel="PK1", ylabel="PK2")

            sample_comparison_name = str(subject_id) + "_Pure_Tetanus_" + str(threshold)
            plot_comparison_btw_2_sp_pvalues_v1(output_path, tn_pval_df, sample_comparison_name, clonotype_level='amino acid',
                                                xlabel="TT1", ylabel="TT2")
            # print(subject_id)
            # print(mixture_df_pval)
            # print(pk_pval_df)
            # print(tn_pval_df)

def provide_thresholds_DbPos_removing_mixed_clns(processed_file_aa_pval_names):
    all_donors_pvalues_universe_to_explore= []
    for filename_aa in processed_file_aa_pval_names:
        if path.isfile(filename_aa):
            df = read_csv(filename_aa, header=None)

            compdataset = ComparisonDataSet(df)
            samples = compdataset.samples

            [exvivo, pept1_repeats, pept2_repeats] = prepare_samples_plot(samples)

            # threshold = 1.23E-88
            threshold = 0.05
            expanded_repeats1 = pept1_repeats.get_expanded_aa_clonotypesList_with_sample_a_specific_threshold(threshold)
            expanded_repeats2 = pept2_repeats.get_expanded_aa_clonotypesList_with_sample_a_specific_threshold(threshold)

            pept1_exp_pval_df = expanded_repeats1.get_pvalues_df()
            pept2_exp_pval_df = expanded_repeats2.get_pvalues_df()

            all_pept_df = pept1_exp_pval_df.merge(pept2_exp_pval_df, how="outer", left_index=True, right_index=True)

            pvalues_universe_to_explore = concatenate(all_pept_df.drop_duplicates().values.tolist())
            pvalues_universe_to_explore = [x for x in pvalues_universe_to_explore if x != 1]
            pvalues_universe_to_explore = [x for x in pvalues_universe_to_explore if not isnan(x) ]

            all_donors_pvalues_universe_to_explore.extend(pvalues_universe_to_explore)

        all_donors_pvalues_universe_to_explore = list(set(all_donors_pvalues_universe_to_explore))
        print("max pval: ", max(all_donors_pvalues_universe_to_explore))
        print(all_donors_pvalues_universe_to_explore)

    # print(processed_file_aa_pval_names)
    final_df = None
    list_final_df = []
    for filename_aa in processed_file_aa_pval_names:
        if path.isfile(filename_aa):
            print("samples to process: ", filename_aa)
            df = read_csv(filename_aa, header=None)

            compdataset = ComparisonDataSet(df)
            samples = compdataset.samples

            subject_id = samples.get_subject_ids()[0]

            [exvivo, pept1_repeats, pept2_repeats] = prepare_samples_plot(samples)

            threshold = 0.05

            total_samples = []
            total_samples.extend(pept1_repeats)
            total_samples.extend(pept2_repeats)

            total_samples = ClonotypeSamples(samples=total_samples, comparisonDataSet=exvivo.comparisonDataSet)

            num_clns = len(total_samples.get_aa_clonotype_ids_df())
            print(total_samples.get_aa_clonotype_ids_df())
            list_of_list_sp_unsp = []

            chunk = 100
            print('# of threshold to analysed: ', str(len(all_donors_pvalues_universe_to_explore)))
            total_iter = ceil(len(all_donors_pvalues_universe_to_explore) / float(chunk))

            j = 0
            for thres_pval in all_donors_pvalues_universe_to_explore:
                if (j % chunk) == 0:
                    print("Threshold performance progress: %d%% \r" % ((float(j) / total_iter)))
                    stdout.flush()

                j = j + 1

                pept1_repeats_exp_clonotypeList = pept1_repeats.get_expanded_aa_clonotypesList_with_sample_a_specific_threshold(
                    thres_pval)

                pept2_repeats_exp_clonotypeList = pept2_repeats.get_expanded_aa_clonotypesList_with_sample_a_specific_threshold(
                    thres_pval)

                pept1_exp_pval_df = pept1_repeats_exp_clonotypeList.get_pvalues_df()
                pept2_exp_pval_df = pept2_repeats_exp_clonotypeList.get_pvalues_df()

                all_pept_df = pept1_exp_pval_df.merge(pept2_exp_pval_df, how="outer", left_index=True, right_index=True)

                all_pept_df = all_pept_df.fillna(1)

                FP_index_loc = where((all_pept_df[[0,1]].min(axis=1) < threshold) & (all_pept_df[[2,3]].min(axis=1) < threshold))[0]
                TP_index_loc = list(set(where((all_pept_df[[0,1]].max(axis=1) < threshold) | (all_pept_df[[2,3]].max(axis=1) < threshold))[0]) - set(FP_index_loc))

                FP_clonotype_indexes = all_pept_df.index.values[FP_index_loc]
                TP_clonotype_indexes = all_pept_df.index.values[TP_index_loc]

                FP_clns_ids = total_samples.get_aa_clonotype_ids_df().ix[FP_clonotype_indexes].values.tolist()
                TP_clns_ids = total_samples.get_aa_clonotype_ids_df().ix[TP_clonotype_indexes].values.tolist()

                # print(TP_clns_ids)

                FP_cell_count = total_samples.get_total_cell_count_for_aa_clonotype_ids(aa_clonotype_ids=FP_clns_ids)
                TP_cell_count = total_samples.get_total_cell_count_for_aa_clonotype_ids(aa_clonotype_ids=TP_clns_ids)

                # print(FP_cell_count)

                if (TP_cell_count + FP_cell_count) == 0:
                    perf_cell_counts = 0.
                    perf_clns = 0.
                    TN = num_clns - (len(TP_clns_ids) + len(FP_clns_ids))
                    MCC_clns = 0.
                else:
                    perf_cell_counts = float(TP_cell_count) / (TP_cell_count + FP_cell_count)
                    perf_clns = float(len(TP_clns_ids)) / (len(TP_clns_ids) + len(FP_clns_ids))
                    TN = num_clns - (len(TP_clns_ids) + len(FP_clns_ids))
                    FN = 0
                    MCC_clns = calculation_of_MCC(len(TP_clns_ids), TN, len(FP_clns_ids), FN) * 100

                list_of_list_sp_unsp.append(
                    [subject_id, thres_pval, len(TP_clns_ids), len(FP_clns_ids), perf_clns, MCC_clns, TP_cell_count, FP_cell_count, perf_cell_counts])

            df_to_return = DataFrame(list_of_list_sp_unsp,
                                     columns=["subject_id", "threshold_pvalue", "#TP clns", "#FP clns", "MCC clns", "performance clns", "#TP cells", "#FP cells", "performance cells"])

            if final_df is None:
                list_final_df.append(df_to_return)
                final_df = df_to_return
            else:
                list_final_df.append(df_to_return)
                final_df = final_df.merge(df_to_return, on='threshold_pvalue', how="outer")

    stacked_df = concat(list_final_df).reset_index(drop=True)

    return [final_df, stacked_df]


def mixed_pure_plot(path_tables_and_figures_folder, specific_unspecific_matrix_df, num_clones_values, yaxis_label, data_type, subject_id):
    f = plt.figure()
    ax = plt.gca()

    ax.set_xscale('log', basex=10)

    if data_type == "cells":
        p1 = ax.plot(specific_unspecific_matrix_df["threshold_pvalue"], specific_unspecific_matrix_df["#TP cells"],
                   color="green")

        # ax.scatter(specific_unspecific_matrix_df["threshold_pvalue"], specific_unspecific_matrix_df["specific"],
        #         color="green", marker='o', linewidths=0.5, edgecolor='w', clip_on=False)

        p2 = ax.plot(specific_unspecific_matrix_df["threshold_pvalue"], specific_unspecific_matrix_df["#FP cells"],
                   color="blue")
    else:
        p1 = ax.plot(specific_unspecific_matrix_df["threshold_pvalue"], specific_unspecific_matrix_df["#TP clns"],
                     color="green")

        # ax.scatter(specific_unspecific_matrix_df["threshold_pvalue"], specific_unspecific_matrix_df["specific"],
        #         color="green", marker='o', linewidths=0.5, edgecolor='w', clip_on=False)

        p2 = ax.plot(specific_unspecific_matrix_df["threshold_pvalue"], specific_unspecific_matrix_df["#FP clns"],
                     color="blue")


    # ax.scatter(specific_unspecific_matrix_df["threshold_pvalue"], specific_unspecific_matrix_df["unspecific"],
    #         color="blue", marker='o', linewidths=0.5, edgecolor='w', clip_on=False)

    ax.set_xlim((min(specific_unspecific_matrix_df["threshold_pvalue"]),
                 max(specific_unspecific_matrix_df["threshold_pvalue"])))
    ax.set_ylim((min(num_clones_values), max(num_clones_values)))

    ax.patch.set_facecolor('None')
    ax.grid(color='gainsboro', linestyle='dashed')

    for tick in ax.get_xticklabels():
        tick.set_rotation(45)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(20)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(20)

    plt.xlabel('Threshold p-values', fontsize=25)
    plt.ylabel(yaxis_label, fontsize=25)

    legend = ax.legend((p1,p2), ("Mixed", "Pure"), bbox_to_anchor=(0.5, 1),
                       fontsize=15, loc='upper center', fancybox=True, shadow=False, ncol=1)#bbox_to_anchor=(0.5, 1.2),

    plt.savefig(path_tables_and_figures_folder + str(subject_id) + '_' + data_type + '_dp_mixed_pure.pdf',
                format='pdf', bbox_inches='tight')


def specific_unspecific_plot(path_tables_and_figures_folder, specific_unspecific_matrix_df, num_clones_values, yaxis_label, data_type, subject_id):
    f = plt.figure()
    ax = plt.gca()

    ax.set_xscale('log', basex=10)

    p1 = ax.plot(specific_unspecific_matrix_df["threshold_pvalue"], specific_unspecific_matrix_df["specific"],
               color="green")

    # ax.scatter(specific_unspecific_matrix_df["threshold_pvalue"], specific_unspecific_matrix_df["specific"],
    #         color="green", marker='o', linewidths=0.5, edgecolor='w', clip_on=False)

    p2 = ax.plot(specific_unspecific_matrix_df["threshold_pvalue"], specific_unspecific_matrix_df["unspecific"],
               color="blue")

    # ax.scatter(specific_unspecific_matrix_df["threshold_pvalue"], specific_unspecific_matrix_df["unspecific"],
    #         color="blue", marker='o', linewidths=0.5, edgecolor='w', clip_on=False)

    ax.set_xlim((min(specific_unspecific_matrix_df["threshold_pvalue"]),
                 max(specific_unspecific_matrix_df["threshold_pvalue"])))
    ax.set_ylim((min(num_clones_values), max(num_clones_values)))

    ax.patch.set_facecolor('None')
    ax.grid(color='gainsboro', linestyle='dashed')

    for tick in ax.get_xticklabels():
        tick.set_rotation(45)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(20)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(20)

    plt.xlabel('Threshold p-values', fontsize=25)
    plt.ylabel(yaxis_label, fontsize=25)

    legend = ax.legend((p1,p2), ("unspecific", "specific"), bbox_to_anchor=(0.5, 1),
                       fontsize=15, loc='upper center', fancybox=True, shadow=False, ncol=1)#bbox_to_anchor=(0.5, 1.2),

    plt.savefig(path_tables_and_figures_folder + str(subject_id) + '_' + data_type + '_dp_specific_unspecific.pdf',
                format='pdf', bbox_inches='tight')

def pct_perf_plot(path_tables_and_figures_folder, specific_unspecific_matrix_df, data_type, subject_id):
    fig = plt.figure()
    ax = plt.gca()

    ax.set_xscale('log', basex=10)

    if data_type == "cells":
        mylist = specific_unspecific_matrix_df["performance cells"] * 100
    else:
        mylist = specific_unspecific_matrix_df["performance clns"] * 100

    ax.plot(specific_unspecific_matrix_df["threshold_pvalue"], mylist, color="green")
    ax.plot(specific_unspecific_matrix_df["threshold_pvalue"], specific_unspecific_matrix_df["MCC clns"]*100, color="red")

    # ax.plot(specific_unspecific_matrix_df["threshold_pvalue"], mylist,
    #         color="green", marker='o', linewidths=0.5, edgecolor='w', clip_on=False)

    ax.set_xlim((min(specific_unspecific_matrix_df["threshold_pvalue"]),
                 max(specific_unspecific_matrix_df["threshold_pvalue"])))
    ax.set_ylim(0, 100)

    ax.patch.set_facecolor('None')
    ax.grid(color='gainsboro', linestyle='dashed')

    for tick in ax.get_xticklabels():
        tick.set_rotation(45)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(20)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(20)

    plt.xlabel('Threshold p-values', fontsize=25)
    plt.ylabel("Performances (% specificity or MCC)", fontsize=25)

    plt.savefig(path_tables_and_figures_folder + str(subject_id) + '_' + data_type + '_dp_pct_perf.pdf', format='pdf',
                bbox_inches='tight')

def MCC_Sn_Sp_perf_plot(path_tables_and_figures_folder, specific_unspecific_matrix_df, data_type, subject_id):
    fig = plt.figure()
    ax = plt.gca()

    ax.set_xscale('log', basex=10)

    ax.plot(specific_unspecific_matrix_df["threshold_pvalue"], specific_unspecific_matrix_df["MCC"] * 100, color="green")
    ax.plot(specific_unspecific_matrix_df["threshold_pvalue"], specific_unspecific_matrix_df["Sn"] * 100, color="blue")
    ax.plot(specific_unspecific_matrix_df["threshold_pvalue"], specific_unspecific_matrix_df["Sp"] * 100, color="red")

    # ax.plot(specific_unspecific_matrix_df["threshold_pvalue"], mylist,
    #         color="green", marker='o', linewidths=0.5, edgecolor='w', clip_on=False)

    ax.set_xlim((min(specific_unspecific_matrix_df["threshold_pvalue"]),
                 max(specific_unspecific_matrix_df["threshold_pvalue"])))
    ax.set_ylim(0, 100)

    ax.patch.set_facecolor('None')
    ax.grid(color='gainsboro', linestyle='dashed')

    for tick in ax.get_xticklabels():
        tick.set_rotation(45)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(20)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(20)

    plt.xlabel('Threshold p-values', fontsize=25)
    plt.ylabel("% performance", fontsize=25)

    plt.savefig(path_tables_and_figures_folder + str(subject_id) + '_' + data_type + '_dp_pct_MCC_Sn_Sp.pdf', format='pdf',
                bbox_inches='tight')


def produce_specific_unspecific_perf_plot(path_tables_and_figures_folder, specific_unspecific_matrix_df, data_type):
    specific_unspecific_matrix_df.sort(["threshold_pvalue"], inplace=True)
    num_clones_values = concatenate(specific_unspecific_matrix_df[["specific", "unspecific"]].values.tolist())

    if data_type == "clonotypes":
        yaxis_label = "# clonotypes"
    else:
        yaxis_label = "# cells"

    subject_id = specific_unspecific_matrix_df["subject_id"].iloc[0]

    specific_unspecific_plot(path_tables_and_figures_folder, specific_unspecific_matrix_df, num_clones_values, yaxis_label,
                             data_type, subject_id)

    pct_perf_plot(path_tables_and_figures_folder, specific_unspecific_matrix_df, data_type, subject_id)

    MCC_Sn_Sp_perf_plot(path_tables_and_figures_folder, specific_unspecific_matrix_df, data_type, subject_id)


def produce_specific_unspecific_removing_mixed_clns_perf_plot(path_tables_and_figures_folder, specific_unspecific_matrix_df, data_type):
    subject_ids = list(set(specific_unspecific_matrix_df["subject_id"].values.tolist()))

    for subject_id in subject_ids:
        subjectid_stats_df_index_loc = where(specific_unspecific_matrix_df["subject_id"] == subject_id)[0]
        subjectid_stats_df = specific_unspecific_matrix_df.iloc[subjectid_stats_df_index_loc]
        subjectid_stats_df.sort(["threshold_pvalue"], inplace=True)

        # num_clones_values = concatenate(subjectid_stats_df[["#FP cells", "#TP cells"]].values.tolist())

        # data_type= "cells"
        # yaxis_label = "# cells"

        #
        # mixed_pure_plot(path_tables_and_figures_folder, specific_unspecific_matrix_df, num_clones_values,
        #                          yaxis_label, data_type, subject_id)

        # pct_perf_plot(path_tables_and_figures_folder, specific_unspecific_matrix_df, data_type, subject_id)

        num_clones_values = concatenate(subjectid_stats_df[["#FP clns", "#TP clns"]].values.tolist())

        data_type = "clonotypes"
        yaxis_label = "# clonotypes"

        mixed_pure_plot(path_tables_and_figures_folder, subjectid_stats_df, num_clones_values,
                        yaxis_label, data_type, subject_id)

        pct_perf_plot(path_tables_and_figures_folder, subjectid_stats_df, data_type, subject_id)

def determine_pep_specificity_thresholds_DbPos_for_multiple_subjects(path_tables_and_figures_folder,
                                                                     processed_file_aa_pval_names,
                                                                     positive_control_names,
                                                                     bonferroni=True):

    print("determine_pep_specificity_thresholds_DbPos_for_multiple_subjects")

    summary_ranking_tab_donors = []
    all_donor_thresholds = []

    all_donor_all_clns_data_for_auc = []

    for filename_aa in processed_file_aa_pval_names:
        # print("file", filename_aa)
        if path.isfile(filename_aa):
            df = read_csv(filename_aa, header=None)

            compdataset = ComparisonDataSet(df)
            samples = compdataset.samples

            exvivo, medium, pos_control, rel_pep_stim, irr_pep_stim = prepare_validation_plot(samples, tetramer_sp=positive_control_names, double_positive=True)

            if bonferroni:
                # print("tet bonf: ", tetramer)
                # print("exvivo bonf: ", exvivo)

                bonf_samples = []
                bonf_samples.extend(pos_control)
                bonf_samples.append(exvivo)

                # print("bonf_samples: ", bonf_samples)

                samples_to_process = ClonotypeSamples(samples=bonf_samples, comparisonDataSet=exvivo.comparisonDataSet)

                # print("samples_to_process: ", samples_to_process)

                pvalue_threshold = bonferroni_calculation(samples_to_process, clonotype_level="amino acid")

            tet_aa_clonotypes_exp = pos_control.get_expanded_aa_clonotypesList_with_sample_specific_threshold(pvalue_threshold)

            # print("tet_aa_clonotypes_exp: ", tet_aa_clonotypes_exp)
            # tet_pval_exp_clonotype_index = tet_aa_clonotypes_exp.get_clonotype_index()

            tet_aa_clonotypes_exp_shared = tet_aa_clonotypes_exp.get_aa_shared_clonotypes()

            # print("tet_aa_clonotypes_exp_shared: ", tet_aa_clonotypes_exp_shared)

            tet_pval_exp_clonotype_index = tet_aa_clonotypes_exp_shared.clonotype_index

            # print("tet_pval_exp_clonotype_index: ", tet_pval_exp_clonotype_index)
            # print("tet_pval_exp_clonotype_ids: ", tet_pval_exp_clonotype_ids)
            # print("# tet_pval_exp_clonotype_ids: ", len(tet_pval_exp_clonotype_ids))

            df_before_selection = assign_min_max_pvals(irr_pep_stim=irr_pep_stim, rel_pep_stim=rel_pep_stim, double_positive=True)  # , rel_pval=relevant_cult_exp_threshold

            # print("df_before_selection: ", df_before_selection)

            donor_thresholds_df = get_pep_specificity_thresholds_to_test_by_subject(df_before_selection, tet_pval_exp_clonotype_index)

            # print("donor_thresholds_df: ", donor_thresholds_df)
            subject_id = pos_control.get_subject_ids()[0]

            donor_thresholds_df = concat([DataFrame([subject_id]), donor_thresholds_df], axis=1).fillna(subject_id)
            all_donor_thresholds.append(donor_thresholds_df)

            # all_donor_all_clns_data_for_auc = prepare_data_for_auc(df_before_selection, tet_pval_exp_clonotype_ids, subject_id, all_donor_all_clns_data_for_auc)

        else:
            print('WARN: ' + filename_aa + ' does not exists.')

    all_donor_thresholds_df = concat(all_donor_thresholds, axis=0)
    all_donor_thresholds_df.reset_index(inplace=True, drop=True)

    # auc_analysis(path_tables_and_figures_folder, all_donor_all_clns_data_for_auc)
    # print("all_donor_thresholds_df: ", all_donor_thresholds_df)

    for filename_aa in processed_file_aa_pval_names:
        if path.isfile(filename_aa):
            df = read_csv(filename_aa, header=None)

            compdataset = ComparisonDataSet(df, clonotype_samples_info_file=paths['path_raw_data_folder'] + 'metadata/sample_info.csv')
            samples = compdataset.samples

            exvivo, medium, pos_control, rel_pep_stim, irr_pep_stim = prepare_validation_plot(samples, tetramer_sp=positive_control_names, double_positive=True)

            if bonferroni:
                bonf_samples = []
                bonf_samples.extend(pos_control)
                bonf_samples.append(exvivo)
                samples_to_process = ClonotypeSamples(samples=bonf_samples, comparisonDataSet=exvivo.comparisonDataSet)
                pvalue_threshold = bonferroni_calculation(samples_to_process, clonotype_level="amino acid")

            tet_aa_clonotypes_exp = pos_control.get_expanded_aa_clonotypesList_with_sample_specific_threshold(
                pvalue_threshold)

            tet_aa_clonotypes_exp_shared = tet_aa_clonotypes_exp.get_aa_shared_clonotypes()
            tet_pval_exp_clonotype_index = tet_aa_clonotypes_exp_shared.clonotype_index

            # tet_pval_exp_clonotype_index = tet_aa_clonotypes_exp.get_clonotype_index()

            df_before_selection = assign_min_max_pvals(irr_pep_stim= irr_pep_stim, rel_pep_stim=rel_pep_stim,double_positive=True)

            summary_ranking_tab_donor_df = determine_pep_specificity_thresholds_per_subject(df_before_selection,
                                                                                            tet_pval_exp_clonotype_index,
                                                                                            pos_control, exvivo,
                                                                                            all_donor_thresholds_df)
            subject_id = pos_control.get_subject_ids()[0]
            summary_ranking_tab_donor_df = concat([DataFrame([subject_id]), summary_ranking_tab_donor_df], axis=1).fillna(subject_id)
            summary_ranking_tab_donor_df.columns.values[0] = "Donors"
            summary_ranking_tab_donors.append(summary_ranking_tab_donor_df)
        else:
            print('WARN: ' + filename_aa + ' does not exists.')

    summary_ranking_tab_donors_df = concat(summary_ranking_tab_donors, axis=1)

    sum_perf_clns = []
    sum_perf_exvivo = []

    prod_perf_clns = []
    prod_perf_exvivo = []

    TP_cells_list = []
    TN_cells_list = []
    FP_cells_list = []
    FN_cells_list = []

    TP_clns_list = []
    TN_clns_list = []
    FP_clns_list = []
    FN_clns_list = []

    mcc_clns = []
    mcc_cells = []

    multi_Sn_clns = []
    multi_Sp_clns = []

    multi_Sn_cells = []
    multi_Sp_cells = []

    print("summary_ranking_tab_donors_df: ", summary_ranking_tab_donors_df)

    summary_ranking_tab_donors_df.to_csv(path_tables_and_figures_folder + "pre_summary_ranked_threshold_donors.csv", index=False)

    chunk=100
    print('# of threshold windows to analysed: ', str(len(summary_ranking_tab_donors_df.index)))
    total_iter = ceil(len(summary_ranking_tab_donors_df.index) / float(chunk))

    j = 0
    for i in range(len(summary_ranking_tab_donors_df.index)):
        if (j % chunk) == 0:
            stdout.write("Threshold performance progress: %d%%  \r" % ((float(j) / total_iter) * 100))
            stdout.flush()

        j = j + 1

        sum_sens_sp_clns = []
        sum_sens_sp_exvivo = []
        prod_sens_sp_clns = []
        prod_sens_exvivo = []

        TP_cells = []
        TN_cells = []
        FP_cells = []
        FN_cells = []

        TP_clns = []
        TN_clns = []
        FP_clns = []
        FN_clns = []

        confusion_mtx_parameters_cells = []
        confusion_mtx_parameters_clns = []

        for index in arange(17, len(summary_ranking_tab_donors_df.columns.values), step=21):
            sum_sens_sp_clns.append(summary_ranking_tab_donors_df.iloc[i][index])
            sum_sens_sp_exvivo.append(summary_ranking_tab_donors_df.iloc[i][index + 1])
            prod_sens_sp_clns.append(summary_ranking_tab_donors_df.iloc[i][index + 2])
            prod_sens_exvivo.append(summary_ranking_tab_donors_df.iloc[i][index + 3])

            cell_overlap = summary_ranking_tab_donors_df.iloc[i][index - 7]
            cell_events = summary_ranking_tab_donors_df.iloc[i][index - 4]
            cell_expanded = summary_ranking_tab_donors_df.iloc[i][index - 5]
            cell_tetp = summary_ranking_tab_donors_df.iloc[i][index - 6]

            num_cols_sep_cells_clns = 7

            clns_overlap = summary_ranking_tab_donors_df.iloc[i][index - 7 - num_cols_sep_cells_clns]
            clns_events = summary_ranking_tab_donors_df.iloc[i][index - 4 - num_cols_sep_cells_clns]
            clns_expanded = summary_ranking_tab_donors_df.iloc[i][index - 5 - num_cols_sep_cells_clns]
            clns_tetp = summary_ranking_tab_donors_df.iloc[i][index - 6 - num_cols_sep_cells_clns]

            TP_cells_value = cell_overlap
            FP_cells_value = cell_expanded - cell_overlap
            FN_cells_value = cell_tetp - cell_overlap
            TN_cells_value = cell_events - (TP_cells_value + FP_cells_value + FN_cells_value)

            TP_cells.append(TP_cells_value)
            TN_cells.append(TN_cells_value)
            FP_cells.append(FP_cells_value)
            FN_cells.append(FN_cells_value)

            TP_clns_value = clns_overlap
            FP_clns_value = clns_expanded - clns_overlap
            FN_clns_value = clns_tetp - clns_overlap
            TN_clns_value = clns_events - (TP_clns_value + FP_clns_value + FN_clns_value)

            TP_clns.append(TP_clns_value)
            TN_clns.append(TN_clns_value)
            FP_clns.append(FP_clns_value)
            FN_clns.append(FN_clns_value)

            confusion_mtx_parameters_cells.append([TP_cells_value, TN_cells_value, FP_cells_value, FN_cells_value])
            confusion_mtx_parameters_clns.append([TP_clns_value, TN_clns_value, FP_clns_value, FN_clns_value])

        multi_mcc_clns = []
        multi_mcc_cells = []

        for confusion_mtx_param in confusion_mtx_parameters_cells:
            # print("TP_cells_value, TN_cells_value, FP_cells_value, FN_cells_value (cells): ", confusion_mtx_param)

            TP_cells_value, TN_cells_value, FP_cells_value, FN_cells_value = confusion_mtx_param
            multi_mcc_cells.append(calculation_of_MCC(TP_cells_value, TN_cells_value, FP_cells_value, FN_cells_value))
            if sum([TP_cells_value, FN_cells_value])> 0:
                multi_Sn_cells.append(calculation_of_Sn(TP_cells_value, FN_cells_value))
            if sum([TP_cells_value, TN_cells_value])> 0:
                multi_Sp_cells.append(calculation_of_Sp(TP_cells_value, TN_cells_value))

        for confusion_mtx_param in confusion_mtx_parameters_clns:
            # print("TP_clns_value, TN_clns_value, FP_clns_value, FN_clns_value (clns): ", confusion_mtx_param)

            TP_clns_value, TN_clns_value, FP_clns_value, FN_clns_value = confusion_mtx_param
            multi_mcc_clns.append(calculation_of_MCC(TP_clns_value, TN_clns_value, FP_clns_value, FN_clns_value))
            if sum([TP_clns_value, FN_clns_value]) > 0:
                multi_Sn_clns.append(calculation_of_Sn(TP_clns_value, FN_clns_value))
            if sum([TP_clns_value, TN_clns_value]) > 0:
                multi_Sp_clns.append(calculation_of_Sp(TP_clns_value, TN_clns_value))

        m_mcc_cells = mean(multi_mcc_cells)
        m_mcc_clns = mean(multi_mcc_clns)

        mcc_cells.append(m_mcc_cells)
        mcc_clns.append(m_mcc_clns)

        TP_cells_list.append(sum(TP_cells))
        TN_cells_list.append(sum(TN_cells))
        FP_cells_list.append(sum(FP_cells))
        FN_cells_list.append(sum(FN_cells))

        TP_clns_list.append(sum(TP_clns))
        TN_clns_list.append(sum(TN_clns))
        FP_clns_list.append(sum(FP_clns))
        FN_clns_list.append(sum(FN_clns))

        sum_perf_clns.append(sum(sum_sens_sp_clns))
        sum_perf_exvivo.append(sum(sum_sens_sp_exvivo))
        prod_perf_clns.append(sum(prod_sens_sp_clns))
        prod_perf_exvivo.append(sum(prod_sens_exvivo))

    test = concat(
        [DataFrame(sum_perf_clns), DataFrame(sum_perf_exvivo), DataFrame(prod_perf_clns), DataFrame(prod_perf_exvivo),
         DataFrame(TP_clns_list), DataFrame(TN_clns_list), DataFrame(FP_clns_list), DataFrame(FN_clns_list),
         DataFrame(multi_Sp_clns), DataFrame(multi_Sn_clns), DataFrame(mcc_clns),
         DataFrame(TP_cells_list), DataFrame(TN_cells_list), DataFrame(FP_cells_list), DataFrame(FN_cells_list),
         DataFrame(multi_Sp_cells), DataFrame(multi_Sn_cells), DataFrame(mcc_cells)], axis=1)


    summary_ranking_tab_donors_summed_df = concat([summary_ranking_tab_donors_df, test], axis=1)

    summary_ranking_tab_donors_summed_df.columns = concatenate([summary_ranking_tab_donors_df.columns.values,
                                                                ["tot sum perf clns", "tot sum perf ex vivo",
                                                                 "tot prod perf clns", "tot prod perf ex vivo",
                                                                 "TP (clns)", "TN (clns)", "FP (clns)", "FN (clns)",
                                                                 "Sp (clns)", "Sn (clns)", "MCC (clns)",
                                                                 "TP (cells)", "TN (cells)", "FP (cells)", "FN (cells)",
                                                                 "Sp (cells)", "Sn (cells)", "MCC (cells)"]])

    summary_ranking_tab_donors_summed_df.sort_values("MCC (cells)", ascending=False, inplace=True)


    summary_ranking_tab_donors_summed_df.to_csv(
        path_tables_and_figures_folder + "summary_" + str(pos_control) + "_ranked_threshold_donors.csv", index=False)

    # take the first row with the highest performance after sorting
    selected_thresholds_row = summary_ranking_tab_donors_summed_df.iloc[0]

    print(selected_thresholds_row)
    print(selected_thresholds_row.shape)

    donors_results = []

    print("selected_thresholds_row.iloc[[1, 2]]: ", selected_thresholds_row.iloc[[1, 2]])

    return selected_thresholds_row.iloc[[1, 2]]


def determine_pep_specificity_thresholds_for_multiple_subjects(paths, path_tables_and_figures_folder_opt, processed_file_aa_pval_names,
                                                               tetramer_sp=['exvivo, tetramer stain'], bonferroni=True, double_positive=False):
    print("determine_pep_specificity_thresholds_for_multiple_subjects")

    path_tables_and_figures_folder = path_tables_and_figures_folder_opt
    path_raw_data_folder = paths['path_raw_data_folder']

    summary_ranking_tab_donors = []
    all_donor_thresholds = []

    all_donor_all_clns_data_for_auc = []

    for filename_aa in processed_file_aa_pval_names:
        if path.isfile(filename_aa):
            df = read_csv(filename_aa, header=None)

            compdataset = ComparisonDataSet(df, clonotype_samples_info_file=path_raw_data_folder + 'metadata/sample_info.csv' )
            samples = compdataset.samples

            # print("samples: ", samples)

            exvivo, medium, tetramer, rel_pep_stim, irr_pep_stim = prepare_validation_plot(samples, tetramer_sp=tetramer_sp, double_positive=double_positive)

            if bonferroni:
                # print("tet bonf: ", tetramer)
                # print("exvivo bonf: ", exvivo)

                bonf_samples = []
                bonf_samples.extend(tetramer)
                bonf_samples.append(exvivo)

                # print("bonf_samples: ", bonf_samples)

                samples_to_process = ClonotypeSamples(samples=bonf_samples, comparisonDataSet=exvivo.comparisonDataSet)

                # print("samples_to_process: ", samples_to_process)

                pvalue_threshold = bonferroni_calculation(samples_to_process, clonotype_level="amino acid")

            tet_aa_clonotypes_exp = tetramer.get_expanded_aa_clonotypesList_with_sample_specific_threshold(pvalue_threshold)

            # print("tet_aa_clonotypes_exp: ", tet_aa_clonotypes_exp)

            tet_pval_exp_clonotype_index = tet_aa_clonotypes_exp.get_clonotype_index()

            # print("tet_pval_exp_clonotype_ids: ", tet_pval_exp_clonotype_ids)
            # print("# tet_pval_exp_clonotype_ids: ", len(tet_pval_exp_clonotype_ids))

            df_before_selection = assign_min_max_pvals(medium, irr_pep_stim, rel_pep_stim)#, rel_pval=relevant_cult_exp_threshold

            # print("df_before_selection: ", df_before_selection)

            donor_thresholds_df = get_pep_specificity_thresholds_to_test_by_subject(df_before_selection, tet_pval_exp_clonotype_index)
            subject_id = tetramer.get_subject_ids()[0]

            donor_thresholds_df = concat([DataFrame([subject_id]), donor_thresholds_df], axis=1).fillna(subject_id)
            all_donor_thresholds.append(donor_thresholds_df)

            # all_donor_all_clns_data_for_auc = prepare_data_for_auc(df_before_selection, tet_pval_exp_clonotype_ids, subject_id, all_donor_all_clns_data_for_auc)

        else:
            print('WARN: ' + filename_aa + ' does not exists.')

    all_donor_thresholds_df = concat(all_donor_thresholds, axis=0)
    all_donor_thresholds_df.reset_index(inplace=True, drop=True)

    # auc_analysis(path_tables_and_figures_folder, all_donor_all_clns_data_for_auc)

    # print("all_donor_thresholds_df: ", all_donor_thresholds_df)

    for filename_aa in processed_file_aa_pval_names:
        if path.isfile(filename_aa):
            df = read_csv(filename_aa, header=None)

            compdataset = ComparisonDataSet(df, clonotype_samples_info_file=path_raw_data_folder + 'metadata/sample_info.csv' )
            samples = compdataset.samples

            exvivo, medium, tetramer, rel_pep_stim, irr_pep_stim = prepare_validation_plot(samples, tetramer_sp=tetramer_sp)

            if bonferroni:
                bonf_samples = []
                bonf_samples.extend(tetramer)
                bonf_samples.append(exvivo)
                samples_to_process = ClonotypeSamples(samples=bonf_samples, comparisonDataSet=exvivo.comparisonDataSet)
                pvalue_threshold = bonferroni_calculation(samples_to_process, clonotype_level="amino acid")

            tet_aa_clonotypes_exp = tetramer.get_expanded_aa_clonotypesList_with_sample_specific_threshold(pvalue_threshold)

            tet_pval_exp_clonotype_index = tet_aa_clonotypes_exp.get_clonotype_index()

            df_before_selection = assign_min_max_pvals(medium, irr_pep_stim, rel_pep_stim)

            summary_ranking_tab_donor_df = determine_pep_specificity_thresholds_per_subject(df_before_selection,
                                                                                            tet_pval_exp_clonotype_index,
                                                                                            tetramer, exvivo, all_donor_thresholds_df)
            subject_id = tetramer.get_subject_ids()[0]
            summary_ranking_tab_donor_df = concat([DataFrame([subject_id]), summary_ranking_tab_donor_df], axis=1).fillna(subject_id)
            summary_ranking_tab_donor_df.columns.values[0] = "Donors"
            summary_ranking_tab_donors.append(summary_ranking_tab_donor_df)
        else:
            print('WARN: ' + filename_aa + ' does not exists.')

    summary_ranking_tab_donors_df = concat(summary_ranking_tab_donors, axis=1)

    sum_perf_clns = []
    sum_perf_exvivo = []

    prod_perf_clns = []
    prod_perf_exvivo = []

    TP_cells_list = []
    TN_cells_list = []
    FP_cells_list = []
    FN_cells_list = []

    TP_clns_list = []
    TN_clns_list = []
    FP_clns_list = []
    FN_clns_list = []

    per_donor_mcc_clns = []
    per_donor_mcc_cells = []

    mcc_clns = []
    mcc_cells = []

    multi_Sn_clns = []
    multi_Sp_clns = []

    multi_Sn_cells = []
    multi_Sp_cells = []

    for i in range(len(summary_ranking_tab_donors_df.index)):
        sum_sens_sp_clns = []
        sum_sens_sp_exvivo = []
        prod_sens_sp_clns = []
        prod_sens_exvivo = []

        TP_cells=[]
        TN_cells=[]
        FP_cells=[]
        FN_cells=[]

        TP_clns=[]
        TN_clns=[]
        FP_clns=[]
        FN_clns=[]

        confusion_mtx_parameters_cells = []
        confusion_mtx_parameters_clns = []

        for index in arange(17, len(summary_ranking_tab_donors_df.columns.values), step=21):
            sum_sens_sp_clns.append(summary_ranking_tab_donors_df.iloc[i][index])
            sum_sens_sp_exvivo.append(summary_ranking_tab_donors_df.iloc[i][index+1])
            prod_sens_sp_clns.append(summary_ranking_tab_donors_df.iloc[i][index+2])
            prod_sens_exvivo.append(summary_ranking_tab_donors_df.iloc[i][index+3])

            cell_overlap = summary_ranking_tab_donors_df.iloc[i][index - 7]
            cell_events = summary_ranking_tab_donors_df.iloc[i][index - 4]
            cell_expanded = summary_ranking_tab_donors_df.iloc[i][index - 5]
            cell_tetp = summary_ranking_tab_donors_df.iloc[i][index - 6]

            num_cols_sep_cells_clns = 7

            clns_overlap = summary_ranking_tab_donors_df.iloc[i][index - 7 - num_cols_sep_cells_clns]
            clns_events = summary_ranking_tab_donors_df.iloc[i][index - 4 - num_cols_sep_cells_clns]
            clns_expanded = summary_ranking_tab_donors_df.iloc[i][index - 5 - num_cols_sep_cells_clns]
            clns_tetp = summary_ranking_tab_donors_df.iloc[i][index - 6 - num_cols_sep_cells_clns]

            TP_cells_value = cell_overlap
            FP_cells_value = cell_expanded - cell_overlap
            FN_cells_value = cell_tetp - cell_overlap
            TN_cells_value = cell_events - (TP_cells_value + FP_cells_value + FN_cells_value)

            TP_cells.append(TP_cells_value)
            TN_cells.append(TN_cells_value)
            FP_cells.append(FP_cells_value)
            FN_cells.append(FN_cells_value)

            TP_clns_value = clns_overlap
            FP_clns_value = clns_expanded - clns_overlap
            FN_clns_value = clns_tetp - clns_overlap
            TN_clns_value = clns_events - (TP_clns_value + FP_clns_value + FN_clns_value)

            TP_clns.append(TP_clns_value)
            TN_clns.append(TN_clns_value)
            FP_clns.append(FP_clns_value)
            FN_clns.append(FN_clns_value)

            confusion_mtx_parameters_cells.append([TP_cells_value, TN_cells_value, FP_cells_value, FN_cells_value])
            confusion_mtx_parameters_clns.append([TP_clns_value, TN_clns_value, FP_clns_value, FN_clns_value])

        multi_mcc_clns = []
        multi_mcc_cells = []

        for confusion_mtx_param in confusion_mtx_parameters_cells:
            # print("TP_cells_value, TN_cells_value, FP_cells_value, FN_cells_value (cells): ", confusion_mtx_param)

            TP_cells_value, TN_cells_value, FP_cells_value, FN_cells_value = confusion_mtx_param
            multi_mcc_cells.append(calculation_of_MCC(TP_cells_value, TN_cells_value, FP_cells_value, FN_cells_value))
            multi_Sn_cells.append(calculation_of_Sn(TP_cells_value, FN_cells_value))
            multi_Sp_cells.append(calculation_of_Sp(TP_cells_value, TN_cells_value))

        for confusion_mtx_param in confusion_mtx_parameters_clns:
            # print("TP_clns_value, TN_clns_value, FP_clns_value, FN_clns_value (clns): ", confusion_mtx_param)

            TP_clns_value, TN_clns_value, FP_clns_value, FN_clns_value = confusion_mtx_param
            multi_mcc_clns.append(calculation_of_MCC(TP_clns_value, TN_clns_value, FP_clns_value, FN_clns_value))
            multi_Sn_clns.append(calculation_of_Sn(TP_clns_value, FN_clns_value))
            multi_Sp_clns.append(calculation_of_Sp(TP_clns_value, TN_clns_value))


        m_mcc_cells = mean(multi_mcc_cells)
        m_mcc_clns = mean(multi_mcc_clns)

        mcc_cells.append(m_mcc_cells)
        mcc_clns.append(m_mcc_clns)

        per_donor_mcc_clns.append(multi_mcc_clns)
        per_donor_mcc_cells.append(multi_mcc_cells)

        TP_cells_list.append(sum(TP_cells))
        TN_cells_list.append(sum(TN_cells))
        FP_cells_list.append(sum(FP_cells))
        FN_cells_list.append(sum(FN_cells))

        TP_clns_list.append(sum(TP_clns))
        TN_clns_list.append(sum(TN_clns))
        FP_clns_list.append(sum(FP_clns))
        FN_clns_list.append(sum(FN_clns))

        sum_perf_clns.append(sum(sum_sens_sp_clns))
        sum_perf_exvivo.append(sum(sum_sens_sp_exvivo))
        prod_perf_clns.append(sum(prod_sens_sp_clns))
        prod_perf_exvivo.append(sum(prod_sens_exvivo))

    #summary_ranking_tab_donors_df.sort_values("sum perf ex vivo", ascending=False, inplace=True)
    #summary_ranking_tab_donors_df.sort_values("sum perf clns", ascending=False, inplace=True)

    # print('summary_ranking_tab_donors_df : ', summary_ranking_tab_donors_df)
    # print('DataFrame(sum_perf_clns) : ', DataFrame(sum_perf_clns))
    # print('DataFrame(sum_perf_exvivo) : ', DataFrame(sum_perf_exvivo))

    # print("multi_Sp_clns: ",multi_Sp_clns)
    # print("multi_Sn_clns: ", multi_Sn_clns)

    # multi_Sp_clns_1, multi_Sp_clns_2 = partition_in_2_list(multi_Sp_clns)
    # multi_Sn_clns_1, multi_Sn_clns_2 = partition_in_2_list(multi_Sn_clns)

    # print("multi_Sp_clns_1", multi_Sp_clns_1)

    # multi_Sp_cells_1, multi_Sp_cells_2 = partition_in_2_list(multi_Sp_cells)
    # multi_Sn_cells_1, multi_Sn_cells_2 = partition_in_2_list(multi_Sn_cells)

    # print("multi_Sn_cells_1, multi_Sn_cells_2: ", [multi_Sn_cells_1, multi_Sn_cells_2])

    # test = concat([DataFrame(sum_perf_clns), DataFrame(sum_perf_exvivo), DataFrame(prod_perf_clns), DataFrame(prod_perf_exvivo),
    #                DataFrame(TP_clns_list), DataFrame(TN_clns_list), DataFrame(FP_clns_list), DataFrame(FN_clns_list),
    #                DataFrame(multi_Sp_clns_1), DataFrame(multi_Sp_clns_2), DataFrame(multi_Sn_clns_1), DataFrame(multi_Sn_clns_2), DataFrame(mcc_clns),
    #                DataFrame(TP_cells_list), DataFrame(TN_cells_list), DataFrame(FP_cells_list), DataFrame(FN_cells_list),
    #                DataFrame(multi_Sp_cells_1), DataFrame(multi_Sp_cells_2), DataFrame(multi_Sn_cells_1), DataFrame(multi_Sn_cells_2), DataFrame(mcc_cells)], axis=1)

    test = concat([DataFrame(sum_perf_clns), DataFrame(sum_perf_exvivo), DataFrame(prod_perf_clns), DataFrame(prod_perf_exvivo),
                   DataFrame(TP_clns_list), DataFrame(TN_clns_list), DataFrame(FP_clns_list), DataFrame(FN_clns_list),
                   DataFrame(multi_Sp_clns), DataFrame(multi_Sn_clns), DataFrame(mcc_clns),
                   DataFrame(TP_cells_list), DataFrame(TN_cells_list), DataFrame(FP_cells_list), DataFrame(FN_cells_list),
                   DataFrame(multi_Sp_cells), DataFrame(multi_Sn_cells), DataFrame(mcc_cells), DataFrame(per_donor_mcc_cells),
                   DataFrame(per_donor_mcc_clns)], axis=1)

    # print('multi_Sn_cells_1: ',DataFrame(multi_Sn_cells_1))
    # print('test: ', test)

    summary_ranking_tab_donors_summed_df = concat([summary_ranking_tab_donors_df, test], axis=1)

    # summary_ranking_tab_donors_summed_df.columns = concatenate([summary_ranking_tab_donors_df.columns.values,
    #                                                             ["tot sum perf clns", "tot sum perf ex vivo", "tot prod perf clns", "tot prod perf ex vivo",
    #                                                              "TP (clns)", "TN (clns)","FP (clns)","FN (clns)", "Sp (clns) 1", "Sp (clns) 2", "Sn (clns) 1 ", "Sn (clns) 2", "MCC (clns)",
    #                                                              "TP (cells)", "TN (cells)", "FP (cells)", "FN (cells)", "Sp (cells) 1", "Sp (cells) 2", "Sn (cells) 1", "Sn (cells) 2", "MCC (cells)"]])

    summary_ranking_tab_donors_summed_df.columns = concatenate([summary_ranking_tab_donors_df.columns.values,
                                                                ["tot sum perf clns", "tot sum perf ex vivo", "tot prod perf clns", "tot prod perf ex vivo",
                                                                 "TP (clns)", "TN (clns)","FP (clns)","FN (clns)", "Sp (clns)", "Sn (clns)", "MCC (clns)",
                                                                 "TP (cells)", "TN (cells)", "FP (cells)", "FN (cells)", "Sp (cells)", "Sn (cells)", "MCC (cells)"],
                                                                 ["Multi donors MCC (cells)"] * len(processed_file_aa_pval_names),  ["Multi donors MCC (clns)"] * len(processed_file_aa_pval_names)])


    summary_ranking_tab_donors_summed_df.sort_values("MCC (cells)", ascending=False, inplace=True)

    # summary_ranking_tab_donors_summed_df.sort_values("tot sum perf clns", ascending=False, inplace=True)
    # summary_ranking_tab_donors_summed_df.sort_values("tot prod perf ex vivo", ascending=False, inplace=True)
    # summary_ranking_tab_donors_summed_df.sort_values("tot prod perf clns", ascending=False, inplace=True)

    summary_ranking_tab_donors_summed_df.to_csv(path_tables_and_figures_folder + "summary_" + str(tetramer_sp) + "_ranked_threshold_donors.csv", index=False)

    #take the first row with the highest performance after sorting

    selected_thresholds_row = summary_ranking_tab_donors_summed_df.iloc[0]

    print(selected_thresholds_row)
    print(selected_thresholds_row.shape)

    donors_results = []

    # print("len row: ", len(selected_thresholds_row.index.values))

    # print(arange(3, len(selected_thresholds_row.index.values)-4, step=31))
    #
    # for index in arange(3, len(selected_thresholds_row.index.values)-4, step=31):
    #     # print("Index: ", index)
    #
    #     subject_id = selected_thresholds_row.iloc[index-3]
    #     irrelevant = selected_thresholds_row.iloc[index-2]
    #     relevant = selected_thresholds_row.iloc[index-1]
    #
    #     overlap_clns = selected_thresholds_row.iloc[index]
    #     tet_clns = selected_thresholds_row.iloc[index+1]
    #     exp_clns = selected_thresholds_row.iloc[index+2]
    #     pept_stim_clns = selected_thresholds_row.iloc[index + 3]
    #
    #     pct_ovlp_tet_clns = selected_thresholds_row.iloc[index+4]
    #     pct_ovlp_exp_clns = selected_thresholds_row.iloc[index+5]
    #
    #     overlap_cells = selected_thresholds_row.iloc[index+6]
    #     tet_cells = selected_thresholds_row.iloc[index+7]
    #     exp_cells = selected_thresholds_row.iloc[index+8]
    #     pept_stim_cells = selected_thresholds_row.iloc[index+9]
    #
    #     pct_ovlp_tet_cells = selected_thresholds_row.iloc[index+10]
    #     pct_ovlp_exp_cells = selected_thresholds_row.iloc[index+11]
    #
    #     donors_results.append(DataFrame([
    #                             [subject_id, subject_id, subject_id, subject_id],
    #                             [irrelevant, irrelevant, irrelevant, irrelevant],
    #                             [relevant, relevant, relevant, relevant],
    #                             [tet_clns, exp_clns, overlap_clns, pept_stim_clns],
    #                             [pct_ovlp_tet_clns, pct_ovlp_exp_clns, "-", "-"],
    #                             [tet_cells, exp_cells, overlap_cells, pept_stim_cells],
    #                             [pct_ovlp_tet_cells, pct_ovlp_exp_cells, "-", "-"]
    #                                     ], columns=["tetramer", "expanded", "shared", "exposed"],
    #                             index=["subject ID", "irrelevant", "relevant", "# clonotypes", "% overlap (clns)",
    #                                      "# ex vivo cells", "%overlap (cells)"]).T)
    #
    # selected_thresholds_df = concat(donors_results, axis=0)
    #
    # selected_thresholds_df.to_csv(path_tables_and_figures_folder + "summary_table_" + str(tetramer_sp) + "_selected_thresholds_donors.csv", index=True)


    print("selected_thresholds_row.iloc[[1, 2]]: ", selected_thresholds_row.iloc[[1, 2]])

    return selected_thresholds_row.iloc[[1, 2]]

def validation_bar_plot_aa(path_tables_and_figures_folder, exvivo, medium, tetramer, rel_pep_stim, irr_pep_stim,
                           tetramer_sp=['exvivo, tetramer stain'], culture_thresholds=[1e-20, 1e-3],
                           pvalue_threshold=0.001, bonferroni=True):

    relevant_cult_exp_threshold = culture_thresholds[0]#1e-20#config 2, e.g.: pep-QAA b200_op-1_pval	b200_op-2_pval c-iv-1_pval	c-iv-2_pval
    irrelevant_cult_exp_threshold = culture_thresholds[1]#1e-2#config 2, e.g.: pep-RQS tu33med2_pval	tu33med1_pval	b2m_np1_pval	b200_np-1_pval	b2m_np12_pval	b2m_np2_pval b200_np-2_pval

    print("Using thresholds : ", culture_thresholds)

    list_of_freq_total_sum_dict = {}

    if bonferroni:
        samples=[]
        samples.extend(tetramer)
        samples.append(exvivo)
        pvalue_threshold = bonferroni_calculation(ClonotypeSamples(samples=samples,comparisonDataSet=exvivo.comparisonDataSet), clonotype_level="amino acid")

    tet_aa_clonotypes_exp = tetramer.get_expanded_aa_clonotypesList_with_sample_specific_threshold(pvalue_threshold)

    print('tetramer: ', tet_aa_clonotypes_exp)

    tet_pval_exp_clonotype_ids = tet_aa_clonotypes_exp.get_aa_clonotype_ids()

    df_before_selection = assign_min_max_pvals(medium, irr_pep_stim, rel_pep_stim)#, rel_pval=relevant_cult_exp_threshold

    #---
    # df_test = df_before_selection.iloc[where((df_before_selection[0] <= relevant_cult_exp_threshold) & (df_before_selection[1] >= irrelevant_cult_exp_threshold))[0]]
    # print('test1 # exp selected: ', len(df_test.index.values))
    # tet_clonotype_ids_test = intersect1d(array(tet_pval_exp_clonotype_ids), array(df_test.index.values))
    # print('test2 # tet intersect: ', len(tet_clonotype_ids_test))
    #---

    total_exvivo_tetp_freq_by_clonotypes = exvivo.aa_clonotypes.get_cell_frequencies_by_aa_clonotype_index(tet_pval_exp_clonotype_ids)

    total_exvivo_tetp = sum(total_exvivo_tetp_freq_by_clonotypes)

    print("total_exvivo_tetp: ", total_exvivo_tetp)

    list_of_freq_total_sum_dict['tetramer'] = total_exvivo_tetp

    # print('expanded tetr : ', tet_pval_exp_clonotype_ids)
    # print('aa clonotypes : ', tet_aa_clonotypes_exp)
    # print('total_exvivo_tetp : ', total_exvivo_tetp)

    df_temp = df_before_selection.iloc[where((df_before_selection["irrelevant"] >= irrelevant_cult_exp_threshold)
                                        & (df_before_selection["relevant"] <= relevant_cult_exp_threshold))[0]]

    exposed_super_confident_clonotypes_freq_by_clonotypes = exvivo.aa_clonotypes.get_cell_frequencies_by_aa_clonotype_index(df_temp.index.values)
    exposed_super_confident_clonotypes = sum(exposed_super_confident_clonotypes_freq_by_clonotypes)
    list_of_freq_total_sum_dict['rel_pep'] = exposed_super_confident_clonotypes

    # fp_interpretation(path_tables_and_figures_folder, exposed_super_confident_clonotypes_freq_by_clonotypes, tet_pval_exp_clonotype_ids, tetramer)

    print('intersection between tetp and exp')

    # cell_count_exvivo = sum(exvivo.get_cell_counts())
    # tetp_cell_count = total_exvivo_tetp*cell_count_exvivo

    # cut_the_cake(df_before_selection, irrelevant_cult_exp_threshold, relevant_cult_exp_threshold, exvivo,
    #              tet_pval_exp_clonotype_ids, cell_count_exvivo, tetp_cell_count, total_exvivo_tetp_freq_by_clonotypes,
    #              verbose=True)

    rel_pep_stim_not_exp_clonotype_ids = setdiff1d(rel_pep_stim.get_clonotype_ids(), df_before_selection.index.values)

    get_2by2_exvivo_table(tet_pval_exp_clonotype_ids, df_before_selection.index.values, rel_pep_stim_not_exp_clonotype_ids, exvivo)

    width = .2

    fig = plt.figure()
    ax = plt.gca()

    comp = list_of_freq_total_sum_dict.values()

    # print(tuple(comp)[0])
    # print(tuple(comp)[1])
    print("frequencies exvivo: ", list(comp))
    mytupcomp=tuple(comp)
    mycompvalues=[float(k) for k in mytupcomp]

    # print("mycompvalues: ",mycompvalues)

    dist_to_add=max(mycompvalues)*0.05

    rects = ax.bar(0.1, tuple(comp)[0], width, color='black')
    for rect in rects:
        height = rect.get_height()
        # print("height: ", int(height))
        if int(height) > 0:
            ax.text(0.05, height + dist_to_add, '{:.2e}'.format(height), ha='center', va='bottom')
        # else:
        #     # print("height: ", height)
        #     ax.text(0.05, ax.get_ylim()[0] + dist_to_add , '0', ha='center', va='bottom')

    # print("rect.get_width(): ",rect.get_width())

    rects = ax.bar(0.2, tuple(comp)[1], width, color='orange')
    for rect in rects:
        height = rect.get_height()
        # print("height: ", height)
        if height > 0:
            ax.text(0.15, height + dist_to_add, '{:.2e}'.format(height), ha='center', va='bottom')
            # ax.text(rect.get_x() + rect.get_width()/2., 1.05*height, '{:.2e}'.format(height), ha='center', va='bottom')
        # else:
        #     ax.text(0.15, ax.get_ylim()[0] + dist_to_add, '0', ha='center', va='bottom')
            # ax.text(rect.get_x() + rect.get_width() / 2., 0.05, '0', ha='center', va='bottom')

    # print("rect.get_width(): ", rect.get_width())

    xtickNames = ax.set_xticklabels(['tetramer binding', 'expanded'])
    ax.set_xticks([0.05, 0.15])
    plt.setp(xtickNames, rotation=0, fontsize=10)
    ax.set_yscale('log', basey=10)

    # ax.patch.set_facecolor('None')

    # fig.patch.set_visible(True)
    # ax.patch.set_visible(True)
    # for k in ax.spines.keys():
    #     ax.spines[k].set_color('0.5')

    # for item in [fig, ax]:
    #     item.patch.set_visible(True)exvivo_df

    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(20)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(20)

    plt.ylabel('total frequency $\it{ex}$ $\it{vivo}$', fontsize=25)

    plt.xlim(0, 0.2)
    subject_id = tetramer.get_subject_ids()[0]
    plt.savefig(path_tables_and_figures_folder + str(subject_id) + '_' + str(tetramer_sp) + '_aa_validation_bar_plot.pdf', format='pdf', bbox_inches='tight')

def plot_comparison_medium_vs_pepstim_pvalues_final(path_tables_and_figures_folder, df, subject_id, pept):
    print('# clonotypes analysed: ', len(df.index))
    # index_mod = where(~((df["medium"] == 1) | (df["pepstim"] == 1)))[0]
    # df_test = df.iloc[index_mod]

    cor_coef, pval = spearmanr(df)
    print("spearmanr => " + str(int(subject_id[0])) + " shared expanded clonotypes: ", [round(cor_coef,3), pval])

    index_mod_not_zero = where((df["medium"] != 0))[0]
    index_mod_zero = where((df["medium"] == 0))[0]

    df_no_zeros = df["medium"].iloc[index_mod_not_zero]

    xmin_val = min(df_no_zeros) * 0.4
    df["medium"].iloc[index_mod_zero] = xmin_val

    index_mod_not_zero = where((df["pepstim"] != 0))[0]
    index_mod_zero = where((df["pepstim"] == 0))[0]

    df_no_zeros = df["pepstim"].iloc[index_mod_not_zero]

    ymin_val = min(df_no_zeros) * 0.4
    df["pepstim"].iloc[index_mod_zero] = ymin_val

    if len(df.index) > 0:

        counts_freq = Counter(zip(df["medium"], df["pepstim"]))

        points = counts_freq.keys()

        # print('--', points)

        x, y = zip(*points)

        x = array(x)
        y = array(y)

        colors = []
        for index in range(len(x)):
            if (ymin_val == y[index]) or (x[index] == xmin_val):
                colors.append('red')
            else:
                colors.append('k')

    size_array = array(map(sqrt, counts_freq.values())) + 15

    # print("x: ", x)
    # print("y: ", y)
    # print("counts: ", counts_freq)
    # print('size dots: ', size_array)

    fig = plt.figure()

    ax = plt.gca()

    ax.scatter(x, y, s=size_array, color=colors, marker='o', linewidths=0.5, edgecolor='w',clip_on=False)
    ax.set_xlim((min(x), max(x)))
    ax.set_ylim((min(y), max(y)))

    ax.set_yscale('log', basey=10)
    ax.set_xscale('log', basex=10)

    # plt.savefig(path_tables_and_figures_folder + str(subject_id[0]) + '_medium_vs_pepstim_pval_aa.pdf', dpi=300,
    #             format='pdf', bbox_inches='tight')

    ax.patch.set_facecolor('None')
    ax.grid(color='gainsboro', linestyle='dashed')

    # labels = [item.get_text() for item in ax.get_xticklabels()]
    #
    # # print(labels)
    #
    # newlabels = []
    # for label in labels:
    #     if label == u'$\\mathdefault{0}$':
    #         newlabels.append(u' ')
    #     else:
    #         newlabels.append(label)
    #
    # # newlabels[len(newlabels) -2]= u'$\\mathdefault{10^{0}}$'
    # ax.set_xticklabels(newlabels)
    #
    # labels = [item.get_text() for item in ax.get_yticklabels()]
    # newlabels = []
    # for label in labels:
    #     if label == u'$\\mathdefault{0}$':
    #         newlabels.append(u' ')
    #     else:
    #         newlabels.append(label)
    #
    # # newlabels[len(newlabels)-2]= u'$\\mathdefault{10^{0}}$'
    # ax.set_yticklabels(newlabels)

    # ax.spines['bottom'].set_color('black')
    # ax.spines['left'].set_color('black')

    for tick in ax.get_xticklabels():
        tick.set_rotation(45)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(20)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(20)

    plt.xlabel('after peptide culture', fontsize=25)
    plt.ylabel('medium', fontsize=25)

    plt.savefig(path_tables_and_figures_folder + str(int(subject_id[0])) + "_" + str(pept) + '_medium_vs_pepstim_pval_aa.pdf', dpi=300, format='pdf', bbox_inches='tight')
    print(str(int(subject_id[0])) + "_" + str(pept) + '_medium_vs_pepstim_pval_aa.pdf')

def add_thres_lines(list_of_axis, mylimits, rel_pepstim_threshold, myfake_value, myfake_min, myfake_max, negctrl_threshold):
    for myaxis_index in range(len(list_of_axis)):
        myaxis = list_of_axis[myaxis_index]
        xlimits = mylimits[myaxis_index][0]
        ylimits = mylimits[myaxis_index][1]

        print('xlimits: ', xlimits)
        print('ylimits: ', ylimits)
        print('myaxis_index: ', myaxis_index)

        print('rel_pepstim_threshold: ', rel_pepstim_threshold)
        print('negctrl_threshold: ', negctrl_threshold)

        # vertical line
        if (rel_pepstim_threshold <= xlimits[1]) & (rel_pepstim_threshold >= xlimits[0]):
            # if myaxis_index in [0, 2]:
            #     myaxis.plot([myfake_value, myfake_value], [ylimits[0], ylimits[1]], '--', linewidth=1.0, color='r')
            # elif myaxis_index in [4, 5]:
            #     myaxis.plot([rel_pepstim_threshold, rel_pepstim_threshold], [myfake_min, myfake_max], '--', linewidth=1.0, color='r')
            # else:
            #     myaxis.plot([rel_pepstim_threshold, rel_pepstim_threshold], [ylimits[0], ylimits[1]], '--', linewidth=1.0, color='r')  # marker='.',

            if myaxis_index == 5:
                myaxis.plot([rel_pepstim_threshold, rel_pepstim_threshold], [myfake_min, myfake_max], '--', linewidth=1.0, color='r')
            else:
                myaxis.plot([rel_pepstim_threshold, rel_pepstim_threshold], [ylimits[0], ylimits[1]], '--', linewidth=1.0, color='r')  # marker='.',



        # horizontal line
        if (negctrl_threshold <= ylimits[1]) & (negctrl_threshold >= ylimits[0]):
            # if myaxis_index in [5]:
            #     myaxis.plot([xlimits[0], xlimits[1]], [myfake_value, myfake_value], '--', linewidth=1.0, color='r')
            # elif myaxis_index in [4]:
            #     myaxis.plot([myfake_min, myfake_max], [myfake_value, myfake_value], '--', linewidth=1.0, color='r')
            # elif myaxis_index in [0]:
            #     myaxis.plot([myfake_min, myfake_max], [negctrl_threshold, negctrl_threshold], '--', linewidth=1.0, color='r')
            # else:
            #     myaxis.plot([xlimits[0], xlimits[1]], [negctrl_threshold, negctrl_threshold], '--', linewidth=1.0, color='r')

            if myaxis_index == 0:
                myaxis.plot([myfake_min, myfake_max], [negctrl_threshold, negctrl_threshold], '--', linewidth=1.0, color='r')
            else:
                myaxis.plot([xlimits[0], xlimits[1]], [negctrl_threshold, negctrl_threshold], '--', linewidth=1.0, color='r')

        # if myaxis_index in [1, 3, 5]:

        if myaxis_index == 1:
            if (rel_pepstim_threshold <= xlimits[1]) & (rel_pepstim_threshold >= xlimits[0]):
                # vertical line
                myaxis.plot([rel_pepstim_threshold, rel_pepstim_threshold], [ylimits[0], ylimits[1]], '--', linewidth=1.0, color='r')  # marker='.',
                myaxis.annotate('{:.2e}'.format(rel_pepstim_threshold), xy=(rel_pepstim_threshold + (0.06 * rel_pepstim_threshold[1]), ylimits[1] + (0.06* ylimits[1])), size=15)

            if (negctrl_threshold <= ylimits[1]) & (negctrl_threshold >= ylimits[0]):
                # horizontal line
                myaxis.plot([xlimits[0], xlimits[1]], [negctrl_threshold, negctrl_threshold], '--', linewidth=1.0, color='r')
                myaxis.annotate('{:.2e}'.format(negctrl_threshold), xy=(xlimits[1] + (0.1 * xlimits[1]),negctrl_threshold), size=15)

        if (rel_pepstim_threshold == 0):
            if myaxis_index in [0, 2]:
                myaxis.plot([myfake_value, myfake_value], [ylimits[0], ylimits[1]], '--', linewidth=1.0, color='r')
                if myaxis_index == 0:
                    myaxis.annotate('0', xy=(myfake_value, ylimits[1] + (0.06 * ylimits[1])), size=15)
            elif myaxis_index == 4:
                myaxis.plot([myfake_value, myfake_value], [myfake_min, myfake_max], '--', linewidth=1.0, color='r')

        if (negctrl_threshold == 0):
            if myaxis_index == 4:
                myaxis.plot([myfake_min, myfake_max], [myfake_value, myfake_value], '--', linewidth=1.0, color='r')
                myaxis.annotate('0', xy=(myfake_min - (0.1 * myfake_min), myfake_value), size=15)

            elif myaxis_index == 5:
                myaxis.plot([xlimits[0], xlimits[1]], [myfake_value, myfake_value], '--', linewidth=1.0, color='r')

    return list_of_axis

def plot_comparison_negctrl_vs_pepstim_pvalues_final(path_tables_and_figures_folder, df, tetramer, df_tet_pval,
                                                     negctrl_threshold, rel_pepstim_threshold, tetramer_sp=['exvivo, tetramer stain'],double_positive=False):

    col0 = df[df.columns.values[0]]
    col1 = df[df.columns.values[1]]

    index_mod_col0_not_zero = where(~(col0 == 0))[0]
    index_mod_col1_not_zero = where(~(col1 == 0))[0]

    col0_not_zero = array(df[df.columns.values[0]].iloc[index_mod_col0_not_zero].dropna().values)
    col1_not_zero = array(df[df.columns.values[1]].iloc[index_mod_col1_not_zero].dropna().values)

    mymin_x_line = min(col0_not_zero) * 0.9
    mymin_y_line_upper = 1e-12 #min(col1_not_zero) * 0.9
    mymin_y_line_lower = min(col1_not_zero)

    # percentileofscore(col1_not_zero, mymin_y_line_upper)
    # y_20pct = percentile(col1_not_zero, 20)

    mymin_x_values_on_axis = min(col0_not_zero) * 0.2
    mymin_y_values_on_axis = mymin_y_line_lower * 0.2

    # label1 = 'p-value $\geqslant$ {:.2e}'.format(pvalue_threshold) + ' (# = ' + str(
    #     len(df.index.values) - len(exp_df.index.values)) + ')'

    # f, [[ax_up_left, ax2_up_center, ax3_up_right], [ax4_center_left, ax5_center_center, ax6_center_right], [ax7_down_left, ax8_down_center, ax9_down_right]] = plt.subplots(
    #                                         3, 3, gridspec_kw={'width_ratios': [1, 20, 1], 'height_ratios': [1, 20, 1]})

    subject_id = tetramer.get_subject_ids()[0]
    # df.to_csv(path_tables_and_figures_folder + str(subject_id) + "_" + str(tetramer_sp) + '_negctrl_vs_pepstim_pval_aa.csv')

    f, axs = plt.subplots(3, 2, gridspec_kw={'width_ratios': [4, 96], 'height_ratios': [77, 19, 4]})  # , sharex=True, sharey=True

    mymax_y_value = max(df[df.columns.values[1]])
    mymax_x_value = max(df[df.columns.values[0]])

    [[ax_up_left, ax2_up_right], [ax3_center_left, ax4_center_right], [ax5_down_left, ax6_down_right]] = axs

    print("limits: ", [mymin_x_values_on_axis, mymin_y_values_on_axis, mymin_x_line, mymin_y_line_upper, mymin_y_line_lower])

    ledg1, subplots_list, mylimits, myfake_value, [myfake_min, myfake_max], var1, var2, yticks_mod = insert_axis_info_relevantpept_compared_to_negctrl(
                                                                                            df, df_tet_pval, mymax_x_value, mymax_y_value,
                                                                                            mymin_x_values_on_axis,
                                                                                         mymin_y_values_on_axis,
                                                                                         mymin_x_line,
                                                                                         mymin_y_line_upper,
                                                                                         mymin_y_line_lower,
                                                                                         [ax_up_left, ax2_up_right,
                                                                                          ax3_center_left, ax4_center_right,
                                                                                          ax5_down_left, ax6_down_right],
                                                                                         color=['k','r'])#, label=label1


    list_of_axis = [ax_up_left, ax2_up_right, ax3_center_left, ax4_center_right, ax5_down_left, ax6_down_right]

    print("mylimits: ", mylimits)

    list_of_axis = add_thres_lines(list_of_axis, mylimits, rel_pepstim_threshold, myfake_value, myfake_min, myfake_max, negctrl_threshold)

    sym1 = ax2_up_right.scatter([1, 2], [1, 2], marker='o', color='r')
    sym2 = ax2_up_right.scatter([1, 2], [1, 2], marker='o', color='k')

    if len(tetramer_sp) == 1:
        print("tetramer+ from " + str(tetramer_sp[0]))
        legend = ax2_up_right.legend((sym1, sym2), ("tetramer+ from " + str(tetramer_sp[0]).split(",")[0], "tetramer-"), numpoints=1,
                                     markerscale=2., bbox_to_anchor=(0, 1.02, 1, 0.2),
                                     scatterpoints=1, fontsize=15, fancybox=True, shadow=False,
                                     ncol=1, loc="lower left", mode="expand")
    elif len(tetramer_sp) == 2:
        legend = ax2_up_right.legend((sym1, sym2), ("tetramer+ from ex vivo & peptide culture stain", "tetramer-"), numpoints=1,
                                     markerscale=2., bbox_to_anchor=(0, 1.02, 1, 0.2),
                                     scatterpoints=1, fontsize=15, fancybox=True, shadow=False,
                                     ncol=1, loc="lower left", mode="expand")
    else:
        legend = ax2_up_right.legend((sym1, sym2), ("tetramer+", "tetramer-"), numpoints=1,
                                     markerscale=2., bbox_to_anchor=(0, 1.02, 1, 0.2),
                                     scatterpoints=1, fontsize=15, fancybox=True, shadow=False,
                                     ncol=1, loc="lower left", mode="expand")


    f.text(0.5, 0.04, 'After peptide culture', fontsize=20, ha='center', va='center')

    f.text(0.025, 0.5, 'Negative control', fontsize=20, ha='center', va='center', rotation='vertical')

    f.subplots_adjust(hspace=0.2, wspace=0.08, left=0.17, bottom=0.21, top=0.95, right=0.85)#, top=0.85, right=0.85

    # ax_up_left.xaxis.set_ticks_position('none')
    # ax_up_left.xaxis.set_ticks([])
    # ax_up_left.xaxis.set_label_text('')

    # plt.savefig(
    #     path_tables_and_figures_folder + str(subject_id) + "_" + str(tetramer_sp) + '_negctrl_vs_pepstim_pval_aa.svg',
    #     format='svg')

    add_thres_lines(list_of_axis, mylimits, rel_pepstim_threshold, myfake_value, myfake_min, myfake_max,
                    negctrl_threshold)

    plt.savefig(
        path_tables_and_figures_folder + str(subject_id) + "_" + str(tetramer_sp) + "_irrel_" +  '{:.2e}'.format(negctrl_threshold) + "_rel_" +  '{:.2e}'.format(rel_pepstim_threshold) + '_negctrl_vs_pepstim_pval_aa.pdf',
        format='pdf',  bbox_inches="tight")

    print(str(subject_id) + "_" + str(tetramer_sp) + "_irrel_" +  '{:.2e}'.format(negctrl_threshold) + "_rel_" +  '{:.2e}'.format(rel_pepstim_threshold) + '_negctrl_vs_pepstim_pval_aa.pdf')

def assign_min_pvals(medium, pep_stim):
    medium_pval_df = medium.get_aa_pvalues_df()
    pep_stim_pval_df = pep_stim.get_aa_pvalues_df()

    min_medium_pval = [min(medium_pval_df.ix[index]) for index in medium_pval_df.index.values]
    min_medium_pval_df = DataFrame(min_medium_pval, index=medium_pval_df.index.values)

    min_pep_stim_pval = [min(pep_stim_pval_df.ix[index]) for index in pep_stim_pval_df.index.values]
    min_pep_stim_pval_df = DataFrame(min_pep_stim_pval, index=pep_stim_pval_df.index.values)

    df = concat([min_medium_pval_df, min_pep_stim_pval_df], axis=1)

    # assume that clonotypes not present in neg ctrl are not expanded = assign a 1 p-value
    # assume that clonotypes not present in selected subset of stim samples are not expanded and were in the cultured assay before stimulation
    df = df.fillna(1)

    # assume that we cannot give an expansion value to clonotypes that are not found in stimulated or in negative control samples
    # df=df.dropna()
    df.columns = ["medium", "pepstim"]

    return df

def assign_min_pvals_for_medium_and_peptstim(medium, peptstim,  clonotype_level="nucleotide", bonferroni_thresholds_dict=None):#
    if bonferroni_thresholds_dict is not None:
        if clonotype_level == "nucleotide":
            medium_samples_list = []
            for medium_sample in medium:
                medium_pval = bonferroni_thresholds_dict[medium_sample.ID]
                medium_pval_df = medium.get_nt_clonotypesList_with_pvalue_lower_than(
                    threshold=medium_pval).get_nt_pvalues_df()
                medium_samples_list.append(medium_pval_df)

            peptstim_samples_list = []
            for peptstim_sample in peptstim:
                peptstim_pval = bonferroni_thresholds_dict[peptstim_sample.ID]
                peptstim_pval_df = peptstim.get_nt_clonotypesList_with_pvalue_lower_than(
                    threshold=peptstim_pval).get_nt_pvalues_df()
                peptstim_samples_list.append(peptstim_pval_df)

        else:
            medium_samples_list = []
            for medium_sample in medium:
                medium_pval = bonferroni_thresholds_dict[medium_sample.ID]
                medium_pval_df = medium.get_aa_clonotypesList_with_pvalue_lower_than(
                    threshold=medium_pval).get_aa_pvalues_df()
                medium_samples_list.append(medium_pval_df)

            peptstim_samples_list = []
            for peptstim_sample in peptstim:
                peptstim_pval = bonferroni_thresholds_dict[peptstim_sample.ID]
                peptstim_pval_df = peptstim.get_aa_clonotypesList_with_pvalue_lower_than(
                    threshold=peptstim_pval).get_aa_pvalues_df()
                peptstim_samples_list.append(peptstim_pval_df)
        medium_pval_df = concat(medium_samples_list)
        peptstim_pval_df = concat(peptstim_samples_list)

    else:
        if clonotype_level == "nucleotide":
            medium_pval_df = medium.get_nt_pvalues_df()
            peptstim_pval_df = peptstim.get_nt_pvalues_df()
        else:
            medium_pval_df = medium.get_aa_pvalues_df()
            peptstim_pval_df = peptstim.get_aa_pvalues_df()

    min_medium_pvalues = [min(medium_pval_df.ix[index]) for index in medium_pval_df.index.values]
    min_medium_pvalues_df = DataFrame(min_medium_pvalues, index=medium_pval_df.index.values)

    min_peptstim_pvalues = [min(peptstim_pval_df.ix[index]) for index in peptstim_pval_df.index.values]
    min_pvalues_stim_df = DataFrame(min_peptstim_pvalues, index=peptstim_pval_df.index.values)

    df = concat([min_medium_pvalues_df, min_pvalues_stim_df], axis=1)
    #assume that clonotypes not present in neg ctrl are not expanded = assign a 1 p-value
    #assume that clonotypes not present in selected subset of stim samples are not expanded and were in the cultured assay before stimulation
    df = df.fillna(1)
    #assume that we cannot give an expansion value to clonotypes that are not found in stimulated or in negative control samples
    #df=df.dropna()
    df.columns = ["x cultures", "y cultures"]

    return df



def assign_min_max_pvals(medium=None, irr_pep_stim=None, rel_pep_stim=None, rel_pval=0.05, double_positive=False):

    # print(isinstance(medium, ClonotypeSamples))

    if medium is not None:
        medium_pval_df = medium.get_aa_pvalues_df()

    # rel_pep_stim_pval_df = rel_pep_stim.get_aa_clonotypesList_with_pvalue_lower_than(threshold=rel_pval).get_aa_pvalues_df()

    rel_pep_stim_pval_df = rel_pep_stim.get_aa_clonotypesList().get_aa_clonotypes_df_with_at_least_pvalue_lower_than(threshold=rel_pval)

    # rel_pep_stim.get_aa_clonotypesList().get_aa_clonotype_cell_count_corresp_to_pvalues()
    # print("rel_pep_stim_pval_df: ", rel_pep_stim_pval_df)
    # print("rel_pep_stim: ", rel_pep_stim.get_sample_ids())
    # clonotype_id = "CASSEAHPGTVSGNTIYF_TCRBV02-01_TCRBJ01-03"

    clonotype_id = medium.get_aa_clonotype_id_df_by_clonotype_index(10404)

    if clonotype_id is not None:
        print("clonotype id: ", clonotype_id)
        print("index_cdr3: ", 10404)
        print("medium.ix[index_cdr3]: ", medium_pval_df.ix[10404])

    clonotype_id = "CASSYSISGNTEAFF_TCRBV06-06_TCRBJ01-01"

    index_cdr3 = rel_pep_stim.get_aa_clonotype_index_df_by_clonotype_id(clonotype_id)

    # print("rel_pep_stim_pval_df: ", rel_pep_stim_pval_df)

    if index_cdr3 is not None:
        print("clonotype id: ", clonotype_id)
        print("index_cdr3: ", index_cdr3)
        print("rel_pep_stim_pval_df.ix[index_cdr3]: ", rel_pep_stim_pval_df.ix[index_cdr3])

    #rel_pep_stim_pval_df = rel_pep_stim.get_aa_pvalues_df()

    irr_pep_stim_pval_df = irr_pep_stim.get_aa_pvalues_df()
    if medium is not None:
        df_negcontrol = concat([medium_pval_df, irr_pep_stim_pval_df], axis=1)
    else:
        df_negcontrol = irr_pep_stim_pval_df

    # print("before df_negcontrol: ", df_negcontrol)

    df_negcontrol = df_negcontrol.fillna(1)

    # print("after df_negcontrol: ", df_negcontrol.ix[10404][0])

    min_pvalues = [min(df_negcontrol.ix[index]) for index in df_negcontrol.index.values]
    min_pvalues_negcontrol_df = DataFrame(min_pvalues, index=df_negcontrol.index.values)

    # print("after df_negcontrol: ", min_pvalues_negcontrol_df.ix[10404][0])
    # print("min_pvalues_negcontrol_df: ", min_pvalues_negcontrol_df)

    indexes = rel_pep_stim_pval_df.index.values

    # print('rel_pep_stim_pval_df: ', rel_pep_stim_pval_df.iloc[1:10])
    # print("rel_pep_stim_pval_df: ", rel_pep_stim_pval_df)
    # max_pvalues = [max(rel_pep_stim_pval_df.ix[index].fillna(0)) for index in indexes]

    max_pvalues = [max(rel_pep_stim_pval_df.ix[index].fillna(0).iloc[where(rel_pep_stim_pval_df.ix[index].fillna(1) < rel_pval)[0]]) for index in indexes]

    #max_pvalues = [max(pepstim_pval_exp_df.ix[index].fillna(0)) for index in indexes]

    max_pvalues_stim_df = DataFrame(max_pvalues, index=indexes)

    # print('max_pvalues_stim_df: ', max_pvalues_stim_df)
    # print("min_pvalues_negcontrol_df.ix[8]: ",min_pvalues_negcontrol_df.ix[258])
    # print("max_pvalues_stim_df.ix[8]: ", max_pvalues_stim_df.ix[258])

    df = concat([max_pvalues_stim_df, min_pvalues_negcontrol_df], axis=1)

    # print(df.ix[index_cdr3])
    #assume that clonotypes not present in neg ctrl are not expanded = assign a 1 p-value
    #assume that clonotypes not present in selected subset of stim samples are not expanded and were in the cultured assay before stimulation

    df = df.fillna(1)

    #assume that we cannot give an expansion value to clonotypes that are not found in stimulated or in negative control samples
    #df=df.dropna()

    df.columns = ["relevant", "irrelevant"]

    # print("df: ", df)

    return df

def produce_medium_only_vs_pepstim_pvalues(path_tables_and_figures_folder, mediums, pepstim_dict, pvalue_threshold=0.001 , bonferroni=True):
    for pept in  pepstim_dict.keys():
        selected_pep_stims = pepstim_dict[pept]
        df = assign_min_pvals(mediums, selected_pep_stims)
        subject_id = mediums.get_subject_ids()
        plot_comparison_medium_vs_pepstim_pvalues_final(path_tables_and_figures_folder, df, subject_id, pept)

def plot_comparison_negctrl_vs_pepstim_pvalues(path_tables_and_figures_folder, exvivo, tetramer, medium, irrpepstim, pepstim,
                                               tetramer_sp=['exvivo, tetramer stain'],
                                               culture_thresholds=[1e-20, 1e-3],
                                               pvalue_threshold=0.001, bonferroni=True, double_positive=False):

    negctrl_threshold = culture_thresholds[1]
    rel_pepstim_threshold = culture_thresholds[0]

    if bonferroni:
        samples = []
        samples.extend(tetramer)
        samples.append(exvivo)
        pvalue_threshold = bonferroni_calculation(ClonotypeSamples(samples=samples,
                                                                   comparisonDataSet=exvivo.comparisonDataSet),
                                                  clonotype_level="amino acid")

    tet_aa_clonotypes_exp = tetramer.get_expanded_aa_clonotypesList_with_sample_specific_threshold(pvalue_threshold)

    if double_positive:
        print("double positive")
        tet_df=tet_aa_clonotypes_exp.get_pvalues_df()
        print("tet: ", tet_df)
        tet_df=tet_df.dropna(inplace=True)
        # tet_df.index
        tet_aa_clonotypes_exp = tet_aa_clonotypes_exp
    else:
        tet_pval_exp_clonotype_index = tet_aa_clonotypes_exp.get_clonotype_index()

    df = assign_min_max_pvals(medium, irrpepstim, pepstim)#, rel_pval=0.05

    # print("pepstim  + negctrl: ", [rel_pepstim_threshold, negctrl_threshold])

    #---
    df_test = df.iloc[where((df["relevant"] <= rel_pepstim_threshold) & (df["irrelevant"] >= negctrl_threshold))[0]]

    print("df_test: ", df_test)

    exvivo_df = exvivo.get_cell_counts_by_clonotype_index(clonotype_index=df_test.index.values)
    exvivo_df.rename("ex vivo # cells", inplace=True)

    aa_clonotype_ids_df = pepstim.get_aa_clonotypesList().get_aa_clonotype_ids_df_by_clonotype_index(df_test.index.values)

    # print("aa_clonotype_ids_df: ", aa_clonotype_ids_df)
    # print("aa_clonotype_ids.tolist: ", aa_clonotype_ids_df.tolist())

    medium_cell_count_df = medium.get_aa_clonotype_cell_count_corresp_to_pvalues(df_test["irrelevant"])
    irrpepstim_cell_count_df = irrpepstim.get_aa_clonotype_cell_count_corresp_to_pvalues(df_test["irrelevant"])
    relpepstim_cell_count_df = pepstim.get_aa_clonotype_cell_count_corresp_to_pvalues(df_test["relevant"])

    print('medium_cell_count_df: ', medium_cell_count_df)
    print('irrpepstim_cell_count_df: ', irrpepstim_cell_count_df)

    clonotype_indexes = list(set(list(concatenate(
        [medium_cell_count_df.index.values, irrpepstim_cell_count_df.index.values,
         relpepstim_cell_count_df.index.values]))))

    irrel_cell_counts = []
    rel_cell_counts = []

    for index in clonotype_indexes:
        if index in medium_cell_count_df.index.values:
            irrel_cell_counts.append(medium_cell_count_df.ix[index])
        elif index in irrpepstim_cell_count_df.index.values:
            irrel_cell_counts.append(irrpepstim_cell_count_df.ix[index])
        else:
            irrel_cell_counts.append(0)

        if index in relpepstim_cell_count_df.index.values:
            rel_cell_counts.append(relpepstim_cell_count_df.ix[index])

    irr_cell_counts_s = Series(irrel_cell_counts, index=clonotype_indexes, name="irrelevant # cells")
    rel_cell_counts_s = Series(rel_cell_counts, index=clonotype_indexes, name="relevant # cells")

    # "subject_id", "reference experiment", "thresholds_irrel_rel", "relevant peptide culture # cells", "irrelevant peptide culture # cells"
    num_rows = len(exvivo_df.index.values)

    optimal_thresholds_s = Series(['{:.2e}'.format(negctrl_threshold) + ", " + '{:.2e}'.format(rel_pepstim_threshold)]*num_rows, name='p-value thresholds [irrelevant, relevant]', index = exvivo_df.index.values)
    subject_id_s = Series([tetramer.get_subject_ids()[0]]*num_rows, name='subject_id', index = exvivo_df.index.values)
    ref_exp_s = Series([str(tetramer_sp)]*num_rows, name='reference experiment', index = exvivo_df.index.values)
    tet_binding = Series(['False']*num_rows, name='tetramer binding clonotype', index = exvivo_df.index.values)

    # print('tet_binding: ', tet_binding)
    # print(tet_pval_exp_clonotype_index)

    tet_binding.ix[intersect1d(exvivo_df.index.values,tet_pval_exp_clonotype_index)] = 'True'

    rel_pvalues_s = Series(['{:.2e}'.format(x) for x in df_test['relevant']], name='relevant p-value', index = exvivo_df.index.values)
    irrel_pvalues_s = Series(['{:.2e}'.format(x) for x in df_test['irrelevant']], name='irrelevant p-value', index=exvivo_df.index.values)

    df_exvivo = concat([ subject_id_s, optimal_thresholds_s, rel_cell_counts_s, ref_exp_s, exvivo_df, irr_cell_counts_s, rel_pvalues_s, irrel_pvalues_s, tet_binding], axis=1)

    df_exvivo.index = aa_clonotype_ids_df.tolist()
    df_exvivo.reset_index(level=0, inplace=True)

    df_exvivo.columns = concatenate([["clonotype ID"], df_exvivo.columns[1:len(df_exvivo.columns.values)]])

    print(df_exvivo)

    df_exvivo.to_csv(path_tables_and_figures_folder + tetramer.get_subject_ids()[0] + str(tetramer_sp) + "_selected_clns.csv")

    print('test1 # exp selected: ', len(df_test.index.values))
    tet_clonotype_ids_test = intersect1d(array(tet_pval_exp_clonotype_index), array(df_test.index.values))
    print('test2 # tet intersect: ', len(tet_clonotype_ids_test))

    #---

    #remove clonotypes not expanded in tetramer peptide relevant samples
    index_mod_lower_0_05 = where(df["relevant"] < 0.05)[0]
    df = df.iloc[index_mod_lower_0_05]

    print('#clns p-value < 0.05: ', len(index_mod_lower_0_05))


    selected_intersect_tet_clonotype_index = intersect1d(array(tet_pval_exp_clonotype_index), array(df.index.values))

    df_tet_pval = df.ix[selected_intersect_tet_clonotype_index]

    plot_comparison_negctrl_vs_pepstim_pvalues_final(path_tables_and_figures_folder, df, tetramer, df_tet_pval,
                                                     negctrl_threshold, rel_pepstim_threshold,
                                                     tetramer_sp=tetramer_sp, double_positive=double_positive)

def prepare_medium_only_vs_pepstim_pval_plot(samples):
    all_pept = samples.get_peptide_sequences()
    pepstim_dict = {}
    # print(all_pept)
    # print(list(all_pept))
    for pept in all_pept:
        # print(pept)
        # print(list(pept))
        pepstim_dict[pept] = samples.get_samples_by_peptide_sequences([pept])
    #pepstim = samples.get_samples_by_peptide_sequences(list(all_pept), selection="or")
    medium = samples.get_samples_by_experiment_types(['medium culture'])
    return medium, pepstim_dict

def prepare_validation_plot(samples, tetramer_sp=['exvivo, tetramer stain'], double_positive=False):
    all_pept = samples.get_peptide_sequences()

    print(samples.get_sample_ids())
    print("positive control: ", tetramer_sp)

    if double_positive:
        positive_control = samples.get_samples_by_peptide_sequences(tetramer_sp, selection="or")
    else:
        positive_control = samples.get_samples_by_experiment_types(tetramer_sp, selection="or")#.exclude_on_experiment_types(['peptide culture'])

    print("positive_control: ", positive_control)

    relevant_peptide_sequence = positive_control.get_peptide_sequences()
    irrelevant_peptide_sequence = setdiff1d(all_pept, relevant_peptide_sequence)

    irr_pep_stim = samples.get_samples_by_peptide_sequences(list(irrelevant_peptide_sequence), selection="or")
    medium = samples.get_samples_by_experiment_types(['medium culture'])

    rel_pep_stim = samples.get_peptide_stimulated(relevant_peptide_sequence, experiment_type_excluded=['peptide culture, tetramer stain']) #total_cell_count_before_culture='2000000',

    exvivo = samples.get_exvivo()[0]

    return [exvivo, medium, positive_control, rel_pep_stim, irr_pep_stim]

def prepare_samples_plot(samples):
    all_pept = samples.get_peptide_sequences()

    print(samples.get_sample_ids())

    samples_to_return=[]
    samples_to_return.append(samples.get_exvivo()[0])
    print(all_pept)
    for peptide in all_pept:
        samples_to_return.append(samples.get_samples_by_peptide_sequences([peptide], selection="or"))

    return samples_to_return

def produce_validation_bar_plot_aa(paths, path_tables_and_figures_folder, filename, tetramer_sp=['exvivo, tetramer stain'], culture_thresholds=[1e-20, 1e-3]):
    if path.isfile(filename):
        df = read_csv(filename, header=None)

        compdataset = ComparisonDataSet(df, clonotype_samples_info_file=paths['path_raw_data_folder'] + 'metadata/sample_info.csv')
        samples = compdataset.samples

        exvivo, medium, tetramer, rel_pep_stim, irr_pep_stim = prepare_validation_plot(samples, tetramer_sp=tetramer_sp)

        print("tetramer samples used for validation: ", tetramer)

        validation_bar_plot_aa(path_tables_and_figures_folder, exvivo, medium, tetramer, rel_pep_stim, irr_pep_stim, tetramer_sp=tetramer_sp,culture_thresholds = culture_thresholds)
    else:
        print('WARN: ' + filename + ' does not exists.')

def produce_medium_only_vs_pepstim_pval_plot(path_tables_and_figures_folder, filename, pvalue_threshold=0.001, bonferroni=True):
    if path.isfile(filename):
        df = read_csv(filename, header=None)

        compdataset = ComparisonDataSet(df)
        samples = compdataset.samples

        mediums, pepstim_dict = prepare_medium_only_vs_pepstim_pval_plot(samples)
        if len(mediums) == 0 or len(pepstim_dict):
            print('WARN: samples are missing (medium or peptide stimulated).')
        else:
            produce_medium_only_vs_pepstim_pvalues(path_tables_and_figures_folder, mediums, pepstim_dict, pvalue_threshold=pvalue_threshold , bonferroni=bonferroni)
    else:
        print('WARN: ' + filename + ' does not exists.')

def produce_negctrl_vs_pepstim_pval_plot(paths, path_tables_and_figures_folder, filename, tetramer_sp=['exvivo, tetramer stain'],
                                         culture_thresholds=[1e-20, 1e-3], pvalue_threshold=0.001 , bonferroni=True, double_positive=False):
    if path.isfile(filename):
        df = read_csv(filename, header=None)

        compdataset = ComparisonDataSet(df, clonotype_samples_info_file = paths['path_raw_data_folder'] + 'metadata/sample_info.csv')
        samples = compdataset.samples

        exvivo, medium, tetramer, rel_pep_stim, irr_pep_stim = prepare_validation_plot(samples, tetramer_sp=tetramer_sp)

        plot_comparison_negctrl_vs_pepstim_pvalues(path_tables_and_figures_folder, exvivo, tetramer, medium, irr_pep_stim,
                                                   rel_pep_stim, tetramer_sp=tetramer_sp, culture_thresholds=culture_thresholds,
                                                   pvalue_threshold=pvalue_threshold , bonferroni=bonferroni, double_positive=double_positive)
    else:
        print('WARN: ' + filename + ' does not exists.')

def produce_figures_and_tables_by_clonotype_level(paths, filename, sequence_level, pvalue_threshold=0.001, level_of_output_detail="detailed", bonferroni=True):
    # plot_frequencies_compared_to_exvivo_by_filename(paths, filename, sequence_level, pvalue_threshold=pvalue_threshold, bonferroni=bonferroni, level_of_output_detail="detailed")
    return plot_comparison_btw_2_sp_pvalues_by_filename(paths, filename, sequence_level, bonferroni=bonferroni, level_of_output_detail=level_of_output_detail)

def produce_figures_and_tables(paths, filename_nt=None, filename_aa=None, pvalue_threshold=0.001, bonferroni=True, level_of_output_detail="detailed"):
    if filename_nt is not None:
        return produce_figures_and_tables_by_clonotype_level(paths, filename_nt, 'nucleotide', pvalue_threshold=pvalue_threshold, bonferroni=bonferroni, level_of_output_detail=level_of_output_detail)
    else:
        return produce_figures_and_tables_by_clonotype_level(paths, filename_aa, 'amino acid', pvalue_threshold=pvalue_threshold, bonferroni=bonferroni, level_of_output_detail=level_of_output_detail)

# return subsets corresponding to intervals and medians of each of subsets
def regroup_values_for_each_defined_intervals(data, nb_class):
        list_of_percentiles = []

        percentile_var = 1./nb_class
        print('# of intervals: ', nb_class)
        print('percentile: ', percentile_var)

        for rank in range(nb_class-1):
            factor = rank + 1
            list_of_percentiles.append(percentile(data, factor*percentile_var*100))

        list_of_percentiles = Series(list_of_percentiles).drop_duplicates().tolist()

        print("data: ", data)
        print('interval limits: ', list_of_percentiles)

        # list_of_percentiles = list(set(list_of_percentiles))
        if len(list_of_percentiles) == 1:
            print("An interval should be separated by 2 values.")

        subsets = []
        avgs = []

        s = Series(data)

        for rank in range(len(list_of_percentiles)):

            # print('rank exvivo cell count: ', list_of_percentiles[rank])

            if (rank == 0) & (len(list_of_percentiles) == 1):
                # print('data', data)
                # print('list_of_percentiles[rank]: ', list_of_percentiles[rank])

                subset = s[s <= list_of_percentiles[rank]]

                subsets.append(subset)
                avgs.append(median(subset))

                subset = s[s > list_of_percentiles[rank]]

                if len(subset) == 0:
                    return [subsets, avgs]

            elif rank == 0:
                # print('data', data)
                # print('list_of_percentiles[rank]: ', list_of_percentiles[rank])

                subset = s[s <= list_of_percentiles[rank]]

            elif rank == (len(list_of_percentiles) - 1):
                # s = Series(data)
                # subset = s.iloc[where((s > list_of_percentiles[rank - 1]) & (s <= list_of_percentiles[rank]))[0]]
                # subsets.append(subset)
                # avgs.append(median(subset))

                print('end ', list_of_percentiles[rank])
                subset = s[s > list_of_percentiles[rank]]

                # subsets.append(subset)
                # avgs.append(median(subset))

            # elif list_of_percentiles[rank - 1] != list_of_percentiles[rank]:
            #     s = Series(data)
            #     subset = s.iloc[where((s > list_of_percentiles[rank - 1]) & (s <= list_of_percentiles[rank]))[0]]
            #     # subsets.append(subset)
            #     # avgs.append(median(subset))
            # elif (list_of_percentiles[rank - 1] == list_of_percentiles[rank]):
            #     if len(list_of_percentiles) < (rank + 1):
            #         if (list_of_percentiles[rank] != list_of_percentiles[rank + 1]):
            #             s = Series(data)
            #             subset = s.iloc[where((s >= list_of_percentiles[rank - 1]) & (s <= list_of_percentiles[rank]))[0]]
            #     else:
            #         s = Series(data)
            #         subset = s.iloc[where((s >= list_of_percentiles[rank - 1]) & (s <= list_of_percentiles[rank]))[0]]
            else:
                subset = s.iloc[where((s > list_of_percentiles[rank - 1]) & (s <= list_of_percentiles[rank]))[0]]

            if len(subset) > 0:
                subsets.append(subset)
                avgs.append(median(subset))
            else:
                #raise BaseException, "No values for subset threshold: " + str(list_of_percentiles[rank]) + " - " + str(rank)
                print("No values for subset threshold: " + str(list_of_percentiles[rank]) + " - " + str(rank))

        return [subsets, avgs]

'''
Tries to redelimit intervals if they have more than 2 fold or less than 0.5 fold compared to others
'''
def scale_exvivo_cat(temp_exvivo_cell_counts, subsets_box):
        len_subsets = [len(subset) for subset in subsets_box]

        print('len subsets: ', len_subsets)

        if len(len_subsets) > 1:
            for index in arange(0, len(len_subsets)):
                if index == len(len_subsets) - 1:
                    #print('returned values: ', subsets_box[0])
                    return subsets_box
                elif ((len_subsets[index] / float(len_subsets[index+1])) > 2) or ((len_subsets[index] / float(len_subsets[index+1])) < 0.5):
                    initial_subsetbox = subsets_box[0]
                    maxi = max(initial_subsetbox)

                    #print('maxi cell count: ', maxi)

                    temp_exvivo_cell_counts = temp_exvivo_cell_counts[where(temp_exvivo_cell_counts > maxi)[0]]
                    num_cat = len(len_subsets) - (index + 1)
                    subsets_box, avgs = regroup_values_for_each_defined_intervals(temp_exvivo_cell_counts, num_cat)
                    #print('subsets_box rec: ', subsets_box[0])
                    num_cat = len(subsets_box)
                    if num_cat > 2:
                        mylist = scale_exvivo_cat(temp_exvivo_cell_counts, subsets_box)
                        l = [initial_subsetbox]
                        l.extend(mylist)
                        return l
                    elif len(subsets_box) == 1:
                        return [initial_subsetbox, subsets_box[0]]
                    elif len(subsets_box) == 2:
                        return [initial_subsetbox, subsets_box[0], subsets_box[1]]
                    else:
                        return []
        return []

'''
Reduce the number of intervals until there is at least 80 cells for each of the intervals.
A minimum number of 3 intervals is used.
Tries to redelimit intervals if they have more than 2 fold or less than 0.5 fold compared to others.
'''
def initiate_bins(exvivo_cell_counts, min_cells=40):
    exvivo_cell_counts_keys = sorted(list(set(exvivo_cell_counts)))

    print('exvivo_cell_counts_keys: ', exvivo_cell_counts_keys)

    # num_cat = len(pvalues)

    exvivo_cell_counts_bins = []
    pval_bins = []

    #maximum number of interval allowed.
    num_cat_dynamic_threshold = 10
    not_good = True

    while not_good:
        subsets_box, avgs = regroup_values_for_each_defined_intervals(exvivo_cell_counts, num_cat_dynamic_threshold)
        num_cat_dynamic_threshold = len(subsets_box)

        print('avgs: ', avgs)
        print('lengths: ', map(len, list(subsets_box)))

        for subset in subsets_box:
            if len(subset) < min_cells:

                # print('failure subset: ', len(subset))
                # print('avg: ', subsets_box[1])

                num_cat_dynamic_threshold = num_cat_dynamic_threshold - 1

                print('num_cat_dynamic_threshold: ', num_cat_dynamic_threshold)

                not_good = True
                break

            not_good = False

        if num_cat_dynamic_threshold <= 3:
            #print('!!! percentile_threshold too low !!!')
            not_good = False

    # print('num_cat_dynamic_threshold: ', num_cat_dynamic_threshold)
    # print('len exvivo subset bef: ', [len(subset) for subset in subsets_box[0]])
    # print('final number class exvivo: ', percentile_threshold)

    temp_exvivo_cell_counts = array(exvivo_cell_counts)

    # selected_subsets = scale_exvivo_cat(temp_exvivo_cell_counts, subsets_box)

    selected_subsets = subsets_box

    # print('selected_subsets: ', selected_subsets)

    #for subset in subsets_box[0]:
    for subset in selected_subsets:
        if len(subset) > 0:
            # print('subset: ', subset)
            print('[len(subset), min(subset), max(subset)]: ', [len(subset), min(subset), max(subset)])
            exvivo_cell_counts_bins.append([min(subset), max(subset)])

    # print('len exvivo subset af: ', [len(subset) for subset in selected_subsets])

    # subsets_box, avgs = regroup_values_for_each_defined_intervals(sorted(list(set(list(concatenate(pvalues.tolist())))), reverse=True), num_cat)
    #
    # for subset in subsets_box:
    #     if len(subset) > 0:
    #         pval_bins.append([max(subset), min(subset)])

    print('exvivo_cell_counts_bins: ', exvivo_cell_counts_bins)
    # print('# pval bins: ', len(pval_bins))

    return exvivo_cell_counts_bins

'''
Merge pvalue rows if one square does not contain number of data points superior to a threshold = min_dpps for an exvivo cell count interval
'''
def redelimit_reproducibility_heatmap_intervals_based_on_min_dpps(new_matrix, pval_bins, min_dpps=20):
    # print('init_matrix: ', new_matrix)

    final_index = len(new_matrix.index.values)

    not_normalised = True

    row_index_mod = 0

    merged_row_index = []

    while not_normalised:

        count_small_num_clonotype_per_square_index_mod = where(new_matrix.iloc[row_index_mod] < min_dpps)[0]

        #test condition if the last row of the matrix contains squares with lower dpps and merge if it is the case
        if (len(count_small_num_clonotype_per_square_index_mod) > 0) & (row_index_mod == len(new_matrix.index.values) - 1):

            #case there is only 2 rows
            if row_index_mod == 1:
                new_row = array(new_matrix.iloc[row_index_mod]) + array(new_matrix.iloc[row_index_mod-1])
                new_matrix = DataFrame(new_row, columns=[myindex]).T
            else:
                #merge the new row to the previous dataframe without the last 2 rows
                new_row = array(new_matrix.iloc[row_index_mod]) + array(new_matrix.iloc[row_index_mod-1])
                new_matrix = concat([new_matrix.iloc[0:row_index_mod-1], DataFrame(new_row, columns=[myindex]).T], axis=0)

            #finalise merged row index list
            if len(merged_row_index) > 0:
                min_df_index = min(merged_row_index[len(merged_row_index)-1])

                del merged_row_index[len(merged_row_index)-1]

                merged_row_index.append(list(arange(min_df_index, final_index)))
            else:
                merged_row_index.append(list(arange(0, final_index)))

            not_normalised = False

        elif len(count_small_num_clonotype_per_square_index_mod) > 0:
            new_row = array(new_matrix.iloc[row_index_mod]) + array(new_matrix.iloc[row_index_mod+1])
            myindex = new_matrix.index.values[row_index_mod]

            #merge the 2 first rows and concat it to the rest of the matrix
            if row_index_mod == 0:
                new_matrix = concat([DataFrame(new_row, columns=[myindex]).T, new_matrix.iloc[row_index_mod+2:len(new_matrix.index)]], axis=0)
            else:
                #merge lower, middle and upper part of the dataframe
                new_matrix = concat([new_matrix.iloc[0:row_index_mod], DataFrame(new_row, columns=[myindex]).T, new_matrix.iloc[row_index_mod+2:len(new_matrix.index)]], axis=0)
        #case last row of the matrix contains enougth dpps
        elif (row_index_mod == len(new_matrix.index.values) - 1):
            min_df_index = new_matrix.index.values[row_index_mod]
            merged_row_index.append(list(arange(min_df_index, final_index)))

            not_normalised = False
        else:
            next_i = row_index_mod + 1#new_matrix.index.values[i+1]
            df_before_index = new_matrix.index.values[row_index_mod]
            df_next_index = new_matrix.index.values[row_index_mod+1]
            merged_row_index.append(list(arange(df_before_index, df_next_index)))
            row_index_mod = next_i

    # print('new_matrix: ', new_matrix)
    # print('merged_row_index: ', merged_row_index)

    pvalue_bins_listoflist = []
    for index_list in merged_row_index:
        mylist = []
        for index in index_list:
            mylist.append(pval_bins[index])
        pvalue_bins_concatenated = concatenate(mylist)
        pvalue_bins_listoflist.append([max(pvalue_bins_concatenated), min(pvalue_bins_concatenated)])

    return new_matrix, pvalue_bins_listoflist

def autogenerate_matrix_classes(exvivo_cell_counts_bins, pval_bins, pvalues_by_exvivo_cell_count_dict, clonotypes_reproducibility, min_dpps=10):
    initial_matrix = []

    # print('exvivo_cell_counts_bins: ', exvivo_cell_counts_bins)

    for j in range(len(exvivo_cell_counts_bins)):
        min_count, max_count = exvivo_cell_counts_bins[j]
        selected_exvivo_counts_index_mod = where((Series(list(clonotypes_reproducibility.keys())) >= min_count) & (Series(list(clonotypes_reproducibility.keys())) <= max_count))[0]
        selected_exvivo_counts = array(Series(list(clonotypes_reproducibility.keys())).iloc[selected_exvivo_counts_index_mod])

        list_clonotypes = []

        #pvalues of clonotypes found to have a number of cell exvivo comprise between min_count and max_count for each samples
        pvalues = {}

        for exvivo_count in selected_exvivo_counts:
            c = clonotypes_reproducibility[exvivo_count]

            list_clonotypes.extend(list(c.keys()))

            for sample_id in pvalues_by_exvivo_cell_count_dict[exvivo_count].keys():
                if sample_id in pvalues.keys():
                    data = pvalues_by_exvivo_cell_count_dict[exvivo_count][sample_id]
                    new_data = pvalues[sample_id]

                    append_new_data_pvalues = new_data.tolist()
                    append_new_data_pvalues.extend(data.tolist())

                    append_new_data_index = list(new_data.index.values)
                    append_new_data_index.extend(data.index.values)

                    pvalues[sample_id] = Series(append_new_data_pvalues, index=append_new_data_index)
                else:
                    pvalues[sample_id] = pvalues_by_exvivo_cell_count_dict[exvivo_count][sample_id]

        clon_index_col = list_clonotypes

        # print('pvalues_by_exvivo_cell_count_dict: ', pvalues_by_exvivo_cell_count_dict)

        # print('sample IDs: ', pvalues.keys())
        # print('# samples: ', len(pvalues.keys()))

        columns_to_sum = []
        for sample_id in pvalues.keys():
            data = pvalues[sample_id]
            matrix_column = []
            for i in range(len(pval_bins)):
                max_val, min_val = pval_bins[i]

                pval_row = data.iloc[where((data >= min_val) & (data <= max_val))[0]]

                if len(pval_row) > 0:
                    cindex=list(pval_row.index)
                    clonotype_per_square = len(intersect1d(cindex, clon_index_col))
                    matrix_column.append(clonotype_per_square)
                else:
                    matrix_column.append(0)
            columns_to_sum.append(matrix_column)

        if len(pvalues.keys()) == 1:
            col_summed = array(columns_to_sum[0])
        else:
            col_summed = array(columns_to_sum[0]) + array(columns_to_sum[1])
            # print('len col: ', len(col_summed))
        initial_matrix.append(list(col_summed))

    #list of columns
    new_matrix = DataFrame(initial_matrix).T

    return redelimit_reproducibility_heatmap_intervals_based_on_min_dpps(new_matrix, pval_bins, min_dpps)


def pvalues_by_exvivo_cell_count_dict_and_clonotypes_reproducibility_dict_factory(samples=[],
                                                    expanded_clonotypes_by_samples=[], exvivo_cell_counts_bins=[],
                                                    exvivo_cell_counts=[], pvalues=[]):

    pvalues_by_exvivo_cell_count_dict={}
    clonotypes_reproducibility_dict={}

    for index in range(len(exvivo_cell_counts_bins)):
        interval = exvivo_cell_counts_bins[index]
        min_exvivo = int(interval[0])
        max_exvivo = int(interval[1])
        sample_pvalues_per_exvivo_cell_count={}

        # print('min-max exvivo: ', [min_exvivo, max_exvivo])

        clonotype_ids_occurence_overall_sp = []

        for sample_index in range(len(expanded_clonotypes_by_samples)):
            expanded_clonotypes_index = expanded_clonotypes_by_samples[sample_index]

            exvivo_cell_counts_index_mod = where((exvivo_cell_counts >= min_exvivo) & (exvivo_cell_counts <= max_exvivo))[0]

            expanded_clonotypes_index = intersect1d(list(exvivo_cell_counts.iloc[exvivo_cell_counts_index_mod].index), list(expanded_clonotypes_index))
            # expanded_clonotypes_index_not_exvivo = setdiff1d(list(expanded_clonotypes_index), list(exvivo_cell_counts.iloc[exvivo_cell_counts_index_mod].index))

            # print('expanded_clonotypes not in exvivo subset: ', len(expanded_clonotypes_index_not_exvivo))
            # print('# expanded clonotypes: ', len(expanded_clonotypes_index))

            if len(expanded_clonotypes_index) > 0:
                # print('pvalues: ', pvalues[sample_index])
                # print('expanded_clonotypes_index: ', expanded_clonotypes_index)
                # print('len expanded_clonotypes: ', len(intersect1d(expanded_clonotypes_index, pvalues[sample_index].index.values)))

                # print('type pvalues[sample_index]: ', type(pvalues[sample_index]))

                # print('sample ID: ', samples[sample_index].ID)
                # print('pvalues[sample_index]: ', pvalues[sample_index])

                sample_pvalues_per_exvivo_cell_count[samples[sample_index].ID] = pvalues[sample_index].ix[expanded_clonotypes_index]
                clonotype_ids_occurence_overall_sp.append(expanded_clonotypes_index)

        if len(clonotype_ids_occurence_overall_sp) > 0:
            c = Counter(concatenate(clonotype_ids_occurence_overall_sp))
            clonotypes_reproducibility_dict[min_exvivo]=c

        # print('sample_pvalues_per_exvivo_cell_count values: ', sample_pvalues_per_exvivo_cell_count.values())
        # print('sample_pvalues_per_exvivo_cell_count : ', sample_pvalues_per_exvivo_cell_count)

        if len(sample_pvalues_per_exvivo_cell_count.values()) > 0:
            # if len(DataFrame(sample_pvalues_per_exvivo_cell_count).values) > 0:
                # print('[min_exvivo, [values]: ', [min_exvivo, len(DataFrame(sample_pvalues_per_exvivo_cell_count).values)])

                # print('sample_pvalues_per_exvivo_cell_count: ', sample_pvalues_per_exvivo_cell_count)

            pvalues_by_exvivo_cell_count_dict[min_exvivo] = sample_pvalues_per_exvivo_cell_count

    # print('pvalues_by_exvivo_cell_count_dict: ', pvalues_by_exvivo_cell_count_dict)

    return [pvalues_by_exvivo_cell_count_dict, clonotypes_reproducibility_dict]

'''
returns a list containing a list with sample id, corresponding cell count exvivo, index for input pvalue interval,
number of clonotypes for the cell count exvivo, number of clonotypes for the pvalue interval for clonotypes with the
input number of cell count exvivo, number of reproduced clonotypes for exvivo counts, number of clonotypes reproduced
and in the pvalue interval
'''
def class_pval(k, min_exvivo, data, clon_reprod_index, results, min_val, max_val, i):
    subset = data.iloc[where((data >= min_val) & (data <= max_val))[0]]
    if len(subset) > 0:
        cindex = list(subset.index)
        results.append([k, min_exvivo, i, len(data), len(cindex), len(clon_reprod_index), len(intersect1d(cindex, clon_reprod_index))])
    else:
        # print('min, no clonotype in ' + str(i) + ': ', min_exvivo)
        results.append([k, min_exvivo, i, len(data), 0, len(clon_reprod_index), 0])
    return results

'''
Produce a heatmap of reproduced clonotype between 2 samples
min_dpps: minimum data points per square
'''
def plot_reprod_heatmap_between_replicates(path_tables_and_figures_folder, exvivo, sample1, sample2,
                                           clonotype_level='nucleotide', pvalue_threshold=0.001, min_dpps=10,
                                           n_rep=1, bonferroni=True):

    if bonferroni:
        samples = []
        samples.extend(sample1)
        samples.extend(sample2)
        samples.append(exvivo)
        bonf_thresholds_reps = bonferroni_calculation(ClonotypeSamples(samples=samples,
                                                                  comparisonDataSet=exvivo.comparisonDataSet),
                                                 clonotype_level=clonotype_level)

    print("bonf_thresholds_reps: ", bonf_thresholds_reps)

    # step 1: selecting expanded clonotypes
    if clonotype_level == "amino acid":
        rep1_pvalues = sample1.get_expanded_aa_clonotypesList_with_sample_specific_threshold(
            bonf_thresholds_reps, sample_ids=[sample1[0].ID]).get_pvalues_df()
        rep2_pvalues = sample2.get_expanded_aa_clonotypesList_with_sample_specific_threshold(
            bonf_thresholds_reps, sample_ids=[sample2[0].ID]).get_pvalues_df()
    else:
        rep1_pvalues = sample1.get_expanded_nt_clonotypesList_with_sample_specific_threshold(
            bonf_thresholds_reps, sample_ids=[sample1[0].ID]).get_pvalues_df()
        rep2_pvalues = sample2.get_expanded_nt_clonotypesList_with_sample_specific_threshold(
            bonf_thresholds_reps, sample_ids=[sample2[0].ID]).get_pvalues_df()

    # rep1_pvalues = sample1.get_expanded_pvalues(threshold=pvalue_threshold)
    # rep2_pvalues = sample2.get_expanded_pvalues(threshold=pvalue_threshold)

    sample1 = sample1[0]
    sample2 = sample2[0]

    clonotypes_index = list(set(concatenate([rep1_pvalues.index, rep2_pvalues.index])))

    if len(intersect1d(rep1_pvalues.index, rep2_pvalues.index)) == 0:
        print("No intersection between " + sample1.ID + " and " + sample2.ID)
    else:
        print("# clns intersecting between " + sample1.ID + " and " + sample2.ID + ": ", str(len(intersect1d(rep1_pvalues.index, rep2_pvalues.index))) )

    rep1_counts = exvivo.get_cell_counts_by_clonotype_index(clonotype_index=rep1_pvalues.index)
    rep1_counts.fillna(0, inplace=True)

    rep2_counts = exvivo.get_cell_counts_by_clonotype_index(clonotype_index=rep2_pvalues.index)
    rep2_counts.fillna(0, inplace=True)

    print('---- ' + sample1.ID + '_vs_' + sample2.ID + ' ----')
    print('--- Building total clonotype count matrix and intervals ---')

    exvivo_cell_counts_nr = exvivo.get_cell_counts_by_clonotype_index(clonotype_index=clonotypes_index)
    exvivo_cell_counts_nr.fillna(0, inplace=True)

    exvivo_cell_counts_r = concatenate([rep1_counts.values, rep2_counts.values])
    combined_pvalues = concatenate([rep1_pvalues.values, rep2_pvalues.values])

    #step 2:
    exvivo_cell_counts_bins = initiate_bins(exvivo_cell_counts_r)

    uniq_combined_pvalues_s = sorted(list(set(list(concatenate(combined_pvalues.tolist())))), reverse=True)

    pval_bins = []
    subsets_box, avgs = regroup_values_for_each_defined_intervals(uniq_combined_pvalues_s, len(uniq_combined_pvalues_s))

    for subset in subsets_box:
        if len(subset) > 0:
            pval_bins.append([max(subset), min(subset)])

    print('exvivo_cell_counts_bins: ', exvivo_cell_counts_bins)
    print('pval_bins: ', pval_bins)

    pvalues_by_exvivo_cell_count_dict, clonotypes_reproducibility_dict = pvalues_by_exvivo_cell_count_dict_and_clonotypes_reproducibility_dict_factory(
                                            samples=[sample1, sample2], expanded_clonotypes_by_samples=[rep1_pvalues.index, rep2_pvalues.index],
                                            exvivo_cell_counts_bins= exvivo_cell_counts_bins,
                                            exvivo_cell_counts=exvivo_cell_counts_nr, pvalues=[rep1_pvalues, rep2_pvalues])

    print('pvalues_by_exvivo_cell_count_dict: ', pvalues_by_exvivo_cell_count_dict)
    print('clonotypes_reproducibility_dict: ', clonotypes_reproducibility_dict)

    total_clonotype_count_matrix_df, pvalue_bins_listoflist = autogenerate_matrix_classes(
                                                exvivo_cell_counts_bins, pval_bins, pvalues_by_exvivo_cell_count_dict,
                                                clonotypes_reproducibility_dict, min_dpps=min_dpps)

    print('total_clonotype_count_matrix_df: ', total_clonotype_count_matrix_df)

    classes_pval = []
    classes_pval_label = []
    
    for cl in pvalue_bins_listoflist:
        classes_pval.append(cl.__str__())
        # classes_pval_label.append('[$\mathregular{%.2e' % float(cl[0]) + '}$, $\mathregular{' + '%.2e' % float(cl[1]) + '}$]')
        if 0 == float(cl[0]):
            s1= '[0, '
        else:
            s1 = '[%.2e' % float(cl[0]) + ', '
        if 0 == float(cl[1]):
            s2= '0]'
        else:
            s2 = '%.2e' % float(cl[1]) + ']'

        classes_pval_label.append(s1 + s2)

    # print('classes_pval: ', classes_pval)
    print('classes_pval_label: ', classes_pval_label)

    cols = []
    for cl in exvivo_cell_counts_bins:
        cols.append([[cl[0], cl[1]]].__str__())

    cols_labels = []
    for cl in exvivo_cell_counts_bins:
        if cl[0] == cl[1]:
            cols_labels.append(str(int(cl[0])))
        else:
            cols_labels.append('[' + str(int(cl[0])) + ', ' + str(int(cl[1])) + ']')

    print('classes_exvivo_counts: ', cols_labels)
    print('--- Building reproducibility clonotype count matrix based on total clonotype count matrix intervals ---')

    reproduced_clonotype_count_matrix = []
    for exvivo_bin_index in range(len(exvivo_cell_counts_bins)):
        exvivo_bin = exvivo_cell_counts_bins[exvivo_bin_index]

        min_cell_count = exvivo_bin[0]
        max_cell_count = exvivo_bin[1]

        cell_count_sorted = sorted(pvalues_by_exvivo_cell_count_dict.keys())

        cell_count_index = where((cell_count_sorted >= min_cell_count) & (cell_count_sorted <= max_cell_count))[0]

        list_of_cell_counts = Series(cell_count_sorted).iloc[cell_count_index]
        reproduced_clonotype_count_matrix_bin=[]

        print("clns reprod df: ", DataFrame(dict(clonotypes_reproducibility_dict)))

        filename = path_tables_and_figures_folder + sample1.ID + '_vs_' + sample2.ID + '_clns_reprod_df_repr-' + str(
            n_rep) + '-pval_' \
                   + '{:.2e}'.format(bonf_thresholds_reps[sample1.ID]) + "_" + '{:.2e}'.format(
            bonf_thresholds_reps[sample2.ID]) + '-' + clonotype_level + "_mindpps_" + str(min_dpps) + '.csv'

        DataFrame(dict(clonotypes_reproducibility_dict)).to_csv(filename)

        for bin_index in range(len(pvalue_bins_listoflist)):
            max_val, min_val = pvalue_bins_listoflist[bin_index]

            print("max-min pval: ", [max_val, min_val])
            for min_exvivo in list_of_cell_counts:
                # print("min_exvivo: ", min_exvivo)

                c = clonotypes_reproducibility_dict[min_exvivo]

                # print(c.keys())
                # print(c.values())

                c_indexes = Series(list(c.keys()))
                c_values = Series(list(c.values()))

                # print("c_indexes: ", c_indexes)

                #get clonotype indexes that are replicated in at least n replicates (n_rep)
                selected_c_indexes = c_indexes[where(c_values > n_rep)[0]]

                clon_reprod_index = selected_c_indexes

                pvalues_for_cell_count = pvalues_by_exvivo_cell_count_dict[min_exvivo]
                reprod_clon_col = []
                for sample_id in pvalues_for_cell_count.keys():
                    # sample_id = pvalues_for_cell_count.keys()
                    # reprod_clon_col = []
                    sample_pvalues = pvalues_for_cell_count[sample_id]

                    subset = sample_pvalues.iloc[where((sample_pvalues >= min_val) & (sample_pvalues <= max_val))[0]]
                    if len(subset) > 0:
                        # print("subsets: ", [subset.index, clon_reprod_index])
                        cindexes = list(subset.index)
                        reprod_clon_col.append(len(intersect1d(cindexes, clon_reprod_index)))
                    else:
                        reprod_clon_col.append(0)
                    # reprod_clon_cols.append(reprod_clon_col)
            reproduced_clonotype_count_matrix_bin.append(sum(array(reprod_clon_col)))
            print(sum(array(reprod_clon_col)))

        # reproduced_clonotype_count_matrix.append(sum(array(reproduced_clonotype_count_matrix_bin), axis=0))
        reproduced_clonotype_count_matrix.append(reproduced_clonotype_count_matrix_bin)

    print('--- Building reproducibility rate matrix ---')

    reproduced_clonotype_count_matrix_df = DataFrame(reproduced_clonotype_count_matrix).T
    # reproduced_clonotype_count_matrix_df = reproduced_clonotype_count_matrix_df.sort_index(ascending=False).reset_index(drop=True)
    total_clonotype_count_matrix_df.reset_index(inplace=True, drop=True)
    reproduced_rate_df = reproduced_clonotype_count_matrix_df.divide(total_clonotype_count_matrix_df)

    print('total_clonotype_count_matrix_df: ', total_clonotype_count_matrix_df)
    print('reproduced_clonotype_count_matrix_df: ', reproduced_clonotype_count_matrix_df)
    print('reproduced_rate_df: ', reproduced_rate_df)

    if len(where(reproduced_rate_df > 1)[0]) > 0:
        print( "reproducibility is > 1 : " + sample1.ID + " and " + sample2.ID)

    rep1_ID = sample1.ID
    rep2_ID = sample2.ID

    fig, ax = plt.subplots()

    filename = path_tables_and_figures_folder + rep1_ID + '_vs_' + rep2_ID + '_heatmap_reproducibility_max_repr-'+ str(n_rep) + '-pval_' \
                                        + '{:.2e}'.format(bonf_thresholds_reps[rep1_ID]) + "_" + '{:.2e}'.format(bonf_thresholds_reps[rep2_ID]) + '-' + clonotype_level + "_mindpps_" + str(min_dpps) + '.pdf'

    Index = classes_pval
    Cols = cols
    # cax = plt.imshow(reproduced_rate_df, interpolation=None, cmap=cm.coolwarm, origin='lower', vmin=0, vmax=1).get_axes()#, aspect='auto'
    #
    # cax.set_xticks(linspace(0, len(Cols)-1, len(Cols)))
    # cax.set_xticklabels(cols_labels)
    # cax.set_yticks(linspace(0, len(Index)-1, len(Index)))
    # cax.set_yticklabels(classes_pval_label)
    #
    # cax.grid('off')
    # # cax.xaxis.tick_top()
    #
    # for i in range(len(Index)):
    #     for j in range(len(Cols)):
    #         cax.text(j, i, '{:.2f}'.format(reproduced_rate_df.iget_value(i, j)), size='small', ha='center', va='center')

    # plt.tick_params(axis='both', which='major', labelsize=6)

    # reproduced_rate_df.columns=cols

    # print("classes_pval before: ", classes_pval)
    # classes_pval.reverse()
    # print("classes_pval after rev: ", classes_pval)

    # reproduced_rate_df.indexes=classes_pval

    # print(reproduced_rate_df)

    ax = heatmap(reproduced_rate_df, ax=ax, square=True, linewidths=.5, vmin=0, vmax=1, annot=True, annot_kws={"size": 20},
                 fmt=".2f", cmap="YlGn")#, cbar_kws={"labelsize":20}

    ax.tick_params(labelsize=20)

    cax = plt.gcf().axes[-1]
    cax.tick_params(labelsize=20)

    ax.set_xticklabels(cols_labels)#, fontsize=20
    classes_pval_label.reverse()
    ax.set_yticklabels(classes_pval_label, rotation=0)#, fontsize=20

    ax.set_xlabel("# cells $\it{ex}$ $\it{vivo}$", fontsize=20)
    ax.set_ylabel("Expansion (p-value)", fontsize=20)

    savefig(filename, bbox_inches='tight')#figsize=(80, 6),

    print(filename)

    copy_df = reproduced_rate_df
    copy_df.index = classes_pval
    copy_df.columns = cols

    filename = path_tables_and_figures_folder + rep1_ID + '_vs_' + rep2_ID + '_heatmap_reproducibility_max_repr-'+ str(n_rep) + '-pval_' \
               + '{:.2e}'.format(bonf_thresholds_reps[rep1_ID]) + "_" + '{:.2e}'.format(bonf_thresholds_reps[rep2_ID]) \
               + '-' + clonotype_level + "_mindpps_" + str(min_dpps) + '.csv'

    max_reprod = copy_df.max().max()
    my_max_classes = where(copy_df == max_reprod)
    my_max_classes = list(concatenate([my_max_classes[0], my_max_classes[1]]))
    my_max_classes= [max_reprod, my_max_classes[0],  my_max_classes[1]]

    min_reprod = copy_df.min().min()
    my_min_classes = where(copy_df == min_reprod)
    my_min_classes = list(concatenate([my_min_classes[0], my_min_classes[1]]))
    my_min_classes = [min_reprod, my_min_classes[0], my_min_classes[1]]

    copy_df.to_csv(filename)

    comparison = rep1_ID + '_vs_' + rep2_ID

    print([comparison], my_max_classes, my_min_classes)

    summary_stats = concatenate([[sample1.get_subject_ids()[0]], [comparison], my_max_classes, my_min_classes])

    return summary_stats

def plot_heatmaps(path_tables_and_figures_folder, filename, sequence_level, pvalue_threshold=0.001, bonferroni=True):

    reprod_stats_summary = []

    if path.isfile(filename):

        df = read_csv(filename, header=None)

        # print(df.head())

        compdataset = ComparisonDataSet(df)
        samples = compdataset.samples

        exvivo = samples.select({'experiment':['exvivo']})[0]

        print('exvivo: ', exvivo)

        for repeats in samples.get_repeatsList():
            for index in range(len(repeats)-1):
                sample1 = ClonotypeSamples(samples=[repeats[index]])
                sample2 = ClonotypeSamples(samples=[repeats[index + 1]])
                stats_summary = plot_reprod_heatmap_between_replicates(path_tables_and_figures_folder, exvivo, sample1, sample2,
                                                       clonotype_level=sequence_level, pvalue_threshold=pvalue_threshold,
                                                       bonferroni=bonferroni, min_dpps=10)

            reprod_stats_summary.append(stats_summary)

        print(reprod_stats_summary)

        return reprod_stats_summary

    else:
        print('WARN: ' + filename + ' does not exists.')
    return None






def produce_heatmaps_by_clonotype_level(path_tables_and_figures_folder, filename, sequence_level, pvalue_threshold=0.001):
    return plot_heatmaps(path_tables_and_figures_folder, filename, sequence_level)

def produce_heatmaps(path_tables_and_figures_folder, filename_aa, pvalue_threshold=0.001):
    # produce_heatmaps_by_clonotype_level(path_tables_and_figures_folder, filename_nt, 'nucleotide', pvalue_threshold=pvalue_threshold)
    return produce_heatmaps_by_clonotype_level(path_tables_and_figures_folder, filename_aa, 'amino acid', pvalue_threshold=pvalue_threshold)