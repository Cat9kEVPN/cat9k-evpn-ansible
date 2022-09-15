# General description #

In this directory there are playbooks for provisioning L2VNI (L2 Overlay) for Campus EVPN Fabric.

# Topology #

Below you can find a topology which is used in the automation scenario

<img width="737" alt="ansible_lab_topology" src="https://user-images.githubusercontent.com/99259970/155182099-7e5d98f4-8e4e-4b01-96a8-30b9badc5be2.png">

# Quick start #

For the quick start with DAG provisioning next steps have to be executed:
 
## Step 1 ## 

On this step Underaly is provisioned.

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
Detailed information could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_l2vni.html#inventory-yml)

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

Detailed information could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_l2vni.html#all-yml)

### Step 1c ###

Edit ``host_vars/<hostname>.yml`` and set required parameters for underlay

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

Detailed information could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_l2vni.html#host-vars).

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

Detailed information could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/playbooks_l2vni.html#underlay-provisioning).

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

Detailed information could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_l2vni.html#overlay-db-yml)

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
 
! vlan block
vlan 101
name Access_VLAN_101
vlan 102
name Access_VLAN_102
vlan 103
name Access_VLAN_103
vlan 104
name Access_VLAN_104
vlan 105
name Access_VLAN_105

! l2vpn evpn global block
l2vpn evpn
replication-type static
router-id Loopback1

<...snip...>
```

### Step 2e ###

Run the overlay provisioning playbook. It is possible to see in terminal logs all the changes - [how to do this](https://cat9k-evpn-ansible.readthedocs.io/en/latest/notes.html#cli-commands-logging).

```
ansible-playbook -i inventory.yml playbook_overlay_commit.yml
```

Detailed information could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/playbooks_l2vni.html#overlay-provisioning)

## Step 3 ##

On this step Access Interfaces are provisioned.

### Step 3a ###

Edit the ``host_vars/access_intf/<nodename>.yml`` files and set desired parameters for access interfaces.

```
access_interfaces:
  trunks:
    - GigabitEthernet1/0/6
  access:
    - GigabitEthernet1/0/7
  access_vlan: 102
```

### Step 3b ###

:pushpin: **This step is optional but recommended**

Run the access interfaces preview playbook. This playbook generates the configuration for preview without deploying it to the network devices.

```
ansible-playbook -i inventory.yml playbook_access_add_preview.yml
```

The files ``<hostname>-add-intf.txt`` could be found in the directory ``cat9k-evpn-ansible/l2vni/preview_files``

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

Detailed information could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/playbooks_l2vni.html#access-interfaces-provisioning)

# Playbook usage #

## Initial provisioning ##

<img width="1215" alt="day0" src="https://user-images.githubusercontent.com/99259970/176646266-1ad9773c-fe88-4beb-bda0-9ed3b6585913.png">

## Incremental provisioning ##

<img width="1220" alt="day1" src="https://user-images.githubusercontent.com/99259970/176646640-c05b3b5a-d756-4118-a960-ebcef83a9a39.png">

# Playbooks description #

## Underlay provisioning ##

**playbook_underlay_preview.yml:**

* the playbook generates the config in text format for underlay for preview

**playbook_underlay_commit.yml:**

* the playbook is used for provisioning configuration for the underlay to the remote devices

## Overlay provisioning ##

**playbook_yml_validation.yml:**

* the playbook checks file ``group_vars/overlay_db.yml`` for possible issues

**playbook_overlay_precheck.yml:**

* the playbook checks IOS-XE version and license level for compatibility with EVPN feature on Cat9k. Additionaly the playbook checks underaly reachibility between NVE loopbacks 

**playbook_overlay_preview.yml:**

* the playbook generates config in text format for overlay for preview

**playbook_overlay_commit.yml:**

* the playbook is used for provisioning configuration for the overlay to the remote devices

## Incremental overlay adding ##

**playbook_overlay_incremental_generate.yml**

* the playbook is checking ``overlay_db.yml``, current configuration on the switch and generate internal configuration files in

directory ``host_vars/inc_vars/``

⚠️ This playbook is used internally and should not be run separately by user.

**playbook_overlay_incremental_preview.yml**

* the playbook is used to generate list of commands which have to be entered on remote device based on

inputs from ``host_vars/inc_vars/<hostname>.yml``. Output could be checked in ``preview_files/<hostname>-inc.txt``

**playbook_overlay_incremental_commit.yml**

* the playbook is used for provisioning incremental add changes to the remote devices

## Incremental overlay deleting ##

**playbook_overlay_delete_generate.yml:**

* the playbook checks ``group_vars/overlay_db.yml, group_vars/delete_vars.yml`` and current configuration on the switch

and generates internal configuration files in the directory ``host_vars/delete_vars/``

⚠️ This playbook is used internally and should not be run separately by user.

**playbook_overlay_delete_preview.yml:**

* the playbook generates list of commands which have to be entered on the remote device based on

inputs from ``playbook_overlay_delete_preview.yml``

**playbook_overlay_delete_commit.yml:**

* the playbook is used for provisioning incremental delete changes to the remote devices


## Access interface provisioning ##

**playbook_access_add_preview.yml:**

* the playbook generates config for access interfaces for preview

**playbook_access_add_commit.yml:**

* the playbook is used for provisioning configuration for the access interfaces to the remote devices

**playbook_access_incremental_preview.yml:**

* the playbook generates config for incremental changes for the access interfaces for preview

**playbook_access_incremental_commit.yml:**

* the playbook is used for provisioning configuration for incremental changes for the access interfaces to the remote devices

## Special playbooks ##

**playbook_cleanup.yml:**

* the playbook reverts the current configuration back to initial default_config.txt

**playbook_output.yml:**

* the playbook is used for collecting outputs from the remote devices

# Documentation #

Detailed documentation could be found [here](https://cat9k-evpn-ansible.readthedocs.io/en/latest/input_l2vni.html)
