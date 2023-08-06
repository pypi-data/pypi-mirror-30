__author__ = 'jlane'

from pandas import DataFrame, Series, concat, read_csv, merge
from numpy import where, arange, concatenate, intersect1d, setdiff1d
from time import asctime, localtime, time
from re import search
from glob import glob
import logging
import logging.config

from view import plot_frequencies_distribution, compress
from view import venn_diagram, gene_usage, write_expanded_summary
from view import produce_figures_and_tables, produce_heatmaps, produce_negctrl_vs_pepstim_pval_plot, determine_pep_specificity_thresholds_DbPos_for_multiple_subjects
from view import produce_validation_bar_plot_aa, determine_pep_specificity_thresholds_for_multiple_subjects, produce_medium_only_vs_pepstim_pval_plot
from view import provide_thresholds_DbPos, produce_specific_unspecific_perf_plot, provide_thresholds_negctrl, provide_thresholds_DbPos_removing_mixed_clns
from view import produce_specific_unspecific_removing_mixed_clns_perf_plot, get_expanded_clonotypes_with_a_threshold, plot_mixed_pure_frequencies

from model import sizeof_fmt, Graph
from collections import Counter

from sys import prefix, exec_prefix
from trace import Trace
from copy import copy

from gc import collect
from os import getpid, path, pardir, mkdir, getcwd,remove
from psutil import Process

from sys import argv
import argparse
import re

from model import AdaptiveBiotechFileColumn, MetadataFile, ComparisonDataFrameFactory, ComparisonDataSet, ClonotypeSamplesInfoFile

def program_setting():
    parser = argparse.ArgumentParser()

    parser.add_argument('-merge', action='store_true', dest='merge',
                        default=False,
                        help='Merge Adaptive Biotechnologies TCR sequencing txt file (default: False)')

    parser.add_argument('-expansion', action='store_true', dest='expansion',
                        default=False,
                        help='Calculate expansion p-values using a Fisher exact test (default: False)')

    parser.add_argument('-analyze', action='store_true', dest='analyze',
                        default=False,
                        help='Produce basic statistics summary tables and figures (default: False)')

    parser.add_argument('-reproducibility', action='store_true', dest='reproducibility',
                        default=False,
                        help='Creating heatmap of reproducibility (default: False)')

    parser.add_argument('-aacdr3', action='store_true', dest='aacdr3',
                        default=True,
                        help='Define the clonotype at the amino acid cdr3 level (default: False)')

    parser.add_argument('-genes_cdr3_aacln', action='store_true', dest='genes_aacdr3',
                        default=False,
                        help='Define the clonotype at the amino acid cdr3 and V, J gene level (default: False)')

    parser.add_argument('-optimize', action='store_true', dest='optimize',
                        default=False,
                        help='Creating negative control vs relevant peptide stimulated clonotype p-value plot (default: False)')

    parser.add_argument('-timepoints', action='store_true', dest='timepoints',
                        default=False,
                        help='Analyzes samples from different time points (default: False)')

    parser.add_argument('-geneusage', action='store_true', dest='geneusage',
                        default=False,
                        help='Provide gene usage statistics (default: False)')

    parser.add_argument('-detailed', action='store_true', dest='detailed',
                        default=False,
                        help='Provide more details')

    parser.add_argument('-compress', action='store_true', dest='compress',
                        default=False,
                        help='Compress work directory (default: False)')

    parser.add_argument('-input_folder', action='store', dest='input_folder',
                        default='',
                        help='Input folder (default: current directory)')

    parser.add_argument('-output_folder', action='store', dest='output_folder',
                        default='',
                        help='Output folder (default: current directory)')

    parser.add_argument('-workdir', action='store', dest='workdir',
                        default='',
                        help='Folder where input and output files should be (default: current directory)')

    parser.add_argument('-nolog', action='store_true', dest='nolog',
                        default=False,
                        help='Disable default log file (default: False)')

    parser.add_argument('-v', action='store_true', dest='VERBOSE',
                        default=False,
                        help='Turns on verbosity (more details)')

    parser.add_argument('--version', action='version', version='pepbox 0.3.3')

    parser.add_argument('-debug', action='store_true', dest='debug',
                        default=False,
                        help='Debug using small input size to test specific cases.')

    return parser

def check_supported_experiment(sample_infos_path):
    sample_infos = read_csv(sample_infos_path)
    sample_infos = sample_infos.dropna()

    l = list(set(sample_infos["experiment"]))
    kw_not_supported = []
    for e in l:
        if e not in ["AIM", "exvivo", "tetramer stain",	"IFNgCapture", "invitroculture+cytokinecapture", "medium culture", "peptide culture", 'exvivo, tetramer stain', 'peptide culture, tetramer stain']:
            kw_not_supported.append(e)
    return kw_not_supported

# def check_existing_file_name(sample_infos_path, sample_ids):
#     sample_infos = read_csv(sample_infos_path)
#     sample_infos = sample_infos.dropna()
#
#     l = list(set(sample_infos["file name"]))
#     return setdiff1d(sample_ids, l)

def produce_nt_aa_source_files(level_of_output_detail="detailed", clonotype_level="aacdr3", parameters_for_sample_selection=None, infos_to_extract=None, paths=None, subject_ids=None ):
    mylist = check_supported_experiment(paths['path_raw_data_folder'] + 'metadata/sample_info.csv')

    if len(mylist) > 0:
        raise ValueError("Sample experiments not recognized: " + str(mylist))

    if subject_ids is None:
        subject_ids = get_subject_ids_from_sample_info_file(paths['path_raw_data_folder'])
        # print("selected subjects:", subject_ids)

    for subject_id in subject_ids:
        # selection = copy(parameters_for_sample_selection)
        # selection['subject_ids'] = [subject_id]

        selection={'subject_ids': [subject_id]}

        # print("selection:", selection)

        sample_ids = get_sample_ids_from_sample_info_file(paths['path_raw_data_folder'], selection)

        # print('selected sample IDs: ', sample_ids)

        if len(sample_ids) > 0:
            factory = ComparisonDataFrameFactory(input_path=paths['path_raw_data_folder'], selected_list_of_files=sample_ids)
            comp_df = factory.merge()

            #print('comp_df: ', comp_df)

            if comp_df is not None:
                compdataset = ComparisonDataSet(comp_df, clonotype_samples_info_file=paths['path_raw_data_folder'] + 'metadata/sample_info.csv')

                samples = compdataset.samples

                # for subject_id in samples.get_subject_ids():

                print('subject id: ', subject_id)

                if parameters_for_sample_selection is not None:
                    parameters_for_sample_selection['subject_ids'] = [subject_id]
                    selected_samples = samples.select(parameters_for_sample_selection)
                else:
                    selected_samples = samples

                # mylist = check_existing_file_name(paths['path_raw_data_folder'] + 'metadata/sample_info.csv', samples.get_sample_ids())
                # if len(mylist) > 0:
                #     raise ValueError("Samples not recognized: " + str(mylist))

                print('--- Extracting and reorganising dataframe ---')

                write_merged_sample_files(selected_samples, infos_to_extract, paths['path_processed_data_folder'], subject_id,
                                        ['CDR3_nucleotide_clonotypes', 'CDR3_amino_acid_clonotypes', 'nucleotide_clonotype_annotations'], clonotype_level, level_of_output_detail)

                process = Process(getpid())
                print('Before mem flush: ', sizeof_fmt(process.memory_info().rss))
                collect()
                process = Process(getpid())
                print('After mem flush: ', sizeof_fmt(process.memory_info().rss))

