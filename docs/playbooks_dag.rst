Playbooks description
*********************

In this section every playbook function will be described. Playbooks for DAG provisioning are stored in ``cat9k-evpn-ansible/dag``

.. code-block::

    ~/cat9k-evpn-ansible/dag$ ls | grep playbook

    playbook_access_add_commit.yml
    playbook_access_add_preview.yml
    playbook_access_incremental_commit.yml
    playbook_access_incremental_preview.yml
    playbook_cleanup.yml
    playbook_output.yml
    playbook_overlay_commit.yml
    playbook_overlay_delete_commit.yml
    playbook_overlay_delete_generate.yml
    playbook_overlay_delete_preview.yml
    playbook_overlay_incremental_commit.yml
    playbook_overlay_incremental_generate.yml
    playbook_overlay_incremental_preview.yml
    playbook_overlay_precheck.yml
    playbook_overlay_preview.yml
    playbook_underlay_commit.yml
    playbook_underlay_preview.yml
    playbook_yml_validation.yml

Underlay provisioning
=====================

playbook_underlay_preview.yml
-----------------------------

This playbook is generating config in text format for underlay for preview.

.. warning::

    No config will be pushed to the remote devices!

Files will be stored in ``preview_files/<hostname>-underlay.txt`` files.

.. code-block::

    ansible-playbook -i inventory.yml playbook_underlay_preview.yml 

Output files could be found in ``preview_files`` directory.

.. code-block::

    ~/cat9k-evpn-ansible/dag/preview_files$ ls | grep underlay
    
    Leaf-01-underlay.txt
    Leaf-02-underlay.txt
    Spine-01-underlay.txt
    Spine-02-underlay.txt

Configuration output will be similar to the next output:

.. code-block::

    ! hostname block 
    hostname Leaf-01

    ! global routing block 
    ip routing
    ipv6 unicast-routing
    ip multicast-routing

    ! underlay interface block 
    interface  Loopback0
    ip address 172.16.255.3 255.255.255.255
    no shut
    interface  Loopback1
    ip address 172.16.254.3 255.255.255.255
    no shut
    interface  GigabitEthernet1/0/1
    no switchport
    ip address 172.16.13.3 255.255.255.0
    no shut
    interface  GigabitEthernet1/0/2
    no switchport
    ip address 172.16.23.3 255.255.255.0
    no shut

    <...snip...>

playbook_underlay_commit.yml
-----------------------------

This playbook is generating config in text format for underlay provisioning which will be pushed to the remote devices.

.. code-block::

    ansible-playbook -i inventory.yml playbook_underlay_commit.yml 

For checking the configuration that is deployed by Ansible on the switch next configuration could be used:

.. code-block::

    conf t
    archive
     log config
      logging enable
      notify syslog contenttype plaintext
    end
    term mon

Overlay provisioning
====================

playbook_yml_validation.yml
---------------------------

This playbook will check ``group_vars/overlay_db.yaml`` for possible issues.

.. code-block::

    ansible-playbook -i inventory.yml playbook_yml_validation.yml

In case of issues it will be highlighed in the playbook output.

Below you can find few examples.

Example 1
^^^^^^^^^

IPv6 present under SVI's but not present under vrf

.. code-block:: yaml

  vrfs:
    green:
      ipv6_unicast: 'enable'
      description: 'green VRF definition'
      rd: '1:1'
      afs:
        ipv4:
          rt_import:
            - '1:1'
            - '1:1 stitching'
          rt_export: 
            - '1:1'
            - '1:1 stitching'
    
  <...snip...>

  svis:
    101:
      svi_type: 'access'
      vrf: 'green'
      ipv4: '10.1.101.1 255.255.255.0'
      ipv6:
        - '2001:101::1/64'
      mac: 'dead.beef.abcd'
    102:
     svi_type: 'access'
     vrf: 'green'
     ipv4: '10.1.102.1 255.255.255.0'
     ipv6:
       - '2001:102::1/64'
     mac: 'dead.beef.abcd'
    901:
     svi_type: 'core'
     vrf: 'green'
     src_intf: 'Loopback1'
     ipv6_enable: 'yes'

  <...snip...>


Playbook output:

