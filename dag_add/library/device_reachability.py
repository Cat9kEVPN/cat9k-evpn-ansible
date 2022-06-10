#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.module_utils.basic import AnsibleModule

import re
import pprint as pp
from genie.utils import Dq
from genie.conf.base import Device
from genie.testbed import load
import yaml, json
import ipaddress
import collections
from ansible.module_utils.basic import AnsibleModule

mul_list_dict = collections.defaultdict(list)

def version_license_check(parsed_output) :
    """
    check version > 17.3 and license is network-advantage 
    Args:
        parsed_output: yaml file converted to dict
    Returns:
        string : "version is compatable or not :
    Raises:
        exception failed due to 
    """

    try :
        if float(parsed_output["version"]["version"][:4]) >= float(17.3) :
            if parsed_output["version"]["license_package"]["network-advantage"]['license_level'] == "network-advantage" :
                return ("{} version is compatible  and license is {} which is expected".format(parsed_output["version"]["version"],parsed_output["version"]["license_package"]["network-advantage"]['license_level']))
            else :
                return ("version {} is compatable but the license {} is Incompatable".format(parsed_output["version"]["version"],parsed_output["version"]["license_package"]["network-advantage"]['license_level']))
        else :
            return ("{} version is Incompatible".format(parsed_output["version"]["version"]))
    except Exception as e :
        return ("Failed due to {}".format(e))
        
def loopback_check(parsed_yaml):
    """
    check loopback is present in the yaml file nve_interfaces
    Args:
        parsed_yaml: yaml file converted to dict
    Returns:
        string : loopback_ip
    Raises:
        KeyError if key not found 
    """
    try :
        for nve_loopback in parsed_yaml['nve_interfaces'].values() :
            loopback = nve_loopback['source_interface']
            
        return loopback
    except KeyError as e :
        return ("failed due to {}".format(e))
    
def loopback_config_check(parsed_loopback) :
    """
    check loopback is configured in the vtep or not
    Args:
        parsed_loopback: loopback ip converted to dict
    Returns:
        string : loopback ip is configured 
    Raises:
        KeyError if key not found 
    """
    try :
        pattren = re.findall(r'((?:[0-9]{1,3}\.){3}[0-9]{1,3})',str(parsed_loopback))
        if pattren :
            return pattren
        else :
            return ("loopback ip is not configured in the vtep")
    except Exception as e :
        return ("failed due to {}".format(e))

def ping_output(host_name,ping_output,loopback_config_check):
    """
    ping check to device itself and neighbors 
    Args:
        host_name: device host_name 
        ping_output: output from the device ping for itself and neighbours
        loopback_config_check: loopback ip configured in the device
    Returns:
        string : loopback ip is reachable or not 
    Raises:
        KeyError if key not found 
    """
    try :
        regex_pattren = re.findall(r'((?:[0-9]{1,3}\.){3}[0-9]{1,3}).\s+timeout\s+is\s+\d+\s+seconds:\\n!!!!!\\nSuccess\s+rate\s+is\s+100|[1-9][0-9]?\s+percent',str(ping_output))
        if regex_pattren :
            for loopback in regex_pattren :
                mul_list_dict['loopback'].append(loopback)
        for loopback_ping in loopback_config_check :
            mul_list_dict['loopback_config_check'].append(loopback_ping)
        set_diff = set(mul_list_dict['loopback_config_check']).difference(set(mul_list_dict['loopback']))
        if set_diff :
            for loopback_ip in set_diff :
                result = mul_list_dict['final_result'].append("loopback {} is not reachable from {}".format(loopback_ip,host_name))
            return mul_list_dict['final_result']
        else :
            return ("All loopbacks are reachable from all the nodes")
    except Exception as e :
        return ("failed due to {}".format(e))
            
    
def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        version=dict(required=True,type='list'),
        fileName=dict(type='str', required=True),
        loopback=dict(required=False,type='dict'),
        ping_output=dict(required=False,type='dict'),
        host_name=dict(type='str', required=False),
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    
    result = {}
    
    show_version = '\n'.join(module.params['version'])
    
    device = Device("Switch", os="iosxe")
    device.custom.abstraction = {'order':["os"]}
    
    parsed_output = device.parse("show version", output=show_version)
    
    
    with open(module.params['fileName'], 'r') as f:
        parsed_yaml=yaml.safe_load(f)
        
    result['version_license_check'] = version_license_check(parsed_output = parsed_output)
    result['yaml_loopback_check'] = loopback_check(parsed_yaml = parsed_yaml)
    result['loopback_ip']= loopback_config_check(parsed_loopback=module.params['loopback'])
    result['ping_output']= ping_output(host_name = module.params['host_name'],ping_output=module.params['ping_output'],loopback_config_check=loopback_config_check(parsed_loopback=module.params['loopback']))
    
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()