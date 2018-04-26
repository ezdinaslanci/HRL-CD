import math
import statistics
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx


class GraphX:

    def __init__(self):
        self.graph = nx.Graph()
        self.row = self.col = 0
        self.initiationSets = defaultdict(list)

    def addEdge(self, source, destination):
        self.graph.add_edge(self.intToStr(source), self.intToStr(destination))

    def hasEdge(self, source, destination):
        return self.graph.has_edge(self.intToStr(source), self.intToStr(destination))

    def createMapToGraph(self, map):
        #add edges
        self.row = len(map)
        self.col = len(map[0])
        for i in range(len(map)):
            for j in range(len(map[0])):
                if map[i, j] in ['F', 'X']:
                    continue

                value = self.hexToBin4(map[i, j])
                if not int(value[0]):   #left
                    self.graph.add_edge(self.intToStr([i, j]), self.intToStr([i, j-1]))

                if not int(value[1]):   #up
                    self.graph.add_edge(self.intToStr([i, j]), self.intToStr([i-1, j]))

                if not int(value[2]):   #right
                    self.graph.add_edge(self.intToStr([i, j]), self.intToStr([i, j + 1]))

                if not int(value[3]):   #down
                    self.graph.add_edge(self.intToStr([i, j]), self.intToStr([i+1, j]))

    def setInitiationSets(self, minPD, minHeight, MeanFilterWindowSize, goalCoordinates):
        # All shortest path in graph

        # self.condition.acquire()
        # while True:
        #     graph = nx.copy.deepcopy(self.graph)
        #     if graph:
        #         break
        #     self.condition.wait()  # sleep until item becomes available
        # self.condition.release()

        try:
            graph = nx.copy.deepcopy(self.graph)
        except:
            return

        # print("[subgoals] ", end="")

        initiationSets = defaultdict(list)
        if len(graph) < 15:
            return
        path = nx.all_pairs_shortest_path(graph)
        shortestPaths = defaultdict(list)
        numberOfShortestPaths = 0
        for source, dummy in path.items():
            for destination, shortestPath in dummy.items():
                numberOfShortestPaths = numberOfShortestPaths + 1
                for p in shortestPath:
                    shortestPaths[p].append(shortestPath)

        betcen = {}
        for node in graph:
            betcen[node] = len(shortestPaths[node])/numberOfShortestPaths

        #subgoal detection
        dummyBetcen = self.weightedMeanFilter(graph, betcen, MeanFilterWindowSize)

        # Peak detection by using betcen values
        subgoals = defaultdict(list)
        # set goal state as subgoal
        subgoals[self.intToStr(goalCoordinates)] = shortestPaths[self.intToStr(goalCoordinates)]

        while True:
            maxKey = max(dummyBetcen, key=dummyBetcen.get)
            if dummyBetcen[maxKey] < minHeight:
                break
            neighbours = nx.ego_graph(graph, maxKey, minPD)
            for n in neighbours:
                dummyBetcen[n] = -1
            subgoals[maxKey] = shortestPaths[maxKey]

        # print("[init] ", end="\n")

        # print(len(subgoals))

        # define initiation set for each subgoal
        for subgoal in subgoals:
            numOfOccursForEachNode = defaultdict(lambda: 0)
            totalTOccurs = 0
            for path in subgoals[subgoal]:
                for node in path:
                    if node == subgoal:
                        continue
                    numOfOccursForEachNode[node] = numOfOccursForEachNode[node] + 1
                    totalTOccurs = totalTOccurs + 1

            numOfOccursForEachNode = self.weightedMeanFilter(graph, numOfOccursForEachNode, MeanFilterWindowSize)
            numOfOccursForEachNode = self.weightedMeanFilter(graph, numOfOccursForEachNode, MeanFilterWindowSize)

            averageOccurs = 0
            for key, value in numOfOccursForEachNode.items():
                averageOccurs += value

            averageOccurs /= len(numOfOccursForEachNode)

            dummyInitiationSet = defaultdict(lambda: 0)

            for node in graph:
                if numOfOccursForEachNode[node] >= averageOccurs:
                    dummyInitiationSet[node] = 1

            dummyInitiationSet = self.medianFilter(graph, dummyInitiationSet, 5)
            dummyInitiationSet = self.medianFilter(graph, dummyInitiationSet, 5)
            dummyInitiationSet = self.medianFilter(graph, dummyInitiationSet, 5)
            for node in graph:
                if dummyInitiationSet[node] and (not subgoal == node):
                    initiationSets[subgoal].append(node)

        self.initiationSets = initiationSets
        # print(self.initiationSets)

    def medianFilter(self, graph, data, medianSize):
        medFilt = {}
        for currentNode in graph:
            neighbours = nx.ego_graph(graph, currentNode, medianSize)
            medianList = []
            for n in neighbours:
                medianList.append(data[n])
            medFilt[currentNode] = math.ceil(statistics.median(medianList))

        return medFilt

    def meanFilter(self, graph, data, meanSize):
        meanFilt = {}
        for currentNode in graph:
            neighbours = nx.ego_graph(graph, currentNode, meanSize)
            meanValue = 0
            for n in neighbours:
                meanValue = meanValue + data[n]

            meanFilt[currentNode] = meanValue/len(neighbours)
        return meanFilt

    def weightedMeanFilter(self, graph,  data, meanSize):
        meanFilt = {}
        for currentNode in graph:
            neighbours = nx.ego_graph(graph, currentNode, meanSize)
            meanValue = 0
            for n in neighbours:
                dist = len(nx.shortest_path(graph, source=currentNode, target=n)) - 1
                meanValue = meanValue + data[currentNode]/(1 + dist)

            meanFilt[currentNode] = meanValue/len(neighbours)
        return meanFilt

    def intToStr(self, coordinate):
        return str(coordinate[0]) + "_" + str(coordinate[1])

    def strToInt(self, s):
        x, y = s.split("_")
        return [int(x), int(y)]

    def hexToBin4(self, number):
       return str('{0:04b}'.format(int(number, 16)))

    def buildPosDict(self):
        posDict = dict()
        for node in self.graph:
            posDict[node] = self.strToInt(node)

    def drawGraph(self):
        posDict = dict()
        colorList = []
        bc = nx.betweenness_centrality(self.graph)

        for node in self.graph:
            pos = self.strToInt(node)
            posDict[node] = [pos[1], self.row - pos[0] - 1]
            colorList.append(bc[node])

        nx.draw_networkx(self.graph, pos=posDict, node_size=500, node_color=colorList, cmap="hot", linewidths=2)
        plt.show()

# x = np.genfromtxt('mapFiles/halls.gwmap', dtype="str", skip_header=3)
# g.createMapToGraph(x)
# g.setInitiationSets()


# g = GraphX()
# bc = g.betcen
# plt.imshow(bc, cmap='hot', interpolation='hamming')
# plt.show()
# np.savetxt('betcen.txt', bc, fmt='%.3f')