.. code-block::

		"yaml_precheck": [
				"partial validation for vlan and svi is done successfully",
				"complete validation for vlan and svi is done successfully",
				[
					"ipv6 parameter present under SVI 101 but not present under VRF green",
					"ipv6 parameter present under SVI 102 but not present under VRF green",
					"ipv6 parameter present under SVI 901 but not present under VRF green"
				]
			]
		}

Example 2
^^^^^^^^^

Mandatory parameter ``ipv4`` is not found under vrf.

.. code-block:: yaml

  vrfs:
    blue:
      rd: '2:2'
        afs:
          #ipv4:
          #  rt_import: 
          #    - '2:2'
          #    - '2:2 stitching'
          #  rt_export: 
          #    - '2:2'
          #    - '2:2 stitching'
          ipv6:
            rt_import: 
              - '2:2'
              - '2:2 stitching'
            rt_export: 
              - '2:2'
              - '2:2 stitching'  

  <...snip...>

Playbook output:

.. code-block::

    "yaml_precheck": [
            "partial validation for vlan and svi is done successfully",
            "complete validation for vlan and svi is done successfully",
            [
            "mandatory parameter not found 'ipv4' under VRF blue"
            ]
        ]
    }

Example 3
^^^^^^^^^

Mandatory parameter ``rd`` is missed under vrf configuration

.. code-block:: yaml

  vrfs:
    green:
      ipv6_unicast: 'enable'
      description: 'green VRF defn'
      #rd: '1:1'

  <...snip...>

Playbook output:

.. code-block::

		"yaml_precheck": [
				"partial validation for vlan and svi is done successfully",
				"complete validation for vlan and svi is done successfully",
				[
					"mandatory parameter 'rd' not found under vrfs green"
				]
			]
		}

Example 4
^^^^^^^^^

Mandatory parameters ``rt_import`` and ``rt_export`` are not found under ipv4 section for VRFs :green:`green` and :blue:`blue`

.. code-block:: yaml

  vrfs:
    green:
      ipv6_unicast: 'enable'
      description: 'green VRF defn'
      rd: '1:1'
      afs:
        ipv4:
          #rt_import: 
          # - '1:1'
          # - '1:1 stitching'
          rt_export: 
            - '1:1'
            - '1:1 stitching' 
        ipv6:
          rt_import:
            - '1:1'
            - '1:1 stitching'
          rt_export:
            - '1:1'
            - '1:1 stitching' 
    blue:
      rd: '2:2'
      afs:
        ipv4:
          rt_import: 
            - '2:2'
            - '2:2 stitching'
          #rt_export: 
          # - '2:2'
          # - '2:2 stitching'
        ipv6:
          rt_import: 
            - '2:2'
            - '2:2 stitching'
          rt_export: 
            - '2:2'

  <...snip...>

Playbook output:

.. code-block::

		"yaml_precheck": [
				"partial validation for vlan and svi is done successfully",
				"complete validation for vlan and svi is done successfully",
				[
					"mandatory parameter not found 'rt_import' under VRF green",
					"mandatory parameter not found 'rt_export' under VRF blue"
				]
			]
		}

Example 5
^^^^^^^^^

Mandatory parameters ``evi``, ``vni`` are missed under ``vlans`` section and for VLAN102 parameter ``replication_mcast`` is present for 
``replication_type: 'ingress'`` which is not expected.

.. code-block:: yaml

  vlans:
  #vrf green vlans
    101:
      vlan_type: 'access'
      description: 'Access_VLAN_101'
      #vni: '10101'
      #evi: '101'
      type: 'vlan-based'
      encapsulation: 'vxlan'
      replication_type: 'static'
      replication_mcast: '225.0.0.101'
   
    102:
      vlan_type: 'access'
      description: 'Access_VLAN_102'
      vni: '10102'
      evi: '102'
      type: 'vlan-based'
      encapsulation: 'vxlan'
      replication_type: 'ingress'
      replication_mcast: '225.0.0.102'
  
  <...snip...>

Playbook output:

.. code-block::

		"yaml_precheck": [
				[
					"mandatory parameter 'vni' not found under vlan 101",
					"mandatory parameter 'evi' not found under vlan 101"
				],
				[
					"replication_mcast ip is present of VLAN 102 for replication_type ingress is not expected "
				],
				"vrf validation is done successfully"
			]
		}

playbook_overlay_precheck.yml
-----------------------------

This playbook will check  **IOS-XE version** and **license level** for compatibility with EVPN feature on Cat9k.

