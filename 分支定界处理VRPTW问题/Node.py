import copy

from Data import Data


class Node(object):
    data=Data()
    d=None
    node_cost=None
    lp_x=None
    node_x_map=None
    node_x=None
    node_routes=None
    node_servetimes=None
    def __init__(self,data):
        self.data=data
        self.node_cost=data.big_num
        self.lp_x=[([([None]*data.veh_num) for i in range(data.vertex_num)]) for i in range(data.vertex_num)]
        self.node_x_map=[([([0]*data.veh_num) for i in range(data.vertex_num)]) for i in range(data.vertex_num)]
        self.node_x=[([0]*data.vertex_num) for i in range(data.vertex_num)]
        self.node_routes=[]
        self.node_servetimes=[]
    def note_copy(self):
        new_node=Node(self.data)
        new_node.d=self.d
        new_node.node_cost=self.node_cost
        for i in range(len(self.lp_x)):
            for j in range(len(self.lp_x[i])):
                new_node.lp_x[i][j]=copy.deepcopy(self.lp_x[i][j])
        for i in range(len(self.node_x)):
            new_node.node_x[i]=copy.deepcopy(self.node_x[i])
        for i in range(len(self.node_x_map)):
            for j in range(len(self.node_x_map[i])):
                new_node.node_x_map[i][j]=copy.deepcopy(self.node_x_map[i][j])
        for i in range(len(self.node_routes)):
            new_node.node_routes.append(copy.deepcopy(self.node_routes[i]))
        for i in range(len(self.node_servetimes)):
            new_node.node_servetimes.append(copy.deepcopy(self.node_servetimes[i]))
        return new_node
        
    def __lt__(self,other):
        return self.node_cost<other.node_cost
