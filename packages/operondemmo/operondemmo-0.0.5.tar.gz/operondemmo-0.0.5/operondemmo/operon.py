import datetime
import sys
import argparse

import os

import numpy

from operondemmo.co_expression_matrix.c_i_j import compute_co_expression_by_c_i_j
from operondemmo.co_expression_matrix.person_i_j import compute_co_expression_by_person
from operondemmo.co_expression_matrix.spearman_i_j import compute_co_expression_by_spearman
from operondemmo.hierarchical_cluster.gamma_domain import get_result_by_clustering, get_result_by_clustering2
from operondemmo.input_file_handle.handle_gff import auto_download, generate_simple_gff, \
    get_gene_pos_strand, from_simple_gff_information_to_get, sorted_gene
from operondemmo.version import version

self_version = version

APP_VERSION = (
        '''
    ----------------------------------------------------------------------
    
    operondemmo-(%s) - an independent demo of KNOWN operon predict method
    
    ----------------------------------------------------------------------
    ''' % self_version
)


def main():
    starting(prepare(sys.argv))


def prepare(argv):
    parser = argparse.ArgumentParser(description=APP_VERSION,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    advanced_argv = parser.add_argument_group("ADVANCED OPTIONS")
    parser.add_argument("-i", action="store", dest="input_files", default="null",
                        help="A directory to store a group of result files "
                             "through [samtools depth XXX > xxx.txt] command")
    parser.add_argument("-o", action="store", dest="output_path", default="OUT",
                        help="A directory include output data(operon file).default:OUT")
    parser.add_argument("-g", action="store", dest="gff_file", default="null",
                        help="The gff file of the prokaryote")
    parser.add_argument("-p", action="store", dest="process_thread", default=1, type=int,
                        help="Specify the number of processing threads (CPUs).default:1")
    parser.add_argument("-t", action="store", dest="threshold", default=0.6, type=int,
                        help="the threshold in (-1,1)")
    advanced_argv.add_argument("-k", action="store", dest="kegg_id", default="null",
                               help="The kegg id of the prokaryote")
    advanced_argv.add_argument("--auto_gff", action="store_true", dest="auto_gff", default=False,
                               help="Auto download gff_file from NCBI Database")
    advanced_argv.add_argument("--person", action="store_true", dest="person", default=False,
                               help="Build co-expression matrix with person correlation")
    advanced_argv.add_argument("--spearman", action="store_true", dest="spearman", default=False,
                               help="Build co-expression matrix with spearman correlation")
    advanced_argv.add_argument("-v", "--version", action="version", version="operondemmo-" + self_version)
    if len(argv) == 1:
        print(parser.print_help())
        sys.exit(0)
    else:
        args = parser.parse_args(argv[1:])
        return args


def starting(args):
    """

    :type args: parser.parse_args()
    """
    if args.auto_gff:
        if args.kegg_id != "null":
            gff_file_path = auto_download(args.kegg_id)
        else:
            print("NEEDED KEGG ID.PLEASE check your input with option '-k'")
            return
    else:
        if args.gff_file != "null":
            gff_file_path = args.gff_file
        else:
            print("NEEDED GFF_FILE.PLEASE check your input with option '-g'")
            return
    if args.person:
        co_expression_method = 1
    else:
        if args.spearman:
            co_expression_method = 2
        else:
            co_expression_method = 0
    if args.input_files != "null":
        depth_files = load_from_input_files(args.input_files)
        check_input_file(depth_files)
    else:
        print("NEEDED INPUT_FILES.PLEASE check your input with option '-i'")
        return
    if args.threshold > 1 or args.threshold < -1:
        print("IT CANNOT BE:", args.threshold, "PLEASE check your input with option '-t'")
        return
    if args.output_path[-1] != "/":
        output_path = args.output_path + "/"
    else:
        output_path = args.output_path
    if not os.path.exists(output_path):
        os.system("mkdir " + output_path)
    operon_predict(args.threshold, depth_files, output_path, gff_file_path, args.process_thread,
                   co_expression_method)


def operon_predict(threshold, depth_files, output_path, gff_file_path, p, co_expression_method):
    # simple_gff_file_information
    print("from your gff file to get [gene_locus_tag, start, stop, strand]...")
    simple_gff_path = generate_simple_gff(gff_file_path, output_path)
    gene_pos_dict, gene_strand_dict = get_gene_pos_strand(simple_gff_path)
    final_gene_strand, final_gene_index, final_gene_sort = \
        from_simple_gff_information_to_get(gene_pos_dict, gene_strand_dict)
    print("done\nfrom your samtools_depth result files to get tpm_co_expression_matrix...\n"
          "it would be cost few minutes, please waiting...")
    # matrix_co_expression
    matrix_i_j = from_depth_file_to_get_co_matrix_co_expression(depth_files, gene_pos_dict, co_expression_method)
    # numpy.savetxt(output_path + "matrix.txt", matrix_i_j, fmt="%.8f")
    print("done\ngamma_domain clustering...")
    # hierarchical_cluster
    result_file = output_path + "operon.txt"
    get_result_by_clustering2(result_file, final_gene_strand, final_gene_index, final_gene_sort, matrix_i_j, threshold)
    print("done")
    print("PLEASE open your output_path:", result_file)


def read_depth_file(depth_file):
    file_content = open(depth_file, 'r').read().strip()
    content_list = file_content.split("\n")
    count_list = []
    for line in content_list:
        tmp_content = line.split("\t")
        count_list.append(tmp_content[-1])
    # print(len(count_list))
    return count_list


def compute_tpm(matrix_a, gene_pos_dict):
    gene_sort = sorted_gene(gene_pos_dict)
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
    sum_genes_matrix = gene_count_matrix.sum(axis=0)
    average_genes_matrix = gene_count_matrix / sum_genes_matrix
    return average_genes_matrix


def compute_expression(depth_files, gene_pos_dict):
    matrix_a = []
    for each in depth_files:
        count_list = read_depth_file(each)
        matrix_a.append(count_list)
    matrix_tpm = compute_tpm(matrix_a, gene_pos_dict)
    return matrix_tpm


def from_depth_file_to_get_co_matrix_co_expression(depth_files, gene_pos_dict, method):
    begin = datetime.datetime.now()
    matrix_groups_by_condition = compute_expression(depth_files, gene_pos_dict)
    end = datetime.datetime.now()
    print("time: compute_tpm,", end - begin)
    if method == 0:
        begin = datetime.datetime.now()
        matrix_c_i_j = compute_co_expression_by_c_i_j(matrix_groups_by_condition)
        end = datetime.datetime.now()
        print("time: compute_co_expression_matrix,", end - begin)
        return matrix_c_i_j
    elif method == 1:
        begin = datetime.datetime.now()
        matrix_c_person = compute_co_expression_by_person(matrix_groups_by_condition)
        end = datetime.datetime.now()
        print("time: compute_co_expression_matrix,", end - begin)
        return matrix_c_person
    else:
        begin = datetime.datetime.now()
        matrix_c_spearman = compute_co_expression_by_spearman(matrix_groups_by_condition)
        end = datetime.datetime.now()
        print("time: compute_co_expression_matrix,", end - begin)
        return matrix_c_spearman


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


if __name__ == "__main__":
    main()
