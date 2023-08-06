import numpy
import sys


class Node:
    def __init__(self, l, r):
        self.a = 0
        self.left_child = l
        self.right_child = r
        self.list_node = []

    def set_left(self, _node):
        self.left_child = _node

    def set_right(self, _node):
        self.right_child = _node

    def to_list(self, _node):
        if type(_node) is numpy.int64:
            # print(_node)
            self.list_node.append(_node)
        else:
            self.to_list(_node.left_child)
            self.to_list(_node.right_child)
        self.list_node = sorted(self.list_node)
        return self.list_node


class Gamma:
    def __init__(self, matrix):
        self.matrix = matrix
        self.trees = []
        self.index_trees = []

    def clustering2(self, t):
        cluster_matrix = self.matrix.copy()
        while cluster_matrix.max() >= t:
            # print(cluster_matrix)
            a = cluster_matrix.max()
            x_array, y_array = numpy.where(cluster_matrix == a)
            x = x_array[0]
            y = y_array[0]
            # print(x, y)
            new_node = Node(x, y)
            new_node.a = a
            left_exist = self.is_exist(new_node.left_child)
            right_exist = self.is_exist(new_node.right_child)
            if left_exist == 0 and right_exist == 0:
                self.save_to_trees(new_node)
            elif left_exist == 0 and right_exist == 1:
                tree_index = self.get_index(new_node.right_child)
                new_node.set_right(self.trees[tree_index])
                self.trees.remove(self.trees[tree_index])
                self.index_trees.remove(self.index_trees[tree_index])
                self.save_to_trees(new_node)
            elif left_exist == 1 and right_exist == 0:
                tree_index = self.get_index(new_node.left_child)
                new_node.set_left(self.trees[tree_index])
                self.trees.remove(self.trees[tree_index])
                self.index_trees.remove(self.index_trees[tree_index])
                self.save_to_trees(new_node)
            elif left_exist == 1 and right_exist == 1:
                tree_index = self.get_index(new_node.left_child)
                new_node.set_left(self.trees[tree_index])
                self.trees.remove(self.trees[tree_index])
                self.index_trees.remove(self.index_trees[tree_index])
                tree_index = self.get_index(new_node.right_child)
                new_node.set_right(self.trees[tree_index])
                self.trees.remove(self.trees[tree_index])
                self.index_trees.remove(self.index_trees[tree_index])
                self.save_to_trees(new_node)
            else:
                print("something wrong")
            cluster_matrix[x][y] = -2
            # print(cluster_matrix)
        for i in range(len(cluster_matrix)):
            if not self.is_exist(i):
                self.index_trees.append([i])
        return self.index_trees

    def clustering(self):
        cluster_matrix = self.matrix.copy()
        while cluster_matrix.max() > 0:
            a = cluster_matrix.max()
            x_array, y_array = numpy.where(cluster_matrix == a)
            x = x_array[0]
            y = y_array[0]
            new_node = Node(x, y)
            new_node.a = a
            left_exist = self.is_exist(new_node.left_child)
            right_exist = self.is_exist(new_node.right_child)
            if left_exist == 0 and right_exist == 0:
                self.save_to_trees(new_node)
            elif left_exist == 0 and right_exist == 1:
                tree_index = self.get_index(new_node.right_child)
                new_node.set_right(self.trees[tree_index])
                self.save_to_trees(new_node)
            elif left_exist == 1 and right_exist == 0:
                tree_index = self.get_index(new_node.left_child)
                new_node.set_left(self.trees[tree_index])
                self.save_to_trees(new_node)
            elif left_exist == 1 and right_exist == 1:
                tree_index = self.get_index(new_node.left_child)
                new_node.set_left(self.trees[tree_index])
                tree_index = self.get_index(new_node.right_child)
                new_node.set_right(self.trees[tree_index])
                self.save_to_trees(new_node)
            else:
                print("something wrong")
            cluster_matrix[x][y] = -2
            # print(cluster_matrix)

    def is_exist(self, num):
        for each in self.index_trees:
            for single in each:
                if num == single:
                    return 1
        return 0

    def get_index(self, num):
        index_list = []
        size_list = []
        for each in self.index_trees:
            # print(each)
            for single in each:
                if num == single:
                    index_list.append(self.index_trees.index(each))
                    size_list.append(len(each))
        return index_list[size_list.index(max(size_list))]

    def save_to_trees(self, _node):
        self.index_trees.append(_node.to_list(_node))
        self.trees.append(_node)

    def gamma_threshold(self, t):
        # negative_predict = []
        for _tree in self.trees:
            if _tree.a < t:
                self.index_trees.remove(_tree.list_node)
                # negative_predict.append(_tree.list_node)
        return self.index_trees

    def statistics_gamma(self):
        a_list = set()
        for _tree in self.trees:
            a_list.add(_tree.a)
        return sorted(list(a_list))


