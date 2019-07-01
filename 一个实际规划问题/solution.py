import random
from collections import Counter
from gurobipy import *
def general_Data(n):
    """根据传入的节点的数量来按照要求生成随机数量的数据"""
    people={}
    counter=random.randint(50,200)*n
    print("总金额",counter)
    print("平均每人",counter/n)
    tmp_e=0
    for i in range(n):
        now_m=counter-tmp_e
        if now_m==0:
            people[i]=0
            continue
        people[i]=random.randint(0,round(now_m/n))*n
        tmp_e+=people[i]
    return people,counter/n,counter
def solution(people,mean,counter):
    """根据传入的支付情况进行处理"""
    c=Counter(people).most_common() 
    print(c)
    one_group=[]#j
    two_group=[]#i
    M=[]
    P=[]
    for i in range(len(c)):
        if c[i][1]>mean:
            one_group.append(c[i][0])
            M.append(c[i][1]-mean)
            continue
        if c[i][1]<mean:
            two_group.append(c[i][0])
            P.append(mean-c[i][1])
            continue
    s_num=len(two_group)#S^{'}
    s2_num=len(one_group)#S
    #注意这里重新调整索引，即one_group和two_group按照顺序从0开始索引
    xxx=[[] for i in range(s_num)]
    m=[[] for i in range(s_num)]
    model=Model("mp")
    model.setParam("OutputFlag",0)
    expr=LinExpr()
    for i in range(s_num):
        for j in range(s2_num):
            xxx[i].append(model.addVar(0,1,1,vtype=GRB.INTEGER,name="xxx"+str(i)+str(j)))
            expr.addTerms(1,xxx[i][j])
            m[i].append(model.addVar(0,counter,1,vtype=GRB.INTEGER,name="m"+str(i)+str(j)))
    model.setObjective(expr,GRB.MINIMIZE)
    for j in range(s2_num):
        model.addConstr(quicksum(xxx[i][j]*m[i][j] for i in range(s_num))==M[j])
    for i in range(s_num):
        model.addConstr(quicksum(xxx[i][j]*m[i][j] for j in range(s2_num))==P[i])
    model.optimize()
    if model.status==GRB.OPTIMAL:
        print("有解")
        for i in range(s_num):
            for j in range(s2_num):
                value_x=model.getVarByName("xxx"+str(i)+str(j))
                value_m=model.getVarByName("m"+str(i)+str(j))
                if value_x.x!=0:
                    print(str(two_group[i])+"给"+str(one_group[j])+"转"+str(value_m.x))
    else:
        print("无解")
if __name__ == "__main__":
    people,mean,counter=general_Data(10)
    solution(people,mean,counter)