#! /usr/bin/env python
#encoding: utf-8

import random

class MinHeap(object):
    def __init__(self, data, keys = None):
        self.heap = data
        n = len(data)
        self.key_start = 0
        if keys:
            self.pos_list = keys # heap position index -> data key
            self.pos_map = dict(zip(keys, range(n))) # data key -> heap position index
        else:
            self.pos_list = range(n)
            self.pos_map = dict(zip(range(n), range(n)))
            self.key_start = n-1
        if n > 2:
            i = (n-1)>>1
            while i >= 0:
                self.AdjustDown(i, n)
                i -= 1
    def Max(self):
        return (self.heap[0], self.pos_list[0])

    def __SwapPos(self, i, j):
        if i != j:
            tmp = self.pos_list[i]
            self.pos_list[i] = self.pos_list[j]
            self.pos_list[j] = tmp

            self.pos_map[self.pos_list[i]] = i
            self.pos_map[self.pos_list[j]] = j

    def AdjustDown(self, i, n):
        while True:
            pos = i
            left = i*2 + 1
            right = left + 1
            if left < n and self.heap[i] > self.heap[left]:
                pos = left
            if right < n and self.heap[pos] > self.heap[right]:
                pos = right
            if  pos != i:
                tmp = self.heap[i]
                self.heap[i] = self.heap[pos]
                self.heap[pos] = tmp
                self.__SwapPos(i, pos)
                i = pos
            else:
                break

    def AdjustUp(self, i, endpos):
        while True:
            p = (i-1)/2
            #print "debug:",p,i,len(self.heap)
            if p >= endpos and self.heap[p] > self.heap[i]:
                tmp = self.heap[i]
                self.heap[i] = self.heap[p]
                self.heap[p] = tmp
                self.__SwapPos(i, p)
                i = p
            else:
                break

    def DeleteTop(self):
        n = len(self.heap)
        if n-1 != 0:
            self.heap[0] = self.heap[n-1]
            self.__SwapPos(0, n-1)
            self.AdjustDown(0, n-1)
        del self.heap[n-1]
        del self.pos_map[self.pos_list[n-1]]
        del self.pos_list[n-1]

    def Add(self, x, key=None):
        if key is not None and key in self.pos_map:
            print "add error: key has existed",str(key)
            return
        self.heap.append(x)
        n = len(self.heap)
        if key is None:
            key = self.key_start + 1
            self.key_start = key
            print "error: key is None", key
        self.pos_list.append(key)
        self.pos_map[key] = n-1
        self.AdjustUp(n-1, 0)

    def Delete(self, key):
        if key not in self.pos_map:
            print "delete error: key not in pos_map",key
            return
        pos = self.pos_map[key]
        n = len(self.heap)
        if pos != n-1:
            self.heap[pos] = self.heap[n-1]
            self.__SwapPos(pos, n-1)
            self.AdjustUp(pos, 0)
            self.AdjustDown(pos, n-1)
        del self.heap[n-1]
        del self.pos_map[self.pos_list[n-1]]
        del self.pos_list[n-1]

    def Validate(self, i, n):
        left = 2*i+1
        if left >= n:
            return True
        if self.heap[left] < self.heap[i]:
            return False
        right = left+1
        if right >= n:
            return True
        if self.heap[right] < self.heap[i]:
            return False
        return self.Validate(left, n)
        return self.Validate(right, n)

    def IsValid(self):
        n = len(self.heap)
        return self.Validate(0, n)

    def PrintHeap(self):
        print "heap:",self.heap
        print "pos:",self.pos_list
        a = [self.pos_map[k] for k in self.pos_list]
        print "pos_map:",a
        print "valid:", self.IsValid()
        #n = len(self.heap)
        #for i in range(n):
        #    depth = int(math.log(i+1, 2)) + 1
        #    sep = '  '*depth
        #    print "%s%s" % (sep, self.heap[i])

if __name__ == '__main__':
    n = 10
    random.seed(0)
    a = random.sample(range(100), n)
    print "raw:"
    for i,x in enumerate(a):
        print i,x
    h = MinHeap(a)
    h.PrintHeap()

    print "\nDeleteTop:"
    h.DeleteTop()
    h.PrintHeap()

    print "\nAdd:", a[0]
    #h.Add(a[0], 10)
    h.Add(a[0])
    h.PrintHeap()

    print "\nDelete key:", 2
    h.Delete(2)
    h.PrintHeap()

    h = MinHeap([])
    for i in range(1,10,2):
        print "\nadd:",i
        h.Add(i,i)
        h.PrintHeap()
