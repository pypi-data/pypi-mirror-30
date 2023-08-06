__author__ = 'jlane'


from sys import stdout, getsizeof
from pandas import DataFrame, Series, concat, read_csv
from collections import Counter
from scipy.stats import spearmanr
from numpy import where, log10, array, concatenate, intersect1d
import matplotlib.pyplot as plt
import math as sqrt

def time(i, total_iter):
        if (j % 10000) == 0:
            iter = iter + 1
            stdout.write("Progress: %d%%   \r" % ((float(iter) / total_iter) * 100))
            stdout.flush()
        j += 1
        return j

def set_limits(ax, xlim, ylim):
    ax.set_xlim(xlim[0], xlim[1])
    ax.set_ylim(ylim[0], ylim[1])
    return ax

# def set_logscale_manage_spine(ax, spines_to_set_to_invisible, kwargs):
#     # d = 0.015
#     # how big to make the diagonal lines in axes coordinates
#     # arguments to pass plot, just so we don't keep repeating them
#     kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
#
#     for spine in spines_to_set_to_invisible:
#         if "top" == spine:
#             ax.xaxis.tick_bottom()
#             # ax.tick_params(labelbottom='off')
#         if "bottom" == spine:
#             ax.xaxis.tick_top()
#             ax.tick_params(labeltop='off')
#         if "left" == spine:
#             ax.yaxis.tick_right()
#             ax.tick_params(labelright='off')
#         if "right" == spine:
#             ax.yaxis.tick_left()
#             # ax.tick_params(labelleft='off')
#         ax.spines[spine].set_visible(False)
#
#     if (len(spines_to_set_to_invisible) == 3) & ("right" in spines_to_set_to_invisible):
#         # ax.tick_params(labelleft='off')
#         ax.tick_params(labelright='off')
#         ax.tick_params(labelbottom='off')
#         ax.tick_params(labeltop='off')
#
#         ax.tick_params(right='off', which='both')
#         ax.tick_params(bottom='off', which='both')
#         ax.tick_params(top='off', which='both')
#
#
#     if (len(spines_to_set_to_invisible) == 3) & ("left" in spines_to_set_to_invisible):
#         ax.tick_params(labelright='off')
#         ax.tick_params(labelleft='off')
#         ax.tick_params(labelbottom='off')
#         ax.tick_params(labeltop='off')
#
#         ax.tick_params(right='off', which='both')
#         ax.tick_params(left='off', which='both')
#         ax.tick_params(bottom='off', which='both')
#         ax.tick_params(top='off', which='both')
#
#         ax.grid(color='gainsboro', linestyle='dashed')
#
#         myx = ax.get_xlim()[1]
#         myy = ax.get_ylim()[1]
#
#     if (len(spines_to_set_to_invisible) == 2) & ("bottom" in spines_to_set_to_invisible) & ("left" in spines_to_set_to_invisible):
#         ax.grid(color='gainsboro', linestyle='dashed')
#
#     if (len(spines_to_set_to_invisible) == 2) & ("top" in spines_to_set_to_invisible) & ("right" in spines_to_set_to_invisible):
#         ax.tick_params(labelleft='off')
#         ax.tick_params(labelbottom='off')
#         ax.tick_params(labeltop='off')
#         ax.tick_params(labelright='off')
#
#         ax.tick_params(right='off', which='both')
#         ax.tick_params(left='off', which='both')
#         ax.tick_params(bottom='off', which='both')
#         ax.tick_params(top='off', which='both')
#
#     if (len(spines_to_set_to_invisible) == 2) & ("top" in spines_to_set_to_invisible) & ("left" in spines_to_set_to_invisible):
#         ax.tick_params(labelleft='off')
#         ax.tick_params(labeltop='off')
#         ax.tick_params(labelright='off')
#
#         ax.tick_params(right='off', which='both')
#         ax.tick_params(left='off', which='both')
#         ax.tick_params(top='off', which='both')
#
#     if ("bottom" in spines_to_set_to_invisible) & ("right" in spines_to_set_to_invisible):
#         ax.tick_params(top='off', which='both')
#
#         myx = ax.get_xlim()[0]
#         myy = ax.get_ylim()[0]
#
#     ax.set_yscale('log', basey=10)
#     ax.set_xscale('log', basex=10)
#
#     ax.set_axis_bgcolor('white')
#
#     for tick in ax.get_xticklabels():
#         tick.set_rotation(45)
#
#     for tick in ax.xaxis.get_major_ticks():
#         tick.label.set_fontsize(20)
#     for tick in ax.yaxis.get_major_ticks():
#         tick.label.set_fontsize(20)
#
#     return ax, kwargs
#
# def insert_axis_info_frequencies_compared_to_exvivo(df, mymin_exvivo, mymin_invitro,
#                                                     mymin_x_line, mymin_y_line, subplots_list,
#                                                     color='silver', label=None, resize=True):
#
#     df_exvivo_nafilled = df[df.columns.values[0]].replace(to_replace=0, value=mymin_exvivo)
#     df_stim_nafilled = df[df.columns.values[1]].replace(to_replace=0,value=mymin_invitro)
#
#     df = concat([df_exvivo_nafilled, df_stim_nafilled], axis=1)
#
#     # print(df.head())
#
#     counts_freq = Counter(zip(df[df.columns.values[0]], df[df.columns.values[1]]))
#     points = counts_freq.keys()
#
#     x, y = zip(*points)
#
#     x = array(x)
#     y = array(y)
#
#     mymax_invitro = max(y)
#     mymax_exvivo = max(x)
#
#     myargs = []
#
#     for subplot_index in range(len(subplots_list)):
#         mysubplot = subplots_list[subplot_index]
#
#         #top left
#         if subplot_index == 0:
#             xlim=[mymin_exvivo, mymin_x_line]
#             ylim=[mymin_y_line, mymax_invitro]
#             spines_to_set_to_invisible=["bottom", "right"]
#
#         # top right
#         if subplot_index == 1:
#             xlim=[mymin_x_line, mymax_exvivo]
#             ylim=[mymin_y_line, mymax_invitro]
#             spines_to_set_to_invisible=["bottom", "left"]
#
#         #bottom left
#         # if subplot_index == 2:
#         #     xlim = [mymin_exvivo, mymin_x_line]
#         #     ylim = [mymin_invitro, mymin_y_line]
#         #     spines_to_set_to_invisible = ["top", "bottom", "right"]
#         #
#         # # bottom right
#         # if subplot_index == 3:
#         #     xlim = [mymin_x_line, mymax_exvivo]
#         #     ylim = [mymin_invitro, mymin_y_line]
#         #     spines_to_set_to_invisible = ["top", "bottom", "left"]
#
#         #bottom left
#         if subplot_index == 2:
#             xlim = [mymin_exvivo, mymin_x_line]
#             ylim = [mymin_invitro, mymin_y_line]
#             spines_to_set_to_invisible = ["top", "right"]
#
#         # bottom right
#         if subplot_index == 3:
#             xlim = [mymin_x_line, mymax_exvivo]
#             ylim = [mymin_invitro, mymin_y_line]
#             spines_to_set_to_invisible = ["top", "left"]
#
#         if resize:
#             set_limits(mysubplot, xlim, ylim)
#
#         x_index_mod = where((x >= xlim[0]) & (x <= xlim[1]))[0]
#         y_index_mod = where((y >= ylim[0]) & (y <= ylim[1]))[0]
#
#         intersect_index_mod = intersect1d(x_index_mod, y_index_mod)
#
#         # print("intersect_index_mod : ", intersect_index_mod)
#
#         scat = mysubplot.scatter(Series(x).iloc[intersect_index_mod], Series(y).iloc[intersect_index_mod], facecolors=color,
#                           s=array(map(sqrt, Series(counts_freq.values()).iloc[intersect_index_mod])) + 15,
#                           marker='o', linewidths=0.5, edgecolor='w', label=label, clip_on=False)
#
#         mysubplot, myargs = set_logscale_manage_spine(mysubplot, spines_to_set_to_invisible, myargs)
#
#     return scat, subplots_list, (mymin_exvivo, max(x)), (mymin_invitro, max(y))




