#Validate overlay_db.yml for any errors

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.module_utils.basic import AnsibleModule

import re
import yaml, json
import collections

mul_list_dict = collections.defaultdict(list)
vni_dup_dict = {}
vni_dict = {}
evi_dict = {}
evi_dup_dict = {}

def yaml_error_validation(parsed_yaml):
  """
  validate some error senarios in the yaml file
  Args:
      parsed_yaml: yaml file converted to dict
  Returns:
      string : "validation for vni and evi under vlans is done successfully"
  Raises:
      KeyError if key not founds
  Error_senarios :
      vni duplication,evi duplication
  """
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
    if key_vni_result and value_vni_result :
      mul_list_dict['yaml_error_validation_lst'].append("Failed due to {} VNI found under VLANS {}".format(key_vni_result,value_vni_result))
  except  KeyError as e :
    mul_list_dict['yaml_error_validation_lst'].append("mandatory parameter {} not found under vlan {}".format(e,vlan))  
      

  try :
    for vlan,vlan_data in parsed_yaml['vlans'].items():
      if parsed_yaml['vlans'][vlan]['evi'] :
        evi_dict[vlan] = vlan_data['evi']
    for key,value in evi_dict.items():
      evi_dup_dict.setdefault(value, set()).add(key)
    key_evi_result = [key for key, values in evi_dup_dict.items()
      if len(values) > 1]
    value_evi_result = [values for key, values in evi_dup_dict.items()
      if len(values) > 1]
    if key_evi_result and value_evi_result :
      mul_list_dict['yaml_error_validation_lst'].append("Failed due to {} EVI found under VLANS {}".format(key_evi_result,value_evi_result))
  except  KeyError as e :
    mul_list_dict['yaml_error_validation_lst'].append("mandatory parameter {} not found under vlan {}".format(e,vlan))  
      
  if mul_list_dict['yaml_error_validation_lst'] :
    return mul_list_dict['yaml_error_validation_lst']
  else :
    return ("validation for 'vni' and 'evi' under vlans is done successfully")

     
def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        fileName=dict(type='str', required=True)
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    result = {}
                
    
    with open(module.params['fileName'], 'r') as f:
        parsed_yaml=yaml.safe_load(f)

    result['yaml_precheck']= (yaml_error_validation(parsed_yaml = parsed_yaml))       
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