def write_merged_sample_files(samples, infos, output_path, subject_id, suffixes, clonotype_level, level_of_result_detail):
    infos_df = samples.get_info_on_samples_df(columns_to_extract=infos)

    write_file3(samples, infos_df, output_path, subject_id, suffixes[1], clonotype_level)

    # if level_of_result_detail == "detailed":
        # write_file2(samples, infos_df, output_path, subject_id, suffixes[0])
        # write_file4(samples, output_path, subject_id, suffixes[2])

#complete identification of V and J gene. Those that are not completely identify do not contain any dash "-"
def select_indexes_of_clonotypes_completely_identified(cdr3):
    myindexes = []
    for mycdr3_index in cdr3.index.values:
        # print(cdr3.ix[mycdr3_index])
        if re.match(".*\\-.*", str(cdr3.ix[mycdr3_index])):
            myindexes.append(mycdr3_index)
        else:
            print("not selected:",cdr3.ix[mycdr3_index])


    return myindexes

def write_file3(samples, infos_df, output_path, subject_id, aa_file_sfx, clonotype_level="aacdr3", pvalues=None):
    excel_lower_number_precision_limit = 2.2251e-308
    aa_cell_count_df = samples.get_aa_clonotype_cell_count_df_by_samples()

    # aa_cell_count_df = samples.get_aa_clonotype_cell_count_df_with_aa_clonotype_ids_as_index_by_samples()

    # print(pvalues)

    if pvalues is not None:
        # cdr3 = samples.get_aminoAcid_sequences()

        cdr3 = samples.get_aa_clonotype_ids_df()
        aa_cell_count_df = aa_cell_count_df.ix[cdr3.index.values]

        # print("cdr3: ", cdr3.head())

        cdr3_associated_nt_clonotype_counts_df = samples.clonotype_sequence_infos.get_cdr3_associated_nt_clonotype_counts_df()

        # print("cdr3_associated_nt_clonotype_counts_df: ", cdr3_associated_nt_clonotype_counts_df.head())

        # print('cdr3_associated_nt_clonotype_counts_df 1: ', cdr3_associated_nt_clonotype_counts_df)

        cdr3_associated_nt_clonotype_counts_df = concat([cdr3, cdr3_associated_nt_clonotype_counts_df], axis=1)

        cdr3_associated_nt_clonotype_counts_df = cdr3_associated_nt_clonotype_counts_df.dropna()

        # print('cdr3_associated_nt_clonotype_counts_df 2: ', cdr3_associated_nt_clonotype_counts_df)

        # print(cdr3_associated_nt_clonotype_counts_df)
        # print(aa_cell_count_df)
        # print(pvalues)

        # cdr3_associated_nt_clonotype_counts_df.index = cdr3_associated_nt_clonotype_counts_df['aminoAcid']
        # cdr3_associated_nt_clonotype_counts_df.drop('aminoAcid', axis=1, inplace=True)

        # print("pvalues: ", pvalues)

        pvalues[pvalues < excel_lower_number_precision_limit]=0
        df2 = concat([cdr3_associated_nt_clonotype_counts_df, aa_cell_count_df, pvalues], axis=1)
        df2 = df2.fillna(1)
        df2.index = cdr3_associated_nt_clonotype_counts_df['aminoAcid']
        df2.drop('aminoAcid', axis=1, inplace=True)
    else:
        cdr3_associated_nt_clonotype_counts_df = samples.get_aa_associated_nt_clonotype_counts_df(clonotype_level)

        # cdr3 = samples.get_aa_clonotype_ids_df()

        # mycdr3_index = select_indexes_of_clonotypes_completely_identified(cdr3)
        # df2 = concat([cdr3_associated_nt_clonotype_counts_df.ix[mycdr3_index], aa_cell_count_df.ix[mycdr3_index]], axis=1)

        # print("write_file3: ", cdr3.iloc[mycdr3_index])

        # cdr3 = cdr3.iloc[mycdr3_index]
        # cdr3_associated_nt_clonotype_counts_df = concat([cdr3, cdr3_associated_nt_clonotype_counts_df], axis=1)
        # print(cdr3_associated_nt_clonotype_counts_df.head())

        df2 = concat([cdr3_associated_nt_clonotype_counts_df, aa_cell_count_df], axis=1)

    # print('df2 columns: ', df2.columns.values)
    # print('df2: ', df2.head())

    sequence_column_df = DataFrame(df2.columns.values, columns=['aminoAcid'], index=df2.columns.values).T

    df2 = sequence_column_df.append(df2)
    header_df = get_samples_info_header_df(infos_df, df2)
    print('header_df: ', header_df)

    # # print(df2.shape)
    # # print(header_df.shape)
    # # print(header_df)

    if header_df is not None:
        num_info_lines = header_df.shape[0]
        header_df.columns = df2.columns
        header_df.index.values[0:num_info_lines] = [''] * num_info_lines
        df2 = header_df.append(df2)

    df2 = concat([Series(df2.index.values, index=df2.index.values), df2], axis=1)

    print(df2.head())

    print('df2: ', df2.index.values)

    # print(subject_id)
    # print(output_path)
    # print(aa_file_sfx)

    myfileabspath = output_path + str(subject_id) + '_' + str(aa_file_sfx) + '.csv'

    df2.to_csv(myfileabspath, header=False, index=False)

def write_file2(samples, infos_df, output_path, subject_id, nt_file_sfx, pvalues=None):
    excel_lower_number_precision_limit = 2.2251e-308
    nt_sequences_df = samples.get_nucleotide_sequences_df()
    nt_cell_count_df = samples.get_nt_clonotype_cell_count_df()
    aa_cdr3_by_nt_clonotypes_df = samples.get_aminoAcid_sequences()

    if pvalues is not None:
        pvalues[pvalues < excel_lower_number_precision_limit]=0
        df1 = concat([nt_sequences_df, aa_cdr3_by_nt_clonotypes_df, nt_cell_count_df, pvalues], axis=1)
        df1 = df1.fillna(1)
    else:
        df1 = concat([nt_sequences_df, aa_cdr3_by_nt_clonotypes_df, nt_cell_count_df], axis=1)

    sequence_column_df = DataFrame(df1.columns.values, columns=['new_row'], index=df1.columns.values).T
    df1 = sequence_column_df.append(df1, ignore_index=True)
    header_df = get_samples_info_header_df(infos_df, df1)
    header_df.columns = df1.columns
    header_df.iloc[0:7, 0] = [''] * 7
    df1 = header_df.append(df1, ignore_index=True)
    df1.to_csv(output_path + str(int(float(subject_id))) + '_' + nt_file_sfx + '.csv', header=False, index=False)

    # writer = pd.ExcelWriter(output_path + str(int(float(subject_id))) + '_' + nt_file_sfx + '.xlsx', engine='xlsxwriter')
    # df1.to_excel(writer, header=False, index=False)
    # writer.save()

def write_file4(samples, output_path, subject_id, annot_file_sfx):
    sequence_annotation_df = samples.get_sequences_info_df(excluded_col_info=['count', 'estimatedNumberGenomes', 'frequency'])
    sequence_annotation_df.to_csv(output_path + str(int(float(subject_id))) + '_' + annot_file_sfx + '.csv', index=False)

