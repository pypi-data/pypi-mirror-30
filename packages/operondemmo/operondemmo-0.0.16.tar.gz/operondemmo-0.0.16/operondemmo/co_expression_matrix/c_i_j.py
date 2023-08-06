import numpy


def get_co_expression_by_condition(matrix_a):
    condition_num = matrix_a.shape[1]
    print("condition_num:", condition_num)
    for i in range(condition_num):
        c_i_expression = matrix_a[..., i:i + 1].copy()
        c_minus_i = matrix_a - c_i_expression
        if i == 0:
            matrix_a_compair = c_minus_i
        else:
            matrix_a_compair = numpy.column_stack((matrix_a_compair, c_minus_i))
    matrix_a_compair[matrix_a_compair >= 0] = 1
    matrix_a_compair[matrix_a_compair < 0] = -1
    return matrix_a_compair


def get_co_expression_gene_i_with_j(matrix_condition_s_v):
    gene_num = matrix_condition_s_v.shape[0]
    print("gene_num:", gene_num)
    matrix_c_i_j = numpy.zeros([gene_num, gene_num])
    for j in range(gene_num - 1):
        s_v_j_expression = matrix_condition_s_v[0:1, ...]
        s_v_other_expression = numpy.delete(matrix_condition_s_v, 0, axis=0)
        matrix_condition_s_v = s_v_other_expression
        # print(s_v_j_expression, "\n")
        # print(s_v_other_expression, "\n")
        s_v_multiply_j = s_v_other_expression * s_v_j_expression
        # print(s_v_multiply_j, "\n")
        matrix_c_i_j_iter = j + 1
        # print(s_v_multiply_j.sum(axis=1), "\n")
        matrix_c_i_j[matrix_c_i_j_iter:, j] = s_v_multiply_j.sum(axis=1)
        # print(matrix_c_i_j, "\n")
    return matrix_c_i_j


def compute_co_expression_by_c_i_j(matrix_a):
    matrix_condition_s_v = get_co_expression_by_condition(matrix_a)
    matrix_c_i_j = get_co_expression_gene_i_with_j(matrix_condition_s_v)
    condition_num = matrix_a.shape[1]
    matrix_c_i_j = matrix_c_i_j /(condition_num * condition_num)
    matrix_t = matrix_c_i_j.T
    matrix_c_i_j_final = matrix_c_i_j + matrix_t
    return matrix_c_i_j_final


if __name__ == "__main__":
    # test matrix_co_expression()
    c1 = [50, 33, 20, 19, 13]
    c2 = [51, 34, 21, 18, 12]
    c3 = [52, 35, 22, 17, 12]
    matrix_test = numpy.array([c1, c2, c3]).T
    print(compute_co_expression_by_c_i_j(matrix_test))
