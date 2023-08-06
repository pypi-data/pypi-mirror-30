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
from mastercardtravelrecommender import ResourceConfig

class Consumer(BaseObject):
	"""
	
	"""

	__config = {
		
		"e490f2d4-d31e-4007-9732-bf6e0b2126e5" : OperationConfig("/labs/proxy/mtr/recommender/api/v1/consumer", "create", [], []),
		
		"a4c5180c-e917-4998-97aa-b443b1df88b2" : OperationConfig("/labs/proxy/mtr/recommender/api/v1/consumer/{consumerId}", "delete", [], []),
		
		"2b13e348-b130-4b7b-a9c5-43f5d8a7e089" : OperationConfig("/labs/proxy/mtr/recommender/api/v1/consumer/{consumerId}", "read", [], []),
		
		"f800e39f-fb2a-4e3a-bede-c5f87d80a7e9" : OperationConfig("/labs/proxy/mtr/recommender/api/v1/consumer", "query", [], ["max","offset"]),
		
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
		Creates object of type Consumer

		@param Dict mapObj, containing the required parameters to create a new object
		@return Consumer of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("e490f2d4-d31e-4007-9732-bf6e0b2126e5", Consumer(mapObj))









	@classmethod
	def deleteById(cls,id,map=None):
		"""
		Delete object of type Consumer by id

		@param str id
		@return Consumer of the response of the deleted instance.
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

		return BaseObject.execute("a4c5180c-e917-4998-97aa-b443b1df88b2", Consumer(mapObj))

	def delete(self):
		"""
		Delete object of type Consumer

		@return Consumer of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("a4c5180c-e917-4998-97aa-b443b1df88b2", self)







	@classmethod
	def read(cls,id,criteria=None):
		"""
		Returns objects of type Consumer by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of Consumer
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

		return BaseObject.execute("2b13e348-b130-4b7b-a9c5-43f5d8a7e089", Consumer(mapObj))







	@classmethod
	def query(cls,criteria):
		"""
		Query objects of type Consumer by id and optional criteria
		@param type criteria
		@return Consumer object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("f800e39f-fb2a-4e3a-bede-c5f87d80a7e9", Consumer(criteria))


