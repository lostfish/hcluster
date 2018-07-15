#!/usr/bin/python
#-*- encoding:utf-8 -*-

import sys
import time
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from minheap import MinHeap

g_debug=0

def hierarchy_cluster(points, titles, max_dist = 0.55):
    '''Standard hierarchical clustering with min-heap O(n^2*logn)
    '''
    N = points.shape[0]
    print "hierarchy_cluster:",N, 1-max_dist
    if N == 0:
        return []
    start = int(time.time())
    dist_mat = 1 - cosine_similarity(points)
    cost = int(time.time()) - start
    print "cosine_similarity cost:", cost

    P = []
    for i in range(N):
        a = [dist_mat[i,j] for j in range(N)]
        heap = MinHeap(a)
        heap.Delete(i)
        P.append(heap)

    I = [True for i in range(N)] #flag whether the point is valid
    clusters = [[i] for i in range(N)]
    merge_count = 0
    for i in range(N-1):
        min_dist = 1e10
        k1 = -1
        for ix,flag in enumerate(I):
            if not flag:
                continue
            dist = P[ix].Max()[0]
            if dist < min_dist:
                min_dist = dist
                k1 = ix
        if min_dist > max_dist:
            break
        k2 =  P[k1].Max()[1]
        if g_debug:
            print "merge_cluster_%d\t%d\t%d\t%.5f" % (merge_count, k1, k2, min_dist)
        I[k2] = False
        P[k1] = MinHeap([])
        for ix,flag in enumerate(I):
            if ix == k1 or not flag:
                continue
            P[ix].Delete(k1)
            P[ix].Delete(k2)

            a = []
            for c1 in clusters[ix]:
                for c2 in clusters[k1]:
                    a.append(dist_mat[c1, c2])
                for c2 in clusters[k2]:
                    a.append(dist_mat[c1, c2])
            new_dist = sum(a)/len(a)

            P[ix].Add(new_dist, k1)
            P[k1].Add(new_dist, ix)

        clusters[k1].extend(clusters[k2])
        merge_count += 1

    labels = range(N)
    for cluster_id,docs in enumerate(clusters):
        if not I[cluster_id]:
            continue
        for doc_id in docs:
            labels[doc_id] = cluster_id
    return labels

def hierarchy_cluster2(points, titles, max_dist=0.55):
    '''Standard hierarchical clustering without min-heap O(n^3)
    '''
    N = points.shape[0]
    print "hierarchy_cluster2:",N, 1-max_dist
    if N == 0:
        return []
    start = int(time.time())
    dist_mat = 1 - cosine_similarity(points)
    cost = int(time.time()) - start
    print "cosine_similarity cost:", cost

    del_flags = [False for i in range(N)] #flag whether the point is deleted
    clusters = [[i] for i in range(N)]
    merge_count = 0
    while True:
        min_dist = 1e10
        min_pair = (-1, -1)
        for i in range(N):
            if del_flags[i]:
                continue
            for j in range(i+1,N):
                if del_flags[j]:
                    continue
                # calc cluster distance
                count = 0
                avg_dist = 0.0
                for ix1 in clusters[i]:
                    for ix2 in clusters[j]:
                        avg_dist += dist_mat[ix1, ix2]
                        count += 1
                avg_dist = avg_dist / count

                # choose the minimum
                if avg_dist < min_dist:
                    min_dist = avg_dist
                    min_pair = (i, j)
        i, j = min_pair
        if min_dist > max_dist:
            break
        clusters[i].extend(clusters[j])
        del_flags[j] = True
        if g_debug:
            print "merge_cluster_%d\t%d\t%d\t%.5f" % (merge_count, i, j, min_dist)
        merge_count += 1

    labels = range(N)
    for cluster_id,docs in enumerate(clusters):
        if del_flags[cluster_id]:
            continue
        for doc_id in docs:
            labels[doc_id] = cluster_id
    return labels

