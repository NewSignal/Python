# -*- coding: utf-8 -*-
"""
Created on Wed May 22 17:09:20 2019

@author: 14395
"""
import matplotlib.pyplot as plt
import networkx as nx
import random
import numpy as np
from collections import Counter
from copy import deepcopy
pos=[]
nodes=[]
edges=[]
edge=[[0]*10 for i in range(10)]
choice_list=[0,0,1,1,1,1,1,1,1,1]
mark=[0]*10
G=nx.Graph()
n=10
m=len(edges)
minPath=float("inf")
mark[1]=1
all_mark=[]
all_value=[]
best_mark=[]

def dfs(cur,dst):
    global minPath
    global n
    global edge
    global mark
    global best_mark
    if minPath<dst:
        return 
    if cur==n-1:
        if mark not in all_mark:
            all_mark.append(deepcopy(mark))
            all_value.append(deepcopy(dst))
        if minPath>dst:
            minPath=dst
            best_mark=deepcopy(mark)
            return
    else:
        for i in range(n):
            if edge[cur][i]!=float("inf") and edge[cur][i]!=0 and mark[i]==0:
                result=Counter(mark)
                mark[i]=n-result[0]+1
                dfs(i,dst+edge[cur][i])
                mark[i]=0
        return
    
for i in range(10):
    r1=np.random.randint(100)
    r2=np.random.randint(100)
    pos.append((r1,r2))
    nodes.append(i)
for i in range(10):
    for j in range(10):
        if i!=j and np.random.choice(choice_list)==1:
            w=np.random.randint(50)
            edges.append((i,j,w))
            edge[i][j]=w
        else:
            edge[i][j]=float("inf")
G.add_nodes_from(nodes)
G.add_weighted_edges_from(edges)
nx.draw(G,pos,with_labels=True)
plt.show()

dfs(1,0)#节点1到节点9的最短路径
print("最小路径长度",minPath)
print("最短路径为:")
tmp_arc=[]
for i in range(1,11):
    if i in best_mark:
        print(best_mark.index(i),end="---")
    else:
        print("")
        break
print("所有路线")
for i in range(len(all_mark)):
    for k in range(1,11):
        if k in all_mark[i]:
            print(all_mark[i].index(k),end="---")
        else:
            print("")
            break
    print("对应的路线成本",all_value[i])

