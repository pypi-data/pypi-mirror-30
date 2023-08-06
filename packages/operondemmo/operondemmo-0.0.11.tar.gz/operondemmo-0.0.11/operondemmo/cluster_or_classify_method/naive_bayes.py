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
    if current_direction_len > 1:
        number_direction = number_direction + 1
    operon_prior = 1 - number_direction / number_pair
    non_operon_prior = 1 - operon_prior
    return operon_prior, non_operon_prior


def kernel_function(bandwidth, bin_size, samples, x_min, x_max):
    estimation = {}
    i = x_min
    while i <= x_max:
        _sum = 0
        for j in samples:
            if abs(i - j) <= bandwidth:
                tmp = (i - j) / bandwidth
                _sum = _sum + tmp * tmp
        value = _sum / (len(samples) * bandwidth)
        estimation[i] = value
        i = i + bin_size
    return estimation


def get_distance_distribution(gene_pos, gene_strand):
    gene_pos_list = []
    for key in gene_pos:
        for (start, stop) in gene_pos[key]:
            gene_pos_list.append((key, (start, stop)))
    gene_pos_list = sorted(gene_pos_list, key=lambda x: x[1][0])
    i = 1
    same_direction = []
    opposite_direction = []
    while i < len(gene_pos_list):
        length = gene_pos_list[i][1][0] - gene_pos_list[i - 1][1][1]
        if gene_strand[gene_pos_list[i][0]] == gene_strand[gene_pos_list[i - 1][0]]:
            same_direction.append(length)
        else:
            opposite_direction.append(length)
    distance_distribution = kernel_function(30, 1, same_direction, -50, 200)
    return distance_distribution


def get_co_expression_distribution(matrix_a):
    co_expression_list = matrix_a.diagonal(-1).tolist()
    co_distribution = kernel_function(5, 1)
    return co_expression_list
