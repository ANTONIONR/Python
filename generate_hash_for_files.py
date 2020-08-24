

"""

   this script validates the integrity of all the files it analyzes at any given time. To do this, 
   it generates three hashes on the file it analyzes. At a time after that generation of the hashes, 
   it can be launched at any time to see if a file has undergone any type of modification, it will 
   have a different hash from the original


"""

###    * * *    G L O B A L    V A R I A B L E S    * * *

trace =  True                          # Flag activate debuger messages
Work_Directory = 'd:\work'             # Directory for download file and anlyzed it

# coordenates file, machine,port,usuario,pass,remote_home

machine     = []
port        = []
user        = []
password    = []
remote_home = []

# Totalizers

Total_servers     = 0     
Total_files       = 0
Total_directories = 0



### Packges imported

import paramiko
import os
import datetime
import hashlib

import time



### Debug funcion, set up by debug flag 
def debug(mensaje):

    cadena = 'DBG [' + str (datetime.datetime.now().time()) + ']'
    print (cadena + '    ' + mensaje)


def show_totalizers():    
	print ('============================================================================')
	print ('Total servers analyzed        : '+ str (Total_servers))
	print ('Total directories analyzed    : '+ str (Total_directories))
	print ('Total files analyzed          : '+ str (Total_files))
	print ('============================================================================')


def generate_integrity_hash(file_to_hash):
	#if trace: debug ('  zzzz  ')
	BLOCKSIZE = 65536

	hasher_md5 = hashlib.md5()         # generate hash with algorithm md5, most simpler, less cpu needed
	hasher_sha = hashlib.sha1()        # generate hash with algorithm sha1, the choice in between 
	hasher_sha256 = hashlib.sha256()   # generate hash with algorithm sha256, most complex, more cpu needed
	
	with open (file_to_hash,'rb') as open_file:
		content = open_file.read (BLOCKSIZE)
		while len(content) > 0:
			hasher_md5.update(content)
			hasher_sha.update(content)
			hasher_sha256.update(content)
			content = open_file.read (BLOCKSIZE) 

	#if trace: debug ('*** HASHs FOR *** '+file_to_hash)
	#print ('Hash (MD5)      : ' + hasher_md5.hexdigest())
	#print ('Hash (SHA1)     : ' + hasher_sha.hexdigest())
	#print ('Hash (SHA256)   : ' + hasher_sha256.hexdigest())	

	return hasher_md5.hexdigest(), hasher_sha.hexdigest(), hasher_sha256.hexdigest()


def get_files_and_directories():
    file_list = sftp.listdir('.')
        
    files = []
    directories = []
    filesSizes = []
    filesLastModified = []
    
    for file_name in file_list:

        try:
            stat = str(sftp.lstat(file_name))    
            if stat[0] == 'd':
                # Total_directories = Total_directories+1
                directories.append(file_name)    
            elif stat[0] == '-':
                # Total_files = Total_files+1
                tamano =  sftp.stat(file_name)      
                files.append(file_name)
                filesSizes.append(tamano.st_size)      
                filesLastModified.append(tamano.st_mtime)      
        except PermissionError:
            print('Skipping '+file_name+' due to permissions')    
            
    return files,directories,filesSizes,filesLastModified


def directory(remote_dir):
  global Total_files
	global Total_directories
	#if trace: debug ('  xxxxx  ')
	#if trace: debug ('  xxxxx  '+remote_dir)
	# es recursivo a si mismo
	sftp.chdir(remote_dir)
	Total_directories += 1
	if trace: debug ('in directory '+remote_dir)
    
	files,directories,filesSizes,filesLastModified=get_files_and_directories()

	j=0   # use for read the size and last modified date	
	for f in files:
		#print('Parsing file '+f)
		Total_files = Total_files+1		
		try:
			sftp.get(f, f)
			try:				
				hash_md5,hash_sha,hash_sha256=generate_integrity_hash(Work_Directory+'\\'+f)
				print (' '+hash_md5+' '+hash_sha+' '+hash_sha256+' '+f+' ')  #+filesSizes[j] ) #  +' '+filesLastModified[j])
			except:
				if trace: debug ('ERR procesing '+remote_dir+'/'+f)
			os.remove(f)
		except PermissionError:
			print('Skipping '+f+' due to permissions')
		except OSError:
			print('Skipping '+f+' Mayme format name is no support')   # Some name file, like including semicolon not are support in Windows.
		j=j+1
        
	for d in directories:
		newremote = remote_dir+'/'+d   #+'/'
		directory(newremote)


	return 0


def load_servers():
	i = 0

  #
  # I have a metadata file with machines, ports, user, password. In this case this medatada is not
  # encryted but it is a bad idea. Please protect you sensible data, permissions and/or encryptation 
  # is a good idea
  #
	with open("C:\ANAVARRO\WORK\PYTHON\connection_repository.txt", "r") as filestream:
         for line in filestream:
             currentline = line.split(";")
             if len (currentline) <= 3: continue  # Skip blank lines                         
             if currentline[0][0] == '#': continue # Skip commnent lines 

             machine.append      (currentline[0])            
             port.append         (int (currentline[1]))  
             user.append         (currentline[2])
             password.append     (currentline[3])
             remote_home.append  (currentline[4].strip())  # para eliminar el EOL
             


             if trace:
                 debug ('--- START OF REGISTRY ---')
                 debug ('    maquina : ' + machine [i])
                 debug ('    puerto  : ' + str (port  [i]))
                 debug ('    usuario : ' + user [i])
                 debug ('    pass    : ' + password [i])
                 debug ('    RH      : ' + remote_home [i])
                 debug ('--- END OF REGISTRY ---')
             i = i+1

	return (i-1)	


# # #    M A I N    # # #	

#if trace: debug ('into Main')

# Setup the work directory
os.chdir(Work_Directory)

# Load the servers into a vector and get the number of registries
NumberOfRegistry = load_servers()
i = 0

while i <= NumberOfRegistry:
    Total_servers += 1	
    transport = paramiko.Transport((machine [i], port [i]))
    transport.connect(username = user[i], password = password [i])
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
    except:
    	if trace: debug ('Fail openning ftp connection to '+machine[i])

    
    directory(remote_home [i])
    
    sftp.close()
    transport.close()
    i = i+1


if trace: debug ('finishing Main')
show_totalizers()




