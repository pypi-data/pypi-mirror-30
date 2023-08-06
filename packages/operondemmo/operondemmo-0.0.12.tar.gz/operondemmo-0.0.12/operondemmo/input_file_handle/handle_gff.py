import numpy
import os
import re


def findall_pat(pat, content, result="list"):
    """
    :param result:
    :param pat: string
    :param content: string
    :return: list
    """
    pat = re.compile(pat)
    find = re.findall(pat, content)
    if result == "list":
        return find
    elif result == "one":
        if len(find) > 0:
            return find[0]
        else:
            print("NOT FOUND")
            return find
    else:
        print("usage:\nresult='list'(default)or'one")


def auto_download(kegg_id):
    print("waiting for coding...")
    download_path = ""
    return download_path


def compute_pos1(g_pos_list):
    start_pos = int(g_pos_list[0][0])
    stop_pos = int(g_pos_list[0][1])
    middle_pos = (start_pos + stop_pos) / 2
    return middle_pos


def compute_pos2(g_pos_list):
    start_pos = int(g_pos_list[0][0])
    stop_pos = int(g_pos_list[0][1])
    for item in g_pos_list[1:]:
        stop_pos = int(item[1]) - (int(item[0]) - stop_pos)
    middle_pos = (start_pos + stop_pos) / 2
    return middle_pos


def sorted_gene(gene_pos):
    name_gene = []
    middle_gene = []
    for key in gene_pos:
        name_gene.append(key)
        g_pos_list = gene_pos[key]
        if len(g_pos_list) == 1:
            middle_pos = compute_pos1(g_pos_list)
        else:
            middle_pos = compute_pos2(g_pos_list)
        middle_gene.append(middle_pos)
    name_gene = [name_gene for (middle_gene, name_gene) in sorted(zip(middle_gene, name_gene))]
    return name_gene


def co_expression_strand(gene_sort, gene_strand):
    list_gene_strand = []
    for item in gene_sort:
        list_gene_strand.append(gene_strand[item])
    return list_gene_strand


def matrix_strand_to_int(matrix_strand):
    matrix_strand[matrix_strand == "++"] = 22
    matrix_strand[matrix_strand == "+-"] = 21
    matrix_strand[matrix_strand == "-+"] = 12
    matrix_strand[matrix_strand == "--"] = 11
    matrix_strand[matrix_strand == " +"] = 92
    matrix_strand[matrix_strand == " -"] = 91
    matrix_strand[matrix_strand == "+ "] = 29
    matrix_strand[matrix_strand == "- "] = 19
    matrix_strand = matrix_strand.astype("int")
    return matrix_strand


def matrix_to_list_gene_strand(list_gene_strand):
    list_a = list_gene_strand.copy()
    list_a.insert(0, " ")
    a = numpy.array([list_a]).T
    list_b = list_gene_strand.copy()
    list_b.append(" ")
    b = numpy.array([list_b]).T
    matrix_strand = numpy.char.add(a, b)
    matrix_strand_int = matrix_strand_to_int(matrix_strand)
    list_strand_int = matrix_strand_int.T.tolist()[0]
    return list_strand_int


def get_list_gene_strand(gene_sort, gene_strand_dict):
    list_gene_strand = co_expression_strand(gene_sort, gene_strand_dict)
    list_gene_strand = matrix_to_list_gene_strand(list_gene_strand)
    return list_gene_strand


def gene_pos_dict_remove_error(gene_pos_dict):
    if "-" in gene_pos_dict:
        gene_pos_dict.pop("-")
        return gene_pos_dict
    else:
        return gene_pos_dict


def gene_strand_dict_remove_error(gene_strand_dict):
    if "-" in gene_strand_dict:
        gene_strand_dict.pop("-")
        return gene_strand_dict
    else:
        return gene_strand_dict


