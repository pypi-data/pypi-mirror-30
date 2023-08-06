"""
This module contains various :class:`enum.IntEnum` generated at runtime from protobufs.
Why generate python enums? In short, protobuf's enums aren't great.
:class:`enum.IntEnum` are much more flexible and easy to work with.
"""

import re
import six
from enum import IntEnum
from google.protobuf.internal.enum_type_wrapper import EnumTypeWrapper

_proto_modules = ['gcsystemmsgs_pb2',
                  'gcsdk_gcmessages_pb2',
                  'cstrike15_gcmessages_pb2',
                  'econ_gcmessages_pb2',
                  ]

_level = -1 if six.PY2 else 0

_proto_module = __import__("csgo.protobufs", globals(), locals(), _proto_modules, _level)

for name in _proto_modules:

    proto = getattr(_proto_module, name)
    gvars = globals()

    for key, value in proto.__dict__.items():
        if not isinstance(value, EnumTypeWrapper):
            continue

        items = {}
        for ikey, ivalue in value.items():
            ikey = re.sub(r'^(k_)?(%s_)?' % key, '', ikey)
            items[ikey] = ivalue

        gvars[key] = IntEnum(key, items)

class ESOType(IntEnum):
    CSOEconItem = 1
    CSOPersonaDataPublic = 2
    CSOItemRecipe = 5
    CSOEconGameAccountClient = 7
    CSOEconItemDropRateBonus = 38
    CSOEconItemEventTicket = 40
    CSOEconDefaultEquippedDefinitionInstanceClient = 43
    CSOEconCoupon = 45
    CSOQuestProgress = 46


class EXPFlag(IntEnum):
    UNKNOWN1                     = 0b0000000000000000000000000000001
    LevelUpDropReceived          = 0b0000000000000000000000000000010
    UNKNOWN2                     = 0b0000000000000000000000000010000  # OW or Prime status
    OverwatchXPReward            = 0b0010000000000000000000000000000
    WeeklyXPBoostReceived        = 0b0100000000000000000000000000000
    UNKNOWN3                     = 0b1000000000000000000000000000000  # OW related?


del re, IntEnum, EnumTypeWrapper, _proto_modules, _proto_module, _level, name, proto, gvars, key, value, items, ikey, ivalue
