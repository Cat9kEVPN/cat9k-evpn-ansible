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
yml_dict = {}
vrfs_dict = {}
svis_dict = {}

def compare(userinput:dict,parsed_output:dict, overlay_db:dict, leaf_data:dict )->dict:
  for vrf in userinput['dag'] :
    if vrf == "all" :
      for overlay_db_vrf in overlay_db['vrfs'].keys() :
        if 'ipv6' not in parsed_output['vrf'][overlay_db_vrf]['address_family'].keys() :
          mul_list_dict['dag'].append(overlay_db_vrf)
    else :
      if 'ipv6' not in parsed_output['vrf'][vrf]['address_family'].keys() :
        mul_list_dict['dag'].append(vrf)
      
  for vrf in mul_list_dict['dag'] :
    if vrf in overlay_db['vrfs'].keys() :     
      if 'ipv6' in overlay_db['vrfs'][vrf]['afs'].keys() and 'ipv6' in parsed_output['vrf'][vrf]['address_family'].keys():
        pass
      elif 'ipv6' in overlay_db['vrfs'][vrf]['afs'].keys() and 'ipv6' not in parsed_output['vrf'][vrf]['address_family'].keys() :
        vrfs_dict[vrf] = {'afs' : {'ipv6' : overlay_db['vrfs'][vrf]['afs']['ipv6']}}
          
  for svis in overlay_db['svis'] :
    if overlay_db['svis'][svis]['vrf'] in mul_list_dict['dag'] :
      if overlay_db['svis'][svis]['vrf'] in mul_list_dict['dag'] and overlay_db['svis'][svis]['svi_type'] == "access" :
        if 'ipv6' in overlay_db['svis'][svis].keys() and "ipv6" not in  parsed_output['svis'][svis].keys() :
          svis_dict[int(svis)] = {'ipv6' : overlay_db['svis'][svis]['ipv6']}
      if overlay_db['svis'][svis]['vrf'] in mul_list_dict['dag'] and overlay_db['svis'][svis]['svi_type'] == "core" :
        if 'ipv6_enable' in overlay_db['svis'][svis].keys() and "ipv6_enable" not in  parsed_output['svis'][svis].keys() :
          svis_dict[int(svis)] = {'ipv6_enable' : overlay_db['svis'][svis]['ipv6_enable']}     
         
  if vrfs_dict and svis_dict :  
    yml_dict =  {'ipv6_action': 'add' ,'ipv6_routing' : 'yes' , 'vrfs' : vrfs_dict, 'bgp' : {'as_number' : int(leaf_data['bgp']['as_number'])} , 'svis' : svis_dict }
  else :
    yml_dict = {}
    
  
  compare_op = json.loads(json.dumps(yml_dict))
  
  return yaml.dump(json.loads(json.dumps(compare_op)), sort_keys=True, default_flow_style=False)
    

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            hostvars=dict(required=False,type='list'),
            overlay_db=dict(required=False,type='dict'),
            userinput=dict(required=False,type='dict'),
            leaf_data=dict(required=False,type='dict'),
            
    ),
        supports_check_mode=True
    )   

    result = {}

    show_run_nve = '\n'.join(module.params['hostvars'])
    
    device = Device("Switch", os="iosxe")
    device.custom.abstraction = {'order':["os"]}
    parsed_output = device.parse('show run nve', output=show_run_nve)
    

    result['yaml'] = compare(module.params['userinput'],parsed_output, module.params['overlay_db'], module.params['leaf_data'])
    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
