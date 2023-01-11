from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: trm_preprocess

short_description: This module contains functions used in preprocessing trm_overlay_db.yml, for TRM related playbooks
'''

def filter_non_existing_vrfs(vrf_dict):
    filtered_vrfs = {}

    unfiltered_vrfs = vrf_dict['unfiltered_vrfs']
    overlay_vrfs = vrf_dict['overlay_vrfs']

    for vrf in unfiltered_vrfs:
        if vrf in overlay_vrfs:
            af_dict = {}
            for af in unfiltered_vrfs[vrf]['afs']:
                if af in overlay_vrfs[vrf]['address_family'] and 'mdt_auto_discovery' in overlay_vrfs[vrf]['address_family'][af]:
                    af_dict[af] = unfiltered_vrfs[vrf]['afs'][af]

            if 'ipv4' in af_dict or 'ipv6' in af_dict:
                filtered_vrfs[vrf] = unfiltered_vrfs[vrf]
                filtered_vrfs[vrf]['afs'] = af_dict
                
    return {'filtered_vrfs': filtered_vrfs}

def filter_trm_enabled_vrfs(overlay_vrf_dict):
    vrfs_unconfig = []

    for vrf in overlay_vrf_dict['vrf_interested']:
        if vrf not in vrfs_unconfig:
            if 'ipv4' in overlay_vrf_dict['db_dict'][vrf]['afs']:

                if 'ipv4' in overlay_vrf_dict['vrf_dict'][vrf]['address_family'] \
                    and 'mdt_auto_discovery' in overlay_vrf_dict['vrf_dict'][vrf]['address_family']['ipv4']:
                    pass
                else:
                    vrfs_unconfig.append(vrf)

        if vrf not in vrfs_unconfig:
            if 'ipv6' in overlay_vrf_dict['db_dict'][vrf]['afs']:

                if 'ipv6' in overlay_vrf_dict['vrf_dict'][vrf]['address_family'] \
                    and 'mdt_auto_discovery' in overlay_vrf_dict['vrf_dict'][vrf]['address_family']['ipv6']:
                    pass
                else:
                    vrfs_unconfig.append(vrf)
                
    return { 'vrfs_unconfig': vrfs_unconfig }

def filter_bgp_neighbors(bgp_data):
 
    bgp_dict = bgp_data['bgp_dict']
    mvpn_afs =  bgp_data['mvpn_afs']

    mvpn_af_neighbors = {}
    filtered_mvpn_afs = []

    as_num = list(bgp_dict.keys())[0]
    neighbors = list(bgp_dict[as_num]['address_family']['l2vpn evpn']['address_family_neighbor'])

    for af in mvpn_afs:
        if af+ ' mvpn' not in bgp_dict[as_num]['address_family']:
            mvpn_af_neighbors[af+'_mvpn_neighbors'] = neighbors
            filtered_mvpn_afs.append(af)

        else:
            try:
                af_mvpn_neighbor = bgp_dict[as_num]['address_family'][af+' mvpn']['address_family_neighbor']
            except KeyError:
                af_mvpn_neighbor = []

            unconfigured_neighbors = (set(neighbors)).difference(set(af_mvpn_neighbor))

            if unconfigured_neighbors != set():
                mvpn_af_neighbors[af+'_mvpn_neighbors'] = list(unconfigured_neighbors)
                filtered_mvpn_afs.append(af)

    return { 'mvpn_af_neighbors': mvpn_af_neighbors, 'mvpn_afs': filtered_mvpn_afs, 'as_number': as_num }

def collect_rp_loopback(vrf_trm_info):
    device_rp_dict, rp_lpbck_dict = {}, {}
    undel_vrfs_afs, del_vrfs_afs = {}, {}
    selected_vrfs = vrf_trm_info['vrfs']

    for vrf in selected_vrfs:
        trm_vrf_dict = selected_vrfs[vrf]
    
        # Get VRF AFs for VRFs in 'vrf' dict
        del_vrfs_afs.update(trm_vrf_dict['afs'])

        if 'fabric_anycast_rp' in trm_vrf_dict:
            vrf_rp = trm_vrf_dict['fabric_anycast_rp']
            rp_device = vrf_trm_info['inventory_leafs']
        elif 'fabric_internal_rp' in trm_vrf_dict:
            vrf_rp = trm_vrf_dict['fabric_internal_rp']
            rp_device = [vrf_rp['rp_device']]
        elif 'fabric_external_rp' in trm_vrf_dict:
            break

        if 'no_loopback_info' not in vrf_trm_info:
            if 'ipv4_rp_address' in vrf_rp:
                if len(vrf_rp['ipv4_rp_address'].split(' ')) == 1:
                    vrf_rp['ipv4_rp_address'] = vrf_rp['ipv4_rp_address'] + ' 255.255.255.255'

                rp_lpbck_dict.setdefault(vrf_rp['rp_loopback'], {})\
                    .setdefault('ipv4', vrf_rp['ipv4_rp_address'])

            if 'ipv6_rp_address' in vrf_rp:
                if len(vrf_rp['ipv6_rp_address'].split('/')) == 1:
                    vrf_rp['ipv6_rp_address'] = vrf_rp['ipv6_rp_address'] + '/128'

                rp_lpbck_dict.setdefault(vrf_rp['rp_loopback'], {})\
                    .setdefault('ipv6', vrf_rp['ipv6_rp_address'])

            rp_lpbck_dict[vrf_rp['rp_loopback']]['vrf'] = vrf 

        for leaf_dev in rp_device:
            device_rp_dict.setdefault(leaf_dev, []).append(vrf_rp['rp_loopback'])

    vrfs_afs = list(del_vrfs_afs.keys())

    if 'action' in vrf_trm_info:
        
        db_vrfs = vrf_trm_info['db_vrfs']
        selected_vrfs = list(selected_vrfs.keys())

        # all VRFs in trm_overlay_db are to be unconfigured for TRM

        if (set(db_vrfs.keys())).difference(set(selected_vrfs)):
            
            # Get VRF AFs for VRFs not in 'vrf' dict
            for vrf in db_vrfs:
                if vrf not in selected_vrfs:
                    undel_vrfs_afs.update(db_vrfs[vrf]['afs'])

            # Delete MVPN if TRM for all VRFs in trm_overlay_db.yml are to be unconfigured
            # mvpn afs to be deleted = (to-be deleted vrfs' afs) - (remaining vrfs' afs)
            vrfs_afs_unfiltered = vrfs_afs
            vrfs_afs = [af for af in vrfs_afs_unfiltered if af not in undel_vrfs_afs]

        vrfs_afs_tmp = vrfs_afs
        vrfs_afs = [af+' mvpn' for af in vrfs_afs_tmp]
        
    return {'rp_loopbacks': device_rp_dict, 'rp_intf': rp_lpbck_dict, 'vrf_mvpn': vrfs_afs}


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            vrf_trm_info=dict(required=False,type='dict'),
            filter_deleted_vrfs=dict(required=False,type='dict'),
            config_vrf_info=dict(required=False,type='dict'),
            get_bgp_af_neighbors=dict(required=False,type='dict')
    ),
        supports_check_mode=True
    )   

    result = {}

    if module.params['vrf_trm_info']:
        result = collect_rp_loopback(module.params['vrf_trm_info'])

    if module.params['filter_deleted_vrfs']:
        result = filter_non_existing_vrfs(module.params['filter_deleted_vrfs'])
    
    if module.params['config_vrf_info']:
        result = filter_trm_enabled_vrfs(module.params['config_vrf_info'])

    if module.params['get_bgp_af_neighbors']:
        result = filter_bgp_neighbors(module.params['get_bgp_af_neighbors'])

    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