def get_gene_pos_strand(simple_gff_file):
    simple_gff_fp = open(simple_gff_file, 'r')
    gene_pos_dict = {}
    gene_strand_dict = {}
    while True:
        line = simple_gff_fp.readline().strip()
        if not line:
            break
        gene_information = line.split("\t")
        # print(gene_information)
        g_b_id = gene_information[0]
        g_start = int(gene_information[4])
        g_stop = int(gene_information[5])
        g_strand = gene_information[-1]
        if g_b_id not in gene_pos_dict:
            gene_pos_dict[g_b_id] = [(g_start, g_stop)]
        else:
            gene_pos_dict[g_b_id].append((g_start, g_stop))
        gene_strand_dict[g_b_id] = g_strand
    gene_pos_dict = gene_pos_dict_remove_error(gene_pos_dict)
    gene_strand_dict = gene_strand_dict_remove_error(gene_strand_dict)
    return gene_pos_dict, gene_strand_dict


def query_strand(num):
    if num == 2:
        return "+"
    elif num == 1:
        return "-"
    elif num == 9:
        return " "
    else:
        return ""


def partition_gene(gene_sorted, list_gene_strand):
    # print(list_gene_strand)
    gene_start = list_gene_strand[0]
    gene1_strand = gene_start % 10
    gene_index_matrix = [[0]]
    gene_strand_matrix = [[query_strand(gene1_strand)]]
    i = 0
    gene_num = len(list_gene_strand)
    # print(gene_num)
    j = 1
    while j < gene_num - 1:
        gene_j_strand = list_gene_strand[j] % 10
        if list_gene_strand[j] == (3 - gene1_strand) * 11:
            tmp_index = gene_index_matrix[i].pop()
            gene_index_matrix.append([tmp_index, j])
            tmp_strand = gene_strand_matrix[i].pop()
            gene_strand_matrix.append([tmp_strand, query_strand(gene_j_strand)])
            k = 2
            while list_gene_strand[j - k] != gene1_strand * 11:
                tmp_index_pre = gene_index_matrix[i][1-k]
                tmp_index_pre_pre = gene_index_matrix[i][0-k]
                gene_index_matrix[i + 1].insert(0, tmp_index_pre)
                gene_index_matrix[i + 1].insert(0, tmp_index_pre_pre)
                tmp_strand_pre = gene_strand_matrix[i][1-k]
                tmp_strand_pre_pre = gene_strand_matrix[i][0-k]
                gene_strand_matrix[i + 1].insert(0, tmp_strand_pre)
                gene_strand_matrix[i + 1].insert(0, tmp_strand_pre_pre)
                k = k + 2
            gene1_strand = 3 - gene1_strand
            i = i + 1
        else:
            gene_index_matrix[i].append(j)
            gene_strand_matrix[i].append(query_strand(gene_j_strand))
        j = j + 1
    sorted_gene_matrix = []
    for each_ in gene_index_matrix:
        sorted_gene_matrix.append([])
        for item in each_:
            sorted_gene_matrix[-1].append(gene_sorted[item])
    # print(len(sorted_gene_matrix))
    # print(len(gene_index_matrix))
    # print(len(gene_strand_matrix))
    # i = 0
    # for each_ in gene_strand_matrix:
    #     frv = each_.count("+")
    #     rev = each_.count("-")
    #     if frv > rev:
    #         if rev != 0:
    #             if i+1 < len(gene_strand_matrix) and i-1 >= 0:
    #                 print(gene_strand_matrix[i - 1], each_, gene_strand_matrix[i + 1])
    #                 print(gene_index_matrix[i-1],gene_index_matrix[i],gene_index_matrix[i+1])
    #                 print(sorted_gene_matrix[i-1], sorted_gene_matrix[i],sorted_gene_matrix[i+1])
    #     else:
    #         if frv != 0:
    #             if i + 1 < len(gene_strand_matrix) and i - 1 >= 0:
    #                 print(gene_strand_matrix[i - 1], each_, gene_strand_matrix[i + 1])
    #                 print(gene_index_matrix[i - 1], gene_index_matrix[i], gene_index_matrix[i + 1])
    #                 print(sorted_gene_matrix[i - 1], sorted_gene_matrix[i], sorted_gene_matrix[i + 1])
    #     i = i + 1
    # print(gene_strand_matrix)
    # print(gene_index_matrix)
    # print(sorted_gene_matrix)
    return gene_strand_matrix, gene_index_matrix, sorted_gene_matrix


