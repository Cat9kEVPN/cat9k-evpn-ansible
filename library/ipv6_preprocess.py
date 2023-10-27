# validate the vlans,svis,vrfs and overlay_interfaces and configures if not present in the host

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: ipv6_preprocess_yml

short_description: This module is used for preprocessing group_vars/ipv6_create_vars.yml(/ipv6_delete_vars.yml) for IPv6 related playbooks
'''

def compare(userinput, parsed_output, overlay_db, leaf_data, playbook_mode):

    ret_dict = {}
    vrfs_dict = {}
    svis_dict = {}

    dev_vrf = parsed_output['vrf']

    svi_type_dict = {
        'core': 'ipv6_enable',
        'access': 'ipv6',
    }
    rt_key_dict = {
        'route_target_import': 'rt_import',
        'route_target_export': 'rt_export',
    }

    if 'dag' in userinput:
        dags = userinput['dag']
    elif 'dag' in userinput:
        dags = userinput['l3vni']

    if 'all' in dags:
        vrf_list = overlay_db['vrfs'].keys()
    else:
        vrf_list = dev_vrf

    if playbook_mode == 'del':
        for vrf in vrf_list:
            try:
                ipv6_dict = dev_vrf[vrf]['address_family']['ipv6']
            except KeyError:
                ipv6_dict = {}
                pass
            if ipv6_dict:
                ipv6_dict['action'] = 'delete'
                vrfs_dict[vrf] = {'afs': {'ipv6': ipv6_dict}}

        for svi in parsed_output['svis']:
            svi_dict = parsed_output['svis'][svi]
            if svi_dict['vrf'] in vrf_list:
                svi_key = svi_type_dict[svi_dict['svi_type']]
                if svi_type_dict[svi_dict['svi_type']] in svi_dict:
                    svis_dict[int(svi)] = {svi_key: svi_dict[svi_key]}

    elif playbook_mode == 'inc':
        for vrf in vrf_list :
            try:
                db_af_dict = overlay_db['vrfs'][vrf]['afs']
                if 'ipv6' in db_af_dict and 'ipv6' not in dev_vrf[vrf]['address_family']:
                    vrfs_dict[vrf] = {'afs': {'ipv6': db_af_dict['ipv6']}}
            except KeyError:
                pass

        for svi in overlay_db['svis']:
            svi_dict = overlay_db['svis'][svi]
            if svi_dict['vrf'] in vrf_list:
                svi_key = svi_type_dict[svi_dict['svi_type']]
                if svi_key in svi_dict and svi_key not in parsed_output['svis'][svi]:
                    svis_dict[int(svi)] = {svi_key: svi_dict[svi_key]}    

    if vrfs_dict:  
        ret_dict =  {
            'vrfs' : vrfs_dict, 
            'bgp' : {'as_number': int(leaf_data['bgp']['as_number'])} , 
            'svis' : svis_dict
        }

    return ret_dict
    

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            hostvars=dict(required=True,type='dict'),
            overlay_db=dict(required=True,type='dict'),
            userinput=dict(required=True,type='dict'),
            leaf_data=dict(required=True,type='dict'),
            playbook_mode=dict(required=True,type='str'),
            
    ),
        supports_check_mode=True
    )   

    result = compare(
        module.params['userinput'], 
        module.params['hostvars'], 
        module.params['overlay_db'], 
        module.params['leaf_data'],
        module.params['playbook_mode']
    )   
    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
