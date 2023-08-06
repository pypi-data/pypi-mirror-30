import time
import sys
import argparse

import os

from operondemmo.cluster_or_classify_method.naive_bayes import get_result_by_classifying
from operondemmo.co_expression_matrix.c_i_j import compute_co_expression_by_c_i_j
from operondemmo.co_expression_matrix.person_i_j import compute_co_expression_by_person
from operondemmo.co_expression_matrix.spearman_i_j import compute_co_expression_by_spearman
from operondemmo.cluster_or_classify_method.gamma_domain import get_result_by_clustering, get_result_by_clustering2
from operondemmo.input_file_handle.handle_gff import auto_download, generate_simple_gff, \
    get_gene_pos_strand, from_simple_gff_information_to_get, sorted_gene
from operondemmo.input_file_handle.handle_input import load_from_input_files, check_input_file, compute_expression
from operondemmo.input_file_handle.handle_kallisto import check_kallisto, split_from_input, generate_kallisto_index, \
    get_tpm_from_kallisto_quant, load_from_tpm_files, split_from_input_old
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
    # parser.add_argument("-i", action="store", dest="input_dir", default="null",
    #                     help="A directory to store a group of files. need fastq files and fna file.")
    parser.add_argument("-i", action="store", dest="input_dir", default="null",
                        help="A directory to store a group of files. fastq files.")
    parser.add_argument("-f", action="store", dest="fna_file", default="null",
                        help="The fna file of the prokaryote genome.")
    parser.add_argument("-o", action="store", dest="output_dir", default="OUT",
                        help="A directory include output data(operon file).default:OUT")
    parser.add_argument("-g", action="store", dest="gff_file", default="null",
                        help="The gff file of the prokaryote.")
    parser.add_argument("-p", action="store", dest="process_thread", default=1, type=int,
                        help="Specify the number of processing threads (CPUs).default:1")
    parser.add_argument("-t", action="store", dest="threshold", default=0.6, type=float,
                        help="the threshold in (-1,1)")
    parser.add_argument("-m", action="store", dest="method", default="GD",
                        help="the method to generate result file.default:GD(gamma_domain)."
                             "option:GD(gamma_domain);NB(naive_bayes)")
    advanced_argv.add_argument("-k", action="store", dest="kegg_id", default="null",
                               help="The kegg id of the prokaryote.(when '--auto_gff')")
    advanced_argv.add_argument("--auto_gff", action="store_true", dest="auto_gff", default=False,
                               help="Auto download gff_file from NCBI Database")
    advanced_argv.add_argument("--person", action="store_true", dest="person", default=False,
                               help="Build co-expression matrix with person correlation")
    advanced_argv.add_argument("--spearman", action="store_true", dest="spearman", default=False,
                               help="Build co-expression matrix with spearman correlation")
    # advanced_argv.add_argument("--kallisto", action="store_true", dest="kallisto", default=False,
    #                            help="Build expression matrix with kallisto result")
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
    if args.fna_file != "null":
        fna_file_path = args.fna_file
    else:
        print("NEEDED FNA_FILE.PLEASE check your input with option '-f'")
        return
    if args.input_dir[-1] != "/":
        input_dir = args.input_dir + "/"
    else:
        input_dir = args.input_dir
    if args.threshold > 1 or args.threshold < -1:
        print("IT CANNOT BE:", args.threshold, "PLEASE check your input with option '-t'")
        return
    if args.output_dir[-1] != "/":
        output_dir = args.output_dir + "/"
    else:
        output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.system("mkdir " + output_dir)
    # operon_predict_old(args.threshold, input_dir, output_dir, gff_file_path,
    #                    co_expression_method, args.kallisto, args.process_thread, args.method)
    operon_predict(args.threshold, input_dir, output_dir, gff_file_path,
                   co_expression_method, fna_file_path, args.process_thread, args.method)


def operon_predict(threshold, input_dir, output_dir, gff_file_path, co_expression_method, fna_file_path, p,
                   result_method):
    # simple_gff_file_information
    print("from your gff file to get [gene_locus_tag, start, stop, strand]...")
    simple_gff_path = generate_simple_gff(gff_file_path, output_dir)
    gene_pos_dict, gene_strand_dict = get_gene_pos_strand(simple_gff_path)
    final_gene_strand, final_gene_index, final_gene_sort = \
        from_simple_gff_information_to_get(gene_pos_dict, gene_strand_dict)

    # co_expression_matrix
    print("done\nRunning kallisto ...")
    print("from your fastq files to get tpm_co_expression_matrix...\n"
          "it would be cost few minutes, please waiting...")
    matrix_i_j = from_fastq_file_to_get_co_matrix_co_expression(input_dir, fna_file_path, output_dir,
                                                                gene_pos_dict, co_expression_method, p)
    # cluster_or_classify_method
    result_file = output_dir + "operon.txt"
    if result_method == "GD":
        print("done\ngamma_domain clustering...")
        get_result_by_clustering2(result_file, final_gene_strand, final_gene_index, final_gene_sort, matrix_i_j,
                                  threshold)
    elif result_method == "NB":
        print("done\nnaive bayes classifying...")
        gene_sort = sorted_gene(gene_pos_dict)
        get_result_by_classifying(gene_sort, gene_strand_dict, gene_pos_dict, matrix_i_j, result_file, 1, 2)
    else:
        pass
    print("done")
    print("PLEASE open your output_path:", result_file)