def single_pass_cluster(points, titles, max_dist = 0.55):
    '''
    points is sparse matrix
    sensitive to data order
    titles is used for debugging if needed
    '''
    N = points.shape[0]
    print "single_pass_cluster:",N, 1-max_dist
    dist_mat = 1 - cosine_similarity(points)
    clusters = []
    knn = N
    for i in range(N):
        x1 = points[i]
        cur_min = 1e10
        cur_index = -1
        for ix,data in enumerate(clusters):
            avg_dist = 0
            dist_list = [dist_mat[i,j] for j in data[:knn]]
            avg_dist = sum(dist_list)/len(dist_list)
            if avg_dist < cur_min:
                cur_min = avg_dist
                cur_index = ix
        if cur_min < max_dist:
            clusters[cur_index].append(i)
            #cluster_first_id = clusters[cur_index][0]
            #print "cluster:\t%.5f\t%d\t%d\t%s\t%s" % (cur_min, i, cluster_first_id, titles[i], titles[cluster_first_id])
        else:
            clusters.append([i]) #new cluster
    labels = range(N)
    for cluster_id,docs in enumerate(clusters):
        for doc_id in docs:
            labels[doc_id] = cluster_id
    return labels

def parse_words(word_str, only_word=False):
    '''Parse the string of segmented words
    Args:
        word_str: a str like hello@nx||world@nx ...
    Returns:
        a: a list of (word, pos)
    '''
    words = word_str.split("||")
    a = []
    for x in words:
        i = x.rfind('@')
        if i == -1:
            continue
        word = x[:i].lower()
        if only_word:
            a.append(word)
        else:
            pos = x[i+1:]
            a.append((word, pos))
    return a

def read_text_file(text_file, title_seg_field, content_seg_field):
    '''Read text file with segmented words
    '''
    x = []
    doc_list = []
    use_title = True if title_seg_field != -1 else False
    use_content = True if content_seg_field != -1 else False
    with open(text_file) as f:
        for line in f:
            line = line.rstrip('\n')
            s =line.split('\t')
            if use_title:
                title_words = parse_words(s[title_seg_field], True)
            if use_content:
                cont_words = parse_words(s[content_seg_field], True)
            words = "%s %s" % (' '.join(title_words), ' '.join(cont_words))
            x.append(words)
            doc_list.append(line)
    return x, doc_list

def calc_cluster_freq(y_pred):
    '''Calc cluster frequency by cluster labels
    '''
    cluster_freq = defaultdict(int)
    for k in y_pred:
        cluster_freq[k] += 1
    return cluster_freq

def run(text_file, title_seg_field, content_seg_field, max_dist, out_file, single_pass=False, charset='utf-8'):
    '''Read text file and do hierarchical clustering

    The clustering result is adding cluster_id and cluster_freq to each input line
    '''
    corpus, doc_list = read_text_file(text_file, title_seg_field, content_seg_field)
    stop_list = [] # TODO
    vectorizer = TfidfVectorizer(max_df=0.7, encoding=charset, stop_words = stop_list, min_df=3, lowercase = True, smooth_idf=False, norm='l2') #smooth_idf=False -> log(N/n,2)+1   smooth_idf=True -> log(N/(n+1),2)
    doc_matrix = vectorizer.fit_transform(corpus)
    print "doc_num & feature_num: %d %d" % doc_matrix.shape

    if single_pass:
        y_pred = single_pass_cluster(doc_matrix, doc_list, max_dist)
    else:
        y_pred = hierarchy_cluster(doc_matrix, doc_list, max_dist)
        #y_pred = hierarchy_cluster2(doc_matrix, doc_list, max_dist) #too slow

    fout = open(out_file, 'w')
    cluster_freq = calc_cluster_freq(y_pred)
    for i,cluster_id in enumerate(y_pred):
        info = "%s\t%d\t%d\n" % (doc_list[i], cluster_id, cluster_freq[cluster_id])
        fout.write(info)
    fout.close()

def main():
    if len(sys.argv) != 6:
        print "usage: %s text_file title_seg_field content_seg_field least_simi out_file" % __file__
        print "\nThe clustering result is adding cluster_id and cluster_freq to each input line"
        sys.exit(-1)

    text_file = sys.argv[1]
    title_seg_field = int(sys.argv[2])
    content_seg_field = int(sys.argv[3]) #-1 means no this field
    least_simi = float(sys.argv[4])
    max_dist = 1 - least_simi
    out_file = sys.argv[5]

    start = int(time.time())
    run(text_file, title_seg_field, content_seg_field, max_dist, out_file)
    cost = int(time.time()) - start
    print "cost: %s\t%.2f\t%d" % (text_file, least_simi, cost)

def test():
    least_simi = 0.4
    run("test.u8.txt", 1, 2, 1-least_simi, "test.out")

if __name__ == '__main__':
    #test()
    main()
