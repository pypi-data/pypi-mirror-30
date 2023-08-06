import numpy


def get_operon_prior(sort_gene, gene_strand):
    number_direction = 0
    number_pair = 0
    pre_strand = "?"
    current_direction_len = 1
    i = 0
    while i < len(sort_gene):
        current_strand = gene_strand[sort_gene[i]]
        if current_strand != pre_strand and current_direction_len > 1:
            number_direction = number_direction + 1
            pre_strand = current_strand
            current_direction_len = 1
        elif current_strand != pre_strand and current_direction_len == 1:
            pre_strand = current_strand
            current_direction_len = 1
        elif current_strand == pre_strand and current_direction_len > 1:
            number_pair = number_pair + 1
            pre_strand = current_strand
            current_direction_len = current_direction_len + 1
        elif current_strand == pre_strand and current_direction_len == 1:
            number_pair = number_pair + 1
            pre_strand = current_strand
            current_direction_len = current_direction_len + 1
        else:
            pass
        i = i + 1
    if current_direction_len > 1:
        number_direction = number_direction + 1
    operon_prior = 1 - number_direction / number_pair
    non_operon_prior = 1 - operon_prior
    return operon_prior, non_operon_prior


def kernel_function(bandwidth, bin_size, samples, x_min, x_max):
    estimation_y = []
    estimation_x = []
    i = x_min
    while i <= x_max:
        _sum = 0
        for j in samples:
            if abs(i - j) <= bandwidth:
                tmp = (i - j) / bandwidth
                _sum = _sum + tmp * tmp
        value = _sum / (len(samples) * bandwidth)
        estimation_x.append(i)
        estimation_y.append(value)
        i = i + bin_size
    return estimation_x, estimation_y


def get_gene_pos_list(gene_pos, sort_gene):
    gene_pos_list = []
    for key in sort_gene:
        for (start, stop) in gene_pos[key]:
            gene_pos_list.append((key, (start, stop)))
    gene_pos_list = sorted(gene_pos_list, key=lambda x: x[1][0])
    return gene_pos_list


def get_distance_distribution(gene_pos, gene_strand, sort_gene):
    gene_pos_list = get_gene_pos_list(gene_pos, sort_gene)
    i = 1
    same_direction = []
    opposite_direction = []
    while i < len(gene_pos_list):
        length = gene_pos_list[i][1][0] - gene_pos_list[i - 1][1][1]
        if gene_strand[gene_pos_list[i][0]] == gene_strand[gene_pos_list[i - 1][0]]:
            same_direction.append(length)
        else:
            opposite_direction.append(length)
        i = i + 1
    return same_direction, opposite_direction


def get_co_expression_distribution(matrix_a, gene_strand, sort_gene):
    i = 1
    same_corr = []
    opposite_corr = []
    while i < len(sort_gene):
        tmp_corr = matrix_a[i - 1][i]
        int_corr = int(tmp_corr * 20)
        if gene_strand[sort_gene[i - 1]] == gene_strand[sort_gene[i]]:
            same_corr.append(int_corr)
        else:
            opposite_corr.append(int_corr)
        i = i + 1
    return same_corr, opposite_corr


def compute_probability(x_list, f_x_list):
    i = 1
    p_x_list = []
    x_list.pop()
    while i < len(f_x_list):
        p_x_list.append((f_x_list[i - 1] + f_x_list[i]) / 2)
        i = i + 1
    return x_list, f_x_list


def get_probability(gene_pos, gene_strand, sort_gene, matrix_a):
    same_direction, opposite_direction = get_distance_distribution(gene_pos, gene_strand, sort_gene)
    same_corr, opposite_corr = get_co_expression_distribution(matrix_a, gene_strand, sort_gene)

    distance_x, distance_y = kernel_function(30, 1, same_direction, -50, 201)
    p_d_x, p_d_y = compute_probability(distance_x, distance_y)
    op_distance_x, op_distance_y = kernel_function(30, 1, opposite_direction,
                                                   min(opposite_direction), max(opposite_direction) + 1)
    p_op_d_x, p_op_d_y = compute_probability(op_distance_x, op_distance_y)

    co_x, co_y = kernel_function(5, 1, same_corr, -20, 21)
    p_co_x, p_co_y = compute_probability(co_x, co_y)
    op_co_x, op_co_y = kernel_function(5, 1, opposite_corr, -20, 21)
    p_op_co_x, p_op_co_y = compute_probability(op_co_x, op_co_y)
    print(max(p_d_y), max(p_op_d_y))
    print(max(p_co_y), max(p_op_co_y))
    return (p_d_x, p_d_y), (p_op_d_x, p_op_d_y), (p_co_x, p_co_y), (p_op_co_x, p_op_co_y)


def naive_bayes_classify(distance_i_j, co_i_j,
                         p_d_x, p_d_y, p_op_d_x, p_op_d_y, p_co_x, p_co_y, p_op_co_x, p_op_co_y,
                         operon_prior, non_operon_prior):
    if distance_i_j not in p_d_x:
        return False
    else:
        p_t = numpy.log(operon_prior) \
          + numpy.log(p_d_y[p_d_x.index(distance_i_j)]) + numpy.log(p_co_y[p_co_x.index(co_i_j)])
    p_f = numpy.log(non_operon_prior) \
          + numpy.log(p_op_d_y[p_op_d_x.index(distance_i_j)]) + numpy.log(p_op_co_y[p_op_co_x.index(co_i_j)])
    if p_t >= p_f:
        return True
    else:
        return False


def get_result_by_classifying(sort_gene, gene_strand, gene_pos, matrix_a, result_file, t1, t2):
    operon_prior, non_operon_prior = get_operon_prior(sort_gene, gene_strand)
    (p_d_x, p_d_y), (p_op_d_x, p_op_d_y), (p_co_x, p_co_y), (p_op_co_x, p_op_co_y) = \
        get_probability(gene_pos, gene_strand, sort_gene, matrix_a)
    result_file_fp = open(result_file, 'w')
    result_list = []
    gene_pos_list = get_gene_pos_list(gene_pos, sort_gene)
    i_iter = 1
    while i_iter < len(sort_gene):
        tmp_co_i_j = matrix_a[i_iter - 1][i_iter]
        co_i_j = int(tmp_co_i_j * 20)
        distance_i_j = gene_pos_list[i_iter][1][0] - gene_pos_list[i_iter - 1][1][1]
        tmp_result = naive_bayes_classify(distance_i_j, co_i_j,
                                          p_d_x, p_d_y, p_op_d_x, p_op_d_y, p_co_x, p_co_y, p_op_co_x, p_op_co_y,
                                          operon_prior, non_operon_prior)
        if tmp_result:
            if len(result_list) == 0:
                result_list.append(sort_gene[i_iter - 1] + ";" + sort_gene[i_iter])
            elif sort_gene[i_iter - 1] in result_list[-1]:
                result_list[-1] = result_list[-1] + ";" + sort_gene[i_iter]
            else:
                result_list.append(sort_gene[i_iter - 1] + ";" + sort_gene[i_iter])
        else:
            result_list.append(sort_gene[i_iter - 1])
            result_list.append(sort_gene[i_iter])
        i_iter = i_iter + 1
    for each_ in result_list:
        result_file_fp.write(each_ + "\n")
    result_file_fp.close()
