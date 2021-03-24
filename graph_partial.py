'''
    DS2500
    Spring 2021
    Lab 6 -- OOP and Inheritance
    
    This is a class for a directed, unweighted graph. In the driver,
    we create an empty graph and then add edges one at a time. 
    
    We have an attribute named graph_dict where the key of the dictionary
    is a vertex name, and the value is a set of all the vertex's neighbors:
        {A : {B, C, D},
         B : {A},
         C : {A, B},
         D : {B} }
         
'''

import collections as col
import pandas as pd
import networkx as nx

class Graph:
    ''' Graph class, for a directed, unweighted graph with an adjacency list
        For an edge A-B, it appears in the adjaency list as A-B and B-A
        Attributes: dictionary of key = vertex, value = set of neighbors
        Methods: shortest_path from one vertex to another, 
                add_vertex given a vertex, add_edge given two vertices
    '''
        
    def __init__(self, V = [], E = []):
        self.G = {}
        for v in V:
            self.add_vertex(v)
        for u, v in E:
            self.add_edge(u, v)
            
    def add_vertex(self, v):
        if v not in self.G:
            self.G[v] = set()
        
    def add_edge(self, u, v):
        self.add_vertex(u)
        self.add_vertex(v)
        self.G[u].add(v)
            
        
    def __getitem__(self, v):
        """ Return all vertices adjacent to v (overriding index operator!)"""
        adj = self.G.get(v, set())
        return list(adj)
        

    def shortest_path(self, start, end):
        backtrack = {} # When visiting a node, remember where you came from
        visited = {start} # The set of nodes that have been visited already
        Q = col.deque()
        Q.appendleft(start)
        
        
        # Visit all nodes using bfs and save backtrack info
        while len(Q)>0: # Q is not empty
            current = Q.pop()
            adj = self.G[current]
            for v in adj:
                if v not in visited:
                    visited.add(v)
                    Q.appendleft(v)
                    backtrack[v] = current
                    
        # Construct path from start to end by working backward from the end
        path = []
        current = end
        while current != start:
            path.append(current)
            if current not in backtrack: # No path start->end exists
                return []
            current = backtrack[current]
            
        # Complete the path
        path.append(start)
        path.reverse()
        return path
    
    def __repr__(self):
        
        graph_str = ''
        for v in self.G:
            graph_str += '['+v+'] => ' + str(self[v]) + '\n'
        return graph_str

    def get_edges(self, edges = []):
        for u in self.G:
            for v in self.G[u]:
                edges.append((u,v))
        return edges

    def toDF(self, columns=['u', 'v']):
        df = pd.DataFrame(columns = columns)
        for (u,v) in self.get_edges():
            df = df.append({columns[0]:u, columns[1]:v}, ingnore_index=True)
        return df
def main():
    
    
    V = list("ABCDEFGH")
    E = [('A','B'), ('A', 'C'), ('B','C'), ('C', 'D'), ('D', 'E'), 
         ('E','F'), ('B','F'), ('A','G'), ('A','H'), ('H', 'F')]
    
    g = Graph(V,E)

    edges = g.get_edges()
    print(edges)
    

   
    
    
if __name__ == '__main__':
    main()
