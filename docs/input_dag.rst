DAG (Distributed Anycast Gateway)
#################################

Distributed anycast gateway feature for EVPN VXLAN is a default gateway addressing mechanism that enables the use of the same gateway IP addresses 
across all the leaf switches that are part of a VXLAN network.

.. warning::

    The same subnet mask and IP address must be configured on all the switch virtual interfaces (SVIs) that act as a distributed anycast gateway (DAG).

Inputs
######

Inventory.yml
*************

 In the inventory file, roles (Spine or Leaf), names, and management IP addresses of the nodes are
 described.

.. code-block:: yaml

    all:
      children:
        leaf:
          hosts:
            Leaf-01:
              ansible_host: 10.1.1.1
            Leaf-02:
              ansible_host: 10.1.1.2
            
        spine:
          hosts:
            Spine-01:
              ansible_host: 10.1.1.3
            Spine-02:
              ansible_host: 10.1.1.4

``leaf`` and ``spine`` are two roles. Each node should be placed under one of these roles.

``Leaf-1`` , ``Spine-01`` are the hostnames (nodes). Keep in mind that the names should be with the name of the configuration files 
in the directory ``host_vars``.

``ansible_host`` is the IP address of the management interface.

group_vars
**********

This directory contains the configurations which are common to all or most of devices.

all.yml
=======

The parameters defined in the file ``all.yml`` are applicable to all devices in the network.

General access
--------------

This section defines access parameters of the remote devices.

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
   **ansible_connection**           This option defines thetype for connection to the remote devices. 
   
                                    In this project, connection via SSH with implementation of CLI is used:

                                    * **ansible.netcommon.network_cli**

   **ansible_network_os**           This option defines the operation system of the remote device. 
                                    This option is needed if “network_cli” is used for 'ansible_connection'. 
                                    
                                    In this project, Cat9k with IOS-XE is used, so this option is set to:

                                    * **cisco.ios.ios** 

   **ansible_python_interpreter**   This option instruct Ansible to use defined python interpreter. 
   
                                    This option is set to:
    
                                    * **python**
    
   **ansible_user**                 This option defines a username which is used for access remote devices 
    
                                    over SSH. In this project, user must have privilege level 15. 
                                    
                                    This option is set to:
    
                                    * **cisco**
    
   **ansible_password**             This option defines a password for the user in 'ansible_user'.
    
                                    In this project, the password is set to:
    
                                    * **cisco123**                                
   ================================ ==========================================================================

.. warning::

   ``ansible_user`` must have privildge level 15. Example of the configuration is below 

   .. code-block::

       username cisco privilege 15 password 0 cisco123

In this example, unencrypted password is used. Feel free to use HIDDEN (7)

If ``enable`` password should be used, check the `Enable Mode <https://docs.ansible.com/ansible/latest/network/user_guide/platform_ios.html>`_ documentation.

overlay_db.yml
==============

In this file information about EVPN configuration is stored.
Let's check this file gradually step-by-step.

L2VPN EVPN general definition
-----------------------------

This section defines global L2VPN EVPN parameters.

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
   **l2vpn_global** / :red:`mandatory`              This option defines L2VPN EVPN globally.

   **replication_type** / :orange:`optional`        This option defines the type of repliction for the L2 BUM traffic globally.

                                                    Could be overwritten per vlan by "vlans" -> "vlan_id" -> "replication_type"

                                                    | section. 
                                                    
                                                    Option **static** enables to use multicast for the BUM replication.

                                                    Option **ingress** enables to use Ingress-replication (unicast) for

                                                    | BUM replication.

                                                    **Choices**:

                                                    * static
                                                    
                                                    * ingress
   
   **router_id** / :orange:`optional`               This option defines the interface whose IP address will be used for defining
                                                    router-id of L2VPN.The  interface **Loopback1** is used for the router-id of L2VPN.
                                                    
                                                    In this project the option is set to:

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
**vrfs** / :red:`mandatory`                     This option defines the vrf section.

**<vrf_name>** / :red:`mandatory`               This option defines the vrf name.

**rd** / :red:`mandatory`                       This option defines the **route distinguisher** of the vrf.

**afs** / :red:`mandatory`                      | This option defines the address families which will be activated for the vrf.

                                                Option **ipv4** defines ipv4 address family.

                                                | Option **ipv6** defines ipv6 address family.

                                                **Choices:**

                                                * ipv4

                                                * ipv6