Also VTEP reachibility will be checked via ``ping``. ``source_interface`` from ``nve`` interface per each Leaf will be taken for ping test.

List of checks which are performed:

* checks the version in the leafs which is ``greater that 17.3`` and the license is ``network-advantage``

.. code-block::

		Leaf-01#show version
		Cisco IOS XE Software, Version 17.06.03
		Cisco IOS Software [Bengaluru], Catalyst L3 Switch Software (CAT9K_IOSXE), Version 17.6.3, RELEASE SOFTWARE (fc4)
		Technical Support: http://www.cisco.com/techsupport
		Copyright (c) 1986-2022 by Cisco Systems, Inc.
		Compiled Wed 30-Mar-22 23:09 by mcpre

		Technology Package License Information:

		------------------------------------------------------------------------------
		Technology-package                                     Technology-package
		Current                        Type                       Next reboot
		------------------------------------------------------------------------------
		network-advantage       Smart License                    network-advantage
		None                    Subscription Smart License       None
		AIR License Level: AIR DNA Advantage
		Next reload AIR license Level: AIR DNA Advantage


* checks whether the Loopback is configured on the leafs under nve interface are reachable from the neighboring leafs devices

.. code-block::

		interface Loopback1
		 description NVE Loopback
		 ip address 172.16.254.3 255.255.255.255
		 ip pim sparse-mode
		 ip ospf 1 area 0
		end

* checks the Loopback ip is reachable or not by pinging neighboring loopback ip's and its own loopback ip

.. code-block::

		Leaf-01#show run interface loopback 1
		Building configuration...

		Current configuration : 132 bytes
		!
		interface Loopback1
		 description NVE Loopback
		 ip address 172.16.254.3 255.255.255.255
		 ip pim sparse-mode
		 ip ospf 1 area 0
		end

		Leaf-01#ping 172.16.254.4
		Type escape sequence to abort.
		Sending 5, 100-byte ICMP Echos to 172.16.254.4, timeout is 2 seconds:
		!!!!!
		Success rate is 100 percent (5/5), round-trip min/avg/max = 204/219/227 ms
    
		Leaf-01#ping 172.16.254.3
		Type escape sequence to abort.
		Sending 5, 100-byte ICMP Echos to 172.16.254.3, timeout is 2 seconds:
		!!!!!
		Success rate is 100 percent (5/5), round-trip min/avg/max = 16/16/17 ms

To run playbook use the below command

.. code-block::

    ansible-playbook -i inventory.yml playbook_overlay_precheck.yml

Successfull result should be similar to next output

.. code-block::

    <...snip...>

    TASK [Print result] **********************************************************************************************************************************
    ok: [Leaf-01] => {
        "msg": "{'version_license_check': '17.6.3 version is compatible  and license is network-advantage which is expected', 'yaml_loopback_check': 'Loopback1', 'loopback_ip': ['172.16.254.3', '172.16.254.4'], 'ping_output': 'All loopbacks are reachable from all the nodes', 'failed': False, 'changed': False}'"
    }
    ok: [Leaf-02] => {
        "msg": "{'version_license_check': '17.6.3 version is compatible  and license is network-advantage which is expected', 'yaml_loopback_check': 'Loopback1', 'loopback_ip': ['172.16.254.3', '172.16.254.4'], 'ping_output': 'All loopbacks are reachable from all the nodes', 'failed': False, 'changed': False}'"
    }

    PLAY RECAP *******************************************************************************************************************************************
    Leaf-01                    : ok=10   changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
    Leaf-02                    : ok=10   changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   

    <...snip...>

playbook_overlay_preview.yml
----------------------------

This playbook is generating config in text format for overlay for preview.

.. warning::

    No config will be pushed to the remote devices!

Files will be stored in ``preview_files/<hostname>-overlay.txt`` files.

.. code-block::

    ansible-playbook -i inventory.yml playbook_overlay_preview.yml

Output files could be found in ``preview_files`` directory.

.. code-block::

    ~/cat9k-evpn-ansible/dag/preview_files$ ls | grep overlay
    
    Leaf-01-overlay.txt
    Leaf-02-overlay.txt
    Spine-01-overlay.txt
    Spine-02-overlay.txt

Configuration output will be similar to the next output:

