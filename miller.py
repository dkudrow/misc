#!/usr/bin/python

import sys

from fractions import gcd

def miller(N):

    result = ''

    for a in range(1,N):
        result += 'a = {0}: '.format(a)

        # Step 1 -- find gcd(a, N)
        g = gcd(a, N)
        if g > 1:
            result += 'success -- gcd({0}, {1}) = {2}\n'.format(a, N, g)
            continue

        # Step 2 -- find multiplicative order of a in (Z/N Z)x
        s = 1
        while (a**s) % N != 1:
            s = s + 1

        # Step 3 -- 
        if s % 2 == 1:
            result += 'failure -- {0} has order {1} in (Z/{2} Z)x\n'.format(a, s, N)
            continue

        # Step 4 -- 
        if (a**(s / 2) + 1) % N == 0:
            result += 'failure -- {0}**({1}) + 1 mod {2} = {3}\n'.format(a, s/2, N, (a**(s / 2) + 1) % N)
            continue

        # Step 5 -- compute non-trivial factors of N
        g_1 = gcd((a**(s/2) - 1), N)
        g_2 = gcd((a**(s/2) + 1), N)
        result += 'success -- {0}, {1}\n'.format(g_1, g_2)

    return result


if __name__ == '__main__':
    try:
        print miller(int(sys.argv[1]))
    except IndexError:
        print 'Usage: ./miller <N>'
