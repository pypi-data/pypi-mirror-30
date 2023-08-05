from collections import deque
from collections import OrderedDict


class DAG(object):
    """ Directed acyclic graph implementation. """

    def __init__(self):
        """ Construct a new DAG with no nodes or edges. """
        self.reset_graph()

    def add_node(self, node_name):
        """ Add a node if it does not exist yet, or error out. """
        if node_name in self.graph:
            raise KeyError('node %s already exists' % node_name)
        self.graph[node_name] = set()
        self.back_graph[node_name] = set()

    def add_node_if_not_exists(self, node_name):
        if node_name not in self.graph:
            self.add_node(node_name)

    def delete_node(self, node_name):
        """ Deletes this node and all edges referencing it. """
        if node_name not in self.graph:
            raise KeyError('node %s does not exist' % node_name)
        children = self.graph.pop(node_name)
        parents = self.back_graph.pop(node_name)
        for child in children:
            self.back_graph[child].remove(node_name)
        for parent in parents:
            self.graph[parent].remove(node_name)

    def delete_node_if_exists(self, node_name):
        if node_name in self.graph:
            self.delete_node(node_name)

    def add_edge(self, ind_node, dep_node):
        """ Add an edge (dependency) between the specified nodes. """
        if ind_node not in self.graph or dep_node not in self.graph:
            raise KeyError('one or more nodes do not exist in graph')
        self.graph[ind_node].add(dep_node)
        self.back_graph[dep_node].add(ind_node)

    def delete_edge(self, ind_node, dep_node):
        """ Delete an edge from the graph. """
        if dep_node not in self.graph.get(ind_node, []):
            raise KeyError('this edge does not exist in graph')
        self.graph[ind_node].remove(dep_node)
        self.back_graph[dep_node].remove(ind_node)

    def predecessors(self, node):
        """ Returns a list of all predecessors of the given node """
        return self.back_graph.get(node)

    def downstream(self, node):
        """ Returns a list of all nodes this node has edges towards. """
        return self.graph.get(node)

    def all_downstreams(self, node):
        """Returns a set of all nodes ultimately downstream
        of the given node in the dependency graph, in
        topological order."""
        nodes = [node]
        nodes_seen = set()
        i = 0
        while i < len(nodes):
            downstreams = self.downstream(nodes[i])
            for downstream_node in downstreams:
                if downstream_node not in nodes_seen:
                    nodes_seen.add(downstream_node)
                    nodes.append(downstream_node)
            i += 1
        return nodes_seen

    def all_nodes(self):
        """ Return a list of all nodes """
        return self.graph.keys()

    def contains_node(self, node):
        """ Return whether the given node exist in the graph"""
        return node in self.graph

    def all_edges(self):
        """ Return a list of all edges """
        result = set()
        for parent, children in self.graph.items():
            for child in children:
                result.add((parent, child))
        return result

    def all_leaves(self):
        """ Return a list of all leaves (nodes with no downstreams) """
        return set(key for key in self.graph if not self.graph[key])

    def ind_nodes(self):
        """ Returns a list of all nodes in the graph with no dependencies. """
        return set(key for key in self.back_graph if not self.back_graph[key])

    def validate(self):
        """ Returns (Boolean, message) of whether DAG is valid. """
        nodes = self.topological_sort()
        return len(nodes) == len(self.graph)

    def topological_sort(self):
        """ Returns a topological ordering of the DAG.
        Raises an error if this is not possible (graph is not valid).
        """
        in_degree = {}
        for u in self.graph:
            in_degree[u] = 0
        for u in self.graph:
            for v in self.graph[u]:
                in_degree[v] += 1
        queue = deque()
        for u in in_degree:
            if in_degree[u] == 0:
                queue.appendleft(u)
        l = []
        while queue:
            u = queue.pop()
            l.append(u)
            for v in self.graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.appendleft(v)
        return l

    def clone(self):
        """Returns a dag with the same node instance"""
        result = DAG()
        for k, v in self.graph.items():
            result.graph[k] = v.copy()
        for k, v in self.back_graph.items():
            result.back_graph[k] = v.copy()
        return result

    def size(self):
        return len(self.graph)

    def reset_graph(self):
        """ Restore the graph to an empty state. """
        self.graph = dict()
        self.back_graph = dict()

