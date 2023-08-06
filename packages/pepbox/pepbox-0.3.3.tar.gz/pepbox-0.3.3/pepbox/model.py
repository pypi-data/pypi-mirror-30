__author__ = 'jlane'


from pandas import DataFrame, Series, concat, read_csv, merge
from re import search, match
from collections import Counter
import numpy as np
from numpy import array, where, concatenate, intersect1d, setdiff1d, sum, unique, isnan, arange
from enum import Enum
from copy import copy
from glob import glob
from os import path, stat
from sys import stdout, getsizeof
from math import ceil
import scipy.stats
#from memory_profiler import profile
from gc import collect, garbage
from scipy.stats import spearmanr, pearsonr
# import matplotlib as plt
import matplotlib.pyplot as plt
from matplotlib_venn import venn3, venn3_circles
import logging


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


class TimePoint(object):
    def __init__(self, id, samples):
        self.id = id
        self.samples = samples

class TimePoints:
    def __init__(self, samples, comparisonset_infos):
        self.samples = samples
        self.comparisonset_infos = comparisonset_infos
        self.dictionary = {}
        self.initiate_tps()

    def initiate_tps(self):
        for sample in self.samples:
            tp = sample.get_time_point()
            if tp in self.dictionary.keys():
                self.dictionary[tp].append(sample)
            else:
                self.dictionary[tp] = ClonotypeSamples(samples=[sample])

    def tostring(self):
        mstr= ""
        for k in self.dictionary.keys():
            mstr += str(k) + ": " + str(self.dictionary[k].get_sample_ids()) + "\n"
        return mstr


class Edges(list):
    def __init__(self, edges=None):
        if edges is not None:
            self.extend(edges)

    def is_present(self, vertice_pair_relation):
        id_to_match = "_".join(concatenate(vertice_pair_relation))
        for e in self:
            if match(".*" + id_to_match + ".*", e.id):
                return True
        return False


    def get_ids(self):
        myids = []
        for e in self:
            myids.append(e.id)
        return myids

    def __repr__(self):
        return str(self)

    def __str__(self):
        mystr=""
        for e in self:
            mystr += e.id + ", "
        return mystr



class Edge:
    def __init__(self, vertice_pair, edge_relation, index):
        self.index = index
        self.vertice_pair = vertice_pair
        self.edge_relation = edge_relation
        self.id = "_".join(concatenate([vertice_pair , edge_relation, [index]]))

class Graph:
    def __init__(self, samples, selected_clns_ids=None, reference_sp=None, vertices=None, edges=None, incidence_matrix=None, adjacency_matrix=None):
        self.samples = samples

        self.selected_clns_ids = selected_clns_ids

        self.vertices = vertices
        self.edges = edges

        self.incidence_matrix = incidence_matrix
        self.adjacency_matrix = adjacency_matrix

        self.vertices = self.create_vertices_vtp()

        print(self.vertices.tostring())

        # self.venn3_table = self.venn_table(reference_sp=reference_sp[0])

        # self.edges = self.create_edges_vtp(reference_sp=reference_sp[0])
        #
        # print("# edges:", len(self.edges))
        #
        # self.create_graph_vtpeclns()


    #Create an graph matrices with time points as vertices and clonotype as edges
    def create_graph_vtpeclns(self):
        # self.create_time_point_incidence_matrix()
        self.create_time_point_adjacency_matrix()


    #Create an graph matrices with clonotype as vertices and time points as edges
    def create_graph_vclnsetp(self):
        self.create_time_point_incidence_matrix()
        self.create_time_point_adjacency_matrix()


    def create_vertices_vtp(self):
        print("create time point vertices")
        return self.samples.get_time_points()

    def venn_table(self, path_tables_and_figures_folder, subject_id, reference_sp=None):
        print("create edges between time point vertices")

        mytimepoints = self.vertices.dictionary

        list_tp = sorted(mytimepoints.keys())

        # print(list_tp)

        vertices_pair_relation = {}

        # all_clns_ids_before = self.samples.get_aa_clonotype_ids_list()
        # all_clns_ids= setdiff1d(all_clns_ids_before, list(set(self.selected_clns_ids)))

        if self.selected_clns_ids is not None:
            all_clns_ids = self.selected_clns_ids
        else:
            all_clns_ids = self.samples.get_aa_clonotype_ids_list()

        print("# analyzed clns: ", str(len(all_clns_ids)))

        if reference_sp is not None:
            ref_clns_id_list = reference_sp.get_aa_clonotype_ids_list()
            ref_intersect = intersect1d(all_clns_ids, ref_clns_id_list)

            print("CD4 intersect: ", len(ref_intersect))

        venn_table_list = []
        for tp_index1 in arange(0, len(list_tp)):
            tp_1 = list_tp[tp_index1]
            tp_samples1 = mytimepoints[tp_1]

            tp_samples1cp = ClonotypeSamples(samples=tp_samples1)

            for cell_type1 in tp_samples1cp.get_cell_types():

                my_tp_samples1 = tp_samples1cp.get_samples_by_cell_types([cell_type1])

                # if reference_sp is not None:
                #     tp_samples1cp.append(reference_sp)

                tp_1_clns_ids = intersect1d(all_clns_ids, my_tp_samples1.get_aa_clonotype_ids_list())
                # myclnsnumpertp.append([str(tp_1), str(len(tp_1_clns_ids))])
                clns_ids_tp1_celltype1 = my_tp_samples1.get_aa_clonotype_ids_list()
                # print("# analyzed clns for  ", [str(tp_1), str(len(tp_1_clns_ids))])
                # print(tp_1_clns_ids[0:5])


                # if (len(list_tp) - 1) > tp_index1:
                for tp_index2 in arange(tp_index1, len(list_tp)):
                    tp_2 = list_tp[tp_index2]
                    tp_samples2 = mytimepoints[tp_2]
                    cell_types_tp_sp2 = tp_samples2.get_cell_types()

                    mycell_types2=[]
                    if cell_type1 in cell_types_tp_sp2:
                        myindex = cell_types_tp_sp2.index(cell_type1)
                        del cell_types_tp_sp2[myindex]
                    for cell_type2 in  cell_types_tp_sp2:

                        tp_samples2.get_samples_by_cell_types([cell_type2])
                        my_tp_samples2 = tp_samples2.get_samples_by_cell_types([cell_type2])
                        clns_ids_tp2_celltype2 = my_tp_samples2.get_aa_clonotype_ids_list()

                        fig = plt.figure()
                        nclnscd4 = intersect1d(all_clns_ids, reference_sp.get_aa_clonotype_ids_list())
                        v = venn3([set(nclnscd4), set(clns_ids_tp1_celltype1), set(clns_ids_tp2_celltype2)], ('CD4 tp1', cell_type1 + "_" +str(tp_1), cell_type2 + "_" +str(tp_2)))
                        plt.savefig(path_tables_and_figures_folder + str(subject_id) + cell_type1 + "_" +str(tp_1) + "-"+cell_type2 + "_" +str(tp_2) +'.pdf', format='pdf', bbox_inches='tight')

                        myids=['111','110','011','010','101','100','001']
                        mylist=[str(tp_1), str(tp_2), cell_type1 , cell_type2]
                        for id in myids:
                            # print(v.get_label_by_id(id))

                            if v.get_label_by_id(id) is None:
                                mylist.append(0)
                            else:
                                mylist.append(int(str(v.get_label_by_id(id)).split(",")[2].split("'")[1]))
                    # print(v.get_label_by_id('111'))
                    venn_table_list.append(mylist)

        mycols = ["time point x", "time point y", "cell type x", "cell type y"]
        mycols.extend(myids)
        mydf = DataFrame(venn_table_list, columns=mycols)
        print(mydf)


        return mydf

    def create_edges_vtp(self, reference_sp=None):
        print("create edges between time point vertices")
        E = Edges()
        index = 0

        mytimepoints = self.vertices.dictionary

        list_tp = sorted(mytimepoints.keys())

        vertices_pair_relation = {}

        # all_clns_ids_before = self.samples.get_aa_clonotype_ids_list()
        # all_clns_ids= setdiff1d(all_clns_ids_before, list(set(self.selected_clns_ids)))

        if self.selected_clns_ids is not None:
            all_clns_ids = self.selected_clns_ids
        else:
            all_clns_ids = self.samples.get_aa_clonotype_ids_list()

        print("# analyzed clns: ", str(len(all_clns_ids)))
        if reference_sp is not None:
            ref_clns_id_list = reference_sp.get_aa_clonotype_ids_list()
            ref_intersect = intersect1d(all_clns_ids, ref_clns_id_list)
            print("CD4 intersect: ", len(ref_intersect))

        myclnsnumpertp=[]
        for tp_index1 in arange(0, len(list_tp)):
            tp_1 = list_tp[tp_index1]
            tp_samples1 = mytimepoints[tp_1]

            tp_samples1cp = ClonotypeSamples(samples=tp_samples1)

            # if reference_sp is not None:
            #     tp_samples1cp.append(reference_sp)

            tp_1_clns_ids = intersect1d(all_clns_ids, tp_samples1cp.get_aa_clonotype_ids_list())
            myclnsnumpertp.append([str(tp_1), str(len(tp_1_clns_ids))])

            # print("# analyzed clns for  ", [str(tp_1), str(len(tp_1_clns_ids))])
            # print(tp_1_clns_ids[0:5])

            clonotype_ids_intersecting_tp1 = []
            if (len(list_tp)- 1) > tp_index1:
                for tp_index2 in arange(tp_index1 + 1, len(list_tp)):
                    tp_2 = list_tp[tp_index2]
                    tp_samples2 = mytimepoints[tp_2]

                    for sample1_index in arange(0, len(tp_samples1cp)):
                        sample1 = tp_samples1cp[sample1_index]
                        for sample2_index in arange(0, len(tp_samples2)):
                            sample2 = tp_samples2[sample2_index]



                            intersection_set = intersect1d(sample1.get_aa_clonotype_ids_list(), sample2.get_aa_clonotype_ids_list())
                            for clonotype_id in intersection_set:
                                clonotype_ids_intersecting_tp1.append(clonotype_id)
                                vertice_pair = [tp_1, tp_2]
                                edge_relation = [clonotype_id, sample1.get_repeat_ID(), sample2.get_repeat_ID(), sample1.get_cell_type(), sample2.get_cell_type()]
                                # edge_relation = [clonotype_id]
                                # my_id = "_".join(concatenate([vertice_pair, edge_relation]))

                                E.append(Edge(vertice_pair, edge_relation, index))
                                index += 1

                                if clonotype_id not in vertices_pair_relation.keys() :
                                    vertices_pair_relation[clonotype_id] = 1
                                else:
                                    vertices_pair_relation[clonotype_id] = vertices_pair_relation[clonotype_id] +1

                    # print("time points: ", [tp_1, tp_2])
                    # print("# clns intersecting: ",  len(list(set(clonotype_ids_intersecting_tp1))))

            clns_in_tp1_only = setdiff1d(tp_1_clns_ids, list(set(clonotype_ids_intersecting_tp1)))

            print("# clns left, # clns intersecting: ", [len(clns_in_tp1_only), len(list(set(clonotype_ids_intersecting_tp1)))] )

            for clonotype_id in clns_in_tp1_only:
                vertice_pair = [tp_1, tp_1]
                edge_relation = [clonotype_id, sample1.get_repeat_ID(), sample1.get_repeat_ID(),
                                 sample1.get_cell_type(), sample1.get_cell_type()]

                # edge_relation = [clonotype_id]
                # my_id = "_".join(concatenate([vertice_pair, edge_relation]))

                if clonotype_id not in vertices_pair_relation.keys():
                    vertices_pair_relation[clonotype_id] = 1
                    E.append(Edge(vertice_pair, edge_relation, index))
                    index += 1
                else:
                    vertices_pair_relation[clonotype_id] = vertices_pair_relation[clonotype_id] + 1

        print("total # clns per tp: ")
        print(DataFrame(myclnsnumpertp ))
        return E

    def create_time_point_adjacency_matrix(self):
        print("create time point adjacency matrix")

        V = sorted(self.vertices.dictionary.keys())
        E = self.edges
        matrix = [[0] * len(V)] * len(V)
        self.adjacency_matrix = DataFrame(matrix, columns=V, index=V)
        for edge in E:
            vertice_pair = edge.vertice_pair
            vertex1 = vertice_pair[0]
            vertex2 = vertice_pair[1]

            # print(vertex1, vertex2)
            if vertex1 == vertex2:
                value1 = self.adjacency_matrix.ix[vertex1, vertex2]
                self.adjacency_matrix.ix[vertex1, vertex2] = value1 + 1
            else:
                value1 = self.adjacency_matrix.ix[vertex1, vertex2]
                self.adjacency_matrix.ix[vertex1, vertex2] = value1 + 1

                value2 = self.adjacency_matrix.ix[vertex2, vertex1]
                self.adjacency_matrix.ix[vertex2, vertex1] = value2 + 1


    def create_time_point_incidence_matrix(self):
        print("create time point incidence matrix")

        V = self.vertices.dictionary.keys()
        E = self.edges
        matrix = [[0] * len(E)] * len(V)
        E_ids = E.get_ids()
        self.incidence_matrix = DataFrame(matrix, columns=E_ids, index=V)
        print("incidence matrix shape: ",self.incidence_matrix.shape)
        for vertex in V:
            for edge in E:
                if vertex in edge.vertice_pair:
                    # print(vertex)
                    # print(str(edge_id))
                    self.incidence_matrix.ix[vertex, edge.id] = 1

class MetadataFile(Enum):
    file_name = ("file name", 1, str)
    sequencing_ID = ("sequencing ID", 2, str)
    mapped_ID = ("mapped ID", 3, str)
    trait = ("trait", 4, str)
    subject_id = ("subject id", 5, str)
    analysis_software = ("analysis software", 6, str)
    time_point = ("time point", 7, str)
    cell_type = ("cell type", 8, str)
    peptide = ("peptide", 9, str)
    peptide_sequence = ("peptide sequence", 10, str)
    experiment = ("experiment", 11, str)
    repeat = ("repeat", 12, str)
    repeat_type = ("repeat type", 13, str)
    sequencing_company = ("sequencing company", 14, str)
    run = ("run", 15, str)
    total_cell_count_before_culture = ("total cell count before culture", 16, str)
    total_cell_count_after_culture = ("total cell count after culture", 17, str)
    frequency_T_cell_type_bc = ("frequency T cell type bc", 18, str)
    frequency_T_cell_type_ac = ("frequency T cell type ac", 19, str)
    T_cells_count_before_culture = ("T cells count before culture", 20, str)
    T_cells_count_after_culture = ("T cells count after culture", 21, str)
    data_sequenced = ("data sequenced", 22, str)
    type_of_sequencing = ("type of sequencing", 23, str)
    organism = ("organism", 24, str)
    MHC = ("MHC", 25, str)
    chain = ("chain", 26, str)
    sequencing_level = ("sequencing level", 27, str)
    read_length = ("read length", 28, str)

    @staticmethod
    def get_col_names():
        values = []
        ranks = []
        #print(list(AdaptiveBiotechFileColumn))
        for my_enum in AdaptiveBiotechFileColumn:
            values.append(my_enum.value[0])
            ranks.append(my_enum.value[1])

        return [x for (y,x) in sorted(zip(ranks, values))]

    @staticmethod
    def get_col_types():
        types = []
        ranks = []
        #print(list(AdaptiveBiotechFileColumn))
        for my_enum in AdaptiveBiotechFileColumn:
            types.append(my_enum.value[2])
            ranks.append(my_enum.value[1])
        return [x for (y,x) in sorted(zip(ranks, types))]

    @staticmethod
    def convert_types(sorted_df):
        col = 0
        for col_type in AdaptiveBiotechFileColumn.get_col_types():
            colname = sorted_df.columns.values[col]
            s = sorted_df[colname]

            # print(col)
            # print(colname)
            # print(col_type)

            if col_type is int:
                s = s.fillna(0)
                s = s.replace('', 0)
                #index_values = [i for i in s.index if str(s[i]) != 'nan']
                s = s.astype(float)
                s = s.astype(col_type)
                sorted_df[colname] = s.replace(0, '')
            else:
                sorted_df[colname] = s.astype(col_type)
            col = col + 1

        return sorted_df

    # adaptive Biotechnologies (alias AB), processed
    @staticmethod
    def check_format(f):
        for col in f.columns.values:
            if col not in MetadataFile.get_col_names():
                return 'FAILURE'
        return 'SUCCES'


class AdaptiveBiotechFileColumn(Enum):
    nucleotide=("nucleotide",1,str)
    aminoAcid=("aminoAcid",2,str)
    count=("count (templates)",3,int)
    frequencyCount=("frequencyCount (%)",4,float)
    cdr3Length=("cdr3Length",5,int)
    vMaxResolved=("vMaxResolved",6,str)
    vFamilyName=("vFamilyName",7,str)
    vGeneName=("vGeneName",8,str)
    vGeneAllele=("vGeneAllele",9,int)
    vFamilyTies=("vFamilyTies",10,str)
    vGeneNameTies=("vGeneNameTies",11,str)
    vGeneAlleleTies=("vGeneAlleleTies",12,str)
    dMaxResolved=("dMaxResolved",13,str)
    dFamilyName=("dFamilyName",14,str)
    dGeneName=("dGeneName",15,str)
    dGeneAllele=("dGeneAllele",16,int)
    dFamilyTies=("dFamilyTies",17,str)
    dGeneNameTies=("dGeneNameTies",18,str)
    dGeneAlleleTies=("dGeneAlleleTies",19,str)
    jMaxResolved=("jMaxResolved",20,str)
    jFamilyName=("jFamilyName",21,str)
    jGeneName=("jGeneName",22,str)
    jGeneAllele=("jGeneAllele",23,int)
    jFamilyTies=("jFamilyTies",24,str)
    jGeneNameTies=("jGeneNameTies",25,str)
    jGeneAlleleTies=("jGeneAlleleTies",26,str)
    vDeletion=("vDeletion",27,int)
    n1Insertion=("n1Insertion",28,int)
    d5Deletion=("d5Deletion",29,int)
    d3Deletion=("d3Deletion",30,int)
    n2Insertion=("n2Insertion",31,int)
    jDeletion=("jDeletion",32,int)
    vIndex=("vIndex",33,int)
    n1Index=("n1Index",34,int)
    dIndex=("dIndex",35,int)
    n2Index=("n2Index",36,int)
    jIndex=("jIndex",37,int)
    estimatedNumberGenomes=("estimatedNumberGenomes",38,int)
    sequenceStatus=("sequenceStatus",39,str)
    cloneResolved=("cloneResolved",40,str)
    vOrphon=("vOrphon",41,str)
    dOrphon=("dOrphon",42,str)
    jOrphon=("jOrphon",43,str)
    vFunction=("vFunction",44,str)
    dFunction=("dFunction",45,str)
    jFunction=("jFunction",46,str)
    fractionNucleated=("fractionNucleated",47,int)

    @staticmethod
    def get_col_names():
        values = []
        ranks = []
        #print(list(AdaptiveBiotechFileColumn))
        for my_enum in AdaptiveBiotechFileColumn:
            values.append(my_enum.value[0])
            ranks.append(my_enum.value[1])

        return [x for (y,x) in sorted(zip(ranks, values))]

    @staticmethod
    def get_col_types():
        types = []
        ranks = []
        #print(list(AdaptiveBiotechFileColumn))
        for my_enum in AdaptiveBiotechFileColumn:
            types.append(my_enum.value[2])
            ranks.append(my_enum.value[1])
        return [x for (y,x) in sorted(zip(ranks, types))]

    @staticmethod
    def check_format(files_to_check):
        failed_files = []
        for f in files_to_check:
            f_df = read_csv(f, sep=" ")
            for col in f_df.columns.values:
                if col not in AdaptiveBiotechFileColumn.get_col_names():
                    failed_files.append(path.basename(f))
                    break
        if len(failed_files) > 0:
            return ['FAILURE', failed_files]
        return ['SUCCES']

    @staticmethod
    def convert_types(sorted_df):
        col = 0
        for col_type in AdaptiveBiotechFileColumn.get_col_types():
            colname = sorted_df.columns.values[col]
            s = sorted_df[colname]

            # print(col)
            # print(colname)
            # print(col_type)

            if col_type is int:
                s = s.fillna(0)
                s = s.replace('', 0)
                #index_values = [i for i in s.index if str(s[i]) != 'nan']
                s = s.astype(float)
                s = s.astype(col_type)
                sorted_df[colname] = s.replace(0, '')
            else:
                sorted_df[colname] = s.astype(col_type)
            col = col + 1

        return sorted_df