**rt_import** / :red:`mandatory`                This option defines the  **Route Target Import** per VRF/AF. This option allows 
                                                more than one RT to be defined. For EVPN AF additional key is used - **"stitching".**

                                                | In this project next parameter are set by default for both AFs(IPv4 and IPv6):

                                                * 1:1

                                                * 1:1 stitching (L2VPN EVPN AF)

**rt_export** / :red:`mandatory`                This option defines the **Route Target Export** per VRF/AF. This option allows
                                                more than one RT to be defined. For EVPN AF, additional key  **"stitching"** is used.

                                                | In this project below parameters are set by default for both AFs(IPv4 and IPv6):

                                                * 1:1

                                                * 1:1 stitching (L2VPN EVPN AF)
=============================================== ==========================================================================

VLANs section
-------------

This section defines the VLANs and their stitching with EVIs (EVPN instance) and VNIs (VXLAN network identifier).

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
   **vlans** / :red:`mandatory`                     This option defines the VLAN section.

   **<vlan_id>** / :red:`mandatory`                 This option defines the VLAN ID. 
   
                                                    In the example shown, VLAN IDs are **101**, **102**, **901**.

   **vlan_type** / :red:`mandatory`                 | This option defines the VLAN type. 

                                                    Option **access** is used for L2VNIs.

                                                    Option **core** is used for L3VNIs.

                                                    | Option **non-vxlan** is used for VLANs, which are not extended over Fabric.

                                                    **Choices**

                                                    * access

                                                    * core

                                                    * non-vxlan
   
   **description** / :orange:`optional`             This option defines the VLAN description.

   **vni** / :red:`mandatory`                       This option defines the VNI which is stitched with the VLAN ID on the switch.

   **evi** / :red:`mandatory`                       This option defines the EVI which is stitched with the VLAN ID on the switch.

                                                    This parameter is **mandatory for L2VNIs only.**

   **type** / :red:`mandatory`                      This option defines the EVI type. For Cat9k **vlan-based** is only supported
                                                    EVI type presently. 
                                                    
                                                    This parameter is  **mandatory for L2VNIs only.**

   **encapsulation** / :red:`mandatory`             This option defines encapsulation for the packet is the core. 
   
                                                    This parameter is  **mandatory for L2VNIs only.**

                                                    In the example shown, it is set to vxlan.
                                                    
   **replication_type** / :red:`mandatory`          | This option defines the replication type for the BUM for L2VNI.
                                                    
                                                    Option **static** is used for multicast replication. In this case, 

                                                    **replication_mcast** parameter is needed.

                                                    | Option **ingress** is used for ingress-replication (unicast).

                                                    **Choices:**

                                                    * static

                                                    * ingress

                                                    This parameter is  **mandatory for L2VNIs only.**

   **vrf** / :red:`mandatory`                       This option defines the VRF that uses the VLAN’s L3VNI for encapsulating
                                                    the routed traffic in the core.
                                                    
                                                    For this option, **vlan_type** must be **core**.

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
   **svis** / :red:`mandatory`                      This option defines SVIs section.

   **<svi_id>** / :red:`mandatory`                  This option defines the SVI ID on the switch. In this example, there are **101,**

                                                    **102, 901**.

   **svi_type** / :red:`mandatory`                  | This option defines the SVI type. 

                                                    Option **access** is used when the VLAN associated with an SVI is stitched to L2VNIs.

                                                    Option **core** is used when the VLAN associated with an SVI is stitched to L3VNIs.

                                                    | Option **non-vxlan** is used when the VLAN associated with an SVI are not extended over Fabric.

                                                    **Choices**

                                                    * access

                                                    * core

                                                    * non-vxlan
   
   **vrf** / :red:`mandatory`                       This option defines the vrf which SVI belongs to.

   **ipv4** / :red:`mandatory`                      This option defines the IPv4 address configured on the SVI. 
   
                                                    This parameter is applicable **for L2VNI SVIs only.**

   **ipv6** / :orange:`optional`                    This option defines the IPv6 addresses configured on the SVI.

                                                    This parameter is applicable **for L2VNI SVIs only.**

   **mac** / :orange:`optional`                     This option defines the MAC which is to be configured on the SVI.

                                                    This parameter is applicable **for L2VNI SVIs only.**

   **src_intf** / :red:`mandatory`                  This option defines thee source Interface for the SVI for L3VNI.

                                                    This parameter is applicable **for L3VNI SVIs only.**
                                                    
   **ipv6_enable** / :orange:`optional`             This option defines enables IPv6 on the SVI.

                                                    This parameter is applicable **for L3VNI SVIs only.**
                                                    
   ================================================ ==========================================================================

