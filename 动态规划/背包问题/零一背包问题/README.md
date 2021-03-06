# 零一背包问题
零一背包问题:有n种重量和价值分别为Wi和Vi的物品。从这些物品中挑选出总重量不超过w的物品，每种物品都只能挑选一件，求所有挑选方案中价值总和的最大值。
看图“零一背包问题.png”,图中的数据与代码中的不同，是因为代码又重新运行了一遍，数据随机生成了。
dp[1][0]按照定义的意思是只有一个物品供选择，质量不能超过0。显然是不存在的，它的值等于之前的状态就好dp[0][0]=0,同理dp[1][1]=dp[1][2]=dp[1][3]=dp[1][4]=0
到dp[1][5]的时候，正好就一件物品W[0]=5,就可以拿这个物品，dp[1][5]存放这件物品的价值V[0]=9,之后上限增加了(dp[n][m]的m增加)，但是目前就一件物品不能
再增加价值了。
我们再添加W[1]=2,重量很轻呀。dp[2][0],dp[2][1]都因为载重上限限制无法加入，dp[2][2]的时候因为右W[0],W[1]两件物品了，W[1]=2那我可以将W[1]放到背包中，
dp[2][2]=W[1]的权值19，之后dp[2][3],dp[2][4],也因为上限没有将W[0]加入，dp[2][5]的时候，可以把W[1]拿出来，把W[0]放进去，是否执行这一步需要比较哪一个
的权值较大。max(d[i][j],dp[i][j-W[i]]+V[i])代码的作用就是比较两种情况那一个权值更大。dp[2][7]满足后，就可以将W[0]加入到背包中，
dp[2][7]=W[1]+W[0]的权值=9+19=28。
再加入W[2]=7,背包的承重上限不断加1，到dp[3][2]的时候，可以将W[1]放进背包中。再不断增加背包的承重，到dp[3][7]的时候，W[0]也可以放到背包中了。这里还有
一种可能是将之前的W[1]从背包中拿出来，放入W[2]刚好达到背包当前的上限。这时需要比较dp[2][7]和dp[2][7-7(W[2])]+V[2]的大小，dp[2][7]是上一步刚好放入
W[0],W[1]的情况。dp[2][0]+V[2]=1，相比较之下在背包载重达到7的时候放入W[0],W[1]的时候权值比单放入W[2]的情况要大。再后面随着背包载重的增加，也放不进去
W[2]，所以也一直保持前面的最大值。
W[3]进来了，同理dp[4][2]的时候这时W[0],W[3]同时争夺进入背包的权限。dp[4][2]=c=max(19,8),选择W[1]放入背包中。
dp[4][5]=max(dp[3][5],dp[3][3]+V[3])=max(19,27)选取W[1],W[3]放入背包。这里解释下dp[3][3],是只有W[0],W[1],W[2]的时候载重为3的时刻最大权值，
我们这时候添加了一个件物品W[3]，并将背包的载重刚好能放下W[3]，这样就将之前3个最大权值和4个最大权值进行比较。
后面同理……
