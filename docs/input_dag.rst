Inputs
######

Inventory.yml
*************

In the inventory file roles (Spine or Leaf), names and management IP addresses of nodes are described.

.. code-block:: yaml

    all:
        children:
            leaf:
                hosts:
                    Leaf-01:
                        ansible_host: 10.62.149.179
                    Leaf-02:
                        ansible_host: 10.62.149.182
            
            spine:
                hosts:
                    Spine-01:
                        ansible_host: 10.62.149.180
                    Spine-02:
                        ansible_host: 10.62.149.181

``leaf`` and ``spine`` are two roles. Each node should be placed under one of the sections.

``Leaf-1`` , ``Spine-01`` are the hostnames. Keep in mind that that names should be in sync with configuration file names in the directory **host_vars**.

``ansible_host`` is an ip address of the management interface.

group_vars
**********

In this directory stored **common** to all or most of devices configuration.

all.yml
=======

In the file ``all.yml`` defined parameters which are applicable for several devices in the network.
Lets check it one by one.

General access
--------------

This section defines access paramerets to the remote devices.

.. code-block:: yaml

    ansible_connection: ansible.netcommon.network_cli
    ansible_network_os: cisco.ios.ios
    ansible_python_interpreter: "python"
    ansible_user: cisco
    ansible_ssh_pass: cisco123

    <...skip...>

.. table::
   :widths: auto

   ================================ ==========================================================================
     **Parameter**                  **Comments**
   ================================ ==========================================================================
   **ansible_connection**           This option defines type for connection to the remote devices. In this

                                    project connection via SSH withimplementation of CLI is used:


                                    * **ansible.netcommon.network_cli**

   **ansible_network_os**           This option defines operation system of the remote device. This option is

                                    needed in case of usage "network_cli". Cat9k uses IOS-XE so parameter is 

                                    set to:

                                    * **cisco.ios.ios** 

   **ansible_python_interpreter**   This option instruct Ansible to use defined python interpreter. This option  

                                    is set to:
    
                                    * **python**
    
   **ansible_user**                 This option defines a username which is used for access remote devices 
    
                                    over SSH. In this project user must have priviledge level 15. It is set to:
    
                                    * **cisco**
    
   **ansible_password**             This option defined a password for the user which is set in ``ansible_user``.
    
                                    In this project password is set to:
    
                                    * **cisco123**                                
   ================================ ==========================================================================

.. warning::

   ``ansible_user`` must have priveldge level 15. Example of the configuration is below 

   .. code-block::

       username cisco privilege 15 password 0 cisco123

   In the example unencrypted password is used. Fill free to use HIDDEN (7)

If ``enable`` password should be used, check the `Enable Mode <https://docs.ansible.com/ansible/latest/network/user_guide/platform_ios.html>`_ documentation.

L2VPN EVPN general definition
-----------------------------

This section defines global l2vpn evpn parameters.

.. code-block:: yaml
    
    l2vpn_global:
        replication_type: 'static'
        router_id: 'Loopback1'
        default_gw: 'yes'
    
    <...skip...>

.. table::
   :widths: auto

   ================================================ ==========================================================================
     **Parameter**                                                            **Comments**
   ================================================ ==========================================================================
   **l2vpn_global** / :red:`mandatory`              This option defines l2vpn epvn globally.

   **replication_type** / :orange:`optional`        This option defines type of repliction for the L2 BUM traffic globally.

                                                    Could be overwritten per vlan in "vlans" -> "vlan_id" -> "replication_type"

                                                    | section. 
                                                    
                                                    Option **static** instuct to use multicast for the BUM replication.

                                                    Option **ingress** instruct to use Ingress-replication (unicast) for

                                                    | BUM replication.

                                                    **Choices**:

                                                    * static
                                                    
                                                    * ingress
   
   **router_id** / :orange:`optional`               This option defines interface, which IP address will be used for defining

                                                    router-id of l2vpn. In this project interface **Loopback1** is used. This option 

                                                    is set to:

                                                    * **Loopback1**
   
   **default_gw** / :orange:`optional`              This option defines if Default GW will be advertised or not. In this project

                                                    it is defined by defualt:

                                                    * **default_gw: 'yes'**
   ================================================ ==========================================================================