NVE section
-----------

   This section defines the NVE interface configuration.

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
   **nve_interfaces** / :red:`mandatory`            This option defines the NVE section.

   **nve_id** / :red:`mandatory`                   This option defines the NVE ID.

   **source_interface** / :red:`mandatory`          This option defines the source interface for the corresponding NVE interface. 

   ================================================ ==========================================================================

dhcp_vars.yml
============

In this file inforrmation about DHCP configuration is stored.

.. code-block:: yaml

   dhcp:
        dhcp_options:
            option_82_link_selection_standard: standard
            option_82_server_id_override: standard
    
        vrfs:
            all:                   
                helper_address: 
                    - 10.1.1.1

.. table::
   :widths: auto

   ========================================================= ==========================================================================
     **Parameter**                                                            **Comments**
   ========================================================= ==========================================================================
   **dhcp** / :red:`mandatory`                               This option defines the DHCP section.

   **dhcp_options** / :orange:`optional`                     This option defines DHCP options.

   **option_82_link_selection_standard** / :red:`mandatory`  This option defines the if cisco dhcp option/suboption 82[150] --> 82[5]
       
   **option_82_server_id_override** / :red:`mandatory`       This option defines the if cisco dhcp option/suboption 82[151] --> 82[11]  
   
   **vrfs** / :red:`mandatory`                               This option defines the VRF section
   ========================================================= ==========================================================================

Examples
--------

Example 1
^^^^^^^^^

DHCP Server is in the Layer 3 Default VRF and the DHCP Client is in the Tenant VRF

.. code-block:: yaml

    vrfs:  
      all:                                             
        helper_address:                                
          - 10.1.1.1                       
        helper_vrf: global                             
        relay_src_intf: Loopback1                     

