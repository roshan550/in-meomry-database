import graphviz
import streamlit as st

class DataStructureVisualizer:
    def __init__(self):
        self.colors = {
            "node": "#FF4B4B",
            "highlight": "#00CC96",
            "edge": "#262730"
        }

    def _create_btree_graph(self, node, graph, parent_name=None, edge_label=None):
        if not node:
            return

        # Create node name
        node_name = f"node_{id(node)}"
        
        # Create label with key-value pairs
        if node.leaf:
            label = " | ".join([f"{k[0]}: {k[1]}" for k in node.keys])
        else:
            label = " | ".join([str(k[0]) for k in node.keys])
            
        graph.node(node_name, label, shape="record", color=self.colors["node"])
        
        if parent_name:
            graph.edge(parent_name, node_name, edge_label or "", color=self.colors["edge"])
            
        if not node.leaf:
            for i, child in enumerate(node.children):
                self._create_btree_graph(child, graph, node_name, str(i))

    def _create_avl_graph(self, node, graph, parent_name=None):
        if not node:
            return

        node_name = f"node_{id(node)}"
        label = f"{node.key}: {node.value}\\nh={node.height}"
        graph.node(node_name, label, color=self.colors["node"])
        
        if parent_name:
            graph.edge(parent_name, node_name, color=self.colors["edge"])
            
        self._create_avl_graph(node.left, graph, node_name)
        self._create_avl_graph(node.right, graph, node_name)

    def _create_skiplist_graph(self, skip_list, graph):
        current = skip_list.header
        level = skip_list.level
        
        # Create header node
        header_name = "header"
        graph.node(header_name, "Header", color=self.colors["node"])
        
        # Create nodes for each level
        prev_nodes = {i: header_name for i in range(level + 1)}
        
        while current.forward[0]:
            current = current.forward[0]
            node_name = f"node_{id(current)}"
            label = f"{current.key}: {current.value}"
            graph.node(node_name, label, color=self.colors["node"])
            
            # Add edges for each level
            for i in range(min(current.forward.__len__(), level + 1)):
                if current.forward[i]:
                    graph.edge(prev_nodes[i], node_name, color=self.colors["edge"], constraint='false')
                prev_nodes[i] = node_name

    def visualize_structure(self, structure_type, structure, title):
        """Generate visualization for a specific data structure"""
        graph = graphviz.Digraph()
        graph.attr(rankdir='LR' if structure_type == "skip_list" else "TB")
        
        if structure_type == "btree":
            self._create_btree_graph(structure.root, graph)
        elif structure_type == "avl":
            self._create_avl_graph(structure.root, graph)
        else:  # skip_list
            self._create_skiplist_graph(structure, graph)
            
        return graph

    def create_transition_animation(self, source_structure, target_structure, source_type, target_type):
        """Create animation frames for structure transition"""
        # Generate before and after visualizations
        source_graph = self.visualize_structure(source_type, source_structure, "Before")
        target_graph = self.visualize_structure(target_type, target_structure, "After")
        
        return source_graph, target_graph
