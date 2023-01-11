# This directory contains cisco verified designs for L2VNI, DAG, TRM, and DHCP configs
#

# Config examples description #

**dag_v4_trm_anycastrp:**
```
    Description: 
        This case covers v4 DAG with mcast replication, access interface, DHCP, and v4 TRM with anycast RP.

    Input files: 
        Under config_examples/dag_v4_trm_anycastrp folder, update the following,
            group_vars/overlay_db.yml,
            group_vars/trm_overlay_db.yml,
            group_vars/dhcp_db.yml,
            host_vars/node_vars/<hostname>.yml,
            host_vars/access_intf/<hostname>.yml

    CLI: 
        preview: ansible-playbook -vvv playbook_preview.yml --extra-vars "design=dag_v4_trm_anycastrp"
        commit: ansible-playbook -vvv playbook_commit.yml --extra-vars "design=dag_v4_trm_anycastrp"
```

**dag_v4_trm_internalrp:**
```
    Description: 
        This case covers v4 DAG with mcast replication, access interface, DHCP, and v4 TRM with internal RP.

    Input files:
        Under config_examples/dag_v4_trm_internalrp folder, update the following,
            group_vars/overlay_db.yml,
            group_vars/trm_overlay_db.yml,
            group_vars/dhcp_db.yml,
            host_vars/node_vars/<inventory>.yml,
            host_vars/access_intf/<inventory>.yml

    CLI: 
        preview: ansible-playbook -vvv playbook_preview.yml --extra-vars "design=dag_v4v6_trm_internalrp"
        commit: ansible-playbook -vvv playbook_commit.yml --extra-vars "design=dag_v4v6_trm_internalrp"
```

**dag_v4v6_trm_anycastrp:**
```
    Description: 
        This case covers v4v6 DAG with mcast replication, access interface, DHCP, and v4v6 TRM with anycast RP.

    Input files:
        Under config_examples/dag_v4v6_trm_anycastrp folder, update the following,
            group_vars/overlay_db.yml,
            group_vars/trm_overlay_db.yml,
            group_vars/dhcp_db.yml,
            host_vars/node_vars/<inventory>.yml,
            host_vars/access_intf/<inventory>.yml

    CLI: 
        preview: ansible-playbook -vvv playbook_preview.yml --extra-vars "design=dag_v4v6_trm_anycastrp"
        commit: ansible-playbook -vvv playbook_commit.yml --extra-vars "design=dag_v4v6_trm_anycastrp"
```

**dag_v4v6_trm_internalrp:**
```
    Description: 
        This case covers v4v6 DAG with mcast replication, access interface, DHCP, and v4v6 TRM with internal RP.

    Input files:
        Under config_examples/dag_v4v6_trm_internalrp folder, update the following,
            group_vars/overlay_db.yml,
            group_vars/trm_overlay_db.yml,
            group_vars/dhcp_db.yml,
            host_vars/node_vars/<inventory>.yml,
            host_vars/access_intf/<inventory>.yml

    CLI: 
        preview: ansible-playbook -vvv playbook_preview.yml --extra-vars "design=dag_v4v6_trm_internalrp"
        commit: ansible-playbook -vvv playbook_commit.yml --extra-vars "design=dag_v4v6_trm_internalrp"
```

**dag_unicast_replication_type_underlay_mcast:**
```
    Description:
        This case covers v4v6 DAG with mcast replication, access interface, and DHCP.

    Input files:
        Under config_examples/dag_unicast_replication_type_underlay_mcast folder, update the following,
            group_vars/overlay_db.yml,
            group_vars/dhcp_db.yml,
            host_vars/node_vars/<inventory>.yml,
            host_vars/access_intf/<inventory>.yml

    CLI: 
        preview: ansible-playbook -vvv playbook_preview.yml --extra-vars "design=dag_unicast_replication_type_underlay_mcast"
        commit: ansible-playbook -vvv playbook_commit.yml --extra-vars "design=dag_unicast_replication_type_underlay_mcast"
```

**dag_unicast_replication_type_ingress:**
```
    Description: 
        This case covers v4v6 DAG with ingress replication, access interface, and DHCP.

    Input files:
        Under config_examples/dag_unicast_replication_type_ingress folder, update the following,
            group_vars/overlay_db.yml,
            group_vars/dhcp_db.yml,
            host_vars/node_vars/<inventory>.yml,
            host_vars/access_intf/<inventory>.yml

    CLI: 
        preview: ansible-playbook -vvv playbook_preview.yml --extra-vars "design=dag_unicast_replication_type_ingress"
        commit: ansible-playbook -vvv playbook_commit.yml --extra-vars "design=dag_unicast_replication_type_ingress"
```

**dag_dot1x_auth:**
```
    Description: 
        This case covers DAG, access interface, DOT1x, and auth.

    Input files:
        Under config_examples/dag_dot1x_auth folder, update the following,
            group_vars/overlay_db.yml,
            group_vars/auth_db.yml,
            host_vars/node_vars/<inventory>.yml,
            host_vars/access_intf/<inventory>.yml

    CLI: 
        preview: ansible-playbook -vvv playbook_preview.yml --extra-vars "design=dag_dot1x_auth"
        commit: ansible-playbook -vvv playbook_commit.yml --extra-vars "design=dag_dot1x_auth"
```

**l2vni_dot1x_auth:**
```
    Description: 
        This case covers L2VNI, access interface, DOT1x, and auth.

    Input files:
        Under config_examples/l2vni_dot1x_auth, update the following,
            group_vars/overlay_db.yml,
            group_vars/auth_db.yml,
            host_vars/node_vars/<inventory>.yml,
            host_vars/access_intf/<inventory>.yml

    CLI: 
        preview: ansible-playbook -vvv playbook_preview.yml --extra-vars "design=l2vni_dot1x_auth"
        commit: ansible-playbook -vvv playbook_commit.yml --extra-vars "design=l2vni_dot1x_auth"
```