class ClonotypeID:
    def __init__(self, ids_tuple):
        if type(ids_tuple) is list:
            ids_tuple = DataFrame(ids_tuple, columns=["aminoAcid", "vMaxResolved", "jMaxResolved"])

            print("ids_tuple_df", ids_tuple)

            self.aa = ids_tuple["aminoAcid"]
            self.v = ids_tuple["vMaxResolved"]
            # self.d = ids_tuple["dMaxResolved"]
            self.j = ids_tuple["jMaxResolved"]

            self.idlist_df = ids_tuple.apply(lambda x: '_'.join(x.astype(str)), axis=1)

            print("idlist_df: ", self.idlist_df)

        else:
            print(ids_tuple)
            print("ERROR: no tuple were provided for clonotype ids")

class Statistics:
    def __init__(self, df):
        if isinstance(df, Series) or (type(df) is list):
            self.dataframe = DataFrame(df)
        else:
            self.dataframe = df

    def get_df_col(self, colname ):
        return self.dataframe[colname]

    #not case sensitive
    def get_df_col_approx(self, motif):
        colnames = []
        motif = motif.replace('+', '\+')
        motif = motif.replace('-', '\-')
        for i in range(len(self.dataframe.columns.values)):
            if search(motif.lower(), self.dataframe.columns.values[i].lower()):
                colnames.append(self.dataframe.columns.values[i])
        init = True
        cols = []
        for colname in colnames:
            if init:
                cols = self.get_df_col(colname)
                init = False
            else:
                col = self.get_df_col(colname)
                cols = concat([cols, col], axis=1)
        return cols

    @staticmethod
    def pvalues_fisher(sp_invitro, sp_exvivo, total_invitro_genome_counts, total_exvivo_genome_counts, source_indexes, dist='right_tail', speed='fast'):

        print('# of clonotypes to compare: ', str(len(source_indexes)))
        total_iter = ceil(len(source_indexes) / float(10000))
        print('# cells [total exvivo, total invitro]: ', [total_exvivo_genome_counts, total_invitro_genome_counts])

        iter = 0
        pvalues = []
        j=0

        # print("sp_invitro: ", sp_invitro)
        # print("sp_exvivo: ", sp_exvivo)

        for i in source_indexes:
            if (j % 10000) == 0:
                iter=iter+1
                # print("Fisher exact test progress: %d%%   \r" % ((float(iter)/total_iter)*100) )
                stdout.write("Fisher exact test progress: %d%%   \r" % ((float(iter)/total_iter)*100) )
                stdout.flush()

            j += 1

            counts_clonotype_invitro = sp_invitro[i]
            counts_clonotype_exvivo = sp_exvivo[i]

            not_counts_clonotype_invitro = total_invitro_genome_counts - counts_clonotype_invitro
            not_counts_clonotype_exvivo = total_exvivo_genome_counts - counts_clonotype_exvivo

            if speed == 'slow':
                # print('slow')
                if dist == 'right_tail':
                    oddratio, pvalue = scipy.stats.fisher_exact([[counts_clonotype_invitro, not_counts_clonotype_invitro],
                                                                [counts_clonotype_exvivo, not_counts_clonotype_exvivo]],
                                                                alternative = 'greater')
            # else:
            #     print('fast')
            #     if dist == 'left_tail':
            #         pvalue = fisher.pvalue(counts_clonotype_invitro, counts_clonotype_exvivo, not_counts_clonotype_invitro, not_counts_clonotype_exvivo).left_tail#.right_tail
            #     if dist == 'two_tail':
            #         pvalue = fisher.pvalue(counts_clonotype_invitro, counts_clonotype_exvivo, not_counts_clonotype_invitro, not_counts_clonotype_exvivo).two_tail
            #     if dist == 'right_tail':
            #         pvalue = fisher.pvalue(counts_clonotype_invitro, counts_clonotype_exvivo, not_counts_clonotype_invitro, not_counts_clonotype_exvivo).right_tail

            pvalues.append(pvalue)
        pvalues = Series(pvalues, index=source_indexes)

        return pvalues

class Counts(Statistics):
    def __init__(self, df):
        Statistics.__init__(self, df)

    def make_func_get_freq(self, total):
        return lambda counts: float(counts)/total

    def convert_df_col_counts_2_freq(self, total, column=None):
        if column is not None:
            if not isinstance(column, Series):
                raise

        if total > 0:
            fun = self.make_func_get_freq(total)
            #print(total)
            if column is None:
                #print(self.dataframe)
                list_of_counts = list(concatenate(self.dataframe.values.tolist()))
                #freq = divide(array(list_of_counts), float(total))
                #print('counts: ', list_of_counts)
                #print('freq: ', freq)
                #print('test: ', Series(map(fun, self.dataframe)))
                #map(print, self.dataframe)
                #print(list_of_counts)
                return Series(map(fun, list_of_counts), index=self.dataframe.index)
            else:
                return Series(map(fun, column), index=column.index)
        else:
            #print(column)
            #print(type(column))
            #logging.warn('Some of your samples have no clonotypes!')
            if column is None:
                raise
            else:
                return Series(column, index=column.index)

    def get_total(self, df_counts=None):
        totalcounts = []
        if df_counts is not None:
            for colname in df_counts.columns.values:
                totalcounts.append(sum(df_counts[colname]))
        else:
            for colname in self.dataframe.columns.values:
                totalcounts.append(sum(self.dataframe[colname]))
        return totalcounts

    def convert_df_counts_2_freq(self, totalcounts):
        clonotypes = None
        if len(self.dataframe.columns.values) == 1:
            if totalcounts > 0:
                clonotypes = self.convert_df_col_counts_2_freq(totalcounts)
        # else:
        #     for i in range(len(self.dataframe.columns.values)):
        #         colname = self.dataframe.columns.values[i]
        #         #print('colname: ', colname)
        #         #if colname == 'estimatedNumberGenomes_B-XV-1':
        #         #        print('estimatedNumberGenomes_B-XV-1 tot counts:', totalcounts[i])
        #         if i == 0:
        #              col = self.convert_df_col_counts_2_freq(totalcounts[i], self.dataframe.iloc[:, i])
        #              clonotypes = DataFrame({colname: col})
        #         else:
        #             col = self.convert_df_col_counts_2_freq(totalcounts[i], self.dataframe.iloc[:, i])
        #             clonotypes[colname] = col

        return clonotypes

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.dataframe)


class Frequencies(Statistics):
    def __init__(self, df):
        Statistics.__init__(self, df)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.dataframe)

    def get_col(self, colname):
        return Frequencies(self.get_df_col(colname))

    def get_col_elt(self, colname, elt):
        return Frequencies(self.get_df_col_elt(colname,elt))

    def get_col_values_by_indexes(self, indexes):
        return Frequencies(self.get_df_col_values_by_indexes(indexes))

class ClonotypeSequencesInfoFile:
    def __init__(self, comparison_dataset, df):
        self.comparison_dataset = comparison_dataset
        self.dataframe = df
        self.count_columnp = 'estimatedNumberGenomes|cell_count|Read.count'

    def is_nt_clonotypes(self):
        if 'nucleotide' in self.dataframe.columns.values:
            return True
        return False

    def get_pvalues(self, ID):
        column = ID + '_pval'
        # print('col to look for: ', column)
        if column in self.dataframe.columns.values:
            return self.dataframe[column].astype(float)
        return None

    def get_aa_clonotype_sequence(self, clonotype_index):
        column = 'aminoAcid'
        if column in self.dataframe.columns.values:
            return self.dataframe[column][clonotype_index]
        return None

    def get_aa_clonotype_seq_gene_name_cell_count(self, clonotype_index=None):
        if clonotype_index is None:
            temp_df = self.get_df_cols(['aminoAcid', 'vMaxResolved', 'jMaxResolved', 'estimatedNumberGenomes'])
            return self.filter_allele_from_gene_name(temp_df)

        temp_df = self.get_df_cols(['aminoAcid', 'vMaxResolved', 'jMaxResolved', 'estimatedNumberGenomes'])[clonotype_index]
        return self.filter_allele_from_gene_name(temp_df)

    def get_cdr3_associated_nt_clonotype_counts_df(self):
        df = self.get_df_col('# nucleotide sequences with that CDR3')
        return df

    def get_genome_counts_for_sample_id_by_aa_clonotype_ids(self, sample_id):
        genome_counts_df = self.get_counts_genomes()
        if genome_counts_df is not None:
            df = genome_counts_df.get_df_col_approx('.*_' + sample_id + '$|^' + sample_id + '_.*').astype(int)

            return df[df > 0]
        return None

    def get_genome_counts_for_sample_id(self, sample_id):
        # print("sample id: ",sample_id)
        genome_counts_df = self.get_counts_genomes( )

        # print("sample id: ", genome_counts_df)

        if genome_counts_df is not None:
            # print(sample_id)
            if sample_id == '':
                Exception("Sample id is an empty string: " + sample_id)
            # print(genome_counts_df.get_df_col_approx('_' + sample_id + '$|^' + sample_id + '_'))
            gc_df = Series(genome_counts_df.get_df_col_approx('.*_' + sample_id + '$|^' + sample_id + '_.*'))

            if len(gc_df) > 0:
                df = gc_df.astype(float).astype(int)
                # print("get_genome_counts_for_sample_id: ", df)
                return Counts(df[df > 0])
            else:
                Exception("No sample id in cloumns name : " + sample_id)
        return None

    def get_df_col_approx_include_exclude(self, inclusion_motifs, exclusion_motifs=None):
        colnames = []

        inclusion_motifs = inclusion_motifs.replace('+', '\+')
        inclusion_motifs = inclusion_motifs.replace('-', '\-')

        exclusion_motifs = exclusion_motifs.replace('+', '\+')
        exclusion_motifs = exclusion_motifs.replace('-', '\-')

        for i in range(len(self.dataframe.columns.values)):
            if search(inclusion_motifs.lower(), self.dataframe.columns.values[i].lower()):
                if exclusion_motifs is not None:
                    if not search(exclusion_motifs.lower(), self.dataframe.columns.values[i].lower()):
                        colnames.append(self.dataframe.columns.values[i])
                else:
                    colnames.append(self.dataframe.columns.values[i])
            elif not search(exclusion_motifs.lower(), self.dataframe.columns.values[i].lower()):
                if not search('^frequency', self.dataframe.columns.values[i].lower()):
                    colnames.append(self.dataframe.columns.values[i])

        init = True
        cols = []

        for colname in colnames:
            if init:
                cols = self.get_df_col(colname)
                init = False
            else:
                col = self.get_df_col(colname)
                cols = concat([cols, col], axis=1)
        return cols

    def get_info(self, sample_ids=[], clonotype_ids=[], excluded_col_info=[]):
        start = True
        inclusion_motifs = ''
        for sample_id in sample_ids:
            if start:
                inclusion_motifs = sample_id
                start = False
            else:
                inclusion_motifs = inclusion_motifs + '|' + sample_id
        exclusion_motifs = ''
        if len(excluded_col_info) > 0:
            start = True
            for info in excluded_col_info:
                if start:
                    start = False
                    exclusion_motifs = '^' + info
                else:
                    exclusion_motifs = exclusion_motifs + '|^' + info
            exclusion_motifs = exclusion_motifs

        # print('inclusion_motifs: ', inclusion_motifs)
        # print('exclusion_motifs: ', exclusion_motifs)

        cols = self.get_df_col_approx_include_exclude(inclusion_motifs, exclusion_motifs)

        # print('get info cols: ', cols)

        df = self.dataframe.ix[clonotype_ids, cols.columns.values]
        return df

    def get_nucleotide_sequences(self, clonotype_index=None):
        if clonotype_index is None:
            return self.get_df_col('nucleotide')
        # print('nucleotides: ', self.get_df_col('nucleotide'))
        return self.get_df_col('nucleotide').ix[clonotype_index]

    def get_amino_acid_sequences_for(self, clonotype_index=None):
        if clonotype_index is None:
            return self.get_df_col('aminoAcid')
        return self.get_df_col('aminoAcid')[clonotype_index]

    def filter_allele_from_gene_name(self, df):
        temp_df = DataFrame([df[col].str.split("*", expand=True)[0] for col in df.columns]).T
        temp_df.columns=df.columns.values
        temp_df.index=df.index.values
        return temp_df

    #colnames 'vMaxResolved', 'dMaxResolved', 'jMaxResolved' remove alleles from strings
    def get_aa_seq_with_gene_name_for(self, clonotype_index=None):
        if clonotype_index is None:
            temp_df = self.get_df_cols(['aminoAcid', 'vMaxResolved', 'jMaxResolved'])
            return self.filter_allele_from_gene_name(temp_df)

        temp_df = self.get_df_cols(['aminoAcid', 'vMaxResolved', 'jMaxResolved'])[clonotype_index]
        return self.filter_allele_from_gene_name(temp_df)

    def get_counts_genomes(self):
        val = self.get_limits(self.count_columnp)
        if val is not None:
            start = val[0]
            end = val[1]
            return Counts(self.dataframe.iloc[:, start:end])
        return None

    def get_limits(self, statistics):
        indexes = []

        # print(self.dataframe.columns.values)

        for index in range(len(self.dataframe.columns.values)):
            if search(statistics, self.dataframe.columns.values[index]):
                print(self.dataframe.columns.values[index])
                indexes.append(index)
        if len(indexes) > 0:
            start_stats = min(indexes)
            end_stats = max(indexes) + 1
            return start_stats, end_stats
        return None

    def get_df_cols(self, colnames):
        existing_colnames=[]
        for colname in colnames:
            if colname not in self.dataframe.columns.values:
                print('WARN: no column with the name ' + colname)
            else:
                existing_colnames.append(colname)
        if len(existing_colnames) > 0:
            return self.dataframe[existing_colnames]
        else:
            print('WARN: no columns found' + colnames)
        return None

    def get_df_col(self, colname):
        if colname in self.dataframe.columns.values:
            return self.dataframe[colname]
        print('WARN: no column with the name ' + colname)
        return None

