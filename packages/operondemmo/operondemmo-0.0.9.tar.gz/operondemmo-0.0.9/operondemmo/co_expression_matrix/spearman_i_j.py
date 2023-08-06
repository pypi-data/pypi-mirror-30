import numpy
import pandas


def get_person_by_condition(matrix_a):
    condition_num = matrix_a.shape[1]
    print("condition_num:", condition_num)
    gene_num = matrix_a.shape[0]
    print("gene_num:", gene_num)
    matrix_a_t = matrix_a.T
    matrix_a_t = pandas.DataFrame(matrix_a_t)
    matrix_a_spearman = numpy.array(matrix_a_t.corr('spearman'))
    return matrix_a_spearman


def compute_co_expression_by_spearman(matrix_a):
    matrix_condition_s_v = get_person_by_condition(matrix_a)
    return matrix_condition_s_v


if __name__ == "__main__":
    # test matrix_co_expression()
    c1 = [50, 33, 20, 19, 13]
    c2 = [51, 34, 21, 18, 12]
    c3 = [52, 35, 22, 17, 12]
    matrix_test = numpy.array([c1, c2, c3]).T
    print(compute_co_expression_by_spearman(matrix_test))
