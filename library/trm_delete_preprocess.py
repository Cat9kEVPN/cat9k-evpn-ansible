from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: trm_delete_preprocess

short_description: This module contains functions used in preprocessing trm_overlay_db.yml, for TRM delete related playbooks
'''
import re as re

def leaf_vars_to_del(dev_ov_dict, dev_bgp_dict, dev_vrf_output, to_del):
    mvpn_to_remain = []
    rp_loopbacks = []
    svis = []
    bgp = {}
    vrfs = {}

    vrfs_dict = dev_ov_dict.get('vrf', {})
    for vrf, vrf_dict in vrfs_dict.items():
        for af, af_dict in vrf_dict['address_family'].items():
            if 'mdt_auto_discovery' in af_dict:
                if vrf in to_del:
                    vrfs.setdefault(vrf, {}).setdefault('afs', {}).setdefault(af, af_dict)
                else:
                    af_mvpn = af + ' mvpn'
                    if af_mvpn not in mvpn_to_remain:
                        mvpn_to_remain.append(af_mvpn)

    svis_dict = dev_ov_dict.get('svis', {})
    for svi, svi_dict in svis_dict.items():
        if svi_dict.get('pim_enable') and svi_dict.get('vrf') in to_del:
            svis.append(svi)

    ovvly_intf = dev_ov_dict.get('overlay_interfaces', {})
    for intf, intf_dict in ovvly_intf.items():
        if intf_dict.get('pim_enable') and intf_dict.get('vrf') in to_del:
            rp_loopbacks.append(intf)

    mvpns_to_del = [ip for ip in ['ipv4 mvpn', 'ipv6 mvpn'] if ip not in mvpn_to_remain]
    bgp = get_bgp_mvpns(dev_bgp_dict, mvpns_to_del)
    vrfs = parser_sec_vrf(dev_vrf_output, vrfs, to_del)
    
    return {
        'vrfs': vrfs, 
        'svis': svis, 
        'rp_loopbacks': rp_loopbacks, 
        'bgp': bgp, 
        'mvpns_to_del': mvpns_to_del
    }

def get_bgp_mvpns(dev_bgp_dict, mvpns_to_del):
    # Assume only one AS exists
    bgp_dict = dev_bgp_dict.get('bgp', {})
    for as_num, as_dict in bgp_dict.items():
        af_dict = as_dict.get('address_family',{})
        return {'as_number': as_num, 'mvpn_afs': [ip for ip in mvpns_to_del if ip in af_dict]}

def spine_vars_to_del(dev_bgp_dict, mvpns_to_del):
    return {'bgp': get_bgp_mvpns(dev_bgp_dict, mvpns_to_del)}

def parser_sec_vrf(showrunsecvrf, vrf_dict, to_del):
    """Parser for show running-config | sec vrf"""

    if showrunsecvrf:
        # ip pim vrf green rp-address 10.2.255.255
        p1 = re.compile(r'^ip pim vrf (?P<vrf>\w+) rp\-address (?P<ipv4>[\d.]+)$')

        # ipv6 pim vrf green rp-address FC00:2:255::255
        p2 = re.compile(r'^ipv6 pim vrf (?P<vrf>\w+) rp\-address (?P<ipv6>[\da-fA-F:]+)$')

        # ip pim vrf green register-source Loopback11
        p3 = re.compile(r'^ip pim vrf (?P<vrf>\w+) register\-source (?P<ipv4>[\w\d]+)$')

        # ipv6 pim vrf green register-source Loopback11
        p4 = re.compile(r'^ipv6 pim vrf (?P<vrf>\w+) register\-source (?P<ipv6>[\w\d]+)$')

        # ip pim vrf green ssm default
        p5 = re.compile(r'^ip pim vrf (?P<vrf>\w+) ssm (?P<default>default)?(range (?P<range>\S+))?$')

        for line in showrunsecvrf:
            line = line.strip()

            # ip pim vrf green rp-address 10.2.255.255
            m = p1.match(line)
            if m:
                group = m.groupdict()
                vrf = group['vrf']
                if vrf in to_del:
                    vrf_dict.setdefault(vrf, {}).setdefault(
                        'fabric_default', {}).setdefault(
                            'ipv4_rp_address', group['ipv4'])
                continue

            # ipv6 pim vrf green rp-address FC00:2:255::255
            m = p2.match(line)
            if m:
                group = m.groupdict()
                vrf = group['vrf']
                if vrf in to_del:
                    vrf_dict.setdefault(vrf, {}).setdefault(
                        'fabric_default', {}).setdefault(
                            'ipv6_rp_address', group['ipv6'])
                continue

            # ip pim vrf green register-source Loopback11
            m = p3.match(line)
            if m:
                group = m.groupdict()
                vrf = group['vrf']
                if vrf in to_del:
                    vrf_dict.setdefault(vrf, {}).setdefault(
                        'register_source', group['ipv4'])
                continue

            # ipv6 pim vrf green register-source Loopback11
            m = p4.match(line)            
            if m:
                group = m.groupdict()
                vrf = group['vrf']
                if vrf in to_del:
                    vrf_dict.setdefault(vrf, {}).setdefault(
                        'ipv6_register_source', group['ipv6'])
                continue

            # ip pim vrf green ssm default
            m = p5.match(line)
            if m:
                group = m.groupdict()
                vrf = group['vrf']
                if vrf in to_del:
                    if group['range']:
                        vrf_dict.setdefault(vrf, {}).setdefault(
                            'ssm_range', group['range'])
                continue
        
        return vrf_dict

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            node=dict(required=True,type='str'),
            dev_ov_dict=dict(required=False,type='dict'),
            dev_bgp_dict=dict(required=False,type='dict'),
            dev_vrf_output=dict(required=False,type='list'),
            to_del=dict(required=False,type='list'),
            mvpns_to_del=dict(required=False,type='list'),
    ),
        supports_check_mode=True
    )

    if module.params['node'] == 'leaf':
        result = leaf_vars_to_del(
            module.params['dev_ov_dict'], 
            module.params['dev_bgp_dict'],
            module.params['dev_vrf_output'], 
            module.params['to_del'],
        )
    elif module.params['node'] == 'spine':
        result = spine_vars_to_del( 
            module.params['dev_bgp_dict'],
            module.params['mvpns_to_del']
        )

    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
