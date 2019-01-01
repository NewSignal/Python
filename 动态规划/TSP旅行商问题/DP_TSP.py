# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 14:36:34 2018

@author: 14395
"""
import numpy as np
import copy
import time
INF=float("inf")
start_time=time.clock()
#一共6个节点(v1,v2,v3,v4,v5,v6),其中v1是起点也是终点\n

graph=np.array([[0,16,16,7,13,6],
                [16,0,9,5,19,7],
                [16,9,0, 7,9,6],
                [7,5, 7,0,7,7],
                [13,19,9,7,0,13],
                [6,7,6,7,13,0]])
def Remove(subset,j):
    dest=[]
    for i in subset:
        if i==j:
            continue
        dest.append(i)
    return dest
def generateOpttour():
    global P
    global vertex
    
    path="1->"
    Set=copy.deepcopy(vertex)
    start=0
    while len(Set)!=0:
        idd=settoid(Set)
        path+=str(P[start][idd]+1)+"->"
        Set=Remove(Set,P[start][idd])
        start=P[start][idd]
    path+="1"
    print(path)
        
#根据出发的节点找到关于它的所有的子集
def getsubsets(vertex):
    global idtoset
    #子集的数量用2进制来表示
    #这里最后sure_flag得到的是1000000 即2^6种子集 1向左移动6位
    sure_flag =1<<len(vertex)
    #idd存放所有的子集一共2^n种情况
    idd=0
    #列成表格，横着是出发点的所有子集
    for i in range(sure_flag):
        #index是节点编号对应的索引0对应节点v1
        index=0
        k=i
        s=[]
        while k>0:
            if (k&1) >0:
                s.append(vertex[index])
            k>>=1
            index+=1
        idtoset[idd]=s
        idd+=1
def settoid(Aminusj):
    global idtoset
    for i in idtoset.keys():
        if np.all(idtoset[i]==Aminusj):
            return i
#所有子集的情况
idtoset={}
#N 节点的数量
n=len(graph)
#vertex 顶点的编号
vertex=np.arange(1,n)
#给idtoset赋值
getsubsets(vertex)
#记录每种子集的距离
D=np.array([([0]*(1<<len(vertex))) for i in range(n)])
P=np.array([([0]*(1<<len(vertex))) for i in range(n)])

for i in range(1,n):
    D[i][0]=graph[i][0]
    
for k in range(1,n-1):
    #遍历子集的所有情况
    for v_id in range(0,len(idtoset)):
        subset=copy.deepcopy(idtoset[v_id])
        #将子集中元素的数量不满足的子集剔除
        if len(subset)!=k:
            continue
        for i in range(1,n):
            if (i in subset):
                continue
            v_min=10000
            value=0
            for j in subset:
                #从子集中移除j元素
                Aminusj=Remove(subset,j)
                idj=settoid(Aminusj)
                value=graph[i][j]+D[j][idj]
                if value<v_min and value!=0:
                    v_min=value
                    P[i][v_id]=j
            if v_min<9999:
                D[i][v_id]=v_min
Vminusv0=copy.deepcopy(vertex)
vminusv0id=settoid(vertex)
v_min=INF
for j in vertex:
    Vminusv0j=Remove(Vminusv0,j)
    idj=settoid(Vminusv0j)
    if graph[0][j]!=0 and D[j][idj]!=0:
        value=graph[0][j]+D[j][idj]
    else:
        value=0
        print("会出现吗？*****************************")
    if value<v_min and value!=0:
        v_min=value
        P[0][vminusv0id]=j
D[0][vminusv0id]=v_min

generateOpttour()
end_time=time.clock()
print("程序运行时间:",end_time-start_time)

                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                