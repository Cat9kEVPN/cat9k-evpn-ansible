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

    ret_dict = {'vrfs': []}

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

def svis_vrfs_dict(module, overlay_vars):

    dhcp_vars = overlay_vars['dhcp_vars']

    vrfs_dict = {}
    all_vrfs = []
    overlay_vrfs = overlay_vars.get('vrf', {})
    if 'all' in dhcp_vars:
        for vrf in overlay_vrfs:
            if vrf not in dhcp_vars:
                vrfs_dict[vrf] = dhcp_vars['all'].copy()
                all_vrfs.append(vrf)
            else:
               vrfs_dict[vrf] = dhcp_vars[vrf]

        if 'all' in overlay_vars['no_src_vrfs']:
            overlay_vars['no_src_vrfs'].remove('all')
            overlay_vars['no_src_vrfs'] += all_vrfs
    else:
        vrfs_dict = dhcp_vars

    vrfs_dict = assign_src_intf(module, overlay_vars, vrfs_dict)

    svis_dict = {}

    if vrfs_dict:
        overlay_svis = overlay_vars.get('svis', {})
        for svi, svi_data in overlay_svis.items():
            if svi_data['vrf'] in vrfs_dict and svi_data['svi_type'] == 'access':
                svis_dict.setdefault(svi_data['vrf'], []).append(svi)

    return {
        'vrfs': vrfs_dict, 
        'svis': svis_dict, 
    }

def assign_src_intf(module, interfaces_data, vrfs_dict):

    overlay_intf = interfaces_data.get('overlay_interfaces', {})

    for vrf in interfaces_data.get('no_src_vrfs', []):
        for intf in overlay_intf:
            if overlay_intf[intf]['vrf'] == vrf:
                vrfs_dict[vrf]['relay_src_intf'] = intf
                break 
        if 'relay_src_intf' not in vrfs_dict[vrf]: 
            module.fail_json(
                """Relay source interface for " + vrf +" is not defined 
                and cannot be found in hostvars/<node>.yml"""
            )

    return vrfs_dict

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            dhcp_vars=dict(required=False,type='dict'),
            overlay_dict=dict(required=False,type='dict')
    ),
        supports_check_mode=True
    )   

    if module.params['dhcp_vars']:
        result = vrfs_with_no_src(module, module.params['dhcp_vars'])

    if module.params['overlay_dict']:
        result = svis_vrfs_dict(module, module.params['overlay_dict'])  

    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
