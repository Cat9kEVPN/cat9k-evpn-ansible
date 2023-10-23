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

def collect_rp_loopback(vrf_trm_info):
    device_rp_dict, rp_lpbck_dict, vrf_mvpn = {}, {}, {}

    for vrf in vrf_trm_info['vrfs']:
        trm_vrf_dict = vrf_trm_info['vrfs'][vrf]
    
        vrf_mvpn.update(trm_vrf_dict['afs'])

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

    return {'rp_loopbacks': device_rp_dict, 'rp_intf': rp_lpbck_dict, 'vrf_mvpn': list(vrf_mvpn.keys())}

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            vrf_trm_info=dict(required=False,type='dict'),
            filter_deleted_vrfs=dict(required=False,type='dict')
    ),
        supports_check_mode=True
    )   

    result = {}

    if module.params['vrf_trm_info']:
        result = collect_rp_loopback(module.params['vrf_trm_info'])
    if module.params['filter_deleted_vrfs']:
        result = filter_non_existing_vrfs(module.params['filter_deleted_vrfs'])

    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