class ClonotypeSamplesInfoFile:
    def __init__(self, filename_abs_path=None, info_df=None):
        if filename_abs_path is not None:
            if stat(filename_abs_path).st_size == 0:
                raise ValueError('Metadata file is empty.')

            if not path.exists(filename_abs_path):
                raise ValueError('Metadata file is does not exists: ' + filename_abs_path)

            self.info_df = read_csv(filename_abs_path)

            # print(self.info_df["file name"])

            index_to_drop = where(self.info_df["file name"].isnull())[0]
            # print("index_to_drop: ", index_to_drop)
            self.info_df = self.info_df.drop(labels=index_to_drop)

            # print('filename_abs_path: ', self.info_df)

            if self.info_df is None:
                raise ValueError('Metadata file does not exist.')

            if self.check_name(self.info_df, format == "metadata") == 'FAILURE':
                raise  ValueError('Metadata file does not have the right format.')

            # print('self.info_df: ', self.info_df)

            mylist=[]
            for col in self.info_df.columns.values:
                # print(col)
                mylist.append(self.format_line(self.info_df[col]))

            self.info_df = DataFrame(mylist, index=self.info_df.columns.values).T

            self.info_df = self.info_df.astype(str)

            self.info_df['subject id'] = self.info_df['subject id'].str.lower()

            # print(self.info_df['subject id'])
            
            self.keys = self.info_df.columns.values

        elif info_df is not None:
            if self.check_name(info_df, format == "metadata") == 'FAILURE':
                raise  ValueError('Metadata file does not have the right format.')

            index_to_drop = where(self.info_df["file name"].isnull())[0]
            self.info_df = self.info_df.drop(labels=index_to_drop)

            mylist = []
            for col in info_df.columns.values:
                mylist.append(self.format_line(info_df[col]))

            self.info_df = DataFrame(mylist, index=info_df.columns.values).T

            # print(int(float(self.info_df['subject id'].iloc[0])))

            self.info_df['subject id'] = (self.info_df['subject id'].astype(float).astype(int).astype(str)).str.lower()
            self.keys = self.info_df.columns.values
        else:
            raise ValueError('Metadata file does not exist.')

        #print(self.info_df)
        if 'file name' in self.keys:
            self.filename = self.info_df['file name']

        if 'sequencing ID' in self.keys:
            # print(self.info_df['sequencing ID'].astype(str))
            self.sequencing_ID = self.info_df['sequencing ID'].astype(str).str.lower()
            # print(self.sequencing_ID)
        else:
            # print(type(self.filename))
            self.sequencing_ID = Series([x.split('.tsv')[0].lower() for x in self.filename], index=self.info_df.index)
            self.info_df = concat([self.sequencing_ID, self.info_df], axis=1)
            self.info_df.columns.values[0] = 'sequencing ID'
            self.info_df['subject id'] = (self.info_df['subject id'].astype(float).astype(int).astype(str)).str.lower()

        # self.sequencing_ID = self.sequencing_ID.astype('str')

        # print("sequencing ID: ", self.sequencing_ID)

        self.subject_id = self.info_df['subject id'].str.lower()
        self.peptide_sequence = self.info_df['peptide sequence']

        self.experiment = self.info_df['experiment'].str.lower()

        if 'cell type' in self.keys:
            self.cell_type = self.info_df['cell type'].str.lower()

        if 'repeat' in self.keys:
            self.repeat_ID = self.info_df['repeat'].str.lower()

        if 'trait' in self.keys:
            self.trait = self.info_df['trait'].str.lower()

        if 'time point' in self.keys:
            self.time_point = self.info_df['time point'].str.lower()

        if 'sequencing level' in self.keys:
            self.sequencing_level = self.info_df['sequencing level'].str.lower()

        if 'total cell count before culture' in self.keys:
            self.total_cell_count_before_culture = self.info_df['total cell count before culture']

    def check_name(self, f, format='AB'):
        if format == 'metadata':
            if MetadataFile.check_format(f)[0] == 'FAILURE':
                raise ValueError('Metadata file does not have the right format.')
        elif format == 'AB':
            if AdaptiveBiotechFileColumn.check_format(f)[0] == 'FAILURE':
                failed_files = AdaptiveBiotechFileColumn.check_format()[1]
                raise ValueError('Data files do not have the right format: ', failed_files)
        return 'SUCCESS'

    def get_info_on_samples(self, sample_sequencing_IDs=None, columns=None):
        df = []
        if sample_sequencing_IDs is not None:
            for id in sample_sequencing_IDs:
                s = self.getInfo(id, columns)
                if s is not None:
                    df.append(s)

            if columns is not None:
                return DataFrame(df, columns=columns)
            else:
                return DataFrame(df, columns=self.info_df.columns.values.tolist())

        if columns is not None:
            return df[columns]

        if (columns is None) & (sample_sequencing_IDs is None):
            return self.info_df

        return df

    def is_not_all_str(self, mylist):
        for val in mylist:
            if type(val) is not str:
                return True
        return False

    def format_line(self, myinputlist):
        mylist = []

        # print("myinputlist: ", myinputlist)

        if isinstance(myinputlist, DataFrame):
            # # print('zup: ', self.info_df)
            # print(myinputlist)
            # print(myinputlist.values.tolist())
            for elt in concatenate(myinputlist.values.tolist()):
                if type(elt) is str:
                    mylist.append(elt.lower())
                else:
                    mylist.append(elt)
            return mylist
        if isinstance(myinputlist, Series):
            for elt in myinputlist:
                if type(elt) is str:
                    mylist.append(elt.lower())
                else:
                    mylist.append(elt)
            return mylist

        print('ERROR: ' + str(type(myinputlist)) + ' of input parameter is not compatible by this method')
        return None

    def getInfo_as_df_for_sample(self, sample_sequencing_ID):
        index_mod = where(self.sequencing_ID  == sample_sequencing_ID)[0]
        return self.info_df.iloc[index_mod]

    #returns a list
    def getInfo(self, sample_sequencing_ID, columns=None):
        # print("self.sequencing_ID: ", self.sequencing_ID)
        # print("sample_sequencing_ID: ", sample_sequencing_ID)

        index_mod = where(self.sequencing_ID == sample_sequencing_ID)[0]
        real_index = [self.sequencing_ID.index.values[i] for i in index_mod]

        if len(real_index) > 0:
            all_columns = self.info_df.columns.values

            #print(real_index)
            if columns is not None:
                # print('columns: ', columns)

                if type(columns) is list:
                    selected_columns = []
                    for column in columns:
                        if column in all_columns:
                            selected_columns.append(column)
                        # else:
                            #print('No info on ' + column + ' found !!')
                    if len(selected_columns) > 0:
                        # print('self.info_df: ',self.info_df)
                        # print('real_index: ', real_index)
                        return self.format_line(self.info_df.ix[real_index, selected_columns])
                    return None
                else:
                    column = columns
                    if column in all_columns:
                        return self.format_line(self.info_df.ix[real_index, column])
                    #print('No info on ' + column + ' found !!')
                    return None
        elif len(real_index) == 0:
                return None

            # print('index: ', real_index)
            # print('test: ', self.format_line(self.info_df.ix[real_index,]))

        return self.format_line(self.info_df.ix[real_index,])

    def exclude_on_experiment_types(self, experiment_types=[]):
        return self.exclude_from_list(SampleCriteriaParameters([(SampleCriteriaCategories.experiment_type, experiment_types)]))

    def get_bool_and(self, request_criterion_params, sample_info):
        list_bool = []

        if len(request_criterion_params) > 0:
            for request_param in request_criterion_params:
                if request_param in sample_info.values:
                    list_bool.append(True)
                else:
                    list_bool.append(False)
            if all(list_bool):
                #print('in: ', [request_criterion_params, sample_criterion_params])
                return True
            return False

        return True

    def get_bool_or(self, request_criterion_params, sample_info):
        if len(request_criterion_params) > 0:
            for request_param in sample_info:
                if request_param in sample_info.values:
                    return True
            return False
        return True

    def get_bool_for_exclusion(self, request_criteria, sample_info):
        list_bool = []
        if len(request_criteria) > 0:
            for request_criterion in request_criteria:
                if request_criterion in sample_info.values:
                    list_bool.append(True)
                else:
                    list_bool.append(False)
            if all(list_bool):
                return True
            return False
        return False

    def get_from_list(self, criteria, sample_ids, selection='and'):
        selected_sps = []
        for sample in sample_ids:

            sample_info = self.getInfo_as_df_for_sample(sample)
            # print('sample_info: ',sample_info)
            booleans = []

            for criterion in criteria.keys():
                if (type(criteria[criterion]) != list):
                    raise

                if len(criteria[criterion]) > 0:

                    # print('criterion.value: ', criterion.value)
                    # print('criterion.name: ', criterion.name)

                    # print("requested: ",criteria[criterion])
                    # print("in sample: ", sample_info[criterion.value])
                    #
                    # print("requested: ", type(criteria[criterion][0]))
                    # print("type in sample: ", type(sample_info[criterion.value].iloc[0]))


                    if selection == 'and':
                        #print('comparison: ',[criterion.name, criteria[criterion], sample.sample_criteria[criterion]] )
                        # print(sample_info[criterion.value].iloc[0])
                        booleans.append(self.get_bool_and(criteria[criterion], sample_info[criterion.value]))
                        # print('booleans: ',booleans )
                    if selection == 'or':
                        booleans.append(self.get_bool_or(criteria[criterion], sample_info[criterion.value]))

            if selection == 'and':
                if all(booleans):
                    selected_sps.append(sample)
            if selection == 'or':
                if any(booleans):
                    selected_sps.append(sample)

        if len(selected_sps) > 0:
            return selected_sps

        return None

    def exclude_from_list(self, criteria, sample_ids):
        selected_sps = []
        for sample in sample_ids:
            sample_info = self.getInfo_as_df_for_sample(sample)

            booleans = []
            for criterion in criteria.keys():
                booleans.append(self.get_bool_for_exclusion(criteria[criterion], sample_info[criterion.value]))

            if not any(booleans):
                selected_sps.append(sample)

        if len(selected_sps) > 0:
            return selected_sps
        return None

    def get_samples_by_subject_ids(self, subject_ids, samples):
         criteria = SampleCriteriaParameters([(SampleCriteriaCategories.subject_id, subject_ids)])
         return self.get_from_list(criteria, samples)

    def get_samples_by_data_sequenced(self, data_sequenced, samples):
         criteria = SampleCriteriaParameters([(SampleCriteriaCategories.data_sequenced, data_sequenced)])
         return self.get_from_list(criteria, samples)

    def get_samples_by_ids(self, sample_ids):
         criteria = SampleCriteriaParameters([(SampleCriteriaCategories.sequencing_ID, sample_ids)])
         return self.get_from_list(criteria)

    def get_samples_by_traits(self, traits, samples, selection):
         criteria = SampleCriteriaParameters([(SampleCriteriaCategories.trait, traits)])
         return self.get_from_list(criteria, samples, selection)

    def get_samples_by_experiment_types(self, experiment_types, samples):
        criteria = SampleCriteriaParameters([(SampleCriteriaCategories.experiment_type, experiment_types)])
        return self.get_from_list(criteria, samples)

    def exclude_on_experiment_types(self, experiment_types=[], samples=[]):
        return self.exclude_from_list(SampleCriteriaParameters([(SampleCriteriaCategories.experiment_type, experiment_types)]), samples)

    def get_samples_by_peptide_sequence(self, peptide_sequence, samples):
        criteria = SampleCriteriaParameters([(SampleCriteriaCategories.peptide_sequence, peptide_sequence)])
        return self.get_from_list(criteria, samples)

    def get_samples_by_cell_type(self, cell_types, samples):
        criteria = SampleCriteriaParameters([(SampleCriteriaCategories.cell_type, cell_types)])
        return self.get_from_list(criteria, samples)


    def get_samples_by_sequencing_level(self, sequencing_level, samples):
        criteria = SampleCriteriaParameters([(SampleCriteriaCategories.sequencing_level, sequencing_level)])
        return self.get_from_list(criteria, samples)

    def get_samples_by_total_cell_count_before_culture(self, total_cell_count_before_culture, samples):
        criteria = SampleCriteriaParameters([(SampleCriteriaCategories.total_cell_count_before_culture, total_cell_count_before_culture)])
        return self.get_from_list(criteria, samples)

    def get_samples_by_repeat_ID(self, repeat_ID, samples):
        criteria = SampleCriteriaParameters([(SampleCriteriaCategories.repeat_ID, repeat_ID)])
        return self.get_from_list(criteria, samples)

    def select(self, parameters):

        # print("info_df: ", self.info_df)
        # print("self.sequencing_ID: ", self.sequencing_ID)
        # print("copy(self.sequencing_ID): ", copy(self.sequencing_ID))

        samples = copy(self.sequencing_ID)

        # print("samples-1:",samples)
        if 'subject_ids' in parameters.keys():
            samples = self.get_samples_by_subject_ids(parameters['subject_ids'], samples)
        # print("samples-2:", samples)
        if 'traits' in parameters.keys():
            samples = self.get_samples_by_traits(parameters['traits'], samples, selection="or")
        # print("samples-3:",samples)

        if 'data_sequenced' in parameters.keys():
            samples = self.get_samples_by_data_sequenced(parameters['data_sequenced'], samples)
        if 'peptide_sequence' in parameters.keys():
            samples = self.get_samples_by_peptide_sequence(parameters['peptide_sequence'], samples)
        if 'sequencing_level' in parameters.keys():
            samples = self.get_samples_by_sequencing_level(parameters['sequencing_level'], samples)
        if 'total_cell_count_before_culture' in parameters.keys():
            samples = self.get_samples_by_total_cell_count_before_culture(parameters['total_cell_count_before_culture'], samples)
        if 'repeat_ID' in parameters.keys():
            samples = self.get_samples_by_repeat_ID(parameters['repeat_ID'], samples)
        if 'experiment' in parameters.keys():
            samples = self.get_samples_by_experiment_types(parameters['experiment'], samples)

        if 'experiment_type_excluded' in parameters.keys():
            experiment_type_excluded = parameters['experiment_type_excluded']
            for to_exclude in experiment_type_excluded:
                samples = self.exclude_on_experiment_types([to_exclude], samples)

        return samples

class ComparisonDataSet:
    def __init__(self, df, clonotype_samples_info_file, input_file_format=None): #
        if input_file_format == 'RAW':
            # sample_info_df, sequence_info_df = self.get_sample_and_sequence_info_df(df)
            self.samples_info_file = ClonotypeSamplesInfoFile(clonotype_samples_info_file)
            self.data_source = ClonotypeSequencesInfoFile(self, df)
            self.samples = ClonotypeSamples(comparisonDataSet=self)

        else:
            # sample_info_df, sequence_info_df = self.get_sample_and_sequence_info_df(df)
            sequence_info_df = self.get_sample_and_sequence_info_df(df)
            # print(sequence_info_df)
            self.samples_info_file = ClonotypeSamplesInfoFile(clonotype_samples_info_file)
            self.data_source = ClonotypeSequencesInfoFile(self, sequence_info_df)
            # print("self.data_source", self.data_source)
            self.samples = ClonotypeSamples(comparisonDataSet=self)

    def get_sample_and_sequence_info_df(self, df):
        # print('test: ', df)

        first_col = df[df.columns.values[0]]
        start=None
        for cell_index in range(len(first_col)):
            if match(".*aminoAcid.*|.*nucleotide.*", str(first_col.iloc[cell_index])):
                start=cell_index
                break

        # s = df.iloc[0]
        # print('s: ', s)
        # sp_info_index = s.tolist().index('file name')
        # sample_info = df.ix[0:(start-1), sp_info_index+1:]
        # sample_info.index = df.ix[0:(start-1),sp_info_index].values
        # sequence_info = df.ix[(start+1):, ]
        # sequence_info.columns = df.ix[start, ].values
        # return sample_info.T.drop_duplicates(), sequence_info

        if start is None:
            sequence_info = df
        else:
            sequence_info = df.ix[(start+1):, ]
            sequence_info.columns = df.ix[start, ].values

        # print('sequence_info.columns: ', sequence_info.columns)
        # print('sequence_info: ', sequence_info)

        return  sequence_info


class ComparisonDataFrameFactory:
    def __init__(self, input_path=None, input_file_format='RAW', selected_list_of_files=None):
        self.selected_list_of_files = selected_list_of_files
        self.input_file_format=input_file_format
        self.input_path = input_path

    def get_column_index_for(self, data, name):
        for i in range(len(data.columns.values)):
             if search(name, data.columns.values[i]):
                 return i
        return None

    def get_df_elt(self, files, column_name, sequence_status='In'):
        print("--- Merging estimated number of genome dataframe ---")
        init = True
        #total_counts = ["total_clonotypes_counts"]
        for f in files:
             data = read_csv(f, sep='\t')
             data = data.iloc[where(data['sequenceStatus'] == sequence_status)[0]]

             #print data
             filename = path.basename(f)



             i = self.get_column_index_for(data,'count')
             #print data.columns.values[i]
             count_colname = data.columns.values[i]

             if column_name == 'count':
                 col = data[count_colname]
             else:
                 col = data[column_name]

             if column_name == "frequencyCount (%)":
                 col = col.astype(float) / 100

             if init:
                 filename_split = column_name + "_" + path.splitext(filename)[0]
                 clonotypes = {"nucleotide": data['nucleotide'], filename_split: col}
                 clonotypes = DataFrame(clonotypes, columns=["nucleotide", filename_split])
                 init=False
             else:
                 filename_split = column_name + "_" + path.splitext(filename)[0]
                 clonotypes_to_add = {"nucleotide": data['nucleotide'], filename_split: col}
                 clonotypes_to_add = DataFrame(clonotypes_to_add, columns=["nucleotide", filename_split])

                 print(["source: ", sizeof_fmt(getsizeof(clonotypes))] ,[filename, sizeof_fmt(getsizeof(clonotypes_to_add))])

                 clonotypes = merge(clonotypes, clonotypes_to_add, on="nucleotide", how="outer")
        return clonotypes

    # @profile
    def get_df_general_info(self, files, sequence_status='In'):
        print("--- Building general info dataframe ---")

        clonotypes_df = None

        for f in files:
            filename = path.basename(f)
            data = read_csv(f, sep='\t')
            data = data.iloc[where(data['sequenceStatus'] == sequence_status)[0]]

            collect()

            # for i in range(len(data.columns.values)):
            #      if search('count', data.columns.values[i]):
            #          break

            print([filename, data.shape])
            # for index in data.index:
            #     #print 'index: ' + str(index)
            #     nucleotide = data["nucleotide"].ix[index]
            #
            #     clonotype_dict[nucleotide] = concat([data.loc[index][0:2], data.loc[index][4:37],
            #                                             data.loc[index][38:len(data.columns.values)]], axis=0).astype(str)

            if clonotypes_df is not None:
                nt_new_indexes = setdiff1d(list(data["nucleotide"]), clonotypes_df.index.values)
                # print('nt_new_indexes: ', nt_new_indexes[1:10])

                indexes = []
                for nt in nt_new_indexes:
                    indexes.append(list(data["nucleotide"]).index(nt))

                if len(indexes) > 0:
                    data = data.iloc[indexes]
                    nt_indexes = data["nucleotide"]
                    df = concat([data.iloc[:, 0:2], data.iloc[:, 4:37], data.iloc[:, 38:len(data.columns.values)]], axis=1).astype(str)
                    df.index = list(nt_indexes)
                    clonotypes_df = concat([clonotypes_df, df], axis=0, copy=False)
            else:
                nt_indexes = data["nucleotide"]
                clonotypes_df = concat([data.iloc[:, 0:2], data.iloc[:, 4:37], data.iloc[:, 38:len(data.columns.values)]], axis=1).astype(str)
                # print(clonotypes_df)
                # print(list(nt_indexes)[0:10])
                # print(str(clonotypes_df.index))
                # print(str(len(clonotypes_df.index)))
                clonotypes_df.index = list(nt_indexes)

            # collect()

        # clonotypes_df = DataFrame(clonotype_dict, columns=clonotype_dict.keys())

        # collect()

        # clonotypes_df = clonotypes_df.transpose(copy=False)

        return clonotypes_df

    def check_existing_file_name(self, sample_infos_path, file_names):
        sample_infos = read_csv(sample_infos_path)
        sample_infos = sample_infos.dropna()

        l = list(set(sample_infos["file name"]))

        print(l)

        my_file_names = [path.basename(file) for file in file_names]

        print(my_file_names)

        selected_sp = intersect1d(my_file_names, l)

        mydir = path.dirname(file_names[0])

        present_sp = []
        for sp in selected_sp:
            present_sp.append(mydir + "/" + sp)

        return setdiff1d(my_file_names, l), present_sp

#    @profile
    def merge(self):
        print('--- Merging Adaptive Biotechnologies files & keep only in-frame clonotypes ---')
        adaptive_files = glob(self.input_path + '*.tsv')

        mylist, adaptive_files = self.check_existing_file_name(self.input_path + 'metadata/sample_info.csv', adaptive_files)

        if len(mylist) > 0:
            logging.info("Samples not in sample info file and that will not be taken in account for the rest of the analysis: " + str(mylist))

        if AdaptiveBiotechFileColumn.check_format(adaptive_files) == 'FAILURE':
            raise  ValueError('At least one of the input data files does not have the right format.')

        # print(adaptive_files)
        # selected_adaptive_files = []
        # if self.selected_list_of_files is not None:
        #     print(self.selected_list_of_files)
        #     for filename in self.selected_list_of_files:
        #         for adaptive_filename in adaptive_files:
        #             if search(filename + '.tsv', adaptive_filename.lower()):
        #                 selected_adaptive_files.append(adaptive_filename)
        #                 break
        #     adaptive_files = selected_adaptive_files

        print('adaptive_files: ', adaptive_files)

        donor_df = None

        if len(adaptive_files) > 0:
            if len(adaptive_files) > 1:
                list_of_df = []

                df_estimated_genomes = self.get_df_elt(adaptive_files, "estimatedNumberGenomes", sequence_status='In')

                # df_vGeneName = self.get_df_elt(adaptive_files, "vGeneName", sequence_status='In')
                # df_dGeneName = self.get_df_elt(adaptive_files, "dGeneName", sequence_status='In')
                # df_jGeneName = self.get_df_elt(adaptive_files, "jGeneName", sequence_status='In')

                df_estimated_genomes = df_estimated_genomes.fillna(0)
                # df_vGeneName = df_vGeneName.fillna(0)
                # df_dGeneName = df_dGeneName.fillna(0)
                # df_jGeneName = df_jGeneName.fillna(0)

                df_general_info = self.get_df_general_info(adaptive_files, sequence_status='In')

                collect()

                print('[estimated_genomes, general_info]: ', [sizeof_fmt(getsizeof(df_estimated_genomes)), sizeof_fmt(getsizeof(df_general_info))])
                print('total= ', sizeof_fmt(getsizeof(df_estimated_genomes) + getsizeof(df_general_info)))

                # print('df_general_info: ', df_general_info)

                df_estimated_genomes.index = df_estimated_genomes["nucleotide"]
                # df_general_info.index = df_general_info["nucleotide"]

                # print('garbage: ', garbage[:])

                # df_vGeneName.index = df_vGeneName["nucleotide"]
                # donor_df = merge(df_estimated_genomes, df_vGeneName, on="nucleotide")
                #
                # df_dGeneName.index = df_dGeneName["nucleotide"]
                # donor_df = merge(donor_df, df_dGeneName, on="nucleotide")
                #
                # df_jGeneName.index = df_jGeneName["nucleotide"]
                # donor_df = merge(donor_df, df_jGeneName, on="nucleotide")

                donor_df = merge(df_estimated_genomes, df_general_info, on="nucleotide")

                # donor_df = concat([df_estimated_genomes, df_general_info], axis=1)
                # print('donor_df: ', donor_df)

                list_of_df.append(donor_df)

                collect()
                donor_df = concat(list_of_df, ignore_index=False, keys=['nucleotide'])
                collect()
                donor_df.reset_index(drop=True, inplace=True)
                collect()

                # print('donor_df index reseted: ', donor_df)

                print('donor df size: ', sizeof_fmt(getsizeof(donor_df)))

            elif len(adaptive_files) == 0:
                print( 'ERROR: no files with tsv extension were found!')
            elif len(adaptive_files) == 1:
                print('ERROR: 1 file with tsv extension was found, need at least 2 for merging!')
        elif self.selected_list_of_files is not None:
            print('WARN: no adaptive files found in ' + str(self.selected_list_of_files))
        else:
            print('WARN: no adaptive files found in ' + self.input_path)
        return donor_df

class RepeatsList(list):
    def __init__(self, list_of_repeats=None, repeats=None, control_merge=True):
        if repeats is not None:
            self.append(repeats)
        if list_of_repeats is not None:
            self.extend(list_of_repeats)
            # if control_merge:
            #     self.control_and_merge_corresponding_repeats()

