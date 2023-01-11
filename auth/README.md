# General description #

In this directory there are playbooks for provisioning AUTH (Authentication of AAA ,DOT1x and access template configs) for Campus EVPN Fabric.

# Topology #

Below you can find a topology which is used in the automation scenario

<img width="737" alt="ansible_lab_topology" src="https://user-images.githubusercontent.com/99259970/155182099-7e5d98f4-8e4e-4b01-96a8-30b9badc5be2.png">

# Quick start #

For the quick start with AUTH provisioning next steps have to be executed:
 
## Step 1 ## 

On this step Underlay is provisioned from any of the DAG or L2vni folders.

### Step 1a ###
 
Edit ``inventory.yml`` and set proper name and management ip address.

```
all:
  children:
    leaf:
      hosts:
        Leaf-01:
          ansible_host: 10.1.1.1

<...snip...>
```
Detailed information could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_dag.html#inventory-yml)

### Step 1b ###

Edit ``group_vars/all.yml`` and set proper login and password

```
ansible_connection: ansible.netcommon.network_cli
ansible_network_os: cisco.ios.ios
ansible_python_interpreter: "python"
ansible_user: cisco
ansible_ssh_pass: cisco123
```

``ansible_user`` must have privildge level 15. Example of the configuration is below

```
username cisco privilege 15 password 0 cisco123
```

