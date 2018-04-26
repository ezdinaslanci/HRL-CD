import numpy as np
import networkx as nx


class GraphX:
    def __init__(self, map):
        self.map = map
        self.row, self.col = np.shape(self.map)
        self.graph = self.createMapToGraph(self.map)
        self.betcen = self.calculateBetcen(self.graph)

    def createMapToGraph(self, map):
        graph = nx.DiGraph()

        #create nodes from size of map
        for i in range(self.row):
            for j in range(self.col):
                if self.map[i, j] in ['F', 'X']:
                    continue
                graph.add_node(self.intToStr(i, j))

        #add edges
        for i in range(self.row):
            for j in range(self.col):
                if self.map[i, j] in ['F', 'X']:
                    continue

                value = self.hexToBin4(map[i, j])
                if not int(value[0]):   #left
                    graph.add_edge(self.intToStr(i,j), self.intToStr(i, j-1))

                if not int(value[1]):   #up
                    graph.add_edge(self.intToStr(i, j), self.intToStr(i-1, j))

                if not int(value[2]):   #right
                    graph.add_edge(self.intToStr(i, j), self.intToStr(i, j + 1))

                if not int(value[3]):   #down
                    graph.add_edge(self.intToStr(i, j), self.intToStr(i+1, j))
        return graph

    def calculateBetcen(self, graph):
        betcen = nx.betweenness_centrality(graph)
        betweenness = np.zeros((self.row, self.col), dtype=np.float)
        for node in graph.node:
            # print(node)
        # return
            betweenness[self.strToInt(node)] = betcen[node]
        return betweenness

    def intToStr(self, x, y):
        return str(x) + "_" + str(y)

    def strToInt(self, s):
        x, y = s.split("_")
        return int(x), int(y)

    def hexToBin4(self, number):
       return str('{0:04b}'.format(int(number, 16)))

#
# x = np.array([['C', '6'], ['9', '3']])
# g = GraphX(x)
# print("MAP:")
# print(x)
# print("Betweenness Centrality")
# print(g.betcen)
#
# print("\n**********************")
#
# x = np.array([['C', '7'], ['9', '7']])
# g = GraphX(x)
# print("MAP:")
# print(x)
# print("Betweenness Centrality")
# print(g.betcen)
#
# print("\n**********************")
#
# x = np.array([['E', 'F'], ['9', '7']])
# g = GraphX(x)
# print("MAP:")
# print(x)
# print("Betweenness Centrality")
# print(g.betcen)