class SampleCriteriaCategories(Enum):
    sequencing_ID = 'sequencing ID'
    # mapped_ID = 'mapped ID'
    trait = 'trait'
    subject_id = 'subject id'
    # analysis_software = 'analysis software'
    time_point = 'time point'
    cell_type = 'cell type'
    # peptide = 'peptide'
    experiment_type = 'experiment'
    repeat_ID = 'repeat'
    # repeat_type = 'repeat type'
    # sequencing_company = 'sequencing company'
    # run = 'run'
    # num_T_cells_before_culture = 'T cells count before culture'
    # num_T_cells_after_culture = 'T cells count after culture'
    total_cell_count_before_culture = 'total cell count before culture'
    data_sequenced = 'data sequenced'
    peptide_sequence = 'peptide sequence'

    @staticmethod
    def get_common_culture_repeats_criteria():
        return [SampleCriteriaCategories.subject_id, SampleCriteriaCategories.experiment_type,
                SampleCriteriaCategories.peptide_sequence, SampleCriteriaCategories.cell_type,
                SampleCriteriaCategories.total_cell_count_before_culture,
                SampleCriteriaCategories.time_point,
                SampleCriteriaCategories.trait,
                SampleCriteriaCategories.data_sequenced]


class SampleCriteriaParameters(dict):
    def __init__(self, parameters=None):
        for criteria in SampleCriteriaCategories:
            self[criteria] = []

        if parameters is not None:
            for criteria in parameters:
                #print('criteria: ', criteria)
                self[criteria[0]] = criteria[1]

    def __str__(self):
        string = '\n'
        for k in self.keys():
            if len(self[k]) > 0:
                string = str(string + k.name + ' = ' + self[k].__repr__() + '\n')
        return string

    def __repr__(self):
        return self.__str__()

    def get_parameter_values(self):
        list_of_list = []
        for criterion in self.keys():
            list_of_list.append(self[criterion])
        return list(concatenate(list_of_list))

    def keep_common_repeat_criteria(self):
        list_of_criteria = SampleCriteriaCategories.get_common_culture_repeats_criteria()
        list_criteria_to_remove=[]
        for criterion in self.keys():
            if criterion not in list_of_criteria:
                list_criteria_to_remove.append(criterion)
        for criterion in list_criteria_to_remove:
            del self[criterion]

    def get_differing_criteria(self, criteria):
        diff_criteria = SampleCriteriaParameters()
        for criterion in self.keys():
            for value in criteria[criterion]:
                if value not in self[criterion]:
                    diff_criteria[criterion].append(value)
        return diff_criteria


class Clonotypes(object):
    #samples = list of samples
    def __init__(self, clonotype_index=None, sample=None, ID='', samples=None):
        self.clonotype_index = []
        self.phenotypes = []



        if samples is not None:
            if clonotype_index is not None:
                self.clonotype_index = list(clonotype_index)
            else:
                indexes = []
                for sample in samples:
                    indexes.append(sample.clonotype_index)
                self.clonotype_index = list(set(concatenate(indexes)))

            self.source = ClonotypeSamples(samples=samples)
            self.data_source_df = samples[0].data_source_df
            self.ID = ID

        elif sample is not None:
            self.phenotypes = []
            self.clonotype_index = list(sample.clonotype_index)
            self.source = ClonotypeSamples(samples=[sample])
            self.data_source_df = sample.data_source_df
            self.ID = ID
        else:
            self.phenotypes = []
            self.clonotype_index = list(clonotype_index)
            self.ID = ID
            self.source = ClonotypeSamples()
            self.data_source_df = DataFrame()

    def __str__(self):
        return str([self.ID, str(len(self.clonotype_index))])

    def __repr__(self):
        return self.__str__()

    def get_shared_clonotypes_index(self, clonotypes):
        return intersect1d(self.clonotype_index, clonotypes.clonotype_index)

    @staticmethod
    def merge_aa(clonotypes1, clonotypes2):
        if isinstance(clonotypes1, NucleotideClonotypes) & isinstance(clonotypes2, NucleotideClonotypes):
            merged_clonotype_index = list(set(concatenate([clonotypes1.clonotype_index, clonotypes2.clonotype_index])))
        else:
            merged_clonotype_index = list(set(concatenate([clonotypes1.nt_clonotype_index, clonotypes2.nt_clonotype_index])))
        merged_ID = clonotypes1.ID + ':' + clonotypes2.ID
        merged_samples = list(set(concatenate([clonotypes1.source, clonotypes2.source])))
        return AminoAcidClonotypes(nt_clonotype_index=merged_clonotype_index, ID=merged_ID, samples=merged_samples)

    @staticmethod
    def shared_clonotypes(clonotypes1, clonotypes2):
        return NucleotideClonotypes(clonotypes1.get_shared_clonotypes_index(clonotypes2),
                   ID=clonotypes1.ID + ':' + clonotypes2.ID,
                   samples=list(set(concatenate([clonotypes1.source, clonotypes2.source]))))

    def get_cell_frequencies_by_sample_source(self, clonotype_index=None):
        sample_cell_frequencies_dict = {}
        for sample in self.source:
            if clonotype_index is not None:
                sample_cell_frequencies_dict[sample.ID] = sample.get_cell_counts_frequencies_by_clonotype_index(clonotype_index=clonotype_index)
            else:
                sample_cell_frequencies_dict[sample.ID] = sample.get_cell_counts_frequencies_by_clonotype_index()

        return sample_cell_frequencies_dict

    def get_pvalues_df(self):
        return self.source.get_pvalues_df_by_clonotype_index(self.clonotype_index)

    def get_aa_clonotypes_from_nt_clonotypes(self):
        return AminoAcidClonotypes(nt_clonotype_index=self.clonotype_index, samples=list(self.source), ID=self.ID)

    def filter_allele_from_gene_name(self, df):
        cols = [AdaptiveBiotechFileColumn.aminoAcid.value[0], AdaptiveBiotechFileColumn.vMaxResolved.value[0], \
                AdaptiveBiotechFileColumn.jMaxResolved.value[0]]
        # print("filter_allele_from_gene_name: ", df)
        temp_df = concat([DataFrame([df[col].str.split("*", expand=True)[0] for col in cols]).T, df[df.columns.values[3:]]], axis=1)
        temp_df.columns=df.columns.values
        temp_df.index=df.index.values
        return temp_df

    def get_df_col_approx(self, df, motif):
        colnames = []
        motif = motif.replace('+', '\+')
        motif = motif.replace('-', '\-')

        # print(motif)

        for i in range(len(df.columns.values)):
            # print(df.columns.values[i].lower())
            # print(type(df.columns.values[i].lower()))
            # print(motif.lower())
            # print(type(motif.lower()))
            # print(match(motif.lower(), df.columns.values[i].lower()))

            if match(motif.lower(), df.columns.values[i].lower()):
                colnames.append(df.columns.values[i])

        # print("mycol: ", colnames)

        init = True
        cols = []
        for colname in colnames:
            if init:
                cols = df[colname]
                init = False
            else:
                col = df[colname]
                cols = concat([cols, col], axis=1)
        return cols

    def get_aa_seq_with_gene_names(self, clonotype_index=None, ID=None):
        cols = [AdaptiveBiotechFileColumn.aminoAcid.value[0], AdaptiveBiotechFileColumn.vMaxResolved.value[0], \
         AdaptiveBiotechFileColumn.jMaxResolved.value[0]]

        # print("test: ", self.data_source_df[cols])
        # print("test: ", clonotype_index)

        # print("get_aa_seq_with_gene_names: ", self.data_source_df)
        # print("cols: ", cols)
        # print("clonotype_index: ", self.clonotype_index)

        if clonotype_index is not None:
            s = self.data_source_df[cols].ix[clonotype_index]
        else:
            s = self.data_source_df[cols].ix[self.clonotype_index]

        # print()
        #
        # if ID is not None:
        #     s = self.get_df_col_approx(s, ID)
        #
        # print("get_aa_seq_with_gene_names: ", s)
        #
        # s = self.filter_allele_from_gene_name(s)
        #
        # # s = s.rename('aminoAcid')
        # # print("test: ", s)
        #
        # print("ID: ",ID)
        # print(s)

        return s

    def get_aa_cell_counts_processed_data(self, clonotype_index=None, ID=None):

        if clonotype_index is None:
            clonotype_index = self.clonotype_index

        if ID is None:
            ID = self.ID

        # print("data_source_df.columns.values: ", self.data_source_df.columns.values)
        print("ID: ", ID)

        start=True

        for sample in self.source:
            id = sample.ID
            if start:
                s2_temp = self.get_df_col_approx(self.data_source_df, id + "_cell_count")

                print(s2_temp)
                print(id + "_cell_count")

                if isinstance(s2_temp, Series):
                    s2_temp = s2_temp.rename(id + "_cell_count")
                elif isinstance(s2_temp, DataFrame):
                    s2_temp.columns = [id + "_cell_count"]

                s2= s2_temp.ix[clonotype_index]
                # print("s2_temp: ", s2_temp)
                start=False
            else:
                s2_temp = self.get_df_col_approx(self.data_source_df, id + "_cell_count")
                if isinstance(s2_temp, Series):
                    s2_temp = s2_temp.rename(id + "_cell_count")
                elif isinstance(s2_temp, DataFrame):
                    s2_temp.columns = [id + "_cell_count"]

                s2 = concat([s2, s2_temp], axis=1)

        # print("s2: ", s2)

        return s2

    def get_aa_seq_with_gene_names_cell_counts(self, clonotype_index=None, ID=None):
        cols = [AdaptiveBiotechFileColumn.aminoAcid.value[0], AdaptiveBiotechFileColumn.vMaxResolved.value[0], \
                AdaptiveBiotechFileColumn.jMaxResolved.value[0]]

        if clonotype_index is None:
            clonotype_index = self.clonotype_index

        s1 = self.data_source_df[cols].ix[clonotype_index]

        # print("s1: ",s1)

        if ID is None:
            ID = self.ID

        # print("ID: ", ID)

        start = True
        for sample in self.source:
            id = sample.ID
            if start:
                print(id)
                s2_temp = self.get_df_col_approx(self.data_source_df, ".*" + id + "$|^" + id + ".*")

                # print('s2_temp: ', s2_temp)

                if isinstance(s2_temp, Series):
                    s2_temp = s2_temp.rename(id + "_cell_count")
                elif isinstance(s2_temp, DataFrame):
                    s2_temp.columns = [id + "_cell_count"]

                s2 = s2_temp.ix[clonotype_index]

                start = False
            else:
                s2_temp = self.get_df_col_approx(self.data_source_df,  ".*" + id + "$|^" + id + ".*")
                if isinstance(s2_temp, Series):
                    s2_temp = s2_temp.rename(id + "_cell_count")
                elif isinstance(s2_temp, DataFrame):
                    s2_temp.columns = [id + "_cell_count"]

                # print()

                s2 = concat([s2, s2_temp], axis=1)

        s =concat([s1, s2],axis=1)
        s = self.filter_allele_from_gene_name(s)

        return s

    def get_amino_acid_sequences(self, clonotype_index=None):
        if clonotype_index is None:
            s = self.data_source_df[AdaptiveBiotechFileColumn.aminoAcid.value[0]][self.clonotype_index]
        else:
            s = self.data_source_df[AdaptiveBiotechFileColumn.aminoAcid.value[0]][clonotype_index]
        s = s.rename('aminoAcid')
        return s

    def get_cell_count_by_clonotype_df(self):
        return self.source.get_cell_counts_df(self.clonotype_index)

    #return dictionnaries of series
    def get_cell_counts_by_sample_source(self, clonotype_index=None):
        if clonotype_index is None:
            clonotype_index = self.clonotype_index

        sample_cell_count_dict = {}
        for sample in self.source:
            sample_cell_count_dict[sample.ID] = sample.get_cell_counts_clonotype_index(clonotype_index)

        return sample_cell_count_dict

    def get_cell_counts_grouping_by_clonotype_ids_by_sample_source(self, clonotype_index=None):
        if clonotype_index is None:
            clonotype_index = self.clonotype_index

        sample_cell_count_dict = {}
        for sample in self.source:
            sample_cell_count_dict[sample.ID] = sample.get_cell_counts_grouping_by_clonotype_ids(clonotype_index)

        return sample_cell_count_dict

