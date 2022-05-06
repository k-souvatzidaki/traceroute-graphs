"""
Helper functions for traceroute

Classes:
    CompatibilityError

Functions: 
    is_compatible(os)
    resolve(hostname)
"""
import socket

# ICMP
ICMP_TIME_EXCEEDED = 11
ICMP_DESTINATION_UNREACHABLE = 3
ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0
# MISC
__NOT_COMPATIBLE = ["Darwin", "Windows"]

# GRAPH PROPERTIES
graph_attr = {
    "fontsize": "16",
    "fixedsize": "false",
}

edge_attr = {
    "arrowhead": "none",
    "minlen": "2.6"
}

node_attr = {
    "fontsize": "12",
    "width": "1"
}


class CompatibilityError(BaseException):
    """
    Exception raised when system is not compatible with the module
    """

    def __init__(self, os):
        self.message = f'Raw sockets not compatible with OS {os}.'
        super().__init__(self.message)


class ResolutionError(BaseException):
    """
    Exception raised when a hostname cannot be resolved
    """

    def __init__(self, hostname):
        self.message = f'Unable to resolve host {hostname}'
        super().__init__(self.message)


def is_compatible(os) -> bool:
    """
    Check if the system is compatible with raw sockets
    Raise CompatibilityError if the system OS is not compatible with the module.

    Args:
        os: The underlying operating system distribution

    Returns: True if the system is compatible (Linux)
    """
    if os in __NOT_COMPATIBLE:
        raise CompatibilityError(os)
    return True


def resolve(hostname) -> str:
    """
    Resolve the ip address of host
    Raise ResolutionError if the hostname cannot be resolved

    Args:
        hostname: the DNS name or IP address of host

    Returns: The host IP address in string format
    """
    try:
        host_address = socket.gethostbyname(hostname)
    except socket.error as e:
        raise ResolutionError(hostname)
    return host_address