def get_samples_info_header_df(info_to_merge_on_top, sample_df):
    filenames = info_to_merge_on_top['file name']
    sample_ids = [x.split(".tsv")[0] for x in filenames]

    list_rep_info = list(arange(0, len(sample_df.columns.values)))
    for index in arange(0, len(sample_df.columns.values)):
        list_rep_info[index] = info_to_merge_on_top.columns.values

    # print('sample_df.columns.values: ', sample_df.columns.values)

    for sample_id_index in arange(0, len(sample_ids)):
        # index_mod = .where(info_to_merge_on_top['file name'] == sample_id)[0]
        transpo = info_to_merge_on_top.iloc[sample_id_index].T

        sample_id = sample_ids[sample_id_index]

        # print('sample_id: ', sample_id)

        for index in arange(0, len(sample_df.columns.values)):
            if search('^' + sample_id.lower() + '_' + '|' +  '_' + sample_id.lower() + '$|^' + sample_id.lower() + '$', sample_df.columns.values[index].lower()):
                # print('list to concat: ', transpo.values.tolist())
                list_rep_info[index] = transpo.values.tolist()

    df = DataFrame(list_rep_info, columns=info_to_merge_on_top.columns.values)

    # print("after: ", df)

    index_mod = intersect1d(where(df['peptide sequence'] != 'no')[0],  where(df['peptide sequence'] != 'peptide sequence')[0])

    # print("before: ", df)
    # for i in range(len(list(df['peptide sequence'])):
    #     df['peptide sequence'].iloc[i]

    df['peptide sequence'].iloc[index_mod] = df['peptide sequence'].iloc[index_mod].str.upper()
    return df.T

def add_pvalues(samples, pvalues, infos_df, output_path, subject_id, sequence_level , suffix, clonotype_level="aacdr3"):
    if sequence_level == 'nucleotide':
        write_file2(samples, infos_df, output_path, subject_id, suffix + '_pval', clonotype_level, pvalues)
    else:
        # print(pvalues)
        write_file3(samples, infos_df, output_path, subject_id, suffix + '_pval', clonotype_level, pvalues )

def get_subject_ids_from_sample_info_file(path_raw_data_folder):
    info_file = ClonotypeSamplesInfoFile(path_raw_data_folder + 'metadata/sample_info.csv')
    # print("info_file.subject_id:", info_file.subject_id.tolist())
    return list(set(info_file.subject_id.tolist()))

def get_sample_ids_from_sample_info_file(path_raw_data_folder, parameters_for_sample_selection):
    info_file = ClonotypeSamplesInfoFile(path_raw_data_folder + 'metadata/sample_info.csv')

    # print('info_file: ', info_file.info_df)
    # print('info_file: ', info_file.sequencing_ID)
    # print('parameters_for_sample_selection: ', parameters_for_sample_selection)

    return info_file.select(parameters_for_sample_selection)

def add_pvalues_to_file_with_cell_counts(paths, filename, sequence_level, fisher_test, infos_to_extract, clonotype_level="aacdr3"):
    if path.isfile(filename):
        df = read_csv(filename, header=None)

        compdataset = ComparisonDataSet(df, clonotype_samples_info_file=paths['path_raw_data_folder'] + 'metadata/sample_info.csv')
        samples = compdataset.samples

        # print('my samples: ', samples)

        infos_df = samples.get_info_on_samples_df(infos_to_extract)

        grouped_samples_by_subject_id = samples.get_samples_by_subject_ids_list()

        print("grouped_samples_by_subject_id: ", grouped_samples_by_subject_id)

        for mygroup_samples in grouped_samples_by_subject_id:
            print(mygroup_samples.get_sample_ids())
            # cell_types = mygroup_samples.get_cell_types()

            # for cell_type in cell_types:
            #     # print(cell_type)

                # samples = mygroup_samples.get_samples_by_cell_types([cell_type])
                # samples.assign_pvalue_expansion_measurments(sequence_level=sequence_level, fisher_test=fisher_test)

            mygroup_samples.assign_pvalue_expansion_measurments(sequence_level=sequence_level, fisher_test=fisher_test)

            for subject_id in samples.get_subject_ids():
                if sequence_level == 'nucleotide':
                    add_pvalues(mygroup_samples, mygroup_samples.get_pvalues_df(), infos_df, paths['path_processed_data_folder'], subject_id, sequence_level, 'nucleotide_clonotypes', clonotype_level)
                else:
                    add_pvalues(mygroup_samples, mygroup_samples.get_pvalues_df(), infos_df, paths['path_processed_data_folder'], subject_id, sequence_level, 'CDR3_amino_acid_clonotypes', clonotype_level)
    else:
        print('WARN: ' + filename + ' does not exists.')

def add_gene_info_to_main_files(path_processed_data_folder, main_filename, annotations_filename):
    if path.isfile(main_filename):

        df_main = read_csv(main_filename, header=None)
        df_main_temp = df_main.ix[8:,]
        df_main_temp.columns = df_main.ix[7,]

        print("cols: ", df_main.ix[7,])

        df_annotations = read_csv(annotations_filename)

        # print(df_annotations.columns.values)

        df_gp = df_annotations.groupby(['aminoAcid'])
        mylist = [(key, df.index.values) for key, df in df_gp]
        mydict = dict(mylist)

        # print("mydict: ", mydict)

        start = 1
        for cdr3_aa in df_main_temp["aminoAcid"]:

            # print("cdr3_aa: ", [cdr3_aa, mydict[cdr3_aa]])

            df_temp = df_annotations.ix[mydict[cdr3_aa],["vGeneName", "dGeneName", "jGeneName"]]

            # print([df_temp["vGeneName"].unique(),df_temp["dGeneName"].unique(), df_temp["jGeneName"].unique()])

            df_temp = DataFrame([cdr3_aa, df_temp["vGeneName"].unique(), df_temp["dGeneName"].unique(), df_temp["jGeneName"].unique()], index=["aminoAcid", "vGeneName", "dGeneName", "jGeneName"]).T

            if start == 0:
                df_final = df_final.append(df_temp)
            else:
                start = 0
                df_final = df_temp

        splitted_path = main_filename.split("/")
        subject_id = splitted_path[(len(splitted_path)-1)].split("_")[0]

        # df_final["aminoAcid"] = df_main_temp["aminoAcid"]
        df_final.to_csv(path_processed_data_folder + subject_id + '_CDR3_amino_acid_gene_info.csv', index=False)

        df_complete = merge(df_final, df_main_temp, on="aminoAcid", how="outer")
        df_complete.to_csv(path_processed_data_folder + subject_id + '_CDR3_amino_acid_complete_info.csv', index=False)

    else:
        print('WARN: ' + main_filename + ' does not exists.')

def add_pvalues_to_files_with_cell_counts(paths, filename_aa, infos_to_extract, clonotype_level="aacdr3"):
    fisher_test = 'slow'

    # try:
    #     import fisher
    #     found = True
    # except ImportError:
    #     found = False
    #
    # if not found:
    #     fisher_test = 'slow'
    #     print('Module fisher NOT found: using slow Fisher exact test')
    # else:
    #     print('Module fisher found: using fast Fisher exact test')
    #     fisher_test = 'fast'

    # add_pvalues_to_file_with_cell_counts(path_processed_data_folder, filename_nt,  'nucleotide', fisher_test, infos_to_extract)
    add_pvalues_to_file_with_cell_counts(paths, filename_aa,  'amino acid', fisher_test, infos_to_extract, clonotype_level=clonotype_level)