class AminoAcidClonotypes(Clonotypes):
    def __init__(self, nt_clonotype_index=None, aa_clonotype_ids=None, clonotype_index=None, samples=None, ID='', clonotype_level="aacdr3"):
        super(AminoAcidClonotypes, self).__init__(samples=samples, ID=ID, clonotype_index=clonotype_index)
        self.nt_clonotype_index = None
        if self.source.is_nt_clonotypes():

            # if nt_clonotype_index is not None:
            #     # print('nt_clonotype_index : ', nt_clonotype_index)
            #     self.nt_to_aa_clonotypes_dict = self.associate_nt_to_aa_clonotypes(nt_clonotype_index=nt_clonotype_index)
            # else:
            #     # print('aa_clonotype_ids : ', aa_clonotype_ids)
            #     self.nt_to_aa_clonotypes_dict = self.associate_nt_to_aa_clonotypes(aa_clonotype_ids=aa_clonotype_ids)
            # self.nt_clonotype_index = concatenate(self.nt_to_aa_clonotypes_dict.values())
            # self.aa_clonotype_ids = self.nt_to_aa_clonotypes_dict.keys()

            self.aa_clonotype_ids_nt_convergence = self.get_convergence_per_aa_clonotype_ids_df_from(nt_clonotype_index)

            self.nt_clonotype_index = nt_clonotype_index
            self.aa_clonotype_ids_cell_counts_df = self.get_aa_clonotype_ids_cell_counts_df_from(nt_clonotype_index, self.ID, clonotype_level)

            # print("aa_clonotype_ids_cell_counts_df: ", self.aa_clonotype_ids_cell_counts_df)

            self.aa_clonotype_ids = self.aa_clonotype_ids_cell_counts_df.index.values

        else:
            # print(aa_clonotype_ids)
            if isinstance(aa_clonotype_ids, DataFrame) | isinstance(aa_clonotype_ids, Series):
                self.clonotype_index = aa_clonotype_ids.index.values
                self.aa_clonotype_ids = aa_clonotype_ids
                self.aa_clonotype_ids_cell_counts_df = self.get_aa_cell_counts_processed_data(self.clonotype_index, self.ID)
            elif clonotype_index is not None:
                # print("self.clonotype_index: ",self.clonotype_index)
                self.clonotype_index = clonotype_index
                self.aa_clonotype_ids = self.get_df_col_approx(self.data_source_df, "aminoAcid").ix[clonotype_index]
                self.aa_clonotype_ids_cell_counts_df = self.get_aa_cell_counts_processed_data(self.clonotype_index, self.ID)
            else:
                raise Exception('ERROR: amino acid sequence ids for aa clonotypes should be DataFrame or Series')
                # print("AminoAcidClonotypes:", aa_clonotype_ids)
                # self.aa_clonotype_ids = aa_clonotype_ids
                # self.aa_clonotype_ids_cell_counts_df = self.get_aa_cell_counts_processed_data( self.aa_clonotype_ids, self.ID)
            # self.clonotype_ids = aa_clonotype_ids.index.values
            # self.clonotype_ids = aa_clonotype_ids.index.values
        # print(self.aa_clonotype_ids)

    def __str__(self):
        if self.nt_clonotype_index is not None:
            return str([self.ID, ['aa', str(len(self.aa_clonotype_ids))], ['nt', str(len(self.nt_clonotype_index))]])
        return str([self.ID, ['aa', str(len(self.aa_clonotype_ids))]])

    def __repr__(self):
        return self.__str__()

    # def get_cell_frequencies_by_aa_clonotype_ids(self, aa_clonotype_ids):
    #     df = self.get_frequencies()
    #     df = df.ix[aa_clonotype_ids]
    #     return df.fillna(0)

    def get_cell_frequencies_by_aa_clonotype_index(self, clonotype_index):
        df = self.get_frequencies()
        # print(df)
        # print(clonotype_index)
        df = df.ix[clonotype_index]
        # print("df: ", df)
        return df.fillna(0)

    def get_total_cell_counts(self):
        return self.get_cell_counts().sum()

    def get_frequencies(self):
        # clonotypes_cell_count_dictionary = super(AminoAcidClonotypes, self).get_cell_frequencies_by_sample_source()
        clonotypes_cell_count_df = self.get_cell_counts()
        total = self.get_total_cell_counts()
        # clonotypes_cell_count_df = DataFrame(clonotypes_cell_count_dictionary)

        # if self.nt_clonotype_index is not None:
        #     df = self.get_associated_nt_aa_clonotype_ids_df(self.nt_clonotype_index)
        #     df = concat([clonotypes_cell_count_df, df], axis=1)
        #     return df.groupby(['aminoAcid']).sum().divide(self.get_)

        # print('nt_clonotypes_cell_count_df: ',  nt_clonotypes_cell_count_df)
        # print('aa_clonotype_ids: ',  self.aa_clonotype_ids)

        # nt_clonotypes_cell_count_df.index = self.aa_clonotype_ids

        return clonotypes_cell_count_df.divide(total)

    def get_shared_clonotypes_index(self, clonotypes):
        return intersect1d(self.clonotype_index, clonotypes.clonotype_index)

    def get_shared_clonotypes_ids(self, clonotypes):
        return intersect1d(self.aa_clonotype_ids, clonotypes.aa_clonotype_ids)

    @staticmethod
    def shared_clonotypes(clonotypes1, clonotypes2):
        return AminoAcidClonotypes(clonotype_index=clonotypes1.get_shared_clonotypes_index(clonotypes2),
                   ID=clonotypes1.ID + ':' + clonotypes2.ID,
                   samples=list(set(concatenate([clonotypes1.source, clonotypes2.source]))))

    def get_associated_nt_clonotype_counts(self):
        mydict = {}
        for k in self.nt_to_aa_clonotypes_dict.keys():
            mydict[k] = len(self.nt_to_aa_clonotypes_dict[k])
        return mydict

    def get_associated_nt_clonotype_counts_df(self):
        return DataFrame(dict(self.get_associated_nt_clonotype_counts()), index=['# nucleotide sequences with that CDR3']).T


    # Define a clonotype at the amino acid level or gene + CDR3 level
    def get_convergence_per_aa_clonotype_ids_df_from(self, nt_clonotype_index=None, clonotype_level=None):
        aaseqs = self.get_aa_seq_with_gene_names(nt_clonotype_index)

        aaseqs = self.filter_allele_from_gene_name(aaseqs)

        aaseqs = concat([aaseqs, DataFrame([1] * aaseqs.shape[0], index=aaseqs.index.values, columns=['# nucleotide sequences with that CDR3'])], axis=1)

        if clonotype_level is not None:
            if clonotype_level == "genes+aacdr3":
                gp = aaseqs.groupby(['vMaxResolved', 'aminoAcid', 'jMaxResolved'])
                mylist = [('_'.join([key[0], key[1], key[2]]), sum(df['# nucleotide sequences with that CDR3'])) for key, df in gp]
            else:
                raise Exception("clonotype level not supported: " + clonotype_level)
        else:
            gp = aaseqs.groupby([ 'aminoAcid'])
            mylist = [(key, sum(df['# nucleotide sequences with that CDR3'])) for key, df in gp]

        # gp = aaseqs.groupby(['aminoAcid'])

        # print("get_convergence_per_aa_clonotype_ids_df_from: ", gp.head())

        # for key, df in gp:
        #     print(key, sum(df['# nucleotide sequences with that CDR3']))



        # mylist = [(key[0], sum(df['# nucleotide sequences with that CDR3'])) for key, df in gp]

        # for test in gp:
        #     print(test)
        #     key, convergence = test
        #     print("key: ", key)
        #     print("convergence: ", convergence["# nucleotide sequences with that CDR3"])

        mydict = dict(mylist)
        df = DataFrame(mydict, index=["# nucleotide sequences with that CDR3"]).T

        # print("get_convergence_per_aa_clonotype_ids_df_from", df)

        return df

    def get_aa_clonotype_ids_by_clonotype_index(self, clonotype_index):
        return self.aa_clonotype_ids.ix[clonotype_index]


    #Define the clonotype (left column of the complete merged clonotypes).
    def get_aa_clonotype_ids_cell_counts_df_from(self, nt_clonotype_index=None, ID=None, clonotype_level=None):

        aaseqs = self.get_aa_seq_with_gene_names_cell_counts(nt_clonotype_index, ID)

        if (clonotype_level is None) or (clonotype_level == "aacdr3"):
            gp = aaseqs.groupby(['aminoAcid'])
            gp_sum_df = gp.sum()
            gp_sum_df.index = gp_sum_df.index.values
        elif clonotype_level == "genes+aacdr3":
            gp = aaseqs.groupby(['vMaxResolved', 'aminoAcid', 'jMaxResolved'])
            gp_sum_df = gp.sum()
            gp_sum_df.index = ['_'.join([str(key[0]), str(key[1]), str(key[2])]) for key in gp_sum_df.index.values]
        else:
            raise Exception("clonotype level not supported: " + clonotype_level)

        # Define the clonotype at the gene + CDR3 level
        # gp = aaseqs.groupby([ 'vMaxResolved', 'aminoAcid', 'jMaxResolved'])
        # gp_sum_df = gp.sum()
        # gp_sum_df.index = ['_'.join([str(key[0]), str(key[1]), str(key[2])]) for key in gp_sum_df.index.values]

        return gp_sum_df

    # Define the clonotype (left column of the complete merged clonotypes).
    def get_aa_clonotype_ids_df_from(self, nt_clonotype_index=None, ID=None):

        aaseqs = self.get_aa_seq_with_gene_names(nt_clonotype_index)

        aaseqs = concat([aaseqs, DataFrame([1] * aaseqs.shape[0], index=aaseqs.index.values)], axis=1)

        # gp = aaseqs.groupby(['vMaxResolved', 'aminoAcid', 'jMaxResolved'])
        # mylist = [('_'.join([str(key[0]), str(key[1]), str(key[2])]), sum(df.index.values)) for key, df in gp]

        gp = aaseqs.groupby(['aminoAcid'])
        # for key, df in gp:
        #     print((key, sum(df.index.values)))


        mylist = [(key, sum(df.index.values)) for key, df in gp]
        mydict = dict(mylist)
        print("-- test mydict --")

        # for k in mydict.keys():
        #     if len(mydict[k]) != 1:
        #         print(mydict[k])
        # print(mydict)

        print("test get_aa_clonotype_ids_df_from: ", )
        print(DataFrame(mydict, index=["cell_counts"]).T)
        return DataFrame(mydict, index=["cell_counts"]).T

    def associate_nt_to_aa_clonotypes(self, nt_clonotype_index=None, aa_clonotype_ids=None):
        if aa_clonotype_ids is not None:
            aaseqs = aa_clonotype_ids
            if (not isinstance(DataFrame)) | (not isinstance(Series)):
                raise
        # else:
        #     # print('nt_clonotype_index: ', nt_clonotype_index)
        #     # aaseqs = self.get_amino_acid_sequences(nt_clonotype_index)
        #     aaseqs = self.get_aa_seq_with_gene_names(nt_clonotype_index)
        #     # print('aaseqs: ', aaseqs)
        #     # aaseqs = DataFrame(aaseqs)
        #     aaseqs = concat([aaseqs, DataFrame([1] * aaseqs.shape[0], index=aaseqs.index.values)], axis=1)
        #     aaseqs.columns = ['aminoAcid','vMaxResolved','jMaxResolved', "counts"]
        #
        # # column_names = aaseqs.columns.values
        # # print(column_names)
        # # gp = aaseqs.groupby(column_names)
        # gp = aaseqs.groupby(['aminoAcid','vMaxResolved','jMaxResolved'])
        #
        # # print("test grouping: ", gp.sum())
        #
        # mylist = [('_'.join([str(key[0]), str(key[1]), str(key[2])] ), df.index.values) for key, df in gp]
        # mydict = dict(mylist)
        # print("test: ", mydict)
        # return mydict
        return self.get_aa_clonotype_ids_df_from(nt_clonotype_index)

    def get_associated_nt_aa_clonotype_ids_df(self, nt_clonotype_index=None):
        if nt_clonotype_index is None:
            return self.aa_clonotype_ids
        return self.aa_clonotype_ids.ix[nt_clonotype_index]
        #return self.source.clonotype_sequence_infget_corresponding_amino_acid_clonotype_unique_IDs_df(nt_clonotype_ids)

    def get_clonotype_index_by_aa_clonotype_ids(self, aa_clonotype_ids):
        clonotype_indexes =[]
        aa_clonotype_ids_df = DataFrame(aa_clonotype_ids)
        # print("aa_clonotype_ids: ", aa_clonotype_ids)
        # print("self.aa_clonotype_ids: ",self.aa_clonotype_ids)

        if len(aa_clonotype_ids_df.values) > 0:
            mynewdf=self.aa_clonotype_ids.to_frame()
            mynewdf["clonotype_index"]=mynewdf.index.values
            # print(mynewdf)
            # print(aa_clonotype_ids_df)
            clonotype_indexes = aa_clonotype_ids_df.merge(mynewdf,left_on=0,right_on="aminoAcid")["clonotype_index"]
            # print("clonotype_indexes: ", clonotype_indexes)
        # for aa_clonotype_id in aa_clonotype_ids:
        #     index_loc = where(self.aa_clonotype_ids == aa_clonotype_id)[0]
        #     if len(index_loc) >0:
        #         clonotype_indexes.extend(self.aa_clonotype_ids.index.values[index_loc])
        # # print("clonotype_indexes: ", clonotype_indexes)
        return clonotype_indexes

    def get_cell_counts_grouping_by_clonotype_ids(self, aa_clonotype_ids = None):
        if aa_clonotype_ids is None:
            return self.aa_clonotype_ids_cell_counts_df
            # df.columns.values[0] = self.ID + '_cell_count'

        # print("self.aa_clonotype_ids_cell_counts_df: ", self.aa_clonotype_ids_cell_counts_df)

        # print("bef: ",aa_clonotype_ids)
        clonotype_indexes = self.get_clonotype_index_by_aa_clonotype_ids(aa_clonotype_ids)

        if len(clonotype_indexes) >0:
            # print(clonotype_indexes)
            # print(type(self.aa_clonotype_ids_cell_counts_df))
            return self.aa_clonotype_ids_cell_counts_df.ix[clonotype_indexes]
        return None

    #TODO
    def get_cell_counts_by_clonotype_index(self, clonotype_index):
        return None

    def get_cell_counts(self, nt_clonotype_index=None):
        if self.source.is_nt_clonotypes():
            if nt_clonotype_index is not None:
                nt_clonotype_index = intersect1d(self.nt_clonotype_index, nt_clonotype_index)
            else:
                nt_clonotype_index = self.nt_clonotype_index

            nt_clonotypes_cell_count_dictionary = super(AminoAcidClonotypes, self).get_cell_counts_by_sample_source(nt_clonotype_index)
            nt_clonotypes_cell_count_df = DataFrame(nt_clonotypes_cell_count_dictionary)

            df = self.get_associated_nt_aa_clonotype_ids_df(nt_clonotype_index)

            df = concat([nt_clonotypes_cell_count_df, df], axis=1)
            # print(df.head())
            amino_acid_col = df.columns.values[1]
            df = df.ix[nt_clonotype_index]

            df = df.groupby([amino_acid_col]).sum()
            df.columns.values[0] = self.ID + '_cell_count'
        else:
            # print('self.aa_clonotype_ids 11: ', self.aa_clonotype_ids)

            aa_clonotypes_cell_count_dictionary = super(AminoAcidClonotypes, self).get_cell_counts_by_sample_source(self.clonotype_index)
            aa_clonotypes_cell_count_df = DataFrame(aa_clonotypes_cell_count_dictionary)

            # df = concat([aa_clonotypes_cell_count_df, self.aa_clonotype_ids], axis=1)
            # amino_acid_col = df.columns.values[1]
            #
            # df = df.groupby([amino_acid_col]).sum()
            # df.columns.values[0] = self.ID + '_cell_count'

            df = aa_clonotypes_cell_count_df

        return df

    def get_pvalues_df(self):

        if self.source.is_nt_clonotypes():
            pvalues_df = self.source.get_pvalues_df_by_clonotype_index(self.nt_clonotype_index)
            #df_to_merge = self.get_cdr3_length()
            #df = df.merge(pvalues_df, )
            if pvalues_df is not None:
                df = self.get_associated_nt_aa_clonotype_ids_df(self.nt_clonotype_index)
                df = concat([pvalues_df, df], axis=1)
                df = df.groupby(['aminoAcid']).mean()
                #df['clonotype ID']=self.ID
                #df.merge(df_to_merge, right_on='sequence', left_on='aminoAcid', how='left')
                #print('test', df)
                return df
        else:
            pvalues_df = self.source.get_pvalues_df_by_clonotype_index(self.clonotype_index)

            # print("len: ", len(self.clonotype_index))
            # print("indexes : ", self.clonotype_index)
            # print('pvalues_df self.aa_clonotype_ids: ', self.aa_clonotype_ids)
            # print('pvalues_df: ', pvalues_df)

            if pvalues_df is not None:
                return pvalues_df

        return None

    def get_pvalue_higher_equal_than(self, threshold=0.05):
        df = self.get_pvalues_df()
        index_mod = where(df >= threshold)[0]
        df = df.iloc[index_mod]
        return AminoAcidClonotypes(aa_clonotype_ids=list(df.index), ID=self.ID + '_higher_equal_pval_' + "{:.2E}".format(threshold), samples=self.source)

    def get_pvalue_lower_than(self, threshold=0.05):
        df = self.get_pvalues_df()
        #print('test1 :', df.iloc[1:10])
        df = df.iloc[where(df < threshold)[0]]
        # print('len clonotype test1: ',len(df.index))
        return AminoAcidClonotypes(clonotype_index=list(df.index), ID=self.ID + '_lower_than_pval_' + "{:.2E}".format(threshold), samples=self.source)

    def get_uniq_pvalues_by_samples_df(self):
        pvalues = []
        sample_ids = []
        for sample in self.source:
            if sample.expansion_pvalues is not None:
                sample_ids.append(sample.ID)
                pvalues.append(sample.expansion_pvalues)

        if len(pvalues) > 0:
            df = concat(pvalues, axis=1)
            df = df.ix[self.clonotype_index]
            df.columns = [sample_id + '_pval' for sample_id in sample_ids]
            return df
        else:
            print('No expansion test was applied for ' + self.ID)

        return None

    def get_nt_clonotypes(self, aa_clonotype_ids):
        my_aa_nt_clonotype_ids = []
        if aa_clonotype_ids is not None:
            for aa_clonotype_id in aa_clonotype_ids:
                if aa_clonotype_id in self.aa_clonotype_ids:
                    my_aa_nt_clonotype_ids.extend(self.nt_to_aa_clonotypes_dict[aa_clonotype_id])
        else:
            my_aa_nt_clonotype_ids = self.clonotype_ids
        return my_aa_nt_clonotype_ids

class NucleotideClonotypes(Clonotypes):
    def __init__(self, clonotype_index=None, sample=None, ID='', samples=None):
        super(NucleotideClonotypes, self).__init__(clonotype_index=clonotype_index, sample=sample, samples=samples, ID=ID)

    # def __init__(self, clonotype_index=None, sample=None, ID='', samples=None):
    # # def __init__(self, nt_clonotype_index=None, aa_clonotype_ids=None, samples=None, ID=''):
    #     super(NucleotideClonotypes, self).__init__(samples=samples, ID=ID)

    def get_shared_clonotypes_index(self, clonotypes):
        return intersect1d(self.clonotype_index, clonotypes.clonotype_ids)

    @staticmethod
    def shared_clonotypes(clonotypes1, clonotypes2):
        return NucleotideClonotypes(clonotypes1.get_shared_clonotypes_index(clonotypes2),
                   ID=clonotypes1.ID + ':' + clonotypes2.ID,
                   samples=list(set(concatenate([clonotypes1.source, clonotypes2.source]))))

    def get_aa_clonotypes_from_nt_clonotypes(self):
        # print('[clonotype_index, source, ID] : ', [self.clonotype_index, list(self.source), self.ID])
        return AminoAcidClonotypes(nt_clonotype_index=self.clonotype_index, samples=list(self.source), ID=self.ID)

class ClonotypesList(list):
    def __init__(self, list_of_clonotypes=None, clonotypes=None):
        self.clonotypes_infos=None
        if clonotypes is not None:
            #super(ClonotypesList, self).__init__(iter([clonotypes]))
            self.append(clonotypes)

        elif list_of_clonotypes is not None:
            #super(ClonotypesList, self).__init__(iter(list_of_clonotypes))
            for clonotypes in list_of_clonotypes:
                self.append(clonotypes)

    def get_nt_shared_clonotypes(self):
        start=True
        shared_clonotypes = ''
        for clonotypes in self:
            if start:
                shared_clonotypes = clonotypes
                start=False
            else:
                shared_clonotypes = NucleotideClonotypes.shared_clonotypes(shared_clonotypes, clonotypes)
        if shared_clonotypes != '':
            return shared_clonotypes
        return None

    def get_aa_shared_clonotypes(self):
        start=True
        shared_clonotypes = ''
        for clonotypes in self:
            if start:
                shared_clonotypes = clonotypes
                start=False
            else:
                shared_clonotypes = AminoAcidClonotypes.shared_clonotypes(shared_clonotypes, clonotypes)
        if shared_clonotypes != '':
            return shared_clonotypes
        return None


    def append(self, clonotypes):
        super(ClonotypesList, self).append(clonotypes)
        if self.clonotypes_infos is None:
            # print('clonotypes: ', clonotypes)
            # if isinstance(clonotypes, AminoAcidClonotypes):
                # print("AminoAcidClonotypes: ", AminoAcidClonotypes)
            #print('source :', clonotypes.source)
            self.clonotypes_infos = clonotypes.source.clonotype_sequence_infos

    def get_total_cells_per_clonotypes(self, clonotype_level="nucleotide", clonotype_ids=None):
        if clonotype_ids is not None:
            if clonotype_level == "nucleotide":
                mylist = self.get_nt_clonotype_cell_count_df(clonotype_ids=clonotype_ids).sum(axis=0).tolist()
            else:
                # print("self.get_aa_clonotype_cell_count_df(clonotype_ids=clonotype_ids): ", self.get_aa_clonotype_cell_count_df(clonotype_ids=clonotype_ids))
                mylist = self.get_aa_clonotype_cell_count_df(clonotype_ids=clonotype_ids).astype(float).sum(axis=0)
                # print("1: ",mylist)
                mylist = mylist.tolist()
                # print("2: ", mylist)
        else:
            if clonotype_level == "nucleotide":
                mylist = self.get_nt_clonotype_cell_count_df().sum(axis=0).tolist()
            else:
                mylist = self.get_aa_clonotype_cell_count_df()
                mylist = mylist.sum(axis=0).tolist()

        return mylist

    def get_nt_clonotype_cell_count_df(self, clonotype_ids=None):
        list_of_df = []
        for clonotypes in self:
            cell_count_df = clonotypes.get_cell_count_by_clonotype_df()
            if cell_count_df is not None:
                list_of_df.append(cell_count_df)

        df = concat(list_of_df, axis=1)
        df = df.fillna(0)

        if clonotype_ids is not None:
            df = df.ix[clonotype_ids]

        return df

    def get_aa_frequencies(self, clonotype_ids=None):
        list_of_df = []
        for aa_clonotypes in self:
            list_of_df.append(aa_clonotypes.get_frequencies())

        df = concat(list_of_df, axis=1)
        df = df.fillna(0)

        if clonotype_ids is not None:
            df = df.ix[clonotype_ids]

        return df


    def get_nt_clonotype_frequency_df_with_aa_clonotype_ids_as_index(self, clonotype_ids=None):
        list_of_df = []
        for aa_clonotypes in self:
            cell_count_df = aa_clonotypes.get_cell_counts_grouping_by_clonotype_ids()
            if cell_count_df is not None:
                list_of_df.append(cell_count_df)

        df = concat(list_of_df, axis=1)
        df = df.fillna(0)

        if clonotype_ids is not None:
            df = df.ix[clonotype_ids]

        return df

    def get_aa_clonotype_cell_count_df(self, clonotype_ids=None):
        list_of_df = []
        for aa_clonotypes in self:
            # cell_count_df = aa_clonotypes.get_cell_counts()
            cell_count_df = aa_clonotypes.get_cell_counts_grouping_by_clonotype_ids()
            # print("aa_clonotypes ID: ", aa_clonotypes.ID)
            # print("get_aa_clonotype_cell_count_df: ", cell_count_df)
            if cell_count_df is not None:
                list_of_df.append(cell_count_df)

        df = concat(list_of_df, axis=1)

        if clonotype_ids is not None:
            df = df.ix[clonotype_ids]

        df = df.fillna(0)
        df = df.astype(float).astype(int)
        return df

    def get_aa_pvalues_df(self):
        list_of_df = []
        for aa_clonotypes in self:
            # pval_df = clonotypes.get_amino_acid_clonotypes().get_uniq_pvalues_by_samples_df()
            pval_df = aa_clonotypes.get_uniq_pvalues_by_samples_df()
            if pval_df is not None:
                list_of_df.append(pval_df)

        df = concat(list_of_df, axis=1)
        df = df.fillna(1)
        return df

    def get_pvalues_df(self):
        list_of_df = []
        for aa_clonotypes in self:
            pval_df = aa_clonotypes.get_pvalues_df()
            if pval_df is not None:
                list_of_df.append(pval_df)
            else:
                 print('No expansion test was applied for ' + aa_clonotypes.ID)
        df = concat(list_of_df, axis=1)
        df = df.fillna(1)
        return df

    def get_aa_clonotypesList_with_pvalue_higher_equal_than(self, threshold=0.05):
        clonotypes_list = ClonotypesList()
        for clonotypes in self:
            exp = clonotypes.get_pvalue_higher_equal_than(threshold=threshold)
            if exp is not None:
                clonotypes_list.append(exp)
        return clonotypes_list

    def get_aa_clonotypesList_with_pvalue_lower_than(self, threshold=0.05):
        clonotypes_list = ClonotypesList()
        for clonotypes in self:
            exp = clonotypes.get_pvalue_lower_than(threshold=threshold)
            print(exp)
            if exp is not None:
                clonotypes_list.append(exp)
        return clonotypes_list

    def get_aa_clonotypes_df_with_at_least_pvalue_lower_than(self, threshold=0.05):
        pvalues_df_list = []
        for clonotypes in self:
            pvalue_df = clonotypes.get_pvalues_df()
            # print(pvalue_df)
            if pvalue_df is not None:
                pvalues_df_list.append(pvalue_df)


        pvalues_df = concat(pvalues_df_list, axis= 1 )
        dict_iloc_indexes = unique(where(pvalues_df < threshold)[0])

        # print("dict_iloc_indexes: ", dict_iloc_indexes)
        # print("pvalues_df: ", pvalues_df)

        pvalues_df = pvalues_df.iloc[dict_iloc_indexes]
        return pvalues_df

    def get_sample_associated_with_pvalues(self, pvalues, ref_pvalues_df):

        # print("pvalues: ", pvalues)

        # print(ref_pvalues_df.head())
        # print(list(ref_pvalues_df.index.values))
        # print(pvalues.iloc[[1, 2, 3, 4, 5]])

        sample_ids=[]
        notin_indexes=[]
        in_indexes=[]

        for index in pvalues.index.values:
            pval = pvalues.ix[index]

            # print('pval: ', pval)

            if index in ref_pvalues_df.index.values:
                myrow = ref_pvalues_df.ix[index]

                # print('myrow: ', type(myrow[0]))

                selected_index = where(myrow == pval)[0]

                # print(myrow.index[selected_index])
                if len(selected_index) > 0:
                    sample_id = myrow.index[selected_index]

                    # print(sample_id)
                    # sample_id=sample_id.split()
                    # print('index: ', index)

                    sample_ids.append(sample_id[0].split("_pval")[0])
                    in_indexes.append(index)
                else:
                    notin_indexes.append(index)
            else:
                notin_indexes.append(index)

        # print("index not in ref_df: ", notin_indexes)
        # print("sample_ids: ", sample_ids)

        s = Series(sample_ids, index=in_indexes)
        return s

    def get_aa_clonotype_cell_count_corresp_to_pvalues(self, pvalues, pvalues_df):
        # pvalues_df = self.get_aa_pvalues_df()

        sample_list = self.get_sample_associated_with_pvalues(pvalues, pvalues_df)
        cell_count_df = self.get_aa_clonotype_cell_count_df()

        # print('cell_count_df: ', cell_count_df)

        mycell_counts = []
        in_indexes = []
        for index in sample_list.index.values:
            in_indexes.append(index)

            # print('sample_list[index]: ',sample_list[index])

            cell_count_sample_df = cell_count_df.filter(regex=(sample_list[index] + "_cell_count"))
            cell_count = cell_count_sample_df.ix[index].tolist()

            # print('cell_count: ', cell_count)

            mycell_counts.append(cell_count)

        # print('mycell_counts: ', concatenate(mycell_counts))
        # print('in_indexes: ', in_indexes)

        s = Series(concatenate(mycell_counts), index=in_indexes)
        return s

    def get_nt_clonotype_index(self):
        clonotype_index = []
        for clonotypes in self:
            clonotype_index.extend(clonotypes.clonotype_index)
        #print(clonotype_ids)
        return list(set(clonotype_index))

    def get_clonotype_index(self):
        clonotype_index = []
        for clonotypes in self:
            clonotype_index.extend(clonotypes.clonotype_index)
        #print(clonotype_ids)
        return list(set(clonotype_index))

    def get_aa_clonotype_ids(self):
        clonotype_ids = []
        for clonotypes in self:
            clonotype_ids.extend(clonotypes.aa_clonotype_ids)
        #print(clonotype_ids)
        return list(set(clonotype_ids))

    def get_aa_clonotype_ids_list(self):
        return concatenate(self.get_aa_clonotype_ids_df().values.tolist)

    def get_aa_clonotype_ids_df(self):
        indexes = []
        values= []
        array_find = False

        for clonotypes in self:
            # print("get_aa_clonotype_ids_df: ", type(sample.aa_clonotypes.aa_clonotype_ids))
            if type(clonotypes.aa_clonotypes.aa_clonotype_ids) == np.ndarray:
                values.extend(clonotypes.aa_clonotype_ids)
                array_find=True
            else:
                indexes.extend(clonotypes.aa_clonotype_ids.index)
                values.extend(clonotypes.aa_clonotype_ids.values)
        #print(clonotype_ids)
        if array_find:
            newdf = DataFrame(list(set(values)), index=list(set(values)))
            newdf.columns = ['aminoAcid']
            return newdf
        else:
            newdf = DataFrame(values, index=indexes)
            newdf = newdf.drop_duplicates(subset=0, keep='last')
            newdf.columns = ['aminoAcid']

        return newdf

    def get_aa_clonotype_id_df_by_clonotype_index(self, clonotype_index):
        clonotype_index_df = []
        start = True
        for clonotypes in self:
            if start:
                clonotype_ids_df = clonotypes.aa_clonotype_ids
                start = False
            else:
                clonotype_ids_df =  concat([clonotype_ids_df, clonotypes.aa_clonotype_ids])

        clonotype_ids_df = clonotype_ids_df.drop_duplicates()

        # print("clonotype_ids_df[0]: ", list(clonotype_ids_df.index.values))

        indexes = where(clonotype_ids_df.index.values == clonotype_index)[0]

        # print("clonotype indexes found: ", indexes)

        if len(indexes) > 0:
            # print("Series(clonotype_ids_df.tolist())[index].tolist(): ", Series(clonotype_ids_df.tolist())[indexes].tolist())
            return Series(clonotype_ids_df.tolist())[indexes].tolist()

        return None

    def get_aa_clonotype_index_df_by_clonotype_id(self, clonotype_id):
        clonotype_ids_df = []
        start = True
        for clonotypes in self:
            if start:
                clonotype_ids_df = clonotypes.aa_clonotype_ids
                start = False
            else:
                clonotype_ids_df =  concat([clonotype_ids_df, clonotypes.aa_clonotype_ids])

        clonotype_ids_df = clonotype_ids_df.drop_duplicates()

        # print("clonotype_ids_df[0]: ", clonotype_ids_df)

        index = where(clonotype_ids_df == clonotype_id)[0]
        if len(index) > 0:
            return Series(clonotype_ids_df.index.values)[index].tolist()

        return None

    def get_aa_clonotype_ids_df_by_clonotype_index(self, clonotype_index):
        clonotype_ids_df = []
        start = True
        for clonotypes in self:
            if start:
                clonotype_ids_df = clonotypes.aa_clonotype_ids
                start = False
            else:
                clonotype_ids_df =  concat([clonotype_ids_df, clonotypes.aa_clonotype_ids])

        clonotype_ids_df = clonotype_ids_df.ix[clonotype_index]
        clonotype_ids_df = clonotype_ids_df.drop_duplicates()

        return clonotype_ids_df

    def merged_in_aa_clonotypes(self, clonotype_level="aacdr3"):
        start=True
        for clonotypes in self:
            if start:
                # print('clonotypes: ', clonotypes)
                if isinstance(clonotypes, NucleotideClonotypes):
                    merged_clonotypes = AminoAcidClonotypes(nt_clonotype_index=clonotypes.clonotype_index,
                                                            samples=clonotypes.source, ID=clonotypes.ID, clonotype_level=clonotype_level)
                else:
                    merged_clonotypes = AminoAcidClonotypes(nt_clonotype_index=clonotypes.nt_clonotype_index,
                                                            samples=clonotypes.source, ID=clonotypes.ID, clonotype_level=clonotype_level)
                start=False
            else:
                merged_clonotypes = Clonotypes.merge_aa(merged_clonotypes, clonotypes)
        return merged_clonotypes


