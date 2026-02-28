from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ELeaderRequest(_message.Message):
    __slots__ = ("id", "view", "cshare")
    ID_FIELD_NUMBER: _ClassVar[int]
    VIEW_FIELD_NUMBER: _ClassVar[int]
    CSHARE_FIELD_NUMBER: _ClassVar[int]
    id: str
    view: int
    cshare: str
    def __init__(self, id: _Optional[str] = ..., view: _Optional[int] = ..., cshare: _Optional[str] = ...) -> None: ...

class ELeaderReply(_message.Message):
    __slots__ = ("id", "view", "cshare")
    ID_FIELD_NUMBER: _ClassVar[int]
    VIEW_FIELD_NUMBER: _ClassVar[int]
    CSHARE_FIELD_NUMBER: _ClassVar[int]
    id: str
    view: int
    cshare: str
    def __init__(self, id: _Optional[str] = ..., view: _Optional[int] = ..., cshare: _Optional[str] = ...) -> None: ...

class CSelectionRequest(_message.Message):
    __slots__ = ("id", "view", "parties", "f")
    ID_FIELD_NUMBER: _ClassVar[int]
    VIEW_FIELD_NUMBER: _ClassVar[int]
    PARTIES_FIELD_NUMBER: _ClassVar[int]
    F_FIELD_NUMBER: _ClassVar[int]
    id: str
    view: int
    parties: int
    f: int
    def __init__(self, id: _Optional[str] = ..., view: _Optional[int] = ..., parties: _Optional[int] = ..., f: _Optional[int] = ...) -> None: ...

class CSelectionReply(_message.Message):
    __slots__ = ("comm",)
    COMM_FIELD_NUMBER: _ClassVar[int]
    comm: int
    def __init__(self, comm: _Optional[int] = ...) -> None: ...

class PRORequest(_message.Message):
    __slots__ = ("id", "type", "instance", "proof", "value")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    PROOF_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    instance: int
    proof: str
    value: str
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., instance: _Optional[int] = ..., proof: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class PROReply(_message.Message):
    __slots__ = ("yes",)
    YES_FIELD_NUMBER: _ClassVar[int]
    yes: str
    def __init__(self, yes: _Optional[str] = ...) -> None: ...

class ClassicPRORequest(_message.Message):
    __slots__ = ("id", "type", "instance", "proof", "value")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    PROOF_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    instance: int
    proof: str
    value: str
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., instance: _Optional[int] = ..., proof: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class ClassicPROReply(_message.Message):
    __slots__ = ("id", "type", "instance", "proof", "value")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    PROOF_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    instance: int
    proof: str
    value: str
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., instance: _Optional[int] = ..., proof: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class ClassicCommitRequest(_message.Message):
    __slots__ = ("id", "type", "instance", "list")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    instance: int
    list: str
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., instance: _Optional[int] = ..., list: _Optional[str] = ...) -> None: ...

class ClassicCommitReply(_message.Message):
    __slots__ = ("id", "type", "instance", "list")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    instance: int
    list: str
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., instance: _Optional[int] = ..., list: _Optional[str] = ...) -> None: ...

class CPRORequest(_message.Message):
    __slots__ = ("id", "instance")
    ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    id: str
    instance: int
    def __init__(self, id: _Optional[str] = ..., instance: _Optional[int] = ...) -> None: ...

class CPROReply(_message.Message):
    __slots__ = ("cfrom", "proof", "value")
    CFROM_FIELD_NUMBER: _ClassVar[int]
    PROOF_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    cfrom: str
    proof: str
    value: str
    def __init__(self, cfrom: _Optional[str] = ..., proof: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class RECORequest(_message.Message):
    __slots__ = ("id", "type", "instance", "recomID", "proof", "value")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    RECOMID_FIELD_NUMBER: _ClassVar[int]
    PROOF_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    instance: int
    recomID: str
    proof: str
    value: str
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., instance: _Optional[int] = ..., recomID: _Optional[str] = ..., proof: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class RECOReply(_message.Message):
    __slots__ = ("id", "type", "instance", "recomID", "proof", "value")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    RECOMID_FIELD_NUMBER: _ClassVar[int]
    PROOF_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    instance: int
    recomID: str
    proof: str
    value: str
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., instance: _Optional[int] = ..., recomID: _Optional[str] = ..., proof: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class CommitteMember(_message.Message):
    __slots__ = ("member",)
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    member: int
    def __init__(self, member: _Optional[int] = ...) -> None: ...

class Committee(_message.Message):
    __slots__ = ("CMember",)
    CMEMBER_FIELD_NUMBER: _ClassVar[int]
    CMember: _containers.RepeatedCompositeFieldContainer[CommitteMember]
    def __init__(self, CMember: _Optional[_Iterable[_Union[CommitteMember, _Mapping]]] = ...) -> None: ...

class mDict(_message.Message):
    __slots__ = ("instance", "step", "ts", "value", "id")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    TS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    instance: int
    step: int
    ts: str
    value: str
    id: str
    def __init__(self, instance: _Optional[int] = ..., step: _Optional[int] = ..., ts: _Optional[str] = ..., value: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...

class messageABBA(_message.Message):
    __slots__ = ("instance", "round", "value", "justification", "sign", "type", "id")
    INSTANCE_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    JUSTIFICATION_FIELD_NUMBER: _ClassVar[int]
    SIGN_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    instance: int
    round: int
    value: int
    justification: str
    sign: str
    type: str
    id: str
    def __init__(self, instance: _Optional[int] = ..., round: _Optional[int] = ..., value: _Optional[int] = ..., justification: _Optional[str] = ..., sign: _Optional[str] = ..., type: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...

class ABBARequest(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: messageABBA
    def __init__(self, message: _Optional[_Union[messageABBA, _Mapping]] = ...) -> None: ...

class ABBAReply(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: messageABBA
    def __init__(self, message: _Optional[_Union[messageABBA, _Mapping]] = ...) -> None: ...

class HelloRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class VCBCRequest(_message.Message):
    __slots__ = ("msg",)
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: mDict
    def __init__(self, msg: _Optional[_Union[mDict, _Mapping]] = ...) -> None: ...

class VCBCReply(_message.Message):
    __slots__ = ("msg",)
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: mDict
    def __init__(self, msg: _Optional[_Union[mDict, _Mapping]] = ...) -> None: ...

class HelloReply(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...
