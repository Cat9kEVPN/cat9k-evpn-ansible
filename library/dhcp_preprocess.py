# Get the DAG related informations from 'show run nve' and 'show run | section ^interface' parsed CLI output 

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: dhcp_preprocess

short_description: This module contains functions used in preprocessing group_vars/dhcp_db.yml, for DHCP delete related playbooks
'''

def vrfs_with_no_src(module, vrfs_dict):

    ret_dict = {}
    ret_dict['vrfs'] = []

    for vrf in vrfs_dict:
        if 'helper_vrf' not in vrfs_dict[vrf]:
            if 'relay_src_intf' not in vrfs_dict[vrf]:
                ret_dict['vrfs'].append(vrf)
        else:
            if vrfs_dict[vrf]['helper_vrf'] == 'global':
                if 'relay_src_intf' not in vrfs_dict[vrf]:
                    module.fail_json(
                        "Relay source interface for " + vrf +" is not defined in group_vars/dhcp_db.yml"
                    )
            else:
                if 'relay_src_intf' not in vrfs_dict[vrf]: 
                    ret_dict['vrfs'].append(vrfs_dict[vrf]['helper_vrf'])

    ret_dict['vrfs'] = list(dict.fromkeys(ret_dict['vrfs']))

    return ret_dict

def assign_src_intf(module, ovrly_intf_info):

    no_src_vrf = ovrly_intf_info['no_src_vrf']

    if 'all' in no_src_vrf: 
        no_src_vrf = ovrly_intf_info['all_vrfs']

    ret_dict = {}
    overlay_intf = ovrly_intf_info['overlay_intf']

    if no_src_vrf != []:
        for vrf in no_src_vrf:
            for intf in overlay_intf:
                if overlay_intf[intf]['vrf'] == vrf:
                    ret_dict[vrf] = intf
                    break            
            if vrf not in ret_dict: 
                module.fail_json(
                    """Relay source interface for " + vrf +" is not defined 
                    and cannot be found in hostvars/<node>.yml"""
                )

    return ret_dict

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            get_no_src_vrf=dict(required=False,type='dict'),
            get_src_intf=dict(required=False,type='dict')
    ),
        supports_check_mode=True
    )   

    result = {}
    if module.params['get_no_src_vrf']:
        result = vrfs_with_no_src(module, module.params['get_no_src_vrf'])

    if module.params['get_src_intf']:
        result = assign_src_intf(module, module.params['get_src_intf'])  

    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
