from multiprocessing import Pool

import numpy
import pandas


def get_spearman_by_condition_old(matrix_a):
    condition_num = matrix_a.shape[1]
    print("condition_num:", condition_num)
    gene_num = matrix_a.shape[0]
    print("gene_num:", gene_num)
    matrix_a_t = matrix_a.T
    matrix_a_t = pandas.DataFrame(matrix_a_t)
    matrix_a_spearman = numpy.array(matrix_a_t.corr('spearman'))
    return matrix_a_spearman


def compute_co_expression_by_spearman_old(matrix_a):
    matrix_condition_s_v = get_spearman_by_condition_old(matrix_a)
    return matrix_condition_s_v


def spearman_task(pd_matrix):
    pd_spearman = pd_matrix.corr('spearman')
    return pd_spearman[0][1]


def get_spearman_by_condition(matrix_a, p):
    condition_num = matrix_a.shape[1]
    print("condition_num:", condition_num)
    gene_num = matrix_a.shape[0]
    print("gene_num:", gene_num)
    list_g_i_g_i_plus_1 = []
    i = 1
    while i < gene_num:
        np_matrix = matrix_a[i - 1:i + 1].T
        pd_matrix = pandas.DataFrame(np_matrix)
        list_g_i_g_i_plus_1.append(pd_matrix)
        i = i + 1
    pool = Pool(p)
    list_a = pool.map(spearman_task, list_g_i_g_i_plus_1)
    matrix_spearman = numpy.diag(list_a, -1)
    matrix_spearman = numpy.nan_to_num(matrix_spearman)
    return matrix_spearman


def compute_co_expression_by_spearman(matrix_a, p):
    matrix_condition_s_v = get_spearman_by_condition(matrix_a, p)
    return matrix_condition_s_v


if __name__ == "__main__":
    # test matrix_co_expression()
    c1 = [50, 33, 20, 19, 13]
    c2 = [51, 34, 21, 18, 12]
    c3 = [52, 35, 22, 17, 12]
    matrix_test = numpy.array([c1, c2, c3]).T
    print(compute_co_expression_by_spearman(matrix_test, 1))
    print(compute_co_expression_by_spearman_old(matrix_test))
