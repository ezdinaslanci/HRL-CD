# -*- coding: utf-8 -*-
'''
Created on 24 Nis 2016

@author: Erbilcan
'''
import networkx as nx
from networkx.algorithms.bipartite.centrality import betweenness_centrality

#Verilen indexleri string biçimine dönüştürür
#Grraph node isimleri için oluşturuldu
#Örnek indToStr(3,5) "[3][5]" döndürür
def indToStr(i, j):
    return "["+str(i)+"]["+str(j)+"]"

def findIndex(grid, value):
    return [(index, row.index(value)) for index, row in enumerate(grid) if value in row]
    
def convertGridToGraph(gridmap, graph):
    #Graph nodeları oluşturan kod
    for k in range(len(gridmap)):
        for m in range(len(gridmap[k])):
            graph.add_node(indToStr(k,m))
    
    #Node'lar oluştuktan sonra Edge ekleme işlemi yapılır
    for i in range(len(gridmap)):
        for j in range(len(gridmap[i])):
            
            if gridmap[i][j]==1 or gridmap[i][j]<0: continue #Eğer duvarsa edge eklemeye zaten gerek yok
            
            elif gridmap[i][j]==0:
                #Köşeler
                if i==0 and j==0:   #Top-left corner
                    '''
                    print("["+str(i)+"]["+str(j)+"] için:")
                    print("\t ["+str((i+1))+"]["+str(j)+"] aşağı bakar.")
                    print("\t ["+str(i)+"]["+str((j+1))+"] sağa bakar.")
                    '''
                    
                    #Eğer duvar yoksa
                    if (gridmap[i+1][j]==0): graph.add_edge(indToStr(i, j), indToStr(i+1, j))   #Aşağı edge
                    if (gridmap[i][j+1]==0): graph.add_edge(indToStr(i, j), indToStr(i, j+1))   #Sağa edge
                elif i==0 and j==(len(gridmap[i])-1):  #Top-right corner
                    '''
                    print("["+str(i)+"]["+str(j)+"] için:")
                    print("\t ["+str((i+1))+"]["+str(j)+"] aşağı bakar.")
                    print("\t ["+str(i)+"]["+str((j-1))+"] sola bakar.")
                    '''
                    
                    if (gridmap[i+1][j]==0): graph.add_edge(indToStr(i, j), indToStr(i+1, j))   #Aşağı edge
                    if (gridmap[i][j-1]==0): graph.add_edge(indToStr(i, j), indToStr(i, j-1))   #Sola edge
                elif i==(len(gridmap)-1) and j==0:  #Lower-left corner
                    '''
                    print("["+str(i)+"]["+str(j)+"] için:")
                    print("\t ["+str((i-1))+"]["+str(j)+"] yukarı bakar.")
                    print("\t ["+str(i)+"]["+str((j+1))+"] sağa bakar.")
                    '''
                    
                    if (gridmap[i-1][j]==0): graph.add_edge(indToStr(i, j), indToStr(i-1, j))   #Yukarı edge
                    if (gridmap[i][j+1]==0): graph.add_edge(indToStr(i, j), indToStr(i, j+1))   #Sağa edge
                elif i==(len(gridmap)-1) and j==(len(gridmap[i])-1):  #Lower-right corner
                    '''
                    print("["+str(i)+"]["+str(j)+"] için:")
                    print("\t ["+str((i-1))+"]["+str(j)+"] yukarı bakar.")
                    print("\t ["+str(i)+"]["+str((j-1))+"] sola bakar.")
                    '''
                    
                    if (gridmap[i-1][j]==0): graph.add_edge(indToStr(i, j), indToStr(i-1, j))   #Yukarı edge
                    if (gridmap[i][j-1]==0): graph.add_edge(indToStr(i, j), indToStr(i, j-1))   #Sola edge
                #Kenarlar
                elif i==0: #Üst kenarda yukarı bakmaz
                    '''
                    print("["+str(i)+"]["+str(j)+"] için:")
                    print("\t ["+str((i+1))+"]["+str(j)+"] aşağı bakar.")
                    print("\t ["+str(i)+"]["+str((j-1))+"] sola bakar.")
                    print("\t ["+str(i)+"]["+str((j+1))+"] sağa bakar.")
                    '''
                    
                    if (gridmap[i+1][j]==0): graph.add_edge(indToStr(i, j), indToStr(i+1, j))   #Aşağı edge
                    if (gridmap[i][j-1]==0): graph.add_edge(indToStr(i, j), indToStr(i, j-1))   #Sola edge
                    if (gridmap[i][j+1]==0): graph.add_edge(indToStr(i, j), indToStr(i, j+1))   #Sağa edge
                elif i==(len(gridmap)-1):   #Alt kenarda aşağı bakmaz
                    '''
                    print("["+str(i)+"]["+str(j)+"] için:")
                    print("\t ["+str((i-1))+"]["+str(j)+"] yukarı bakar.")
                    print("\t ["+str(i)+"]["+str((j-1))+"] sola bakar.")
                    print("\t ["+str(i)+"]["+str((j+1))+"] sağa bakar.")
                    '''
                    
                    if (gridmap[i-1][j]==0): graph.add_edge(indToStr(i, j), indToStr(i-1, j))   #Yukarı edge
                    if (gridmap[i][j-1]==0): graph.add_edge(indToStr(i, j), indToStr(i, j-1))   #Sola edge
                    if (gridmap[i][j+1]==0): graph.add_edge(indToStr(i, j), indToStr(i, j+1))   #Sağa edge
                elif j==0:  #Sol kenarda sola bakmaz
                    '''
                    print("["+str(i)+"]["+str(j)+"] için:")
                    print("\t ["+str((i-1))+"]["+str(j)+"] yukarı bakar.")
                    print("\t ["+str((i+1))+"]["+str(j)+"] aşağı bakar.")
                    print("\t ["+str(i)+"]["+str((j+1))+"] sağa bakar.")
                    '''
                    
                    if (gridmap[i-1][j]==0): graph.add_edge(indToStr(i, j), indToStr(i-1, j))   #Yukarı edge
                    if (gridmap[i+1][j]==0): graph.add_edge(indToStr(i, j), indToStr(i+1, j))   #Aşağı edge
                    if (gridmap[i][j+1]==0): graph.add_edge(indToStr(i, j), indToStr(i, j+1))   #Sağa edge
                elif j==(len(gridmap[i])-1):    #Sağ kenarda sağa bakmaz
                    '''
                    print("["+str(i)+"]["+str(j)+"] için:")
                    print("\t ["+str((i-1))+"]["+str(j)+"] yukarı bakar.")
                    print("\t ["+str((i+1))+"]["+str(j)+"] aşağı bakar.")
                    print("\t ["+str(i)+"]["+str((j-1))+"] sola bakar.")
                    '''
                    
                    if (gridmap[i-1][j]==0): graph.add_edge(indToStr(i, j), indToStr(i-1, j))   #Yukarı edge
                    if (gridmap[i+1][j]==0): graph.add_edge(indToStr(i, j), indToStr(i+1, j))   #Aşağı edge
                    if (gridmap[i][j-1]==0): graph.add_edge(indToStr(i, j), indToStr(i, j-1))   #Sola edge
                #Ortadakiler
                else:
                    '''
                    print("["+str(i)+"]["+str(j)+"] için:")
                    print("\t ["+str((i-1))+"]["+str(j)+"] yukarı bakar.")
                    print("\t ["+str((i+1))+"]["+str(j)+"] aşağı bakar.")
                    print("\t ["+str(i)+"]["+str((j+1))+"] sağa bakar.")
                    print("\t ["+str(i)+"]["+str((j-1))+"] sola bakar.")
                    '''
                    
                    if (gridmap[i-1][j]==0): graph.add_edge(indToStr(i, j), indToStr(i-1, j))   #Yukarı edge
                    if (gridmap[i+1][j]==0): graph.add_edge(indToStr(i, j), indToStr(i+1, j))   #Aşağı edge
                    if (gridmap[i][j+1]==0): graph.add_edge(indToStr(i, j), indToStr(i, j+1))   #Sağa edge
                    if (gridmap[i][j-1]==0): graph.add_edge(indToStr(i, j), indToStr(i, j-1))   #Sola edge
            #---- WORMHOLE bulunursa
            elif gridmap[i][j]>1:   
                temp = gridmap[i][j]    #Degerini negatifini gridte aramak için temp degiskenine atar
                indices = findIndex(gridmap, -temp)     #Negatifinin index'ini bulur ve indices degiskenine atar
                graph.add_edge(indToStr(i,j), indToStr(indices[0][0], indices[0][1]))   #Pozitifinden negatifine edge koyar
                

#Module olarak kullanmak istersek bu method yeterli olacaktır.
def get_bet_cen(gridmap):
    G=nx.Graph()
    convertGridToGraph(gridmap, G)
    return nx.betweenness_centrality(G)
    
def main():
    G=nx.Graph()
    
    grid = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0],
			[0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
			[1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1],
			[0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
			[0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
			[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
			[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1],
			[1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
			[1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1],
			[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
			[0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0],
			[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]]
    
    convertGridToGraph(grid, G)
    bc = nx.betweenness_centrality(G)

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            print(str(grid[i][j])+" ", end="")
        print("")

    bcf = open("bc.dat", "w")

    for i in range(len(grid)):
        for j in range(len(grid[i])):
        	bcf.write("%.2f " % bc["[" + str(i) + "][" + str(j) + "]"])
        bcf.write("\n")

    bcf.close()

    
if __name__ == '__main__':
    main()