def presence_abscence_pattern_to_csv(path_tables_and_figures_folder, samples, subject_id, tag):
    allg = Graph(samples)
    mydf_allg = presence_abscence_pattern(samples, allg.vertices.dictionary)
    mydf_allg.to_csv(path_tables_and_figures_folder + str(subject_id) + "_" + tag + "_presence_abscence.csv")

    mypatterns = []
    for index in mydf_allg.index.values:
        mypatterns.append(str(list(mydf_allg.ix[index])))

    myc = Counter(mypatterns)
    mydf_allg_freq_tab = DataFrame(dict(myc), index=['frequency']).T

    return mydf_allg_freq_tab, mydf_allg

def timepoint_analysis(path_tables_and_figures_folder, filename):
    if path.isfile(filename):
        df = read_csv(filename, header=None)

        compdataset = ComparisonDataSet(df)
        samples = compdataset.samples

        subject_id = samples.get_subject_ids()[0]

        mysubsetsps = samples.get_samples_by_experiment_types(experiment_types=["peptide culture"])
        mydf_allg, my_detailed_df = presence_abscence_pattern_to_csv(path_tables_and_figures_folder, mysubsetsps, subject_id)

        # il5_sp = samples.get_samples_by_cell_types(['il5_tcell'])
        # mydf_IL5, detailed_df_IL5 = presence_abscence_pattern_to_csv(path_tables_and_figures_folder, il5_sp, subject_id, "IL5")

        # il10_sp = samples.get_samples_by_cell_types(['il10_tcell'])
        # mydf_IL10, detailed_df_IL10 = presence_abscence_pattern_to_csv(path_tables_and_figures_folder, il10_sp, subject_id, "IL10")
        #
        # my_detailed_df = concat([detailed_df_IL5, detailed_df_IL10, detailed_df_all], axis=1)
        # my_detailed_df.columns = concatenate([["IL5"]*7, ["IL10"]*7, ["IL5+IL10"]*7])
        # my_detailed_df.columns = ["IL5", "IL10", "IL5+IL10"]

        # for index in my_detailed_df.index.values:
        #     for tp in
        #         raw = my_detailed_df.ix[index,]
        #         for index2 in raw.index.values:

        # my_detailed_df.to_csv(path_tables_and_figures_folder + str(subject_id) + "_frequency_presence_abscence_pattern.csv")

        mydf = concat([mydf_allg], axis=1)
        # mydf.columns = ["IL5", "IL10", "IL5+IL10"]

        myindex_list=[]
        for index in mydf.index.values:
            # print(index)
            # print(type(index))
            index = index.replace(",","")
            index = index.replace("]","")
            index = index.replace("[", "")
            index = index.replace("0", "")
            index = index.replace(" ", "")
            index = index.replace("'", "")
            index = "'" + index
            # tp=1
            # mstr_index=""
            # for value in index:
            #
            #     if value == "1":
            #         mstr_index += str(tp)
            #     tp+=1

            myindex_list.append(index)

        mydf.index=myindex_list

        mydf = mydf.fillna(0)
        mydf.to_csv(path_tables_and_figures_folder + str(subject_id) + "_frequency_presence_abscence_pattern.csv")

        # all_clonotypes_ids = mysubsetsps.get_aa_clonotype_ids_list()
        #
        # mydf = venn_overlap_summary(mysubsetsps, ref_sp, g5.vertices.dictionary, g10.vertices.dictionary)
        # mydf.to_csv(
        #     path_tables_and_figures_folder + str(subject_id) + "_tovenn.csv")

        # il5_sp = samples.get_samples_by_cell_types(['il5_tcell'])
        # g1 = Graph(il5_sp)
        # print("Adjacency matrix (IL5): ")
        # print(g1.adjacency_matrix)
        #
        # il10_sp = samples.get_samples_by_cell_types(['il10_tcell'])
        # g1 = Graph(il10_sp)
        # print("Adjacency matrix (IL10): ")
        # print(g1.adjacency_matrix)
        #
        # il10_il5_sp = samples.get_samples_by_cell_types(['il10_tcell', 'il5_tcell'], selection="or")
        # g1 = Graph(il10_il5_sp)
        # print("Adjacency matrix (il10_il5_sp): ")
        # print(g1.adjacency_matrix)

        # mysubsetsps = samples.get_samples_by_cell_types(['il5_tcell'])
        # ref_sp = samples.get_samples_by_cell_types(["cd4_t_cell"])
        # il5_exvivo_sp = samples.get_samples_by_cell_types(['il5_tcell'])
        # # interesting_clns = mysubsetsps.get_aa_clonotype_ids_list()
        # g1 = Graph(il5_exvivo_sp, reference_sp=ref_sp)
        # print("Adjacency matrix (il5_cd4_sp): ")
        # print(g1.adjacency_matrix)
        #
        # # mysubsetsps = samples.get_samples_by_cell_types(['il10_tcell'])
        # ref_sp = samples.get_samples_by_cell_types(["cd4_t_cell"])
        # il10_exvivo_sp = samples.get_samples_by_cell_types(['il10_tcell'])
        # # interesting_clns = mysubsetsps.get_aa_clonotype_ids_list()
        # g1 = Graph(il10_exvivo_sp, reference_sp=ref_sp)
        # print("Adjacency matrix (il10_cd4_sp): ")
        # print(g1.adjacency_matrix)

        # mysubsetsps = samples.get_samples_by_cell_types(['il10_tcell'])
        # ref_sp = samples.get_samples_by_cell_types(["cd4_t_cell"])
        # il10_exvivo_sp = samples.get_samples_by_cell_types(['il10_tcell'])
        # interesting_clns = mysubsetsps.get_aa_clonotype_ids_list()
        # g1 = Graph(il10_exvivo_sp, selected_clns_ids=interesting_clns, reference_sp=ref_sp)
        # print("Adjacency matrix (il10_cd4_sp): ")
        # print(g1.adjacency_matrix)

        # il5_sp = len(samples.get_samples_by_cell_types(['il5_tcell']).get_aa_clonotype_ids_list())
        # il10_sp = len(samples.get_samples_by_cell_types(['il10_tcell']).get_aa_clonotype_ids_list())
        # cd4_sp = samples.get_samples_by_cell_types(["cd4_t_cell"]).get_aa_clonotype_ids_list()
        # mysubsetsps = samples.get_samples_by_experiment_types(experiment_types=["invitroculture+cytokinecapture"])
        # interesting_clns = len(mysubsetsps.get_aa_clonotype_ids_list())
        # mycd4_selected=intersect1d(mysubsetsps.get_aa_clonotype_ids_list(), cd4_sp)
        # print("il5_sp, il10_sp, selected cd4_sp: ", [il5_sp, il10_sp, len(mycd4_selected)])

