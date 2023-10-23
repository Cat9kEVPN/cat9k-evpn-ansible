# Get the DAG related informations from 'show run nve' and 'show run | section ^interface' parsed CLI output 
# 'show run nve' - VRFs, VLANs, SVIs, NVE interface
# 'show run | section ^interface' - access interfaces

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: overlay_delete_preprocess

short_description: Get the DAG related informations from 
                   'show run nve', 'show run | section ^interface' parsed CLI output
                   and add them to the dictionary
'''

import json

def add_action_to_dict(value_to_del, device_op, block, nve_output=None):

    value_to_del = list(map(str, value_to_del))    # values from yml: int -> str 

    ret_dict = {}

    for key in value_to_del:
        if key in device_op:
            if block == 'vlans':
                ret_dict[key] = device_op[key].copy()
                vni_type = 'l2vni' if 'evi' in device_op[key] else 'l3vni'
                ret_dict[key].update(nve_output['vni'][vni_type][device_op[key]['vni']])
                ret_dict[key].update({'action':'delete'})
            else:
                ret_dict[key] = {'action':'delete'}
            
    return ret_dict

def get_access_inf_vlans(value_to_del, interface_parsed):
    
    ret_dict = {}
    
    for intf in interface_parsed:
        try:
            sw_mode = interface_parsed[intf]['switchport_mode']
        except KeyError:
            sw_mode = ''
            pass

        if sw_mode:
            if sw_mode == 'trunk':
                intf_mode = sw_mode + 's'
                key_switch = 'switchport_' + sw_mode + '_vlans'
            elif sw_mode == 'access':
                intf_mode = sw_mode
                key_switch = 'switchport_' + sw_mode + '_vlan'

            if key_switch in interface_parsed[intf]:
                vlan_raw_list = interface_parsed[intf][key_switch].split(',')
                vlan_list = []

                for vlan_raw in vlan_raw_list:
                    if '-' in vlan_raw:
                        vlan_rg = vlan_raw.split('-')
                        vlan_expded = [
                            str(i_intf) for i_intf in range(int(vlan_rg[0]), int(vlan_rg[1])+1)
                        ]
                        vlan_list = vlan_list + vlan_expded
                    else:
                       vlan_list.append(vlan_raw)

                vlan_intf = list(set(vlan_list).intersection(value_to_del))

                if vlan_intf:
                    ret_dict.setdefault(intf_mode,{}).setdefault(intf,{})
                    ret_dict[intf_mode][intf] = {
                        'action': 'delete',
                        'vlans': vlan_intf
                    } 
            
    return ret_dict

def get_overlay_intf_vrf(ovrl_intf_list, vrf_list):
    
    ret_dict = {}
    
    for ol_intf in ovrl_intf_list:
        vrf = ovrl_intf_list[ol_intf].get('vrf')
        if vrf in vrf_list:
            ret_dict[ol_intf] = {
                'action': 'delete',
                'vrf': vrf
            }

    return ret_dict

def get_delete_dict(parsed_output, interface_parsed, to_del):

    ret_dict = {}

    to_del = {k:v for k,v in to_del.items() if k in ['vlans', 'svis', 'dag', 'l3vni', 'update_overlay_intf', 'update_access_intf']}

    if 'vlans' in to_del:
        to_del['vlans'] = list(map(str, to_del['vlans']))
    else:
        to_del['vlans'] = []
            
    if 'dag' in to_del:
        dags = to_del['dag']
    elif 'l3vni' in to_del:
        dags = to_del['l3vni']
    
    if dags:
        to_del['svis'] = []
        
        if 'all' in dags:
            dags = list(parsed_output['vrf'])
        else:
            dags = [
                k for k in dags if k in parsed_output['vrf']
            ]
            
        to_del['vrf'] = dags.copy()

        # to collect DAG vlans
        if 'all' not in to_del['vlans']:
            for dag in dags:
                svi_dict = parsed_output.get('svis', {})
                for sk, sv in svi_dict.items(): 
                    if sv.get('vrf') == dag:
                        to_del['vlans'].append(sk)
        
    if 'all' in to_del['vlans']:
        to_del['vlans'] = list(parsed_output['vlans'])
            
    to_del['svis']  = to_del['vlans'].copy()

    parsed_output = json.loads(json.dumps(parsed_output))
       
    for ele in to_del:
        if ele in parsed_output:
            if ele == 'vlans':
                nve_dict = parsed_output['nve_interfaces']
                ret_val = add_action_to_dict(
                    value_to_del=to_del[ele], 
                    device_op=parsed_output[ele],
                    block=ele, 
                    nve_output=list(nve_dict.values())[0]
                )
                if ret_val:
                    ret_dict[ele] = ret_val
                    if to_del.get('update_access_intf', True):
                        ret_dict['access_interfaces'] = get_access_inf_vlans(
                            value_to_del=to_del['vlans'],
                            interface_parsed = interface_parsed.get('interfaces',{})
                        )
                    ret_dict['nve_interfaces'] = {
                        list(nve_dict.keys())[0]:{
                            'action': 'delete_vlans'
                        }
                    }           
            else: 
                ret_val = add_action_to_dict(
                    value_to_del=to_del[ele], 
                    device_op=parsed_output[ele], 
                    block=ele
                )

                if ele == 'vrf':
                    if to_del.get('update_overlay_intf', True):
                        ret_dict['overlay_interfaces'] = get_overlay_intf_vrf(
                            parsed_output.get('overlay_interfaces', {}), 
                            ret_val
                        )                        
                    ele = 'vrfs' # vrf to vrfs
                if ret_val:
                    ret_dict[ele] = ret_val

    return ret_dict

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            device_vars=dict(required=True,type='dict'),
            to_del=dict(required=True,type='dict')
    ),
        supports_check_mode=True
    )   

    device_vars = module.params['device_vars']

    result = get_delete_dict(
        device_vars['run_nve'], 
        device_vars.get('intf_sec', {}), 
        module.params['to_del']
    )

    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
