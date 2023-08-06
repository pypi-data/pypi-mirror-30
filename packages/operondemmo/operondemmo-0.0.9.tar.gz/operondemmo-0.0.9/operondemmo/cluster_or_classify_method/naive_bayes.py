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


