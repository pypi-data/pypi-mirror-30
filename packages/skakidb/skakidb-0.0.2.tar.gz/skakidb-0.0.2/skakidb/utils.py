import distutils.dir_util
import os , io , json
import pprint
import requests
import jsonlines


BASE_DIR = None
CONFIG_FILE_PATH = None
END_POINT = None
INDEX_NAME = None



def create_skaki_db_config_file( wEndPoint , wIndexName ):
	global BASE_DIR
	global CONFIG_FILE_PATH
	distutils.dir_util.mkpath( BASE_DIR )
	wJSON = json.dumps( { "endpoint": wEndPoint , "index_name": wIndexName } )
	if os.path.isfile( CONFIG_FILE_PATH ):
		os.remove( CONFIG_FILE_PATH )
	with open( CONFIG_FILE_PATH , "a+" ) as f:
		f.write( wJSON )
		f.close()

#create_skaki_db_config_file( "https://search-fide-sugcghmp4dyqfgc6yj4xotumje.us-east-1.es.amazonaws.com:443" , "test-201804" )

def read_skaki_db_config_file():
	global CONFIG_FILE_PATH
	global END_POINT
	global INDEX_NAME
	d = None
	try:
		with open( CONFIG_FILE_PATH ) as json_data:
			d = json.load( json_data )
	except Exception as e:
		d = None
	
	if d == None:
		return False
	if d[ "endpoint" ] == None:
		return False
	if d[ "index_name" ] == None:
		return False
	if len( d[ "endpoint" ] ) < 3:
		return False
	if len( d[ "index_name" ] ) < 3:
		return False

	END_POINT = d[ "endpoint" ]
	INDEX_NAME = d[ "index_name" ]
	return True

#valid = read_skaki_db_config_file()
#print valid

def init():
	global BASE_DIR
	global CONFIG_FILE_PATH
	global END_POINT
	global INDEX_NAME
	BASE_DIR =  os.path.expanduser( "~" )
	BASE_DIR = os.path.join( BASE_DIR , ".config" , "skaki" )
	CONFIG_FILE_PATH = os.path.join( BASE_DIR , "elastic_search_db_config.json" )
	if read_skaki_db_config_file() == False:
		END_POINT = raw_input( "Enter Endpoint URL:\n" )
		INDEX_NAME = raw_input( "Enter Index Name:\n" )
		create_skaki_db_config_file( END_POINT , INDEX_NAME )

#init()

def delete_index():
	global END_POINT
	global INDEX_NAME
	wURL1 = END_POINT + "/test"
	wURL2 = END_POINT + "/" + INDEX_NAME
	
	r1 = requests.delete( wURL1 )
	try:
		r1 = r1.json()
		print ""
	except:
		print r1.stats_code
	
	r2 = requests.delete( wURL2 )
	try:
		r2 = r2.json()
	except:
		return r2.stats_code

	print ""
	pprint.pprint( r1 )
	print ""
	pprint.pprint( r2 )
	raw_input( "\nPress Enter to Continue\n" )

#delete_index()		

def create_index():
	global END_POINT
	global INDEX_NAME
	wURL = END_POINT + "/" + INDEX_NAME + "?pretty"
	wPayLoad = json.dumps({
		"mappings": {
			"rating": {
				"properties": {
					"fideid" : { "type" : "long" },
					"name" : { "type" : "text" },
					"country" : { "type" : "keyword" },
					"sex" : { "type" : "keyword" },
					"title" : { "type" : "keyword" },
					"w_title" : { "type" : "keyword" },
					"o_title" : { "type" : "keyword" },
					"foa_title" : { "type" : "keyword" },
					"rating" : { "type" : "short" },
					"games" : { "type" : "short" },
					"k" : { "type" : "short" },
					"birthday" : { "type" : "long" },
					"flag" : { "type" : "keyword" }					
				}
			}
		}
	})
	wHeaders = { "content-type": "application/json" , "Accept-Charset": "UTF-8" }
	r = requests.put( wURL , data=wPayLoad , headers=wHeaders )
	try:
		r = r.json()
		print ""		
		pprint.pprint( r )
		raw_input( "\nPress Enter to Continue\n" )
	except:
		return r.stats_code

#create_index()

def perform_index():
	global END_POINT
	global INDEX_NAME
	wURL = END_POINT + "/" + INDEX_NAME + "/rating/_bulk"
	wHeaders = { "content-type": "application/x-ndjson" , "Accept-Charset": "UTF-8" }

	wIndexFP = os.path.expanduser( "~" )
	wIndexFP = os.path.join( wIndexFP , "@201804-10000.ndjson" )
	if os.path.isfile( wIndexFP ):
		fileContent = None
		with open( wIndexFP , mode="rb" ) as file:
			fp = io.BytesIO( file.read() )
			reader = jsonlines.Reader( fp )
			fileContent = reader.read()
			reader.close()
			file.close()
		r = requests.put( wURL , data=fileContent , headers=wHeaders )
	else:
		r = requests.put( wURL , data="{}\n" , headers=wHeaders )

	try:
		r = r.json()
		print ""
		pprint.pprint( r )
		raw_input( "\nPress Enter to Continue\n" )
	except:
		return r.stats_code	

#perform_index()