.. code-block::

    ! vrf definition block 
    vrf definition green
    description green VRF defn
    rd 1:1
    address-family ipv4
    route-target import 1:1
    route-target import 1:1 stitching
    route-target export 1:1
    route-target export 1:1 stitching
    address-family ipv6
    route-target import 1:1
    route-target import 1:1 stitching
    route-target export 1:1
    route-target export 1:1 stitching
    vrf definition blue
    rd 2:2
    address-family ipv4
    route-target import 2:2
    route-target import 2:2 stitching
    route-target export 2:2
    route-target export 2:2 stitching
    address-family ipv6
    route-target import 2:2
    route-target import 2:2 stitching
    route-target export 2:2

    ! bgp per vrf block 
    router bgp 65001
    address-family ipv4 vrf green
    advertise l2vpn evpn
    redistribute connected

    <...snip...>

playbook_overlay_commit.yml
-----------------------------

This playbook is generating config in text format for overlay provisioning which will be pushed to the remote devices.

.. code-block::

    ansible-playbook -i inventory.yml playbook_overlay_commit.yml 

For checking the configuration that is deployed by Ansible on the switch next configuration could be used:

.. code-block::

    conf t
    archive
     log config
      logging enable
      notify syslog contenttype plaintext
    end
    term mon

Incremental overlay provisioning
================================

After initial configuration (aka Day0) some incremental changes are need after some time.

For avoiding full reprovisioning of the network incremental update could be used.

New DAG tenant configuration should be added to the file ``group_vars/overlay_db.yml``.

For example, during the inital configuration VRF :green:`green`, VLANs/SVIs :green:`101,102,901` were configured.

.. code-block:: yaml

    vrfs:
      green:
        description: 'green VRF definition'
        rd: '1:1'
        afs:
          ipv4:
            rt_import: 
              - '1:1'
              - '1:1 stitching'
            rt_export: 
              - '1:1'
              - '1:1 stitching'

          ipv6:
            rt_import:
              - '1:1'
              - '1:1 stitching'
            rt_export:
              - '1:1'
              - '1:1 stitching'
 
    vlans:
    #vrf green vlans
     101:
      vlan_type: 'access'
      description: 'Access_VLAN_101'
      vni: '10101'
      evi: '101'
      type: 'vlan-based'
      encapsulation: 'vxlan'
      replication_type: 'static'
      replication_mcast: '225.0.0.101'
    
     102:
      vlan_type: 'access'
      description: 'Access_VLAN_102'
      vni: '10102'
      evi: '102'
      type: 'vlan-based'
      encapsulation: 'vxlan'
      replication_type: 'ingress'
    
     901:
      vlan_type: 'core'
      description: 'Core_VLAN_VRF_green'
      vni: '50901'
      vrf: 'green'

    svis:
    #vrf green svi's
     101:
      svi_type: 'access'
      vrf: 'green'
      ipv4: '10.1.101.1 255.255.255.0'
      ipv6:
        - '2001:101::1/64'
      mac: 'dead.beef.abcd'

     102:
      svi_type: 'access'
      vrf: 'green'
      ipv4: '10.1.102.1 255.255.255.0'
      ipv6:
        - '2001:102::1/64'
      mac: 'dead.beef.abcd'
    
     901:
      svi_type: 'core'
      vrf: 'green'
      src_intf: 'Loopback1'
      ipv6_enable: 'yes'
    
    <...snip...>

Then VRF :blue:`blue` and VLANs/SVIs :blue:`201,202,902` should be provisioned. Respectful config is added for vrf blue and VLANs/SVIs 201,202,902.

