# 文本层次聚类

特点：
1. 实现简单版凝聚层次聚类算法 (时间复杂度O(N^3)，不消耗内存)
2. 实现优化版凝聚层次聚类算法 (时间复杂度O(N^2*logN)，消耗内存)
3. 实现单路径层次聚类算法 (时间复杂度O(N^2)，不消耗内存)

## 测试运行

运行脚本为do_hcluster.py，测试命令如下：

    python do_hcluster.py  test.u8.txt 1 2 0.4 test.out
    
    doc_num & feature_num: 1000 9226
    hierarchy_cluster: 1000 0.4
    cosine_similarity cost: 0
    cost: test.u8.txt   0.40    10

默认结果是在输入文本每一行追加两列：**簇id**和**簇大小**。如果要更好地观察结果，可以按照簇的大小从大到小输出，并且将相同簇的文本输出在一起，如下：

    cut -f 1,4-5 test.out |sort -t$'\t' -k3nr,3 -k2n,2 > test.out.new

## 依赖

+ conda install python=2.7
+ conda install scikit-learn=0.19.1

## 参考

《Introduction to Information Retrieval》[第17章](https://nlp.stanford.edu/IR-book/)
