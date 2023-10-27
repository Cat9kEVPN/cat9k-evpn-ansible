# validate the vlans,svis,vrfs and overlay_interfaces and configures if not present in the host

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: overlay_inc_preprocess

short_description: This module contains functions used in preprocessing group_vars/create_vars.yml, for overlay incremental playbook
'''

def compare(create_vars, overlay_db_vars, hostvars_vars, parsed_output):

    vrf_dict = {}
    vlan_dict = {}
    svi_dict = {}
    access_inft_dict = {} 
    overlay_intf_dict = {}

    if 'dag' in create_vars:
        dags = create_vars['dag']
    elif 'l3vni' in create_vars:
        dags = create_vars['l3vni']
    else:
        dags = {}

    if dags:
        for dag in dags:
            vrf_present = parsed_output.get('vrf', {})
            if dag == "all" :
                vrf_dict = {k:v for k, v in overlay_db_vars['vrfs'].items() \
                            if k not in vrf_present}
            else:
                vrf_dict = {k:v for k, v in overlay_db_vars['vrfs'].items() \
                            if (k not in vrf_present and k in dags)}

        overlay_intf = hostvars_vars.get('overlay_interfaces', {})
        if overlay_intf:
            overlay_intf_present = parsed_output.get('overlay_interfaces', {})

            overlay_intf_dict = { k:v for k, v in overlay_intf.items() \
                                 if v['vrf'] in vrf_dict and k not in overlay_intf_present}

        svis_all = overlay_db_vars.get('svis', {})
        if svis_all:
            svis_have = parsed_output.get('svis', {})
            svi_dict = {k:v for k, v in svis_all.items() \
                        if v['vrf'] in vrf_dict and k not in svis_have}

    vlans_all = overlay_db_vars.get('vlans', {})
    if create_vars.get('vlans'):
        vlans_all = {k:v for k, v in vlans_all.items() \
                     if int(k) in create_vars['vlans']}
        
    if vlans_all:
        vlans_have = parsed_output.get('vlans', {})
        vlan_dict = {k:v for k, v in vlans_all.items() \
                     if k not in vlans_have}
        access_inft_dict = [k for k, v in vlan_dict.items() \
                            if v['vlan_type'] == 'access']
 
    vars_dict =  {
        'vrfs': vrf_dict, 
        'vlans': vlan_dict, 
        'svis': svi_dict, 
        'access_side_vlans': access_inft_dict, 
        'overlay_interfaces': overlay_intf_dict
    }

    vars_dict = {k:v for k, v in vars_dict.items() if v}

    return vars_dict
    
  
def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            create_vars=dict(required=True,type='dict'),
            overlay_db_vars=dict(required=True,type='dict'),
            hostvars_vars=dict(required=True,type='dict'),
            sh_run_parsed=dict(required=True,type='dict'),
    ),
        supports_check_mode=True
    )   

    result = compare(
      module.params['create_vars'],
      module.params['overlay_db_vars'],
      module.params['hostvars_vars'],
      module.params['sh_run_parsed']
    )
    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