def add_name(_result, gene_name_list):
    added_name = []
    for each_ in _result:
        added_name.append([])
        for item in each_:
            # print(item, gene_name_list[item])
            added_name[-1].append(gene_name_list[item])
    return added_name


def get_index_partition(current_strand_list):
    forw_num = current_strand_list.count("+")
    rev_num = current_strand_list.count("-")
    if forw_num > rev_num:
        rev_index = []
        for i, j in enumerate(current_strand_list):
            if j == "-":
                rev_index.append(i)
        return rev_index
    elif rev_num > forw_num:
        forw_index = []
        for i, j in enumerate(current_strand_list):
            if j == "+":
                forw_index.append(i)
        return forw_index
    else:
        print("something wrong", current_strand_list)
        sys.exit(1)


def partition_s_rna(cluster_result, partition_index):
    for each_list in cluster_result:
        for each_item in each_list:
            if each_item in partition_index:
                # print("each:", each_)
                _index = cluster_result.index(each_list)
                each_list.remove(each_item)
                if cluster_result.count(each_list) > 1 or len(each_list) == 0:
                    cluster_result.remove(each_list)
                new_result = [each_item]
                if new_result not in cluster_result:
                    cluster_result.insert(_index, new_result)
    return cluster_result


def get_result_by_clustering(result_file, final_gene_strand, final_gene_index, final_gene_sort, matrix_i_j, threshold):
    threshold = threshold + 2
    result_list = []
    result_file_fp = open(result_file, 'w')
    i_iter = 0
    while i_iter < len(final_gene_index):
        # print(final_gene_index[i_iter])
        slice_start = final_gene_index[i_iter][0]
        slice_stop = final_gene_index[i_iter][-1]
        matrix_tmp = matrix_i_j[slice_start:slice_stop + 1, slice_start:slice_stop + 1]
        matrix_tmp = numpy.diag(matrix_tmp.diagonal(-1) + 2, -1)
        # print(matrix_tmp)
        gamma = Gamma(matrix_tmp)
        gamma.clustering()
        gamma_result = gamma.gamma_threshold(threshold)
        # print(result)
        current_gene_strand_list = final_gene_strand[i_iter]
        # print(current_gene_strand_list)
        tmp_index = get_index_partition(current_gene_strand_list)
        # print("result:", result)
        # print("tmp_index:", tmp_index)
        gamma_result = partition_s_rna(gamma_result, tmp_index)
        # print("final_result:", result)
        # print("\n")
        current_gene_name_list = final_gene_sort[i_iter]
        added_name_result = add_name(gamma_result, current_gene_name_list)
        for each_ in added_name_result:
            if each_ not in result_list:
                result_list.append(each_)
                result_file_fp.write(";".join(each_) + "\n")
        i_iter = i_iter + 1
    result_file_fp.close()


def get_result_by_clustering2(result_file, final_gene_strand, final_gene_index, final_gene_sort, matrix_i_j, threshold):
    threshold = threshold + 2
    result_list = []
    result_file_fp = open(result_file, 'w')
    i_iter = 0
    while i_iter < len(final_gene_index):
        # print(final_gene_index[i_iter])
        slice_start = final_gene_index[i_iter][0]
        slice_stop = final_gene_index[i_iter][-1]
        matrix_tmp = matrix_i_j[slice_start:slice_stop + 1, slice_start:slice_stop + 1]
        matrix_tmp = numpy.diag(matrix_tmp.diagonal(-1) + 2, -1)
        # print(matrix_tmp)
        gamma = Gamma(matrix_tmp)
        gamma_result = gamma.clustering2(threshold)
        current_gene_strand_list = final_gene_strand[i_iter]
        # print(current_gene_strand_list)
        tmp_index = get_index_partition(current_gene_strand_list)
        # print("result:", result)
        # print("tmp_index:", tmp_index)
        gamma_result = partition_s_rna(gamma_result, tmp_index)
        # print("final_result:", result)
        # print("\n")
        current_gene_name_list = final_gene_sort[i_iter]
        added_name_result = add_name(gamma_result, current_gene_name_list)
        for each_ in added_name_result:
            if each_ not in result_list:
                result_list.append(each_)
                result_file_fp.write(";".join(each_) + "\n")
        i_iter = i_iter + 1
    result_file_fp.close()
