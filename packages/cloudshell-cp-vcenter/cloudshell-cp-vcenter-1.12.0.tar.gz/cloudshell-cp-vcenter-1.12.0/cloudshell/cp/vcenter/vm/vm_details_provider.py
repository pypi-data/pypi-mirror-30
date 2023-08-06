import re
from pyVmomi import vim

from cloudshell.cp.vcenter.common.vcenter.vmomi_service import pyVmomiService
from cloudshell.cp.vcenter.network.vnic.vnic_service import VNicService
from cloudshell.cp.vcenter.vm.ip_manager import VMIPManager


class VmDetailsProvider(object):
    def __init__(self, pyvmomi_service, ip_manager):
        self.pyvmomi_service = pyvmomi_service # type: pyVmomiService
        self.ip_manager = ip_manager  # type: VMIPManager

    def create(self, vm, name, reserved_networks, ip_regex, deployment_details_provider, logger):
        """"""
        vm_details = VmDetails(name)
        vm_details.vm_instance_data = self._get_vm_instance_data(vm, deployment_details_provider)
        vm_details.vm_network_data = self._get_vm_network_data(vm, reserved_networks, ip_regex, logger)
        return vm_details

    def _get_vm_instance_data(self, vm, deployment_details_provider):
        data = []

        data.extend(deployment_details_provider.get_details())

        memo_size_kb = vm.summary.config.memorySizeMB * 1024
        disk_size_kb = next((device.capacityInKB for device in vm.config.hardware.device if
                             isinstance(device, vim.vm.device.VirtualDisk)), 0)
        snapshot = None
        if vm.snapshot:
            snapshot = self._get_snapshot_path(vm.snapshot.rootSnapshotList, vm.snapshot.currentSnapshot)

        data.append(VmDataField('Current Snapshot', snapshot))
        data.append(VmDataField('CPU', '%s vCPU' % vm.summary.config.numCpu))
        data.append(VmDataField('Memory', self._convert_kb_to_str(memo_size_kb)))
        data.append(VmDataField('Disk Size', self._convert_kb_to_str(disk_size_kb)))
        data.append(VmDataField('Guest OS', vm.summary.config.guestFullName))

        return data

    def _get_vm_network_data(self, vm, reserved_networks, ip_regex, logger):
        data_list = []
        primary_ip = self._get_primary_ip(vm, ip_regex, logger)
        net_devices = [d for d in vm.config.hardware.device if isinstance(d, vim.vm.device.VirtualEthernetCard)]

        for device in net_devices:
            network = VNicService.get_network_by_device(vm, device, self.pyvmomi_service, logger)
            vlan_id = self._convert_vlan_id_to_str(VNicService.get_network_vlan_id(network))
            ip = self._get_ip_by_device(vm , device)

            if vlan_id and (network.name.startswith('QS_') or network.name in reserved_networks):
                data = VmNetworkData()
                data.interface_id = device.macAddress
                data.is_predefined = network.name in reserved_networks
                data.network_id = vlan_id
                if ip:
                    data.is_primary = primary_ip == ip
                data.network_data.append(VmDataField('IP', ip))
                data.network_data.append(VmDataField('MAC Address', device.macAddress))
                data.network_data.append(VmDataField('Network Adapter', device.deviceInfo.label))
                data.network_data.append(VmDataField('Port Group Name', network.name))
                data_list.append(data)

        return data_list

    def _get_primary_ip(self, vm, ip_regex, logger):
        match_function = self.ip_manager.get_ip_match_function(ip_regex)
        primary_ip = self.ip_manager.get_ip(vm, None, match_function, None, None, logger).ip_address
        return primary_ip

    @staticmethod
    def _get_ip_by_device(vm, device):
        for net in vm.guest.net:
            if str(net.deviceConfigId) == str(device.key):
                return next(iter(net.ipAddress), None)
        return None

    @staticmethod
    def _get_snapshot_path(nodes, snapshot):
        for node in nodes:
            if node.snapshot == snapshot:
                return node.name
            sn = VmDetailsProvider._get_snapshot_path(node.childSnapshotList, snapshot)
            if sn:
                return node.name + '/' + sn
        return None

    @staticmethod
    def _convert_kb_to_str(kb):
        mb = kb / 1024
        gb = mb / 1024
        if gb > 0:
            return '%0.0f GB' % gb
        elif mb > 0:
            return '%0.0f MB' % mb
        else:
            return '%0.0f KB' % kb

    @staticmethod
    def _convert_vlan_id_to_str(vlan_id):
        if vlan_id:
            if isinstance(vlan_id, list):
                return ','.join([VmDetailsProvider._convert_vlan_id_to_str(v) for v in vlan_id if v])

            if isinstance(vlan_id, vim.NumericRange):
                if vlan_id.start == vlan_id.end:
                    return '%s' % vlan_id.start
                else:
                    return '%s-%s' % (vlan_id.start, vlan_id.end)

            if isinstance(vlan_id, str):
                return vlan_id

            if isinstance(vlan_id, int):
                return str(vlan_id)

        return ''


class VmDetails(object):
    def __init__(self, app_name):
        self.app_name = app_name
        self.error = None
        self.vm_instance_data = []  # type: list[VmDataField]
        self.vm_network_data = []  # type: list[VmNetworkData]


class VmNetworkData(object):
    def __init__(self):
        self.interface_id = None  # type: str
        self.network_id = None  # type: str
        self.is_primary = False  # type: bool
        self.network_data = []  # type: list[VmDataField]


class VmDataField(object):
    def __init__(self, key, value, hidden=False):
        self.key = key
        self.value = value
        self.hidden = hidden
