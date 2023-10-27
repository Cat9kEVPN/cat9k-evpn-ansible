# Get the DAG related informations from 'show run nve' and 'show run | section ^interface' parsed CLI output 

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: dhcp_del_preprocess

short_description: This module contains functions used in preprocessing group_vars/dhcp_db.yml, for DHCP delete related playbooks
'''


def dhcp_del_dict(to_del, overlay_dict, header_output):

    del_header = False

    if 'all' in to_del:
        del_header = True
        to_del = list(overlay_dict['vrf'])
    elif sorted(to_del) == sorted(list(overlay_dict['vrf'])):
        del_header = True

    if del_header:
        dhcp_header_list = [
            'ip dhcp relay information option', 
            'ip dhcp relay information option vpn', 
            'ip dhcp snooping',
            'ip dhcp compatibility suboption link-selection standard',
            'ip dhcp compatibility suboption server-override standard'
        ]
        header_output = [k for k in header_output if k in dhcp_header_list]
    else:
        header_output = []

    dev_svis_dict = overlay_dict.get('svis', {})

    svis_dict = {}
    
    for svi, svi_val in dev_svis_dict.items():
        if svi_val['svi_type'] == 'access' and svi_val.get('vrf') in to_del:
            if 'helper_address' in svi_val:
                svis_dict.setdefault(svi, {}).setdefault(
                    'helper_address', svi_val['helper_address']
                )
            if 'dhcp_relay_source' in svi_val:
                svis_dict.setdefault(svi, {}).setdefault(
                    'relay_src_intf', svi_val['dhcp_relay_source']
                )

    return {'svis': svis_dict, 'dhcp_options': header_output}

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            to_del=dict(required=True,type='list'),
            overlay_dict=dict(required=True,type='dict'),
            header_output=dict(required=True,type='list')
    ),
        supports_check_mode=True
    )   

    result = dhcp_del_dict(
        module.params['to_del'],
        module.params['overlay_dict'],
        module.params['header_output'],
    ) 

    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
