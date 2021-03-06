"""
Implementation of traceroute command with raw sockets

Functions:
    trace(host, hops=30, port=33434, timeout=0.2)
    trace_graph(host, hops=30, port=33434, timeout=0.2, export_png = False)
"""
import sys
import datetime
import platform
import struct
from traceroute.helpers import *

from diagrams import Diagram, Edge
from diagrams.generic.network import Router
from diagrams.generic.blank import Blank


def trace(host, hops=30, port=33434, timeout=2.0) -> list:
    """
    Execute a traceroute to a remote host

    Args:
        host: the host IP address or domain name
        hops: maximum number of hops before timeout (default: 30)
        port: application port used for traceroute (default: 33434)
        timeout: seconds before timeout (default: 0.2)

    Returns: a list of all nodes in traceroute path
    """
    # resolve host name to ip address
    host_address = resolve(host)
    sys.stdout.write(f'Traceroute to host {host_address} with a maximum of {hops} hops\n')

    is_compatible(platform.system())

    ttl = 1
    reached = False
    all_nodes = []
    try:
        while ttl <= hops+1:
            start = datetime.datetime.now()
            try: 
                # receive icmp responses from hosts
                receive_icmp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
                receive_icmp.settimeout(timeout)
                receive_icmp.bind(('', port))

                # send udp messages with ttl = step
                send_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.getprotobyname('udp'))
                send_udp.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
                send_udp.sendto(''.encode(), (host_address, port))
            except PermissionError:
                sys.stdout.write('Run as root!! \n')
                exit(-1)

            step_address = '*'
            step_name = '*'
            step_timeout = None
            try:
                packet, step_address = receive_icmp.recvfrom(512)
                icmp_header = packet[20:28]
                icmp_type, _, _, _, _ = struct.unpack(
                    "bbHHh", icmp_header
                )
                step_address = step_address[0]
                if icmp_type == ICMP_TIME_EXCEEDED:
                    try:
                        step_name = socket.gethostbyaddr(step_address)[0]
                    except socket.error:
                        step_name = step_address 
                elif icmp_type == ICMP_DESTINATION_UNREACHABLE:
                    step_name = host
                    reached = True
                step_timeout = int((datetime.datetime.now() - start).total_seconds() * 1000)
            except socket.error as e:  # timeout reached
                step_timeout = int(timeout*1000)
                sys.stdout.write(f'{ttl}: {step_timeout} ms * \n')
                ttl += 1

            send_udp.close()
            receive_icmp.close()
            node = {
                'step': ttl,
                'name': step_name,
                'address': step_address,
                'timeout': step_timeout
            }

            if step_address != '*':
                if step_address == step_name:
                    step_address = ''
                else:
                    step_address = f'[{step_address}]'
                sys.stdout.write(f'{ttl}: {step_timeout} ms {step_name} {step_address}\n')
            
            # next step
            all_nodes.append(node)
            ttl += 1
            if reached:
                sys.stdout.write('Traceroute complete. \n\n')
                break
            if ttl >= hops + 2:
                sys.stdout.write(f'Traceroute to host {host} failed. TTL exceeded.')
                all_nodes = None

        return all_nodes
    except OSError:
        sys.stdout.write('Not compatible with OS \n')
        exit(-1)


def trace_graph(host, hops=30, port=33434, timeout=2.0):
    """
    Execute a traceroute to a remote host 
    And render a visualization graph of the path

    Args:
        host: the host IP address or domain name
        hops: maximum number of hops before timeout (default: 30)
        port: application port used for traceroute (default: 33434)
        timeout: seconds before timeout (default: 0.2)
    """
    route = trace(host, hops, port, timeout)

    if route is not None:
        with Diagram(f'Traceroute to host {host}', direction='LR', graph_attr=graph_attr, edge_attr=edge_attr,
                     node_attr=node_attr, filename=f'output/{host}_route', show=False) as graph:
            previous_node = None
            for node in route:
                name = node["name"]
                timeout = node["timeout"]
                if name == '*':
                    current_node = Blank('*')
                else:
                    current_node = Router(f'[{name}] {timeout} ms')
                if previous_node is not None:
                    previous_node >> Edge(color='black', style='dotted') >> current_node
                previous_node = current_node


if __name__ == '__main__':
    print('This is a module.')
