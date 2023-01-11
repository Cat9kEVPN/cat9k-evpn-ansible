# Get the DAG related informations from 'show run nve' and 'show run | section ^interface' parsed CLI output 
# 'show run nve' - VRFs, VLANs, SVIs, NVE interface
# 'show run | section ^interface' - access interfaces

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

import re

DOCUMENTATION = r'''
---
module: sh_run_nve_parse

short_description: Parse 
                  'show run nve CLI output
'''

def showRunningConfigNve(showRunningConfigNveOutput):
    """Parser for show running-config | sec bgp"""

    output = showRunningConfigNveOutput

    if output:
        # l2vpn evpn
        p1_0 = re.compile(r'^l2vpn evpn$')

        # replication-type ingress
        p1_1 = re.compile(r'^replication\-type +(?P<rep_type>ingress|static)$')

        # router-id loopback 0
        p1_2 = re.compile(r'^router\-id +(?P<router_id>.*)$')

        # default-gateway advertise
        p1_3 = re.compile(r'^default-gateway advertise$')

        # logging peer state
        p1_4 = re.compile(r'^logging peer state$')

        # mac duplication limit 20 time 5
        # ip duplication limit 20 time 5
        p1_5 = re.compile(r'^(?P<addr>\w+) duplication limit +(?P<limit_number>\d+) +time (?P<time_limit>\d+)$')

        # route-target auto vni
        p1_6 = re.compile(r'^route\-target auto vni$')

        # l2vpn evpn instance 1 vlan-based
        p1_7 = re.compile(r'^l2vpn evpn instance +(?P<l2vpn_evi>\d+) +vlan-based$')

        # encapsulation vxlan
        p1_8 = re.compile(r'^encapsulation +(?P<encapsulation>\w+)$')

        # default-gateway advertise enable
        p1_9 = re.compile(r'^default\-gateway advertise +(?P<adv_default_gateway>enable|disable)$')

        # ip local-learning enable
        p1_10 = re.compile(r'^ip local\-learning +(?P<learn_ip_addr>enable|disable)$')

        # no auto-route-target
        p1_11 = re.compile(r'^no auto-route\-target$')

        # rd 65000:100
        p1_12 = re.compile(r'^rd +(?P<rd>[\d:]+)$')

        # route-target import 3:201
        # route-target export 1:201
        # route-target both 65000:100
        # route-target export 100:1 stitching
        p1_13 = re.compile(r'^route\-target +(?P<type>import|export|both) +(?P<rt>[\d:]+)(\s+(?P<stitch>stitching))?$')

        # vlan configuration 200
        p2_0 = re.compile(r'^vlan configuration +(?P<vlan_id>\d+)$')

        #   interface nve1
        #   interface GigabitEthernet1/0/30
        #   interface Loopback14
        #   interface Vlan200
        p3_0 = re.compile(r'^interface +(?P<if_name>.*)$')

        #   no ip address
        p3_1 = re.compile(r'^no ip address$')

        #   host-reachability protocol bgp
        p3_2 = re.compile(r'^host-reachability protocol +(?P<host_reachability_protocol>\w+)$')

        #   source-interface loopback1
        p3_3 = re.compile(r'^source\-interface +(?P<source_if>\w+)$')

        #   vxlan encapsulation dual-stack prefer-ipv6 underlay-mcast ipv4
        #   vxlan encapsulation ipv6
        p3_3_1 = re.compile(r'^vxlan encapsulation +(?P<type>dual-stack|ipv6|ipv4)(.*)?$')

        #   member vni 5000 vrf green
        #   member vni 6000 ingress-replication
        #   member vni 10000 mcast-group 227.0.0.1
        #   member evpn-instance 1 vni 6000
        p3_4 = re.compile(r'^member +(evpn\-instance +(?P<evi>\d+) )?vni (?P<vni>[\d\-]+)( +vrf\s+(?P<vrf>\w+))?( +(?P<type>ingress\-replication|mcast\-group\s+(?P<mcast_group>([\d.]+))?(\s+)?(?P<mcast_group_ipv6>[\da-fA-F:]+)?))?$')
        
        # no shutdown
        p3_5 = re.compile(r'^no +shutdown$')

        #   description core svi for l3vni
        #   description access-svi
        p3_6 = re.compile(r'^description +(?P<descr>.+)$')

        #   vrf forwarding green
        p3_7 = re.compile(r'^vrf +forwarding +(?P<vrf_name>.+)$')

        #   ip address 192.168.1.201 255.255.255.0
        #   ip address 192.168.1.202 255.255.255.0 secondary
        p3_8 = re.compile(r'^ip +address +(?P<ipv4>[\d.]+)\s(?P<mask>[\d.]+)(\s+(?P<sec>secondary))?$')

        #   ipv6 address 2001:DB8:201::201/64
        p3_9 = re.compile(r'^ipv6 +address +(?P<ipv6>[\da-fA-F:]+)(?P<mask>/\d+)$')

        #   ipv6 enable
        p3_10 = re.compile(r'^ipv6 +enable$')

        #   mac-address aabb.cc01.f100
        p3_11 = re.compile(r'^mac\-address +(?P<mac>[\da-f.]+)$')

        #   ip unnumbered Loopback0
        p3_12 = re.compile(r'^ip +unnumbered +(?P<if_loopback>.+)$')

        #   no autostate
        p3_13 = re.compile(r'^no +autostate$')

        #   ip pim sparse-mode
        p3_14 = re.compile(r'^ip +pim +sparse\-mode$')

        #   private-vlan mapping 222-224
        #   private-vlan mapping add 303-307,309,440
        p3_15 = re.compile(r'^private\-vlan +mapping *(?P<action>add|remove)? *(?P<vlan_id>[\d\-,]+)$')

        #   ip helper-address 10.1.1.1
        #   ip helper-address global 10.1.1.1
        #   ip helper-address vrf green 10.1.1.1
        p3_16 = re.compile(r'^ip +helper\-address +((?P<reachable_over>(global|vrf \S+)) +)?(?P<ip>[\d.]+)$')

        #   ip dhcp relay source-interface Loopback12
        p3_17 = re.compile(r'^ip +dhcp +relay +source\-interface +(?P<if_name>\S+)$')

        #   router bgp 65535.65535
        p4_0 = re.compile(r'^router +bgp +(?P<asn>[\d.]+)$')

        #   bgp router-id interface Loopback0
        p4_1 = re.compile(r'^bgp +router\-id +interface +(?P<if_name>\S+)$')

        #   bgp log-neighbor-changes
        p4_2 = re.compile(r'^bgp +log\-neighbor\-changes$')

        #   bgp update-delay 240
        p4_3 = re.compile(r'^bgp +update\-delay +(?P<delay_time>\d+)$')

        #   bgp graceful-restart
        p4_4 = re.compile(r'^bgp +graceful\-restart$')

        #   no bgp default ipv4-unicast
        p4_5 = re.compile(r'^no +bgp +default +ipv4\-unicast$')

        #   neighbor 10.11.11.11 remote-as 1
        p4_6 = re.compile(r'^neighbor +(?P<ip>[\d.]+) +remote\-as +(?P<remote_as>[\d.]+)$')

        #   neighbor 10.11.11.11 update-source Loopback0
        p4_7 = re.compile(r'^neighbor +(?P<ip>[\d.]+) +update\-source +(?P<if_name>\S+)$')

        #   address-family l2vpn evpn
        #   address-family ipv4
        #   address-family ipv4 vrf green
        #   address-family ipv4 mvpn
        #   address-family ipv6 mvpn
        p4_8 = re.compile(r'^address\-family +(?P<family_name>l2vpn evpn|ipv4|ipv6|ipv4 mvpn|ipv6 mvpn)(\s+vrf +(?P<vrf_name>\S+))?$')

        #   bgp additional-paths select all
        p4_9 = re.compile(r'^bgp +additional\-paths +select +all$')

        #   bgp additional-paths send
        p4_10 = re.compile(r'^bgp +additional\-paths +(?P<option>send|receive|send receive)$')

        #   neighbor 10.5.5.50 activate
        p4_11 = re.compile(r'^neighbor +(?P<ip>[\d.]+) +activate$')

        #   neighbor 10.5.5.50 send-community both
        p4_12 = re.compile(r'^neighbor +(?P<ip>[\d.]+) +send\-community +(?P<community_attr>both|extended|standard)$')

        #   neighbor 10.5.5.50 additional-paths send
        p4_13 = re.compile(r'^neighbor +(?P<ip>[\d.]+) +additional\-paths +(?P<option>send|receive|send receive)$')

        #   neighbor 10.5.5.50 advertise additional-paths best 2
        #   neighbor 10.5.5.50 advertise additional-paths group-best
        #   neighbor 10.5.5.50 advertise additional-paths all group-best
        p4_14 = re.compile(r'^neighbor +(?P<ip>[\d.]+) +advertise +additional\-paths +(?P<option>.*)$')

        #   advertise l2vpn evpn
        p4_15 = re.compile(r'^advertise +l2vpn +evpn$')

        #   redistribute connected
        p4_16 = re.compile(r'^redistribute +connected$')

        #   redistribute static
        p4_17 = re.compile(r'^redistribute +static$')

        #   maximum-paths 4
        p4_18 = re.compile(r'^maximum\-paths +(?P<max_path>\d+)$')

        #   default-information originate
        p4_19 = re.compile(r'^default\-information +originate$')

        #   vrf definition green
        p5_0 = re.compile(r'^vrf +definition +(?P<vrf_name>\S+)$')

        #   mdt default vxlan 225.2.2.2
        p5_1 = re.compile(r'^mdt +default +vxlan +(?P<group_addr>\S+)$')

        #   mdt auto-discovery vxlan
        #   mdt auto-discovery vxlan inter-as
        p5_2 = re.compile(r'^mdt +auto\-discovery +(?P<option>\S+)(\s+(?P<inter_as>inter\-as))?$')

        #   mdt strict-rpf interface
        p5_3 = re.compile(r'^mdt +strict\-rpf +interface$')

        ret_dict = {}
        bgp_asn = ''
        if_name = ''
        l2vpn = ''
        vlan = ''
        vrf_defn = ''
        svis=''
        overlay = ''
        nve_flag=False
        intf_flag=False
        if_others_dict = {}
        helper_address_idx = 0

        for line in output.splitlines():
            line = line.strip()

            # l2vpn evpn
            m = p1_0.match(line)
            if m:
                vrf_defn = ''       # shares route-target, route distinguisher
                l2vpn = 'evpn'
                l2vpn_global_flag = True    ## flags for replication-type identification
                l2vpn_evi_flag = False
                l2vpn_global_dict = ret_dict.setdefault('l2vpn_global', {})
                continue
            if l2vpn:

                # replication-type ingress
                m = p1_1.match(line)
                if m:
                    group = m.groupdict()
                    if l2vpn_global_flag:
                        l2vpn_global_dict.update({'replication_type': group['rep_type']})
                    elif l2vpn_evi_flag:
                        l2vpn_evi_dict.update({'replication_type': group['rep_type']})
                    continue

                # router-id loopback 0
                # router-id 172.16.255.3
                m = p1_2.match(line)
                if m:
                    l2vpn_global_dict['router_id'] = m.groupdict()['router_id']
                    continue

                # default-gateway advertise
                m = p1_3.match(line)
                if m:
                    l2vpn_global_dict['default_gateway'] = True
                    continue

                # logging peer state
                m = p1_4.match(line)
                if m:
                    l2vpn_global_dict['peer_state_log'] = True
                    continue

                # mac duplication limit 20 time 5
                # ip duplication limit 20 time 5
                m = p1_5.match(line)
                if m:
                    group = m.groupdict()
                    addr_type = group.pop('addr')
                    dupl_limit_dict = l2vpn_global_dict.setdefault(addr_type+'_duplication_limit', {})
                    dupl_limit_dict.update({'limit_number': int(group['limit_number']),'time_limit': int(group['time_limit'])})
                    continue

                # route-target auto vni
                m = p1_6.match(line)
                if m:
                    l2vpn_global_dict.update({'id_auto_rt': 'vni'})
                    continue

                # l2vpn evpn instance 1 vlan-based
                m = p1_7.match(line)
                if m:
                    l2vpn_evi_flag = True
                    l2vpn_global_flag = False         ## flag for replication-type identification
                    group = m.groupdict()
                    l2vpn_evi_dict = ret_dict.setdefault('l2vpn_evi', {}).setdefault(group['l2vpn_evi'], {})
                    l2vpn_evi_dict['type'] = "vlan-based"
                    continue

                # encapsulation vxlan
                m = p1_8.match(line)
                if m:
                    l2vpn_evi_dict.update({'encapsulation': m.groupdict()['encapsulation']})
                    continue

                # default-gateway advertise enable
                m = p1_9.match(line)
                if m:
                    group = m.groupdict()
                    if group['adv_default_gateway'] =='enable':
                        l2vpn_evi_dict.update({'adv_default_gateway': True})
                    elif group['adv_default_gateway'] =='disable':
                        l2vpn_evi_dict.update({'adv_default_gateway': False})
                    continue

                # ip local-learning enable
                m = p1_10.match(line)
                if m:
                    group = m.groupdict()
                    if group['learn_ip_addr'] =='enable':
                        l2vpn_evi_dict.update({'learn_ip_addr': True})
                    elif group['learn_ip_addr'] =='disable':
                        l2vpn_evi_dict.update({'learn_ip_addr': False})
                    continue

                # no auto-route-target
                m = p1_11.match(line)
                if m:
                    l2vpn_evi_dict.update({'autogenerate_route_target': False})
                    continue

            # vlan configuration 200
            m = p2_0.match(line)
            if m:
                if_name=''          # shares member vni
                vlan = m.groupdict()['vlan_id']
                vlan_dict = ret_dict.setdefault('vlans', {}).setdefault(vlan, {})
                continue

            #   interface nve1
            #   interface GigabitEthernet1/0/30
            #   interface Loopback14
            #   interface Vlan200
            m = p3_0.match(line)
            if m:
                overlay = ''        # shares same key field
                vrf_defn = ''       # shares description

                if 'Vlan' in m.groupdict()['if_name']:
                    if_name = ''    # shares same key field
                    nve_flag=False  # nve dont need all the fields of svi
                    helper_address_idx = 0
                    svis = m.groupdict()['if_name'][4:]

                    if svis in ret_dict['vlans']:
                        if 'vni' in ret_dict['vlans'][svis]:
                            svi_dict = ret_dict.setdefault('svis', {}).setdefault(svis, {})

                        if 'evi' in ret_dict['vlans'][svis]:
                            svi_dict['svi_type'] = 'access'
                        else:
                            svi_dict['svi_type'] = 'core'

                    else:
                        svis  =''
                        if_name = m.groupdict().pop('if_name')
                        intf_flag=True
                        if_dict = if_others_dict.setdefault('interfaces', {}).setdefault(if_name, {})

                else:
                    if_name = m.groupdict().pop('if_name')
                    svis = ''           # shares same key field

                    if 'nve' in if_name:
                        nve_flag=True       # shares vni and treated differently
                        intf_flag=False
                        if_dict = ret_dict.setdefault('nve_interfaces', {}).setdefault(if_name[3:], {})
                    else:
                        nve_flag=False
                        intf_flag=True
                        if_dict = if_others_dict.setdefault('interfaces', {}).setdefault(if_name, {})
                continue

            if nve_flag==True:
                #   host-reachability protocol bgp
                m = p3_2.match(line)
                if m:
                    host_reachability_protocol = m.groupdict().pop('host_reachability_protocol')
                    if_dict.update({'host_reachability_protocol': host_reachability_protocol})
                    continue

            if if_name or svis or overlay:
                #   no ip address
                if if_name:
                    current_dict = if_dict
                elif svis:
                    current_dict = svi_dict
                elif overlay:
                    current_dict = overlay_dict

                #   no ip address
                m = p3_1.match(line)
                if m:
                    current_dict.update({'ip_addr_state': 'disabled'})
                    continue

                #   source-interface loopback1
                m = p3_3.match(line)
                if m:
                    current_dict.update({'source_interface': m.groupdict()['source_if']})
                    continue

                #   vxlan encapsulation dual-stack prefer-ipv6 underlay-mcast ipv4
                #   vxlan encapsulation ipv6
                m = p3_3_1.match(line)
                if m:
                    current_dict = current_dict.setdefault('vxlan_encapsulation', {}).setdefault(
                        'encapsulation_type', m.groupdict()['type'])
                    continue

                # no shutdown
                m = p3_5.match(line)
                if m:
                    current_dict['shutdown'] = False
                    continue
                if nve_flag == False:

                    #   vrf forwarding green
                    m = p3_7.match(line)
                    if m:
                        current_dict['vrf'] = m.groupdict()['vrf_name']
                        if if_name:
                            overlay = if_name
                            intf_dict = if_others_dict['interfaces'][if_name]
                            overlay_dict = ret_dict.setdefault('overlay_interfaces', {}).setdefault(if_name, intf_dict)
                            if_others_dict['interfaces'].pop(if_name)
                            if_name = ''    # tranferred from interfaces to overlay_interfaces
                        continue

                    #   ip address 192.168.1.201 255.255.255.0
                    #   ip address 192.168.1.202 255.255.255.0 secondary
                    m = p3_8.match(line)
                    if m:
                        group = m.groupdict()
                        ip_addr = group['ipv4']+group['mask']
                        if group['sec']:
                            current_dict.setdefault('secondary_ip_address', []).append(ip_addr)
                        else:
                            current_dict['ipv4'] = ip_addr
                        continue

                    #   ipv6 address 2001:DB8:201::201/64
                    m = p3_9.match(line)
                    if m:
                        group = m.groupdict()
                        ipv6_addr = group['ipv6']+group['mask']
                        current_dict.setdefault('ipv6', []).append(ipv6_addr)
                        continue

                    #   ipv6 enable
                    m = p3_10.match(line)
                    if m:
                        current_dict['ipv6_enable'] = True
                        continue

                    #   mac-address aabb.cc01.f100
                    m = p3_11.match(line)
                    if m:
                        current_dict['mac_addr'] = m.groupdict()['mac']
                        continue

                    #   ip unnumbered Loopback0
                    m = p3_12.match(line)
                    if m:
                        current_dict['unnumbered_interface'] = m.groupdict()['if_loopback']
                        continue

                    #   no autostate
                    m = p3_13.match(line)
                    if m:
                        current_dict['autostate'] = False
                        continue

                    #   ip pim sparse-mode
                    m = p3_14.match(line)
                    if m:
                        current_dict['pim_enable'] = True
                        continue

                    #   private-vlan mapping 222-224
                    #   private-vlan mapping add 303-307,309,440
                    m = p3_15.match(line)
                    if m:
                        group = m.groupdict()

                        vlan_id = group.pop('vlan_id')

                        if '-' in vlan_id:
                            vlan_id = vlan_id.split('-')
                            vlan_list = list(range(int(vlan_id[0]), int(vlan_id[1])+1))
                        else:
                            vlan_list = [int(vlan_id)]

                        current_dict['mapped_private_vlan']['vlans'] = vlan_list

                        if group['action']:
                            current_dict['mapped_private_vlan']['action'] = group['action']
                        continue

            if svis:

                #   ip helper-address 10.1.1.1
                #   ip helper-address global 10.1.1.1
                #   ip helper-address vrf green 10.1.1.1
                m = p3_16.match(line)
                if m:
                    helper_address_idx +=1
                    group = m.groupdict()

                    svi_dict.setdefault('helper_address', {}).setdefault(helper_address_idx, {}).setdefault('ip_address', group['ip'])

                    if group['reachable_over']:
                        svi_dict.setdefault('helper_address', {}).setdefault(helper_address_idx, {}).setdefault('reachable_over', group['reachable_over'])
                    continue

                #   ip dhcp relay source-interface Loopback12
                m = p3_17.match(line)
                if m:
                    svi_dict['dhcp_relay_source'] = m.groupdict()['if_name']
                    continue


            if vlan or if_name:

                #   member vni 5000 vrf green
                #   member vni 6000 ingress-replication
                #   member vni 10000 mcast-group 227.0.0.1
                #   member evpn-instance 1 vni 6000
                m = p3_4.match(line)
                if m:
                    group = m.groupdict()
                    vni = group.pop('vni')

                    if if_name:
                        if nve_flag:
                            if group['vrf']:
                                current_dict = if_dict.setdefault('vni', {}).setdefault('l3vni', {}).setdefault(vni, {})
                            else:
                                current_dict = if_dict.setdefault('vni', {}).setdefault('l2vni', {}).setdefault(vni, {})
                        elif intf_flag:
                            current_dict = if_dict.setdefault('vni', {}).setdefault(vni, {})
                    elif vlan:
                        current_dict = vlan_dict
                        if group['evi']:
                            current_dict.update({'evi': group['evi']})
                            current_dict.update({'vlan_type': 'access'})
                        else:
                            current_dict.update({'vlan_type': 'core'})  # vni is must field in this regex

                        current_dict.update({'vni': vni})

                    if group['vrf']:
                        current_dict.update({'vrf': group['vrf']})

                    if group['type']:
                        repl_type = group['type'].split(' ')
                        if repl_type[0] == 'mcast-group':
                            current_dict.update({'replication_type': 'static'})
                            if group['mcast_group']:
                                current_dict.update({'replication_mcast': group['mcast_group']})
                            if group['mcast_group_ipv6']:
                                current_dict.update({'replication_mcast_ipv6': group['mcast_group_ipv6']})
                        elif repl_type[0] == 'ingress-replication':
                            current_dict.update({'replication_type': repl_type[0]})
                    continue

            #   router bgp 65535.65535
            m = p4_0.match(line)
            if m:
                vrf_defn = ''       # Shares adress family
                bgp_asn = m.groupdict().pop('asn')
                bgp_dict = ret_dict.setdefault('bgp', {}).setdefault(bgp_asn, {})
                bgp_dict.update({'as_number': bgp_asn})
                continue

            if bgp_asn:
                #   bgp router-id interface Loopback0
                m = p4_1.match(line)
                if m:
                    bgp_dict.update({'router_id': m.groupdict()['if_name']})
                    continue

                #   bgp log-neighbor-changes
                m = p4_2.match(line)
                if m:
                    bgp_dict.update({'log_neighbor_change': True})
                    continue

                #   bgp update-delay 240
                m = p4_3.match(line)
                if m:
                    bgp_dict.update({'max_update_delay': m.groupdict()['delay_time']})
                    continue

                #   bgp graceful-restart
                m = p4_4.match(line)
                if m:
                    bgp_dict.update({'graceful_restart': True})
                    continue

                #   no bgp default ipv4-unicast
                m = p4_5.match(line)
                if m:
                    bgp_dict.update({'ipv4_unicast_state': False})
                    continue

                #   neighbor 10.11.11.11 remote-as 1
                m = p4_6.match(line)
                if m:
                    group = m.groupdict()
                    neighbor_dict = bgp_dict.setdefault('neighbors', {}).setdefault(group['ip'], {})
                    neighbor_dict['peer_as_number'] = group['remote_as']
                    continue

                #   neighbor 10.11.11.11 update-source Loopback0
                m = p4_7.match(line)
                if m:
                    neighbor_dict['bgp_update_source'] = m.groupdict()['if_name']
                    continue

                #   bgp additional-paths select all
                m = p4_9.match(line)
                if m:
                    af_dict.update({'select_additional_paths': True})
                    continue
                #   bgp additional-paths send receive
                m = p4_10.match(line)
                if m:
                    af_dict['addr_family_additional_paths'] = m.groupdict()['option']
                    continue

                #   neighbor 10.5.5.50 activate
                m = p4_11.match(line)
                if m:
                    neighbor = m.groupdict()['ip']
                    address_family_neighbor_dict = af_dict.setdefault('address_family_neighbor', {}).setdefault(neighbor, {})
                    continue

                #   neighbor 10.5.5.50 send-community both
                m = p4_12.match(line)
                if m:
                    address_family_neighbor_dict['community_attr_to_send'] = m.groupdict()['community_attr']
                    continue

                #   neighbor 10.5.5.50 additional-paths send
                m = p4_13.match(line)
                if m:
                    address_family_neighbor_dict['additional_paths'] = m.groupdict()['option']
                    continue

                #   neighbor 10.5.5.50 advertise additional-paths best 3
                #   neighbor 10.5.5.50 advertise additional-paths group-best
                #   neighbor 10.5.5.50 advertise additional-paths all group-best
                m = p4_14.match(line)
                if m:
                    address_family_neighbor_dict['advertise_additional_paths'] = m.groupdict()['option']
                    continue

                #   advertise l2vpn evpn
                m = p4_15.match(line)
                if m:
                    af_dict['advertise_l2vpn_evpn'] = True
                    continue

                #   redistribute connected
                m = p4_16.match(line)
                if m:
                    af_dict.update({'redistribute_connected': True})
                    continue

                #   redistribute static
                m = p4_17.match(line)
                if m:
                    af_dict.update({'redistribute_static': True})
                    continue

                #   maximum-paths 4
                m = p4_18.match(line)
                if m:
                    af_dict.update({'max_path': m.groupdict()['max_path']})
                    continue

                # default-information originate
                m = p4_19.match(line)
                if m:
                    af_dict.update({'default_info_originate': True})
                    continue

            #   vrf definition green
            m = p5_0.match(line)
            if m:
                bgp_asn = ''        # Shares adress family
                l2vpn = ''          # Shares route-target, rd
                if_name = ''        # Shares description
                svis = ''           # Shares description
                vrf_defn = m.groupdict()['vrf_name']
                vrf_dict = ret_dict.setdefault('vrf', {}).setdefault(vrf_defn, {})
                continue

            if vrf_defn:
                #  mdt default vxlan 225.2.2.2
                m = p5_1.match(line)
                if m:
                    af_dict['mdt_default_vxlan'] = m.groupdict()['group_addr']
                    continue

                #  mdt auto-discovery vxlan
                #  mdt auto-discovery vxlan inter-as
                m = p5_2.match(line)
                if m:
                    group = m.groupdict()
                    af_dict['mdt_auto_discovery'] = group['option']
                    if group['inter_as']:
                        af_dict['bgp_inter_as'] = True
                    continue

                #   mdt strict-rpf interface
                m = p5_3.match(line)
                if m:
                    af_dict['strict_rpf_check'] = True
                    continue

            if bgp_asn or vrf_defn:
                #   address-family l2vpn evpn
                #   address-family ipv4
                #   address-family ipv4 vrf green
                #   address-family ipv4 mvpn
                #   address-family ipv6 mvpn
                m = p4_8.match(line)
                if m:
                    group = m.groupdict()
                    af = group['family_name']
                    if bgp_asn:
                        current_dict = bgp_dict
                    elif vrf_defn:
                        current_dict = vrf_dict

                    if group['vrf_name']:
                        af_dict = current_dict.setdefault('address_family', {}).setdefault(af+ ' ' + group['vrf_name'], {})
                    else:
                        af_dict = current_dict.setdefault('address_family', {}).setdefault(af, {})
                    continue

            if if_name or vrf_defn or svis:
                #   description core svi for l3vni
                #   description access-svi
                m = p3_6.match(line)
                if m:
                    if if_name:
                        if_dict['name'] = m.groupdict()['descr']
                    else:
                        if vrf_defn:
                            current_dict = vrf_dict
                        elif svis:
                            current_dict = svi_dict
                        current_dict['description'] = m.groupdict()['descr']
                    continue

            if l2vpn or vrf_defn:
                # rd 65000:100
                m = p1_12.match(line)
                if m:
                    if l2vpn:
                        current_dict = l2vpn_evi_dict
                    elif vrf_defn:
                        current_dict = vrf_dict

                    current_dict.update({'route_distinguisher': m.groupdict()['rd']})
                    continue
                # route-target import 3:201
                # route-target export 1:201
                # route-target both 65000:100
                # route-target export 100:1 stitching
                m = p1_13.match(line)
                if m:
                    if l2vpn:
                        current_dict = l2vpn_evi_dict
                    elif vrf_defn:
                        current_dict = af_dict

                    group = m.groupdict()

                    if group['stitch']:
                        value = group['rt']+' stitching'
                    else:
                        value = group['rt']
                    current_dict.setdefault('route_target'+'_'+group['type'], []).append(value)
                    continue

        return ret_dict

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            command_output=dict(required=True,type='str')
    ),
        supports_check_mode=True
    )   

    result = {}

    command_output = module.params['command_output']

    result['parsed'] = showRunningConfigNve(command_output)

    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
