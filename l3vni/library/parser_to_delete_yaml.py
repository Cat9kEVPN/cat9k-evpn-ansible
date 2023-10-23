# Get the DAG related informations from 'show run nve' and 'show run | section ^interface' parsed CLI output 
# 'show run nve' - VRFs, VLANs, SVIs, NVE interface
# 'show run | section ^interface' - access interfaces

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

from genie.utils import Dq
from genie.conf.base import Device
import yaml, json

DOCUMENTATION = r'''
---
module: parser_to_delete_yaml

short_description: Get the DAG related informations from 
                   'show run nve', 'show run | section ^interface' parsed CLI output
                   and add them to the dictionary
'''

import json

def add_action_to_keys(value_to_del, dict_block, block, parsed_output=None):

    value_to_del = list(map(str, value_to_del))    # values from yml: int -> str 

    ret_dict = {}

    for key in value_to_del:
        
        if key in dict_block:
 
            if block == 'vlans':
                ret_dict[key] = dict_block[key].copy()
                vni_type = 'l2vni' if 'evi' in dict_block[key] else 'l3vni'
                ret_dict[key].update(parsed_output['vni'][vni_type][dict_block[key]['vni']])
                ret_dict[key].update({'action':'delete'})
            else:
                ret_dict[key] = {'action':'delete'}
            
    return ret_dict

def access_intf_block(value_to_del, interface_parsed):
    
    filtered_intf_parsed = \
        {intf:interface_parsed[intf] for intf in interface_parsed if 'switchport_mode' in interface_parsed[intf]}
    ret_dict = {}
    
    for intf in filtered_intf_parsed:
        if filtered_intf_parsed[intf]['switchport_mode'] == 'trunk':
            intf_mode = filtered_intf_parsed[intf]['switchport_mode'] + 's'
            key_switch = 'switchport_'+filtered_intf_parsed[intf]['switchport_mode']+'_vlans'
        else:
            intf_mode = filtered_intf_parsed[intf]['switchport_mode']
            key_switch = 'switchport_'+filtered_intf_parsed[intf]['switchport_mode']+'_vlan'
    
        if key_switch in filtered_intf_parsed[intf]:
            vlan_raw_list = filtered_intf_parsed[intf][key_switch].split(',')
            vlan_list = []
            
            for vlan_raw in vlan_raw_list:
                if '-' in vlan_raw:
                    vlan_rg = vlan_raw.split('-')
                    vlan_expded = [str(i_intf) for i_intf in range(int(vlan_rg[0]), int(vlan_rg[1])+1)]
                    vlan_list = vlan_list + vlan_expded
                else:
                   vlan_list.append(vlan_raw)
                   
            vlan_intf = list(set(vlan_list).intersection(value_to_del))
        
            if vlan_intf:
                ret_dict.setdefault(intf_mode,{}).setdefault(intf,{})
                ret_dict[intf_mode][intf]['action'] = 'delete'
                ret_dict[intf_mode][intf]['vlans'] = vlan_intf  
            
    return ret_dict

def overl_intf_block(ovrl_intf_list, vrf_list):
    
    ret_dict = {}
    
    for ol_intf in ovrl_intf_list:
        try:
            if ovrl_intf_list[ol_intf]['vrf'] in vrf_list:
                ret_dict[ol_intf] = {}
                ret_dict[ol_intf]['action'] = 'delete'
                ret_dict[ol_intf]['vrf'] = ovrl_intf_list[ol_intf]['vrf']
        except KeyError:
            pass
            
    return ret_dict

def delete_action(parsed_output, interface_parsed, toDel):

    if 'vlans' in toDel:
        toDel['vlans'] = list(map(str, toDel['vlans']))
    else:
        toDel['vlans'] = []
            
    if 'dag' in toDel:
        toDel['svis'] = []
        
        if 'all' in toDel['dag']:
            toDel['dag'] = list(parsed_output['vrf'].keys())
            
        toDel['vrf'] = toDel['dag'].copy()

        # to collect DAG vlans
        if 'all' not in toDel['vlans']:
            for dag in toDel['dag']:
                if dag in parsed_output['vrf']:
                    try:
                        for svi in parsed_output['svis']: 
                            if 'vrf' in parsed_output['svis'][svi] \
                                and parsed_output['svis'][svi]['vrf'] == dag:
                                toDel['vlans'].append(svi)
                    except KeyError:
                        pass

        toDel['vlans'] = list(dict.fromkeys(toDel['vlans']))
        
    if toDel['vlans'][0] == 'all':
        toDel['vlans'] = list(parsed_output['vlans'].keys())
            
    toDel['svis']  = toDel['vlans'].copy()
        
    toDel_filter = [i for i in toDel if i in ['vlans', 'svis', 'vrf']]
    filtered_op = {key:val for key, val in parsed_output.items() if key in toDel_filter}
    
    delete_op = json.loads(json.dumps(filtered_op))
    
    if 'update_access' not in toDel: toDel['update_access'] = False
    if 'update_overlay_intf' not in toDel: toDel['update_overlay_intf'] = False

    ret_dict = {}
                
    for ele in toDel_filter:
        
        if ele in delete_op:
            if ele == 'vlans':
                nve_number = list((parsed_output['nve_interfaces']).keys())
                delete_op[ele] = add_action_to_keys(value_to_del=toDel[ele], dict_block=delete_op[ele], \
                                                    block=ele, parsed_output=parsed_output['nve_interfaces'][nve_number[0]])
                if toDel['update_access']:
                    delete_op['access_interfaces'] = access_intf_block(value_to_del=toDel['vlans'], \
                                                                       interface_parsed = interface_parsed['interfaces'])            
            else:
               delete_op[ele] = add_action_to_keys(value_to_del=toDel[ele], dict_block=delete_op[ele], block=ele)

    if 'vrf' in delete_op:

        if 'overlay_interfaces' in parsed_output:
            if toDel['update_overlay_intf']:
                delete_op['overlay_interfaces'] = overl_intf_block(parsed_output['overlay_interfaces'], delete_op['vrf'])
      
        # key vrf to vrfs
        delete_op['vrfs'] = delete_op['vrf'].copy()
        del delete_op['vrf']

    for ele in delete_op:
        if delete_op[ele]: ret_dict[ele] = delete_op[ele]

    if 'vlans' in ret_dict:
        # create nve intf key and loop through nve number to add source interface info
        ret_dict['nve_interfaces'] = {}
        
        for i in parsed_output['nve_interfaces']:        
            ret_dict['nve_interfaces'][i] = {'source_interface':parsed_output['nve_interfaces'][i]['source_interface']}
     
    return yaml.dump(json.loads(json.dumps(ret_dict)), sort_keys=True, default_flow_style=False)


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            hostvars=dict(required=True,type='dict'),
            toDel=dict(required=True,type='dict')
    ),
        supports_check_mode=True
    )   

    result = {}

    hostvars = module.params['hostvars']

    run_nve = '\n'.join(hostvars['run_nve'])
    
    device = Device("Switch", os="iosxe")
    device.custom.abstraction = {'order':["os"]}
    nve_parsed = device.parse('show run nve', output=run_nve)

    intf_parsed = ''
    
    if 'intf_sec' in hostvars:
        intf_sec = '\n'.join(hostvars['intf_sec'])
        intf_parsed = device.parse('show run | section ^interface', output=intf_sec)

    result['yaml'] = delete_action(nve_parsed, intf_parsed, module.params['toDel'])

    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
