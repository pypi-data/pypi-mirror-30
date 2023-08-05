
# coding: utf-8

import requests, urllib3, json, time, scp, paramiko, io, os
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


public_key_default = set()
private_key = ''
username_default = os.environ.get('fyre_username')
api_key_default = os.environ.get('fyre_api_key')
if os.environ.get('public_key'): public_key_default.add(os.environ.get('public_key'))
if os.environ.get('private_key'): private_key = os.environ.get('private_key')


if private_key == '':
    import cryptography
    key = cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key(
        public_exponent=65537,
        key_size=1024,
        backend=cryptography.hazmat.backends.default_backend())

    public_key_default.add( key.public_key().public_bytes(
        encoding=cryptography.hazmat.primitives.serialization.Encoding.OpenSSH,
        format=cryptography.hazmat.primitives.serialization.PublicFormat.OpenSSH).decode() )

    private_key = key.private_bytes(
        encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM,
        format=cryptography.hazmat.primitives.serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=cryptography.hazmat.primitives.serialization.NoEncryption()).decode()


class fyre(object):
    
    TimeOut_default = 5
        
    def __init__(self, username, api_key, public_key):
        self.username = username
        self.api_key = api_key
        self.public_key = public_key
        
    def list(self, TimeOut = TimeOut_default):
        r = requests.post('https://api.fyre.ibm.com/rest/v1/?operation=query&request=showclusters',
                          auth = (self.username, self.api_key),
                          verify = False,
                          timeout = TimeOut)
        return r.json()['clusters']

    def details(self, cluster_name, TimeOut = TimeOut_default):
        r = requests.post('https://api.fyre.ibm.com/rest/v1/?operation=query&request=showclusterdetails&cluster_name='+cluster_name,
                          auth = (self.username, self.api_key),
                          verify = False,
                          timeout = TimeOut)
        return r.json()[cluster_name]
    #https://api.fyre.ibm.com/rest/v1/?operation=query&request=show[cluster|node]details&[cluster|node]_name=[cluster|node]_name
    
    def boot(self, cluster_name, TimeOut = TimeOut_default):
        r = requests.post('https://api.fyre.ibm.com/rest/v1/?operation=boot&cluster_name='+cluster_name,
                          auth = (self.username, self.api_key),
                          verify = False,
                          timeout = TimeOut)
        return r.json()
    #https://api.fyre.ibm.com/rest/v1/?operation=boot&node_name=node_name
    
    def shutdown(self, cluster_name, TimeOut = TimeOut_default):
        r = requests.post('https://api.fyre.ibm.com/rest/v1/?operation=shutdown&cluster_name='+cluster_name,
                          auth = (self.username, self.api_key),
                          verify = False,
                          timeout = TimeOut)
        return r.json()
    #https://api.fyre.ibm.com/rest/v1/?operation=shutdown&node_name=node_name
        
    def delete(self, cluster_name, TimeOut = TimeOut_default):
        r = requests.post('https://api.fyre.ibm.com/rest/v1/?operation=delete',
                          data = json.dumps({"cluster_name":cluster_name}),
                          auth = (self.username, self.api_key),
                          verify = False,
                          timeout = TimeOut)
        return r.json()

    def cluster(self, cluster_name, instance_type = None):
        if instance_type == None:
            return self.cluster_instance(self, cluster_name)
        else:
            return self.cluster_instance(self, cluster_name, instance_type)
    
    class cluster_instance(object):
        
        TimeOut_default = 5
        
        def __init__(self, fyre_instance, cluster_name, instance_type = "virtual_server", platform = "x"):
            """ Initialize instance """
            self.cluster_name = cluster_name
            self.fyre_instance = fyre_instance
            self.data = {
                "cluster_prefix": cluster_name,
                "clusterconfig":{
                    "instance_type": instance_type,
                    "platform": platform
                },
                cluster_name: []
            }
            
        def addNode(self, node_name, cpu = 2, memory = 2, os = "RedHat 7.4", publicvlan = "y", additional_disks = None):
            node = {
                "name" : node_name,
                "cpu" : cpu,
                "memory" : memory,
                "os" : os,
                "publicvlan" : publicvlan
            }
            if additional_disks is not None:
                node['additional_disks'] = []
                for disk in additional_disks:
                    node['additional_disks'].append({"size" : disk})
            self.data[self.cluster_name].append(node)
            
        def addNode2(self, node_name, baremetal_profile = "3650m5a", os = "Centos 7.2", publicvlan = "y", additional_disks = None):
            node = {
                "name" : node_name,
                "baremetal_profile": baremetal_profile,
                "os" : os,
                "publicvlan" : publicvlan
            }
            if additional_disks is not None:
                node['additional_disks'] = []
                for disk in additional_disks:
                    node['additional_disks'].append({"size" : disk})
            self.data[self.cluster_name].append(node)
            
        def submit(self, wait = False, TimeOut = TimeOut_default):
            self.data["fyre"] = {
                    "creds": {
                        "username" : self.fyre_instance.username,
                        "api_key" : self.fyre_instance.api_key,
                        "public_key" : self.fyre_instance.public_key
                    }
                }
            r = requests.post('https://api.fyre.ibm.com/rest/v1/?operation=build',
                      data = json.dumps(self.data),
                      auth = (self.fyre_instance.username, self.fyre_instance.api_key),
                      verify = False,
                      timeout = TimeOut)
            self.id = r.json()['request_id']
            
            if wait == True:
                time.sleep(2)
                self.waitForDeployed()
                
            d = self.details()
            for node in d[self.cluster_name]:
                globals()['exec_'+node['node'].replace(self.cluster_name+'-','')] = ssh(node['publicip']).exec
                globals()['scp_'+node['node'].replace(self.cluster_name+'-','')] = ssh(node['publicip']).scp2
                globals()['domain_'+node['node'].replace(self.cluster_name+'-','')] = node['node']+'.fyre.ibm.com'
            
            return self.id
        
        def status(self, id = None, TimeOut = TimeOut_default):
            if id is None:
                id = self.id
            r = requests.post('https://api.fyre.ibm.com/rest/v1/?operation=query&request=showrequests&request_id='+str(id),
                              auth = (self.fyre_instance.username, self.fyre_instance.api_key),
                              verify = False,
                              timeout = TimeOut)
            return r.json()['request'][0]
            
        def details(self, cluster_name = None, TimeOut = TimeOut_default):
            if cluster_name is None: cluster_name = self.cluster_name
            r = requests.post('https://api.fyre.ibm.com/rest/v1/?operation=query&request=showclusterdetails&cluster_name='+cluster_name,
                              auth = (self.fyre_instance.username, self.fyre_instance.api_key),
                              verify = False,
                              timeout = TimeOut)
            return r.json()
            
        def waitForDeployed(self):
            while True:
                s = self.status()
                if s['status'] == 'completed':
                    print(s['status'])
                    break
                elif s['status'] == 'error':
                    print(s['status'], ':', s['error_details'])
                    break
                else:
                    print(s['status'])
                time.sleep(15)
                
        def shutdown(self, cluster_name = None):
            if cluster_name is None: cluster_name = self.cluster_name
            return self.fyre_instance.shutdown(cluster_name)

        def getExec(self, cluster_name = None):
            if cluster_name is None: cluster_name = self.cluster_name
            ret = []
            for node in self.fyre_instance.details(cluster_name):
                ret.append(ssh(node['publicip']).exec)
            return ret
            

            #TODO