VRF definition
--------------

This section defines vrf parameters. Lets review parameters for unicast first.

.. code-block:: yaml

    vrfs:
        green:
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
    <...skip...>

=============================================== ========================================================================== 
**Parameter**                                                            **Comments**
=============================================== ==========================================================================
**vrfs** / :red:`mandatory`                     This option defines vrf section globally.

**<vrf_name>** / :red:`mandatory`               This option defines a vrf name.

**rd** / :red:`mandatory`                       This option defines a **route distinguisher** of the vrf.

**afs** / :red:`mandatory`                      | This option defines Address Families which will be activated for vrf.

                                                Option **ipv4** defines ipv4 address family.

                                                | Option **ipv6** defines ipv6 address family.

                                                **Choices:**

                                                * ipv4

                                                * ipv6

**rt_import** / :red:`mandatory`                This option defines Route Target **Import** per VRF/AF. In the option is it allowed

                                                to define more than one RT. For EVPN AF additional key is used - **"stitching".**

                                                | In this project next parameter are set by default for both AFs(IPv4 and IPv6):

                                                * 1:1

                                                * 1:1 stitching (L2VPN EVPN AF)

**rt_export** / :red:`mandatory`                This option defines Route Target **Export** per VRF/AF. In the option is it allowed

                                                to define more than one RT. For EVPN AF additional key is used - **"stitching".**

                                                | In this project next parameter are set by default for both AFs(IPv4 and IPv6):

                                                * 1:1

                                                * 1:1 stitching (L2VPN EVPN AF)
=============================================== ==========================================================================

VLANs section
-------------

This section defines VLANs and it stitching with EVIs(EVPN instance) and VNIs(VXLAN network identifier).

.. code-block:: yaml

    vlans:

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

    <...snip...>

.. table::
   :widths: auto

   ================================================ ==========================================================================
     **Parameter**                                                            **Comments**
   ================================================ ==========================================================================
   **vlans** / :red:`mandatory`                     This option defines vlan section globally.

   **<vlan_id>** / :red:`mandatory`                 This option defines VLAN ID on the switch. In this example there are **101,**

                                                    **102, 901**.

   **vlan_type** / :red:`mandatory`                 | This option defines type of the VLAN. 

                                                    Option **access** is used for L2VNIs.

                                                    Option **core** is used for L3VNIs.

                                                    | Option **non-vxlan** is used for VLANs, which are not extended over Fabric.

                                                    **Choices**

                                                    * access

                                                    * core

                                                    * non-vxlan
   
   **description** / :orange:`optional`             This option defines VLAN description.

   **vni** / :red:`mandatory`                       This option defines the VNI which is stitched with a VLAN ID on the swith.

   **evi** / :red:`mandatory`                       This option defines the EVI which is stitched with a VLAN ID on the swith.

                                                    This parameter is **mandatory for L2VNIs only.**

   **type** / :red:`mandatory`                      This option defines the type of EVI. On Cat9k **vlan-based** is supported

                                                    for now. This parameter is  **mandatory for L2VNIs only.**

   **encapsulation** / :red:`mandatory`             This option defines encapsulation for packet is the core. It is set to

                                                    **vxlan**. This parameter is  **mandatory for L2VNIs only.**
                                                    
   **replication_type** / :red:`mandatory`          | This option defines replication type for the BUM for L2VNI.
                                                    
                                                    Option **static** is used for multicast replication. In this case 

                                                    **replication_mcast** parameter is needed.

                                                    | Option **ingress** is used for Ingress-replication (unicast).

                                                    **Choices:**

                                                    * static

                                                    * ingress

                                                    This parameter is  **mandatory for L2VNIs only.**

   **vrf** / :red:`mandatory`                       This option defines VRF for which L3VNI is used for encapsulation the routed

                                                    | traffic in the core. For this option **vlan_type** must be **core**.

                                                    This parameter is  **mandatory for L3VNIs only.**
   ================================================ ==========================================================================