def from_simple_gff_information_to_get(gene_pos_dict, gene_strand_dict):
    gene_sort = sorted_gene(gene_pos_dict)
    list_strand = get_list_gene_strand(gene_sort, gene_strand_dict)
    final_gene_strand, final_gene_index, final_gene_sort = partition_gene(gene_sort, list_strand)
    return final_gene_strand, final_gene_index, final_gene_sort


def get_annotation(gff_file):
    gff_fp = open(gff_file, "r")
    genes = []
    while True:
        line = gff_fp.readline().strip()
        if not line:
            break
        line_content = line.split("\t")
        if len(line_content) > 1:
            start_pos = int(line_content[3])
            stop_pos = int(line_content[4])
            annotation_dict = {}
            annotation_ls = line_content[-1].split(";")
            for ann in annotation_ls:
                split_ann = ann.split("=")
                key = split_ann[0]
                info = split_ann[1].split(",")
                annotation_dict[key] = info
            genes.append([(start_pos, stop_pos), annotation_dict])
        else:
            # print(line)
            pass
    gff_fp.close()
    return genes


def filter_genes(gff_file):
    genes = get_annotation(gff_file)
    i = 0
    curr_len = len(genes)
    tmp_need_del = []
    while i < curr_len:
        annotation = genes[i][1]
        if 'Parent' in annotation:
            # if 'locus_tag' in annotation:
            #     print(genes[i])
            record = i - 1
            gene_id = annotation['Parent']
            while record > 0:
                if genes[record][-1]['ID'] == gene_id:
                    if 'part' not in genes[record][-1]:
                        if genes[record][0] != genes[i][0]:
                            genes[record].insert(-1, genes[i][0])
                            tmp_need_del.append(genes[i])
                            # if 'pseudo' not in genes[record][-1]:
                            #     print(genes[record])  # only 'prfB' without keyword 'pesudo'
                        else:
                            tmp_need_del.append(genes[i])
                        record = 0
                    else:
                        tmp_need_del.append(genes[i])
                        record = 0
                else:
                    record = record - 1
        i = i + 1
    for tmp_del in tmp_need_del:
        genes.remove(tmp_del)
    return genes


def get_strand_dict(gff_file):
    gff_fp = open(gff_file, "r")
    strand_id_dict = {}
    while True:
        line = gff_fp.readline().strip()
        if not line:
            break
        line_content = line.split("\t")
        if len(line_content) > 1:
            _id = findall_pat("ID\=([A-Za-z0-9]+)\;", line_content[-1], "one")
            strand_id_dict[_id] = line_content[6]
        else:
            pass
    gff_fp.close()
    return strand_id_dict


