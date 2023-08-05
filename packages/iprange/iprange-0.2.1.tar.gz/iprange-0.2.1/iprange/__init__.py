from .ipaddress import IPv4Address


def increase_ip(ip):
  return IPv4Address(ip) + IPv4Address(_int_addr=1)
  

def generate_range(ip_start, ip_end):
    start = IPv4Address(ip_start)
    end = IPv4Address(ip_end)
    if end.intaddr < start.intaddr: 
        raise ValueError('The end ip address must be '
                         'bigger or equal to the start address')
    for i in range(start.intaddr, end.intaddr + 1):
        yield IPv4Address(_int_addr=i)

