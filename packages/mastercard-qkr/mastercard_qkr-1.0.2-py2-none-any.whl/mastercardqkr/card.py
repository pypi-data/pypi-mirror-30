#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2016 MasterCard International Incorporated
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list of
# conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of
# conditions and the following disclaimer in the documentation and/or other materials
# provided with the distribution.
# Neither the name of the MasterCard International Incorporated nor the names of its
# contributors may be used to endorse or promote products derived from this software
# without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#


from __future__ import absolute_import
from mastercardapicore import BaseObject
from mastercardapicore import RequestMap
from mastercardapicore import OperationConfig
from mastercardapicore import OperationMetadata
from mastercardqkr import ResourceConfig

class Card(BaseObject):
	"""
	
	"""

	__config = {
		
		"5991d077-663d-487b-b6a7-acf9a119198b" : OperationConfig("/labs/proxy/qkr2/internal/api2/card", "create", ["X-Auth-Token"], []),
		
		"6105101d-419f-4101-8fed-afda2262147f" : OperationConfig("/labs/proxy/qkr2/internal/api2/card/{id}", "delete", ["X-Auth-Token"], []),
		
		"b6f1a25b-6a02-4677-b8da-8799a78997da" : OperationConfig("/labs/proxy/qkr2/internal/api2/card", "query", ["X-Auth-Token"], []),
		
		"dd21b3ce-e8c7-41e4-9af7-b34cecb9ccd7" : OperationConfig("/labs/proxy/qkr2/internal/api2/card/{id}", "read", ["X-Auth-Token"], []),
		
		"6350d642-d595-4038-bcbc-48e47a527c55" : OperationConfig("/labs/proxy/qkr2/internal/api2/card/{id}", "update", ["X-Auth-Token"], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUID)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())


	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type Card

		@param Dict mapObj, containing the required parameters to create a new object
		@return Card of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("5991d077-663d-487b-b6a7-acf9a119198b", Card(mapObj))









	@classmethod
	def deleteById(cls,id,map=None):
		"""
		Delete object of type Card by id

		@param str id
		@return Card of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""

		mapObj =  RequestMap()
		if id:
			mapObj.set("id", id)

		if map:
			if (isinstance(map,RequestMap)):
				mapObj.setAll(map.getObject())
			else:
				mapObj.setAll(map)

		return BaseObject.execute("6105101d-419f-4101-8fed-afda2262147f", Card(mapObj))

	def delete(self):
		"""
		Delete object of type Card

		@return Card of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("6105101d-419f-4101-8fed-afda2262147f", self)








	@classmethod
	def query(cls,criteria):
		"""
		Query objects of type Card by id and optional criteria
		@param type criteria
		@return Card object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("b6f1a25b-6a02-4677-b8da-8799a78997da", Card(criteria))





	@classmethod
	def read(cls,id,criteria=None):
		"""
		Returns objects of type Card by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of Card
		@raise ApiException: raised an exception from the response status
		"""
		mapObj =  RequestMap()
		if id:
			mapObj.set("id", id)

		if criteria:
			if (isinstance(criteria,RequestMap)):
				mapObj.setAll(criteria.getObject())
			else:
				mapObj.setAll(criteria)

		return BaseObject.execute("dd21b3ce-e8c7-41e4-9af7-b34cecb9ccd7", Card(mapObj))



	def update(self):
		"""
		Updates an object of type Card

		@return Card object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("6350d642-d595-4038-bcbc-48e47a527c55", self)