def operon_predict_old(threshold, input_dir, output_dir, gff_file_path, co_expression_method, kallisto, p,
                       result_method):
    # simple_gff_file_information
    print("from your gff file to get [gene_locus_tag, start, stop, strand]...")
    simple_gff_path = generate_simple_gff(gff_file_path, output_dir)
    gene_pos_dict, gene_strand_dict = get_gene_pos_strand(simple_gff_path)
    final_gene_strand, final_gene_index, final_gene_sort = \
        from_simple_gff_information_to_get(gene_pos_dict, gene_strand_dict)

    # co_expression_matrix
    if kallisto:
        print("done\nRunning kallisto ...")
        print("from your fastq files to get tpm_co_expression_matrix...\n"
              "it would be cost few minutes, please waiting...")
        matrix_i_j = from_fastq_file_to_get_co_matrix_co_expression_old(input_dir, output_dir,
                                                                        gene_pos_dict, co_expression_method, p)
    else:
        print("done\nfrom your samtools_depth result files to get tpm_co_expression_matrix...\n"
              "it would be cost few minutes, please waiting...")
        # matrix_co_expression
        matrix_i_j = from_depth_file_to_get_co_matrix_co_expression(input_dir, gene_pos_dict, co_expression_method, p)

    # cluster_or_classify_method
    result_file = output_dir + "operon.txt"
    if result_method == "GD":
        print("done\ngamma_domain clustering...")
        get_result_by_clustering2(result_file, final_gene_strand, final_gene_index, final_gene_sort, matrix_i_j,
                                  threshold)
    elif result_method == "NB":
        pass
    else:
        pass
    print("done")
    print("PLEASE open your output_path:", result_file)


def from_depth_file_to_get_co_matrix_co_expression(depth_files, gene_pos_dict, method, p):
    depth_files = load_from_input_files(depth_files)
    check_input_file(depth_files)

    gene_sort = sorted_gene(gene_pos_dict)

    matrix_groups_by_condition = compute_expression(depth_files, gene_pos_dict, gene_sort, p)
    matrix_co_expression = compute_co_expression(matrix_groups_by_condition, method, p)
    return matrix_co_expression


def from_fastq_file_to_get_co_matrix_co_expression(input_files, fna_file, output_path, gene_pos_dict, method, p):
    check_kallisto()
    fastq_files = split_from_input(input_files)
    check_input_file(fastq_files)
    gene_sort = sorted_gene(gene_pos_dict)
    kallisto_index = generate_kallisto_index(fna_file, gene_pos_dict, output_path, gene_sort)
    tpm_files = get_tpm_from_kallisto_quant(kallisto_index, fastq_files, output_path, p)
    tpm_matrix_by_condition = load_from_tpm_files(tpm_files)
    matrix_co_expression = compute_co_expression(tpm_matrix_by_condition, method, p)
    return matrix_co_expression


def from_fastq_file_to_get_co_matrix_co_expression_old(input_files, output_path, gene_pos_dict, method, p):
    check_kallisto()
    fna_file, fastq_files = split_from_input_old(input_files)
    check_input_file(fastq_files)
    gene_sort = sorted_gene(gene_pos_dict)
    kallisto_index = generate_kallisto_index(fna_file, gene_pos_dict, output_path, gene_sort)
    tpm_files = get_tpm_from_kallisto_quant(kallisto_index, fastq_files, output_path, p)
    tpm_matrix_by_condition = load_from_tpm_files(tpm_files)
    matrix_co_expression = compute_co_expression(tpm_matrix_by_condition, method, p)
    return matrix_co_expression


def compute_co_expression(expression_matrix, method, p):
    begin = time.time()
    if method == 0:
        matrix_c_i_j = compute_co_expression_by_c_i_j(expression_matrix)
        end = time.time()
        print("time: compute_co_expression_matrix: %.2f" % (end - begin))
        return matrix_c_i_j
    elif method == 1:
        matrix_c_person = compute_co_expression_by_person(expression_matrix)
        end = time.time()
        print("time: compute_co_expression_matrix: %.2f" % (end - begin))
        return matrix_c_person
    else:
        matrix_c_spearman = compute_co_expression_by_spearman(expression_matrix, p)
        end = time.time()
        print("time: compute_co_expression_matrix: %.2f" % (end - begin))
        return matrix_c_spearman


if __name__ == "__main__":
    main()
