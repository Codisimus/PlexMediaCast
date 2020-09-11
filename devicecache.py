import pychromecast

from util import *


def get_device_uuids():
    device_uuids = {}
    devices, browser = pychromecast.discover_chromecasts()
    pychromecast.stop_discovery(browser)
    for mDNS, uuid, model, name, ip, port in devices:
        device_uuids[name.casefold()] = uuid
    return device_uuids


class DeviceCache:
    device_uuids = get_device_uuids()

    @classmethod
    def refresh_cache(cls):
        cls.device_uuids = get_device_uuids()

    @classmethod
    def get_devices(cls):
        devices, browser = pychromecast.get_chromecasts()
        pychromecast.stop_discovery(browser)
        return devices

    @classmethod
    def get_device(cls, name):
        uuid = cls.device_uuids.get(name.casefold())
        if uuid:
            devices, browser = pychromecast.get_listed_chromecasts(uuids=[uuid])
            pychromecast.stop_discovery(browser)
            if devices:
                return list(devices)[0]
            else:
                raise NotFoundError('Device ' + name)
        else:
            device = find_by_attr(cls.get_devices(), 'name', name, case_sensitive=False)
            if device:
                cls.device_uuids[device['name']] = device['uuid']
                return device
            else:
                raise NotFoundError('Device ' + name)
