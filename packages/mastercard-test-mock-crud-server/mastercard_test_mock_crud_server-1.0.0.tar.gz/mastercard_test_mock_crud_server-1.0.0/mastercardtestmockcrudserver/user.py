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
from mastercardtestmockcrudserver import ResourceConfig

class User(BaseObject):
	"""
	
	"""

	__config = {
		
		"57c14be9-5be5-403a-ad4d-69acea09bb03" : OperationConfig("/users", "create", [], []),
		
		"c99e4e17-0cb6-460f-b074-7f9bc02b8e76" : OperationConfig("/users/{id}", "delete", [], []),
		
		"09a03ec9-a6a6-4c6d-8d6e-0b6b079068d8" : OperationConfig("/users", "list", [], []),
		
		"9bddaf05-7ac0-4983-b297-1917d8b1b6cf" : OperationConfig("/users/{id}", "read", [], []),
		
		"a57bd692-a8f7-4bf3-8ee6-b7290c6c1fec" : OperationConfig("/users/{id}", "update", [], []),
		
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
		Creates object of type User

		@param Dict mapObj, containing the required parameters to create a new object
		@return User of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("57c14be9-5be5-403a-ad4d-69acea09bb03", User(mapObj))









	@classmethod
	def deleteById(cls,id,map=None):
		"""
		Delete object of type User by id

		@param str id
		@return User of the response of the deleted instance.
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

		return BaseObject.execute("c99e4e17-0cb6-460f-b074-7f9bc02b8e76", User(mapObj))

	def delete(self):
		"""
		Delete object of type User

		@return User of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("c99e4e17-0cb6-460f-b074-7f9bc02b8e76", self)





	@classmethod
	def listByCriteria(cls,criteria=None):
		"""
		List objects of type User

		@param Dict criteria
		@return Array of User object matching the criteria.
		@raise ApiException: raised an exception from the response status
		"""

		if not criteria :
			return BaseObject.execute("09a03ec9-a6a6-4c6d-8d6e-0b6b079068d8", User())
		else:
			return BaseObject.execute("09a03ec9-a6a6-4c6d-8d6e-0b6b079068d8", User(criteria))








	@classmethod
	def read(cls,id,criteria=None):
		"""
		Returns objects of type User by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of User
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

		return BaseObject.execute("9bddaf05-7ac0-4983-b297-1917d8b1b6cf", User(mapObj))



	def update(self):
		"""
		Updates an object of type User

		@return User object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("a57bd692-a8f7-4bf3-8ee6-b7290c6c1fec", self)