def venn_overlap_summary(mysubsetsps, cd4, il5tps, il10tps):
    # mycd4_clns_ids = cd4[0].get_aa_clonotype_ids_df()
    all_clns_ids = mysubsetsps.get_aa_clonotype_ids_df()
    il5tp1 = il5tps["1"].get_aa_clonotype_ids_df()
    il5tp7 =il5tps["7"].get_aa_clonotype_ids_df()

    il10tp1 = il10tps["1"].get_aa_clonotype_ids_df()
    il10tp7 = il10tps["7"].get_aa_clonotype_ids_df()

    mydf=concat([all_clns_ids, il5tp1,il5tp7,il10tp1,il10tp7],axis=1).T
    mydf.index=["all", "IL5 tp1", "IL5 tp7", "IL10 tp1", "IL10 tp7"]
    return mydf

def presence_abscence_pattern(samples, timepoints):
    all_clns_ids = samples.get_aa_clonotype_ids_list()
    mydict={}
    for clonotype_id in samples.get_aa_clonotype_ids_list():
        mydict[clonotype_id] = []

    list_tp = sorted(timepoints.keys())
    mymat = [[0]*7]*len(all_clns_ids)

    mydf=DataFrame(mymat, columns=list_tp, index=all_clns_ids)

    for tp_index in arange(0, len(list_tp)):
        tp = list_tp[tp_index]
        samples_tp = timepoints[tp]
        clonotype_ids_tp = samples_tp.get_aa_clonotype_ids_list()
        mydf[tp].ix[clonotype_ids_tp] = tp
    return mydf


def subject_clonal_distribution(paths, filename_aa):
    # path_processed_data_folder =  paths['path_processed_data_folder']
    path_tables_and_figures_folder = paths["path_tables_and_figures_folder"]

    df = read_csv(filename_aa, header=None)
    compdataset = ComparisonDataSet(df, clonotype_samples_info_file=paths['path_raw_data_folder'] + 'metadata/sample_info.csv')

    samples = compdataset.samples

    # mysptp1 = samples.get_samples_by_time_points(["1"])
    # il5_sp_cd4 = mysptp1.get_samples_by_cell_types(["il5_t_cell", "cd4_t_cell"])
    #
    # il10_sp_cd4 = mysptp1.get_samples_by_cell_types(["il10_t_cell", "cd4_t_cell"])
    #
    # il5_sp_cd4_frequencies_df = il5_sp_cd4.get_frequencies()
    # intersection_il5_sp_cd4 = il5_sp_cd4_frequencies_df[il5_sp_cd4_frequencies_df != 0]
    #
    # intersection_il5_sp_cd4

    for sample in samples:
        plot_frequencies_distribution(path_tables_and_figures_folder, sample)

    # for repeats in samples.get_repeatsList():
    #     plot_frequencies_distribution(path_tables_and_figures_folder, repeats)

def merge(logger, paths, level_of_output_detail, clonotype_level):
    logger.info('++++++++++++++++++++++++++++')
    logger.info(' Producing cell count files ')
    logger.info('++++++++++++++++++++++++++++')

    parameters_for_sample_selection = None

    infos_to_extract = ['file name', 'subject id', 'experiment', 'peptide', 'peptide sequence', 'sequencing level',
                        'repeat', 'time point', 'cell type']

    for k in paths.keys():
        mypath = paths[k]
        if not path.isdir(mypath):
            logger.debug("Folder " + mypath + " does not exist !!")
            logger.debug("Creating it !!")
            mkdir(mypath)
            if 'path_raw_data_folder' == k:
                mkdir(mypath + "/metadata")

    # if options.keys() in ['additional_parameters']:
    #     parameters_for_sample_selection = options['additional_parameters']

        # parameters_for_sample_selection = { 'traits':['ex vivo', 'PK', 'PT', 'TG', 'TN'], 'data_sequenced':['dna'],
        #                                'experiment_type_excluded':['aim', 'ifngcapture']}

        # parameters_for_sample_selection = {'traits': ['ex vivo', 'pk', 'pt', 'tg', 'tn'], 'data_sequenced':['dna']}

        # parameters_for_sample_selection = {'traits': ['tuberculosis']}

        # infos_to_extract = ['file name', 'subject id', 'experiment', 'peptide sequence',
        #                             'total cell count before culture', 'sequencing level', 'repeat']

        # produce_nt_aa_source_files(level_of_output_detail=level_of_output_detail, clonotype_level=clonotype_level,
        #                            parameters_for_sample_selection=parameters_for_sample_selection,
        #                            infos_to_extract=infos_to_extract, paths=paths)

    produce_nt_aa_source_files(level_of_output_detail=level_of_output_detail, clonotype_level=clonotype_level,
                               parameters_for_sample_selection=parameters_for_sample_selection,
                               infos_to_extract=infos_to_extract, paths=paths)

def expansion(logger, paths, clonotype_level):
    logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++')
    logger.info('Adding pvalues to previously created cell count files')
    logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++')

    # processed_file_nt_names = glob(path_processed_data_folder + '*nucleotide_clonotypes.csv')
    processed_file_aa_names = glob(paths['path_processed_data_folder']  + '*CDR3_amino_acid_clonotypes.csv')

    # infos_to_extract = ['file name', 'subject id', 'experiment', 'peptide sequence', 'total cell count before culture', 'sequencing level', 'repeat']

    infos_to_extract = ['file name', 'subject id', 'experiment', 'peptide', 'peptide sequence', 'sequencing level',
                        'repeat']

    if len(processed_file_aa_names) > 0:
        for filename_aa in processed_file_aa_names:
            add_pvalues_to_files_with_cell_counts(paths, filename_aa, infos_to_extract, clonotype_level)

            remove(filename_aa)

            process = Process(getpid())
            logger.info('Before mem flush: ', sizeof_fmt(process.memory_info().rss))
            collect()
            process = Process(getpid())
            logger.info('After mem flush: ', sizeof_fmt(process.memory_info().rss))
    elif len(glob(paths['path_processed_data_folder']  + '*CDR3_amino_acid_clonotypes_pval.csv')) > 0:
        raise Exception("Summary file already contains p-values.")
    else:
        raise Exception(
            "Requested file(s) are not in \"" + paths['path_processed_data_folder']  + "\" or do not have the right identifiers.")

def analyze(logger, paths, level_of_output_detail):
    logger.info('++++++++++++++++++++++++++++++')
    logger.info(' Producing figures and tables ')
    logger.info('++++++++++++++++++++++++++++++')

    # processed_file_nt_pval_names = glob(path_processed_data_folder + '*nucleotide_clonotypes_pval.csv')
    processed_file_aa_pval_names = glob(paths['path_processed_data_folder'] + '*CDR3_amino_acid_clonotypes_pval.csv')

    paths["path_tables_and_figures_folder"] = paths['path_processed_data_folder'] + "/Basic stats/"

    # path_tables_and_figures_folder_basic = path_tables_and_figures_folder + "/Basic stats/"

    concat_df = ""
    if not path.isdir(paths['path_processed_data_folder']):
        logger.info("output_folder:", paths['path_processed_data_folder'])
        logger.info("Does not exist !!")
        logger.info("Creating one !!")
        mkdir(paths['path_processed_data_folder'])

        # for filename_nt, filename_aa in zip(processed_file_nt_pval_names, processed_file_aa_pval_names):

    correlation_list_df = []
    for filename_aa in processed_file_aa_pval_names:
        logger.info("amino acid sequence processing...")

        # subject_clonal_distribution(paths, filename_aa)

        df = produce_figures_and_tables(paths, filename_aa=filename_aa, pvalue_threshold=0.001, bonferroni=True,
                                        level_of_output_detail=level_of_output_detail)

        # venn_diagram(path_tables_and_figures_folder, filename_aa, 'amino acid', bonferroni=True, level_of_output_detail=level_of_output_detail)

        write_expanded_summary(paths, filename_aa, 'amino acid', bonferroni=True,
                               level_of_output_detail=level_of_output_detail)

        process = Process(getpid())
        logger.debug('Before mem flush: ', sizeof_fmt(process.memory_info().rss))

        collect()

        process = Process(getpid())
        logger.debug('After mem flush: ', sizeof_fmt(process.memory_info().rss))

        if df is not None:
            correlation_list_df.append(df)

    if len(correlation_list_df) > 0:
        concat_df = concat(correlation_list_df, axis=1)
        concat_df.to_csv(paths['path_tables_and_figures_folder'] + "/Basic stats/summary_expansion_correlations.csv", index=False)

