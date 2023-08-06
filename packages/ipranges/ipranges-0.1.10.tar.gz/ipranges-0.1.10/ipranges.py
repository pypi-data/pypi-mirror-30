#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, CESNET, z. s. p. o.
# Use of this source is governed by an ISC license, see LICENSE file.

__version__ = '0.1.10'
__author__ = 'Pavel Kácha <pavel.kacha@cesnet.cz>'

import socket
import struct
import numbers
import sys

try:
    basestring
except NameError:
    basestring = str

class Range(object):
    __slots__ = ()

    single = int

    def __len__(self):
        return self.high() - self.low() + 1

    def __eq__(self, other):
        return (self.low() == other.low() and self.high() == other.high())

    def __ne__(self, other):
        return not self.__eq__(other)

    def __contains__(self, other):
        return (self.low() <= other.low() and self.high() >= other.high())

    def __iter__(self):
        for i in range(self.low(), self.high()+1):
            yield self.single(i)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return (self.single(self.low() + i) for i in range(*key.indices(len(self))))
        else:
            if key < 0:
                idx = self.high() + key + 1
            else:
                idx = self.low() + key
            if self.low() <= idx <= self.high():
                return self.single(idx)
            else:
                raise IndexError

    def __repr__(self):
        return "%s('%s')" % (type(self).__name__, str(self))


class IPBase(Range):
    __slots__ = ()

    def __init__(self, s):
        if isinstance(s, basestring):
            rng = self._from_str(s)
        elif isinstance(s, IPBase):
            rng = self._from_range(s)
        else:
            rng = self._from_val(s)
        self._assign(rng)

    def cidr_split(self):
        lo, hi = self.low(), self.high()
        lo, hi = min(lo, hi), max(lo, hi)
        while lo<=hi:
            lower_bits = (~lo & (lo-1)).bit_length()
            size = hi - lo + 1
            size_bits = size.bit_length() - 1
            bits = min(lower_bits, size_bits)
            yield self.net((lo, self.bit_length-bits))
            lo += 1 << bits

    def _from_val(self, v):
        try:
            a, b = v
            return int(a), int(b)
        except Exception:
            raise ValueError("Two value tuple expected, got %s" % v)


class IPRangeBase(IPBase):
    __slots__ = ("lo", "hi")

    def _from_range(self, r):
        return (r.low(), r.high())

    def _from_str(self, s):
        try:
            ip1, ip2 = s.split("-")
            return (self.from_str(ip1), self.from_str(ip2))
        except Exception:
            raise ValueError("Wrong range format: %s" % s)

    def _assign(self, v):
        self.lo = min(v)
        self.hi = max(v)

    def low(self): return self.lo

    def high(self): return self.hi

    def __str__(self):
        return "%s-%s" % (self.to_str(self.lo), self.to_str(self.hi))

    def __hash__(self):
        return hash((self.lo, self.hi))


class IPNetBase(IPBase):
    __slots__ = ("base", "cidr", "mask")

    def _from_range(self, r):
        lo = r.low()
        mask = len(r) - 1
        if (len(r) & mask) or (lo & mask):
            raise ValueError("%s is not a proper network prefix" % r)
        return lo, self.bit_length - mask.bit_length()

    def _from_str(self, s):
        try:
            net, cidr = s.split("/")
            base = self.from_str(net)
            cidr = int(cidr)
            return base, cidr
        except Exception:
            raise ValueError("Wrong network format: %s" % s)

    def _assign(self, v):
        self.base, self.cidr = v
        self.mask = (self.full_mask << (self.bit_length - self.cidr)) & self.full_mask

    def low(self): return self.base & self.mask

    def high(self): return self.base | (self.mask ^ self.full_mask)

    def __str__(self):
        return "%s/%i" % (self.to_str(self.base), self.cidr)

    def __hash__(self):
        return hash((self.base, self.mask))


class IPAddrBase(IPBase):
    __slots__ = ("ip")

    def _from_range(self, r):
        if len(r)!=1:
            raise ValueError("Unable to convert network %s to one ip address" % r)
        return r.low()

    def _from_str(self, s): return self.from_str(s)

    def _from_val(self, r):
        try:
            return int(r)
        except Exception:
            raise ValueError("Integer expected as IP")

    def _assign(self, v): self.ip = v

    def __str__(self): return self.to_str(self.ip)

    def __int__(self): return self.ip

    def __hash__(self): return hash(self.ip)

    def low(self): return self.ip

    def high(self): return self.ip


