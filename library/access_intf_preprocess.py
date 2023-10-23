from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: access_intf_preprocess

short_description: This module contains functions used in preprocessing trm_overlay_db.yml, for TRM related playbooks
'''

def get_interfaces(access_interfaces, vlan_overlay_db):
    key_list = {'access': 'access_vlan', 'trunks': 'trunk_vlan_list'}

    interface_dict = {}
    interfaces_dict = {}

    for port_mode in access_interfaces:
        if port_mode in ['trunks', 'access']:
            if port_mode == 'trunks':
                interfaces_dict.setdefault(port_mode, [])
                if 'trunk_vlan_list' in access_interfaces:
                    port_vlans = access_interfaces['trunk_vlan_list']
                else:
                    port_vlans = vlan_overlay_db
            elif port_mode == 'access':
                interfaces_dict.setdefault(port_mode, [])
                port_vlans = access_interfaces.get('access_vlan')
            for interface in access_interfaces[port_mode]:
                if type(interface) == dict:
                    interface_dict['name'] = list(interface)[0]
                    if key_list[port_mode] in interface:
                        port_vlans = interface['vlan_list']
                else:
                    interface_dict['name'] = interface  
                interface_dict['vlans'] = port_vlans
                interfaces_dict[port_mode].append(interface_dict.copy())

    return interfaces_dict

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            access_interfaces=dict(required=True,type='dict'),
            vlan_overlay_db=dict(required=True,type='list')
    ),
        supports_check_mode=True
    )   

    result = {}

    result = get_interfaces(
        module.params['access_interfaces'], 
        module.params['vlan_overlay_db']
    )

    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
