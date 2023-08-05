# -*- coding: utf-8 -*-

class AppHortonworksInstance(object):
	"""
	Details about the Instance object specific to Hortonworks. The information
	presented here is obtained by interrogating the Hortonworks API. Backward
	compatibility object will not be ensured when the underlying Hortonworks API
	changes.
	"""

	def __init__(self):
		pass;


	"""
	The instance ID of the node
	"""
	instance_id = None;

	"""
	The instance label of the node
	"""
	instance_label = None;

	"""
	The status of the instance.
	"""
	instance_service_status = None;

	"""
	The subdomain of the node
	"""
	instance_hostname = None;

	"""
	The cluster UI url of the node
	"""
	instance_cluster_url = None;

	"""
	The health status of the node
	"""
	instance_health = None;

	"""
	The schema type
	"""
	type = None;