def reproducibility(logger, paths):
    logger.info('+++++++++++++++++++++++++++++++++++')
    logger.info('Creating heatmap of reproducibility')
    logger.info('+++++++++++++++++++++++++++++++++++')

    # processed_file_nt_pval_names = glob(path_processed_data_folder + '*nucleotide_clonotypes_pval.csv')
    processed_file_aa_pval_names = glob(paths['path_processed_data_folder'] + '*CDR3_amino_acid_clonotypes_pval.csv')

    path_tables_and_figures_folder_reprod = paths['path_tables_and_figures_folder'] + "/Reproducibility assessment/"

    if not path.isdir(path_tables_and_figures_folder_reprod):
        logger.debug("output_folder:", path_tables_and_figures_folder_reprod)
        logger.debug("Does not exist !!")
        logger.debug("Creating one !!")
        mkdir(path_tables_and_figures_folder_reprod)

    # print("processed_file_aa_pval_names: ", processed_file_aa_pval_names)

    reprod_stats_summary = []

    for filename_aa in processed_file_aa_pval_names:
        # print('filename_aa: ', filename_aa)

        stats_summary = produce_heatmaps(path_tables_and_figures_folder_reprod, filename_aa, pvalue_threshold=0.001)
        reprod_stats_summary.append(stats_summary)

        process = Process(getpid())
        logger.debug('Before mem flush: ', sizeof_fmt(process.memory_info().rss))

        collect()

        process = Process(getpid())
        logger.debug('After mem flush: ', sizeof_fmt(process.memory_info().rss))

    reprod_stats_summary_df = DataFrame(concatenate(reprod_stats_summary),
                                        columns=['subject_id', 'comparison', 'max reproducibility (%)',
                                                 'expansion p-values',
                                                 '# ex vivo cells', 'min reproducibility (%)', 'expansion p-values',
                                                 '# ex vivo cells'])

    reprod_stats_summary_df.to_csv(path_tables_and_figures_folder_reprod + "reprod_stats_summary_df.csv", index=False)

def optimize(logger,paths ):
    logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    logger.info('Creating negative control vs relevant peptide stimulated clonotype p-value plot')
    logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

    path_tables_and_figures_folder_opt = paths['path_tables_and_figures_folder'] + "/Optimized pvalue assessment/"

    if not path.isdir(path_tables_and_figures_folder_opt):
        logger.debug("output_folder:", path_tables_and_figures_folder_opt)
        logger.debug("Does not exist !!")
        logger.debug("Creating one !!")
        mkdir(path_tables_and_figures_folder_opt)

    # processed_file_nt_pval_names = glob(path_processed_data_folder + '*nucleotide_clonotypes_pval.csv')

    processed_file_aa_pval_names = glob(paths['path_processed_data_folder'] + '*CDR3_amino_acid_clonotypes_pval.csv')

    # tetramer_sp_subsets=[['exvivo, tetramer stain'], ['peptide culture, tetramer stain'], ['exvivo, tetramer stain', 'peptide culture, tetramer stain']]
    # tetramer_sp_subsets=[['exvivo, tetramer stain', 'peptide culture, tetramer stain']]

    tetramer_sp_subsets = [['peptide culture, tetramer stain']]

    for tetramer_sp in tetramer_sp_subsets:
        irrelevant, relevant = determine_pep_specificity_thresholds_for_multiple_subjects(paths,
                                                                                          path_tables_and_figures_folder_opt,
                                                                                          processed_file_aa_pval_names,
                                                                                          tetramer_sp=tetramer_sp,
                                                                                          bonferroni=True)

        logger.info("Thresholds used [irrelevant, relevant]: ", [irrelevant, relevant])

        for filename_aa in processed_file_aa_pval_names:
            produce_negctrl_vs_pepstim_pval_plot(paths, path_tables_and_figures_folder_opt, filename_aa,
                                                 culture_thresholds=[relevant, irrelevant],
                                                 tetramer_sp=tetramer_sp, pvalue_threshold=0.001, bonferroni=True)

            process = Process(getpid())
            logger.debug('Before mem flush: ', sizeof_fmt(process.memory_info().rss))
            collect()
            process = Process(getpid())
            logger.debug('After mem flush: ', sizeof_fmt(process.memory_info().rss))

    logger.info('+++++++++++++++++++++++++++++')
    logger.info('Creating validation bar plot ')
    logger.info('+++++++++++++++++++++++++++++')

    # processed_file_nt_pval_names = glob(path_processed_data_folder + '*nucleotide_clonotypes_pval.csv')
    processed_file_aa_pval_names = glob(paths['path_processed_data_folder'] + '*CDR3_amino_acid_clonotypes_pval.csv')
    # tetramer_sp_subsets=[['exvivo, tetramer stain'], ['peptide culture, tetramer stain'], ['exvivo, tetramer stain', 'peptide culture, tetramer stain']]
    tetramer_sp_subsets = [['peptide culture, tetramer stain']]

    path_tables_and_figures_folder_exvivo = paths['path_tables_and_figures_folder'] + "/Ex vivo frequency/"

    if not path.isdir(path_tables_and_figures_folder_exvivo):
        logger.debug("output_folder:", path_tables_and_figures_folder_exvivo)
        logger.debug("Does not exist !!")
        logger.debug("Creating one !!")
        mkdir(path_tables_and_figures_folder_exvivo)

    for tetramer_sp in tetramer_sp_subsets:

        logger.info("tetramer_sp : ", tetramer_sp)

        irrelevant, relevant = determine_pep_specificity_thresholds_for_multiple_subjects(paths,
                                                                                          path_tables_and_figures_folder_exvivo,
                                                                                          processed_file_aa_pval_names,
                                                                                          tetramer_sp=tetramer_sp,
                                                                                          bonferroni=True)

        logger.info("Thresholds used [irrelevant, relevant]: ", [irrelevant, relevant])

        for filename_aa in processed_file_aa_pval_names:
            produce_validation_bar_plot_aa(paths, path_tables_and_figures_folder_exvivo, filename_aa,
                                           tetramer_sp=tetramer_sp, culture_thresholds=[relevant, irrelevant])

            process = Process(getpid())
            logger.debug('Before mem flush: ', sizeof_fmt(process.memory_info().rss))
            collect()
            process = Process(getpid())
            logger.debug('After mem flush: ', sizeof_fmt(process.memory_info().rss))

