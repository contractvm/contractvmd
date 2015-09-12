# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import os
import logging
import subprocess
import uuid
from lxml import etree

from .. import config

logger = logging.getLogger(config.APP_NAME)


CONTRACT_SCHEMA = """<?xml version="1.0" encoding="UTF-8" ?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">

	<!-- LIST OF ATTRIBUTES -->
	
	<xs:attribute name="id">
	  <xs:simpleType>
	    <xs:restriction base="xs:string">
	      <xs:pattern value="[a-z]+"/>
	    </xs:restriction>
	  </xs:simpleType>
	</xs:attribute>
	
	<xs:attribute name="context">
	  <xs:simpleType>
	    <xs:restriction base="xs:string">
	      <xs:pattern value="[a-z]+"/>
	    </xs:restriction>
	  </xs:simpleType>
	</xs:attribute>
	
	<xs:attribute name="name">
	  <xs:simpleType>
	    <xs:restriction base="xs:string">
	      <xs:pattern value="[a-z]+"/>
	    </xs:restriction>
	  </xs:simpleType>
	</xs:attribute>
	
	<xs:attribute name="op">
    	<xs:simpleType>
			<xs:restriction base="xs:string">
				<xs:enumeration value="less" />
				<xs:enumeration value="great" />
			</xs:restriction>
		</xs:simpleType>
	</xs:attribute>
	
	<xs:attribute name="value" type="xs:nonNegativeInteger"/>



	<!-- LIST OF BASIC TAGS -->
	
	<!-- Contract (root element) -->
	<xs:element name="contract">
		<xs:complexType>
			<xs:choice>
				<xs:element ref="intaction" />
				<xs:element ref="extaction" />
				<xs:element ref="intchoice" />
				<xs:element ref="extchoice" />
				<xs:element ref="sequence" />
				<xs:element ref="rec"/>
			</xs:choice>
			<xs:attribute ref="context"/>
		</xs:complexType>
	</xs:element>
	
	<!-- Internal action -->
    <xs:element name="intaction">
    	<xs:complexType>
    		<xs:sequence>
				<xs:element ref="guards" minOccurs="0"/>
				<xs:element ref="resets" minOccurs="0"/>
			</xs:sequence>
			<xs:attribute ref="id" use="required"/>
    	</xs:complexType>
    </xs:element>
    
    <!-- External action -->
    <xs:element name="extaction">
    	<xs:complexType>
    		<xs:sequence>
				<xs:element ref="guards" minOccurs="0"/>
				<xs:element ref="resets" minOccurs="0"/>
			</xs:sequence>	
			<xs:attribute ref="id" use="required"/>
    	</xs:complexType>
    </xs:element>
    
    <!-- Guard container  -->
    <xs:element name="guards">
    	<xs:complexType>
    		<xs:choice>
				<xs:element ref="guard" minOccurs="0" maxOccurs="unbounded"/>
			</xs:choice>
    	</xs:complexType>
	</xs:element>
	
	<!-- Reset container -->
	<xs:element name="resets">
    	<xs:complexType>
    		<xs:choice>
				<xs:element ref="reset" minOccurs="0" maxOccurs="unbounded"/>
			</xs:choice>
    	</xs:complexType>
	</xs:element>
	
	<!-- Single guard -->
	<xs:element name="guard">
		<xs:complexType>
			<xs:attribute ref="id" use="required"/>
			<xs:attribute ref="op" use="required"/>
			<xs:attribute ref="value" use="required"/>
		</xs:complexType>
	</xs:element>
	
	<!-- Single reset -->
	<xs:element name="reset">
		<xs:complexType>
			<xs:attribute ref="id" use="required"/>
		</xs:complexType>
	</xs:element>
	
	<!-- Sequence -->
	<xs:element name="sequence">
		<xs:complexType>
			<xs:choice>
				<xs:sequence>
					<xs:element ref="intaction" />
					<xs:choice>
						<xs:sequence>
				    		<xs:choice minOccurs="1" maxOccurs="unbounded">
				    			<xs:element ref="intaction"/>
								<xs:element ref="extaction"/>
				    		</xs:choice>
				    		<xs:choice minOccurs="0" maxOccurs="1">
				    			<xs:element ref="intchoice" />
								<xs:element ref="extchoice" />
								<xs:element ref="rec"/>
								<xs:element ref="call"/>
				    		</xs:choice>
			    		</xs:sequence>
						<xs:sequence>
				    		<xs:choice>
				    			<xs:element ref="intchoice" />
								<xs:element ref="extchoice" />
								<xs:element ref="rec"/>
								<xs:element ref="call"/>
				    		</xs:choice>
			    		</xs:sequence>
			    	</xs:choice>
		    	</xs:sequence>
		    	<xs:sequence>
					<xs:element ref="extaction" />
					<xs:choice>
						<xs:sequence>
				    		<xs:choice minOccurs="1" maxOccurs="unbounded">
				    			<xs:element ref="intaction"/>
								<xs:element ref="extaction"/>
				    		</xs:choice>
				    		<xs:choice minOccurs="0" maxOccurs="1">
				    			<xs:element ref="intchoice" />
								<xs:element ref="extchoice" />
								<xs:element ref="rec"/>
								<xs:element ref="call"/>
				    		</xs:choice>
			    		</xs:sequence>
						<xs:sequence>
				    		<xs:choice>
				    			<xs:element ref="intchoice" />
								<xs:element ref="extchoice" />
								<xs:element ref="rec"/>
								<xs:element ref="call"/>
				    		</xs:choice>
			    		</xs:sequence>
			    	</xs:choice>
	    		</xs:sequence>
	    	</xs:choice>
		</xs:complexType>
	</xs:element>
	
    
    <!-- Internal choice -->
    <xs:element name="intchoice">
		<xs:complexType>
		 	<xs:choice minOccurs="2" maxOccurs="unbounded">
				<xs:element ref="intaction"/>
				<xs:element name="sequence" type="intSequence" />
		 	</xs:choice>
		</xs:complexType>
	</xs:element>
	
	<!-- External choice -->
    <xs:element name="extchoice">
		<xs:complexType>
		 	<xs:choice minOccurs="2" maxOccurs="unbounded">
				<xs:element ref="extaction"/>
				<xs:element name="sequence" type="extSequence" />
		 	</xs:choice>
		</xs:complexType>
	</xs:element>
	
	<!-- Recursive sequence -->
	<xs:element name="rec">
		<xs:complexType>
			<xs:choice>
				<xs:sequence>
					<xs:choice maxOccurs="unbounded">
						<xs:element ref="intaction"/>
						<xs:element ref="extaction"/>
					</xs:choice>
					<xs:choice minOccurs="0">
						<xs:element ref="intchoice" />
						<xs:element ref="extchoice" />
						<xs:element ref="call"/>
						<xs:element ref="rec"/>						
					</xs:choice>
				</xs:sequence>
				<xs:choice minOccurs="0">
					<xs:element ref="intchoice" />
					<xs:element ref="extchoice" />
					<xs:element ref="rec"/>						
				</xs:choice>
			</xs:choice>
			<xs:attribute ref="name" use="required"/>
		</xs:complexType>
	</xs:element>
	
	<!-- Recursive call -->
	<xs:element name="call">
		<xs:complexType>
			<xs:attribute ref="name" use="required"/>
		</xs:complexType>
	</xs:element>
	
	
	
	<!-- LIST OF COMPLEX TYPES -->
	
	<!-- Sequence starting with internal action -->
	<xs:complexType name="intSequence">
		<xs:sequence>
			<xs:element ref="intaction" />
			<xs:choice>
				<xs:sequence>
		    		<xs:choice minOccurs="1" maxOccurs="unbounded">
		    			<xs:element ref="intaction"/>
						<xs:element ref="extaction"/>
		    		</xs:choice>
		    		<xs:choice minOccurs="0" maxOccurs="1">
		    			<xs:element ref="intchoice" />
						<xs:element ref="extchoice" />
						<xs:element ref="rec"/>
						<xs:element ref="call"/>
		    		</xs:choice>
	    		</xs:sequence>
				<xs:sequence>
		    		<xs:choice>
		    			<xs:element ref="intchoice" />
						<xs:element ref="extchoice" />
						<xs:element ref="rec"/>
						<xs:element ref="call"/>
		    		</xs:choice>
	    		</xs:sequence>
	    	</xs:choice>
    	</xs:sequence>
	</xs:complexType>
	
	<!-- Sequence starting with external action -->
	<xs:complexType name="extSequence">
		<xs:sequence>
			<xs:element ref="extaction" />
			<xs:choice>
				<xs:sequence>
		    		<xs:choice minOccurs="1" maxOccurs="unbounded">
		    			<xs:element ref="intaction"/>
						<xs:element ref="extaction"/>
		    		</xs:choice>
		    		<xs:choice minOccurs="0" maxOccurs="1">
		    			<xs:element ref="intchoice" />
						<xs:element ref="extchoice" />
						<xs:element ref="rec"/>
						<xs:element ref="call"/>
		    		</xs:choice>
	    		</xs:sequence>
				<xs:sequence>
		    		<xs:choice>
		    			<xs:element ref="intchoice" />
						<xs:element ref="extchoice" />
						<xs:element ref="rec"/>
						<xs:element ref="call"/>
		    		</xs:choice>
	    		</xs:sequence>
	    	</xs:choice>
    	</xs:sequence>
	</xs:complexType>

</xs:schema>"""

