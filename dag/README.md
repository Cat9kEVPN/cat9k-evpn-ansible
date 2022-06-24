# General description #

In this directory there are playbooks for provisioning DAG (Distributed Anycast Gateway) for Campus EVPN Fabric.

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

## Incremental overlay deleting ##

**playbook_overlay_delete_generate.yml:**

* the playbook checks ``group_vars/overlay_db.yml, group_vars/delete_vars.yml`` and current configuration on the switch

and generates internal configuration files in the directory ``host_vars/delete_vars/``

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