class ClonotypeSample:
    def __init__(self, column, comparisonDataSet):

        # print(comparisonDataSet.samples_info_file)

        self.name_descriptor = SampleLabel(column, comparisonDataSet.samples_info_file)

        # print("descriptor: ",self.name_descriptor)

        self.comparisonDataSet = comparisonDataSet

        self.ID = self.name_descriptor.ID
        self.sample_criteria = self.name_descriptor.sample_criteria

        self.all_samples_infos = comparisonDataSet.samples_info_file
        self.data_source_df = comparisonDataSet.data_source.dataframe
        self.data_source = comparisonDataSet.data_source

        self.nt_clonotypes = None

        if self.data_source.is_nt_clonotypes():
            self.genome_counts = self.data_source.get_genome_counts_for_sample_id(self.ID)
            self.genome_counts_frequencies = self.calculate_genome_counts_frequencies()

            self.clonotype_index = list(self.genome_counts.dataframe.index.values)
            self.clonotype_ids = list(self.genome_counts.dataframe.index.values)

            self.nt_clonotypes = NucleotideClonotypes(clonotype_index=self.clonotype_index, sample=self, ID=self.ID)

            # print('nt 1: ', self.nt_clonotypes)

            self.aa_clonotypes = self.nt_clonotypes.get_aa_clonotypes_from_nt_clonotypes()

            # print('aa 2: ', self.aa_clonotypes)

            self.expansion_pvalues = self.data_source.get_pvalues(self.ID)
        else:

            self.genome_counts = self.data_source.get_genome_counts_for_sample_id(self.ID)

            # print('self.genome_counts : ', self.genome_counts )

            self.genome_counts_frequencies = self.calculate_genome_counts_frequencies()

            # print("genome_counts_frequencies: ", self.genome_counts_frequencies)

            self.clonotype_index = list(self.genome_counts.dataframe.index.values)

            # print("self.clonotype_index: ", self.clonotype_index)
            # print("self.genome_counts.dataframe: ", self.genome_counts.dataframe)

            # self.clonotype_ids = self.data_source.get_aa_clonotype_sequence(clonotype_index=self.clonotype_index)

            # print('self.genome_counts: ', self.genome_counts.dataframe)
            # print('self.clonotype_ids: ', self.clonotype_ids)

            # print("self.genome_counts.dataframe: ", self.genome_counts.dataframe)
            # print("self.data_source_df: ", self.data_source_df)

            self.aa_clonotype_ids = self.data_source_df["aminoAcid"].ix[self.clonotype_index]

            self.aa_clonotypes = AminoAcidClonotypes(aa_clonotype_ids=self.aa_clonotype_ids, samples=[self], ID=self.ID)

            # print("ClonotypeSample ID: ", self.ID)
            # print("ClonotypeSample clns IDS: ", self.aa_clonotypes.aa_clonotype_ids)
            # print("ClonotypeSample cell count: ", self.aa_clonotypes.get_cell_count_by_clonotype_df())

            self.clonotype_ids = self.aa_clonotypes.aa_clonotype_ids

            # self.genome_counts.dataframe.index = self.clonotype_ids
            # self.genome_counts_frequencies.dataframe.index = self.clonotype_ids
            # print("self.data_source:",self.data_source.dataframe)

            self.expansion_pvalues = self.data_source.get_pvalues(self.ID)

            # print("self.expansion_pvalues:", self.expansion_pvalues)
            # print('self.expansion_pvalues: ', self.expansion_pvalues)

            if self.expansion_pvalues is not None:
                self.expansion_pvalues_index = self.expansion_pvalues.index.values
                # aminoacid_seq = self.data_source.get_aa_clonotype_sequence(clonotype_index=self.expansion_pvalues.index.values)
                # self.expansion_pvalues.index = aminoacid_seq

        if len(self.clonotype_ids) == 0:
            print('sample '+ self.ID +' does not have any clonotypes !')

    def __str__(self):
        if self.clonotype_ids is not None:
            return str(self.ID + str(self.clonotype_ids))
        return str(self.ID + ': No clonotype ids')

    def __repr__(self):
        return self.__str__()

    def get_aa_clonotype_ids_list(self):
        # print(self.aa_clonotype_ids.values.tolist())
        return self.aa_clonotype_ids.values.tolist()

    def get_repeat_ID(self):
        return self.name_descriptor.get_repeat_ID()[0]

    def get_cell_type(self):
        return self.name_descriptor.get_cell_type()[0]

    def get_time_point(self):
        return self.name_descriptor.get_time_point()[0]

    def calculate_genome_counts_frequencies(self):
        # print('self.ID):',self.ID)
        total_genome_counts = self.genome_counts.get_total()[0]
        if total_genome_counts > 0:
            return Frequencies(self.genome_counts.convert_df_counts_2_freq(total_genome_counts))
        return None

    def get_differing_criteria(self, sample):

        # print('repeat sp1 - sp2: ', [self.sample_criteria, sample.sample_criteria])

        return self.sample_criteria.get_differing_criteria(sample.sample_criteria)

    def assign_pvalue_expansion_measurments(self, exvivo, sequence_level='nucleotide', fisher_test='fast'):
        if sequence_level=='amino acid':
            exvivo_counts_initial = exvivo.get_amino_acid_cell_counts()
            stimulated_counts_initial = self.get_amino_acid_cell_counts()
        else:
            exvivo_counts_initial = exvivo.get_cell_counts()
            stimulated_counts_initial = self.get_cell_counts()

        print('comparison: ', [exvivo.ID, self.ID])

        if self.get_total_cell_count() == 0:
            print('--- Fisher exact test ---')
            print('Sample [' + str(self) + '] has no clonotypes !')

        compared_df = DataFrame({exvivo.ID:exvivo_counts_initial, self.ID:stimulated_counts_initial})
        compared_df = compared_df.fillna(0)

        compared_df = compared_df.iloc[where((compared_df[exvivo.ID] > 0) | (compared_df[self.ID] > 0))[0]]

        total_stim = self.get_total_cell_count()
        total_exvivo = exvivo.get_total_cell_count()

        exvivo_counts_unadj = compared_df[exvivo.ID]
        stimulated_counts_unadj = compared_df[self.ID]

        if len(compared_df.values.tolist()) > 0:
            self.expansion_pvalues = Statistics.pvalues_fisher(stimulated_counts_unadj, exvivo_counts_unadj, total_stim, total_exvivo, list(compared_df.index), speed=fisher_test)#expanded
        else:
            self.expansion_pvalues = None

    def  get_cell_counts_by_aa_clonotype_ids(self, clonotype_ids):
        return self.aa_clonotypes.get_cell_counts_grouping_by_clonotype_ids(clonotype_ids)

    def  get_cell_counts_df(self):
        return self.aa_clonotypes.get_cell_counts_grouping_by_clonotype_ids()

    def get_cell_counts_by_clonotype_ids(self, clonotype_ids):
        return self.get_cell_counts(clonotype_ids)
        # print('cell_counts: ', s)
        # print('clonotype_ids: ', clonotype_ids)
        # print('self clonotype ids:', self.clonotype_ids)
        # return s[clonotype_ids]

    def get_cell_counts_by_clonotype_index(self,clonotype_index=None):
        # print('clonotype_ids: ',clonotype_ids)
        if clonotype_index is None:
            return self.genome_counts.dataframe.iloc[:, 0]
        # print('clonotype_ids: ',clonotype_ids)
        return self.genome_counts.dataframe.ix[clonotype_index, 0]


    def get_cell_counts_frequencies_by_clonotype_index(self, clonotype_index=None):
        if clonotype_index is None:
            return self.genome_counts_frequencies.dataframe.iloc[:, 0]
        return self.genome_counts_frequencies.dataframe.ix[clonotype_index, 0]


    def has_repeat(self, sample):
        diff_criteria = self.get_differing_criteria(sample)

        # print([self.ID, sample.ID])

        # print('has_repeat: ', diff_criteria)

        diff_criteria.keep_common_repeat_criteria()

        # print('common has_repeat: ', diff_criteria)

        diff_parameters = diff_criteria.get_parameter_values()

        # print('diff params has_repeat: ', diff_parameters)

        num_diff_parameters = len(diff_parameters)

        if num_diff_parameters == 0:
            return True

        return False

    def get_amino_acid_cell_counts(self, aa_clonotype_ids=None):
        if aa_clonotype_ids is None:
            return self.aa_clonotypes.get_cell_counts().iloc[:, 0]
        else:
            return self.aa_clonotypes.get_cell_counts().ix[aa_clonotype_ids]

    def get_amino_acid_cell_counts_by_clonotype_index(self, clonotype_index):
        return self.aa_clonotypes.get_cell_count().ix[clonotype_index]


    def get_cell_frequencies_by_clonotype_index(self, clonotype_index=None):
        if clonotype_index is None:
            return self.genome_counts_frequencies.dataframe.iloc[:, 0]
        return self.genome_counts_frequencies.dataframe.ix[clonotype_index, 0]

    def get_cell_counts_grouping_by_clonotype_ids(self, clonotype_index=None):
        if clonotype_index is None:
            return self.genome_counts_df_grouped_by_clonotype_ids.iloc[:, 0]
        # print('clonotype_ids: ',clonotype_ids)
        return self.genome_counts_df_grouped_by_clonotype_ids.ix[clonotype_index, 0]

    def get_cell_counts_clonotype_index(self, clonotype_index=None):
        # print('clonotype_ids: ',clonotype_ids)

        if clonotype_index is None:
            return self.genome_counts.dataframe.iloc[:, 0]

        # print('clonotype_ids: ', clonotype_ids)
        # print("get_cell_counts, clonotype_index: ", clonotype_index)
        # print("self.genome_counts.dataframe: ", self.genome_counts.dataframe)

        return self.genome_counts.dataframe.ix[clonotype_index, 0]


    def get_total_clonotype_count(self):
        return len(self.get_clonotype_ids())

    def get_total_cell_count(self):
        df = self.get_cell_counts_clonotype_index()
        return sum(array(df.values.tolist()))

    def get_aa_clonotype_ids_with_min_cell(self, threshold):
        cell_counts = self.aa_clonotypes.get_cell_counts()
        aa_clonotype_ids_indexes = cell_counts.iloc[where(cell_counts >= threshold)[0]].index.values
        df = self.aa_clonotype_ids.ix[aa_clonotype_ids_indexes]
        return df

    def get_aa_clonotypes_with_cells_equal_to(self, number):
        cell_counts = self.aa_clonotypes.get_cell_counts()

        # print('cell_counts: ', cell_counts)

        sample_clonotypes_min_cell_counts = cell_counts.iloc[where(cell_counts == number)[0]]

        # print('sample_clonotypes_min_cell_counts: ', sample_clonotypes_min_cell_counts)
        # nt_clonotype_ids = self.aa_clonotypes.get_nt_clonotypes(aa_clonotype_ids=sample_clonotypes_min_cell_counts.index.values)

        return AminoAcidClonotypes(aa_clonotype_ids=sample_clonotypes_min_cell_counts.index.values, ID=self.ID + '_num_cell_' + str(number), samples=[self])

    def get_nt_clonotypes_with_cells_equal_to(self, number):
        sample_clonotypes_min_cell_counts = self.genome_counts.dataframe[self.genome_counts.dataframe == number]
        return NucleotideClonotypes(list(sample_clonotypes_min_cell_counts.index), ID=self.ID + '_num_cell_' + str(number), samples=[self])

    def get_expanded_nt_clonotypes(self, threshold=0.001):
        clonotype_ids = self.get_expanded_clonotypes_ids(threshold=threshold)
        return NucleotideClonotypes(list(clonotype_ids), ID=self.ID + '_min_pval_' + "{:.2E}".format(threshold), samples=[self])


    def get_expanded_aa_clonotypes(self, threshold=0.001):
        aa_clonotype_ids_index = self.get_expanded_clonotypes_ids(threshold=threshold)
        aa_clonotype_ids = self.aa_clonotype_ids.ix[aa_clonotype_ids_index]
        if self.data_source.is_nt_clonotypes():
            nt_clonotype_index = self.aa_clonotypes.get_nt_clonotypes(aa_clonotype_ids=aa_clonotype_ids)
            if nt_clonotype_index is not None:
                return AminoAcidClonotypes(nt_clonotype_index=nt_clonotype_index, ID=self.ID + '_max_pval_' + "{:.2E}".format(threshold), samples=[self])
            else:
                return AminoAcidClonotypes(ID=self.ID + "{:.2E}".format(threshold) + str(threshold), samples=[self])
        else:
            # print("get_expanded_aa_clonotypes: ", len(aa_clonotype_ids.index.values))
            # print("threshold: ",threshold)
            # print("type: ", type(threshold))
            return AminoAcidClonotypes(aa_clonotype_ids=aa_clonotype_ids, ID=self.ID + '_max_pval_' + "{:.2E}".format(threshold), samples=[self])

    def get_aa_clonotypes_with_min_cells(self, threshold):
        aa_clonotype_ids = self.get_aa_clonotype_ids_with_min_cell(threshold)

        # print(self.ID)
        # print('# aa_clonotype_ids: ', len(aa_clonotype_ids))
        # print('aa_clonotype_ids: ', aa_clonotype_ids[0:15])

        if self.data_source.is_nt_clonotypes():
            nt_clonotype_index = self.aa_clonotypes.get_nt_clonotypes(aa_clonotype_ids=aa_clonotype_ids)
            if nt_clonotype_index is not None:
                return AminoAcidClonotypes(nt_clonotype_index=nt_clonotype_index, ID=self.ID + '_min_cell_' + str(threshold), samples=[self])
            else:
                return AminoAcidClonotypes(ID=self.ID + '_min_cell_' + str(threshold), samples=[self])
        else:
            # index_mod = where(self.aa_clonotypes.aa_clonotype_ids == aa_clonotype_ids)[0]
            # self.aa_clonotypes.aa_clonotype_ids.iloc[index_mod]
            # print('aa_clonotype_ids 22: ', aa_clonotype_ids)
            return AminoAcidClonotypes(aa_clonotype_ids=aa_clonotype_ids, ID=self.ID + '_min_cell_' + str(threshold), samples=[self])

    def get_clonotypes_with_cells_in_all_samples_equal_to(self, number):
        sample_clonotypes_min_cell_counts = self.genome_counts.dataframe[self.genome_counts.dataframe == number]
        return NucleotideClonotypes(list(sample_clonotypes_min_cell_counts.index), ID=self.ID + '_cell_' + str(number), samples=[self])

    def get_nt_clonotypes_with_min_cells(self, threshold):
        # form = controller.Format()
        # formatted_id = form.default_sample_ID(self)
        sample_clonotypes_min_cell_counts = self.genome_counts.dataframe[self.genome_counts.dataframe >= threshold]
        return NucleotideClonotypes(list(sample_clonotypes_min_cell_counts.index), ID=self.ID + '_min_cell_' + str(threshold), samples=[self])

    def get_expanded_clonotypes_ids(self, threshold=0.05):
        if len(self.expansion_pvalues) > 0:
            sample_expanded_clonotypes_pvalues = self.expansion_pvalues[self.expansion_pvalues < threshold]
            return list(sample_expanded_clonotypes_pvalues.index)

        return None

    def get_expanded_pvalues(self, threshold=0.001):
        if len(self.expansion_pvalues) > 0:
            sample_expanded_clonotypes_pvalues = self.expansion_pvalues[self.expansion_pvalues < threshold]
            return sample_expanded_clonotypes_pvalues
        return None

    def get_clonotype_ids(self):
        cell_count = self.genome_counts.dataframe.iloc[:,0]
        index_mod = where(cell_count > 0)[0]
        return list(cell_count.iloc[index_mod].index)

    def get_subject_ids(self):
        return self.sample_criteria[SampleCriteriaCategories.subject_id]