def geneusage(logger, paths):
    logger.info('++++++++++++++++++++++++++++++')
    logger.info(' Gene usage statistics ')
    logger.info('++++++++++++++++++++++++++++++')

    # processed_file_nt_pval_names = glob(path_processed_data_folder + '*nucleotide_clonotypes_pval.csv')
    processed_file_aa_pval_names = glob(paths['path_processed_data_folder'] + '*CDR3_amino_acid_clonotypes*.csv')

    # path_tables_and_figures_folder = path_tables_and_figures_folder + "/Basic stats/"

    if not path.isdir(paths['path_tables_and_figures_folder']):
        logger.info("output_folder:", paths['path_tables_and_figures_folder'])
        logger.info("Does not exist !!")
        logger.info("Creating one !!")
        mkdir(paths['path_tables_and_figures_folder'])

        # for filename_nt, filename_aa in zip(processed_file_nt_pval_names, processed_file_aa_pval_names):

    for filename_aa in processed_file_aa_pval_names:
        gene_usage(paths['path_tables_and_figures_folder'], filename_aa)

def timepoints(logger, paths):
    logger.info('++++++++++++++++++++++++++++++')
    logger.info(' Time point analysis ')
    logger.info('++++++++++++++++++++++++++++++')

    processed_file_aa_pval_names = glob(paths['path_processed_data_folder'] + '*CDR3_amino_acid_clonotypes*.csv')

    path_tables_and_figures_folder_basic = paths['path_tables_and_figures_folder'] + "/Basic stats/"

    if not path.isdir(paths['path_tables_and_figures_folder']):
        logger.info("output_folder:", paths['path_tables_and_figures_folder'])
        logger.info("Does not exist !!")
        logger.info("Creating one !!")
        mkdir(paths['path_tables_and_figures_folder'])

    for filename_aa in processed_file_aa_pval_names:
        timepoint_analysis(path_tables_and_figures_folder_basic, filename_aa)

