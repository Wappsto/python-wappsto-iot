import __main__
import netrc
import logging
import atexit
import json

from pathlib import Path

# from urllib.parse import ParseResult

from enum import Enum

from typing import Any, Dict, Optional, Union, Callable, Literal

from pydantic import UUID4
# from pydantic import parse_file_as


from ..service.template import ServiceClass
# from .service.rest_api import RestAPI
from ..service.iot_api import IoTAPI

from .template import dict_diff
from .device import Device
# from .value import Value

# from .template import _Config
# from .template import _ConfigFile
# from .template import _UnitsInfo

from ..schema import base_schema as WSchema
from ..schema.iot_schema import WappstoMethod

# from .utils import exceptions
from ..utils.certificateread import CertificateRead
from ..utils.offline_storage import OfflineStorage
from ..utils.offline_storage import OfflineStorageFiles


# #############################################################################
#                        Status Observer Setup
# #############################################################################

from ..utils import observer 
from ..connections import protocol as connection
from ..service import template as service


class StatusID(str, Enum):
    CONNECTION = "CONNECTION"
    SERVICE = "SERVICE"


# TODO: TEST the Status thingy.
ConnectionStatus = connection.Status.DISCONNETCED
ServiceStatus = service.Status.IDLE


def __connectionStatus(
    layer: Literal[StatusID.CONNECTION],
    newStatus: connection.Status
):
    global ConnectionStatus
    ConnectionStatus = newStatus


def __serviceStatus(
    layer: Literal[StatusID.SERVICE],
    newStatus: service.Status
):
    global ServiceStatus
    ServiceStatus = newStatus


def subscribe_all_status():    
    observer.subscribe(
        event_name=StatusID.CONNECTION,
        callback=__connectionStatus
    )
    observer.subscribe(
        event_name=StatusID.SERVICE,
        callback=__serviceStatus
    )


# #############################################################################
#                                 Network Setup
# #############################################################################

class NetworkChangeType(str, Enum):
    description = "description"
    device = "device"
    info = "info"
    name = "name"


class NetworkRequestType(str, Enum):
    refresh = "refresh"
    delete = "delete"


class ConnectionTypes(str, Enum):
    IOTAPI = "jsonrpc"
    RESTAPI = "HTTPS"

# class status:
#     Connection -> *REf
#