SVIs section
------------

This section defines SVIs configuration.

.. code-block:: yaml

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
     ipv6_enable: 'yes


    <...snip...>

.. table::
   :widths: auto

   ================================================ ==========================================================================
     **Parameter**                                                            **Comments**
   ================================================ ==========================================================================
   **svis** / :red:`mandatory`                      This option defines SVIs section globally.

   **<svi_id>** / :red:`mandatory`                  This option defines SVI ID on the switch. In this example there are **101,**

                                                    **102, 901**.

   **svi_type** / :red:`mandatory`                  | This option defines type of the SVI. 

                                                    Option **access** is used for SVI for vlans stitched to L2VNIs.

                                                    Option **core** is used for SVI for vlans stitched to L3VNIs.

                                                    | Option **non-vxlan** is used for SVI for vlans, which are not extended over Fabric.

                                                    **Choices**

                                                    * access

                                                    * core

                                                    * non-vxlan
   
   **vrf** / :red:`mandatory`                       This option defines vrf which SVI belongs to.

   **ipv4** / :red:`mandatory`                      This option defines the IPv4 address configured on the SVI. 
   
                                                    This parameter is applicable **for SVIs for L2VNIs only.**

   **ipv6** / :orange:`optional`                    This option defines the IPv6 addresses configured on the SVI.

                                                    This parameter is applicable **for SVIs for L2VNIs only.**

   **mac** / :orange:`optional`                     This option defines the MAC to be configured on SVI.

                                                    This parameter is applicable **for SVIs for L2VNIs only.**

   **src_intf** / :red:`mandatory`                  This option defines Source Interface for the SVI for L3VNI.

                                                    This parameter is applicable **for SVIs for L3VNIs only.**
                                                    
   **ipv6_enable** / :orange:`optional`             This option defines enables IPv6 on the SVI.

                                                    This parameter is applicable **for SVIs for L3VNIs only.**
                                                    
   ================================================ ==========================================================================

NVE section
-----------

   This section defines NVE interface configuration.

.. code-block:: yaml

    nve_interfaces:
        1:
            source_interface: 'Loopback1'

    <...snip...>

.. table::
   :widths: auto

   ================================================ ==========================================================================
     **Parameter**                                                            **Comments**
   ================================================ ==========================================================================
   **nve_interfaces** / :red:`mandatory`            This option defines NVE section globally.

   **nve_id>** / :red:`mandatory`                   This option defines NVE ID on the switch. 

   **source_interface** / :red:`mandatory`          This option defines source interface for corresponding NVE interface. 

   ================================================ ==========================================================================

host_vars
*********

In this directory stored **specific** to the dedicated device configuration.

<node_name>.yml
===============

In the file ``<node_name>.yml`` defined specific to the dedicated node configuration parameters. Usually it is related to interface 
configuration and underlay configuration in general.

Lets review the configuration options one by one.

Hostname section
----------------

In this section hostname of the node is defined.

.. code-block:: yaml

    hostname: 'Leaf-01'

    <...snip...>


.. table::
    :widths: auto

    =============================================== ==========================================================================
    **Parameter**                                                            **Comments**
    =============================================== ==========================================================================
    **hostname** / :orange:`optional`               This option defines remote device hostname.
    =============================================== ==========================================================================

Global routing section
----------------------

In this section parameters of IPv4/IPv6 in GRT are defined.

ç


.. table::
    :widths: auto

    =============================================== ==========================================================================
    **Parameter**                                                            **Comments**
    =============================================== ==========================================================================
    **routing** / :red:`mandatory`                  This option defines global routing section.

    **ipv4_uni** / :red:`mandatory`                 This option enables global IPv4 unicast routing on the switch.

    **ipv6_uni** / :red:`mandatory`                 This option enables global IPv6 unicast routing on the switch.

    **ipv6_multi** / :red:`mandatory`               This option enables global IPv4 multicast routing on the swith.

    =============================================== ==========================================================================