def pepbox():
    try:
        parser = program_setting()
        args = parser.parse_args()

        options={}
        options['main_processing'] = ["0"]

        path_raw_data_folder=""
        path_processed_data_folder=""
        path_tables_and_figures_folder=""

        if args.detailed:
            level_of_output_detail = "detailed"
        else:
            level_of_output_detail = "basic"

        clonotype_level = "aacdr3"
        if not args.aacdr3:
            clonotype_level="genes+aacdr3"

        print(args)
        logger = logging.getLogger('pepbox')

        test_folder=""
        if args.debug:
            test_folder='/test/'

        if args.workdir is None:

            if not args.nolog and (args.input_folder is not None):
                hdlr = logging.FileHandler(args.input_folder+ '/pepbox.log', mode='w')
                # logging.basicConfig(filename=args.input_folder + '/pepbox.log', level=logging.INFO)
            else:
                hdlr = logging.FileHandler(getcwd()  + '/pepbox.log', mode='w')
                # logging.basicConfig(filename=getcwd() + '/pepbox.log', level=logging.INFO)

            if args.merge or (args.expansion) or (args.reproducibility) or (args.analyze) or (args.optimize):
                if args.merge:
                    if (args.input_folder is not None):
                        path_raw_data_folder =  args.input_folder + test_folder
                    else:
                        path_raw_data_folder = getcwd() + '/Raw data/' + test_folder

                    if args.output_folder is not None:
                        path_processed_data_folder = args.output_folder + test_folder
                    else:
                        path_processed_data_folder = getcwd() + '/Processed data/' + test_folder

                else:
                    if (args.expansion) or (args.reproducibility) or (args.analyse) or (args.optimize):
                        if (args.input_folder is not None):
                            path_processed_data_folder = args.input_folder + test_folder
                        else:
                            path_processed_data_folder = getcwd() + '/Processed data/' + test_folder
                        if (args.output_folder is not None):
                            path_tables_and_figures_folder = args.output_folder  + '/Tables and Figures/' + test_folder
                        else:
                            path_tables_and_figures_folder = getcwd() + '/Tables and Figures/' + test_folder
            else:
                args.merge = True
                args.expansion = True
                args.reproducibility = True
                args.analyze = True
                args.optimize = True

                if (args.input_folder is not None):
                    path_raw_data_folder = args.input_folder + test_folder
                else:
                    path_raw_data_folder = getcwd() + '/Raw data/' + test_folder

                if (args.output_folder is not None):
                    path_processed_data_folder = args.output_folder + '/Processed data/' + test_folder
                    path_tables_and_figures_folder = args.output_folder + '/Tables and Figures/' + test_folder
        else:
            if not args.nolog:
                # print(args.workdir + '/pepbox.log')
                hdlr = logging.FileHandler(args.workdir + '/pepbox.log', mode='w')
                # logger = logging.basicConfig(filename=args.workdir + '/pepbox.log', filemode='w', level=logging.INFO)

            path_raw_data_folder = args.workdir + '/Raw data/' + test_folder
            path_processed_data_folder = args.workdir + '/Processed data/' + test_folder
            path_tables_and_figures_folder = args.workdir + '/Tables and Figures/' + test_folder

        # logger = logging.getLogger("pepbox")
        # logger.setLevel(logging.DEBUG)
        # create console handler and set level to debug

        # create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        # add formatter to ch
        hdlr.setFormatter(formatter)
        # add ch to logger
        logger.addHandler(hdlr)
        logger.setLevel(logging.INFO)

        paths = {'path_raw_data_folder': path_raw_data_folder,
                 'path_processed_data_folder': path_processed_data_folder,
                 'path_tables_and_figures_folder': path_tables_and_figures_folder}

        logger.info("options: ")
        logger.info(args)

        logger.info("--- Program starts at: %s ---" % asctime(localtime(time())))
        logger.info("Pepbox")
        logger.info("Paths: ", paths)

        if args.merge:
            merge(logger, paths, level_of_output_detail, clonotype_level)

        if args.expansion:
            expansion(logger, paths, clonotype_level)

        if args.analyze:
            analyze(logger, paths, level_of_output_detail)

        if args.reproducibility:
            reproducibility(logger, paths)

        if args.optimize:
            optimize(logger, paths)

        if args.geneusage:
            geneusage(logger, paths)

        if args.timepoints:
            timepoints(logger, paths)

        if args.compress:
            if args.workdir is not None:
                output = args.workdir
            elif args.output_folder is not None:
                output = args.output_folder
            else:
                output = getcwd()
            compress(output, 'pepbox_results.zip', logger)

        if "8" in options['main_processing']:
            logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            logger.info('Creating medium only vs peptide stimulated sample p-values comparison plots')
            logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

            processed_file_aa_pval_names = glob(path_processed_data_folder + '*CDR3_amino_acid_clonotypes_pval.csv')

            for filename_aa in processed_file_aa_pval_names:
                produce_medium_only_vs_pepstim_pval_plot(path_tables_and_figures_folder, filename_aa, pvalue_threshold=0.001, bonferroni=True)
                process = Process(getpid())
                logger.debug('Before mem flush: ', sizeof_fmt(process.memory_info().rss))
                collect()
                process = Process(getpid())
                logger.debug('After mem flush: ', sizeof_fmt(process.memory_info().rss))

        if "9" in options['main_processing']:
            logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            logger.info('Adding gene usage to previously created cell count and p-value files')
            logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

            processed_file_aa_pval_names = glob(path_processed_data_folder + '*CDR3_amino_acid_clonotypes_pval.csv')
            processed_file_annotations = glob(path_processed_data_folder + "*nucleotide_clonotype_annotations.csv")

            for main_filename, annotations_filename in zip(processed_file_aa_pval_names, processed_file_annotations):
                if level_of_output_detail == "detailed":
                    add_gene_info_to_main_files(path_processed_data_folder, main_filename, annotations_filename)

                process = Process(getpid())
                logger.debug('Before mem flush: ', sizeof_fmt(process.memory_info().rss))
                collect()
                process = Process(getpid())
                logger.debug('After mem flush: ', sizeof_fmt(process.memory_info().rss))

        if "10" in options['main_processing']:
            logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            logger.info('Thresholds without tetramer to validate')
            logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

            processed_file_aa_pval_names = glob(path_processed_data_folder + '*CDR3_amino_acid_clonotypes_pval.csv')

            irrelevant, relevant = determine_pep_specificity_thresholds_DbPos_for_multiple_subjects(path_tables_and_figures_folder,
                                                                                              processed_file_aa_pval_names,
                                                                                              ["pk-megapool-11"],
                                                                                              bonferroni=True)

            for filename_aa in processed_file_aa_pval_names:
                produce_negctrl_vs_pepstim_pval_plot(path_tables_and_figures_folder, filename_aa,
                                                     culture_thresholds=[relevant, irrelevant],
                                                     tetramer_sp=["pk-megapool-11"],
                                                     pvalue_threshold=0.001, bonferroni=True,double_positive=True)
                process = Process(getpid())
                logger.debug('Before mem flush: ', sizeof_fmt(process.memory_info().rss))
                collect()
                process = Process(getpid())
                logger.debug('After mem flush: ', sizeof_fmt(process.memory_info().rss))

        if "11" in options['main_processing']:
            logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            logger.info('Thresholds without tetramer to validate')
            logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            #bug in cell counts and DP clns sum
            processed_file_aa_pval_names = glob(path_processed_data_folder + '*CDR3_amino_acid_clonotypes_pval.csv')

            for filename_aa in processed_file_aa_pval_names:
                specific_unspecific_matrix_df = provide_thresholds_DbPos(filename_aa, "clonotypes", bonferroni=True)
                logger.debug("specific_unspecific_matrix_df clonotypes: ", specific_unspecific_matrix_df)
                produce_specific_unspecific_perf_plot(path_tables_and_figures_folder, specific_unspecific_matrix_df,
                                                      "clonotypes")

                specific_unspecific_matrix_df = provide_thresholds_DbPos(filename_aa, "cells", bonferroni=True)
                logger.debug("specific_unspecific_matrix_df cells: ", specific_unspecific_matrix_df)
                produce_specific_unspecific_perf_plot(path_tables_and_figures_folder, specific_unspecific_matrix_df,
                                                      "cells")

                process = Process(getpid())
                logger.debug('Before mem flush: ', sizeof_fmt(process.memory_info().rss))
                collect()
                process = Process(getpid())
                logger.debug('After mem flush: ', sizeof_fmt(process.memory_info().rss))

        if "12" in options['main_processing']:
            logger.info('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            logger.info('Bonferroni correction + negative control culture removal')
            logger.info('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            processed_file_aa_pval_names = glob(path_processed_data_folder + '*CDR3_amino_acid_clonotypes_pval.csv')

            for filename_aa in processed_file_aa_pval_names:
                pvalues_df = provide_thresholds_negctrl(path_tables_and_figures_folder, filename_aa, 'PT', bonferroni=True)
                logger.debug("pvalues: ", pvalues_df)

                pvalues_df = provide_thresholds_negctrl(path_tables_and_figures_folder, filename_aa, 'TG', bonferroni=True)
                logger.debug("pvalues: ", pvalues_df)

                process = Process(getpid())
                logger.debug('Before mem flush: ', sizeof_fmt(process.memory_info().rss))
                collect()
                process = Process(getpid())
                logger.debug('After mem flush: ', sizeof_fmt(process.memory_info().rss))

        if "13" in options['main_processing']:
            logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            logger.info('Expansion thresholds identification clonotypes expanded in all repeats     ')
            logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

            processed_file_aa_pval_names = glob(path_processed_data_folder + '*CDR3_amino_acid_clonotypes_pval.csv')

            # for filename_aa in processed_file_aa_pval_names:
                # specific_unspecific_matrix_df = provide_thresholds_DbPos(filename_aa, "clonotypes", bonferroni=True)
                # print("specific_unspecific_matrix_df clonotypes: ", specific_unspecific_matrix_df)
                # produce_specific_unspecific_perf_plot(path_tables_and_figures_folder, specific_unspecific_matrix_df,
                #                                       "clonotypes")

            # specific_unspecific_matrix_df, stacked_df = provide_thresholds_DbPos_removing_mixed_clns(processed_file_aa_pval_names)
            #
            # print("specific_unspecific_matrix_df cells: ", specific_unspecific_matrix_df)
            # print("stacked_df: ", stacked_df)
            #
            # specific_unspecific_matrix_df.to_csv(path_tables_and_figures_folder + "all_donors_stats_dp_perf.csv")
            #
            # # produce_specific_unspecific_removing_mixed_clns_perf_plot(path_tables_and_figures_folder, specific_unspecific_matrix_df,
            # #                                       "cells")
            #
            # produce_specific_unspecific_removing_mixed_clns_perf_plot(path_tables_and_figures_folder, stacked_df, "clonotypes")

            threshold=1.35E-12
            get_expanded_clonotypes_with_a_threshold(path_tables_and_figures_folder, processed_file_aa_pval_names, threshold)

            process = Process(getpid())
            print('Before mem flush: ', sizeof_fmt(process.memory_info().rss))
            collect()
            process = Process(getpid())
            print('After mem flush: ', sizeof_fmt(process.memory_info().rss))
        if "14" in options['main_processing']:
            logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            logger.info('Plot mixture pure plots pvalue comparison                                  ')
            logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

            processed_file_aa_pval_names = glob(path_processed_data_folder + '*CDR3_amino_acid_clonotypes_pval.csv')
            plot_mixed_pure_frequencies(path_tables_and_figures_folder, processed_file_aa_pval_names)

            process = Process(getpid())
            print('Before mem flush: ', sizeof_fmt(process.memory_info().rss))
            collect()
            process = Process(getpid())
            print('After mem flush: ', sizeof_fmt(process.memory_info().rss))

        if "15" in options['main_processing']:
            logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            logger.info('Leave One Out cross validation                                             ')
            logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

            processed_file_aa_pval_names = glob(path_processed_data_folder + '*CDR3_amino_acid_clonotypes_pval.csv')
            plot_mixed_pure_frequencies(path_tables_and_figures_folder, processed_file_aa_pval_names)

            process = Process(getpid())
            logger.debug('Before mem flush: ', sizeof_fmt(process.memory_info().rss))
            collect()
            process = Process(getpid())
            logger.debug('After mem flush: ', sizeof_fmt(process.memory_info().rss))

        logger.info("--- Program finishes at: %s ---" % asctime(localtime(time())))
    except Exception as e:
        print(e)
        process = Process(getpid())
        print('Memory usage before error raised: ', sizeof_fmt(process.memory_info().rss))
