#!/usr/bin/env python
from fabric.api import env,hosts,run,execute,roles
from fabric.contrib.files import append
 
env.hosts = ['192.168.122.7','192.168.122.65','192.168.122.53','192.168.122.216','192.168.122.40','192.168.122.244']
env.user = "root"
env.password = "password"
env.roledefs = {
   'master': ['192.168.122.7','192.168.122.65','192.168.122.53'],
   'slave': ['192.168.122.216','192.168.122.40','192.168.122.244']}
def set_hosts():
	run("rm -rf /etc/hosts")
        append('/etc/hosts', '127.0.0.1       localhost', use_sudo=True)
        append('/etc/hosts', 'ff02::1 	      ip6-allnodes', use_sudo=True)
        append('/etc/hosts', 'ff02::2 	ip6-allrouters', use_sudo=True)
	append('/etc/hosts', '192.168.122.7	mesos01', use_sudo=True)
	append('/etc/hosts', '192.168.122.65	mesos02', use_sudo=True)
	append('/etc/hosts', '192.168.122.53	mesos03', use_sudo=True)
	append('/etc/hosts', '192.168.122.216	agent01', use_sudo=True)
	append('/etc/hosts', '192.168.122.40	agent02', use_sudo=True)
	append('/etc/hosts', '192.168.122.244	agent03', use_sudo=True)
	run("cat /etc/hosts")
def set_hostname():
	run("rm -rf /etc/hostname")
	append('/etc/hostname', env.host_string)
	run("hostname -F /etc/hostname")
        run("cat /etc/hostname")
def install_repo():
	run("rpm -Uvh http://repos.mesosphere.com/el/7/noarch/RPMS/mesosphere-el-repo-7-1.noarch.rpm")
def purge_all():
	run("yum -y remove mesos marathon mesosphere-zookeeper")
def restart_master_service():
        run("systemctl start zookeeper")
        run("service mesos-master restart")
        run("service marathon restart")
	run("systemctl restart firewalld")
def restart_slave_service():
        run("service mesos-slave restart")
	run("systemctl restart firewalld")

@roles('master')
def install_master():
	run("yum -y install mesos marathon mesosphere-zookeeper")
	run("systemctl stop mesos-slave.service")
	run("systemctl disable mesos-slave.service")
        run("firewall-cmd --zone=public --permanent --add-port=5050/tcp")   
	run("firewall-cmd --zone=public --permanent --add-port=2181/tcp")	
	run("firewall-cmd --zone=public --permanent --add-port=2888/tcp")	
	run("firewall-cmd --zone=public --permanent --add-port=3888/tcp")	
	run("firewall-cmd --zone=public --permanent --add-port=8080/tcp")	
	run("echo 2 > /etc/mesos-master/quorum")
        if env.host == "mesos01": run("echo 1 > /var/lib/zookeeper/myid")
        if env.host == "mesos02": run("echo 2 > /var/lib/zookeeper/myid")
        if env.host == "mesos03": run("echo 3 > /var/lib/zookeeper/myid")
	run("rm -rf /etc/mesos/zk")
	append('/etc/mesos/zk', 'zk://192.168.122.7:2181,192.168.122.65:2181,192.168.122.53:2181/mesos', use_sudo=True)
	run("systemctl start zookeeper")
        run("service mesos-master restart")
        run("service marathon restart")
        run("systemctl restart firewalld")
	run("echo master")

@roles('slave')
def install_agent():
	run("yum -y install mesos")
	run("systemctl stop mesos-master.service")
	run("systemctl disable mesos-master.service")
	run("firewall-cmd --zone=public --permanent --add-port=5051/tcp")	
	run("firewall-cmd --zone=public --permanent --add-port=2181/tcp")	
        run("rm -rf /etc/mesos/zk")
        append('/etc/mesos/zk', 'zk://192.168.122.7:2181,192.168.122.65:2181,192.168.122.53:2181/mesos', use_sudo=True)
        run("service mesos-slave restart")
        run("systemctl restart firewalld")
	run("echo SLAVE")