def ip4_from_str(s):
    try:
        return struct.unpack("!L", socket.inet_pton(socket.AF_INET, s))[0]
    except Exception:
        raise ValueError("Wrong IPv4 address format: %s" % s)

def ip4_to_str(i):
    try:
        return socket.inet_ntop(socket.AF_INET, struct.pack('!L', i))
    except Exception:
        raise ValueError("Unable to convert to IPv6 address: %s" % i)

def ip6_from_str(s):
    try:
        hi, lo = struct.unpack("!QQ", socket.inet_pton(socket.AF_INET6, s))
        return hi << 64 | lo
    except Exception:
        raise ValueError("Wrong IPv6 address format: %s" % s)

def ip6_to_str(i):
    try:
        hi = i >> 64
        lo = i & 0xFFFFFFFFFFFFFFFF
        return socket.inet_ntop(socket.AF_INET6, struct.pack('!QQ', hi, lo))
    except Exception:
        raise ValueError("Unable to convert to IPv6 address: %s" % i)


class IP4(IPAddrBase):
    __slots__ = ()
    bit_length = 32
    full_mask = 2**bit_length-1

    from_str = staticmethod(ip4_from_str)
    to_str = staticmethod(ip4_to_str)

    if sys.version_info < (3,):
        def to_ptr_str(self):
            return ".".join(str(ord(s)) for s in (reversed(struct.pack("!L", self.ip)))) + ".in-addr.arpa."
    else:
        def to_ptr_str(self):
            return ".".join(str(s) for s in self.ip.to_bytes(4, "little")) + ".in-addr.arpa."

IP4.single = IP4

class IP4Range(IPRangeBase):
    __slots__ = ()
    bit_length = IP4.bit_length
    full_mask = IP4.full_mask
    single = IP4

    from_str = staticmethod(ip4_from_str)
    to_str = staticmethod(ip4_to_str)

class IP4Net(IPNetBase):
    __slots__ = ()
    bit_length = IP4.bit_length
    full_mask = IP4.full_mask
    single = IP4

    from_str = staticmethod(ip4_from_str)
    to_str = staticmethod(ip4_to_str)

IP4.net = IP4Net
IP4Range.net = IP4Net
IP4Net.net = IP4Net

class IP6(IPAddrBase):
    __slots__ = ()
    bit_length = 128
    full_mask = 2**bit_length-1

    from_str = staticmethod(ip6_from_str)
    to_str = staticmethod(ip6_to_str)

    def to_ptr_str(self):
        return ".".join(reversed("%016x" % self.ip)) + ".ip6.arpa."

IP6.single = IP6

class IP6Range(IPRangeBase):
    __slots__ = ()
    bit_length = IP6.bit_length
    full_mask = IP6.full_mask
    single = IP6

    from_str = staticmethod(ip6_from_str)
    to_str = staticmethod(ip6_to_str)

class IP6Net(IPNetBase):
    __slots__ = ()
    bit_length = IP6.bit_length
    full_mask = IP6.full_mask
    single = IP6

    from_str = staticmethod(ip6_from_str)
    to_str = staticmethod(ip6_to_str)

IP6.net = IP6Net
IP6Range.net = IP6Net
IP6Net.net = IP6Net

def from_str(s):
    for t in IP4Net, IP4Range, IP4, IP6Net, IP6Range, IP6:
        try:
            return t(s)
        except ValueError:
            pass
    raise ValueError("%s does not appear as IP address, network or range string" % s)

def from_str_v4(s):
    for t in IP4Net, IP4Range, IP4:
        try:
            return t(s)
        except ValueError:
            pass
    raise ValueError("%s does not appear as IPv4 address, network or range string" % s)

def from_str_v6(s):
    for t in IP6Net, IP6Range, IP6:
        try:
            return t(s)
        except ValueError:
            pass
    raise ValueError("%s does not appear as IPv6 address, network or range string" % s)

def ip_from_str(s):
    for t in IP4, IP6:
        try:
            return t(s)
        except ValueError:
            pass
    raise ValueError("%s does not appear as IPv4 nor IPv6 address" % s)
