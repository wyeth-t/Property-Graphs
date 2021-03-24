#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 16:23:20 2021

@author: wyeththompson
"""

from graph_partial import Graph
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

class Node():
    """Create nodes with name, category, and property attributes to be used in the property graph classes"""
    def __init__(self, name, category, props={}):
        self.name = name
        self.category = category
        self.props = props
        
    def get_name(self):
        return self.name
    
    def get_category(self):
        return self.category 
    
    def get_property(self, key):
        return self.props[key]
    
    def set_property(self, key, value):
        self.props[key] = value
        
    def get_all_properties(self):
        return self.props
    
    def __hash__(self):
        return hash(self.name) 
    
    def __eq__(self, other):
        "Are two nodes the same"
        return self.get_name() == other.get_name() and self.get_category() == other.get_category() \
            and self.get_all_properties() == other.get_all_properties()
            
    
    
class Relationship():
    """Create relationships connecting nodes directionally, with category and propery attributes to be used in the 
    property graph class
    """
    def __init__(self, category, props={}):
        self.category = category
        self.props = props
        
    def get_category(self):
        return self.category 
    
    def get_property(self, key):
        return self.props[key]
        
    def set_property(self, key, value):
        self.props[key] = value
        
    def get_all_properties(self):
        return self.props
    
class PropertyGraph(Graph):
    """Create a property graph """
    def __init__(self, nodes = {}, relationships = {}):
        self.nodes = nodes
        self.relationships = relationships
        self.V = nodes.keys()
        self.E = relationships.keys()
        super().__init__(self.V, self.E)

    def add_node(self, n):
        """ add a node to a pre-existing property graph, takes n as an argument 
        Parameters: n is a variable representing an instanced node object
        """
        self.add_vertex(n.get_name())
        self.nodes[n.get_name()] = n
        
    def add_relationship(self, n, m, rel):
        """add a node to a pre-existing property graph, takes n as an argument 
        Parameters: rel is a variable representing an instanced relationship object, n and m are strs representing nodes,
            with n being the parent and m being the child to show directionality
        """
        self.add_edge(n,m)
        self.relationships[(n,m)] = rel
        
    def get_all_relationships(self, node):
        """gets all property graph relationships of a node and returns them as tuples
        Paramters: node (STR) 
        Returns: list of tuples with node as the first value and saved relationship as the second value
        """
        graph = self.get_graph()
        relationships = graph[node]
        tups = []
        for relationship in relationships:
            tups.append((node,relationship))
        return tups
    
    def get_interconnected_relationships(self, nodes):
        """gets all existing relationships linking a list of nodes
        Parameters: nodes - list of strings
        Returns: list of all existing relationships interconnecting the provided nodes list
        """
        rels = []
        for node in nodes:
            #find all existing relationships from each node in nodes
            all_relationships = self.get_all_relationships(node)
            for rel in all_relationships:
                #filter out relationships that are not interconnecting list of nodes
                x,y = rel
                if x in nodes and y in nodes:
                    rels.append(rel)
        return rels
    
    def find_nodes(self, name=None, category=None, key=None, value=None):
        """ finds nodes in the property graph based on optional parameters
            Parameters: name-finds nodes with specific name, category-finds nodes with specific category, 
                key- finds nodes that contain a specific property key, value- finds nodes that have a specfic value key
            Returns: list of Nodes STRs
        """
        functs_list = ['identifier', name, category, key, value]
        found = []
        
        for i in self.nodes.values():
            #create a list for each node in graph that shows true false value for each category if the parameter is met
            lst = [i.get_name()]
            lst.append(i.get_name() == name)
            lst.append(i.get_category() == category)
            lst.append(value in i.props.values())
            lst.append(key in i.props.keys())
            found.append(lst)
            
        #create a dataframe from the list of node lists with columns containing true false values showing if the parameter conditions are met
        df = pd.DataFrame(found, columns = functs_list)
        
        #remove columns in DF that have a value of none 
        df.pop(None)   
        
        #create a list of parameters that match all provided parameters (true) and return the node names
        df = df.set_index(df.columns[0])
        result = df[df.all(axis=1)].index.tolist()
        return result

    def get_graph(self):
        """
        Returns an instance of the current property graph
        """
        return PropertyGraph(self.nodes, self.relationships)
        
    def shared_set(self,list1,list2):
        """Parameters: 2 lists containing str values
        returns a third list of all the common values from both lists
        """
        return list(set(list1) & set(list2))
    
    def subgraph(self, nodes):
        """Creates a subgraph containing a list of nodes and any interconnecting relationships
        Parameters: list of nodes (strs)
        returns: PropertyGraph instance 
        """
        #get interconnected relationships between nodes
        rels = self.get_interconnected_relationships(nodes)
        
        #creates lists for nodes and keys that can be read into the property graph function
        All_relationships = {rel:self.relationships[rel] for rel in rels}
        All_keys = {node:self.nodes[node] for node in nodes}
        
        #return a new instance of property graph with the new key and relationship dicts
        return PropertyGraph(All_keys, All_relationships)
        
    def adjacent(self, n, node_category=None, rel_category=None):
        """retuns a list of nodes of all nodes directly connected to one node (n)
        parameters: n: node (STR) node_category: optional, node category to filter results, rel_category: optional, relationship category to filter results
        returns: list of nodes (STRs)
        """
        #gets a list of all attached nodes and filters them based on the category parameter
        graph = self.get_graph()
        adj_nodes = graph[n]
        node_lst = {node:self.nodes[node] for node in adj_nodes}
        nodes_filtered = [key for key,value in node_lst.items() if value.get_category() == node_category]
        
        #get a list of all relationships of n and filter based on the relationship parameter
        rels = self.get_all_relationships(n)
        rels_filtered = [child for parent,child in rels if self.relationships[parent,child].get_category() == rel_category]
        
        #combine the two filtered lists to show common values
        if node_category != None and rel_category == None:
            nodes = nodes_filtered
        elif node_category == None and rel_category!= None:
            nodes = rels_filtered
        else:
            nodes = self.shared_set(nodes_filtered, rels_filtered)
        return nodes
    
    def recommendation_engine(self,n):
        """takes a node and makes recommendations of movies to watch based on friends watched movies
        parameters: node (STR)
        returns a list of recommended movie nodes (STRs)
        """
        #gets a list of known people
        friends = self.adjacent(n, node_category='person')
        friends_movies = []
        
        #gets a list of movies friends have watched
        for friend in friends:
            friends_movies += self.adjacent(friend, node_category='movie')
            
        #remove movies n has already watched from the list
        my_movies = self.adjacent(n, node_category='movie')
        recommendations = list(set(friends_movies) - set(my_movies))
        return recommendations
    
    def visualize(self):
        """
      create a directed unweighted propertygraph
        """
        G=nx.DiGraph()
        G.add_edges_from(self.relationships.keys())
        G.add_nodes_from(self.nodes)
        node_labels = {node:node for (node,node1) in self.nodes.items()}
        pnodes = self.find_nodes(category = "person")
        
        
        pnode_pos = {}
        i = 0.1
        x = 1.15
        y = -0.05
        for pnode in pnodes:
            pnode_pos[pnode] = (i,x+y)
            y=-y
            i+=1
        
        nx.draw_networkx_nodes(G,pos = pnode_pos,node_size=1000,nodelist=pnodes,node_color='red', alpha=0.5, node_shape='8')
        
        mnodes = self.find_nodes(category = "movie")
        a,b,c = .1,0.45,.05
        for mnode in mnodes:
            pnode_pos[mnode] = (a,b + c)
            c = -c
            a+=.39
        
        nx.draw_networkx_nodes(G,pos = pnode_pos,node_size=500,nodelist=mnodes,node_color='blue', alpha=.5, node_shape='^')
        nx.draw_networkx_labels(G,pos= pnode_pos,labels =node_labels, font_size=8)
        nx.draw_networkx_edges(G,pos = pnode_pos, alpha=0.9)
        #edge_labels = {key:value.get_category() for (key,value) in self.relationships.items()}
        #nx.draw_networkx_edge_labels(G, pos=pnode_pos, edge_labels= edge_labels)
        
def main():
    #instantiate nodes
    Strange = Node('Strange', "person", {"occupation" : "teacher"})
    Rachlin = Node('Rachlin', "person", {"occupation" : "teacher"})
    Rueben = Node('Rueben', "person", {"occupation" : "student"})
    New_Hope = Node('A New Hope', 'movie', {"released": '1977'})
    Phantom_Menace = Node('The Phantom Menace', 'movie', {"released": '1999'})
    Attack_Clones = Node('Attack of the Clones', 'movie', {"released": '2002'})
    Revenge_Sith = Node('Revenge of the Sith', 'movie', {"released": '2005'})
    Strikes_Back = Node('The Empire Strikes Back', 'movie', {"released": '1980'})
    Return_Jedi = Node('Return of the Jedi', 'movie', {"released": '1983'})
    
    #instatiate relationships
    SR = Relationship('KNOWS')
    RRu = Relationship('KNOWS') 
    RS = Relationship('KNOWS')
    M1 = Relationship('WATCHED', {'enjoyment': 10})
    M2 = Relationship('WATCHED', {'enjoyment': 6})
    M3 = Relationship('WATCHED', {'enjoyment': 4})
    M4 = Relationship('WATCHED', {'enjoyment': 7})
    M5 = Relationship('WATCHED', {'enjoyment': 7})
    M6 = Relationship('WATCHED', {'enjoyment': 5})
    M7 = Relationship('WATCHED', {'enjoyment': 8})
    M8 = Relationship('WATCHED', {'enjoyment': 6})
    M9 = Relationship('WATCHED', {'enjoyment': 9})
    M10 = Relationship('WATCHED', {'enjoyment': 4})
    
    #create dictionary of node names and objects
    All_nodes = {'Strange': Strange, 'Rachlin': Rachlin, 'Rueben': Rueben, 
                 'The Phantom Menace': Phantom_Menace, 'Attack of the Clones': Attack_Clones,
                  'Revenge of the Sith': Revenge_Sith,  'A New Hope': New_Hope,
                 'The Empire Strikes Back':Strikes_Back, 'Return of the Jedi': Return_Jedi}
    
    #create dictionary of property names and objects
    All_relationships = {('Strange', 'Rachlin') : SR, ('Rachlin', 'Strange'): RS, ('Rachlin', 'Rueben'): RRu,
                         ('Strange', 'The Phantom Menace'): M1, ('Strange', 'Attack of the Clones'): M2, ('Strange', 'Return of the Jedi'): M3,
                         ('Rueben', 'The Empire Strikes Back'): M4, ('Rueben', 'Revenge of the Sith'): M5, ('Rueben', 'A New Hope'): M6,
                         ('Rachlin', 'A New Hope'): M7, ('Rachlin', 'The Empire Strikes Back'):M8 , ('Rachlin', 'Return of the Jedi'): M9,
                         ('Rachlin', 'Attack of the Clones'): M10}
    
    
    GPH = PropertyGraph(All_nodes, All_relationships)

    #create visualization
    #GPH.visualize()
    
    #create subgraph visualization
    People = GPH.subgraph(['Rachlin', 'Strange', 'Rueben'])
    People.visualize()
    
    #what movies have john and laney both watched?
    Rachlin_movies = GPH.adjacent("Rachlin",node_category='movie')
    Strange_movies = GPH.adjacent("Strange",node_category='movie')
    print("John and Laney have both watched: "+ ", ".join(GPH.shared_set(Rachlin_movies, Strange_movies))+'\n')
    
    #what recommendations of movies can we give to john?
    print("Movie Recommendations for John: " +", ".join(GPH.recommendation_engine('Rachlin')))
if __name__ == '__main__':
    main()
    
                
        
    