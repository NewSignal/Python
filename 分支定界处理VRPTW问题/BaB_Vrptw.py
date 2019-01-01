from collections import namedtuple
from queue import PriorityQueue

from gurobipy import GRB, LinExpr, Model, quicksum

from Data import Data
from Node import Node
import copy


class Bab_Vrptw(object):
    data=Data()
    node1=None
    node2=None
    deep=None
    pq=PriorityQueue()
    best_note=None
    cur_best=None
    record_arc=[]
    x_gap=None
    model=None
    x=None
    w=None
    cost=None
    x_map=None
    #Node=namedtuple("Node",["data","d","node_cost","lp_x","node_x_map","node_x","node_routes","node_servetimes"])
    #Data=namedtuple("Data",["vertex_num","veh_num","dist","arcs","s","a","b","cap","E","L","demands","gap"])
    def doubleCompare(self,a,b):
        if a-b>self.x_gap:
            return 1
        if b-a>self.x_gap:
            return -1
        return 0
    def __init__(self,data):
        self.data=data
        self.x_gap=data.gap
        self.routes=[[] for i in range(data.veh_num)]
        self.servetimes=[[] for i in range(data.veh_num)]
        self.x_map=[([([None]*data.veh_num) for i in range(data.vertex_num)]) for i in range(data.vertex_num)]
        self.x=[([([None]*data.veh_num) for i in range(data.vertex_num)]) for i in range(data.vertex_num)]
        self.w=[([None]*data.veh_num) for i in range(data.vertex_num)]
    def build_original_model(self,data):
        model=Model("original_model")
        model.setParam("OutputFlag",0)
        self.x=[([([None]*data.veh_num) for i in range(data.vertex_num)]) for i in range(data.vertex_num)]
        self.w=[([None]*data.veh_num) for i in range(data.vertex_num)]
        #变量
        for i in range(data.vertex_num):
            for k in range(data.veh_num):
                self.w[i][k]=model.addVar(0,GRB.INFINITY,1,GRB.CONTINUOUS,"w"+str(i)+","+str(k))
            for j in range(data.vertex_num):
                if data.arcs[i][j]==0:
                    self.x[i][j]=None
                else:
                    for k in range(data.veh_num):
                        self.x[i][j][k]=model.addVar(0,1,1,GRB.CONTINUOUS,"x"+str(i)+","+str(j)+","+str(k))
        #目标公式
        expr=LinExpr()
        for i in range(data.vertex_num):
            for j in range(data.vertex_num):
                if data.arcs[i][j]==0:
                    continue
                for k in range(data.veh_num):
                    expr.addTerms(data.dist[i][j],self.x[i][j][k])
        model.setObjective(expr,GRB.MINIMIZE)
        #约束
        original_con=[]
        #每个客户只能被一辆车服务一次
        for i in range(1,data.vertex_num-1):
            expr.clear()
            for k in range(data.veh_num):
                for j in range(data.vertex_num):
                    if data.arcs[i][j]==1:
                        expr.addTerms(1,self.x[i][j][k])
            original_con.append(model.addConstr(expr==1))
        #车辆必须从配送中心0出发
        for k in range(data.veh_num):
            expr.clear()
            for j in range(1,data.vertex_num):
                if data.arcs[0][j]==1:
                    expr.addTerms(1,self.x[0][j][k])
            original_con.append(model.addConstr(expr==1))
        #除开始和结束节点，每个客户节点的前驱和后继应该相等
        for k in range(data.veh_num):
            for j in range(1,data.vertex_num-1):
                expr1=LinExpr()
                expr2=LinExpr()
                for i in range(data.vertex_num):
                    if data.arcs[i][j]==1:
                        expr1.addTerms(1,self.x[i][j][k])
                    if data.arcs[j][i]==1:
                        expr2.addTerms(1,self.x[j][i][k])
                original_con.append(model.addConstr(expr1-expr2==0))
        #每辆车必须回到配送中心n+1
        for k in range(data.veh_num):
            expr.clear()
            for i in range(data.vertex_num-1):
                if data.arcs[i][data.vertex_num-1]==1:
                    expr.addTerms(1,self.x[i][data.vertex_num-1][k])
            original_con.append(model.addConstr(expr==1))
        #满足时间窗口约束
        M=1e5
        for k in range(data.veh_num):
            for i in range(data.vertex_num):
                for j in range(data.vertex_num):
                    if data.arcs[i][j]==1:
                        expr1=LinExpr()
                        expr2=LinExpr()
                        expr3=LinExpr()
                        expr1.addTerms(1,self.w[i][k])
                        expr2.addTerms(1,self.w[j][k])
                        expr3.addTerms(1,self.x[i][j][k])
                        original_con.append(model.addConstr(expr1+data.s[i]+data.dist[i][j]-expr2<=M*(1-expr3)))
        #到达时间在时间窗之内
        for k in range(data.veh_num):
            for i in range(1,data.vertex_num-1):
                expr.clear()
                for j in range(data.vertex_num):
                    if data.arcs[i][j]==1:
                        expr.addTerms(1,self.x[i][j][k])
                original_con.append(model.addConstr(data.a[i]*expr<=self.w[i][k]))
                original_con.append(model.addConstr(data.b[i]*expr>=self.w[i][k]))
        #时间窗在配送中心的时间窗之内
        for k in range(data.veh_num):
            original_con.append(model.addConstr(self.w[0][k]>=data.E))
            original_con.append(model.addConstr(self.w[data.vertex_num-1][k]>=data.E))
            original_con.append(model.addConstr(self.w[0][k] <= data.L))
            original_con.append(model.addConstr(self.w[data.vertex_num-1][k] <= data.L))
        #车辆的容量约束
        for k in range(data.veh_num):
            expr.clear()
            for i in range(1,data.vertex_num-1):
                for j in range(data.vertex_num):
                    if data.arcs[i][j]==1:
                        expr.addTerms(data.demands[i],self.x[i][j][k])
            original_con.append(model.addConstr(expr<=data.cap))
        self.model=model
    #将求解器中的值赋值到x_map中，并根据x_map的生成车辆路线，获得其成本
    def get_value(self):
        self.routes.clear()
        self.servetimes.clear()
        self.cost=0
        for k in range(self.data.veh_num):
            self.routes.append([])
            self.servetimes.append([])
        for i in range(self.data.vertex_num):
            for j in range(self.data.vertex_num):
                for k in range(self.data.veh_num):
                    self.x_map[i][j][k]=0
                if self.data.arcs[i][j]>0.5:
                    for k in range(self.data.veh_num):
                        self.x_map[i][j][k]=self.model.getVarByName("x"+str(i)+","+str(j)+","+str(k)).x
        #生成车辆路径
        for k in range(self.data.veh_num):
            terminate=True
            i=0
            self.routes[k].append(0)
            self.servetimes[k].append(0)
            while(terminate):
                for j in range(self.data.vertex_num):
                    if self.doubleCompare(self.x_map[i][j][k],0)==1:
                        self.routes[k].append(j)
                        self.servetimes[k].append(self.model.getVarByName("w"+str(j)+","+str(k)).x)
                        i=j
                        break
                if i == self.data.vertex_num-1:
                    terminate=False
        self.cost=self.model.objVal
            
    def init(self,lp):
        lp.build_original_model(data)
        lp.model.optimize()
        if lp.model.status == GRB.OPTIMAL:
            lp.get_value()
            number_of_invalid_paths=0
            for i in range(len(lp.routes)):
                if len(lp.routes[i])==2:
                    number_of_invalid_paths+=1
            if number_of_invalid_paths==0:
                self.data.veh_num-=1
                lp.model=Model("original_model")
                lp=Bab_Vrptw(self.data)
                return self.init(lp)
            else:
                self.data.veh_num-=number_of_invalid_paths
                lp.model=Model("original_model")
                lp=Bab_Vrptw(self.data)
                return self.init(lp)
        else:
            data.veh_num+=1
            lp.model=Model("original_model")
            lp=Bab_Vrptw(data)
            lp.build_original_model(data)
            lp.model.optimize()
            if lp.model.status == GRB.OPTIMAL:
                lp.get_value()
                return lp
            else:
                print("发现错误")
                return None 
    def copy_lp_to_node(self,lp,node):
        node.node_routes.clear()
        node.node_servetimes.clear()
        node.node_cost=lp.cost
        for i in range(len(lp.x_map)):
            for j in range(len(lp.x_map[i])):
                node.lp_x[i][j]=copy.deepcopy(lp.x_map[i][j])
        for i in range(len(lp.routes)):
            node.node_routes.append(copy.deepcopy(lp.routes[i]))
        for i in range(len(lp.servetimes)):
            node.node_servetimes.append(copy.deepcopy(lp.servetimes[i]))
    def is_one_zero(self,temp):
        if self.doubleCompare(temp,0)==0 or self.doubleCompare(temp,1)==0:
            return True
        else:
            return False
    def find_arc(self,x):
        record=[-1,-1,-1]
        for i in range(self.data.vertex_num):
            for j in range(self.data.vertex_num):
                if self.data.arcs[i][j]>0.5:
                    for k in range(data.veh_num):
                        if self.is_one_zero(x[i][j][k]):
                            continue
                        record[0]=i
                        record[1]=j
                        record[2]=k
                        return record
        return record
    def set_bound(self,node):
        for i in range(self.data.vertex_num):
            for j in range(self.data.vertex_num):
                if self.data.arcs[i][j]>0.5:
                    if node.node_x[i][j]==0:
                        for k in range(self.data.veh_num):
                            self.x[i][j][k].setAttr("LB",0.0)
                            self.x[i][j][k].setAttr("UB",1.0)
                    #禁止x ij 在所有的车辆上使用
                    elif node.node_x[i][j]==-1:
                        for k in range(self.data.veh_num):
                            self.x[i][j][k].setAttr("LB",0.0)
                            self.x[i][j][k].setAttr("UB",0.0)
                    else:
                        for k in range(self.data.veh_num):
                            if node.node_x_map[i][j][k]==1:
                                self.x[i][j][k].setAttr("LB",1.0)
                                self.x[i][j][k].setAttr("UB",1.0)
                            else:
                                self.x[i][j][k].setAttr("LB",0.0)
                                self.x[i][j][k].setAttr("UB",0.0)
    def branch_left_arc(self,lp,father_node,record):
        if record[0]==-1:
            return None
        new_node=Node(data)
        new_node=father_node.note_copy()
        new_node.node_x[record[0]][record[1]]=-1
        for k in range(data.veh_num):
            new_node.node_x_map[record[0]][record[1]][k]=0
        lp.set_bound(new_node)
        lp.model.optimize()
        if lp.model.status == GRB.OPTIMAL:
            lp.get_value()
            self.deep+=1
            new_node.d=self.deep
            lp.copy_lp_to_node(lp,new_node)
        else:
            new_node.node_cost=data.big_num
        return new_node
    def branch_right_arc(self,lp,father_node,record):
        if record[0]==-1:
            return None
        new_node=Node(data)
        new_node=father_node.note_copy()
        new_node.node_x[record[0]][record[1]]=1
        for k in range(data.veh_num):
            if k==record[2]:
                new_node.node_x_map[record[0]][record[1]][k]=1
            else:
                new_node.node_x_map[record[0]][record[1]][k]=0
        lp.set_bound(new_node)
        lp.model.optimize()
        if lp.model.status == GRB.OPTIMAL:
            lp.get_value()
            self.deep+=1
            new_node.d=self.deep
            lp.copy_lp_to_node(lp,new_node)
        else:
            new_node.node_cost = data.big_num
        return new_node
    def branch_and_bound(self,lp):
        self.cur_best=3000
        self.deep=0
        self.record_arc=[0,0,0]
        self.node1=Node(data)
        self.best_note=None
        self.pq=PriorityQueue()
        for i in range(len(lp.routes)):
            r=lp.routes[i]
            print()
            for j in range(len(r)):
                print(r[j],end=" ")
        #将lp对象转化为node节点
        lp.copy_lp_to_node(lp,self.node1)
        self.node2=self.node1.note_copy()
        self.deep=0
        self.node1.d=self.deep
        self.pq.put(self.node1)
        while not self.pq.empty():
            node=self.pq.get()
            if self.doubleCompare(node.node_cost,self.cur_best)>0:
                continue
            else:
                self.record_arc=lp.find_arc(node.lp_x)
                if self.record_arc[0]==-1:
                    if self.doubleCompare(node.node_cost,self.cur_best)==-1:
                        lp.cur_best=node.node_cost
                        lp.best_note=node
                    continue
                else:
                    self.node1=lp.branch_left_arc(lp, node, self.record_arc)
                    self.node2=lp.branch_right_arc(lp, node, self.record_arc)
                    if self.node1!=None and self.doubleCompare(self.node1.node_cost,self.cur_best)<=0:
                        self.pq.put(self.node1)
                    if self.node2!=None and self.doubleCompare(self.node2.node_cost,self.cur_best)<=0:
                        self.pq.put(self.node2)
data=Data()
data.Read_data(data,102)
lp=Bab_Vrptw(data)
lp=lp.init(lp)
lp.branch_and_bound(lp)
for i in range(len(lp.best_note.node_routes)):
    r=lp.best_note.node_routes[i]
    print()
    for j in range(len(r)):
        print(r[j],end=" ")

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
G=nx.Graph()
G.add_nodes_from(np.arange(lp.data.vertex_num))
line=lp.best_note.node_routes
lines=[]
for i in range(len(line)):
        for j in range(1,len(line[i])):
                arc=(line[i][j-1],line[i][j])
                if arc not in lines:
                        lines.append(copy.deepcopy(arc))
G.add_edges_from(lines)
pos=[]
for i in range(lp.data.vertex_num):
    pos.append((lp.data.vertexs[i][0],lp.data.vertexs[i][1]))
nx.draw(G,pos,with_labels=True)
plt.show()