def generate_simple_gff(gff_file, output_path):
    specie_name = gff_file.split("/")
    specie_name = specie_name[-1]
    tmp_path = output_path + "tmp/"
    if not os.path.exists(tmp_path):
        os.system("mkdir " + tmp_path)
    simple_gff_path = tmp_path + "simple_" + specie_name
    genes = filter_genes(gff_file)
    simple_gff_fp = open(simple_gff_path, 'w')
    for gene in genes:
        if 'locus_tag' not in gene[-1]:
            pass
            # print(gene)  # always with one (start, stop)
            # if 'gbkey' not in gene[-1]:
            #     print(gene)  # NONE
            # start = gene[0][0]
            # stop = gene[0][1]
            # _id = gene[1]['ID'][0]
            # gb_key = gene[1]['gbkey'][0]
            # simple_gff_fp.write("-\t-\t-\t-\t" + str(start) + "\t" + str(stop) + "\t" + _id + "\t" + gb_key + "\n")
        else:
            if len(gene) == 2:
                start = gene[0][0]
                stop = gene[0][1]
                _id = gene[1]['ID'][0]
                gb_key = gene[1]['gbkey'][0]
                locus_tag = gene[1]['locus_tag'][0]
                symbol = gene[1]['gene'][0]
                synonym = ";".join(gene[1]['gene_synonym'])
                if 'part' in gene[1]:
                    part = gene[1]['part'][0]
                    part_i = part.split("/")[0]
                    for gene_syn in gene[-1]['gene_synonym']:
                        gene_syn = gene_syn + "_" + part_i
                        synonym = synonym + ";" + gene_syn
                    synonym = synonym + ";" + symbol + "_" + part_i
                    simple_gff_fp.write(locus_tag + "\t" + symbol + "\t" + synonym + "\t" + part + "\t"
                                        + str(start) + "\t" + str(stop) + "\t" + _id + "\t" + gb_key + "\n")
                else:
                    simple_gff_fp.write(locus_tag + "\t" + symbol + "\t" + synonym + "\t" + "-" + "\t"
                                        + str(start) + "\t" + str(stop) + "\t" + _id + "\t" + gb_key + "\n")
            else:
                # if 'pseudogene' not in gene[-1]['gene_biotype']:
                #     print(4, gene)  # prfB
                start = gene[0][0]
                stop = gene[0][1]
                _id = gene[-1]['ID'][0]
                gb_key = gene[-1]['gbkey'][0]
                locus_tag = gene[-1]['locus_tag'][0]
                symbol = gene[-1]['gene'][0]
                synonym = ";".join(gene[-1]['gene_synonym'])
                simple_gff_fp.write(locus_tag + "\t" + symbol + "\t" + synonym + "\t" + "-" + "\t"
                                    + str(start) + "\t" + str(stop) + "\t" + _id + "\t" + gb_key + "\n")
                j = 1
                while j < len(gene) - 1:
                    start = gene[j][0]
                    stop = gene[j][1]
                    _id = gene[-1]['ID'][0]
                    gb_key = gene[-1]['gbkey'][0]
                    locus_tag = gene[-1]['locus_tag'][0]
                    symbol = gene[-1]['gene'][0] + "_" + str(j)
                    synonym = ";".join(gene[-1]['gene_synonym'])
                    for gene_syn in gene[-1]['gene_synonym']:
                        gene_syn = gene_syn + "_" + str(j)
                        synonym = synonym + ";" + gene_syn
                    simple_gff_fp.write(locus_tag + "\t" + symbol + "\t" + synonym + "\t" + "-" + "\t"
                                        + str(start) + "\t" + str(stop) + "\t" + _id + "\t" + gb_key + "\n")
                    j = j + 1
    simple_gff_fp.close()
    strand_dict = get_strand_dict(gff_file)
    simple_fp = open(simple_gff_path, "r")
    write_fp = open(simple_gff_path + "_2", "w")
    while True:
        line = simple_fp.readline().strip()
        if not line:
            break
        line_content = line.split("\t")
        _id = line_content[6]
        if _id in strand_dict:
            write_fp.write(line + "\t" + strand_dict[_id] + "\n")
        else:
            print(_id)
            write_fp.write(line + "\t-\n")
    write_fp.close()
    simple_fp.close()
    os.system("rm -f " + simple_gff_path)
    os.system("mv " + simple_gff_path + "_2 " + simple_gff_path)
    return simple_gff_path


if __name__ == "__main__":
    test_gff_path = "/home/lyd/document/2018.1/gamma_domain/simple_eco.gff_3"
    test_gene_pos, test_gene_strand = get_gene_pos_strand(test_gff_path)
    _gene_strand, _gene_index, _gene_sort = \
        from_simple_gff_information_to_get(test_gene_pos, test_gene_strand)

    # test get_list_gene_strand()
    a = ["+", "-", "-"]
    d = matrix_to_list_gene_strand(a)
    print(d)