TEST_COMPLIANCE = """A[] not deadlock"""

class Tibet:
	class BadXMLException (Exception):
		pass

	class NoOutputException (Exception):
		pass

	class TimeoutException (Exception):
		pass

	class StdErrorException (Exception):
		def __init__ (self, stderr):
			self.message = stderr


	TIBET_CMD = 'ctu'
	UPPAAL_CMD = '/usr/local/uppaal/bin-Linux/verifyta' #verifyta'
	TEMP_BASE_DIR = config.TEMP_DIR
	TIMEOUT = 10

	CONTRACT_SCHEMA = etree.XMLSchema (etree.XML (CONTRACT_SCHEMA.encode ('ascii')))


	# Exec the tibet binary, return the stdout
	def exec (params, in_data = None, binary = TIBET_CMD):
		proc = subprocess.Popen([binary] + params, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
		try:
			if in_data != None:
				data = ''
				for x in in_data:
					data += (x + '\n')
					
				data = data.encode ('ascii')
			else:
				data = None

			outs, errs = proc.communicate (input=data, timeout=Tibet.TIMEOUT)
		except:
			proc.kill()
			raise Tibet.TimeoutException ()

		return [outs.decode () if outs != None else None, errs.decode () if errs != None else None]




	## Session handling

	# Get the list of possible actions for a player in a session state
	def sessionPossibleActions (raw_state):
		sesfile = Tibet._writeTempSessionFile (raw_state)

		pa = {'0': [], '1': []}

		for i in range (0,2):
			(out,err) = Tibet.exec (['-pa', str (i), sesfile])

			out = '<actionlist>' + (out.split ('<actionlist>')[1])
			parser = etree.XMLParser(remove_blank_text=True)
			elem = etree.XML(out, parser=parser)
	
			for child in elem:
				name = child.get ('name')
				time = int (child.get ('time'))

				pa[str (i)].append ({'name': name, 'time': time})

		return pa
		

	# Fire an anction in the session, return update session
	def sessionDo (raw_state, action, player, time_delay):
		# player (A|B), act, delay, fn, fn', check=0
		sesfile = Tibet._writeTempSessionFile (raw_state)
		nsesfile = Tibet._uniqfilename ()

		Tibet.exec (['-step', str (player), str (action), str (time_delay), sesfile, nsesfile, str (0)])
		raw_state = Tibet._readTempSessionFile (nsesfile)
		
		return raw_state


	# Create the inital state of the session, return initial session
	def startSession (contract1xml, contract2xml):
		sesfile = Tibet._uniqfilename ()
		(out,err) = Tibet.exec (['-start', sesfile], [contract1xml, contract2xml])

		raw_state = Tibet._readTempSessionFile (sesfile)

		return raw_state


	def sessionDelay (raw_state, delay_unit):
		nsesfile = Tibet._uniqfilename ()
		sesfile = Tibet._writeTempSessionFile (raw_state)
		Tibet.exec (['-delay', str (delay_unit), sesfile, nsesfile])
		os.remove (sesfile)

		raw_state = Tibet._readTempSessionFile (nsesfile)

		return raw_state


	def sessionDutyState (raw_state):
		sesfile = Tibet._writeTempSessionFile (raw_state)
		duty0 = Tibet.exec (['-id', '0', sesfile])[0]
		duty1 = Tibet.exec (['-id', '1', sesfile])[0]
		os.remove (sesfile)

		return {'0': True if (duty0.find ('yes') != -1) else False, '1': True if (duty1.find ('yes') != -1) else False}

	
	def sessionCulpableState (raw_state):
		sesfile = Tibet._writeTempSessionFile (raw_state)
		culp0 = Tibet.exec (['-ic', '0', sesfile])[0]
		culp1 = Tibet.exec (['-ic', '1', sesfile])[0]
		os.remove (sesfile)

		return {'0': True if (culp0.find ('yes') != -1) else False, '1': True if (culp1.find ('yes') != -1) else False}


	# Return true if the session is ended
	def sessionEndState (raw_state):
		sesfile = Tibet._writeTempSessionFile (raw_state)
		ie = Tibet.exec (['-ie', sesfile])[0]
		os.remove (sesfile)

		if ie.find ('yes') != -1:
			return True
		elif ie.find ('no') != -1:
			return False
		else:
			raise Tibet.NoOutputException ()


		

	## Data transformations and validation

	# Return True if contractxml starts with an internal action
	def _dutyOnFuseOfContract (root):
		for child in root:
			if child.tag == 'intaction':
				return True
			elif child.tag == 'extaction':
				return False
			else:
				return Tibet._dutyOnFuseOfContract (child)

	def dutyOnFuseOfContract (contractxml):
		parser = etree.XMLParser (schema=Tibet.CONTRACT_SCHEMA)
		try:
			root = etree.fromstring (contractxml, parser)
			return Tibet._dutyOnFuseOfContract (root)
		except:
			raise Tibet.BadXMLException ()		

	def kindOfContract (contractxml):
		if Tibet._validateXMLContract (contractxml):
			out = Tibet.exec (['-dk'], [contractxml])[0]
			#if out.find ('true') and out.find ('false') == -1:
			#	return True
			#	return [True, None]
			if out.find ('false'):
				return False
			else:
				return True
			#	return [False, out.split ('|| ')[1]]
			#else:		
			#	raise Tibet.NoOutputException ()
		else:
			raise Tibet.BadXMLException ()

	def translateContract (contract):
		return Tibet._stripXML (Tibet.exec (['-s'], [contract])[0]).decode ()

	def validateContract (contractxml):
		if Tibet._validateXMLContract (contractxml):
			return (Tibet.exec (['-v'], [contractxml])[0].find ('Contract is valid') != -1)
		else:
			raise Tibet.BadXMLException ()

	def dualContract (contractxml):
		if Tibet._validateXMLContract (contractxml):
			return Tibet._stripXML (Tibet.translateContract (Tibet.exec (['-dd'], [contractxml])[0])).decode ()
		else:
			raise Tibet.BadXMLException ()


	def checkContractsCompliance (contract1xml, contract2xml):
		if not Tibet._validateXMLContract (contract1xml) or not Tibet._validateXMLContract (contract2xml):
			raise Tibet.BadXMLException ()

		# Create the automata
		automata = Tibet._createAutomata (contract1xml, contract2xml)

		# Save automata on temp file
		fn = Tibet._uniqfilename ()
		f = open (fn, 'w')
		f.write (automata)
		f.close ()		

		fc = Tibet._uniqfilename ()
		f = open (fc, 'w')
		f.write (TEST_COMPLIANCE)
		f.close ()		


		# Tests automata with Uppaal software
		[out, err] = Tibet.exec ([fn, fc], in_data=None, binary=Tibet.UPPAAL_CMD)

		# Remove file
		os.remove (fn)

		# Check response
		if out.find ("is satisfied") != -1:
			return True
		elif out.find ("is NOT satisfied") != -1:
			return False
		else:
			raise Tibet.NoOutputException ()



	## Private functions

	def _validateXMLContract (contractxml):
		parser = etree.XMLParser (schema=Tibet.CONTRACT_SCHEMA)
		try:
			root = etree.fromstring (contractxml, parser)
			return True
		except:
			return False


	def _readTempSessionFile (fn):
		f = open (fn, 'rb')
		state = f.read ()
		f.close ()
		os.remove (fn)
		return state

	def _writeTempSessionFile (raw):
		fn = Tibet._uniqfilename ()
		f = open (fn, 'wb')
		f.write (raw)
		f.close ()
		return fn	
	
	# Strip xml removing spaces and returns
	def _stripXML (xmldata):
		parser = etree.XMLParser(remove_blank_text=True, schema=Tibet.CONTRACT_SCHEMA)
		elem = etree.XML(xmldata, parser=parser)
		return etree.tostring(elem)
	
	# Create an automata starting from two contracts
	def _createAutomata (contract1xml, contract2xml):
		# Creates XML automata with Ocaml CTU
		automata = Tibet.exec ([], [contract1xml, contract2xml])
		automata = '<?xml' + automata[0].split ('<?xml')[1]
		return automata


	def _uniqfilename (ext='xml'):
		return Tibet.TEMP_BASE_DIR + 'tst-' + str (uuid.uuid4()) + '.' + ext