class SampleLabel:
    def __init__(self, string=None, samples_info_file=None):
        self.source_string = ''
        self.all_infos = ''
        self.ID = ''

        if samples_info_file is not None:
            self.samples_info_file = samples_info_file

        self.sample_criteria = SampleCriteriaParameters()
        if string is not None:
            self.analyse(string, samples_info_file)
            #self.source_string = string

    def occurence(self, pattern, string):
        m = search(pattern, string)
        if m is None:
            return 'No ID found'
        else:
            return m.group(1)

    def get_repeat_ID(self):
        return self.sample_criteria[SampleCriteriaCategories.repeat_ID]

    def get_cell_type(self):
        return self.sample_criteria[SampleCriteriaCategories.cell_type]

    def get_time_point(self):
        return self.sample_criteria[SampleCriteriaCategories.time_point]

    def analyse(self, string, samples_info_file):
        self.source_string = string
        # occurence('^\D+\s{0,1}\\({0,1}%{0,1}\\){0,1}_(\d{4}.*)', string).lower()
        pattern1 = '^estimatedNumberGenomes_(.*)'
        respatt1 = self.occurence(pattern1, string)
        pattern2 = '^(.*)_cell_count'
        respatt2 = self.occurence(pattern2, string)
        pattern3 = '^(.*)_Read\\.count.*'
        respatt3 = self.occurence(pattern3, string)

        if respatt1 != 'No ID found':
            self.ID = respatt1.lower()
        elif respatt2 != 'No ID found':
            self.ID = respatt2.lower()
        elif respatt3 != 'No ID found':
            self.ID = respatt3.lower()

        # print(string)
        # print("self.ID: ", self.ID)

        self.all_infos = samples_info_file.getInfo(self.ID)
        #print('ID: ', self.ID )

        for criterion in self.sample_criteria :
            #print(samples_info_file.info_df)
            #print(self.ID)
            #print('criterion, samples_info_file: ', [criterion, samples_info_file.getInfo(self.ID, criterion.value)])
            mystringlist = samples_info_file.getInfo(self.ID, criterion.value)

            # print('value: ', criterion.value)
            # print('stringos: ', mystringlist)

            if mystringlist is not None:
                if type(mystringlist) is list:
                    if len(mystringlist) > 0 :
                        if type(mystringlist[0]) is str:
                            for mystring in mystringlist:
                                # values = mystring.split(", ")
                                #print('values: ', values)
                                # for value in values:
                                #     self.sample_criteria[criterion].append(value.lower())
                                self.sample_criteria[criterion].append(mystring.lower())
                        else:
                            self.sample_criteria[criterion].extend(mystringlist)
                else:
                    self.sample_criteria[criterion].append(mystringlist)

        #print('self.sample_criteria: ', self.sample_criteria)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.sample_criteria


