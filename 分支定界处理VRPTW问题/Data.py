import pandas as pd
import math
import copy
import numpy as np
class Data(object):
    vertex_num=102
    E=None  		
    L=None   	
    veh_num=None
    cap=None
    vertexs=[]
    demands=[]
    vehicles=[]	
    a=[]
    b=[]
    s=[]
    arcs=[]
    dist=[]
    for i in range(vertex_num):
        one_arcs=[]
        one_dist=[]
        for j in range(vertex_num):
            one_arcs.append(0)
            one_dist.append(0)
        arcs.append(one_arcs)
        dist.append(one_dist)
    gap=1e-6
    big_num = 100000
    def Read_data(self,data,vertexnum):
        cin=pd.read_excel("data/test_VRPTW_data.xlsx")
        data.vertexnum=vertexnum
        data.veh_num=20
        data.cap=200
        for i in range(len(cin)):
            data.vertexs.append([cin["XCOORD"][i],cin["YCOORD"][i]])
            data.demands.append(cin["DEMAND"][i])
            data.a.append(cin["READYTIME"][i])
            data.b.append(cin["DUEDATE"][i])
            data.s.append(cin["SERVICETIME"][i])
        #新增最后一个和配送中心一样的节点
        data.vertexs.append(data.vertexs[0])
        data.demands.append(0)
        data.a.append(data.a[0])
        data.b.append(data.b[0])
        data.E=data.a[0]
        data.L=data.b[0]
        data.s.append(0)

        min1=1e15
        min2=1e15
        for i in range(data.vertex_num):
            for j in range(i,data.vertex_num):
                if i!=j:
                    data.dist[i][j]=round(math.sqrt((data.vertexs[i][0]-data.vertexs[j][0])**2+(data.vertexs[i][1]-data.vertexs[j][1])**2),1)
                    data.dist[j][i]=data.dist[i][j]
        data.dist[0][data.vertex_num-1]=0
        data.dist[data.vertex_num-1][0]=0
        print("距离的平均值：",np.mean(data.dist))
        for k in range(data.vertex_num):
            for i in range(data.vertex_num):
                for j in range(data.vertex_num):
                    if data.dist[i][j] > data.dist[i][k] + data.dist[k][j]:
                        data.dist[i][j] = data.dist[i][k] + data.dist[k][j]
        for i in range(data.vertex_num):
            for j in range(data.vertex_num):
                if i!=j:
                    data.arcs[i][j]=1
        for i in range(data.vertex_num):
            for j in range(data.vertex_num):
                if i==j:
                    continue
                if data.a[i]+data.s[i]+data.dist[i][j]>data.b[j] or data.demands[i]+data.demands[j]>data.cap:
                    data.arcs[i][j]=0
                if data.a[0]+data.s[i]+data.dist[0][i]+data.dist[i][data.vertex_num-1]>data.b[data.vertex_num-1]:
                    print("数据有问题")
        for i in range(1,data.vertex_num-1):
            if data.b[i] - data.dist[0][i] < min1:
                min1 = data.b[i] - data.dist[0][i]
            if data.a[i] + data.s[i] + data.dist[i][data.vertex_num-1] < min2:
                min2 = data.a[i] + data.s[i] + data.dist[i][data.vertex_num-1]
        if data.E > min1 or data.L < min2:
            print("数据有问题")
        data.arcs[data.vertex_num-1][0] = 0
        data.arcs[0][data.vertex_num-1] = 1
        for i in range(1,data.vertex_num-1):
            data.arcs[data.vertex_num-1][i] = 0
        for i in range(1,data.vertex_num-1):
            data.arcs[i][0] = 0