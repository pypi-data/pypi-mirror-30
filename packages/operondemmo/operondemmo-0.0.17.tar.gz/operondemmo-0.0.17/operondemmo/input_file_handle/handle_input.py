import sys
import os
from multiprocessing import Pool
import numpy
import time


def check_input_file(depth_files):
    num_depth_files = len(depth_files)
    if num_depth_files <= 1:
        print("need more condition")
        sys.exit(1)


def load_from_input_files(input_files):
    depth_files = []
    for each_file in os.listdir(input_files):
        depth_files.append(input_files + each_file)
    return depth_files


def read_depth_file(depth_file):
    file_content = open(depth_file, 'r').read().strip()
    content_list = file_content.split("\n")
    count_list = []
    for line in content_list:
        tmp_content = line.split("\t")
        count_list.append(tmp_content[-1])
    # print(len(count_list))
    return count_list


def compute_tpm(matrix_a, gene_pos_dict, gene_sort):
    count_matrix = numpy.array(matrix_a).astype('int').T
    # print(count_matrix.shape[0],count_matrix.shape[1])
    condition_num = count_matrix.shape[1]
    i = 0
    for item in gene_sort:
        sum_count = numpy.zeros([1, condition_num])
        len_gene = 0
        for (start, stop) in gene_pos_dict[item]:
            len_gene = len_gene + stop - start + 1
            sum_count = sum_count + count_matrix[start - 1: stop, ...].sum(axis=0)
        average_count = sum_count / len_gene
        if i == 0:
            gene_count_matrix = average_count
        else:
            gene_count_matrix = numpy.row_stack((gene_count_matrix, average_count))
        i = i + 1
    sum_genes_matrix = gene_count_matrix.sum(axis=0)
    average_genes_matrix = gene_count_matrix / sum_genes_matrix
    return average_genes_matrix


def compute_average(matrix_a, gene_pos_dict, gene_sort):
    count_matrix = numpy.array(matrix_a).astype('int').T
    # print(count_matrix.shape[0],count_matrix.shape[1])
    condition_num = count_matrix.shape[1]
    i = 0
    for item in gene_sort:
        sum_count = numpy.zeros([1, condition_num])
        len_gene = 0
        for (start, stop) in gene_pos_dict[item]:
            len_gene = len_gene + stop - start
            sum_count = sum_count + count_matrix[start - 1: stop, ...].sum(axis=0)
        average_count = sum_count / len_gene
        if i == 0:
            gene_count_matrix = average_count
        else:
            gene_count_matrix = numpy.row_stack((gene_count_matrix, average_count))
        i = i + 1
    return gene_count_matrix


def compute_expression(depth_files, gene_pos_dict, gene_sort, p):
    start = time.time()
    pool = Pool(p)
    matrix_a = pool.map(read_depth_file, depth_files)
    pool.close()
    pool.join()
    # matrix_a = []
    # for each in depth_files:
    #     count_list = read_depth_file(each)
    #     matrix_a.append(count_list)
    matrix_tpm = compute_tpm(matrix_a, gene_pos_dict, gene_sort)
    end = time.time()
    print("time: compute tpm: %.2f" % (end - start))
    numpy.savetxt("/home/lyd/document/2018.1/gamma_domain/my_matrix.txt", matrix_tpm, fmt="%.8f")
    return matrix_tpm