class ClonotypeSamples(list):
    def __init__(self, samples=[], comparisonDataSet=None, data_source=None):
        self.ID = 'ID not defined'
        self.sample_criteria = SampleCriteriaParameters()

        self.clonotype_sequence_infos = None

        # print(data_source)

        if comparisonDataSet is not None:
            self.comparisonDataSet = comparisonDataSet
            if data_source is None:
                self.clonotype_sequence_infos = comparisonDataSet.data_source

            # self.nucleotide_sequences = self.get_nucleotide_sequences()
            # self.counts_reads = self.clonotype_sequence_infget_counts_reads()
            # self.frequencies_reads = self.clonotype_sequence_infget_freq_reads()

            self.counts_genomes = self.clonotype_sequence_infos.get_counts_genomes()

            # total_counts_genomes = self.counts_genomes.get_total()
            # new_freq_genomes = self.counts_genomes.convert_df_counts_2_freq(total_counts_genomes, self.nucleotide_sequences)
            # self.frequencies_genomes = Frequencies(new_freq_genomes)

            if len(samples) == 0:
                self.build_samples(comparisonDataSet)
                # self.initialise_label()
                # self.assign_subject_clonotype_ids()

        if len(samples) > 0:
            for sample in samples:
                # print("testing sample: ", sample)
                self.append(sample)

        # self.assign_subject_clonotype_ids()

    def get_frequencies(self):
        return self.get_aa_clonotypesList().get_aa_frequencies()

    def get_cell_types(self):
        cell_types = []
        for sample in self:
            cell_types.append(sample.get_cell_type())

        return list(set(cell_types))

    def get_time_points(self):
        return TimePoints(self, self.clonotype_sequence_infos)


    def gene_usage_stats_calculation(self, gene_freq, gene_type):
        my_gene_stats = []
        for i in arange(0,len(gene_freq.columns.values)-1):
            col1=gene_freq.columns.values[i]
            for j in arange(i+1, len(gene_freq.columns.values) ):
                col2 = gene_freq.columns.values[j]
                # print(gene_freq[col2])
                num_elts1 = len(where(isnan(gene_freq[col1]) == False)[0])
                num_elts2 = len(where(isnan(gene_freq[col2])== False)[0])

                if (num_elts1 > 3) and (num_elts2 > 3):
                    scor_coef, spval = spearmanr(gene_freq[col1], gene_freq[col2])
                    pcor_coef, ppval = pearsonr(gene_freq[col1], gene_freq[col2])
                    my_gene_stats.append([gene_type, col1, col2, scor_coef, spval, pcor_coef, ppval])

        return DataFrame(my_gene_stats, columns=["gene type", "sample1", "sample2", "spearman coef", "spearman pval", "pearson cor_coef", "pearson pval"])

    def get_gene_usage_stats_clns_cells(self):
        cell_count_df =  self.get_aa_clonotype_cell_count_df_with_aa_clonotype_ids_as_index_by_samples()

        cell_gene_stats_df, cell_gene_counts_df = self.get_gene_usage_sats(cell_count_df, "cells")

        clns_count_df = cell_count_df
        clns_count_df[clns_count_df > 0] = 1

        clns_gene_stats_df, clns_gene_counts_df = self.get_gene_usage_sats(clns_count_df, "clns")

        colnames = [sample + "_cln_counts" for sample in self.get_sample_ids()]
        # print(colnames)
        clns_gene_counts_df.columns=colnames

        return [clns_gene_stats_df, clns_gene_counts_df, cell_gene_stats_df, cell_gene_counts_df]

    def get_gene_usage_sats(self, counts_df, feature):
        # print(counts_df)

        totals = counts_df.sum()

        clns_ids = counts_df.index.values
        clns_ids_selected = self.get_aa_clonotype_ids_df().ix[clns_ids]

        # print(clns_ids_selected[1:5])

        # counts_df.index = clns_ids_selected
        # print(counts_df.head())
        # clns_ids = counts_df.index.values

        clns_ids_list = concatenate(clns_ids_selected.values.tolist())

        # print(clns_ids_list[1:5])

        splitted_ids = [ cln_id.split("_") for cln_id in clns_ids_list]

        # print(splitted_ids[1:5])

        mydf = DataFrame(splitted_ids, index=counts_df.index )

        # print(mydf[range(3)])

        merged_df = concat([mydf[range(3)], counts_df],axis=1)

        # print(merged_df.head())

        merged_df.columns = concatenate([ ["CDR3"], ["V gene"], ["J gene"], counts_df.columns.values])

        vgene_col = concatenate([["V gene"], counts_df.columns.values])
        jgene_col = concatenate([["J gene"], counts_df.columns.values])

        # mydf= merged_df[vgene_col].astype(int)

        # print("test", merged_df[vgene_col].groupby("V gene").sum().head())

        # print(merged_df[vgene_col].groupby("V gene").sum().head())

        # print(totals)

        gp_vgene_counts_df = merged_df[vgene_col].groupby("V gene").sum()
        gp_jgene_counts_df = merged_df[jgene_col].groupby("J gene").sum()

        gp_vgene_freq_df = gp_vgene_counts_df.divide(totals) * 100
        gp_jgene_freq_df = gp_jgene_counts_df.divide(totals) *100

        # print(gp_vgene_freq_df.head())

        # gp_vgene_freq = gp_vgene_freq
        # gp_vgene_freq.corr(method='spearman')

        vgene_stats_df = self.gene_usage_stats_calculation(gp_vgene_freq_df, "V gene" + " " + feature)
        jgene_stats_df = self.gene_usage_stats_calculation(gp_jgene_freq_df, "J gene "+ " " + feature)

        gene_stats_df = concat([vgene_stats_df, jgene_stats_df], axis=0)

        gene_freq_df = concat([gp_vgene_counts_df, gp_jgene_counts_df], axis=0)

        return gene_stats_df, gene_freq_df

    def is_nt_clonotypes(self):
        return self.clonotype_sequence_infos.is_nt_clonotypes()

    def get_aa_clonotype_index_df_by_clonotype_id(self, clonotype_id):
        return self.get_aa_clonotypesList().get_aa_clonotype_index_df_by_clonotype_id(clonotype_id)

    def get_aa_clonotype_id_df_by_clonotype_index(self, clonotype_index):
            return self.get_aa_clonotypesList().get_aa_clonotype_id_df_by_clonotype_index(clonotype_index)

    def get_aa_clonotype_cell_count_corresp_to_pvalues(self, pvalues):
        ref_pvalues = self.get_aa_pvalues_df()
        return self.get_aa_clonotypesList().get_aa_clonotype_cell_count_corresp_to_pvalues(pvalues, ref_pvalues)

    def is_technical(self, sample1, sample2):
        rep1 = sample1.get_repeat_ID()
        rep2 = sample2.get_repeat_ID()

        if search('\-', rep1[0]):
            splitted_string = rep1[0].split('-')
            rep1 = splitted_string[0]
        if search('\-',rep2[0]):
            splitted_string = rep2[0].split('-')
            rep2 = splitted_string[0]
        if rep1 == rep2:
            return True
        return False

    def get_repeatsList(self):
        samples_to_return = []
        for i1 in range(len(self)-1):
            sample1 = self[i1]
            for i2 in range(i1 + 1, len(self)):
                sample2 = self[i2]
                if sample1.has_repeat(sample2):

                    print('repeat: ', [sample1.ID,sample2.ID] )

                    samples = ClonotypeSamples([sample1, sample2])
                    if self.is_technical(sample1, sample2):
                        repeats = Repeats(samples=samples, repeat_type='technical')
                    else:
                        repeats = Repeats(samples=samples, repeat_type='culture')

                    samples_to_return.append(repeats)

        if len(samples_to_return) > 0:
            return RepeatsList(list_of_repeats=samples_to_return)
        return None

    def get_pvalues_df(self):
        list_of_df = []
        sample_ids = []
        for sample in self:
            pvals = sample.expansion_pvalues
            if pvals is not None:
                list_of_df.append(pvals)
                sample_ids.append(sample.ID)
            else:
                print('No expansion test was applied for ' + sample.ID)

        df = concat(list_of_df, axis=1)
        df.columns = [x + '_pval' for x in sample_ids]
        df = df.fillna(1)
        return df

    def get_pvalues_df_by_clonotype_index(self, clonotype_index):
        list_of_pvalues = []
        samples_with_pvalues = []
        for sample in self:
            pvalues = sample.expansion_pvalues
            # print("get_pvalues_df_by_clonotype_index: ", sample.expansion_pvalues)
            # print("ix: ", clonotype_index)
            if pvalues is not None:
                # print("sample.expansion_pvalues:", sample.expansion_pvalues)
                list_of_pvalues.append(sample.expansion_pvalues.ix[clonotype_index])
                samples_with_pvalues.append(sample)

        if len(list_of_pvalues) > 0:
            samples_with_pvalues = ClonotypeSamples(samples=samples_with_pvalues)
            df = concat(list_of_pvalues, axis=1)

            df.columns = [x + '_pval' for x in samples_with_pvalues.get_sample_ids()]
            df = df.ix[clonotype_index]
            df = df.fillna(1)
            return df
        return None

    def get_aa_seq_with_gene_names(self, clonotype_index=None):
        if clonotype_index is not None:
            return self.clonotype_sequence_infos.get_amino_acid_sequences_for(clonotype_index)
        clonotype_index = self.get_clonotype_indexes()
        return self.clonotype_sequence_infos.get_amino_acid_sequences_for(clonotype_index)

    def get_aminoAcid_sequences(self, clonotype_index=None):
        if clonotype_index is not None:
            return self.clonotype_sequence_infos.get_amino_acid_sequences_for(clonotype_index)
        clonotype_index = self.get_clonotype_indexes()
        return self.clonotype_sequence_infos.get_amino_acid_sequences_for(clonotype_index)

    def assign_pvalue_expansion_measurments(self, sequence_level='nucleotide', fisher_test='fast'):#amino acid
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print('Fisher exact test at the ' + sequence_level + ' level...')
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        # print('Experiment types: ', self.get_experiment_types())
        for subject_id in self.get_subject_ids():
            for experiment_type in self.get_experiment_types():
                if experiment_type != 'exvivo':

                    exposed_samples_criteria = SampleCriteriaParameters(
                                                    [(SampleCriteriaCategories.experiment_type, [experiment_type]),
                                                    (SampleCriteriaCategories.subject_id, [subject_id])])

                    subset_samples = self.get_from_list(exposed_samples_criteria)

                    # print('exposed_samples_criteria: ', exposed_samples_criteria)
                    # print('subset_samples: ',subset_samples)

                    if subset_samples is not None:

                        exvivo_sample_criteria = SampleCriteriaParameters([(SampleCriteriaCategories.experiment_type, ['exvivo']),
                                                         (SampleCriteriaCategories.subject_id, [subject_id])])

                        #print(self)

                        exvivo_list = self.get_from_list(exvivo_sample_criteria)

                        if exvivo_list is None:
                            raise ValueError('ERROR: no exvivo sample found !!')
                        elif len(exvivo_list) > 1:
                            raise ValueError('WARN: > 1 exvivo sample found: ' + exvivo_list)

                        exvivo = exvivo_list[0]

                        if exvivo.get_total_cell_count() == 0:
                            print('--- Fisher 2x2 exact test ---')
                            print('Sample [' + str(exvivo) + '] has no clonotypes !')

                        # with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                        #     t = [ executor.map(sample.assign_pvalue_expansion_measurments, exvivo, sequence_level=sequence_level) for sample in subset_samples ]
                            # t = executor.map(sample.assign_pvalue_expansion_measurments, exvivo, sequence_level=sequence_level)

                        for sample in subset_samples:
                            sample.assign_pvalue_expansion_measurments(exvivo, sequence_level=sequence_level, fisher_test=fisher_test)

    def get_aa_associated_nt_clonotype_counts_df_by_samples(self):
        return self.get_aa_clonotypesList().get_associated_nt_clonotype_counts_df()

    def get_aa_cdr3_by_nt_clonotype_df(self):
        return self.get_nt_clonotypesList().get_aa_cdr3_by_nt_clonotype_df()

    def get_aa_clonotype_frequency_df(self):
        return self.get_aa_clonotypesList().get_aa_clonotype_frequency_df()

    def get_aa_associated_nt_clonotype_counts_df(self, clonotype_level="aacdr3"):
        # print('get_aa_clonotypesList: ', self.get_aa_clonotypesList())
        # print('get_aa_clonotypesList + merged_in_aa_clonotypes: ', self.get_aa_clonotypesList().merged_in_aa_clonotypes())
        # return self.get_aa_clonotypesList().merged_in_aa_clonotypes().get_associated_nt_clonotype_counts_df()
        return self.get_aa_clonotypesList().merged_in_aa_clonotypes(clonotype_level).aa_clonotype_ids_nt_convergence

    def get_aa_clonotype_cell_count_df_by_samples(self):
        return self.get_aa_clonotypesList().get_aa_clonotype_cell_count_df()

    def get_aa_clonotype_cell_count_df_with_aa_clonotype_ids_as_index_by_samples(self):
        return self.get_aa_clonotypesList().get_aa_clonotype_cell_count_df()

    def get_nt_clonotype_frequency_df(self):
        return self.get_nt_clonotypesList().get_nt_clonotype_frequency_df_with_aa_clonotype_ids_as_index()

    def get_nt_clonotype_cell_count_df(self):
        return self.get_nt_clonotypesList().get_nt_clonotype_cell_count_df()

    def get_aa_clonotype_ids_list(self):
        return concatenate(self.get_aa_clonotype_ids_df().values.tolist())

    def get_aa_clonotype_ids_df(self):
        indexes = []
        values= []
        array_find = False

        for sample in self:
            # print("get_aa_clonotype_ids_df: ", type(sample.aa_clonotypes.aa_clonotype_ids))
            if type(sample.aa_clonotypes.aa_clonotype_ids) == np.ndarray:
                values.extend(sample.aa_clonotypes.aa_clonotype_ids)
                array_find=True
            else:
                indexes.extend(sample.aa_clonotypes.aa_clonotype_ids.index)
                values.extend(sample.aa_clonotypes.aa_clonotype_ids.values)
        #print(clonotype_ids)
        if array_find:
            newdf = DataFrame(list(set(values)), index=list(set(values)))
            newdf.columns = ['aminoAcid']
            return newdf
        else:
            newdf = DataFrame(values, index=indexes)
            newdf = newdf.drop_duplicates(subset=0, keep='last')
            newdf.columns = ['aminoAcid']

        return newdf

    def get_aa_pvalues_df(self):
        return self.get_aa_clonotypesList().get_pvalues_df()

    def get_nt_pvalues_df(self):
        return self.get_nt_clonotypesList().get_pvalues_df()

    def get_sample_ids(self):
        sample_ids = []
        for sample in self:
            sample_ids.append(sample.ID)
        return sample_ids

    def get_nucleotide_sequences_df(self, clonotype_index=None):
        nucleotide_sequences = self.get_nucleotide_sequences(clonotype_index=clonotype_index)
        return DataFrame(nucleotide_sequences)

    def exclude_on_experiment_types(self, experiment_types=[]):
        return self.exclude_from_list(SampleCriteriaParameters([(SampleCriteriaCategories.experiment_type, experiment_types)]))

    def get_bool_and(self, request_criterion_params, sample_criterion_params):
        list_bool = []
        if len(request_criterion_params) > 0:
            for request_param in request_criterion_params:
                if request_param in sample_criterion_params:
                    list_bool.append(True)
                else:
                    list_bool.append(False)
            if all(list_bool):
                #print('in: ', [request_criterion_params, sample_criterion_params])
                return True
            return False

        return True

    def get_bool_or(self, request_criterion_params, sample_criterion_params):
        if len(request_criterion_params) > 0:
            for request_param in request_criterion_params:
                if request_param in sample_criterion_params:
                    return True
            return False
        return True

    def get_bool_for_exclusion(self, request_criteria, sample_criteria):
        list_bool = []
        if len(request_criteria) > 0:
            for request_criterion in request_criteria:
                if request_criterion in sample_criteria:
                    list_bool.append(True)
                else:
                    list_bool.append(False)
            if all(list_bool):
                return True
            return False
        return False

    def get_from_list(self, criteria, selection='and'):
        selected_sps = []
        for sample in self:
            booleans = []

            # print("criteria: ", criteria)

            for criterion in criteria.keys():
                if (type(criteria[criterion]) != list) or (type(sample.sample_criteria[criterion]) != list):
                    raise ValueError("Criterion should be a list.")

                if len(criteria[criterion]) > 0:
                    #print('criterion: ', criterion.name)
                    #print('sample.sample_criteria[criterion]: ', sample.sample_criteria[criterion])

                    # print("requested: ",criteria[criterion])
                    # #
                    # print("in sample: ",sample.sample_criteria[criterion])

                    if selection == 'and':
                        #print('comparison: ',[criterion.name, criteria[criterion], sample.sample_criteria[criterion]] )
                        booleans.append(self.get_bool_and(criteria[criterion], sample.sample_criteria[criterion]))
                        #print('booleans: ',booleans )
                    if selection == 'or':
                        booleans.append(self.get_bool_or(criteria[criterion], sample.sample_criteria[criterion]))
                    # if criterion.name == 'subject_id':
                    #     print('subjects: ', [criteria[criterion], sample.sample_criteria[criterion]])
                    #     print('bool: ', booleans)

            if selection == 'and':
                if all(booleans):
                    selected_sps.append(sample)
            if selection == 'or':
                if any(booleans):
                    selected_sps.append(sample)

        if len(selected_sps) > 0:
            return ClonotypeSamples(samples=selected_sps)
        #print('selected list of samples: ', selected_sps.get_sample_ids())
        return None

    def exclude_from_list(self, criteria, selection='and'):
        selected_sps = ClonotypeSamples()
        for sample in self:
            booleans = []
            for criterion in criteria.keys():
                booleans.append(self.get_bool_for_exclusion(criteria[criterion], sample.sample_criteria[criterion]))

            if not any(booleans):
                selected_sps.append(sample)

        if len(selected_sps) > 0:
            selected_sps = ClonotypeSamples(samples=selected_sps)
        return selected_sps

    def initialise_label(self):
        for sample in self:
            for criterion in self.sample_criteria:
                self.sample_criteria[criterion].extend(sample.sample_criteria[criterion])
        for criterion in self.sample_criteria:
            # print(criterion.value)
            # print('criteria: ', self.sample_criteria[criterion])
            self.sample_criteria[criterion] = list(set(self.sample_criteria[criterion]))

    def build_samples(self, comparisonDataSet):
        start, end = comparisonDataSet.data_source.get_limits('estimatedNumberGenomes|cell_count|Read.count')
        # print("start, end",[start, end])
        columns = comparisonDataSet.data_source.dataframe.columns.values[start:end]
        print('build sample columns: ', columns)
        for i in range(len(columns)):
            print(columns[i])
            # if
            sample = ClonotypeSample(columns[i], comparisonDataSet)
            if len(sample.clonotype_ids) > 0:
                self.append(sample)
            else:
                print('Sample [' + sample.ID +'] has not been added because it has no clonotypes')

    def get_nucleotide_sequences(self, clonotype_index=None):
        if clonotype_index is not None:
            return self.clonotype_sequence_infos.get_nucleotide_sequences(clonotype_index)
        clonotype_index = self.get_clonotype_indexes()

        # print('clonotype_index: ', clonotype_index)

        return self.clonotype_sequence_infos.get_nucleotide_sequences(clonotype_index)

    def get_total_cell_count_for_aa_clonotype_ids(self, aa_clonotype_ids):
        list_of_cell_counts = []
        for sample in self:
            counts=sample.get_cell_counts_by_aa_clonotype_ids(aa_clonotype_ids)
            # print(counts)
            if counts is not None:
                counts=counts.astype(int)

                list_of_cell_counts.append(sum(counts))
        return sum(list_of_cell_counts)

    def get_cell_counts_df(self, clonotype_ids=None):
        if (clonotype_ids is None):
            list_of_cell_counts = []

            for sample in self:
                list_of_cell_counts.append(sample.get_cell_counts_clonotype_index())

            df = concat(list_of_cell_counts, axis=1)
            df.columns = [x + '_cell_count' for x in self.get_sample_ids()]
            df = df.fillna(0)
            #df.index = self.get_nucleotide_sequences()
        else:
            list_of_cell_counts = []
            for sample in self:
                #print(sample)
                list_of_cell_counts.append(sample.get_cell_counts_clonotype_index(clonotype_ids))
            df = concat(list_of_cell_counts, axis=1)
            df.columns = [x + '_cell_count' for x in self.get_sample_ids()]
            df = df.fillna(0)
            #df.index = self.get_nucleotide_sequences(clonotype_ids=clonotype_ids)
        return df

    def assign_subject_clonotype_ids(self):
        for subject_id in self.get_subject_ids():
            samples = self.get_samples_by_subject_ids([subject_id])
            clonotype_ids_to_assign = samples.get_clonotype_ids()
            for sample in samples:
                sample.subject_clonotype_ids = clonotype_ids_to_assign

    def extend(self, samples):
        if not isinstance(samples, ClonotypeSamples):
            print('item is not of type %s' % ClonotypeSamples)
        super(ClonotypeSamples, self).extend(samples)  #append the item to itself (the list)
        self.sample_criteria = SampleCriteriaParameters()
        if self.clonotype_sequence_infos is None:
            self.clonotype_sequence_infos = samples.clonotype_sequence_infos
        if samples.clonotype_sequence_infos is None:
            print( 'Samples ' + str(samples) + ' have not been correctly instantiated')
        self.initialise_label()

    def append(self, sample):
        if not isinstance(sample, ClonotypeSample):
            print( 'item is not of type %s' % ClonotypeSample)

        super(ClonotypeSamples, self).append(sample)  #append the item to itself (the list)
        self.sample_criteria = SampleCriteriaParameters()

        if self.clonotype_sequence_infos is None:
            self.clonotype_sequence_infos = sample.data_source
        if sample.data_source is None:
            print('Sample ' + str(sample) + ' has not been correctly instantiated')
        self.initialise_label()


    def __str__(self):
        string = str(self.ID.__repr__() + ':')
        list_of_samples = []
        for k in self:
            list_of_samples.append(k)
        string = string + str(list_of_samples)
        return string

    def __repr__(self):
        return self.__str__()

    def get_nt_clonotypesList(self):
        clonotypes_list = ClonotypesList()
        for sample in self:
            clonotypes_list.append(sample.nt_clonotypes)
        return clonotypes_list

    def get_total_cells_per_clonotypes(self, clonotype_ids=None, clonotype_level=None):
        return self.get_aa_clonotypesList().get_total_cells_per_clonotypes(clonotype_ids=clonotype_ids, clonotype_level=clonotype_level)

    def get_aa_clonotypesList(self):
        clonotypes_list = ClonotypesList()
        for sample in self:
            clonotypes_list.append(sample.aa_clonotypes)
        return clonotypes_list

    def get_expanded_aa_clonotypesList_with_sample_a_specific_threshold(self, threshold, sample_ids=[]):
        clonotypes_list = ClonotypesList()
        for sample in self:
            # print("sample.ID: ", sample.ID)
            if len(sample_ids) > 0:
                if sample.ID in sample_ids:
                    clonotypes_list.append(sample.get_expanded_aa_clonotypes(threshold=threshold))
            else:
                clonotypes_list.append(sample.get_expanded_aa_clonotypes(threshold=threshold))

        # print("get_expanded_aa_clonotypesList_with_sample_specific_threshold: clonotypes_list: ", clonotypes_list)

        return clonotypes_list

    def get_expanded_aa_clonotypesList_with_sample_specific_threshold(self, threshold_dict, sample_ids=[]):
        clonotypes_list = ClonotypesList()
        for sample in self:
            # print("sample.ID: ", sample.ID)
            if len(sample_ids) > 0:
                if sample.ID in sample_ids:
                    threshold = threshold_dict[sample.ID]
                    clonotypes_list.append(sample.get_expanded_aa_clonotypes(threshold=threshold))
            else:
                threshold = threshold_dict[sample.ID]
                clonotypes_list.append(sample.get_expanded_aa_clonotypes(threshold=threshold))

        # print("get_expanded_aa_clonotypesList_with_sample_specific_threshold: clonotypes_list: ", clonotypes_list)

        return clonotypes_list

    def get_expanded_nt_clonotypesList_with_sample_specific_threshold(self, threshold_dict, sample_ids=[]):
        clonotypes_list = ClonotypesList()
        for sample in self:
            # print("sample.ID: ", sample.ID)
            if len(sample_ids) > 0:
                if sample.ID in sample_ids:
                    threshold = threshold_dict[sample.ID]
                    clonotypes_list.append(sample.get_expanded_nt_clonotypes(threshold=threshold))
            else:
                threshold = threshold_dict[sample.ID]
                clonotypes_list.append(sample.get_expanded_nt_clonotypes(threshold=threshold))
        return clonotypes_list

    def get_expanded_aa_clonotypesList(self,threshold=0.001):
        clonotypes_list = ClonotypesList()
        for sample in self:
            clonotypes_list.append(sample.get_expanded_aa_clonotypes(threshold=threshold))
        return clonotypes_list

    def get_samples_by_subject_ids_list(self):
        mysamples=[]
        for subject_id in self.get_subject_ids():
            mysamples.append(self.get_samples_by_subject_ids([subject_id]))

        return mysamples

    def get_samples_by_subject_ids(self, subject_id):
         criteria = SampleCriteriaParameters([(SampleCriteriaCategories.subject_id, subject_id)])
         return self.get_from_list(criteria)

    def get_samples_by_ids(self, sample_ids):
         criteria = SampleCriteriaParameters([(SampleCriteriaCategories.sequencing_ID, sample_ids)])
         return self.get_from_list(criteria)

    def get_samples_by_traits(self, traits, selection="and"):
         criteria = SampleCriteriaParameters([(SampleCriteriaCategories.trait, traits)])
         return self.get_from_list(criteria, selection=selection)

    def get_samples_by_experiment_types(self, experiment_types, selection="and"):
        criteria = SampleCriteriaParameters([(SampleCriteriaCategories.experiment_type, experiment_types)])
        return self.get_from_list(criteria, selection=selection)

    def get_samples_by_cell_types(self, cell_types, selection="and"):
        criteria = SampleCriteriaParameters([(SampleCriteriaCategories.cell_type, cell_types)])
        return self.get_from_list(criteria, selection=selection)

    def get_samples_by_peptide_sequences(self, peptide_sequences, selection="and"):
        criteria = SampleCriteriaParameters([(SampleCriteriaCategories.peptide_sequence, peptide_sequences)])
        return self.get_from_list(criteria, selection=selection)

    def get_samples_by_time_points(self, time_points, selection="and"):
        criteria = SampleCriteriaParameters([(SampleCriteriaCategories.time_point, time_points)])
        return self.get_from_list(criteria, selection=selection)

    def get_peptide_sequences(self):
        peptides = self.sample_criteria[SampleCriteriaCategories.peptide_sequence]
        if len(peptides) > 0:
            return [x for x in peptides if x != 'no']
        return None

    def get_negctrls(self, irrelevant_peptide_sequence):
        parameters={}
        parameters['experiment']="medium culture"
        mediums=self.select(parameters)
        parameters={}
        parameters['peptide_sequence']=irrelevant_peptide_sequence
        parameters['experiment']="peptide culture"
        parameters['experiment_type_excluded']="tetramer stain"
        irrelevant_pepstim=self.select(parameters)
        return mediums.extend(irrelevant_pepstim)

    def get_peptide_stimulated(self, peptide_sequence, total_cell_count_before_culture=None, experiment_type_excluded=None):
        parameters={}
        parameters['peptide_sequence']=peptide_sequence
        parameters['experiment']=['peptide culture']

        if total_cell_count_before_culture is not None:
            parameters['total cell count before culture'] = total_cell_count_before_culture
        if experiment_type_excluded is not None:
            parameters['experiment_type_excluded']=experiment_type_excluded
        return self.select(parameters)

    def select(self, parameters):
        print("select parameters:", parameters)
        # print("samples: ",self.get_sample_ids())
        samples = ClonotypeSamples(samples=self)
        if 'subject_ids' in parameters.keys():
            samples = samples.get_samples_by_subject_ids(parameters['subject_ids'])

        # print(samples)

        if 'traits' in parameters.keys():
            samples = samples.get_samples_by_traits(parameters['traits'], selection="or")
        if 'data_sequenced' in parameters.keys():
            samples = samples.get_samples_by_data_sequenced(parameters['data_sequenced'])
        if 'peptide_sequence' in parameters.keys():
            samples = samples.get_samples_by_peptide_sequences(parameters['peptide_sequence'])
        if 'sequencing_level' in parameters.keys():
            samples = samples.get_samples_by_sequencing_level(parameters['sequencing_level'])
        if 'total_cell_count_before_culture' in parameters.keys():
            samples = samples.get_samples_by_total_cell_count_before_culture(parameters['total_cell_count_before_culture'])
        if 'repeat_ID' in parameters.keys():
            samples = samples.get_samples_by_repeat_ID(parameters['repeat_ID'])
        if 'experiment' in parameters.keys():
            samples = samples.get_samples_by_experiment_types(parameters['experiment'])

        if 'experiment_type_excluded' in parameters.keys():
            experiment_type_excluded = parameters['experiment_type_excluded']
            for to_exclude in experiment_type_excluded:
                samples = samples.exclude_on_experiment_types([to_exclude])
        # print("samples: ", samples)
        samples.comparisonDataSet = self.comparisonDataSet
        return samples

    def get_info_on_samples_df(self, columns_to_extract=None):
        return self.comparisonDataSet.samples_info_file.get_info_on_samples(self.get_sample_ids(), columns_to_extract)

    def get_sequences_info_df(self, sample_ids=None, clonotype_ids=None, excluded_col_info=None):
        if sample_ids is None:
            sample_ids = self.get_sample_ids()
        if clonotype_ids is None:
            clonotype_ids = self.get_clonotype_ids()
        return self.comparisonDataSet.data_source.get_info(sample_ids=sample_ids, clonotype_ids=clonotype_ids, excluded_col_info=excluded_col_info)

    def get_samples_by_data_sequenced(self, data_sequenced):
         criteria = SampleCriteriaParameters([(SampleCriteriaCategories.data_sequenced, data_sequenced)])
         return self.get_from_list(criteria)

    def get_subject_ids(self):
        return self.sample_criteria[SampleCriteriaCategories.subject_id]

    def get_sample_ids(self):
        sample_ids = []
        for sample in self:
            sample_ids.append(sample.ID)
        return sample_ids

    def get_experiment_types(self):
        return self.sample_criteria[SampleCriteriaCategories.experiment_type]

    def get_total_clonotype_count_per_clonotypes(self, clonotype_level="nucleotide"):
        mylist = []
        if clonotype_level == "nucleotide":
            clonotypeslist = self.get_nt_clonotypesList_with_min_cells(1)
        else:
            clonotypeslist = self.get_aa_clonotypesList_with_min_cells(1)

        for clonotypes in clonotypeslist:
            if isinstance(clonotypes, NucleotideClonotypes):
                mylist.append(len(clonotypes.clonotype_index))
            else:
                mylist.append(len(clonotypes.aa_clonotype_ids))

        return mylist

    def get_traits(self):
        return self.sample_criteria[SampleCriteriaCategories.trait]

    def get_exvivo(self):
        criteria = SampleCriteriaParameters([(SampleCriteriaCategories.experiment_type,['exvivo'])])
        return self.get_from_list(criteria)

    def get_nt_clonotype_ids_with_min_cells_in_all_samples(self, number):
        clonotypes_list = ClonotypesList()
        for sample in self:
            nt_clonotypes = sample.get_nt_clonotypes_with_min_cells(number)
            if nt_clonotypes is not None:
                clonotypes_list.append(nt_clonotypes)
        return clonotypes_list.get_nt_shared_clonotypes().clonotype_index

    def get_aa_clonotype_ids_with_min_cells_in_all_samples(self, number):
        clonotypes_list = ClonotypesList()
        for sample in self:
            aa_clonotypes = sample.get_aa_clonotypes_with_min_cells(number)
            if aa_clonotypes is not None:
                clonotypes_list.append(aa_clonotypes)
        return clonotypes_list.get_aa_shared_clonotypes().aa_clonotype_ids

    def get_aa_clonotype_ids_with_cells_in_all_samples_equal_to(self, number):
        clonotypes_list = ClonotypesList()
        for sample in self:
            aa_clonotypes = sample.get_aa_clonotypes_with_cells_equal_to(number)
            if aa_clonotypes is not None:
                clonotypes_list.append(aa_clonotypes)

        # print('clonotypes_list: ', clonotypes_list)

        return clonotypes_list.get_aa_shared_clonotypes().aa_clonotype_ids

    def get_nt_clonotype_ids_with_cells_in_all_samples_equal_to(self, number):
        clonotypes_list = ClonotypesList()
        for sample in self:
            nt_clonotypes = sample.get_nt_clonotypes_with_cells_equal_to(number)
            if nt_clonotypes is not None:
                clonotypes_list.append(nt_clonotypes)

        return clonotypes_list.get_nt_shared_clonotypes().clonotype_index

    def get_clonotypesList_with_cells_in_all_samples_equal_to(self, number):
        clonotypes_list = ClonotypesList()
        for sample in self:
            clonotypes = sample.get_clonotypes_with_cells_in_all_samples_equal_to(number)
            if clonotypes is not None:
                clonotypes_list.append(clonotypes)
        return clonotypes_list

    def get_nt_clonotypesList_with_min_cells(self, threshold):
        clonotypes_list = ClonotypesList()
        for sample in self:
            clonotypes = sample.get_nt_clonotypes_with_min_cells(threshold)
            if clonotypes is not None:
                clonotypes_list.append(clonotypes)
        return clonotypes_list

    def get_aa_clonotypesList(self):
        clonotypes_list = ClonotypesList()
        for sample in self:
            # print("sample ID: ", sample.ID)
            aa_clonotypes = sample.aa_clonotypes
            if aa_clonotypes is not None:
                clonotypes_list.append(aa_clonotypes)
        return clonotypes_list

    def get_aa_clonotypesList_with_min_cells(self, threshold):
        clonotypes_list = ClonotypesList()
        for sample in self:
            # print("sample ID: ", sample.ID)
            aa_clonotypes = sample.get_aa_clonotypes_with_min_cells(threshold)
            if aa_clonotypes is not None:
                clonotypes_list.append(aa_clonotypes)
        return clonotypes_list



    def get_aa_clonotypesList_with_pvalue_higher_equal_than(self, threshold=0.001):
        return self.get_aa_clonotypesList().get_aa_clonotypesList_with_pvalue_higher_equal_than(threshold=threshold)

    def get_aa_clonotypesList_with_pvalue_lower_than(self, threshold=0.001):
        return self.get_aa_clonotypesList().get_aa_clonotypesList_with_pvalue_lower_than(threshold=threshold)

    def get_clonotype_ids(self):
        samples_clonotype_ids= []
        for sample in self:
            samples_clonotype_ids.extend(sample.get_clonotype_ids())
        return list(set(samples_clonotype_ids))

    def get_clonotype_indexes(self):
        samples_clonotype_indexes= []
        for sample in self:
            samples_clonotype_indexes.extend(sample.clonotype_index)
        return list(set(samples_clonotype_indexes))

class Repeats(ClonotypeSamples):
    def __init__(self, samples=[], repeat_type='culture'):
        super(Repeats, self).__init__(samples=samples)
        if type(repeat_type) != str:
            raise
        self.repeat_type=repeat_type