.. code-block:: yaml

    vrfs:
    ########################################
    # Day 0 VRF green configuration        #
    ########################################
      green:
        ipv6_unicast: 'enable'
        description: 'green VRF defn'
        rd: '1:1'
        afs:
          ipv4:
            rt_import: 
              - '1:1'
              - '1:1 stitching'
            rt_export: 
              - '1:1'
              - '1:1 stitching'

          ipv6:
            rt_import:
              - '1:1'
              - '1:1 stitching'
            rt_export:
              - '1:1'
              - '1:1 stitching'
    ########################################
    # Day 1 VRF blue configuration         #
    ########################################
      blue:
        rd: '2:2'
        afs:
          ipv4:
            rt_import: 
              - '2:2'
              - '2:2 stitching'
            rt_export: 
              - '2:2'
              - '2:2 stitching'
          ipv6:
            rt_import: 
              - '2:2'
              - '2:2 stitching'
            rt_export: 
              - '2:2'
    
    vlans:
    ###########################################
    # Day 0 VLANs configuration for VRF green #
    ###########################################
     101:
      vlan_type: 'access'
      description: 'Access_VLAN_101'
      vni: '10101'
      evi: '101'
      type: 'vlan-based'
      encapsulation: 'vxlan'
      replication_type: 'static'
      replication_mcast: '225.0.0.101'
    
     102:
      vlan_type: 'access'
      description: 'Access_VLAN_102'
      vni: '10102'
      evi: '102'
      type: 'vlan-based'
      encapsulation: 'vxlan'
      replication_type: 'ingress'
    
     901:
      vlan_type: 'core'
      description: 'Core_VLAN_VRF_green'
      vni: '50901'
      vrf: 'green'
    
    ###########################################
    # Day 1 VLANs configuration for VRF blue  #
    ###########################################
     201:
      vlan_type: 'access'
      description: 'Access_VLAN_101'
      vni: '10201'
      evi: '201'
      type: 'vlan-based'
      encapsulation: 'vxlan'
      replication_type: 'static'
      replication_mcast: '225.0.0.101'

     202:
      vlan_type: 'access'
      description: 'Access_VLAN_102'
      vni: '10202'
      evi: '202'
      type: 'vlan-based'
      encapsulation: 'vxlan'
      replication_type: 'ingress'
    
     902:
      vlan_type: 'core'
      description: 'Core_VLAN_VRF_blue'
      vni: '50902'
      vrf: 'blue'

    svis:
    ###########################################
    # Day 0 SVIs configuration for VRF green  #
    ###########################################
     101:
      svi_type: 'access'
      vrf: 'green'
      ipv4: '10.1.101.1 255.255.255.0'
      ipv6:
        - '2001:101::1/64'
      mac: 'dead.beef.abcd'

     102:
      svi_type: 'access'
      vrf: 'green'
      ipv4: '10.1.102.1 255.255.255.0'
      ipv6:
        - '2001:102::1/64'
      mac: 'dead.beef.abcd'
    
     901:
      svi_type: 'core'
      vrf: 'green'
      src_intf: 'Loopback1'
      ipv6_enable: 'yes'
    
    ###########################################
    # Day 1 SVIs configuration for VRF blue   #
    ###########################################
     201:
      svi_type: 'access'
      vrf: 'blue'
      ipv4: '10.1.201.1 255.255.255.0'
      ipv6:
        - '2001:201::1/64'

     202:
      svi_type: 'access'
      vrf: 'blue'
      ipv4: '10.1.202.1 255.255.255.0'
      ipv6:
        - '2001:202::1/64'

     902:
      svi_type: 'core'
      vrf: 'blue'
      src_intf: 'Loopback1'
      ipv6_enable: 'yes'
    
    <...snip...>

Now in the file ``group_vars/overlay_db.yml`` stored config for **already provisioned** VRF :green:`green` 

**AND** for **to be provisioned** VRF :blue:`blue`.

But it is needed to avoid re-provisioning of the configuration related to VRF :green:`green`.

To achive this you should edit ``group_vars/create_vars.yml`` and choose which ``dag`` to provision.

``DAG`` configuration includes VRF configuration and respective VLANs/SVIs/Overlay interfaces.

For example, in ``group_vars/overlay.db`` is present configuration for VRFs :green:`green` and :blue:`blue` 

and respective VLANs/SVIs/Overlay interfaces. Only DAG :blue:`blue`  has to provisioned.

.. code-block:: yaml

    dag:
       - blue

This config (or similar one) could be used with next playbooks: 

* playbook_overlay_incremental_generate.yml

* playbook_overlay_incremental_preview.yml

* playbook_overlay_incremental_commit.yml

playbook_overlay_incremental_generate.yml
-----------------------------------------

This playbook is checking ``overlay_db.yml``, current configuration on the switch and generate internal configuration files in 

directory ``host_vars/inc_vars/``

.. code-block:: 

    ansible-playbook -i inventory.yml playbook_overlay_incremental_generate.yml

Output is generated to the files ``host_vars/inc_vars/<hostname>.yml``