Interface section
-----------------

In this section interfaces configuration is defined.

.. code-block:: yaml

    interfaces:

        Loopback0:
            name: 'Routing Loopback'
            ip_address: '172.16.255.3'
            subnet_mask: '255.255.255.255'
            loopback: 'yes'
            pim_enable: 'no'

        Loopback1:
            name: 'NVE Loopback'
            ip_address: '172.16.254.3'
            subnet_mask: '255.255.255.255'
            loopback: 'yes'
            pim_enable: 'yes'

        GigabitEthernet1/0/1:
            name: 'Backbone interface to Spine-01'
            ip_address: '172.16.13.3'
            subnet_mask: '255.255.255.0'
            loopback: 'no'
            pim_enable: 'yes'

        GigabitEthernet1/0/2:
            name: 'Backbone interface to Spine-02'
            ip_address: '172.16.23.3'
            subnet_mask: '255.255.255.0'
            loopback: 'no'
            pim_enable: 'yes' 

    <...snip...>


.. table::
    :widths: auto

    =============================================== ==========================================================================
    **Parameter**                                                            **Comments**
    =============================================== ==========================================================================
    **interfaces** / :red:`mandatory`               This option defines global interface section.

    **<interface_name>** / :red:`mandatory`         This option defines interface name i.e. ``Loopback0`` or ``GigabitEthernet1/0/1``

    **name** / :orange:`optional`                   This option defines interface description.

    **ip_address** / :red:`mandatory`               This option defines IPv4 address on the interface.

    **subnet_mask** / :red:`mandatory`              This option defines subnet mask for the IPv4 address.

    **loopback** / :red:`mandatory`                 | This option defines if interface is loopback or not.

                                                    **Choices:**

                                                    * yes

                                                    * no

    **pim_enable** / :red:`mandatory`               | This option defines if PIM has to be enabled on the interface.

                                                    **Choices:**

                                                    * yes

                                                    * no
    =============================================== ==========================================================================

OSPF section
------------

This section defines ospf parameters.

By default next OSPF configuration is applied:

* Interface network type - **point-to-point**

* OSPF process ID - **1**

* OSPF area number - **0**

OSPF router-id is configurable parameter.

.. code-block:: yaml

    ospf:
        router_id: '172.16.255.3'

    <...snip...>

.. table::
    :widths: auto

    =============================================== ==========================================================================
    **Parameter**                                                            **Comments**
    =============================================== ==========================================================================
    **ospf** / :red:`mandatory`                     This option defines OSPF section globally.
    
    **router_id** / :red:`mandatory`                This option defines OSPF router-id.
    =============================================== ==========================================================================

PIM section
-----------

This section defines global PIM parameters. This section is optional if Ingress-Replication in the core is used.


.. code-block:: yaml

    pim:
        rp_address: '172.16.255.255'
    
    <...skip...>

.. table::
    :widths: auto

    =============================================== ==========================================================================
    **Parameter**                                                            **Comments**
    =============================================== ==========================================================================
    **pim** / :red:`mandatory`                      This option defines PIM section globally.
    
    **rp_address** / :red:`mandatory`               This option defines RP address.
    =============================================== ==========================================================================

MSDP section
------------

This section defines MSDP parameters. Usually MSDP is used for configuration RP redundancy in underlay.

This section in general is optional.

.. code-block:: yaml
    
    msdp:
        '1':
            peer_ip: '172.16.254.2'
            source_interface: 'Loopback1'
            remote_as: '65001'

    <...skip...>

.. table::
    :widths: auto

    =============================================== ==========================================================================
    **Parameter**                                                            **Comments**
    =============================================== ==========================================================================
    **msdp** / :red:`mandatory`                     This option defines MSDP section globally.
    
    **<msdp_neighbor_id>** / :red:`mandatory`       This option defines ID for the MSDP peer. This number is not used in the 

                                                    switch configuration, just index number.

    **peer_ip** / :red: `mandatory`                 This option defines MSDP peer IPv4 address.

    **source_interface** / :red: `mandatory`        This option defindes source interface which IP address will be used like SRC IP

                                                    for the MSDP seession.

    **remote_as** / :red: `mandatory`               This option is used for defining BGP AS number of the MSDP peer.                               
    =============================================== ==========================================================================