class Network(object):

    schema = WSchema.Network

    def __init__(
        self,
        configFolder: Union[Path, str] = ".",  # Relative to the main.py-file.
        name: str = "TheNetwork",
        description: str = "",
        connection: ConnectionTypes = ConnectionTypes.IOTAPI,
        mixMaxEnforce="warning",  # "ignore", "enforce"
        stepEnforce="warning",  # "ignore", "enforce"
        deltaHandling="",
        period_handling="",
        connectSync: bool = True,  # Start with a Network GET to sync.  # TODO:
        pingPongPeriod: Optional[int] = None,  # Period between a RPC ping-pong.
        offlineStorage: Union[OfflineStorage, bool] = False,
        # none_blocking=True,  # Whether the post should wait for reply or not.
    ) -> None:
        """
        Configure the WappstoIoT settings.

        This function call is optional.
        If it is not called, the default settings will be used for WappstoIoT.
        This function will also connect to the WappstoIoT API on call.
        In the cases that this function is not called, the connection will be
        make when an action is make that requests the connection.

        The 'minMaxEnforce' is default set to "Warning" where a warning is
        reading to log, when the value range is outside the minimum & maximum
        range.
        The 'ignore' is where it do nothing when it is outside range.
        The 'enforce' is where the range are enforced to fit the minimum &
        maximum range. Meaning if it is above the maximum it is changed to
        the maximum, if it is below the minimum, it is set to the minimum value.
        """
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

        self.closed = False

        kwargs = locals()
        self.__uuid: UUID4
        self.element: WSchema.Network = self.schema()

        self.children_uuid_mapping: Dict[UUID4, Device] = {}
        self.children_id_mapping: Dict[int, UUID4] = {}
        self.children_name_mapping: Dict[str, UUID4] = {}

        self.cloud_id_mapping: Dict[int, UUID4] = {}

        if not isinstance(configFolder, Path):
            if configFolder == ".":
                configFolder = Path(__main__.__file__).absolute().parent
            else:
                configFolder = Path(configFolder)
        self.configFolder = configFolder

        self.connection: ServiceClass

        self._setup_offline_storage(offlineStorage)

        if connection == ConnectionTypes.IOTAPI:
            self._setup_IoTAPI(configFolder)
            cer = CertificateRead(crt=self.configFolder / "client.crt")
            self.__uuid = cer.network

        elif connection == ConnectionTypes.RESTAPI:
            # TODO: Find & load configs.
            configs: Dict[Any, Any] = {}
            self._setup_RestAPI(self.configFolder, configs)  # FIXME:

        subscribe_all_status()

        self.element = self.schema(
            name=name,
            description=description,
            meta=WSchema.NetworkMeta(
                version=WSchema.WappstoVersion.V2_0,
                type=WSchema.WappstoMetaType.NETWORK,
                id=self.uuid
            )
        )

        element = self.connection.get_network(self.uuid)
        if element:
            self.__update_self(element)
            # self.log.debug(
            #     type(self.element.meta)
            # )
            # self.log.debug(
            #     self.element.meta
            # )
            # self.log.debug(
            #     type(element.meta)
            # )
            # self.log.debug(
            #     element.meta
            # )
            if self.element != element:
                # TODO: Post diff only.
                self.log.info("Data Models Differ. Sending Local.")
                self.connection.post_network(self.element)
        else:
            self.connection.post_network(self.element)

        atexit.register(self.close)

    def clean(self) -> None:
        """
        Remove local storage, and references to the Wappsto data-model.
        """
        pass

    @property
    def name(self) -> str:
        """Returns the name of the value."""
        return self.element.name

    @property
    def uuid(self) -> UUID4:
        """Returns the name of the value."""
        return self.__uuid

    # -------------------------------------------------------------------------
    #   Helper methods
    # -------------------------------------------------------------------------

    def _setup_IoTAPI(self, configFolder, configs=None):
        # TODO: Setup the Connection.
        kwargs = self._certificate_check(configFolder)
        self.connection = IoTAPI(**kwargs)

    def _setup_RestAPI(self, configFolder, configs):
        # TODO: Setup the Connection.
        token = configs.get("token")
        login = netrc.netrc().authenticators(configs.end_point)
        if token:
            kwargs = {"token": token}
        elif login:
            kwargs = {"username": login[0], "password": login[1]}
        else:
            raise ValueError("No login was found.")
        self.connection = RestAPI(**kwargs, url=configs.end_point)

    def _device_name_gen(self, device_id):
        return f"device_{device_id}"

    def _setup_offline_storage(
        self,
        offlineStorage: Union[OfflineStorage, bool]
    ) -> None:
        # TODO: Test me!!
        if offlineStorage is False:
            return
        if offlineStorage is True:
            offlineStorage = OfflineStorageFiles(
                location=self.configFolder
            )

        observer.subscribe(
            service.Status.SENDERROR,
            lambda _, data: offlineStorage.save(data.json(exclude_none=True))
        )

        def _resend_logic(status, data):
            nonlocal offlineStorage
            self.log.debug(f"Resend called with: {status=}")
            try:
                self.log.debug("Resending Offline data")
                while True:
                    data = offlineStorage.load(10)
                    if not data:
                        return

                    s_data = [json.loads(d) for d in data]
                    self.log.debug(f"Sending Data: {s_data}")
                    self.connection._resend_data(
                        json.dumps(s_data)
                    )

            except Exception:
                self.log.exception("")

        observer.subscribe(
            connection.Status.CONNECTED,
            _resend_logic
        )

    # -------------------------------------------------------------------------
    #   Save/Load helper methods
    # -------------------------------------------------------------------------

    # def __restore_from_save_file(self, configs, kwargs):
    #     # TODO(MBK): Create the self.element & All the Children.

    #     # the kwargs weigh higher then the loaded settings.
    #     for key, value in configs.dict().items():
    #         if kwargs[key] is None:
    #             kwargs[key] = value
    #     # self.__init_devices(self.uuid, configs)
    #     pass

    def __update_self(self, element: WSchema.Network):
        # TODO(MBK): Check if new devices was added! & Check diff.
        # NOTE: If there was a diff, post local one.
        self.element = element.copy(update=self.element.dict(exclude_none=True))
        self.element.meta = element.meta.copy(update=self.element.meta)
        for nr, device in enumerate(self.element.device):
            self.cloud_id_mapping[nr] = device

    def _certificate_check(self, path) -> Dict[str, Path]:
        """
        Check if the right certificates are at the given path.
        """
        self.certi_path = {
            "ca": "ca.crt",
            "crt": "client.crt",
            "key": "client.key",
        }
        r_paths: Dict[str, Path] = {}
        for k, f in self.certi_path.items():
            r_paths[k] = path / f
            if not r_paths[k].exists():
                raise FileNotFoundError(f"'{f}' was not found in at: {path}")

        return r_paths

    # def _load_config(self) -> _ConfigFile:
    #     try:
    #         return parse_file_as(_ConfigFile, self.__config_file)
    #     except FileNotFoundError:
    #         exceptions.ConfigFileNotFoundError(
    #             "Could not find the config file."
    #         )
    #     except Exception:  # JSONDecodeError
    #         exceptions.ConfigFileError(
    #             "Could not parse config file."
    #         )

    # def _get_json(self) -> _UnitsInfo:
    #     """Generate the json-object ready for to be saved in the configfile."""
    #     unit_list = []
    #     for unit in self.children_uuid_mapping.values():
    #         unit_list.extend(unit._get_json())
    #     unit_list.append(_UnitsInfo(
    #         self_type=WSchema.WappstoObjectType.NETWORK,
    #         parent=None,
    #         children=list(self.children_uuid_mapping.keys()),
    #         children_id_mapping=self.children_id_mapping,
    #         children_name_mapping=self.children_name_mapping
    #     ))
    #     return unit_list

    # def _save_config(self):
    #     cofigdata = _ConfigFile(
    #         units=self._get_json(),
    #         configs=_Config(
    #             network_uuid=self.uuid,
    #             # network_name=self.name,
    #             port=self.port,
    #             end_point=self.end_point,
    #             # connectSync=self.connectSync,
    #             # storeQueue=self.storeQueue,
    #             # mixMaxEnforce=self.mixMaxEnforce,
    #             # stepEnforce=self.stepEnforce,
    #             # deltaHandling=self.deltaHandling,
    #             # period_handling=self.period_handling,
    #         )
    #     )
    #     with open(self.__config_file, "w") as file:
    #         file.write(cofigdata.json())

    # def __init_devices(self, uuid, configs):
    #     for device_uuid in configs.unit[uuid].children:
    #         device_settings = configs.units[device_uuid]
    #         # TODO(MBK): 'self.connection.get_device' ?
    #         theDevice = self.connection.get_device(device_uuid)
    #         temp = Device(
    #             device_id=device_settings.self_id,
    #             device_uuid=device_uuid,
    #             name=device_settings.name if device_settings.name else self._device_name_gen(device_settings.self_id),
    #             post_self=(not theDevice)
    #         )
    #         self.__add_device(device=temp, id=device_settings.self_id, name=device_settings.name)

    # def __init_values(self, uuid, parent, configs):
    #     # TODO(MBK): 'self.connection.get_value' ?    
    #     theValue = configs.units[uuid]
    #     temp = Value(
    #         name=theValue.name,
    #         value_id=theValue.self_id,
    #         value_uuid=uuid,
    #     )

    # -------------------------------------------------------------------------
    #   Status methods
    # -------------------------------------------------------------------------

    def onStatusChange(
        self,
        layer: StatusID,
        callback: Callable[[StatusID, str], None]
    ):
        """
        Configure an action when the Status have changed.

        def callback(layer: LayerEnum, newStatus: str):

        """
        observer.subscribe(
            event_name=layer,
            callback=callback
        )

    # -------------------------------------------------------------------------
    #   Network 'on-' methods
    # -------------------------------------------------------------------------

    def onChange(
        self,
        callback: Callable[[str, NetworkChangeType], None],
    ) -> None:
        """
        Configure a callback for when a change to the Network have occurred.

        # UNSURE(MBK): How should it get the data back?

        # def Networkcallback(name: str, event: NetworkChangeType, /) -> None:
        #     pass
        """
        def _cb(obj, method):
            if method == WappstoMethod.PUT:
                callback(...)

        self.connection.subscribe_network_event(
            uuid=self.uuid,
            callback=_cb
        )

    def onRequest(
        self,
        callback: Callable[[str, NetworkRequestType], None],
    ) -> None:
        """
        Configure a callback for when a request of the Network have been requested.

        # UNSURE(MBK): Name & Event, is the Same! o.0

        # def Networkcallback(name: str, event: NetworkRequestType, /) -> None:
        #     pass
        """
        def _cb(obj, method):
            if method in [WappstoMethod.DELETE, WappstoMethod.GET]:
                callback(...)

        self.connection.subscribe_network_event(
            uuid=self.uuid,
            callback=_cb
        )

    def onRefresh(
        self,
        callback: Callable[[None], None]
    ):
        """
        Configure an action when a refresh Network have been Requested.

        Normally when a refresh have been requested on a Network, ...
        ...
        # It can not! there is no '{"status":"update"}' that can be set.
        """
        def _cb(obj, method):
            if method == WappstoMethod.GET:
                callback()

        self.connection.subscribe_network_event(
            uuid=self.uuid,
            callback=_cb
        )

    def onDelete(
        self,
        callback: Callable[[None], None]
    ):
        """
        Configure an action when a Delete Network have been Requested.

        Normally when a Delete have been requested on a Network,
        it is when it is not wanted anymore, and the Network have been
        unclaimed. Which mean that all the devices & value have to be
        recreated, and/or the program have to close.
        """
        def _cb(obj, method):
            if method == WappstoMethod.DELETE:
                callback()

        self.connection.subscribe_network_event(
            uuid=self.uuid,
            callback=_cb
        )

    # -------------------------------------------------------------------------
    #   Network methods
    # -------------------------------------------------------------------------

    def change(self):
        pass

    def refresh(self):
        raise NotImplementedError("Method: 'refresh' is not Implemented.")

    def request(self):
        raise NotImplementedError("Method: 'request' is not Implemented.")

    def delete(self):
        """
        Normally it is used to unclaim a Network & delete all children.

        If a network delete itself, it will prompt a factory reset.
        This means that manufacturer and owner will be reset (or not),
        in relation of the rules set up in the certificates.
        """
        self.connection.delete_network(uuid=self.uuid)
        self._delete()

    def _delete(self):
        """Helper function for Delete, to only localy delete."""
        for c_uuid, c_obj in self.children_uuid_mapping.items():
            c_obj._delete()
        self.children_id_mapping.clear()
        self.children_name_mapping.clear()
        self.children_uuid_mapping.clear()

    # -------------------------------------------------------------------------
    #   Create methods
    # -------------------------------------------------------------------------

    def createDevice(
        self,
        name: Optional[str] = None,
        device_id: Optional[int] = None, 
        manufacturer: Optional[str] = None,
        product: Optional[str] = None,
        version: Optional[str] = None,
        serial: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Device:
        """
        Create a new Wappsto Device.

        A Wappsto Device is references something that is attached to the network
        that can be controlled or have values that can be reported to Wappsto.

        This could be a button that is connected to this unit,
        or in the case of this unit is a gateway, it could be a remote unit.
        """
        kwargs = locals()
        kwargs.pop('self')

        if not device_id:
            if self.children_id_mapping:
                device_id = max(self.children_id_mapping.keys()) + 1
            else:
                device_id = 0
        elif device_id in self.children_id_mapping:
            return self.children_uuid_mapping[self.children_id_mapping[device_id]]

        kwargs['device_uuid'] = self.cloud_id_mapping.get(device_id)
        # if kwargs['device_uuid']:
        #     kwargs['name'] = self._configs.units[self.uuid].children_name_mapping.get(kwargs['device_uuid'])

        if not kwargs['name']:
            kwargs['name'] = self._device_name_gen(device_id)
        elif kwargs['name'] in self.children_name_mapping.keys():
            # The Device have already been created.
            return self.children_uuid_mapping[self.children_name_mapping[kwargs['name']]]

        device_obj = Device(parent=self, **kwargs)
        self.__add_device(device_obj, device_id, kwargs['name'])
        return device_obj

    def __add_device(self, device: Device, id: int, name: str):
        """Helper function for Create, to only localy create it."""
        self.children_uuid_mapping[device.uuid] = device
        self.children_id_mapping[id] = device.uuid
        self.children_name_mapping[name] = device.uuid

    # -------------------------------------------------------------------------
    #   Connection methods
    # -------------------------------------------------------------------------

    def connect(self):
        pass

    def disconnect(self):
        pass

    def close(self):
        """."""
        if not self.closed:
            self.connection.close()
            self.closed = True
        # Disconnect
        pass
