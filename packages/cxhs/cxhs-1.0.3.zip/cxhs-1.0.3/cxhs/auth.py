import hmac
import requests
import scram

from scram import *

class SS2Auth(requests.auth.AuthBase):
	def __init__(self, username, password, debug=False):
		self.username = username
                self.password = password
		self.debug = debug

        def __call__(self,r):
		print type(r)
		url = r.url
	
		urlsplit = url.split('/')
		host = urlsplit[2]
		proj = urlsplit[4]
		urlauth = "http://%s/auth/%s/api?%s" % (host,proj,self.username)
		rr = requests.get(urlauth)
		if rr.status_code == 404:
			print "Not Found - Try Auth 3.0"
			return r
		
		# good response:
		# 'username:paul\nuserSalt:LUovBt/WrOrmwK0faY9SuGBUg7fiSvmmr13nHMBGK8o=\nrealm:demo\nnonce:31c2cbe80c5272ce4ea3f80940569e2d\nonAuthEnabled:false'
		
		resp = rr.content.split('\n')
		salt = resp[1].split(':')[-1]
		realm = resp[2].split(':')[-1]
		nonce = resp[3].split(':')[-1]
		onAuth = resp[4].split(':')[-1]
		if self.debug:
			print "salt  :",salt
			print "realm :",realm
			print "nonce :",nonce
			print "onAuth:",onAuth
		
		message = "%s:%s" % (self.username,salt)
		signed_pass = self.password.encode('utf-8')
                hashed = hmac.new(signed_pass, message, sha1).digest()
		hmac_final = standard_b64encode(hashed).strip()
		digest_msg = "%s:%s" % (hmac_final.decode('utf-8'),nonce)
		digest = sha1()
		digest.update(digest_msg)
		digest_final = standard_b64encode((digest.digest()))

		if self.debug:
			print "hmac  :",hmac_final
			print "digest:",digest_final

		data = "nonce:%s\ndigest:%s\n" % (nonce,digest_final)
		if self.debug:
			print "data:\n",data
		rr = requests.post(urlauth,data=data,headers={"Content-Type":"text/plain; charset=utf-8","Content-Length":str(len(data))})
		cookie = rr.content.split(":")[-1]
		if self.debug:
			print rr.status_code,rr.content
			print cookie
		r.headers["Cookie"] = cookie
		#r.cookies[rr.content.split(":")[-1].split("=")[0]] = rr.content.split(":")[-1].split("=")[-1]
		return r
	
		