If enable password should be used, check the [Enable Mode](https://docs.ansible.com/ansible/latest/network/user_guide/platform_ios.html) documentation.

Detailed information could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_dag.html#all-yml)

### Step 1c ###

Edit ``host_vars/node_vars/<hostname>.yml`` and set required parameters for underlay

```
hostname: 'Leaf-01'

routing:
 ipv4_uni: 'yes'
 ipv6_uni: 'yes'
 ipv4_multi: 'yes'

interfaces:

  Loopback0:
    name: 'Routing Loopback'
    ip_address: '172.16.255.3'
    subnet_mask: '255.255.255.255'
    loopback: 'yes'
    pim_enable: 'no'
    
<...snip...>
```

Detailed information could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_dag.html#host-vars).

### Step 1d ###

:pushpin: This step is optional but recommended.

Run the underlay preview playbook. This playbook generates the configuration for preview without deploying it to the network devices.

```
ansible-playbook -i inventory.yml playbook_underlay_preview.yml
```
The files ``<hostname>-underlay.txt`` could be found in the directory ``cat9k-evpn-ansible/dag/preview_files``

```
#cat preview_files/Leaf-01-underlay.txt

! hostname block 
hostname Leaf-01

! global routing block 
ip routing
ipv6 unicast-routing
ip multicast-routing

<...snip...>
```

### Step 1e ###

Run the underlay provisioning playbook. It is possible to see in terminal logs all the changes - [how to do this](https://cat9k-evpn-ansible.readthedocs.io/en/latest/notes.html#cli-commands-logging).

```
ansible-playbook -i inventory.yml playbook_underlay_commit.yml
```

Detailed information could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/playbooks_dag.html#underlay-provisioning).

## Step 2 ##

On this step Overlay is provisioned.

### Step 2a ###

Edit the ``group_vars/overlay_db.yml`` file and set desired parameters for EVPN overlay.

```
l2vpn_global:
    replication_type: 'static'
    router_id: 'Loopback1'
    default_gw: 'yes'

<...skip...>
```

Detailed information could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_dag.html#overlay-db-yml)

### Step 2b ###

:pushpin: **This step is optional but recommended**

Run the yml config validation playbook. This playbook checks for issues in the file ``group_vars/overlay_db.yml``

```
ansible-playbook -i inventory.yml playbook_yml_validation.yml
```

### Step 2c ###

:pushpin: **This step is optional but recommended**

Run the network precheck playbook. It will check if the activated license and current version. Also underlay reachibility between "nve loopback" is checked.

```
ansible-playbook -i inventory.yml playbook_overlay_precheck.yml 
```

### Step 2d ###

:pushpin: **This step is optional but recommended**

Run the overlay preview playbook. This playbook generates the configuration for preview without deploying it to the network devices.

```
ansible-playbook -i inventory.yml playbook_overlay_preview.yml
```

The files ``<hostname>-overlay.txt`` could be found in the directory ``cat9k-evpn-ansible/dag/preview_files``

```
#cat preview_files/Leaf-01-overlay.txt 
 
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

<...snip...>
```

### Step 2e ###

Run the overlay provisioning playbook. It is possible to see in terminal logs all the changes - [how to do this](https://cat9k-evpn-ansible.readthedocs.io/en/latest/notes.html#cli-commands-logging).

```
ansible-playbook -i inventory.yml playbook_overlay_commit.yml
```

Detailed information could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/playbooks_dag.html#overlay-provisioning)

## Step 3 ##

On this step Access Interfaces are provisioned.

### Step 3a ###

Edit the ``host_vars/access_intf/<nodename>.yml`` files and set desired parameters for access interfaces.

```
leaf_auth_type : DefaultWiredDot1xClosedAuth  
access_interfaces:
  trunks:
    - GigabitEthernet1/0/7
    - GigabitEthernet1/0/8
  access:
   - GigabitEthernet1/0/4:
       auth_type : DefaultWiredDot1xOpenAuth
       access_vlan: 201
   - GigabitEthernet1/0/5:
       access_vlan: 201
   - GigabitEthernet1/0/6:
       auth_type : DefaultWiredDot1xLowImpactAuth
       access_vlan: 201
```

### Step 3b ###

:pushpin: **This step is optional but recommended**

Run the access interfaces preview playbook. This playbook generates the configuration for preview without deploying it to the network devices.

```
ansible-playbook -i inventory.yml playbook_access_add_preview.yml
```

The files ``<hostname>-add-intf.txt`` could be found in the directory ``cat9k-evpn-ansible/dag/preview_files``

```
#cat preview_files/Leaf-01-add-intf.txt

! access interface block 
interface GigabitEthernet1/0/8
switchport trunk allowed vlan 101,102,201,202
switchport mode trunk
interface GigabitEthernet1/0/7
switchport trunk allowed vlan 101,102,201,202

<...snip...>
```
### Step 3c ###

Run the Access Interfaces provisioning playbook. It is possible to see in terminal logs all the changes - [how to do this](https://cat9k-evpn-ansible.readthedocs.io/en/latest/notes.html#cli-commands-logging).

```
ansible-playbook -i inventory.yml playbook_access_add_commit.yml
```

Detailed information could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/playbooks_dag.html#access-interfaces-provisioning)

## Step 4 ##

On this step AAA configs and policy maps are provisioned.

### Step 4a ###

:pushpin: **This step is optional but recommended**

Run the aaa auth preview playbook. This playbook generates the configuration for preview without deploying it to the network devices.

```
ansible-playbook -i inventory.yml playbook_aaa_auth_preview.yml
```

The files ``{{inventory_hostname}}-auth.txt`` could be found in the directory ``cat9k-evpn-ansible/auth/preview_files``

```
#cat preview_files/Leaf-01-auth.txt

! aaa configs block
!
enable password 0 cisco123
aaa authentication login default local
aaa authentication login dnac-cts-list group dnac-client-radius-group local
aaa authentication login VTY_authen group dnac-network-radius-group local
aaa authentication dot1x default group dnac-client-radius-group
aaa authorization exec default local
aaa authorization exec VTY_author group dnac-network-radius-group local if-authenticated
aaa authorization network default group dnac-client-radius-group
aaa authorization network dnac-cts-list group dnac-client-radius-group
aaa accounting exec default start-stop group dnac-network-radius-group
aaa accounting Identity default start-stop group dnac-client-radius-group
username user1 privilege 15 password 0 Cisco123
!
aaa server radius dynamic-author
client 172.19.71.10 server-key cisco
!
!

<...snip...>
```

### Step 4b ###

Run the aaa auth provisioning playbook. It is possible to see in terminal logs all the changes - [how to do this](https://cat9k-evpn-ansible.readthedocs.io/en/latest/notes.html#cli-commands-logging).

```
ansible-playbook -i inventory.yml playbook_aaa_auth_commit.yml
```

Detailed information could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/playbooks_dag.html#access-interfaces-provisioning)

## Step 5 ##

On this step source template to the access interfaces are provisioned.

### Step 5a ###

:pushpin: **This step is optional but recommended**

Run the access auth preview playbook. This playbook generates to which interfaces configs needs to be pushed under host_vars/auth_vars/{{ inventory_hostname }}.yml

```
ansible-playbook -vvv -i ~/testbed/inventory-2-leafs-2-spines.yml --extra-vars "access_dir=dag" playbook_access_auth_generate.yml
```

The files ``{{ inventory_hostname }}.yml`` could be found in the directory ``cat9k-evpn-ansible/auth/host_vars/auth_vars``

```
#cat auth/host_vars/auth_vars/Leaf-01.yml

auth_type:
  GigabitEthernet1/0/4: DefaultWiredDot1xOpenAuth
  GigabitEthernet1/0/5: DefaultWiredDot1xClosedAuth
  GigabitEthernet1/0/6: DefaultWiredDot1xLowImpactAuth

<...snip...>
```

### Step 5b ###

:pushpin: **This step is optional but recommended**

Run the access auth generate playbook. This playbook generates the configuration for preview without deploying it to the network devices.

```
ansible-playbook -vvv -i ~/testbed/inventory-2-leafs-2-spines.yml --extra-vars "access_dir=dag" playbook_access_auth_preview.yml
```

The files ``{{inventory_hostname}}-access_auth.txt`` could be found in the directory ``cat9k-evpn-ansible/auth/preview_files``

```
#cat preview_files/Leaf-01-access_auth.txt

! access auth configs block
!
interface GigabitEthernet1/0/4
dot1x timeout tx-period 7
dot1x max-reauth-req 3
source template DefaultWiredDot1xOpenAuth
!
interface GigabitEthernet1/0/5
dot1x timeout tx-period 7
dot1x max-reauth-req 3
source template DefaultWiredDot1xClosedAuth
!
interface GigabitEthernet1/0/6
dot1x timeout tx-period 7
dot1x max-reauth-req 3
source template DefaultWiredDot1xLowImpactAuth

<...snip...>
```

### Step 5c ###

Run the Access auth provisioning playbook. It is possible to see in terminal logs all the changes - [how to do this](https://cat9k-evpn-ansible.readthedocs.io/en/latest/notes.html#cli-commands-logging).

```
ansible-playbook -vvv -i ~/testbed/inventory-2-leafs-2-spines.yml --extra-vars "access_dir=dag" playbook_access_auth_commit.yml
```

Detailed information could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/playbooks_dag.html#access-interfaces-provisioning)

# Playbook usage #

## Initial provisioning ##

<img width="1215" alt="day0" src="https://user-images.githubusercontent.com/99259970/176646266-1ad9773c-fe88-4beb-bda0-9ed3b6585913.png">

## Incremental provisioning ##

<img width="1220" alt="day1" src="https://user-images.githubusercontent.com/99259970/176646640-c05b3b5a-d756-4118-a960-ebcef83a9a39.png">

# Playbooks description #

## AAA auth provisioning ##

**playbook_aaa_auth_preview.yml**

* the playbook generates config for AAA and policy-maps to be added for preview

```
ansible-playbook -i inventory.yml playbook_aaa_auth_preview.yml
```

**playbook_aaa_auth_commit.yml**

* the playbook is used for provisioning configuration of AAA and policy-maps to the remote devices

```
ansible-playbook -i inventory.yml playbook_aaa_auth_commit.yml
```

**playbook_delete_aaa_auth_preview.yml**

* the playbook generates config for AAA and policy-maps to be deleted for preview

```
ansible-playbook -i inventory.yml playbook_delete_aaa_auth_preview.yml
```

**playbook_delete_access_auth_commit.yml**

* the playbook is used for unprovisioning configuration of AAA and policy-maps to the remote devices

```
ansible-playbook -i inventory.yml playbook_delete_aaa_auth_commit.yml
```

## Access auth provisioning ##

**playbook_access_auth_generate.yml**

* the playbook checks ``group_vars/auth_db.yml`` and current configuration on the switch

and generates internal configuration files in the directory ``host_vars/auth_vars/``

```
ansible-playbook -vvv -i ~/testbed/inventory-2-leafs-2-spines.yml --extra-vars "access_dir=dag" playbook_access_auth_generate.yml
```

**playbook_access_auth_preview.yml**

* the playbook is used for provisioning template configuration of access interfaces to the remote devices

```
ansible-playbook -vvv -i ~/testbed/inventory-2-leafs-2-spines.yml --extra-vars "access_dir=dag" playbook_access_auth_preview.yml
```

**playbook_access_auth_commit.yml**

* the playbook is used for provisioning template configuration of access interfaces to the remote devices

```
ansible-playbook -vvv -i ~/testbed/inventory-2-leafs-2-spines.yml --extra-vars "access_dir=dag" playbook_access_auth_commit.yml
```

**playbook_delete_access_auth_generate.yml**

* the playbook checks ``group_vars/auth_db.yml`` and current configuration on the switch

and generates internal configuration files in the directory ``host_vars/auth_vars/`` which are to be unprovisioned

```
ansible-playbook -vvv -i ~/testbed/inventory-2-leafs-2-spines.yml --extra-vars "access_dir=dag" playbook_delete_access_auth_generate.yml
```

**playbook_delete_access_auth_preview.yml**

* the playbook is used for unprovisioning template configuration of access interfaces to the remote devices

```
ansible-playbook -vvv -i ~/testbed/inventory-2-leafs-2-spines.yml --extra-vars "access_dir=dag" playbook_delete_access_auth_preview.yml
```

**playbook_delete_access_auth_commit.yml**

* the playbook is used for unprovisioning template configuration of access interfaces to the remote devices

```
ansible-playbook -vvv -i ~/testbed/inventory-2-leafs-2-spines.yml --extra-vars "access_dir=dag" playbook_delete_access_auth_commit.yml
```

## Special playbooks ##

**playbook_cleanup.yml:**

* the playbook reverts the current configuration back to initial default_config.txt

**playbook_output.yml:**

* the playbook is used for collecting outputs from the remote devices

# Documentation #

Detailed documentation could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_dag.html)
