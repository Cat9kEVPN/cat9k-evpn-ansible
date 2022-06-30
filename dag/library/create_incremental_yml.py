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

def compare(userinput:dict,parsed_output:dict, tocompare:dict , overlay_intf:dict)->dict:

    for dag in userinput['dag'] :
        try :
          if dag in tocompare['vrfs'].keys() and "vrf" not in parsed_output :
            mul_list_dict['vrf'].append(dag)
          elif dag in tocompare['vrfs'].keys() and dag not in parsed_output['vrf']:
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
    
    for access_vlan in mul_list_dict['vlan_svi'] :
      if tocompare['vlans'][str(access_vlan)]['vlan_type'] == "access" :
        mul_list_dict['access_vlan'].append(int(access_vlan))
    
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
            tocompare=dict(required=False,type='dict'),
            overlay_intf=dict(required=False,type='dict'),
            
    ),
        supports_check_mode=True
    )   

    result = {}

    show_run_nve = '\n'.join(module.params['hostvars'])
    
    device = Device("Switch", os="iosxe")
    device.custom.abstraction = {'order':["os"]}
    parsed_output = device.parse('show run nve', output=show_run_nve)
    

    result['yaml'] = compare(module.params['userinput'],parsed_output, module.params['tocompare'], module.params['overlay_intf'])
    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
