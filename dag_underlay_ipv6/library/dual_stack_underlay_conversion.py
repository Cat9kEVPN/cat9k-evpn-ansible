#check the nve vxlan encapsulation type as dual_stack or ipv6

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.module_utils.basic import AnsibleModule

import re
import pprint as pp
from genie.utils import Dq
from genie.conf.base import Device
from genie.testbed import load
import yaml, json
import collections
from ansible.module_utils.basic import AnsibleModule

nve_dict = collections.defaultdict(list)

# Get the nve vxlan_encapsulatin type and return if type is dual_stack or ipv6 else returns key error
def nve_vxlan_encap(parsed_nve_output) :
  for nve in parsed_nve_output['nve_interfaces'].keys() :
    try :
      if parsed_nve_output['nve_interfaces'][nve]['vxlan_encapsulation']['encapsulation_type'] == 'dual-stack' :
          encap_type = parsed_nve_output['nve_interfaces'][nve]['vxlan_encapsulation']['encapsulation_type']
          return (
            {'type': encap_type, 'msg': "Conversion of overlay fabric from dual_stack is successful "}
          )

      elif parsed_nve_output['nve_interfaces'][nve]['vxlan_encapsulation']['encapsulation_type'] == 'ipv6' :
          return (
            {'type': 'not dual-stack', 'msg': "Conversion unsuccessful as overlay fabric is in ipv6 mode. please convert the fabric to dual-stack for downgrading "}
          )
    except KeyError as e :
      return (
            {'type': 'not dual-stack', 'msg': "Overlay Fabric is not in dual-stack mode for downgrading "}
          )

# Get the ipv4 and ipv6 address from loopback in nve and returns if type as dual_stack else returns key error
def underlay_conversion_check(overlay_db_output:dict , sec_int_output:dict) :
  for loopback_int in overlay_db_output['nve_interfaces'].values() :
    try :
      if (sec_int_output['interfaces'][loopback_int['source_interface']]['ipv4']) and (sec_int_output['interfaces'][loopback_int['source_interface']]['ipv6']) and (sec_int_output['interfaces'][loopback_int['source_interface']]['ip_ospf']) and (sec_int_output['interfaces'][loopback_int['source_interface']]['ipv6_ospf']) :
        return (
              {'type': 'dual-stack', 'msg': "Conversion of underlay fabric from dual_stack to ipv4 is successful "}
            )
    except KeyError as e :
      return (
            {'type': 'not dual-stack', 'msg': "underlay Fabric is not in dual-stack mode for downgrading to ipv4"}
          )

# Get the ipv4 , ipv6 address and ip ospf and ipv6 ospf from loopback in nve and returns type as dual_stack else returns key error
def underlay_conversion_check_ipv6(parsed_nve_output , overlay_db_output:dict , sec_int_output:dict) :
  for nve_int,loopback_int in overlay_db_output['nve_interfaces'].items() :
    try :
      if (sec_int_output['interfaces'][loopback_int['source_interface']]['ipv4']) and (sec_int_output['interfaces'][loopback_int['source_interface']]['ipv6']) and (sec_int_output['interfaces'][loopback_int['source_interface']]['ip_ospf']) and (sec_int_output['interfaces'][loopback_int['source_interface']]['ipv6_ospf']) :
        if parsed_nve_output['nve_interfaces'][nve_int]['vxlan_encapsulation']['encapsulation_type'] == 'ipv6' :
          return (
                {'type': 'dual-stack', 'msg': "Conversion of underlay fabric from dual_stack to ipv6 is successful "}
              )
    except KeyError as e :
      return (
            {'type': 'not dual-stack', 'msg': "underlay Fabric is not in dual-stack mode for downgrading to ipv6"}
          )
            
    
def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        nve_output=dict(required=False,type='dict'),
        overlay_db_output=dict(required=False,type='dict'),
        sec_int_output=dict(required=False,type='list'),      
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    
    result = {}  
    
    if module.params['nve_output']:
      parsed_nve_output = module.params['nve_output']
         
      result['nve_output'] = nve_vxlan_encap(parsed_nve_output = parsed_nve_output)
    
    if module.params['overlay_db_output'] and module.params['sec_int_output'] :
    
      show_run_sec_int = '\n'.join(module.params['sec_int_output'])
    
      device = Device("Switch", os="iosxe")
      device.custom.abstraction = {'order':["os"]}
      
      parsed_sec_int_output = device.parse('show run | sec ^int', output=show_run_sec_int)
       
      result['nve_output'] = underlay_conversion_check(overlay_db_output= module.params['overlay_db_output'],sec_int_output = parsed_sec_int_output )

    if module.params['nve_output'] and module.params['overlay_db_output'] and module.params['sec_int_output'] :
    
      show_run_sec_int = '\n'.join(module.params['sec_int_output'])
    
      device = Device("Switch", os="iosxe")
      device.custom.abstraction = {'order':["os"]}
      
      parsed_nve_output = module.params['nve_output']
      parsed_sec_int_output = device.parse('show run | sec ^int', output=show_run_sec_int)
       
      result['nve_output'] = underlay_conversion_check_ipv6(parsed_nve_output = parsed_nve_output,overlay_db_output= module.params['overlay_db_output'],sec_int_output = parsed_sec_int_output )
    
    
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
