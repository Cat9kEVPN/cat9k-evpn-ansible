#check the version,license and loopback ip reachability

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.module_utils.basic import AnsibleModule

import re
import yaml
import ipaddress
import collections

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
        parsed_output_version = parsed_output['version']['version_short']
        version = parsed_output_version.split('.')
        str1 = "{} version is compatible and license is {} which is expected"
        str2 = "version {} is compatable but the license {} is Incompatable"

        try:
            license_level = parsed_output["version"]["license_package"]["network-advantage"]['license_level']
        except KeyError:
            license_level = ''
        
        if int(version[0]) > int(17) :
            if license_level == "network-advantage" :
                return (str1.format(parsed_output["version"]["version"],license_level))
            else :
                return (str2.format(parsed_output["version"]["version"],license_level))
        elif int(version[1]) >= int(3) :
            if license_level == "network-advantage" :
                return (str1.format(parsed_output["version"]["version"],license_level))
            else :
                return (str2.format(parsed_output["version"]["version"],license_level))
        else :
            return ("{} version is Incompatible".format(parsed_output["version"]["version"]))
    except Exception as e :
        return ("Failed due to {}".format(e))

def ping_output(host_name, ping_output):
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

    failed_connection = []

    for leaf_item in ping_output:
        if "stdout" in leaf_item:
            if 'Success rate is 100 percent' not in leaf_item["stdout"]:
                failed_connection.append(leaf_item['item'])

    if failed_connection:
        for dev in failed_connection:
            result = mul_list_dict['final_result'].append(
                "Device {} is not reachable from {}".format(dev, host_name)
            )
        return mul_list_dict['final_result']
    else:
        return ("All devices are reachable")
    
def run_module():

    module_args = dict(
        sh_ver_parsed=dict(required=True,type='dict'),
        overlay_db_vars=dict(required=True, type='dict'),
        loopback=dict(required=False,type='dict'),
        ping_output=dict(required=False,type='list'),
        host_name=dict(required=False,type='str'), 
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    
    result = {'checks': {}}

    result['checks']['version_license_check'] = version_license_check(
        module.params['sh_ver_parsed']
    )
    result['checks']['ping_output'] = ping_output(
        module.params['host_name'],
        module.params['ping_output']
    )
    
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
