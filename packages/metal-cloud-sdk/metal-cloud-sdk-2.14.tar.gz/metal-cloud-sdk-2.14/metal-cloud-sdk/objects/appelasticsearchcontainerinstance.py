# -*- coding: utf-8 -*-

class AppElasticsearchContainerInstance(object):
	"""
	Details about the Container object specific to Elasticsearch.
	"""

	def __init__(self):
		pass;


	"""
	The ID of the ContainerArray associated with the node.
	"""
	container_array_id = None;

	"""
	The label of the ContainerArray associated with the node.
	"""
	container_array_label = None;

	"""
	The schema type
	"""
	type = None;
