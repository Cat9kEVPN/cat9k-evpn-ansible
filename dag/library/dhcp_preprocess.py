# Get the DAG related informations from 'show run nve' and 'show run | section ^interface' parsed CLI output 

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: dhcp_preprocess

short_description: This module contains functions used in preprocessing, for DHCP related playbooks
'''

def get_vrf_with_no_source_intf(dhcp_dict):

    ret_dict = {}
    ret_dict['global_src_err'] = False
    ret_dict['no_src_vrf'] = []

    for vrf in dhcp_dict['dag']:
        if 'helper_vrf' not in dhcp_dict['dag'][vrf]:
            if 'relay_src_intf' not in dhcp_dict['dag'][vrf]:
                ret_dict['no_src_vrf'].append(vrf)
        else:
            if dhcp_dict['dag'][vrf]['helper_vrf'] == 'global':
                if 'relay_src_intf' not in dhcp_dict['dag'][vrf]: 
                    ret_dict['global_src_err'] = vrf
                    break
            else:
                if 'relay_src_intf' not in dhcp_dict['dag'][vrf]: 
                    ret_dict['no_src_vrf'].append(dhcp_dict['dag'][vrf]['helper_vrf'])

    ret_dict['no_src_vrf'] = list(dict.fromkeys(ret_dict['no_src_vrf']))

    return ret_dict

def get_src_intf(ovrly_intf_info):
    
    no_src_vrf = ovrly_intf_info['no_src_vrf']
    
    ret_dict = {}
    ret_dict['overlay_intf'] = {}
    ret_dict['intf_err'] = False
    overlay_intf = ovrly_intf_info['overlay_intf']

    for vrf in no_src_vrf:
        for intf in overlay_intf:
            if overlay_intf[intf]['vrf'] == vrf:
                ret_dict['overlay_intf'][vrf] = intf
                break            
        if vrf not in ret_dict['overlay_intf']: 
            ret_dict['intf_err'] = vrf
            break

    return ret_dict

def get_filter_svis(filter_svis_dict):

    dhcp_dict = filter_svis_dict['dhcp_dict']
    dhcp_vrfs = dhcp_dict['dag']
    svis_dict = filter_svis_dict['svis_dict']
    overlay_intf = filter_svis_dict['overlay_intf']

    filtered_svis = {}
    vrf_dict = {}

    config_dhcp_header = True

    if filter_svis_dict['dhcp_output']:

        dhcp_header_list = [
            'ip dhcp relay information option', 
            'ip dhcp relay information option vpn', 
            'ip dhcp snooping']

        if 'option_82_link_selection_standard' in dhcp_dict['dhcp_options'] \
            and dhcp_dict['dhcp_options']['option_82_link_selection_standard'] == 'standard':
            dhcp_header_list.append('ip dhcp compatibility suboption link-selection standard')

        if 'option_82_server_id_override' in dhcp_dict['dhcp_options'] \
            and dhcp_dict['dhcp_options']['option_82_server_id_override'] == 'standard':
            dhcp_header_list.append('ip dhcp compatibility suboption server-override standard')

        if not (set(dhcp_header_list)).difference(set(filter_svis_dict['dhcp_output'])):
            config_dhcp_header = False

    # Get relay_src_interface and helper address info per VRFs

    for vrf in filter_svis_dict['all_vrfs']:
        mapped_vrf = vrf if vrf in dhcp_vrfs else 'all'     # map to 'all' if vrf not found in dhcp_db
        
        vrf_dict[vrf] = dhcp_vrfs[mapped_vrf].copy()

        if 'helper_vrf' not in vrf_dict[vrf]:
            intf_vrf = vrf
            vrf_dict[vrf]['helper_vrf'] = 'own'

        else:
            if vrf_dict[vrf]['helper_vrf'] != 'global':

                if vrf_dict[vrf]['helper_vrf'] == vrf:
                    intf_vrf = vrf
                    vrf_dict[vrf]['helper_vrf'] = 'own'
                else:
                    intf_vrf = vrf_dict[vrf]['helper_vrf']
                    vrf_dict[vrf]['helper_vrf'] = 'vrf ' + vrf_dict[vrf]['helper_vrf']
        
        if 'relay_src_intf' not in vrf_dict[vrf]:
            overlay_intf_list = []

            for intf in overlay_intf:
                if overlay_intf[intf]['vrf'] == intf_vrf:
                    overlay_intf_list.append(intf)

            vrf_dict[vrf]['relay_src_intf'] = overlay_intf_list
        else:
            vrf_dict[vrf]['relay_src_intf'] = [vrf_dict[vrf]['relay_src_intf']]

    # Check if SVIs are already configured and filter SVIs

    for svi in svis_dict:
        if 'vrf' in svis_dict[svi]:
            
            if svis_dict[svi]['vrf'] in filter_svis_dict['all_vrfs'] and svis_dict[svi]['svi_type'] == 'access':
                
                vrf = svis_dict[svi]['vrf']

                if 'helper_address' in svis_dict[svi] and 'dhcp_relay_source' in svis_dict[svi]:

                    # Check dhcp rely source
                    if svis_dict[svi]['dhcp_relay_source'] in vrf_dict[vrf]['relay_src_intf']:
                        pass
                    else:
                        filtered_svis.setdefault(vrf, []).append(svi)

                    svi_dict_helper_address = [svis_dict[svi]['helper_address'][idx]['ip_address']\
                        for idx in svis_dict[svi]['helper_address']]

                    # Check dhcp helper address
                    if not (set(vrf_dict[vrf]['helper_address'])).difference(set(svi_dict_helper_address)):

                        for helper_addr_idx in svis_dict[svi]['helper_address']:
                            helper_addr_dict = svis_dict[svi]['helper_address'][helper_addr_idx]

                            if 'reachable_over' not in helper_addr_dict:
                                helper_addr_dict['reachable_over'] = 'own'

                            try:
                                if helper_addr_dict['ip_address'] in vrf_dict[vrf]['helper_address']:
                                    assert helper_addr_dict['reachable_over'] == vrf_dict[vrf]['helper_vrf']
                            except AssertionError:
                                filtered_svis.setdefault(vrf, []).append(svi)
                                break
 
                    else:
                        filtered_svis.setdefault(vrf, []).append(svi)

                else:
                    filtered_svis.setdefault(vrf, []).append(svi)

    for vrf in filtered_svis:
        filtered_svis[vrf] = list(set(filtered_svis[vrf]))

    filtered_all_vrfs = list(filtered_svis.keys())
    
    # filter VRFs from dhcp dict if SVIs of that VRFs are already configured

    if (set(filter_svis_dict['all_vrfs'])).difference(set(filtered_all_vrfs)):
        
        filtered_dhcp_vrfs = {}

        for vrf in dhcp_vrfs.keys():
            if vrf in filtered_all_vrfs or vrf == 'all':
                filtered_dhcp_vrfs[vrf] = dhcp_vrfs[vrf]
    else:
        filtered_dhcp_vrfs = dhcp_vrfs

    ret_dict = { 'filtered_svis': filtered_svis, 'all_vrfs': filtered_all_vrfs, \
        'filtered_dhcp_vrfs': filtered_dhcp_vrfs, 'config_dhcp_header': config_dhcp_header }

    return ret_dict


def get_svis_info(vrfs_svis_dict):

    filtered_svis_dict = {}

    dhcp_options = vrfs_svis_dict['dhcp_options']

    config_dhcp_header = vrfs_svis_dict['config_dhcp_header']

    if config_dhcp_header:

        if vrfs_svis_dict['dhcp_output']:

            dhcp_header_list = ['ip dhcp relay information option', 
            'ip dhcp relay information option vpn', 
            'ip dhcp snooping']

            if 'option_82_link_selection_standard' in dhcp_options \
                and dhcp_options['option_82_link_selection_standard'] == 'standard':
                dhcp_header_list.append('ip dhcp compatibility suboption link-selection standard')

            if 'option_82_server_id_override' in dhcp_options \
                and dhcp_options['option_82_server_id_override'] == 'standard':
                dhcp_header_list.append('ip dhcp compatibility suboption server-override standard')

            if (set(dhcp_header_list)).intersection(set(vrfs_svis_dict['dhcp_output'])):
                config_dhcp_header = True
            else:
                config_dhcp_header = False

        else:
            config_dhcp_header = False

    for svi in vrfs_svis_dict['overlay_svis_dict']:

        svi_data = vrfs_svis_dict['overlay_svis_dict'][svi]

        if 'vrf' in svi_data:
            if svi_data['vrf'] in vrfs_svis_dict['all_vrfs'] and svi_data['svi_type'] == 'access':
                
                if 'helper_address' in svi_data:
                    filtered_svis_dict.setdefault(svi, {}).setdefault(
                        'helper_address', svi_data['helper_address'])

                if 'dhcp_relay_source' in svi_data:
                    filtered_svis_dict.setdefault(svi, {}).setdefault(
                        'relay_src_intf', svi_data['dhcp_relay_source'])

    return {'filtered_svis': filtered_svis_dict, 'config_dhcp_header': config_dhcp_header}

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            dhcp_dict=dict(required=False,type='dict'),
            no_src_vrf_dict=dict(required=False,type='dict'),
            filter_svis_dict=dict(required=False,type='dict'),
            vrfs_svis_dict=dict(required=False,type='dict')
    ),
        supports_check_mode=True
    )   

    result = {}
    if module.params['dhcp_dict']:
        result = get_vrf_with_no_source_intf(module.params['dhcp_dict'])

    if module.params['no_src_vrf_dict']:
        result = get_src_intf(module.params['no_src_vrf_dict']) 

    if module.params['filter_svis_dict']:
        result = get_filter_svis(module.params['filter_svis_dict']) 

    if module.params['vrfs_svis_dict']:
        result = get_svis_info(module.params['vrfs_svis_dict']) 

    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
