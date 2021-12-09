import uuid

from enum import Enum

from typing import List
from typing import Optional
# from typing import Union

from pydantic import BaseModel
# from pydantic import validator
from pydantic import Extra

# from wappstoiot.schema.base_schemas import BlobValueSchema
# from wappstoiot.schema.base_schemas import DeviceSchema
from wappstoiot.schema.base_schema import BaseMeta
# from wappstoiot.schema.base_schemas import NetworkSchema
# from wappstoiot.schema.base_schemas import NumberValueSchema
# from wappstoiot.schema.base_schemas import StateSchema
# from wappstoiot.schema.base_schemas import StringValueSchema
# from wappstoiot.schema.base_schemas import WappstoMetaType
from wappstoiot.schema.base_schema import WappstoVersion


class WappstoObjectType(str, Enum):
    # WappstoMetaType
    NETWORK = "network"
    DEVICE = "device"
    VALUE = "value"
    STATE = "state"
    CREATOR = "creator"
    # session = "session"
    # prototype = "prototype"


class CreatorStatusType(str, Enum):
    PENDING = "pending"  # Not in use?
    ASSIGNED = "assigned"  # In use
    CREATED = "created"  # ??


class MetaAPIData(BaseMeta):
    type: WappstoObjectType


class CreatorStatusSchema(BaseModel):
    id: Optional[uuid.UUID]  # NOTE: Need to be optional.
    status: CreatorStatusType


class FactorySchema(BaseModel):
    reset_manufacturer: bool
    reset_owner: bool


class CreatorSchema(BaseModel):
    ca: Optional[str]  # NOTE: Only on reply. TODO: Change to certificates verification.
    certificate: Optional[str]  # NOTE: Only on reply. TODO: Change to certificates verification.
    private_key: Optional[str]  # NOTE: Only on reply. TODO: Change to certificates verification.
    network: Optional[CreatorStatusSchema]
    bound: Optional[bool]

    data: Optional[str]  # UNSURE: what is in this?  str of 'NetworkSchema' Only vr 2.0?
    product: Optional[str]

    factory_reset: Optional[FactorySchema]
    manufacturer_as_owner: Optional[bool]
    test_mode: Optional[bool]

    meta: Optional[MetaAPIData]

    class Config:
        extra = Extra.forbid

    def __str__(self):
        pstr = []

        uid = self.meta.id
        pstr.append(f"Creator: {uid}")

        nuuid = self.network.id
        pstr.append(f" - Network: {nuuid}")

        product = self.product
        pstr.append(f" - product: {product}")

        # Version 2.1 only
        if self.meta.version == WappstoVersion.v2_1:
            status = self.network.status.name
            pstr.append(f" - Status : {status}")

        return "\n".join(pstr)

    def _repr_pretty_(self, p, cycle):
        """
        Determents how the Creator Schema should be shown in IPython.

        # TODO: Add color check & colors.
        """
        print("\n" + str(self))  # NOTE: Error with WappstoVersion != v2_1


class SessionSchema(BaseModel):
    # TODO:
    provider: str
    type: str
    system: str

    remember_me: bool
    to_upgrade: bool
    upgrade: bool
    meta: MetaAPIData
