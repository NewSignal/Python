import pandas as pd
import numpy as np
import networkx as nx
from random import sample
import matplotlib.pyplot as plt

data=pd.read_excel("data/test.xlsx","Customer_data")
print(type(data["first_receive_tm"][55]))
#在前1000个节点中随机选取200个客户节点
choice_index=sample(range(1,1001),200)
pos=[[data["lng"][0],data["lat"][0]]]
#获取它们的位置信息
for i in choice_index:
    pos.append([data["lng"][i],data["lat"][i]])
choice_index_2=sample(range(1102,1201),20)
for i in choice_index_2:
    pos.append([data["lng"][i],data["lat"][i]])
G=nx.Graph()
G.add_nodes_from(range(201+20))
nodecolor=[]
for i in range(221):
    if i <201:
        nodecolor.append("b")
    else:
        nodecolor.append("r")
nx.draw(G,pos,with_labels=True,node_size=200,node_color=nodecolor)
plt.show()

