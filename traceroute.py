"""
Implementation of traceroute command with raw sockets

Functions:
    trace(host, hops=30, port=33434, timeout=0.2)
    trace_pathviz(host, hops=30, port=33434, timeout=0.2, export_png = False)
"""
import socket
import sys
import datetime
import platform
import struct
from helpers import *


def trace(host, hops=30, port=33434, timeout=0.2) -> list:
    """
    Execute a traceroute to a remote host 

    Parameters:
        host: the host IP address or domain name
        hops: maximum number of hops before timeout (default: 30)
        port: application port used for traceroute (default: 33434)
        timeout: seconds before timeout (default: 0.2)
    """
    # check system compatibility of raw sockets
    is_compatible(platform.system())
    host_address = resolve(host)
    sys.stdout.write(f'Traceroute to host {host_address}\n')
    ttl = 1
    reached = False

    try:
        while ttl <= hops+1:
            start = datetime.datetime.now()
            try: 
                # receive icmp responses from hosts
                receive_icmp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
                receive_icmp.settimeout(timeout)
                receive_icmp.bind(('',port))
                # send udp messages with ttl = step
                send_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.getprotobyname('udp'))
                send_udp.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
                send_udp.sendto(''.encode(), (host_address, port))
            except PermissionError:
                sys.stdout.write('Run as root!! \n')
                exit(-1)

            step_address = None
            step_name = None
            try:
                packet, step_address = receive_icmp.recvfrom(512)
                icmp_header = packet[20:28]
                type, _, _, _, _ = struct.unpack(
                    "bbHHh", icmp_header
                )
                step_address = step_address[0]
                if type == ICMP_TIME_EXCEEDED:
                    try:
                        step_name = socket.gethostbyaddr(step_address)[0]
                    except socket.error:
                        step_name = step_address 
                elif type == ICMP_DESTINATION_UNREACHABLE:
                    step_name = host
                    reached = True

            except socket.error as e: # timeout reached
                sys.stdout.write(f'{ttl}: {int((datetime.datetime.now() - start).microseconds/1000)} ms * \n')
                ttl+= 1

            send_udp.close()
            receive_icmp.close()

            if step_address is not None:
                if step_address == step_name:
                    step_address = ''
                else:
                    step_address = f'[{step_address}]'
                sys.stdout.write(f'{ttl}: {int((datetime.datetime.now() - start).microseconds/1000)} ms {step_name} {step_address}\n')
            
            # next step
            ttl+= 1
            if reached:
                sys.stdout.write('Traceroute complete. \n\n')
                break
            if ttl == hops + 2:
                sys.stdout.write(f'Traceroute to host {host} failed. TTL exceeded.')

        # todo: return a list with the path
    except OSError:
        sys.stdout.write('Not compatible with OS \n')
        exit(-1)


def trace_pathviz(host, hops=30, port=33434, timeout=0.2, export_png = False):
    """
    Execute a traceroute to a remote host 
    And render a visualization graph of the path

    Parameters:
        host: the host IP address or domain name
        hops: maximum number of hops before timeout (default: 30)
        port: application port used for traceroute (default: 33434)
        timeout: seconds before timeout (default: 0.2)
        export_png: whether the graph should be exported in a png or not
    """
    route = trace(host,hops,port,timeout)
    # todo



if __name__ == '__main__':
    print('Running tests on traceroute.py')
    trace('google.com')
    trace('192.168.2.1')
    trace('gshsahashj')