BGP section
-----------

This section defines BGP parameters. 

By default next design assumption are made:

* Leafs are Route-Reflector clients

* Two present Spines in the topology are Route-Reflectors


.. code-block:: yaml

    bgp:
      as_number: '65001'
      router_id: 'Loopback0'
      neighbors:
        '172.16.255.1':
            peer_as_number: '65001'
            source_interface: 'Loopback0'

        '172.16.255.2':
            peer_as_number: '65001'
            source_interface: 'Loopback0'

        '172.16.255.3':
            peer_as_number: '65001'
            source_interface: 'Loopback0'
            rrc: 'yes'
    
    <...snip...>

.. table::
    :widths: auto

    =============================================== ==========================================================================
    **Parameter**                                                            **Comments**
    =============================================== ==========================================================================
    **bgp** / :red:`mandatory`                      This option defines BGP section globally.
    
    **as_number** / :red:`mandatory`                This option defines BGP AS number.

    **router_id** / :red:`mandatory`                This option defines interface which ip address will be used like BGP router ID.

    **neighbors** / :red:`mandatory`                This option defines neighbors section.

    **neigbor_ip_address** / :red:`mandatory`       This option defines BGP neighbor ip address

    **peer_as_number** / :red:`mandatory`           This option defines BGP neighbor AS number

    **source_interface** / :red:`mandatory`         This option defines source interface which ip address will be used like a SRC IP

                                                    for BGP session.

    **rrc** / :orange:`optional`                    This option defines the peer like a BGP route-reflector client.
    =============================================== ==========================================================================

Access interface configuration
==============================

This section defines configuration for the customer-facing access interfaces.

By default all access interfaces will be configured like trunks with all L2VNI vlans that are mentioned in ``all.yml``

Trunk configuration
-------------------

Vlans to be assigned to an interace are taken from the following in increasing **order of priority (3 > 2 > 1).**

.. note::

    **Trunk configuration order of priority (3 > 2 > 1)**
 
1. ``vlans`` in ``all.yml`` (for ``playbook_access_add_commit/preview.yml``) or ``access_intf_cli`` in ``host_vars/inc_vars/<hostname>.yml`` 

(for ``playbook_access_incremental_commit/preview.yml``)
 
.. code-block:: yaml
    
    access_interfaces:              
        trunks:                       
            - GigabitEthernet1/0/6     

    <...snip...>


2. ``trunk_vlan_list`` in ``access_interfaces`` dictionary

.. code-block:: yaml
    
    access_interfaces:                
        trunk_vlan_list: 101,102,201     
        trunks:                         
            - GigabitEthernet1/0/6       
    
    <...snip...>

3. ``trunk_vlan_list`` in specific interface dictionary

.. code-block:: yaml

    access_interfaces:                 
        trunks:                          
            - GigabitEthernet1/0/6:        
                trunk_vlan_list: 101,102   
    
    <...snip...>


Access configuration
--------------------

Vlan to be assigned to an interace are taken from the following in increasing **order of priority (2 > 1).**

.. note::

    **Access configuration order of priority (2 > 1)**

1. ``access_vlan`` in ``access_interfaces`` dictionary

.. code-block:: yaml

    access_interfaces:               
        access_vlan: 101 
        access:                        
            - GigabitEthernet1/0/6       
        
    <...snip...>
    

2. ``access_vlan`` in specific interface dictionary

.. code-block:: yaml

    access_interfaces:               
        access:                        
            - GigabitEthernet1/0/6:      
                access_vlan: 102         

    <...snip...>



Examples
--------

There is an assumption, that in ``all.yml`` defined next vlans: :green:`101,102,201,202`

Example 1
^^^^^^^^^

