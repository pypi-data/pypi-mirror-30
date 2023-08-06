#!/usr/bin/python3
"""
Convert decimal to bin.

Shows math process and output result in a table.
"""


from collections import defaultdict
from ipaddress import IPv4Address, IPv4Network


def dict_values():
    """
    Return a defaultdict with eigth keys from 128 to 1 dividing the first by 2.

    Lambda: False is used to set false a key that not exists.

    """
    d_list = defaultdict(lambda: False)
    n = 256
    for i in range(8):
        n = n/2
        d_list[n] = i
    return d_list


def convert_ip(dec_number):
    """Convert ip in decimal notation to binary."""
    _ip_list_bin = []
    for i in dec_number.split('.'):
        _bin = [0, 0, 0, 0, 0, 0, 0, 0]
        _i = int(i)
        if _i == 0:
            _ip_list_bin.append("00000000")
            continue
        elif _i == 255:
            _ip_list_bin.append("11111111")
            continue
        else:
            _t = [x for x in dict_values() if x <= _i]
            if len(_t) > 0:
                _n = max(_t)
            _v = _i - _n
            while True:
                _bin[dict_values()[_n]] = 1
                _t = [x for x in dict_values() if x <= _v]
                if len(_t) > 0:
                    _n = max(_t)
                else:
                    break
                _v = _v - _n
        _ip_list_bin.append("".join(map(str, _bin)))
    return ".".join(_ip_list_bin)


def convert_mask(mask):
    """Convert mask in slash notation to binary."""
    return ".".join(['{:032}'.format(int('1'*int(mask)))[::-1][i:i+8]
                     for i in range(0, 32, 8)])


def return_mask(mask):
    """Return full mask."""
    b_mask = convert_mask(mask)
    return ".".join(
        map(str, [int(sum([list(dict_values().keys())[x[0]] for x in list(
            enumerate(map(int, list(i)))) if x[1] == 1]))
                  for i in b_mask.split('.')]))


def return_network(ip, mask):
    """Return network with an and operation."""
    b_ip = convert_ip(ip).replace('.', '')
    b_mask = convert_mask(mask).replace('.', '')
    b_network = [
        "".join(map(str, [int(x[0]) & int(x[1]) for x in list(
            zip(b_ip, b_mask))]))[i:i+8] for i in range(0, 32, 8)]
    return ".".join(
        map(str, [int(sum([list(dict_values().keys())[x[0]] for x in list(
            enumerate(map(int, list(i)))) if x[1] == 1])) for i in b_network]))


def hosts_number(mask):
    """Return number of hosts based on network mask."""
    return int(2**(32-int(mask))-2)


def networks_number(mask):
    """Return number of sub nets based on network mask."""
    return int(2**(32-int(mask)-2))


def return_broadcast(ip, mask):
    """Return broadcast."""
    rev = ['1', '0']
    b_network = convert_ip(return_network(ip, mask)).replace('.', '')
    r_mask = "".join([rev[x] for x in map(int, list(
        convert_mask(mask).replace('.', '')))])
    b_mask = ["".join(map(str, [int(x[0]) | int(x[1]) for x in list(zip(
        b_network, r_mask))]))[i:i+8] for i in range(0, 32, 8)]
    return ".".join(
        map(str, [int(sum([list(dict_values().keys())[x[0]] for x in list(
            enumerate(map(int, list(i)))) if x[1] == 1])) for i in b_mask]))


def return_class(ip):
    if IPv4Address(ip) in IPv4Network(("10.0.0.0", "255.0.0.0")):
        return "Class A Private"
    elif IPv4Address(ip) in IPv4Network(("39.0.0.0", "255.0.0.0")):
        return "Class A Reserved"
    elif IPv4Address(ip) in IPv4Network(("127.0.0.0", "255.0.0.0")):
        return "Class A Loopback"
    elif IPv4Address(ip) in IPv4Network(("128.0.0.0", "255.255.0.0")):
        return "Class B Reserved (IANA)"
    elif IPv4Address(ip) in IPv4Network(("169.254.0.0", "255.255.0.0")):
        return "Zeroconf"
    elif IPv4Address(ip) in IPv4Network(("172.16.0.0", "255.240.0.0")):
        return "Class B Private"
    elif IPv4Address(ip) in IPv4Network(("191.255.0.0", "255.255.0.0")):
        return "Class B Reseved (IANA)"
    elif IPv4Address(ip) in IPv4Network(("192.0.2.0", "255.255.255.0")):
        return "Class C Documentation"
    elif IPv4Address(ip) in IPv4Network(("192.88.99.0", "255.255.255.0")):
        return "Class C Relay Anycast (IPv6 to IPv4)"
    elif IPv4Address(ip) in IPv4Network(("192.168.0.0", "255.255.0.0")):
        return "Class C Private"
    elif IPv4Address(ip) in IPv4Network(("198.18.0.0", "255.254.0.0")):
        return "Class C Benchmarking Network"
    elif IPv4Address(ip) in IPv4Network(("223.255.255.0", "255.255.255.0")):
        return "Class C Reserver to Internet"
    elif IPv4Address(ip) in IPv4Network(("224.0.0.0", "240.0.0.0")):
        return "Class D Multicast"
    elif IPv4Address(ip) in IPv4Network(("240.0.0.0", "240.0.0.0")):
        return "Class E Reserved"
    else:
        return "Public Address"


def return_ip_data(ip, mask):
    ip_data = defaultdict(lambda: False)
    ip_data['Ip'] = ip
    ip_data['Network_Ip'] = return_network(ip, mask)
    ip_data['Broadcast_Ip'] = return_broadcast(ip, mask)
    ip_data['Class'] = return_class(ip)
    ip_data['Full_Mask'] = return_mask(mask)
    ip_data['Max_Networks'] = networks_number(mask)
    ip_data['Max_Hosts'] = hosts_number(mask)
    ip_data['Binary_Ip'] = convert_ip(ip)
    ip_data['Binary_Mask'] = convert_mask(mask)
    return ip_data
