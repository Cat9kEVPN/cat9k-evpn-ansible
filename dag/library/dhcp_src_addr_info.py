# Get the DAG related informations from 'show run nve' and 'show run | section ^interface' parsed CLI output 

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: dhcp_src_addr_info

short_description: This module contains functions used in preprocessing, for DHCP related playbooks
'''

def dhcp_vrf_addr_test(dhcp_dict):

    ret_dict = {}
    ret_dict['global_src_err'] = False
    ret_dict['no_src_vrf'] = []

    for vrf in dhcp_dict['vrfs']:
        if 'helper_vrf' not in dhcp_dict['vrfs'][vrf]:
            if 'relay_src_intf' not in dhcp_dict['vrfs'][vrf]:
                ret_dict['no_src_vrf'].append(vrf)
        else:
            if dhcp_dict['vrfs'][vrf]['helper_vrf'] == 'global':
                if 'relay_src_intf' not in dhcp_dict['vrfs'][vrf]: 
                    ret_dict['global_src_err'] = vrf
                    break
            else:
                if 'relay_src_intf' not in dhcp_dict['vrfs'][vrf]: 
                    ret_dict['no_src_vrf'].append(dhcp_dict['vrfs'][vrf]['helper_vrf'])

    ret_dict['no_src_vrf'] = list(dict.fromkeys(ret_dict['no_src_vrf']))

    return ret_dict

def dhcp_vrf_ovrly_intf(ovrly_intf_info):
    
    no_src_vrf = ovrly_intf_info['no_src_vrf']

    if 'all' in no_src_vrf: no_src_vrf = ovrly_intf_info['all_vrfs']
    
    ret_dict = {}
    ret_dict['overlay_intf'] = {}
    ret_dict['intf_err'] = False
    overlay_intf = ovrly_intf_info['overlay_intf']

    if no_src_vrf != []:
        for vrf in no_src_vrf:
            for intf in overlay_intf:
                if overlay_intf[intf]['vrf'] == vrf:
                    ret_dict['overlay_intf'][vrf] = intf
                    break            
            if vrf not in ret_dict['overlay_intf']: 
                ret_dict['intf_err'] = vrf
                break

    return ret_dict

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            dhcp_info=dict(required=False,type='dict'),
            ovrly_intf_info=dict(required=False,type='dict')
    ),
        supports_check_mode=True
    )   

    result = {}
    if module.params['dhcp_info']:
        dhcp_info = module.params['dhcp_info']
        result['dhcp_ret_dict'] = dhcp_vrf_addr_test(dhcp_info)

    if module.params['ovrly_intf_info']:
        ovrly_intf_info = module.params['ovrly_intf_info']
        result['dhcp_ret_dict'] = dhcp_vrf_ovrly_intf(ovrly_intf_info)  

    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