.. code-block:: yaml

    ~/cat9k-evpn-ansible/dag$ cat host_vars/inc_vars/Leaf-01.yml 

    access_inft_cli:
    - 202
    - 201
    ovrl_intf_cli:
    - Loopback12
    svi_cli:
    - 202
    - 902
    - 201
    vlan_cli:
    - 202
    - 902
    - 201
    vrf_cli:
    - blue

This output is an input for the next playbook.

playbook_overlay_incremental_preview.yml
----------------------------------------

This playbook is used to generate list of commands which have to be entered on remote device based on 

inputs from ``playbook_overlay_incremental_preview.yml``. 

.. warning::

    No config will be pushed to the remote devices!

.. code-block::

    ansible-playbook -i inventory.yml playbook_overlay_incremental_preview.yml

Output could be checked in ``preview_files/<hostname>-inc.txt``.

.. code-block::

    :~/cat9k-evpn-ansible/dag$ cat preview_files/Leaf-01-inc.txt 
 
    ! vrf block 
    vrf definition blue
    rd 2:2
    address-family ipv4
    route-target import 2:2
    route-target import 2:2 stitching
    route-target export 2:2
    route-target export 2:2 stitching
    address-family ipv6
    route-target import 2:2
    route-target import 2:2 stitching
    route-target export 2:2

    ! bgp l2vpn ipv46 per vrf block 
    router bgp 65001
    address-family ipv4 vrf blue
    advertise l2vpn evpn
    redistribute connected
    redistribute static
    address-family ipv6 vrf blue
    advertise l2vpn evpn
    redistribute connected
    redistribute static

    ! vlan block 
    vlan 201
    name Access_VLAN_101
    vlan 202
    name Access_VLAN_102
    vlan 902
    name Core_VLAN_VRF_blue

    <...snip...>
    
playbook_overlay_incremental_commit.yml
---------------------------------------

This playbook is used for provisioning incremental changes to the remote devices.

The playbook can be used separtely from previous two. 

.. code-block::
    
    ansible-playbook -i inventory.yml playbook_overlay_incremental_commit.yml   

Incremental overlay deleting
============================

It is possible not only to add but also delete the configuration incrementally.

For avoiding full reprovisioning of the network incremental update could be used.

``DAG`` configuration includes VRF configuration and respective VLANs/SVIs/Overlay interfaces.

Full DAG tenants configuration is present in the file ``group_vars/overlay_db.yml``.

