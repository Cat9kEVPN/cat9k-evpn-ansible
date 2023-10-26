# Validate overlay_db.yml for any errors

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: overlay_yml_validation

short_description: This module contains functions used to validate group_vars/overlay_db.yml
'''

import re
import yaml, json
import ipaddress
from netaddr import IPAddress
import collections

check_result = collections.defaultdict(list)
dup_dict = {}
rd_dup_dict = {}

def yaml_error_validation(overlay_data, verbose_mode):
    """
    validate some error senarios in the yaml file
    Args:
        overlay_data: yaml file converted to dict
        verbose_mode: for completed output 
    Returns:
        string : "partial validation for vlan and svi is done successfully"
    Raises:
        KeyError if key not founds
    Error_senarios :
        vni duplication,evi duplication,svi_type core duplication
    """

    # NVE interface test
    for nve, nve_data in overlay_data['nve_interfaces'].items():
        if nve_data['source_interface']:
            check_result['success_msg'].append(
                "source_interface {} is present under nve_interfaces".format(
                    nve_data['source_interface']
                )
            )
        else:
            check_result['error_msg'].append(
                "mandatory parameter {} not found under nve_interfaces {}".format(e,nve)
            ) 
    
    # VLAN test
    try:
        for vlan, vlan_data in overlay_data['vlans'].items():
            if vlan_data['vni'] :
                dup_dict.setdefault('vni', {}).setdefault(vlan_data['vni'], set()).add(vlan)
            if vlan_data['vlan_type'] == "access" and vlan_data['evi']:
                dup_dict.setdefault('evi', {}).setdefault(vlan_data['vni'], set()).add(vlan)
            if vlan_data['vlan_type'] == "core" and vlan_data['vrf']:
                dup_dict.setdefault('vrf', {}).setdefault(vlan_data['vni'], set()).add(vlan)
    except KeyError as e :
        check_result['error_msg'].append(
            "mandatory parameter {} not found under vlan {}".format(e,vlan)
        )

    for vlan_key, vlan_val in dup_dict.items():
        count = 0

        for key, val in vlan_val.items():
            if len(val) > 1:
                count+=1
                check_result['error_msg'].append(
                    "Failed due to {} {} found under VLANS {}".format(key, vlan_key, val)
                )
        if count == 0:
            check_result['success_msg'].append(
                "Checked VLAN and {} mappping".format(vlan_key)
            )

    # -----
    if check_result['error_msg']:
        return check_result['error_msg']
    else:
        if verbose_mode:
            return ("Partial validation for VLAN and NVE interface is done successfully", check_result['success_msg'])
        else:
            return ("Partial validation for VLAN and NVE interface is done successfully")

def vlan_svi_validation(overlay_data, verbose_mode) :
    """
    validate some error senarios in the yaml file
    Args:
        overlay_data: yaml file converted to dict
        verbose_mode: for completed output 
    Returns:
        string : "complete validation for vlan and svi is done successfully",list of data
    Raises:
        KeyError if key not found
    Error_senarios :
        Incomplete vlan id's , Incomplete svi_id's, 
        replication_mcast for static and ingress , 
        svi_vaid_ipv4 , svi_valid_ipv6 , svi_valid_mac 
    """

    if 'svis' not in overlay_data:
        return []
    
    try:
        l2vpn_global_gw = overlay_data['l2vpn_global']['default_gw']
    except:
        l2vpn_global_gw = 'not defined'

    # VLAN - SVI mapping
    vlan_diff = set(overlay_data['vlans']).difference(overlay_data['svis'])
    svi_diff = set(overlay_data['svis']).difference(overlay_data['vlans'])

    if vlan_diff:
        check_result['error_msg'].append(
            "vlan_id {} present under VLANS is not present under SVIS".format(list(vlan_diff))
        )
    else :
        check_result['vlan_valid_lst'].append("All VLANs are valid")

    if svi_diff:
        check_result['error_msg'].append(
            "svi_id {} present under SVIS is not present under VLANS".format(list(svi_diff))
        )    
    else :
        check_result['svi_valid_lst'].append("All SVIs  are valid")

    # SVI keys check
    acc_vlan_vars = {'vni', 'evi', 'encapsulation', 'replication_type'}
    core_vlan_vars = {'vni', 'vrf'}

    for vlans, vlans_data in overlay_data['vlans'].items():
        if 'vlan_type' in vlans_data:
            vlan_type = vlans_data['vlan_type']

            if vlan_type == 'access':
                check_parameters = acc_vlan_vars.difference(vlans_data.keys())
                if check_parameters:
                    check_result['error_msg'].append(
                        "mandatory parameter not found {} under VLAN {}".format(check_parameters, vlans)
                    )
                else:
                    if vlans_data['replication_type'] == 'static':
                        if 'replication_mcast' in vlans_data:
                            check_result['vlan_rep_lst'].append(
                                "replication_mcast ip {} for vlan {} is present".format(
                                    vlans_data['replication_mcast'], vlans
                                )
                            )
                        else:
                            check_result['error_msg'].append(
                                "mandatory key {} not found under VLAN {}".format(e, vlans)
                            )
                    elif vlans_data['replication_type'] == 'ingress':
                        if 'replication_mcast' in vlans_data:
                            check_result['error_msg'].append(
                                "replication_mcast ip is present of VLAN {} for replication_type ingress is not expected".format(vlans)
                            )

                    check_result['vni_lst'].append(
                        "vni {} is present under vlan {} of vlan_type {}".format(
                            vlans_data['vni'], vlans, vlan_type
                        )
                    )
                    check_result['evi_lst'].append(
                        "evi {} is present under vlan {} of vlan_type {}".format(
                            vlans_data['evi'], vlans, vlan_type
                        )
                    )
            
            elif vlan_type == 'core':
                check_parameters = core_vlan_vars.difference(vlans_data.keys())
                if check_parameters:
                    check_result['error_msg'].append(
                        "mandatory parameter not found {} under VLAN {}".format(check_parameters, vlans)
                    )
                else:
                    check_result['vlan_vrf_lst'].append(vlans_data['vrf'])
                    check_result['vni_lst'].append(
                        "vni {} is present under vlan {} of vlan_type {} for vrf {}".format(
                            vlans_data['vni'], vlans, vlan_type, vlans_data['vrf']
                        )
                    )
        else:
            check_result['error_msg'].append(
                "mandatory parameter not found {} under VLAN {}".format(e, vlans)
            )
        
        # SVI key check
        if vlans in overlay_data['svis']:
            svi_data = overlay_data['svis'][vlans]
            check_parameters = {'vrf', 'svi_type'}.difference(svi_data.keys())
            
            if check_parameters:
                check_result['error_msg'].append(
                    "mandatory parameter {} not found under access SVIS {}".format(check_parameters, vlans)
                )
                
            else: 
                if svi_data['svi_type'] == "access":
                    # IP check
                    if 'ipv4' in svi_data:
                        try:
                            ipv4_pattren = re.split(r' ', svi_data['ipv4'])
                            ipv4_address = ipv4_pattren[0] + '/' + str(IPAddress(ipv4_pattren[1]).netmask_bits())
                            ip = ipaddress.ip_network(ipv4_address, strict=False)
                            if isinstance(ip, ipaddress.IPv4Network):
                                check_result['svis_ipv4_lst'].append(
                                    "IPv4 address {0} under svi {1} with access is valid".format(
                                        svi_data['ipv4'],vlans
                                    )
                                )
                        except Exception as e :
                            check_result['error_msg'].append(
                                "IPv4 address {0} under SVI {1} with access is Invalid".format(
                                    svi_data['ipv4'], vlans
                                )
                            )
                    else:
                        check_result['error_msg'].append(
                            "ipv4 address not found under svis {}".format(vlans)
                        )
                        
                    if 'ipv6' in svi_data :
                        for ipv6_address in svi_data['ipv6']:
                            try :
                                ip = ipaddress.ip_network(ipv6_address, strict=False)
                                if isinstance(ip, ipaddress.IPv6Network):
                                    check_result['svis_ipv6_lst'].append (
                                        "IPv6 address {0} for {1} vlan of svi with access are valid".format(ipv6_address, vlans)
                                    )
                            except ValueError as e :
                                check_result['error_msg'].append(
                                    "IPv6 address {0} for {1} vlan of SVI with access is Invalid".format(
                                        svi_data['ipv6'], vlans
                                    )
                                )
                    else:
                        check_result['svis_ipv6_lst'].append(
                            "ipv6 address not found under svis {}".format(vlans)
                        )
                    
                    # MAC check
                    if l2vpn_global_gw == "no":
                        mac_pattren = re.compile("^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})|([0-9a-fA-F]{4}\\.[0-9a-fA-F]{4}\\.[0-9a-fA-F]{4})$")
                        try:
                            if svi_data['mac']:
                                if(re.search(mac_pattren, svi_data['mac'])):
                                    check_result['svis_mac_lst'].append(
                                        "Mac address {0} for {1} vlan of svi with access are valid".format(svi_data['mac'], vlans)
                                    )
                                else :
                                    check_result['error_msg'].append(
                                        "Mac address {0} for {1} vlan of SVI with access is Invalid".format(svi_data['mac'],vlans)
                                    )
                        except KeyError:
                            check_result['error_msg'].append(
                                "Mac address not found under svis {}".format(vlans)
                            )
                            
                    elif l2vpn_global_gw == "yes":
                        if 'mac' in svi_data: 
                            check_result['svis_mac_lst'].append(
                                "warning: mac_address found under svis {} is not required ".format(vlans)
                            )
                        else:
                            check_result['svis_mac_lst'].append(
                                "mac address not found under svis {} is expected ".format(vlans)
                            )
                    else:
                        check_result['svis_mac_lst'].append(
                            "mandatory parameter 'default_gw' not found under l2vpn_global"
                        )
                elif svi_data['svi_type'] == "core":
                    if 'src_intf' not in svi_data:
                        check_result['error_msg'].append(
                            "mandatory parameter {} not found under core SVI {}".format(e,vlans)
                        )
                    if 'ipv6_enable' in svi_data and svi_data['ipv6_enable']:
                        check_result['svis_ipv6_lst'].append(
                            "ipv6 is enabled under svi {}".format(vlans)
                        )
                    else:
                        check_result['svis_ipv6_lst'].append(
                            "ipv6_enable is not found {} under svi {}".format(e,vlans)
                        )
                        
                    if svi_data['vrf'] in check_result['vlan_vrf_lst'] :
                        check_result['svi_vrf_lst'].append(svi_data['vrf'])
                    else :
                        check_result['error_msg'].append(
                            "VRF present under {} SVI {} but not in core VLAN {}".format(
                                vlans, svi_data['vrf'], vlans
                            ) 
                        )

    
    if  check_result['error_msg'] :
        return check_result['error_msg']
    else:
        ret_tup = ("Complete validation for VLANs and SVIs are done successfully",)
        list_to_check = ['vlan_valid_lst', 
                         'svi_valid_lst', 
                         'vlan_rep_lst', 
                         'vni_lst, evi_lst', 
                         'svis_ipv4_lst', 
                         'svis_ipv6_lst', 
                         'svis_mac_lst'
                        ]
        if verbose_mode:
            for res in list_to_check:
                if check_result[res]:
                    ret_tup += (check_result[res],)
                
            return ret_tup
        else :
            return ret_tup
    
def vrf_validation(overlay_data, verbose_mode) :
    """
    validate some error senarios in the yaml file
    Args:
        overlay_data: yaml file converted to dict
        verbose_mode: for completed output 
    Returns:
        string : "vrf validation is done successfully",list of data
    Raises:
        KeyError if key not found
    Error_senarios :
        Found ipv6 under vrf but not found under svi's
        Found ipv6 under vrf and found under svi's
        Found ipv6 under svi's but not found under vrf's
        ipv4 under vrf is present or not
        rd under vrf is present or not        
    """
    if 'vrfs' not in overlay_data:
        return []
    
    for svi, svi_data in overlay_data['svis'].items():
        try:
            svi_vrf = svi_data['vrf']           
    
            # IPv6 in SVI not under VRF
            if ((svi_data['svi_type'] == "access" and svi_data['ipv6']) or 
                    (svi_data['svi_type'] == "core" and svi_data['ipv6_enable'] == "yes")):
                if svi_vrf in overlay_data['vrfs']:  
                    try:
                        if overlay_data['vrfs'][svi_vrf]['afs']['ipv6']:
                            check_result['vrf_success_msg'].append(
                                "IPv6 present under SVI {} and resepective VRF {}".format(svi, svi_vrf)
                            )
                    except KeyError as e :
                        check_result['vrf_error_msg'].append(
                            "ipv6 parameter present under SVI {} but not present under VRF {}".format(
                                svi, svi_vrf
                            )
                        )
                else:
                    pass
            else:
                # IPv6 in VRF not under SVIs
                if 'ipv6' in overlay_data['vrfs'][svi_vrf]['afs']:
                    check_result['vrf_error_msg'].append(
                        "IPv6 key not found under svi {}".format(svi, vrf)
                    )
                else: 
                    check_result['vrf_success_msg'].append(
                        "IPv6 not found under vrf {} and svi {} which is expected".format(
                            overlay_data['svis'][svi]['vrf'], svi
                        )
                    ) 
        except KeyError as e : 
            check_result['vrf_error_msg'].append(
                "mandatory parameter {} not found under SVIS {}".format(e,svi)
            )

    for vrf, vrf_data in overlay_data['vrfs'].items():
        # Check RD, IPv4 rt import and export
        try:
            if vrf_data['rd']:
                rd_dup_dict.setdefault(vrf_data['rd'], set()).add(vrf)

            if (vrf_data['afs']['ipv4']['rt_import'] and 
                    vrf_data['afs']['ipv4']['rt_export']):
                check_result['vrf_success_msg'].append(
                    "IPv4 and respective RTs is present under VRF {}".format(vrf)
                ) 
        except KeyError as e:
            check_result['vrf_error_msg'].append(
                "mandatory parameter not found {} under VRF {}".format(e, vrf)
            )

    count = 0
    for key, val in rd_dup_dict.items():
        if len(val) > 1:
            count+=1
            check_result['vrf_error_msg'].append(
                "{} rd is found under VRFs {}".format(key ,val)
            )
    if count == 0:
        check_result['vrf_success_msg'].append(
            "Checked VLAN and RD mappping"
        ) 

    if check_result['vrf_error_msg']:
        return check_result['vrf_error_msg']
    else:
        if verbose_mode:
            return ("VRF validation is done successfully", check_result['vrf_success_msg'])
        else:
            return ("VRF validation is done successfully")
    
def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        overlay_data=dict(type='dict', required=True),
        verbose=dict(type='bool', required=False)
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    
    verbose_mode = module.params.get('verbose', False)

    result['yaml_precheck']= (
        yaml_error_validation(
            module.params['overlay_data'],
            verbose_mode
        ) +
        vlan_svi_validation(
            module.params['overlay_data'],
            verbose_mode
        ) +
        vrf_validation(
            module.params['overlay_data'],
            verbose_mode
        )
    )

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
