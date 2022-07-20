# validate the vlans,svis,vrfs and overlay_interfaces and configures if not present in the host

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

import re
from genie.utils import Dq
from genie.conf.base import Device
import yaml, json
import collections

mul_list_dict = collections.defaultdict(list)

DOCUMENTATION = r'''
---
module: create_incremental_yml

short_description: This module is used for getting the extra values  by comparing all.yml and show run nve parser  
                   configurations and return the modified dictionary
'''

def compare(userinput:dict,parsed_output:dict,parsed_sec_output:dict ,access_input:dict , tocompare:dict , overlay_intf:dict)->dict:

    for dag in userinput['dag'] :
        try :
          if dag in tocompare['vrfs'].keys() and "vrf" not in parsed_output :
            mul_list_dict['vrf'].append(dag)
          elif dag in tocompare['vrfs'].keys() :
            mul_list_dict['vrf'].append(dag)
        except :
            pass
    
    for overlay_inft in overlay_intf['overlay_interfaces'] :
        try :
            if (overlay_intf['overlay_interfaces'][overlay_inft]['vrf'] in mul_list_dict['vrf'] and overlay_inft not in parsed_output['overlay_interfaces'].keys()) :
                mul_list_dict['overlay_inft'].append(str(overlay_inft))
        except :
            mul_list_dict['overlay_inft'].append(str(overlay_inft))
    
    if "svis" in parsed_output :
        filtered_svis = list( set(tocompare['svis'].keys()) - set(parsed_output['svis'].keys()) )
    else :
        filtered_svis = list( set(tocompare['svis'].keys()))

    for svi in filtered_svis :
      if tocompare['svis'][svi]['vrf'] in mul_list_dict['vrf'] :
        mul_list_dict['vlan_svi'].append(int(svi))
    
    for svi in tocompare['svis'] :
      if tocompare['svis'][svi]['svi_type'] == "access" and tocompare['svis'][svi]['vrf'] in mul_list_dict['vrf'] :
        mul_list_dict['tocompare_vlan'].append(svi)
    for intf in access_input['access_interfaces']['trunks']:
      if 'switchport_trunk_vlans' in parsed_sec_output['interfaces'][intf].keys() :
        if parsed_sec_output['interfaces'][intf]['switchport_trunk_vlans'] != "none" :
          mul_list_dict['sec_output_vlan'].append(parsed_sec_output['interfaces'][intf]['switchport_trunk_vlans'])
    
    if mul_list_dict['sec_output_vlan'] :
      for trunk_vlan in mul_list_dict['sec_output_vlan'] :
        diff = list(set(mul_list_dict['tocompare_vlan']) - set(trunk_vlan.split(',')))
    else :
      diff = list(set(mul_list_dict['tocompare_vlan']) - set(mul_list_dict['sec_output_vlan']))  
    
    for access_vlan in diff :
      mul_list_dict['access_vlan'].append(int(access_vlan)) 
            
    
    for dag in mul_list_dict['vrf'] :
      if mul_list_dict['vlan_svi'] :
        pass
      else :
        mul_list_dict['vrf'].clear() 
    
    yml_dict_output =  {'vrf_cli' : mul_list_dict['vrf'] , 'vlan_cli' : mul_list_dict['vlan_svi'] , 'svi_cli' : mul_list_dict['vlan_svi'] , 'access_inft_cli' : mul_list_dict['access_vlan'] , 'ovrl_intf_cli' : mul_list_dict['overlay_inft']  }
    
    yml_dict = {}
    
    for keys,values in yml_dict_output.items() :
        if values != [] :
            yml_dict[keys] = values
        
    compare_op = json.loads(json.dumps(yml_dict))

    return yaml.dump(json.loads(json.dumps(compare_op)), sort_keys=True, default_flow_style=False)

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            userinput=dict(required=False,type='dict'),
            hostvars=dict(required=False,type='list'),
            access_input=dict(required=False,type='dict'),
            sec_output=dict(required=False,type='list'),
            tocompare=dict(required=False,type='dict'),
            overlay_intf=dict(required=False,type='dict'),
            
    ),
        supports_check_mode=True
    )   

    result = {}

    show_run_nve = '\n'.join(module.params['hostvars'])
    show_run_int = '\n'.join(module.params['sec_output'])
    
    device = Device("Switch", os="iosxe")
    device.custom.abstraction = {'order':["os"]}
    parsed_output = device.parse('show run nve', output=show_run_nve)
    parsed_sec_output = device.parse('show run | sec ^int', output=show_run_int)
    

    result['yaml'] = compare(module.params['userinput'],parsed_output,parsed_sec_output,module.params['access_input'], module.params['tocompare'], module.params['overlay_intf'])
    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
