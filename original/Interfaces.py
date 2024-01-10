# Use those functions to enumerate all interfaces available on the system using Python.
# found on http://code.activestate.com/recipes/439093/#c1
 
import socket
import fcntl
import struct
import array

def all_interfaces():
    max_possible = 128  # arbitrary. raise if needed.
    obytes = max_possible * 32
    deb = b'\0'
 
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    names = array.array('B', deb * obytes)
    outbytes = struct.unpack('iL', fcntl.ioctl(
        s.fileno(),
        0x8912,  # SIOCGIFCONF
        struct.pack('iL', obytes, names.buffer_info()[0])

    ))[0]

    namestr = names.tostring()

    lst = []
    for i in range(0, outbytes, 40):
        name = namestr[ i: i+16 ].split( deb, 1)[0]
        name = name.decode()
       #iface_name = namestr[ i : i+16 ].split( deb, 1 )[0]
        ip   = namestr[i+20:i+24]
        lst.append((name, ip))
    return lst
 
def format_ip(addr):
    return f'{addr[0]}.{addr[1]}.{addr[2]}.addr{3}'

  

ifs = all_interfaces()
for i in ifs:
    print ( f"\t{i[0]}\t: %s" % (format_ip(i[1])))