Two VRFs :green:`green` and :blue:`blue` with respectful VLANs/SVIs :green:`101,102,901` and :blue:`201,202,902`` are provisioned.

.. code-block:: yaml

    vrfs:
      green:
        ipv6_unicast: 'enable'
        description: 'green VRF defn'
        rd: '1:1'
        afs:
          ipv4:
            rt_import: 
              - '1:1'
              - '1:1 stitching'
            rt_export: 
              - '1:1'
              - '1:1 stitching'

          ipv6:
            rt_import:
              - '1:1'
              - '1:1 stitching'
            rt_export:
              - '1:1'
              - '1:1 stitching'

      blue:
        rd: '2:2'
        afs:
          ipv4:
            rt_import: 
              - '2:2'
              - '2:2 stitching'
            rt_export: 
              - '2:2'
              - '2:2 stitching'
          ipv6:
            rt_import: 
              - '2:2'
              - '2:2 stitching'
            rt_export: 
              - '2:2'
    
    vlans:
    #vrf green vlans
     101:
      vlan_type: 'access'
      description: 'Access_VLAN_101'
      vni: '10101'
      evi: '101'
      type: 'vlan-based'
      encapsulation: 'vxlan'
      replication_type: 'static'
      replication_mcast: '225.0.0.101'
    
     102:
      vlan_type: 'access'
      description: 'Access_VLAN_102'
      vni: '10102'
      evi: '102'
      type: 'vlan-based'
      encapsulation: 'vxlan'
      replication_type: 'ingress'
    
     901:
      vlan_type: 'core'
      description: 'Core_VLAN_VRF_green'
      vni: '50901'
      vrf: 'green'
    
    #vrf blue vlans
     201:
      vlan_type: 'access'
      description: 'Access_VLAN_101'
      vni: '10201'
      evi: '201'
      type: 'vlan-based'
      encapsulation: 'vxlan'
      replication_type: 'static'
      replication_mcast: '225.0.0.101'

     202:
      vlan_type: 'access'
      description: 'Access_VLAN_102'
      vni: '10202'
      evi: '202'
      type: 'vlan-based'
      encapsulation: 'vxlan'
      replication_type: 'ingress'
    
     902:
      vlan_type: 'core'
      description: 'Core_VLAN_VRF_blue'
      vni: '50902'
      vrf: 'blue'

    svis:
    #vrf green svi's
     101:
      svi_type: 'access'
      vrf: 'green'
      ipv4: '10.1.101.1 255.255.255.0'
      ipv6:
        - '2001:101::1/64'
      mac: 'dead.beef.abcd'

     102:
      svi_type: 'access'
      vrf: 'green'
      ipv4: '10.1.102.1 255.255.255.0'
      ipv6:
        - '2001:102::1/64'
      mac: 'dead.beef.abcd'
    
     901:
      svi_type: 'core'
      vrf: 'green'
      src_intf: 'Loopback1'
      ipv6_enable: 'yes'
    
    #vrf blue svi's
     201:
      svi_type: 'access'
      vrf: 'blue'
      ipv4: '10.1.201.1 255.255.255.0'
      ipv6:
        - '2001:201::1/64'

     202:
      svi_type: 'access'
      vrf: 'blue'
      ipv4: '10.1.202.1 255.255.255.0'
      ipv6:
        - '2001:202::1/64'

     902:
      svi_type: 'core'
      vrf: 'blue'
      src_intf: 'Loopback1'
      ipv6_enable: 'yes'
    
    <...snip...>

``DAG`` :blue:`blue` has to be deleted.

To achive this you should edit ``group_vars/create_vars.yml`` and choose which ``dag`` to provision.

.. code-block:: yaml

    dag:
    - blue

    <...snip...>

If **ALL** ``DAGs`` have to be deleted, next config has to be used

.. code-block:: yaml

    dag:
    - all

    <...snip...>

Additionally access interface configuration could be controlled. 

Option `update_access` is used for this:

* true - remove the resespective vlans from access interfaces

* false - makes NO changes to access interface

.. code-block:: yaml

    dag:
    - blue

    update_access: false

This config (or similar one) could be used with next playbooks: 

* playbook_overlay_delete_generate.yml

* playbook_overlay_delete_preview.yml

* playbook_overlay_delete_commit.yml

playbook_overlay_delete_generate.yml
------------------------------------

This playbook is checking ``group_vars/overlay_db.yml``, ``group_vars/delete_vars.yml`` amd current configuration on the switch 

and generate internal configuration files in directory ``host_vars/delete_vars/``.

.. code-block:: 

    ansible-playbook -i inventory.yml playbook_overlay_delete_generate.yml

Output is generated to the files ``host_vars/delete_vars/<hostname>.yml``

.. code-block:: yaml

    ~/cat9k-evpn-ansible/dag$ cat host_vars/delete_vars/Leaf-01.yml 

    access_inft_cli:
    - 202
    - 201
    ovrl_intf_cli:
    - Loopback12
    svi_cli:
    - 202
    - 902
    - 201
    vlan_cli:
    - 202
    - 902
    - 201
    vrf_cli:
    - blue

This output is an input for the next playbook.

playbook_overlay_delete_preview.yml
----------------------------------------

This playbook is used to generate list of commands which have to be entered on remote device based on 

inputs from ``playbook_overlay_delete_preview.yml``. 

.. warning::

    No config will be pushed to the remote devices!

.. code-block::

    ansible-playbook -i inventory.yml playbook_overlay_delete_preview.yml

Output could be checked in ``preview_files/<hostname>-delete.txt``.

.. code-block::

    :~/cat9k-evpn-ansible/dag$ cat preview_files/Leaf-01-delete.txt 

    ! svi block 
    no interface Vlan201
    no interface Vlan202
    no interface Vlan902

    ! nve block 
    interface nve1
    no ip address
    source-interface Loopback1
    host-reachability protocol bgp
    no member vni 10201 mcast-group 225.0.0.101
    no member vni 10202 ingress-replication
    no member vni 50902 vrf blue

    ! vlan block 
    no vlan 201
    no vlan configuration 201
    no vlan 202
    no vlan configuration 202
    no vlan 902
    no vlan configuration 902

    ! l2vpn evpn evi block 
    no l2vpn evpn instance 201
    no l2vpn evpn instance 202

    ! vrf block 
    no vrf definition blue

    <...snip...>

playbook_overlay_delete_commit.yml
---------------------------------------

This playbook is used for provisioning incremental delete changes to the remote devices.

The playbook can be used separtely from previous two. 

.. code-block::
    
    ansible-playbook -i inventory.yml playbook_overlay_delete_commit.yml  

Access interfaces provisioning
==============================

Playbooks described in this section are used for provisioning access interfaces.

Detailed description for the configuration file you can find `here <https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_dag.html#access-interface-configuration>`_

