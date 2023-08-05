import pandas as pd
import networkx as nx
import numpy as np


class SimplePaths(object):
    def __init__(self, nodes, edges, depth, header=False):
        """
        :param nodes: dataframe or csv
        :param edges: dataframe or csv
        :param depth: int
        :param header: bool
        """
        self.nodes = nodes
        self.edges = edges
        self.depth = depth
        self.header = header
        self.nodes_df = None
        self.edges_df = None
        self.node_list = None
        self.di_graph = None
        self.edge_tuple_list = None
        self._get_node_edge_data()
        self._get_node_edge_lists()
        self._get_graph()

    def get_graph_score(self):
        """
        inputs:
            graph - directed networkx graph object
            depth - maximum length of simple path
        -------
        returns:
            node_score_df - dataframe of simple_path scores for all nodes
                in graph, format: |node|node score|
        """
        node_weights = self._get_node_weights()

        node_info_list = []

        for node in self.node_list:
            node_paths_list = self._get_node_simple_paths(node)
            node_score = SimplePaths.get_node_score(node_paths_list, node_weights)

            node_info_list.append([node, node_score])

        node_score_df = pd.DataFrame(node_info_list, columns=['node', 'node_score'])

        return node_score_df

    def get_simple_paths_result(self, csv_name=''):
        """
        inputs:
            nodes, edges - csv or dataframe

            format of nodes:
            |Node|Node text name|

            format of edges:
            |Node A|value of A|Node B|value of B|

            depth - maximum length of simple path

            csv - save results as csv (boolean)
            header - does csv of dataframe contain header (boolean)
        ------
        returns:
            results_df - dataframe of final results
            format:
                |node|node_text|node_score|
        """
        scores_df = self.get_graph_score()
        results_df = pd.merge(self.nodes_df, scores_df, on='node', how='left')

        if len(csv_name) > 0:
            results_df.to_csv(csv_name, index=False)

        return results_df

    def get_graph_diameter(self):
        return nx.diameter(self.di_graph)

    def _get_node_edge_data(self):
        """
        inputs: nodes, edges - csv or dataframe (headers optional):
            nodes need to be integers, node names can be any format
        header - if csv contains header (boolean)

        :return: dataframe in same format as csv inputs

        format of nodes:
        |Node|Node text name|

        format of edges:
        |Node A|value of A|Node B|value of B|
        """
        if self.header is True:
            header = 0
        else:
            header = None

        if isinstance(self.nodes, str):
            nodes_df = pd.read_csv(self.nodes, header=header)
        elif isinstance(self.nodes, pd.DataFrame):
            nodes_df = self.nodes
        else:
            raise TypeError('node variable can only be path to csv or pandas dataframe')

        if isinstance(self.edges, str):
            edges_df = pd.read_csv(self.nodes, header=header)
        elif isinstance(self.edges, pd.DataFrame):
            edges_df = self.edges
        else:
            raise TypeError('node variable can only be path to csv or pandas dataframe')

        edges_df.columns = ['node_a', 'a_value', 'node_b', 'b_value']
        nodes_df.columns = ['node', 'node_text']

        self.nodes_df = nodes_df
        self.edges_df = edges_df

    def _get_node_edge_lists(self):
        """
        returns:
            node_list - list of integers
            edge_tuple_list - list of tuples where each tuple is an edge of origin and
                terminal node
        """
        node_list = [int(node) for node in self.nodes_df.node.tolist()]

        edge_tuple_list = []
        for _, edge in self.edges_df.iterrows():
            # if tie then 2 edges will be added in either direction
            if edge.a_value == edge.b_value:
                edge_tuple_list.append((edge.node_a, edge.node_b))
                edge_tuple_list.append((edge.node_b, edge.node_a))
            elif edge.a_value > edge.b_value:
                edge_tuple_list.append((edge.node_a, edge.node_b))
            else:
                edge_tuple_list.append((edge.node_b, edge.node_a))

        self.node_list = node_list
        self.edge_tuple_list = edge_tuple_list

    def _get_graph(self):
        """
        returns:
            di_graph - directed graph, using networkx
            node_df - dataframe of nodes, see get_node_edge_data for format
        """
        di_graph = nx.DiGraph()
        di_graph.add_nodes_from(self.node_list)
        di_graph.add_edges_from(self.edge_tuple_list)

        self.di_graph = di_graph

    def _get_node_simple_paths(self, starting_node):
        """
        inputs:
            graph - directed graph, networkx object
            nodes - list of nodes to get paths for (all nodes in graph)
            starting_node - node for which paths are generated
            depth - maximum length of simple path
        -------
        returns:
            list of list where each list is a simple path from the starting_node,
            there will be len(nodes) - 1 elements in list
        """

        node_paths_list = []

        for node in self.node_list:
            # we don't want the simple paths from origin node to itself so continue
            if node == starting_node:
                continue
            else:
                paths_temp = nx.all_simple_paths(self.di_graph, starting_node, node, cutoff=self.depth)
                node_paths_list += list(paths_temp)

        return node_paths_list

    def _get_node_weights(self):
        """
        inputs:
            graph - directed networkx graph object
            list_of_nodes - list of nodes in graph
        -------
        returns:
            weight_dict - dictionary of node weights, format {node: node weight}
        """
        node_all_list = self.di_graph.degree(self.node_list)

        weight_dict = {}

        for node_pair in node_all_list:
            node_weight = 1 / float(node_pair[1])
            weight_dict[node_pair[0]] = node_weight

        return weight_dict

    @staticmethod
    def get_node_score(node_paths_list, weight_dict):
        """
        inputs:
            node_paths_list - list of lists of node paths from origin node_paths_list
            weight_dict - dictionary of weights of all nodes, format {node: node weight}
        --------
        returns:
            node_value - score of simple_path_algorithm for node (float)
        """
        node_value = 0
        for path in node_paths_list:
            temp_path_value_list = []
            for i in range(len(path) - 1):
                temp_path_value_list.append(weight_dict[path[i]])

            node_value += np.prod(temp_path_value_list)

        return node_value
