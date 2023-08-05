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

class Post(BaseObject):
	"""
	
	"""

	__config = {
		
		"3a8c7273-c7a2-4377-809f-1cb4b9681334" : OperationConfig("/posts", "create", [], []),
		
		"eb7168ed-235b-490e-8175-1abcefd97718" : OperationConfig("/posts/{id}", "delete", [], []),
		
		"8858d0d4-8543-41e6-97cd-08afb853d655" : OperationConfig("/posts", "list", [], []),
		
		"09973933-3236-498b-a506-06fa667ecfc6" : OperationConfig("/posts/{id}", "read", [], []),
		
		"0d3ff055-228a-4077-b04c-9365ff1bb8d1" : OperationConfig("/posts/{id}", "update", [], []),
		
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
		Creates object of type Post

		@param Dict mapObj, containing the required parameters to create a new object
		@return Post of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("3a8c7273-c7a2-4377-809f-1cb4b9681334", Post(mapObj))









	@classmethod
	def deleteById(cls,id,map=None):
		"""
		Delete object of type Post by id

		@param str id
		@return Post of the response of the deleted instance.
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

		return BaseObject.execute("eb7168ed-235b-490e-8175-1abcefd97718", Post(mapObj))

	def delete(self):
		"""
		Delete object of type Post

		@return Post of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("eb7168ed-235b-490e-8175-1abcefd97718", self)





	@classmethod
	def listByCriteria(cls,criteria=None):
		"""
		List objects of type Post

		@param Dict criteria
		@return Array of Post object matching the criteria.
		@raise ApiException: raised an exception from the response status
		"""

		if not criteria :
			return BaseObject.execute("8858d0d4-8543-41e6-97cd-08afb853d655", Post())
		else:
			return BaseObject.execute("8858d0d4-8543-41e6-97cd-08afb853d655", Post(criteria))








	@classmethod
	def read(cls,id,criteria=None):
		"""
		Returns objects of type Post by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of Post
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

		return BaseObject.execute("09973933-3236-498b-a506-06fa667ecfc6", Post(mapObj))



	def update(self):
		"""
		Updates an object of type Post

		@return Post object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("0d3ff055-228a-4077-b04c-9365ff1bb8d1", self)






