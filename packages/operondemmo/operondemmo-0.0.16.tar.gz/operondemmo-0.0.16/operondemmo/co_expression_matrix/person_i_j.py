import numpy


def get_person_by_condition(matrix_a):
    condition_num = matrix_a.shape[1]
    print("condition_num:", condition_num)
    gene_num = matrix_a.shape[0]
    print("gene_num:", gene_num)
    matrix_a_person = numpy.corrcoef(matrix_a, rowvar=True)
    return matrix_a_person


def compute_co_expression_by_person(matrix_a):
    matrix_condition_s_v = get_person_by_condition(matrix_a)
    matrix_condition_s_v = numpy.nan_to_num(matrix_condition_s_v)
    return matrix_condition_s_v


if __name__ == "__main__":
    # test matrix_co_expression()
    c1 = [50, 33, 20, 19, 13]
    c2 = [51, 34, 21, 18, 12]
    c3 = [52, 35, 22, 17, 12]
    matrix_test = numpy.array([c1, c2, c3]).T
    print(compute_co_expression_by_person(matrix_test))
