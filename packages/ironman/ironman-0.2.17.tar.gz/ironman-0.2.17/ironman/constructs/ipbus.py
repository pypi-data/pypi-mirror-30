from construct import Array, BitField, BitStruct, Embed, Enum, GreedyRange, Struct, Switch, UBInt32, SBInt32, OneOf, Pass
from ..globals import IPBUS_VERSION

from ironman.utilities import PrintContext

PacketHeaderStruct = BitStruct("header",
                        OneOf(BitField("protocol_version", 4), [IPBUS_VERSION]),
                        OneOf(BitField("reserved", 4), [0x0]),
                        BitField("id", 16),
                        OneOf(BitField("byteorder", 4), [0xf]),
                        Enum(BitField("type_id", 4),
                            CONTROL = 0x0,
                            STATUS = 0x1,
                            RESEND = 0x2
                        )
)
"""
Struct detailing the Packet Header logic
"""

ControlHeaderStruct = BitStruct("transaction",
                        OneOf(BitField("protocol_version", 4), [IPBUS_VERSION]),
                        BitField("id", 12),
                        BitField("words", 8),
                        Enum(BitField("type_id", 4),
                            READ = 0x0,
                            NOINCREAD = 0x2,
                            WRITE = 0x1,
                            NOINCWRITE = 0x3,
                            RMWBITS = 0x4,
                            RMWSUM = 0x5,
                            RCONFIG = 0x6,
                            WCONFIG = 0x7
                        ),
                        Enum(BitField("info_code", 4),
                            SUCCESS = 0x0,
                            BADHEADER = 0x1,
                            RBUSERROR = 0x4,
                            WBUSERROR = 0x5,
                            RBUSTIMEOUT = 0x6,
                            WBUSTIMEOUT = 0x7,
                            REQUEST = 0xf
                        )
)
"""
Struct detailing the Control Header logic
"""

ReadStruct = Struct("read",
                Switch("data", lambda ctx: ctx.info_code,
                    {
                        "REQUEST": Pass,
                        "SUCCESS": Array(lambda ctx: ctx.words, UBInt32("data"))
                    },
                    default = Pass
                )
)
"""
Struct detailing the Read Transaction logic
"""

WriteStruct = Struct("write",
                Switch("data", lambda ctx: ctx.info_code,
                    {
                        "REQUEST": Array(lambda ctx: ctx.words, UBInt32("data")),
                        "SUCCESS": Pass
                    },
                    default = Pass
                )
)
"""
Struct detailing the Write Transaction logic
"""

RMWBitsStruct = Struct("rmwbits",
                Switch("data", lambda ctx: ctx.info_code,
                    {
                        "REQUEST": Embed(Struct("data", UBInt32("and"), UBInt32("or"))),
                        "SUCCESS": UBInt32("data")
                    },
                    default = Pass
                )
)
"""
Struct detailing the RMWBits Transaction logic

Should compute via :math:`X \Leftarrow (X\wedge A)\\vee (B\wedge(!A))`
"""

RMWSumStruct = Struct("rmwsum",
                Switch("data", lambda ctx: ctx.info_code,
                    {
                        "REQUEST": SBInt32("addend"),  # note: signed 32-bit for subtraction!
                        "SUCCESS": UBInt32("data")
                    },
                    default = Pass
                )
)
"""
Struct detailing the RMWSum Transaction logic

Should compute via :math:`X \Leftarrow X+A`
"""

ControlStruct = Struct("ControlTransaction",
                    Embed(ControlHeaderStruct),
                    UBInt32("address"),
                    Embed(Switch("data", lambda ctx: ctx.type_id,
                        {
                            "READ": ReadStruct,
                            "NOINCREAD": ReadStruct,
                            "WRITE": WriteStruct,
                            "NOINCWRITE": WriteStruct,
                            "RMWBITS": RMWBitsStruct,
                            "RMWSUM": RMWSumStruct,
                            "RCONFIG": ReadStruct,
                            "WCONFIG": WriteStruct
                        }
                    ))
)
"""
Struct detailing the Control Action logic
"""

StatusRequestStruct = Struct("StatusTransaction", Array(15, OneOf(UBInt32("data"), [0])))
StatusResponseStruct = Struct("StatusTransaction", Array(15, UBInt32("data")))
"""
Struct detailing the Status Action logic
"""

ResendStruct = Struct("ResendTransaction")
"""
Struct detailing the Resend Action logic
"""

IPBusWords = Struct('IPBusWords', GreedyRange(UBInt32('data')))

IPBusConstruct = Struct("IPBusPacket",
                    PacketHeaderStruct,  # defined as 'header' in context
                    Switch("data", lambda ctx: ctx.header.type_id,
                        {
                            "CONTROL" : GreedyRange(ControlStruct),
                            "STATUS" : StatusRequestStruct,
                            "RESEND" : ResendStruct,
                        }
                    )
)
"""
Top-level IPBus Construct which is a packet parser/builder
"""