#        def __repr__(self):
#            return str(self.data)
        
#        def __str__(self):
#            return "member of Test"

def new(username = username_default, api_key = api_key_default, public_key = ','.join(map(str, public_key_default))):
    return fyre(username, api_key, public_key)


class ssh(object):
    def __init__(self, node):
        self.node = node
        
    def exec(self, cmd, node = None, port = 22, username = 'root', retval = False):
        client = paramiko.Transport((self.node, port))
        client.connect(username = username, pkey = paramiko.RSAKey.from_private_key(io.StringIO(private_key)))
        session = client.open_channel(kind = 'session')
        session.exec_command(cmd)
        ret = ''
        while True:
            if session.recv_ready():
                output = session.recv(4096).decode("utf-8", "ignore")
                if retval:
                    ret += output
                else:
                    print(output)
            if session.recv_stderr_ready():
                output = session.recv_stderr(4096).decode("utf-8", "ignore")
                print(output)
            if session.exit_status_ready():
                break
        if session.recv_ready():
            output = session.recv(4096).decode("utf-8", "ignore")
            if retval:
                ret += output
            else:
                print(output)
        session.close()
        client.close()
        if ret != '': return ret

    def exec1_deprecated(self, cmd, node = None, port = 22, username = 'root', retval = False):
        if node is None:
            node = self.node
        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(node, port, username, pkey = paramiko.RSAKey.from_private_key(io.StringIO(private_key)))
        (stdin, stdout, stderr) = s.exec_command(cmd)
        ret = ''
        for line in stdout.readlines():
            if retval:
                ret = ret + line
            else:
                print(line, end='')
        for line in stderr.readlines():
            if retval:
                ret = ret + line
            else:
                print(line, end='')
        s.close()
        if ret != '': return ret
        
    def scp2(self, src, tgt, node = None, port = 22, username = 'root'):
        if node is None:
            node = self.node
        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(node, port, username, pkey = paramiko.RSAKey.from_private_key(io.StringIO(private_key)))
        scp_client = scp.SCPClient(s.get_transport())
        scp_client.put(src, recursive=True, remote_path=tgt)
        scp_client.close()

