# validate the vlans,svis,vrfs and overlay_interfaces and configures if not present in the host

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: overlay_inc_preprocess

short_description: This module is used for getting the extra values  by comparing all.yml and show run nve parser  
                   configurations and return the modified dictionary
'''

def compare(userinput, parsed_output, tocompare, overlay_intf):

    vrf_dict = {}
    vlan_dict = {}
    svi_dict = {}
    access_inft_dict = {} 
    overlay_intf_dict = {}

    if 'dag' in userinput:
        dags = userinput.get['dag']
    elif 'l3vni' in userinput:
        dags = userinput.get['l3vni']
    else:
        dags = {}

    for dag in dags:
        vrf_present = parsed_output.get('vrf', {})
        if dag == "all" :
            vrf_dict = {key:value for key, value in tocompare['vrfs'].items() \
                        if key not in vrf_present}
        else:
            vrf_dict = {key:value for key, value in tocompare['vrfs'].items() \
                        if key not in vrf_present and key in dag}

    overlay_intf = overlay_intf.get('overlay_interfaces', {})
    if overlay_intf:
        overlay_intf_present = parsed_output.get('overlay_interfaces', {})

        overlay_intf_dict = { key:value for key, value in overlay_intf.items() \
                             if value['vrf'] in vrf_dict and key not in overlay_intf_present}
    
    svis_all = tocompare.get('svis', {})
    if svis_all:
        svis_have = parsed_output.get('svis', {})
        svi_dict = {key:value for key, value in svis_all.items() \
                    if value['vrf'] in vrf_dict and key not in svis_have}
    
    vlans_all = tocompare.get('vlans', {})
    if userinput.get('vlans'):
        vlans_all = {key:value for key, value in vlans_all.items() \
                     if int(key) in userinput['vlans']}
        
    if vlans_all:
        vlans_have = parsed_output.get('vlans', {})
        vlan_dict = {key:value for key, value in vlans_all.items() \
                     if key not in vlans_have}
        access_inft_dict = [key for key, value in vlan_dict.items() \
                            if value['vlan_type'] == 'access']
        
    yml_dict =  {
        'vrfs': vrf_dict, 
        'vlans': vlan_dict, 
        'svis': svi_dict, 
        'access_interfaces': access_inft_dict, 
        'overlay_interfaces': overlay_intf_dict
    }

    return yml_dict
    
  
def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            userinput=dict(required=False,type='dict'),
            hostvars=dict(required=False,type='dict'),
            tocompare=dict(required=False,type='dict'),
            overlay_intf=dict(required=False,type='dict'),
            
    ),
        supports_check_mode=True
    )   

    result = compare(
      module.params['userinput'],
      module.params['hostvars'],
      module.params['tocompare'],
      module.params['overlay_intf']
    )
    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
