# Generate the Auth_type for access_interfaces if auth_type is present

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

import re
from genie.utils import Dq
from genie.conf.base import Device
import yaml, json
import collections

collect_dict_lst = collections.defaultdict(list)

DOCUMENTATION = r'''
---
module: auth_configs

short_description: This module is used for deleting the Auth_type for access_interfaces if auth_type is present in host_vars/access_intf folder,else it will take from the auth_db.yml by taking diff from the leaf configs and return the modified dictionary
'''

auth_dict = {}


def auth_configs_generate(userinput:dict,access_input:dict,parsed_sec_output:dict)->dict:
    if 'access' in access_input['access_interfaces'] :
      for access_intf in access_input['access_interfaces']['access'] :
          if isinstance(access_intf,dict) :
            for keys,values in access_intf.items():
              if 'auth_type' in values and 'source_template' in parsed_sec_output['interfaces'][keys]:
                auth_dict[keys] = values['auth_type']
              elif 'leaf_auth_type' in access_input and 'source_template' in parsed_sec_output['interfaces'][keys] :
                auth_dict[keys] = access_input['leaf_auth_type']
              elif 'site_level_fabric_auth_type' in userinput and 'source_template' in parsed_sec_output['interfaces'][keys] :
                auth_dict[keys] = userinput['site_level_fabric_auth_type']
    
    yml_dict_output =  {'auth_type' : auth_dict  }
    
    yml_dict = {}
    
    for keys,values in yml_dict_output.items() :
        if values != {} :
            yml_dict[keys] = values
        
    compare_op = json.loads(json.dumps(yml_dict))

    return yaml.dump(json.loads(json.dumps(compare_op)), sort_keys=True, default_flow_style=False)
    
  
def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            userinput=dict(required=False,type='dict'),
            access_input=dict(required=False,type='dict'),
            sec_output=dict(required=False,type='list'),    
    ),
        supports_check_mode=True
    )   

    result = {}
    
    show_run_int = '\n'.join(module.params['sec_output'])
    
    device = Device("Switch", os="iosxe")
    device.custom.abstraction = {'order':["os"]}
    
    parsed_sec_output = device.parse('show run | sec ^int', output=show_run_int)

    result['yaml'] = auth_configs_generate(module.params['userinput'],module.params['access_input'],parsed_sec_output)
    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
