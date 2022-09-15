#Validate overlay_db.yml for any errors

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.module_utils.basic import AnsibleModule

import re
import yaml, json
import ipaddress
from netaddr import IPAddress
import collections

mul_list_dict = collections.defaultdict(list)
vni_dup_dict = {}
vni_dict = {}
evi_dict = {}
evi_dup_dict = {}
vlan_vrf_dup_dict = {}
vlan_vrf_dict = {}
svi_vrf_dup_dict = {}
svi_vrf_dict = {}
rd_dict = {}
rd_dup_dict = {}

def yaml_error_validation(parsed_yaml,debug):
    """
    validate some error senarios in the yaml file
    Args:
        parsed_yaml: yaml file converted to dict
        debug: for completed output 
    Returns:
        string : "partial validation for vlan and svi is done successfully"
    Raises:
        KeyError if key not founds
    Error_senarios :
        vni duplication,evi duplication,svi_type core duplication
    """

    for nve in parsed_yaml['nve_interfaces'].keys() :
        try :
            if len(parsed_yaml['nve_interfaces'][nve]['source_interface']) != 0 :
                mul_list_dict['nve_lst'].append("source_interface {} is present under nve_interfaces".format(parsed_yaml['nve_interfaces'][nve]['source_interface']))
        except TypeError as e :
                mul_list_dict['yaml_error_validation_error_lst'].append("mandatory parameter {} not found under nve_interfaces {}".format(e,nve)) 

    for vlan,vlan_data in parsed_yaml['vlans'].items():
        mul_list_dict['vlan_validation_lst'].append(vlan)
    
    for svi,svi_data in parsed_yaml['svis'].items() :
            mul_list_dict['svis_vlan_validation_lst'].append(svi)
    
    try :
        for vlan,vlan_data in parsed_yaml['vlans'].items():
            if parsed_yaml['vlans'][vlan]['vni'] :
                vni_dict[vlan] = vlan_data['vni']
        for key,value in vni_dict.items():
            vni_dup_dict.setdefault(value, set()).add(key)
        key_vni_result = [key for key, values in vni_dup_dict.items()
              if len(values) > 1]
        value_vni_result = [values for key, values in vni_dup_dict.items()
              if len(values) > 1]
        if  key_vni_result and value_vni_result :
            mul_list_dict['yaml_error_validation_error_lst'].append("Failed due to {} VNI found under VLANS {}".format(key_vni_result,value_vni_result))
    except  KeyError as e :
        mul_list_dict['yaml_error_validation_error_lst'].append("mandatory parameter {} not found under vlan {}".format(e,vlan)) 
    
    try :
        for vlan,vlan_data in parsed_yaml['vlans'].items():
            if parsed_yaml['vlans'][vlan]['vlan_type'] == "core" :
                if parsed_yaml['vlans'][vlan]['vrf'] :
                    vlan_vrf_dict[vlan] = vlan_data['vrf']
        for key,value in vlan_vrf_dict.items():
            vlan_vrf_dup_dict.setdefault(value, set()).add(key)
        key_vlan_vrf_result = [key for key, values in vlan_vrf_dup_dict.items()
              if len(values) > 1]
        value_vlan_vrf_result = [values for key, values in vlan_vrf_dup_dict.items()
              if len(values) > 1]
        if  key_vlan_vrf_result and value_vlan_vrf_result :
            mul_list_dict['yaml_error_validation_error_lst'].append("{} VRF of vlan_type core is found under VLANS {}".format(key_vlan_vrf_result,value_vlan_vrf_result))
    except KeyError as e:
        mul_list_dict['yaml_error_validation_error_lst'].append("mandatory parameter not found {} under vlan {}".format(e, vlan))

    try :
        for svi,svi_data in parsed_yaml['svis'].items() :
            if parsed_yaml['svis'][svi]['svi_type'] == "core" :
                if parsed_yaml['svis'][svi]['vrf'] :
                    svi_vrf_dict[svi] = svi_data['vrf']
        for key,value in svi_vrf_dict.items():
            svi_vrf_dup_dict.setdefault(value, set()).add(key)
        key_svi_vrf_result = [key for key, values in svi_vrf_dup_dict.items()
              if len(values) > 1]
        value_svi_vrf_result = [values for key, values in svi_vrf_dup_dict.items()
              if len(values) > 1]
        if  key_svi_vrf_result and value_svi_vrf_result :
            mul_list_dict['yaml_error_validation_error_lst'].append("{} VRF of svi_type core is found under VLANS {}".format(key_svi_vrf_result,value_svi_vrf_result))
    except KeyError as e:
        mul_list_dict['yaml_error_validation_error_lst'].append("mandatory parameter {} not found under svis {}".format(e, svi))
    

    if debug == "verbose" :
        if  mul_list_dict['yaml_error_validation_error_lst'] :
            for error in mul_list_dict['yaml_error_validation_error_lst'] :
                return  mul_list_dict['yaml_error_validation_error_lst']
        else :
            return ("partial validation for vlan and svi is done successfully",mul_list_dict['nve_lst'])
    else :
        if  mul_list_dict['yaml_error_validation_error_lst'] :
            for error in mul_list_dict['yaml_error_validation_error_lst'] :
                return  mul_list_dict['yaml_error_validation_error_lst']
        else :
            return ("partial validation for vlan and svi is done successfully")
    
    
    

