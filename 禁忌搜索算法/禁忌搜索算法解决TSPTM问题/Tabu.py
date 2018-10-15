#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 14 19:57:26 2018

@author: signal

"""
#代码一共分为main()算法的主体框架
#ReadIn_and_Initialization()初始化所有的变量,完成数据读入操作并存储
#Construction()禁忌算法的初始解
#Calculation()禁忌算法计算对应解的适应值
#Tabu_Search()禁忌算法对邻域进行搜索并选择对应操作进行禁忌
#Check()用来检验解是否满足对应的所有约束
#Output()输出结果

#初始化全局变量
#除仓库外的节点数目
import time
start=time.clock()
import copy
import math
import numpy as np

Customer_Number=100
#车辆最大容量
Capacity=200
#搜索迭代次数
Iter_Max=500

#禁忌长度 禁止在之后的20次迭代中对禁忌表中所记录的状态进行改变,这里的20禁忌长度
Tabu_tenure=20
#无穷大
INF=float("inf")
Alpha=1.0
Beta=1.0
Sita=0.5

class Customer_Type(object):
        def __init__(self,Number,R,X,Y,Begin,End,Service,Demand):
            self.Number=int(Number)#节点自身编号
            self.R=int(R)#节点所属车辆路径编号
            self.X=float(X)#节点横坐标
            self.Y=float(Y)#节点纵坐标
            self.Begin=float(Begin)#节点访问的最早时间
            self.End=float(End)#节点访问的最晚时间
            self.Service=float(Service)#节点的服务时长
            self.Demand=float(Demand)#节点的需求
            
class  Route_Type(object):
    def __init__(self,Load,SubT,Dis,V):
        self.Load=float(Load)#单条路径承载量
        self.SubT=float(SubT)#单条路径违反各节点时间窗约束时长总和
        self.Dis=float(Dis)#单条路径总长度
        self.V=V#单条路径上顾客节点序列
        
def Distance(C1,C2):
    return math.sqrt(math.pow((float(C1.X)-float(C2.X)),2)+math.pow((float(C1.Y)-float(C2.Y)),2))
##ReadIn_and_Initialization()初始化所有的变量,完成数据读入操作并存储
Customer=[None]
Route=[None]
Route_Ans=[None]
Graph=[None]*(Customer_Number+2)
for i in range(len(Graph)):
    Graph[i]=[None]*(Customer_Number+2)
Vehicle_Number=Customer_Number#由于无车辆数量限制,因此将上限设为顾客总数
def ReadIn_and_Initialization():
    global Customer_Number
    global Capacity
    global Iter_Max
    global Tabu_tenure
    global INF
    global Customer
    global Route
    global Route_Ans
    global Graph
    global Ans
    f=open('data/R101.txt','r')
    lines=f.readlines()
    Customer_Type_Value=[None]
    for line in lines:
        Customer_Type_Parameter=[]
        for db in line.split():
            Customer_Type_Parameter.append(float(db))
        Customer_Type_Value.append(Customer_Type_Parameter)
    #初始化Customer和Route
    for i in range(1,Customer_Number+2):
        Customer.append(Customer_Type(Customer_Type_Value[i][0],-1,Customer_Type_Value[i][1],Customer_Type_Value[i][2],Customer_Type_Value[i][4],Customer_Type_Value[i][5],Customer_Type_Value[i][6],Customer_Type_Value[i][3]))
        Route.append(Route_Type(0.0,0.0,0.0,[]))
        Route_Ans.append(Route_Type(0.0,0.0,0.0,[]))
    f.close()    
    #初始化每条路径,默认路径首尾在仓库,且首仓库最早最晚时间均为原仓库最早时间,尾仓库则均为原仓库的最晚时间
    for i in range(1,Vehicle_Number+2):
        Route[i].V.append(copy.deepcopy(Customer[1]))
        Route[i].V.append(copy.deepcopy(Customer[1]))
        Route[i].V[0].End=Route[i].V[0].Begin
        Route[i].V[1].Begin=Route[i].V[1].End
        Route[i].Load=0
        
    Ans=INF
    for i in range(1,Customer_Number+2):
        for j in range(1,Customer_Number+2):
            Graph[i][j]=Distance(Customer[i],Customer[j])
ReadIn_and_Initialization()            
#将文件读入到系统中,通过Customer列表中的对象进行保存,根据车辆的数量初始化路线列表,路线的首尾都是仓库节点(Customer[1]),将路径的承载量置为零
#创建一个列表矩阵,存储各各节点之间的距离
#Construction()禁忌算法的初始解
def Construction():
    global Customer_Number
    global Capacity
    global Iter_Max
    global Tabu_tenure
    global INF
    global Customer
    global Route
    global Route_Ans
    global Graph
    
    Customer_Set=[None]*(Customer_Number+1)
    for i in range(1,Customer_Number+1):
        Customer_Set[i]=i+1
    #Customer_Set [None,2,3,4,5……,101]
    Sizeof_Customer_Set=copy.deepcopy(Customer_Number)
    Current_Route=1
    
    #以满足容量约束为目的的随机初始化
    #即随机挑选一个节点插入到第m条路径中,若超过容量约束,则插入第m+1条路径
    #且插入路径的位置由该路径上已经存在的各节点最早时间的升序决定
    while Sizeof_Customer_Set>0:
#        print("Sizeof_Customer_Set",Sizeof_Customer_Set)
        #产生1~Sizeof_Customer的随机整数,第一次是1……100
        K=np.random.randint(1,Sizeof_Customer_Set+1)
        #获取随机索引的数值
        C=Customer_Set[K]
        #将当前的数值赋值为Customer_Set最后一个数值并将最后一个数值减去
        Customer_Set[K]=Customer_Set[Sizeof_Customer_Set]
        Sizeof_Customer_Set-=1
        
#        print("用户的编号:",Customer[C].Number)
#        print("所属的路线:",Current_Route)
        #找到随机节点能插入的位置,要求大于前者的最早时间,小于后者的.Load单条路径的承载量,Capacity车辆的承载量
        #如果当前的路线的承载量+新加入的用户节点的服务量>车辆承载量,就换另一条路线
        if Route[Current_Route].Load+Customer[C].Demand>Capacity:
            Current_Route+=1
        #循环当前路线中存在的节点,找到要插入的位置要求当前节点的时间窗起始时间>=上一个节点的开始时间,<=下一个节点的起始时间
        #循环从0……Route中的节点数-1
        for i in range(len(Route[Current_Route].V)-1):
            if Route[Current_Route].V[i].Begin<=Customer[C].Begin and Customer[C].Begin<=Route[Current_Route].V[i+1].Begin:
                #插入
                Route[Current_Route].V.insert(i+1,Customer[C])
                #路径的承载量+插入节点的插入量
                Route[Current_Route].Load+=Customer[C].Demand
                Customer[C].R=Current_Route
                break
        #如果没有合适的位置进行插入,将重新寻找
        
    #初始化计算超过容量约束的总量和超过时间窗约束的总量
    #填写Route中的SubT和Dis属性
    for i in range(1,Vehicle_Number+1):
        #获取每条路径的第一个节点时间窗的起始时间,这里一直是节点1的Begin时间0
        ArriveTime=Route[i].V[0].Begin
        Route[i].SubT=0.0#单条路径违反各节点时间窗约束时长总和
        Route[i].Dis=0.0#单条路径总长度
        #循环每条路径中节点,从第2个节点开始,第一个节点是1仓库
        for j in range(1,len(Route[i].V)):
            #ArriveTime 累加路径中所有的上个节点的服务时间+上个节点的到这个节点的路程时间
            ArriveTime=ArriveTime+Route[i].V[j-1].Service+Graph[Route[i].V[j-1].Number][Route[i].V[j].Number]
            Route[i].Dis+=Graph[Route[i].V[j-1].Number][Route[i].V[j].Number]
            #SubT统计
            #如果到达这个节点的时间已经大于时间窗结束的时间,用到达这个节点的时间-时间窗结束的时间就是
            if ArriveTime>Route[i].V[j].End:
                #SubT累加超过的时间值
                Route[i].SubT=Route[i].SubT+ArriveTime-Route[i].V[j].End
            else:
                #如果连时间窗的起始时间都没到,快递员需要等待到时间窗的起始时间,
                if ArriveTime<Route[i].V[j].Begin:
                    ArriveTime=Route[i].V[j].Begin
Construction()

for i in range(1,len(Route)):
    if len(Route[i].V)>2:
        print("初始第",i,"号路线包含的节点",end=" ")
        for j in range(len(Route[i].V)):
            print(Route[i].V[j].Number,end=" ")
        print("")
#计算路径规划R的目标函数值
#目标函数主要由三部分组成:D路径总长度(优化目标),Q超出容量约束总量,T超出时间窗约束总量
#目标函数结构为F(R)=D+Alpha*Q+Beta*T,第一项为问题最小化目标,后两项为惩罚部分,Alpha与Beta为变量,分别根据当前解是否满足两个约束进行变化
#R (Route是修改后的路线) Cus(删除和插入的节点索引) NewR(插入的节点路径的索引)
def Calculation(R,Cus,NewR):
    global Customer_Number
    global Capacity
    global Iter_Max
    global Tabu_tenure
    global INF
    global Alpha
    global Beta
    D=0#路径总长度
    T=0#超出时间窗约束总量
    Q=0#超出容量约束总量
    #计算每条路径超出容量约束的总量
    #循环次数1……100
    for i in range(1,Vehicle_Number+1):
        #在路径中找节点数目大于2且路径的承载量超过容量的
        if len(R[i].V)>2 and R[i].Load>Capacity:
            #求超出承载量上限的差值,统计到Q变量中
            Q=Q+R[i].Load-Capacity
    #计算单条路径上各个节点超出 时间窗约束的总量(仅更新进行移除和插入节点操作的两条路径)
    ArriveTime=0
    #将Cus下标对应的路径的超出 时间窗约束的总量置零
    R[Customer[Cus].R].SubT=0
    #循环1……路径中节点数的次数 重新计算移除路径中的超出时间窗约束的总量
    for j in range(1,len(R[Customer[Cus].R].V)):
        #前一个节点的服务时间+上一个节点到这个节点的时间距离
        ArriveTime=ArriveTime+R[Customer[Cus].R].V[j-1].Service+Graph[R[Customer[Cus].R].V[j - 1].Number][R[Customer[Cus].R].V[j].Number]
        #如果Arrive大于路径中这个节点的结束时间,说明没在节点规定的时间窗到达,SubT统计超出的部分
        if ArriveTime>R[Customer[Cus].R].V[j].End:
            R[Customer[Cus].R].SubT=R[Customer[Cus].R].SubT+ArriveTime-R[Customer[Cus].R].V[j].End
        else:
            #不到节点的开始时间,ArriveTime调整到节点的开始时间
            if ArriveTime<R[Customer[Cus].R].V[j].Begin:
                ArriveTime=R[Customer[Cus].R].V[j].Begin
    
    ArriveTime=0
    R[NewR].SubT=0
    #计算插入的路径中超出时间窗约束的总量
    #循环1……新路径中节点的数目
    for j in range(1,len(R[NewR].V)):
        ArriveTime=ArriveTime+R[NewR].V[j-1].Service+Graph[R[NewR].V[j-1].Number][R[NewR].V[j].Number]
        if ArriveTime>R[NewR].V[j].End:
            R[NewR].SubT=R[NewR].SubT+ArriveTime-R[NewR].V[j].End
        else:
            if ArriveTime<R[NewR].V[j].Begin:
                ArriveTime=R[NewR].V[j].Begin
    
    #循环1……100
    #计算路径总SubT统计到T
    #SubT计算总的超出时间窗的值
    for i in range(1,Vehicle_Number+1):
        T+=R[i].SubT
    
    #计算所有路径的总长度
    for i in range(1,Vehicle_Number+1):
        D+=R[i].Dis
    return D+Alpha*Q+Beta*T

#for i in range(1,len(Route)):
#    if len(Route[i].V)>2:
#        print("初始第",i,"号路线包含的节点")
#        for j in range(len(Route[i].V)):
#            print(Route[i].V[j].Number)
#Tabu_Search()禁忌算法对邻域进行搜索并选择对应操作进行禁忌
#禁忌表 用于禁忌节点的插入操作 矩阵大小102*102 索引0……101*0……101
Tabu=[[None]*(Customer_Number+2)]*(Customer_Number+2)
#禁忌表 用于禁忌拓展新路径或使用新车辆 大小102*102 索引0……101
TabuCreate=[None]*(Customer_Number+2)

def Check(R):
    global Alpha
    global Sita
    global Beta
    global Capacity
    global Vehicle_Number
    Q=0
    T=0
    
    for i in range(1,Vehicle_Number+2):
        if len(R[i].V)>2 and R[i].Load>Capacity:
            Q=Q+R[i].Load-Capacity
    
    for i in range(1,Vehicle_Number+1):
        T+=R[i].SubT
    #调整alpha的值
    #载重没有不满足的，降低Alpha
    if Q==0 and Alpha>=0.001:
        Alpha/=(1+Sita)
    else:
        #提高惩罚值所占的比重
        if Q!=0 and Alpha<=2000:
            Alpha*=(1+Sita)
    
    if T==0 and Beta>=0.001:
        Beta/=(1+Sita)
    else:
        if T!=0 and Beta<=2000:
            Beta*=(1+Sita)
            
    if T==0 and Q==0:
        return True
    else:
        return False
    
def Copy_Route():
    global Vehicle_Number
    for i in range(1,Vehicle_Number):
        Route_Ans[i].Load=Route[i].Load
        Route_Ans[i].V.clear()
        for j in range(0,len(Route[i].V)):
            Route_Ans[i].V.append(Route[i].V[j])
def Tabu_Search():
    global Ans
    global Customer_Number
    global Capacity
    global Iter_Max
    global Tabu_tenure
    global INF
    
    Temp1=0.0
    Temp2=0.0
    #禁忌搜索采用插入算子,即从一条路径中选择一点插入到另一条路径中
    #在该操作下形成的领域中选取使目标函数最小化的解
    #循环的范围2……101
    #初始化Iteration迭代对象
    for i in range(2,Customer_Number+2):
        #循环的范围1……100
        for j in range(1,Vehicle_Number+1):
            Tabu[i][j]=0
        TabuCreate[i]=0
    #迭代的次数    
    Iteration=0
    #开始进行迭代
    while Iteration<Iter_Max:
        print(Iteration,end=" ")
        Iteration+=1
        BestC=0
        BestR=0
        BestP=0
        P=0#存放节点在路径中的索引位置
        BestV=INF#用来存放最好的适应值
        #循环2……101从2号节点开始遍历(从2开始才是配送的节点)
        for i in range(2,Customer_Number+2):
            #1……当前节点所在的路线中所包含的节点的数目
            #下面的for循环从节点所包含的路径中找到节点所在的位置,在路径中的索引存放在P中
           for j in range(1,len(Route[Customer[i].R].V)):
                #如果当前节点所在路径中的节点的编号和路径
                if Route[Customer[i].R].V[j].Number==i:
                    P=j
                    break
           #从节点原路径承载量中去除该节点的服务量
           Route[Customer[i].R].Load-=Customer[i].Demand
           #从节点原路径中去除该节点所组成的路径并重组
           #减去路径中前一个节点到当前节点的距离,再减去当前节点到下一个节点的距离,加上前一个节点和后一个节点的距离
           Route[Customer[i].R].Dis=Route[Customer[i].R].Dis - Graph[Route[Customer[i].R].V[P - 1].Number][Route[Customer[i].R].V[P].Number] - Graph[Route[Customer[i].R].V[P].Number][Route[Customer[i].R].V[P + 1].Number] + Graph[Route[Customer[i].R].V[P - 1].Number][Route[Customer[i].R].V[P + 1].Number]
           #在路径中删除当前节点
           del(Route[int(Customer[i].R)].V[P])
           #循环1……100 删除节点后开始遍历路径
           for j in range(1,Vehicle_Number+1):
               #禁忌插入操作
               #如果路径中节点的数量大于2 并且 禁忌节点的插入操作的禁忌表中的数据小于等于迭代次数（非空车并且禁忌表中的数据<迭代次数）
               #或者路径中节点的数量等于2 并且 禁忌拓展新路径或使用新车辆的禁忌表小于等于迭代次数（空车并且车辆禁忌表中的数据<迭代次数）
               if (len(Route[j].V)>2 and Tabu[i][j]<=Iteration) or (len(Route[j].V)==2 and TabuCreate[i]<=Iteration):
                   #循环次数1……路径中节点的数目,如果是满足的路径进入节点列表进行循环
                   for l in range(1,len(Route[j].V)):
                       #找到节点的之前路径不在当前路径中,就加入进去
                       #找不存在索引为i的路线
                       if Customer[i].R!=j:
                           #加入路径的承载量
                           Route[j].Load+=Customer[i].Demand
                           #加入路径的总长度
                           Route[j].Dis=Route[j].Dis - Graph[Route[j].V[l - 1].Number][Route[j].V[l].Number]+ Graph[Route[j].V[l - 1].Number][Customer[i].Number] + Graph[Route[j].V[l].Number][Customer[i].Number];
                           #在节点新路径中插入节点
                           Route[j].V.insert(l,Customer[i])
                           #单条路径 违反各节点时间窗约束 时长总和
                           #之前路线的SubT的值(原值还没有改变SubT)
                           Temp1=copy.deepcopy(Route[Customer[i].R].SubT)
                           #当前路径中SubT的值(原值)
                           Temp2=copy.deepcopy(Route[j].SubT)
                           #i是节点的索引,j是插入路径的索引,返回一个判断当前所有路径的适应值
                           #Calculation()计算对应解的适应值(修改过的)
                           TempV=Calculation(Route,i,j)
                           #在当前路径中寻找最好的插入位置
                           if TempV<BestV:
                               #存放最好的适应值
                               BestV=TempV
                               #操作的节点,插入的路径,插入的位置
                               BestC=i
                               BestR=j
                               BestP=l
                           #复原
                           Route[Customer[i].R].SubT=Temp1
                           Route[j].SubT=Temp2
                           del(Route[j].V[l])
                           Route[j].Load-=Customer[i].Demand
                           Route[j].Dis=Route[j].Dis + Graph[Route[j].V[l - 1].Number][Route[j].V[l].Number] - Graph[Route[j].V[l - 1].Number][Customer[i].Number] - Graph[Route[j].V[l].Number][Customer[i].Number]
           #复原操作
           Route[Customer[i].R].V.insert (P,Customer[i])
           Route[Customer[i].R].Load += Customer[i].Demand
           Route[Customer[i].R].Dis = Route[Customer[i].R].Dis + Graph[Route[Customer[i].R].V[P - 1].Number][Route[Customer[i].R].V[P].Number] + Graph[Route[Customer[i].R].V[P].Number][Route[Customer[i].R].V[P + 1].Number] - Graph[Route[Customer[i].R].V[P - 1].Number][Route[Customer[i].R].V[P + 1].Number]
        #如果是新创建的路径
        if  len(Route[BestR].V) == 2:
            #将其放入到禁忌表中，在过了这个迭代次数后才能将该节点添加到新的路径中
            TabuCreate[BestC]=Iteration+2*Tabu_tenure+np.random.randint(10)
        #将要调换的节点的之前所在的路径迭代次数放入禁忌表中在这个次数的迭代中不会在移动这个节点到其它的路径中
        Tabu[BestC][Customer[BestC].R]=Iteration+Tabu_tenure+np.random.randint(10)
        for i in range(1,len(Route[Customer[BestC].R].V)):
            if Route[Customer[BestC].R].V[i].Number==BestC:
                P=i
                break
        Route[Customer[BestC].R].Load -= Customer[BestC].Demand
        Route[Customer[BestC].R].Dis = Route[Customer[BestC].R].Dis - Graph[Route[Customer[BestC].R].V[P - 1].Number][Route[Customer[BestC].R].V[P].Number] - Graph[Route[Customer[BestC].R].V[P].Number][Route[Customer[BestC].R].V[P + 1].Number] + Graph[Route[Customer[BestC].R].V[P - 1].Number][Route[Customer[BestC].R].V[P + 1].Number]
        del(Route[Customer[BestC].R].V[P])
        
        Route[BestR].Dis = Route[BestR].Dis - Graph[Route[BestR].V[BestP - 1].Number][Route[BestR].V[BestP].Number]+ Graph[Route[BestR].V[BestP - 1].Number][Customer[BestC].Number] + Graph[Route[BestR].V[BestP].Number][Customer[BestC].Number]
        Route[BestR].Load += Customer[BestC].Demand
        Route[BestR].V.insert(BestP,Customer[BestC])
        
        ArriveTime=0
        Route[BestR].SubT=0
        #重新计算路径中的SubT的值
        for j in range(1,len(Route[BestR].V)):
            ArriveTime = ArriveTime + Route[BestR].V[j - 1].Service + Graph[Route[BestR].V[j - 1].Number][Route[BestR].V[j].Number]
            if ArriveTime>Route[BestR].V[j].End:
                Route[BestR].SubT = Route[BestR].SubT + ArriveTime - Route[BestR].V[j].End
            else:
                if ArriveTime<Route[BestR].V[j].Begin:
                    ArriveTime=Route[BestR].V[j].Begin
        #重新计算插入节点的所在路径的SubT的值
        ArriveTime=0
        Route[Customer[BestC].R].SubT = 0
        for j in range(1,len(Route[Customer[BestC].R].V)):
            ArriveTime=ArriveTime + Route[Customer[BestC].R].V[j - 1].Service + Graph[Route[Customer[BestC].R].V[j - 1].Number][Route[Customer[BestC].R].V[j].Number]
            if ArriveTime > Route[Customer[BestC].R].V[j].End:
                Route[Customer[BestC].R].SubT = Route[Customer[BestC].R].SubT + ArriveTime - Route[Customer[BestC].R].V[j].End
            else:
                if ArriveTime < Route[Customer[BestC].R].V[j].Begin:
                    ArriveTime = Route[Customer[BestC].R].V[j].Begin
        #为节点重新赋值
        Customer[BestC].R=BestR
        #如果优打破禁忌规则
        #Check()方法修改Alpha和Beta的值，如果载重和时间窗约束都满足并且优于之前的值，保存到最优的路径变量中
        if Check(Route)==True and Ans>BestV:
            Copy_Route()
            Ans=BestV
Tabu_Search()
M=0
for i in range(1,Vehicle_Number+1):
    if len(Route[i].V)>2:
        M+=1
        print("No.",M,":")
        for j in range(len(Route[i].V)-1):
            print(Route[i].V[j].Number,"->",end=" ")
        print(Route[i].V[len(Route[i].V) - 1].Number)
Check_Ans=0.0
for i in range(1,Vehicle_Number+1):
    for j in range(1,len(Route[i].V)):
        Check_Ans+=Graph[Route[i].V[j - 1].Number][Route[i].V[j].Number]
print("总成本:",Check_Ans)
#for i in range(1,len(Route_Ans)):
#    if len(Route_Ans[i].V)>2:
#        print("处理后第",i,"号路线包含的节点")
#        for j in range(len(Route_Ans[i].V)):
#            print(Route_Ans[i].V[j].Number)
#Tabu_Search()禁忌算法对邻域进行搜索并选择对应操作进行禁忌
end=time.clock()
print("程序所用时间:",end-start)