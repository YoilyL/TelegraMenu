from struct import pack
from math import ceil
from itertools import chain
from io import BytesIO
import json

def get_packed(num,menu=False):
    negative = num < 0
    if negative:
        num = abs(num)
    byte_length = ceil(num.bit_length()/8) or 1
    packed = num.to_bytes(byte_length,'big')
    fmt = pack_fmt(byte_length,negative,menu)
    return fmt, packed
def pack_fmt(byte_length,negative,menu):
    return menu << 3 | negative << 2 | (byte_length -1)
def unpack_fmt(fmt):
    return (fmt & 0b0011) +1, bool(fmt & 0b0100),bool(fmt & 0b1000)
def pack_fmts(fmts):
    packed_fmts = b''
    for i in range(0,len(fmts),2):
        try:
            fmt = (fmts[i] << 4) | fmts[i+1]
        except IndexError:
            fmt = fmts[i] << 4
        packed_fmts += fmt.to_bytes(1,'big')
    return packed_fmts

def unpack_fmts(fmts,fmts_len):
    cnt = 0
    for byte in fmts:
        for fmt in byte >>4, byte & 0x0f:
            if cnt < fmts_len:
                yield unpack_fmt(fmt)
            cnt += 1
def callback_encode(action_list):
    values = [get_packed(value,tuple_index==0) for actions in action_list for tuple_index,value in enumerate(actions)]      
    fmts = [i[0] for i in values]
    packed = b''.join(i[1] for i in values)
    packed_fmts = pack_fmts(fmts)
    final = len(fmts).to_bytes(1,'big') + packed_fmts + packed
    return final
def callback_decode(data):
    data = BytesIO(data)
    fmts_len = int.from_bytes(data.read(1),'big')
    fmts = data.read(ceil(fmts_len/2))
    last_sub = []
    actions = []
    for byte_length,negative,menu  in unpack_fmts(fmts,fmts_len):
        value = int.from_bytes(data.read(byte_length),'big')
        if negative:
            value *= -1
        if menu and last_sub:
            actions.append(tuple(last_sub))
        if byte_length:
            if menu:
                last_sub = [value]
            else:
                last_sub.append(value)
    actions.append(tuple(last_sub))
    return actions