def vlan_svi_validation(parsed_yaml,debug) :
    """
    validate some error senarios in the yaml file
    Args:
        parsed_yaml: yaml file converted to dict
        debug: for completed output 
    Returns:
        string : "complete validation for vlan and svi is done successfully",list of data
    Raises:
        KeyError if key not found
    Error_senarios :
        Incomplete vlan id's , Incomplete svi_id's, replication_mcast for static and ingress , svi_vaid_ipv4 , svi_valid_ipv6 , svi_valid_mac 
    """
        
    vlan_set_difference = set(mul_list_dict['vlan_validation_lst']).difference(set(mul_list_dict['svis_vlan_validation_lst']))
    if vlan_set_difference :
        mul_list_dict['vlan_svi_validation_error_lst'].append("vlan_id {} present under  VLANS is not present under SVIS".format(list(vlan_set_difference)))
    else :
        mul_list_dict['vlan_id_validation_lst'].append("All vlans are valid ")
    
    svi_set_difference = set(mul_list_dict['svis_vlan_validation_lst']).difference(set(mul_list_dict['vlan_validation_lst']))
    if svi_set_difference :
        mul_list_dict['vlan_svi_validation_error_lst'].append("svi_id {} present under SVIS is not present under VLANS".format(list(svi_set_difference)))    
    else :
        mul_list_dict['svi_validation_lst'].append("All svis  are valid ")
        
    for vlans,vlans_data in parsed_yaml['vlans'].items():
        try:
            if vlans_data['vlan_type'] == 'core' and vlans_data['vni'] and vlans_data['vrf'] :
                mul_list_dict['vlan_vrf_lst'].append(vlans_data['vrf'])
                mul_list_dict['vni_lst'].append("vni {} is present under vlan {} of vlan_type {} for vrf {}".format(vlans_data['vni'],vlans,vlans_data['vlan_type'],vlans_data['vrf']))
                
            
        except KeyError as e:
            mul_list_dict['vlan_svi_validation_error_lst'].append("mandatory parameter not found {} under VLAN {}".format(e, vlans))

        try : 
            if vlans in parsed_yaml['svis'].keys() :       
                try :
                    if parsed_yaml['svis'][vlans]['svi_type'] == "core" and parsed_yaml['svis'][vlans]['vrf'] and parsed_yaml['svis'][vlans]['src_intf'] :
                        try :
                            if parsed_yaml['svis'][vlans]['ipv6_enable'] :
                                mul_list_dict['svis_ipv6_lst'].append("ipv6 is enabled under svi {}".format(vlans))
                        except KeyError as e :
                            mul_list_dict['svis_ipv6_lst'].append("mandatory parameter not found {} under svis {}".format(e,vlans))
                            
                        if  parsed_yaml['svis'][vlans]['vrf'] in mul_list_dict['vlan_vrf_lst'] :
                            mul_list_dict['svi_vrf_lst'].append(parsed_yaml['svis'][vlans]['vrf'])
                        else :
                            mul_list_dict['vlan_svi_validation_error_lst'].append("vrf present under {} SVI {} but not in core VLAN {}".format(vlans,parsed_yaml['svis'][vlans]['vrf'],vlans) )
                except KeyError as e :
                    mul_list_dict['vlan_svi_validation_error_lst'].append("mandatory parameter {} not found under core SVI {}".format(e,vlans))
        except KeyError as e:
            mul_list_dict['vlan_svi_validation_error_lst'].append("mandatory parameter not found {} under svis {}".format(e, vlans))

    
    if debug == "verbose" :
        if  mul_list_dict['vlan_svi_validation_error_lst'] :
            for error in mul_list_dict['vlan_svi_validation_error_lst'] :
                return  mul_list_dict['vlan_svi_validation_error_lst']
        else :
            return ("complete validation for vlan and svi is done successfully",mul_list_dict['vlan_id_validation_lst'],mul_list_dict['svi_validation_lst'],mul_list_dict['vni_lst'],mul_list_dict['svis_ipv6_lst'])
    else :
        if  mul_list_dict['vlan_svi_validation_error_lst'] :
            for error in mul_list_dict['vlan_svi_validation_error_lst'] :
                return  mul_list_dict['vlan_svi_validation_error_lst']
        else :
            return ("complete validation for vlan and svi is done successfully")
    
