from unittest import TestCase
from ...examples import example_graph_1
from ...paths_functions import SimplePaths
from nose.tools import eq_
import networkx

ex1_nodes, ex1_edges = example_graph_1()
simple_path = SimplePaths(ex1_nodes, ex1_edges, 4)

class TestPath(TestCase):

    def test_get_simple_paths_result(self):
        """
        test get_simple_paths_result
        """
        results = simple_path.get_simple_paths_result()
        eq_(round(results.node_score[0], 2), .96)

    def test_get_node_edge_data_nodes(self):
        """
        test get_node_edge_data, nodes output
        """
        eq_(simple_path.nodes_df.columns[0], 'node')

    def test_get_node_edge_data_edges(self):
        """
        test get_node_edge_data, edges output
        """
        eq_(simple_path.edges_df.columns[0], 'node_a')

    def test_get_node_edge_lists_nodes(self):
        """
        test get_node_edge_lists, nodes output
        """
        self.assertCountEqual(simple_path.node_list, [1, 2, 3, 4])

    def test_get_node_edge_lists_edges(self):
        """
        test get_node_edge_lists, edges output
        """
        eq_(simple_path.edge_tuple_list[0], (1, 2))

    def test_get_graph_graph(self):
        """
        test get_graph, graph output
        """
        self.assertIsInstance(simple_path.di_graph, networkx.digraph.DiGraph)

    def test_get_node_simple_paths(self):
        """
        test simple paths output of node 1
        """
        test_paths_list = [[1, 2], [1, 3, 2], [1, 2, 4, 3], [1, 3], [1, 2, 4], [1, 3, 2, 4]]
        paths_list = simple_path._get_node_simple_paths(1)
        self.assertCountEqual(paths_list, test_paths_list)

    def test_get_node_weights(self):
        """
        test node 1 weight
        """
        weight_dict = simple_path._get_node_weights()
        eq_(weight_dict[1], 1 / float(3))

    def test_get_node_score(self):
        """
        test value of node 1
        """
        weight_dict = simple_path._get_node_weights()
        paths_list = simple_path._get_node_simple_paths(1)
        node_score = simple_path.get_node_score(paths_list, weight_dict)
        eq_(round(node_score, 2), .96)

    def test_get_graph_score(self):
        """
        test score of node 1
        """
        node_scores = simple_path.get_graph_score()
        eq_(round(node_scores.node_score[0], 2), .96)

    def test_get_graph_diameter(self):
        graph_diameter = simple_path.get_graph_diameter()
        eq_(graph_diameter, 3)
