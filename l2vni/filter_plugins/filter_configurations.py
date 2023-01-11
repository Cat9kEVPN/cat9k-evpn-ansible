class FilterModule(object):

  def filters(self):
    return {
      'filter_configured_interfaces' : self.filter_configured_interfaces,
      'filter_configured_neighbors' : self.filter_configured_neighbors,
      'get_mvpns_afs' : self.get_mvpns_afs,
      'get_vrf_list' : self.get_vrf_list,
      'filter_unconfigured_vrfs': self.filter_unconfigured_vrfs,
      'get_dag_data_from_db': self.get_dag_data_from_db,
      'filter_dict_for_vrfs': self.filter_dict_for_vrfs,
      'get_residual_mvpns': self.get_residual_mvpns,
      'get_spine_mvpns': self.get_spine_mvpns

    }

  def filter_configured_interfaces(self, interfaces_to_filter, interfaces_on_device):
    filtered_intf_dict = {}

    for intf in interfaces_to_filter:
      if (intf not in interfaces_on_device) or \
        (intf in interfaces_on_device and \
          ('ipv4' not in interfaces_on_device[intf] and 'ipv6' not in interfaces_on_device[intf]) ):

        filtered_intf_dict[intf] = interfaces_to_filter[intf]

    return filtered_intf_dict

  def filter_configured_neighbors(self, neighbors_to_filter, bgp_on_device, as_number):
    filtered_neighbors_dict = {}

    neighbors_on_device = list(bgp_on_device[as_number]['address_family']['l2vpn evpn']['address_family_neighbor'])

    for neighbor in neighbors_to_filter:
      if neighbor not in neighbors_on_device:

        filtered_neighbors_dict[neighbor] = neighbors_to_filter[neighbor]

    return filtered_neighbors_dict

  def get_mvpns_afs(self, vrf_list, dag_dict):
    mvpn_afs_list = []

    for vrf in dag_dict['dag']:
      if vrf in vrf_list:
        mvpn_afs_list = mvpn_afs_list + list( dag_dict['dag'][vrf]['afs'].keys() )

    mvpn_afs_list = list(set(mvpn_afs_list))
    return mvpn_afs_list

  def get_vrf_list(self, vrf_from_input_file, vrf_from_db):

    vrf_from_db = list(vrf_from_db)
    vrf_from_input_file = list(vrf_from_input_file)
    
    if 'all' in vrf_from_input_file:
      return vrf_from_db
    else:
      return list(set(vrf_from_input_file).intersection(set(vrf_from_db)))

  def filter_unconfigured_vrfs(self, dhcp_dict, vrf_list):

    dag_filtered = {}
    
    for dag in dhcp_dict:
      if dag in vrf_list:
        dag_filtered[dag] = dhcp_dict[dag]

    return dag_filtered

  def get_dag_data_from_db(self, dag_from_create_vars, dag_data_from_db):

    dag_filtered = {}
    
    if 'all' in dag_from_create_vars:
      dag_filtered = dag_data_from_db
    else:
      for dag in dag_from_create_vars:
        if dag in dag_data_from_db:
          dag_filtered[dag] = dag_data_from_db[dag]
        else:
          if 'all' in dag_data_from_db:
            dag_filtered[dag] = dag_data_from_db['all']

    return dag_filtered

  def filter_dict_for_vrfs(self, unfiltered_dict, vrf_list):

    filtered_dict = []
    
    for key in unfiltered_dict:
      if unfiltered_dict[key]['vrf'] in vrf_list: filtered_dict.append(key)

    return filtered_dict

  def get_residual_mvpns(self, selected_vrfs, db_vrfs, overlay_dict):

    undel_vrfs_afs = set()
    vrf_afs = set()
  
    for vrf in db_vrfs:
      vrf_afs = vrf_afs.union(db_vrfs[vrf]['afs'])

      if vrf not in selected_vrfs:

        for af in db_vrfs[vrf]['afs']:
          try:
            vrf_af_dict = overlay_dict[vrf]['address_family'][af]
          except KeyError:
            vrf_af_dict = []

          if 'mdt_auto_discovery' in vrf_af_dict: undel_vrfs_afs = undel_vrfs_afs.union({af})

    return [af+ ' mvpn' for af in list(vrf_afs - undel_vrfs_afs)]

  def get_spine_mvpns(self, leaf_group, hostvars_dict):

    vrf_mvpn_ref = hostvars_dict[leaf_group[0]]['vrf_mvpn']

    for leaf in leaf_group:
      vrf_mvpn_ref = list(set(hostvars_dict[leaf]['vrf_mvpn']).intersection(set(vrf_mvpn_ref)))

      if not vrf_mvpn_ref: break

    return vrf_mvpn_ref