def vrf_validation(parsed_yaml,debug) :
    """
    validate some error senarios in the yaml file
    Args:
        parsed_yaml: yaml file converted to dict
        debug: for completed output 
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
    for svi in parsed_yaml['svis'].keys() :    
        try :
            if parsed_yaml['svis'][svi]['svi_type'] == "core" and parsed_yaml['svis'][svi]['vrf'] and parsed_yaml['svis'][svi]['ipv6_enable'] == "yes" :
                for vrf in parsed_yaml['vrfs'].keys():   
                    if vrf == parsed_yaml['svis'][svi]['vrf']:
                        try :
                            if parsed_yaml['vrfs'][vrf]['afs']['ipv6'] :
                                mul_list_dict['ipv6_vrf_lst'].append("ipv6 {} under vrf {}".format(parsed_yaml['vrfs'][vrf]['afs']['ipv6'],vrf))
                        except KeyError as e :
                            mul_list_dict['vrf_validation_error_lst'].append("ipv6 parameter present under SVI {} but not present under VRF {}".format(svi,parsed_yaml['svis'][svi]['vrf']))
        
            if mul_list_dict['vrf_validation_error_lst'] :
                pass
            else :   
                for vrf,vrf_data in parsed_yaml['vrfs'].items():
                    try :
                        if vrf in mul_list_dict['svi_vrf_lst'] :
                            if parsed_yaml['vrfs'][vrf]['rd'] and parsed_yaml['vrfs'][vrf]['afs']  :
                                if  parsed_yaml['vrfs'][vrf]['afs']['ipv4']['rt_import']  :
                                    mul_list_dict['vrf_import_lst'].append(parsed_yaml['vrfs'][vrf]['afs']['ipv4']['rt_import'])
                                if  parsed_yaml['vrfs'][vrf]['afs']['ipv4']['rt_export']  :
                                    mul_list_dict['vrf_export_lst'].append(parsed_yaml['vrfs'][vrf]['afs']['ipv4']['rt_export'])
                    except KeyError as e:
                            mul_list_dict['vrf_validation_error_lst'].append("mandatory parameter not found {} under VRF {}".format(e, vrf))
        except :
            try :
                for vrf in parsed_yaml['vrfs'].keys():
                    if vrf == parsed_yaml['svis'][svi]['vrf']:
                        try :
                            if parsed_yaml['vrfs'][vrf]['afs']['ipv6'] :
                                mul_list_dict['vrf_validation_error_lst'].append("ipv6 key not found under svi {}".format(svi,vrf))
                        except :
                            mul_list_dict['ipv6_vrf_lst'].append("ipv6 not found under vrf {} and svi {} which is expected".format(parsed_yaml['svis'][svi]['vrf'],svi)) 
            except KeyError as e : 
                mul_list_dict['vrf_validation_error_lst'].append("mandatory parameter {} not found under SVIS {}".format(e,svi))             
    
    for vrf,vrf_data in parsed_yaml['vrfs'].items():
        try :
            if parsed_yaml['vrfs'][vrf]['rd'] :
                rd_dict[vrf] = vrf_data['rd']
            for key,value in rd_dict.items():
                rd_dup_dict.setdefault(value, set()).add(key)
            key_rd_result = [key for key, values in rd_dup_dict.items()
                  if len(values) > 1]
            value_rd_result = [values for key, values in rd_dup_dict.items()
                  if len(values) > 1]
            if  key_rd_result and value_rd_result :
                mul_list_dict['vrf_validation_error_lst'].append("{} rd is found under vrfs {}".format(key_rd_result,value_rd_result))
        except KeyError as e : 
            mul_list_dict['vrf_validation_error_lst'].append("mandatory parameter {} not found under vrfs {}".format(e,vrf))    
    
    if debug == "verbose" :
        if  mul_list_dict['vrf_validation_error_lst'] :
            for error in mul_list_dict['vrf_validation_error_lst'] :
                return  mul_list_dict['vrf_validation_error_lst']
        else :
            return ("vrf validation is done successfully",mul_list_dict['ipv6_vrf_lst'])
    else :
        if  mul_list_dict['vrf_validation_error_lst'] :
            for error in mul_list_dict['vrf_validation_error_lst'] :
                return  mul_list_dict['vrf_validation_error_lst']
        else :
            return ("vrf validation is done successfully")
        
    
def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        fileName=dict(type='str', required=True),
        debug=dict(type='str', required=True)
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    result = {}
                
    
    with open(module.params['fileName'], 'r') as f:
        parsed_yaml=yaml.safe_load(f)

    result['yaml_precheck']= (yaml_error_validation(parsed_yaml = parsed_yaml,debug = module.params['debug']),vlan_svi_validation(parsed_yaml = parsed_yaml,debug = module.params['debug']),vrf_validation(parsed_yaml = parsed_yaml,debug = module.params['debug']))       
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
