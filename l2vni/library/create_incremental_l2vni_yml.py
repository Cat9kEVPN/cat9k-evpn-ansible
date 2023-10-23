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

short_description: This module is used for getting the incremental values by taking the input from the user and comparing with all.yml,hostvars/        <inventory>.yml,host_vars/access_intf,'show run nve','show run | sec ^int' configurations and return the modified dictionary 
'''

def compare(userinput:dict,parsed_output:dict,parsed_sec_output:dict ,access_input:dict , tocompare:dict , overlay_intf:dict)->dict:
  for vlan in userinput['vlans'] :
    if vlan == 'all' :
      for tocompare_vlan in tocompare['vlans'].keys() :
        if tocompare_vlan not in parsed_output['vlans'].keys():
          mul_list_dict['inc_vlans'].append(int(tocompare_vlan))
    else :
      try :
        if str(vlan) in tocompare['vlans'].keys() and str(vlan) not in parsed_output['vlans'].keys() :
          mul_list_dict['inc_vlans'].append(vlan)
      except :
        if str(vlan) in tocompare['vlans'].keys() :
          mul_list_dict['inc_vlans'].append(vlan) 

  for vlan_access in tocompare['vlans'].keys() :
    mul_list_dict['tocompare_vlans'].append(int(vlan_access))
      
  for intf in access_input['access_interfaces']['trunks']:
    if type(intf) != dict : 
      if 'switchport_trunk_vlans' in parsed_sec_output['interfaces'][intf].keys():
        if parsed_sec_output['interfaces'][intf]['switchport_trunk_vlans'] != "none":
          mul_list_dict['sec_output_vlan'].append(parsed_sec_output['interfaces'][intf]['switchport_trunk_vlans'])
              
  if mul_list_dict['sec_output_vlan']:
    for trunk_vlan in mul_list_dict['sec_output_vlan']:
      vlans_lst = trunk_vlan.split(',')

    for vlans_split in vlans_lst:
      if "-" in vlans_split:
        vlans_after_split = vlans_split.split("-")
        for range_svi in range(int(vlans_after_split[0]), int(vlans_after_split[1]) + 1):
          mul_list_dict['range'].append(range_svi)
      else:
          mul_list_dict['range'].append(int(vlans_split))
              
  if mul_list_dict['range']:
    diff = list(set(mul_list_dict['tocompare_vlans']) - set(mul_list_dict['range']))
  else:
    diff = mul_list_dict['tocompare_vlans']

  for access_intf_cli in diff:
    mul_list_dict['access_vlan'].append(int(access_intf_cli))


  yml_dict_output =  {'vlan_cli' : mul_list_dict['inc_vlans'] , 'access_inft_cli' : mul_list_dict['access_vlan'] }
    
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
