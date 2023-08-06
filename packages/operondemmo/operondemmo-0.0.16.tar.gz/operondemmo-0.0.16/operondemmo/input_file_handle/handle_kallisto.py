import os
from multiprocessing import Pool
import sys

import numpy
import time

from operondemmo.version import kallisto_out_file


def check_kallisto():
    is_exist = os.system("kallisto version")
    if is_exist != 0:
        print("need kallisto. link: https://pachterlab.github.io/kallisto/download")
        sys.exit(1)


def split_from_input(input_files):
    fastq_files = []
    all_file = []
    for each_dir in os.listdir(input_files):
        all_file.append(input_files + each_dir + "/")
    for each_dir in all_file:
        condition_files = []
        condition_name = []
        for each_file in os.listdir(each_dir):
            condition_files.append(each_dir + each_file)
        for each_file in condition_files:
            tmp_each = each_file.split("/")[-1]
            tmp_each2 = tmp_each.split("_")[0]
            if tmp_each2 not in condition_name:
                condition_name.append(tmp_each2)
        if ".gz" in condition_files[0]:
            i = 0
            while i < len(condition_name):
                condition_name[i] = each_dir + condition_name[i] + "_1.fastq.gz " \
                                    + each_dir + condition_name[i] + "_2.fastq.gz"
                i = i + 1
        else:
            i = 0
            while i < len(condition_name):
                condition_name[i] = each_dir + condition_name[i] + "_1.fastq " \
                                    + each_dir + condition_name[i] + "_2.fastq"
                i = i + 1
        fastq_files.append(" ".join(condition_name))
    return fastq_files


def split_from_input_old(input_files):
    fna_file = ""
    all_files = []
    for each_file in os.listdir(input_files):
        all_files.append(input_files + each_file)
    for each_ in all_files:
        if ".fna" in each_:
            fna_file = each_
            all_files.remove(each_)
    if fna_file == "":
        print("need .fna file.")
        sys.exit(1)
    fastq_files = []
    for each_ in all_files:
        tmp_each = each_.split("/")[-1]
        tmp_each2 = tmp_each.split("_")[0]
        if tmp_each2 not in fastq_files:
            fastq_files.append(tmp_each2)
    if ".gz" in all_files[0]:
        i = 0
        while i < len(fastq_files):
            fastq_files[i] = input_files + fastq_files[i] + "_1.fastq.gz " \
                             + input_files + fastq_files[i] + "_2.fastq.gz"
            i = i + 1
    else:
        i = 0
        while i < len(fastq_files):
            fastq_files[i] = input_files + fastq_files[i] + "_1.fastq " + input_files + fastq_files[i] + "_2.fastq"
            i = i + 1
    # print(fastq_files)
    # print(fna_file, type(fna_file))
    return fna_file, fastq_files


def read_fna(fna_file):
    fna_fp = open(fna_file, 'r')
    fna_str = ""
    while True:
        line = fna_fp.readline().strip()
        if not line:
            break
        if ">" in line:
            pass
        else:
            fna_str = fna_str + line
    fna_fp.close()
    return fna_str


def to_fasta(gene_name, gene_str):
    gene_name = ">" + gene_name
    line_len = 80
    new_gene_str = gene_name
    i = 0
    while i < len(gene_str):
        new_gene_str = new_gene_str + "\n" + gene_str[i:i + line_len]
        i = i + line_len
    return new_gene_str


def frg_fna_according_to_gene_pos(fna_file, fna_path, gene_pos_dict, gene_sort):
    fna_str = read_fna(fna_file)
    fna_frg_fp = open(fna_path, 'w')
    fna_frg_list = []
    for gene in gene_sort:
        fna_frg_list.append("")
        for (start, stop) in gene_pos_dict[gene]:
            fna_frg_list[-1] = fna_frg_list[-1] + fna_str[start - 1:stop]
        fna_frg_fp.write(to_fasta(gene, fna_frg_list[-1]) + "\n")
    # print(len(fna_frg_list))
    fna_frg_fp.close()


def generate_kallisto_index(fna_file, gene_pos_dict, output_path, gene_sort):
    tmp_path = output_path + "tmp/"
    fna_name = fna_file.split("/")[-1]
    fna_path = tmp_path + "frg_" + fna_name
    if not os.path.exists(fna_path):
        frg_fna_according_to_gene_pos(fna_file, fna_path, gene_pos_dict, gene_sort)
    kallisto_index = fna_path.split(".")[0] + ".idx"
    if not os.path.exists(kallisto_index):
        os.system("kallisto index -i " + kallisto_index + " " + fna_path)
    return kallisto_index


def run_kallisto_quant_paired(fastq_files, kallisto_index, output_path):
    if not os.path.exists(output_path):
        is_ok = os.system("kallisto quant -i " + kallisto_index + " -o " + output_path + " " + fastq_files)
        if is_ok != 0:
            print("check your input. something wrong.")
            sys.exit(1)
    return output_path + kallisto_out_file


def get_tpm_from_kallisto_quant(kallisto_index, fastq_files, output_path, p):
    tmp_path = output_path + "tmp/"
    kallisto_out = []
    for i in range(len(fastq_files)):
        kallisto_out.append(tmp_path + str(i) + "_out/")
    kallisto_index_list = [kallisto_index] * len(fastq_files)
    start = time.time()
    pool = Pool(p)
    tpm_files = pool.starmap(run_kallisto_quant_paired, zip(fastq_files, kallisto_index_list, kallisto_out))
    pool.close()
    pool.join()
    end = time.time()
    print("time: compute tpm: %.2f" % (end - start))
    return tpm_files


def load_from_tpm_files(tpm_files):
    tmp_matrix = []
    for each_ in tpm_files:
        tmp_matrix.append([])
        file_fp = open(each_, 'r')
        file_fp.readline()
        file_content = file_fp.read().strip()
        content_list = file_content.split("\n")
        for line in content_list:
            tmp_content = line.split("\t")
            tmp_matrix[-1].append(tmp_content[-1])
    tmp_matrix = numpy.array(tmp_matrix).astype('float64').T
    # numpy.savetxt("/home/lyd/document/2018.1/gamma_domain/kallisto_matrix.txt", tmp_matrix, fmt="%.8f")
    # print(tmp_matrix.shape[0], tmp_matrix.shape[1])
    return tmp_matrix


if __name__ == "__main__":
    # test read_fna()
    fna_file_path = "/home/lyd/document/2018.1/eco/eco.fna"
    eco_fna = read_fna(fna_file_path)
    print(len(eco_fna))