For provisioning access interfaces next playbook could be used:

* playbook_access_add_preview.yml

* playbook_access_add_commit.yml

* playbook_access_incremental_preview.yml

* playbook_access_incremental_commit.yml

playbook_access_add_preview.yml
-------------------------------

This playbook is used for generating config which will be pushed to remote devices.

.. warning::

    No config will be pushed to the remote devices!

For this example basic config is used ``host_vars/access_intf/Leaf-01.yml``

.. code-block:: yaml

    access_interfaces:
        trunks:
            - GigabitEthernet1/0/7
            - GigabitEthernet1/0/8

Let's execute the playbook.

.. code-block:: 

     ansible-playbook -i inventory.yml playbook_access_add_preview.yml

Outputs will be written to files ``preview_files/<hostname>-add-intf.txt``.

.. code-block::

    ! access interface block 
    interface GigabitEthernet1/0/8
    switchport trunk allowed vlan 101,102,201,202
    switchport mode trunk
    interface GigabitEthernet1/0/7
    switchport trunk allowed vlan 101,102,201,202

playbook_access_add_commit.yml
------------------------------

This playbook is used for deploying the configration on the remote devices.

This playbook could be used separetly.

.. code-block::

    ansible-playbook -i inventory.yml playbook_access_add_commit.yml

playbook_access_incremental_preview.yml
---------------------------------------

After initial configuration (aka Day0) some incremental changes are need after some time.

For avoiding full reprovisioning of the network incremental update could be used.

This playbook generates list of commands that will be pushed to the remote devices without provisioning.

.. warning::

    No config will be pushed to the remote devices!

.. code-block::

     ansible-playbook -i inventory.yml playbook_access_incremental_preview.yml

Output files could be found in ``preview_files/<hostname>-inc-intf.txt``

playbook_access_incremental_commit.yml
--------------------------------------

This playbook is used for provisioning remote devices.

.. code-block::

    ansible-playbook -i inventory.yml playbook_access_incremental_commit.yml

Special playbooks
=================

playbook_cleanup.yml
--------------------

This playbook is used for reverting the current configuration back to initial ``default_config.txt``.

.. note::

  ``default_config.txt`` is not part of the repository. You have to make it by yourself.

This playbook is very usefull during the POC or testing, when a lot of changes happens in the network.

.. code-block::

  ansible-playbook -i inventory.yml playbook_cleanup.yml 

playbook_output.yml
-------------------

This playbook is used for collecting outputs from the remote devices.

List of **show commands** is build based on ``templates/leaf_show_command.j2`` and ``templates/spine_show_command.j2``.

.. code-block::

  ansible-playbook -i inventory.yml playbook_output.yml

List of commands to collect:

.. code-block::

  cat output/Leaf-01-show_commands.txt 
  
  show run nve
  show nve peers
  show l2vpn evpn peers vxlan
  show bgp l2vpn evpn summary 
  show bgp l2vpn evpn 

Output collected:

.. code-block::

  cat output/Leaf-01-show_output.txt 
  
  -   - show run nve
    -   - Building configuration...
        - ''
        - 'Current configuration : 3530 bytes'
        - l2vpn evpn
        - ' replication-type static'
        - ' router-id Loopback1'
        - ' default-gateway advertise'
        - '!' 
  <...snip...>
  -   - show nve peers
    -   - '''M'' - MAC entry download flag  ''A'' - Adjacency download flag'
        - '''4'' - IPv4 flag  ''6'' - IPv6 flag'
        - ''
        - Interface  VNI      Type Peer-IP          RMAC/Num_RTs   eVNI     state
            flags UP time
        - nve1       50901    L3CP 172.16.254.4     7c21.0dbd.9548 50901      UP  A/M/4
            00:19:04
        - nve1       50902    L3CP 172.16.254.4     7c21.0dbd.957e 50902      UP  A/M/4
            00:19:04
  
  <...snip...>