Content of ``host_vars/access_intf/<hostname>.yml``

.. code-block:: yaml

    access_interfaces:
        trunks:
            - GigabitEthernet1/0/7
            - GigabitEthernet1/0/8

Values assigned after execution

**GigabitEthernet1/0/7** - :green:`101,102,201,202` (from ``all.yml`` or ``host_vars/inc_vars/<hostname>.yml``)

**GigabitEthernet1/0/8** - :green:`101,102,201,202` (from ``all.yml`` or ``host_vars/inc_vars/<hostname>.yml``)

Example 2
^^^^^^^^^

Content of ``host_vars/access_intf/<hostname>.yml``

.. code-block:: yaml

    access_interfaces:
        access_vlan: 202
        access:
            - GigabitEthernet1/0/7
            - GigabitEthernet1/0/8

Values assigned after execution

**GigabitEthernet1/0/7** - :green:`202`

**GigabitEthernet1/0/8** - :green:`202`

Example 3
^^^^^^^^^

Content of ``host_vars/access_intf/<hostname>.yml``

.. code-block:: yaml

    access_interfaces:
        trunks:
            - GigabitEthernet1/0/6
            - GigabitEthernet1/0/7:
                trunk_vlan_list: 101,102,201
        access:
            - GigabitEthernet1/0/8
            - GigabitEthernet1/0/9
        access_vlan: 202

Values assigned after execution

**GigabitEthernet1/0/6** - :green:`101,102,201,202` (from ``all.yml`` or ``host_vars/inc_vars/<hostname>.yml``)

**GigabitEthernet1/0/7** - :green:`101,102,201`

**GigabitEthernet1/0/8** - :green:`202`

**GigabitEthernet1/0/9** - :green:`202`

Example 4
^^^^^^^^^

Content of ``host_vars/access_intf/<hostname>.yml``

.. code-block:: yaml

    access_interfaces:
        trunks:
            - GigabitEthernet1/0/6
            - GigabitEthernet1/0/7:
                trunk_vlan_list: 101,102,201
        trunk_vlan_list: 101,201
        access:
            - GigabitEthernet1/0/8
            - GigabitEthernet1/0/9:
                access_vlan: 102
        access_vlan: 202

Values assigned after execution

**GigabitEthernet1/0/6** - :green:`101,201`

**GigabitEthernet1/0/7** - :green:`101,102,201`

**GigabitEthernet1/0/8** - :green:`202`

**GigabitEthernet1/0/9** - :green:`102`

Example 5
^^^^^^^^^

Content of ``host_vars/access_intf/<hostname>.yml``

.. code-block:: yaml

    access_interfaces:
        trunks:
            - GigabitEthernet1/0/5
            - GigabitEthernet1/0/6:
                trunk_vlan_list: 101,102,201
            - GigabitEthernet1/0/7
        access:
            - GigabitEthernet1/0/8:
                access_vlan: 201
            - GigabitEthernet1/0/9:
                access_vlan: 102
        access_vlan: 202

Values assigned after execution

**GigabitEthernet1/0/5** - :green:`101,102,201,202` (from ``all.yml`` or ``host_vars/inc_vars/<hostname>.yml``)

**GigabitEthernet1/0/6** - :green:`101,102,201`

**GigabitEthernet1/0/7** - :green:`101,102,201,202` (from ``all.yml`` or ``host_vars/inc_vars/<hostname>.yml``)

**GigabitEthernet1/0/8** - :green:`201`

**GigabitEthernet1/0/9** - :green:`102`

Example 6
^^^^^^^^^

Content of ``host_vars/access_intf/<hostname>.yml``

.. code-block:: yaml

    access_interfaces:
        trunks:
            - GigabitEthernet1/0/7
    access:
        - GigabitEthernet1/0/8:
            access_vlan: 201

Values assigned after execution

**GigabitEthernet1/0/7** - :green:`101,102,201,202` (from ``all.yml`` or ``host_vars/inc_vars/<hostname>.yml``)

**GigabitEthernet1/0/8** - :green:`201`




