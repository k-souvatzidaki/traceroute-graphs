import sys
sys.path.append('..\\traceroute')

from traceroute.traceroute import *

if __name__ == '__main__':
    print('Running test traceroutes')
    trace('google.com')
    trace('192.168.2.1')