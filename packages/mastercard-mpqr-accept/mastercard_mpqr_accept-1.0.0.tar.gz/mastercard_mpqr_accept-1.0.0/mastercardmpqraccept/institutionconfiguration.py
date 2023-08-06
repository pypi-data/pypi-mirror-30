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
from mastercardmpqraccept import ResourceConfig

class InstitutionConfiguration(BaseObject):
	"""
	
	"""

	__config = {
		
		"6009e45f-92a4-4021-8ac5-da3cbe6e6733" : OperationConfig("/labs/proxy/mpqr-accept/v1/api/bank/configuration", "query", [], []),
		
		"85efa9ba-fbca-40ff-b296-bd18a61924ea" : OperationConfig("/labs/proxy/mpqr-accept/v1/api/bank/configuration/publish", "update", [], []),
		
		"1163c432-41e8-425a-a76f-03d2e82362ab" : OperationConfig("/labs/proxy/mpqr-accept/v1/api/bank/configuration", "update", [], []),
		
		"ad3cc1b5-726d-47e8-8f73-368e277ca3cc" : OperationConfig("/labs/proxy/mpqr-accept/v1/api/bank/configuration/terminate", "update", [], []),
		
		"3d168683-6738-4a95-b7e3-f4184493f30a" : OperationConfig("/labs/proxy/mpqr-accept/v1/api/bank/configuration/unpublish", "update", [], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUID)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())







	@classmethod
	def read(cls,criteria):
		"""
		Query objects of type InstitutionConfiguration by id and optional criteria
		@param type criteria
		@return InstitutionConfiguration object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("6009e45f-92a4-4021-8ac5-da3cbe6e6733", InstitutionConfiguration(criteria))


	def publish(self):
		"""
		Updates an object of type InstitutionConfiguration

		@return InstitutionConfiguration object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("85efa9ba-fbca-40ff-b296-bd18a61924ea", self)






	def update(self):
		"""
		Updates an object of type InstitutionConfiguration

		@return InstitutionConfiguration object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("1163c432-41e8-425a-a76f-03d2e82362ab", self)






	def terminate(self):
		"""
		Updates an object of type InstitutionConfiguration

		@return InstitutionConfiguration object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("ad3cc1b5-726d-47e8-8f73-368e277ca3cc", self)






	def unpublish(self):
		"""
		Updates an object of type InstitutionConfiguration

		@return InstitutionConfiguration object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("3d168683-6738-4a95-b7e3-f4184493f30a", self)