class SS3Auth(requests.auth.AuthBase):
	def __init__(self, username, password, debug=False):
		self.username = username
		self.password = password
		self.debug = debug

	def __call__(self,r):
		url = r.url
		ssScram = False
		ssHmac = False
		# implement authentication
	        aa = "Authorization"

        	# = = = = = HELLO = = = = =
	        msg = "HELLO username=%s" % scram.base64_no_padding(self.username)
		if self.debug: print msg
        	resp = requests.get(url,headers={aa:msg})
		if self.debug: print resp.headers
		# get WWW-Authenticate header
	        server_auth = resp.headers.get("WWW-Authenticate",None)
		if self.debug: print "'%s'" % server_auth

	        # = = = = = FIRST MESSAGE = = = = =
        	# Extract from response
		if 'scram ' in server_auth:
			ssScram = True
		if 'hmac ' in server_auth:
			ssHmac = True

		final_msg = ""
		if ssScram:
	        	auth_response = server_auth.split(',')
        		handshake_token = scram.regex_after_equal(auth_response[0])
	        	algorithm_raw = scram.regex_after_equal(auth_response[1])
	        	algorithm_name = algorithm_raw.replace("-","").lower()
		        algorithm = None
        		if algorithm_name == 'sha256':
                		algorithm = sha256
		        elif algorithm_name == 'sha2':
        		        algorithm = sha1
	        	else:	
				print "Algorithm '%s' not supported" % algorithm_raw
	        	        return r
			if self.debug: print 'AA:',algorithm_name,algorithm
	        	# Calculate next request
		        client_nonce = scram.get_nonce()[:32]
		        first_message = "n=%s,r=%s" % (self.username,client_nonce)
	        	msg = "SCRAM handshakeToken=%s, data=%s" % (handshake_token,scram.base64_no_padding(first_message))
			if self.debug: print msg
		        resp = requests.get(url,headers={aa:msg})
        		server_auth = resp.headers.get("WWW-Authenticate",None)

		        # = = = = = SECOND MESSAGE = = = = =
        		# Extract from response
        		auth_response = server_auth.split(',')
		        server_data = scram.regex_after_equal(auth_response[0])
        		missing_pad = len(server_data) % 4
	        	if missing_pad != 0:
        	        	server_data += '='* (4 - missing_pad)
		        server_first_msg = scram.b64decode(server_data).decode()
        		message_parts = server_first_msg.split(',')
	        	server_nonce = scram.regex_after_equal(message_parts[0])
	        	server_salt = scram.regex_after_equal(message_parts[1])
		        if isinstance(server_salt, unicode):
                		server_salt = server_salt.encode()
	        	server_iterations = scram.regex_after_equal(message_parts[2])
		        if not server_nonce.startswith(client_nonce):
        		        print "Invalid Nonce\n- - - - - - - - - -\nC:",client_nonce,"\nS:",server_nonce
	        	# Calculate next request
		        client_final_no_proof = "c=%s,r=%s" % (scram.standard_b64encode(b'n,,').decode(),server_nonce)
        		auth_message = "%s,%s,%s" % (first_message,server_first_msg,client_final_no_proof)
	        	salted_pass = scram.salted_password(server_salt, server_iterations, algorithm_name, self.password)
        		key = "Client Key".encode('UTF-8')
        		client_key = hmac.new(unhexlify(salted_pass),"Client Key".encode('UTF-8'),algorithm).hexdigest()
	        	stored_key = scram._hash_sha256(unhexlify(client_key), algorithm)
        		client_sig = hmac.new(unhexlify(stored_key),auth_message.encode('utf-8'),algorithm).hexdigest()
        		client_proof = scram._xor(client_key,client_sig).replace("L","")
		        if len(client_proof) % 4 != 0:
        		        client_proof = '0'* (4 - (len(client_proof) % 4)) + client_proof
        		client_proof_encode = b2a_base64(unhexlify(client_proof)).decode()

	        	client_final = client_final_no_proof + ",p=" + client_proof_encode
        		client_final_b64 = scram.base64_no_padding(client_final)
        		final_msg = "scram handshakeToken=%s, data=%s" % (handshake_token, client_final_b64)
			if self.debug: print final_msg
		        resp = requests.get(url,headers={aa:final_msg})
			if self.debug: print "Status:",resp.status_code,"\n",resp.headers

                        # AUTH TOKEN
                        if resp.status_code == 200:
                                auth_info = resp.headers['Authentication-Info']
                                auth_parts = auth_info.split(",")
                                auth_token = scram.regex_after_equal(auth_parts[0])
                                auth_data = scram.regex_after_equal(auth_parts[1])
                                cookie = resp.headers['Set-Cookie']
                                msg = "BEARER authToken=%s" % auth_token
                                r.headers['Authorization'] = msg

                        # BEARER authToken=xxxyyyzzz
		elif ssHmac:
			auth_response = server_auth.split()
			server_nonce = scram.regex_after_equal(auth_response[2])
			server_salt = scram.regex_after_equal(auth_response[3])
			message = "%s:%s" % (self.username,server_salt)
			password = self.password.encode('utf-8')
			hashed = hmac.new(password, message, sha1).digest()
			hmac_final = standard_b64encode(hashed).strip()
			digest_msg = "%s:%s" % (hmac_final.decode('utf-8'),nonce)
			digest = sha1()
			digest.update(digest_msg)
			digest_final = standard_b64encode((digest.digest()))
			
			
		return r