As a result on **ALL** L2 SVIs for **ALL** VRFs ``helper-address`` **10.1.1.1** which is reachible over ``global`` VRF with **source-interface** ``Loopback1` will be configured.

Example 2 
^^^^^^^^^ 

DHCP Server is in the Layer 3 Default VRF and the DHCP Client is in the Tenant VRF

.. code-block:: yaml

    vrfs:  
      all:                                             <--------- Applies configs to all except 'green' DAG 
        helper_address:                                <--------- configs 'ip helper-address global 10.1.1.1' for all SVIs except green's
          - 10.1.1.1   
        helper_vrf: global                     
        relay_src_intf: Loopback1                      <--------- configs 'Loopback1' as DHCP relay source for all SVIs except green's
  
      green:                                           <--------- Applies configs to 'green' DAG 
        helper_address:                                <--------- configs 'ip helper-address global 10.1.1.2' for all 'green' DAG SVIs
          - 10.1.1.2                       
        helper_vrf: global  
        relay_src_intf: Loopback1                      <--------- configs 'Loopback1' as DHCP relay source for 'green' SVIs

Example 3 
^^^^^^^^^

DHCP Client and DHCP Server are in Different Tenant VRFs

.. code-block:: yaml

    vrfs:
      all:
        helper_address: 
          - 10.1.1.1
        helper_vrf: green                               <--------- Specifies the server tenant location
        relay_src_intf: Loopback1


Example 4
^^^^^^^^^

DHCP Server and DHCP Client are in the Same Tenant VRF

.. code-block:: yaml

    vrfs:
      all:                                              <--------- Applies configs to all DAGs
        helper_address:                                 <--------- configs 'ip helper-address 10.1.1.1' and 'ip helper-address 10.1.1.2' ll SVIs
          - 10.1.1.1
          - 10.1.1.2


Example 5
^^^^^^^^^

Repective DAG's interface from the overlay_interface section of host_vars/<inventory>.yml file is set as DHCP relay source interface for SVIs

.. code-block:: yaml

    vrfs:
      green:                                            <--------- Applies configs to 'green' DAG 
        helper_address:                                 <--------- configs 'ip helper-address 10.1.1.1' and 'ip helper-address 10.1.1.2' ll 'green' SVIs
          - 10.1.1.1
          - 10.1.1.2
        helper_vrf: green
        relay_src_intf: Loopback1                       <--------- configs 'Loopback1' as DHCP relay source for all 'green' SVIs
      blue:                                             <--------- Applies configs to 'blue' DAG 
        helper_address:                                 <--------- configs 'ip helper-address 10.1.1.3' for 'blue' SVIs
          - 10.1.1.3 
        helper_vrf: blue 
        relay_src_intf: Loopback2                       <--------- configs 'Loopback2' as DHCP relay source for all 'blue' SVIs

Since ``relay_src_intf`` key is explicitly mentioned in this case, Loopback1 is set as DHCP relay source interface for all :green:`green` SVIs and
Loopback2 is set as DHCP relay source interface for all :blue:`blue` SVIs.

trm_overlay_db.yml
==================

This section defines TRM configuration for the EVPN Fabric.

By default all TRM-related configuration is stored in ``group_vars/trm_overlay_db.yml``.

It is assumed that DAG configuration for unicast is alredy done and only TRM part is needed.

.. code-block:: yml
    vrfs:
      blue:                                                 
        register_source: loopback1 
                         
        fabric_anycast_rp:                                  
          rp_loopback: Loopback256                          
          ipv4_rp_address: '10.2.255.255'                   
 
        afs:
          ipv4:
          default_mdt_group: '239.1.1.1' 
    <...snip...>

.. table::
    :widths: auto

    =============================================== ==========================================================================
    **Parameter**                                                            **Comments**
    =============================================== ==========================================================================
    **vrfs** / :red:`mandatory`                     This option defines VRF section globally.
    
    **vrf_name** / :red:`mandatory`                 This option defines VRF name which will be configured.

    **register_source** / :red:`mandatory`          This option defines interface which IPv4 will be used for SRC Registration.

    **ipv6_register_source** / :orange:`optional`   This option defines interface which IPv6 will be used for SRC Registration.

    **fabric_anycast_rp** / :orange:`optional`      This option defines Anycast RP section.

    **fabric_internal_rp** / :orange:`optional`     This option defines Internal RP section.

    **fabric_external_rp** / :orange:`optional`     This option defines External RP section.

    **ipv4_rp_address** / :orange:`optional`        This option defines RP IPv4 address.

    **ipv6_rp_address** / :orange:`optional`        This option defines RP IPv6 address.

    **rp_loopback** / :orange:`optional`            This option defines RP loopback interface (Anycast or Internal)

    **rp_device** / :orange:`optional`              This option defines VTEP where Internal RP is configured. 

    **ssm_range: 'x-y'** / :orange:`optional`       This option defines per VRF SSM range.

    **afs** / :red:`mandatory`                      This option defines address family section.

    **ipv4** / :orange:`optional`                   This option defines IPv4 AF section.

    **ipv6** / :orange:`optional`                   This option defines IPv6 AF section.

    **default_mdt_group** / :orange:`optional`      This option defines Default MDT multicast group.

    **data_mdt_group** / :orange:`optional`         This option defines Data MDT multicast group.

    **data_mdt_threshold** / :orange:`optional`     This option defines Data MDT threshold.
    =============================================== ==========================================================================

Examples
--------

Example 1
^^^^^^^^^

TRM v4 with anycast RP fabric for DAG 'blue'

.. code-block:: yml
  
  vrfs:
    blue:                                                 <--------- Applies config to blue DAG
      register_source: loopback1                          <--------- configs unique IP for the loopback
      fabric_anycast_rp:                                  <--------- configs PIM sparse mode with anycast RP
        rp_loopback: Loopback256                          <--------- configs loopback (on all device) if not already configured
        ipv4_rp_address: '10.2.255.255'                   <--------- configs IPv4 addr as PIM RP for the multicast group, by default /32 mask is applied
   
      afs:
        ipv4:
          default_mdt_group: '239.1.1.1'                  <--------- configs mcast group address for default MDT groups

Example 2
^^^^^^^^^

TRM v4 and v6 with internal RP fabric for DAG 'blue'.

.. code-block:: yml

  vrfs:   
    blue:
      register_source: loopback1
      ipv6_register_source: loopback1                     <--------- configs unique IP for the loopback for IPv6; if this key is missing, "register_source" is used for IPv6

      fabric_internal_rp:                                 <--------- configs PIM sparse mode with internal RP
        rp_device: Leaf-02
        rp_loopback: Loopback256                          <--------- configs loopback (only on the mentioned device above) if not already configured
        ipv4_rp_address: '10.2.255.255 255.255.255.255'
        ipv6_rp_address: 'FC00:2:255::255'                <--------- configs IPv6 addr as PIM RP for the multicast group, by default /128 mask is applied
  
      afs:
        ipv4:
          default_mdt_group: '239.1.1.1'                  
          data_mdt_group: '225.2.2.0 0.0.0.255'           <--------- configs mcast group address for data MDT groups for IPv4
          data_mdt_threshold: '111'                       <--------- defines bandwidth threshold for data MDT groups

        ipv6:
          default_mdt_group: '239.1.1.1'                  <--------- configs mcast group address for default MDT groups for IPv6

Example 3
^^^^^^^^^

TRM v6 with external RP fabric for DAG 'blue'

.. code-block:: yml

  vrfs:   
    blue:
      ipv6_register_source: loopback1                     <--------- configs unique IP for the loopback for IPv6

      fabric_external_rp:                                 <--------- configs PIM sparse mode with external RP
        ipv6_rp_address: 'FC00:2:255::255'                <--------- configs IPv6 addr as PIM RP for the multicast group, by default /128 mask is applied   

      afs:
        ipv6:
          default_mdt_group: '239.1.1.1'                  <--------- configs mcast group address for default MDT groups for IPv6

Example 4
^^^^^^^^^

TRM v4 with anycast RP fabric for DAG 'blue'
TRM v4 and v6 with internal RP fabric for DAG 'green'

.. code-block:: yml

  vrfs:
    blue:
      register_source: Loopback0
  
      fabric_anycast_rp:
        rp_loopback: Loopback256
        ipv4_rp_address: '10.2.255.255 255.255.255.255'
  
      afs:
        ipv4:
          default_mdt_group: '239.1.1.1'
          data_mdt_group: '225.2.2.0 0.0.0.255'
          data_mdt_threshold: '111'
  
    green:
      register_source: Loopback1
      ipv6_register_source: Loopback2
  
      fabric_internal_rp:
        rp_device: Leaf-02
        rp_loopback: Loopback255
        ipv4_rp_address: '10.3.255.255'
        ipv6_rp_address: 'FC00:2:255::255'
  
      afs:
        ipv4:
          default_mdt_group: '239.1.1.2'
          data_mdt_group: '225.2.3.0 0.0.0.255'
          data_mdt_threshold: '111'
  
        ipv6:
          default_mdt_group: '239.1.1.2'
          
host_vars
*********

This directory contains configuration specific to a device.

<node_name>.yml
===============

The file ``<node_name>.yml`` contains configurations, usually the ones related to interface and underlay, specific to a node.

Let us review the configuration in ``<node_name>.yml``.

Hostname section
----------------

This section defines the hostname of a node.

.. code-block:: yaml

    hostname: 'Leaf-01'

    <...snip...>


.. table::
    :widths: auto

    =============================================== ==========================================================================
    **Parameter**                                                            **Comments**
    =============================================== ==========================================================================
    **hostname** / :orange:`optional`               This option defines the remote device's hostname.
    =============================================== ==========================================================================

Global routing section
----------------------

In this section, IPv4/IPv6 related parameters for global routing table are defined.


.. table::
    :widths: auto

    =============================================== ==========================================================================
    **Parameter**                                                            **Comments**
    =============================================== ==========================================================================
    **routing** / :red:`mandatory`                  This option defines the global routing section.

    **ipv4_uni** / :red:`mandatory`                 This option enables the global IPv4 unicast routing on the device.

    **ipv6_uni** / :red:`mandatory`                 This option enables the global IPv6 unicast routing on the device.

    **ipv6_multi** / :red:`mandatory`               This option enables the global IPv4 multicast routing on the device.

    =============================================== ==========================================================================

Interface section
-----------------

In this section, the configurations of the interfaces are defined.

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
    **interfaces** / :red:`mandatory`               This option defines the interface section.

    **<interface_name>** / :red:`mandatory`         This option defines the interface name. For example: ``Loopback0`` or
                                                    ``GigabitEthernet1/0/1``

    **name** / :orange:`optional`                   This option defines the interface description.

    **ip_address** / :red:`mandatory`               This option defines the IPv4 address on the interface.

    **subnet_mask** / :red:`mandatory`              This option defines the subnet mask for the IPv4 address.

    **loopback** / :red:`mandatory`                 | This option tells whether the interface is loopback or not.

                                                    **Choices:**

                                                    * yes

                                                    * no

    **pim_enable** / :red:`mandatory`               | This option tells whether PIM must be enabled on the interface.

                                                    **Choices:**

                                                    * yes

                                                    * no
    =============================================== ==========================================================================

OSPF section
------------

This section defines the OSPF parameters.

By default, next OSPF configurations are applied:

* Interface network type - **point-to-point**

* OSPF process ID - **1**

* OSPF area number - **0**

OSPF **router-id** is a configurable parameter.

.. code-block:: yaml

    ospf:
      router_id: '172.16.255.3'

    <...snip...>

.. table::
    :widths: auto

    =============================================== ==========================================================================
    **Parameter**                                                            **Comments**
    =============================================== ==========================================================================
    **ospf** / :red:`mandatory`                     This option defines the OSPF section.
    
    **router_id** / :red:`mandatory`                This option defines the OSPF router-id.
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
    **pim** / :red:`mandatory`                      This option defines the PIM section.
    
    **rp_address** / :red:`mandatory`               This option defines the RP address.
    =============================================== ==========================================================================

MSDP section
------------

This section defines the MSDP parameters. Usually, MSDP is used for configuration RP redundancy in the underlay.

This section is optional.

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
    **msdp** / :red:`mandatory`                     This option defines the MSDP section.
    
    **<msdp_neighbor_id>** / :red:`mandatory`       This option defines ID for the MSDP peer. This number is not used in the 

                                                    switch configuration, just index number.

    **peer_ip** / :red: `mandatory`                 This option defines the MSDP peer's IPv4 address.

    **source_interface** / :red: `mandatory`        This option defines the IP address of the source interface which will be 
                                                    used as a source IP for the MSDP session.

    **remote_as** / :red: `mandatory`               This option is used for defining the BGP AS number of the MSDP
                                                    peer.                               
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

By default all access interfaces will be configured like trunks with all L2VNI vlans that are mentioned in ``group_vars/overlay_db.yml``

Trunk configuration
-------------------

Vlans to be assigned to an interace are taken from the following in increasing **order of priority (3 > 2 > 1).**

.. note::

    **Trunk configuration order of priority (3 > 2 > 1)**
 
1. ``vlans`` in ``group_vars/overlay_db.yml`` (for ``playbook_access_add_commit/preview.yml``) or ``access_intf_cli`` in ``host_vars/inc_vars/<hostname>.yml`` 

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

There is an assumption, that in ``group_vars/overlay_db.yml`` defined next vlans: :green:`101,102,201,202`

Example 1
^^^^^^^^^

Content of ``host_vars/access_intf/<hostname>.yml``

.. code-block:: yaml

    access_interfaces:
      trunks:
        - GigabitEthernet1/0/7
        - GigabitEthernet1/0/8

Vlans assigned after execution:

**GigabitEthernet1/0/7** - :green:`101,102,201,202` (from ``group_vars/overlay_db.yml`` or ``host_vars/inc_vars/<hostname>.yml``)

**GigabitEthernet1/0/8** - :green:`101,102,201,202` (from ``group_vars/overlay_db.yml`` or ``host_vars/inc_vars/<hostname>.yml``)

Example 2
^^^^^^^^^

Content of ``host_vars/access_intf/<hostname>.yml``

.. code-block:: yaml

    access_interfaces:
      access_vlan: 202
      access:
        - GigabitEthernet1/0/7
        - GigabitEthernet1/0/8

Vlans assigned after execution:

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

Vlans assigned after execution:

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

Vlans assigned after execution:

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

Vlans assigned after execution:

**GigabitEthernet1/0/5** - :green:`101,102,201,202` (from ``group_vars/overlay_db.yml`` or ``host_vars/inc_vars/<hostname>.yml``)

**GigabitEthernet1/0/6** - :green:`101,102,201`

**GigabitEthernet1/0/7** - :green:`101,102,201,202` (from ``group_vars/overlay_db.yml`` or ``host_vars/inc_vars/<hostname>.yml``)

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

Vlans assigned after execution:

**GigabitEthernet1/0/7** - :green:`101,102,201,202` (from ``group_vars/overlay_db.yml`` or ``host_vars/inc_vars/<hostname>.yml``)

**GigabitEthernet1/0/8** - :green:`201`
