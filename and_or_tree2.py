#!/usr/bin/python

import itertools
import random
import time


def int_to_bit_array(n):
    return [(n % 2**(i+1)) >> i for i in range(3, -1, -1)]


def bit_array_to_int(a):
    return reduce(lambda x, y: (x << 1) + y, a)


def frange(start, stop, step=1.0):
    i = start
    while i < stop:
        yield i
        i += step


def f(n):
    x = int_to_bit_array(n)
    return (x[0] or x[1]) and (x[2] or x[3])


def generate_algorithms():
    algorithms = []
    for output in range(8):
        for i, j in itertools.combinations(range(4), 2):
            if (i == 0 and j == 1) or (i == 2 and j == 3):
                algorithms.append(Algorithm((i, j), output))
            else:
                algorithms.append(Algorithm((i, j), output | 0x8))

    return algorithms


class Algorithm():

    def __init__(self, queries, outputs):
        self.query_1 = queries[0]
        self.query_2 = queries[1]
        self.outputs = outputs
        self.output_array = int_to_bit_array(outputs)

    def evaluate(self, n):
        x = int_to_bit_array(n)
        a = x[self.query_1]
        b = x[self.query_2]
        return self.output_array[(a << 1) + b]

    def __repr__(self):
        return '[{},{}:{}{}{}{}]'.format(self.query_1+1, self.query_2+1, self.output_array[0], self.output_array[1], self.output_array[2], self.output_array[3])

    @staticmethod
    def generate():
        algorithms = []
        for output in range(8):
            for i, j in itertools.combinations(range(4), 2):
                if (i == 0 and j == 1) or (i == 2 and j == 3):
                    algorithms.append(Algorithm((i, j), output))
                else:
                    algorithms.append(Algorithm((i, j), (output << 1) | 0x1))

        return algorithms


class ResultMatrix():

    def __init__(self, algorithms):
        s = []
        for a in algorithms:
            s.append([1 if a.evaluate(x) == f(x) else 0 for x in range(16)])
        self.M = s
        self.size = len(s)

    def generate_q(self):
        prob_dist = [1.0 for i in range(len(self.M))]
        for i, j in itertools.combinations(range(len(self.M)), 2):
            if prob_dist[i] == 0 or prob_dist[j] == 0:
                continue
            a, b = self.M[i], self.M[j]
            a_supercedes_b, b_supercedes_a = True, True
            for k in range(16):
                if b_supercedes_a and a[k] == 1 and b[k] == 0:
                    b_supercedes_a = False
                if a_supercedes_b and b[k] == 1 and a[k] == 0:
                    a_supercedes_b = False
            if a_supercedes_b:
                # print '***\n{} supercedes {}'.format(i, j)
                # print '->{}\n<-{}'.format(a, b)
                prob_dist[j] = 0.0
            elif b_supercedes_a:
                # print '***\n{} supercedes {}'.format(j, i)
                # print '->{}\n<-{}'.format(b, a)
                prob_dist[i] = 0.0

        # prob_dist = [p * random.randint(0, 10) for p in prob_dist]
        # return [prob_dist[i] / sum(prob_dist) for i in range(self.size)]

        # prob_dist[0] = 0.0
        weights = [sum(a) for a in self.M]
        total_weight = sum([weights[i] * prob_dist[i] for i in range(self.size)])
        return [prob_dist[i] * weights[i] / total_weight for i in range(self.size)]

        # prob_dist = [0.0 for i in range(self.size)]
        # prob_dist[42] = prob_dist[47] = 0.325
        # prob_dist[0] = prob_dist[5] = .175

        return prob_dist

    def revise_q(self, q, max_a, min_a, amt=0.005):
        increment_probs = [i for i in range(self.size) if q[i] > 0 and i in max_a]
        decrement_probs = [i for i in range(self.size) if q[i] > 0 and i not in max_a]
        # decrement_probs = [i for i in range(self.size) if q[i] > 0 and i in min_a]
        balance = amt
        for i in decrement_probs:
            dec = min(amt / len(decrement_probs), q[i])
            q[i] -= dec
            balance -= dec
        for i in increment_probs:
            q[i] += (amt - balance) / len(increment_probs)

        return q

    def find_min_p(self, q):
        prob, failures = [], []
        for x in range(16):
            incorrect_algorithms = []
            prob_success = 0.0
            for a in range(len(q)):
                if q[a] > 0 and self.M[a][x] == 0:
                    incorrect_algorithms.append(a)
                prob_success += self.M[a][x] * q[a]
            prob.append(prob_success)
            failures.append(incorrect_algorithms)

        # for i in range(16): print '{}: {:.2} - {}'.format(i, prob[i], failures[i])

        p = [1.0 if prob[i] == min(prob) else 0 for i in range(16)]
        return [i / sum(p) for i in p], min(prob)

    def find_max_q(self, p):
        prob = []
        for a in self.M:
            prob_success = 0.0
            for x in range(16):
                prob_success += a[x] * p[x]
            prob.append(prob_success)

        # for i in range(len(self.S)): print '{}: {:.2}'.format(i, prob[i])
        return [i for i in range(len(self.M)) if prob[i] == max(prob)], max(prob), [i for i in range(self.size) if prob[i] == min(prob)]

    def success_rates_by_a(self, q=None):
        print 'Success rate by algorithm\n<algorithm>: <successes> <sigma>'
        if not q:
            q = [1.0 for i in range(len(self.M))]
        for a in range(len(self.M)):
            if q[a] > 0:
                print '{}:\t{}\t{}'.format(a, sum(self.M[a]), self.M[a])

    def success_rates_by_x(self, q=None):
        print 'Success rate by input\n<input>: <successes> <sigma>'
        if not q:
            q = [1.0 for i in range(len(self.M))]
        for x in range(16):
            s = [self.M[s][x] for s in range(len(self.M)) if q[s] > 0]
            print '{}:\t{}\t{}'.format(x, sum(s), s)


if __name__ == '__main__':
    A = Algorithm.generate()
    S = ResultMatrix(A)
    q = S.generate_q()

    for i in range(len(A)):
        a = A[i]
        if q[i] > 0: print '{}\t{}'.format(i, a)
    S.success_rates_by_a(q)
    S.success_rates_by_x(q)

    x, prob_x = S.find_min_p(q)
    print 'S* = {:.2}, x = {}'.format(prob_x, x)
    a_max, prob_a, a_min = S.find_max_q(x)
    print 'S* = {:.2}, a_max = {}, a_min = {}'.format(prob_a, a_max, a_min)
    S.revise_q(q, a_max, a_min)

    while False:
        # print sum(q), q
        x, prob_x = S.find_min_p(q)
        print 'S* = {:.2}, x = {}'.format(prob_x, x)
        a_max, prob_a, a_min = S.find_max_q(x)
        print 'S* = {:.2}, a_max = {}, a_min = {}'.format(prob_a, a_max, a_min)
        S.revise_q(q, a_max, a_min)
        # time.sleep(1)

    # for f in frange(0.0, 0.5, 0.01):
    #     q = [0.0 for i in range(len(A))]
    #     q[42] = q[47] = 0.5 - f
    #     q[0] = q[5] = 0.0 + f
    #     print 'q = {}'.format(q)
    #     x, prob_x = S.find_min_p(q)
    #     print 'S* = {:.2}, x = {}'.format(prob_x, x)
    #     a, prob_a = S.find_max_q(x)
    #     print 'S* = {:.2}, a = {}'.format(prob_a, a)
