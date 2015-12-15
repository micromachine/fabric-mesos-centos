#!/usr/bin/env python
from fabric.api import env,hosts,run,execute,roles
from fabric.contrib.files import append
 
env.hosts = ['mesos01','mesos02','mesos03','agent01','agent02','agent03']
env.user = "root"
env.password = "password"
env.roledefs = {
   'master': ['mesos01','mesos02','mesos03'],
   'slave': ['agent01','agent02','agent03']}
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
        run("firewall-cmd --zone=public --permanent --add-port=53/udp")
	run("echo 2 > /etc/mesos-master/quorum")
        if env.host == "mesos01": 
		run("echo 1 > /var/lib/zookeeper/myid")
        if env.host == "mesos02": 
		run("echo 2 > /var/lib/zookeeper/myid")
        if env.host == "mesos03": 
		run("echo 3 > /var/lib/zookeeper/myid")
	run("rm -rf /etc/mesos/zk")
	append('/etc/mesos/zk', 'zk://mesos01:2181,mesos02:2181,mesos03:2181/mesos', use_sudo=True)
 	append('/etc/zookeeper/conf/zoo.cfg', '# specify all zookeeper servers', use_sudo=True)
        append('/etc/zookeeper/conf/zoo.cfg', 'server.1=mesos01:2888:3888', use_sudo=True)
        append('/etc/zookeeper/conf/zoo.cfg', 'server.2=mesos03:2888:3888', use_sudo=True)
        append('/etc/zookeeper/conf/zoo.cfg', 'server.3=mesos02:2888:3888', use_sudo=True)
        if env.host == "mesos01":
                run("echo 192.168.122.7 > /etc/mesos-master/ip")
                run("cp /etc/mesos-master/ip /etc/mesos-master/hostname")
        if env.host == "mesos02":
                run("echo 192.168.122.65 > /etc/mesos-master/ip")
                run("cp /etc/mesos-master/ip /etc/mesos-master/hostname")
        if env.host == "mesos03":
                run("echo 192.168.122.53 > /etc/mesos-master/ip")
                run("cp /etc/mesos-master/ip /etc/mesos-master/hostname")
	run("mkdir -p /etc/marathon/conf")
        run("cp /etc/mesos-master/hostname /etc/marathon/conf")
        run("cp /etc/mesos/zk /etc/marathon/conf/master")
        run("cp /etc/marathon/conf/master /etc/marathon/conf/zk")
        run("sed -i -e 's/mesos/marathon/g' /etc/marathon/conf/zk")
	run("systemctl start zookeeper")
        run("service mesos-master restart")
        run("service marathon restart")
        run("systemctl restart firewalld")
@roles('slave')
def install_agent():
	run("yum -y install mesos")
	run("systemctl stop mesos-master.service")
	run("systemctl disable mesos-master.service")
	run("firewall-cmd --zone=public --permanent --add-port=5051/tcp")	
	run("firewall-cmd --zone=public --permanent --add-port=2181/tcp")	
        run("rm -rf /etc/mesos/zk")
        append('/etc/mesos/zk', 'zk://mesos01:2181,mesos02:2181,mesos03:2181/mesos', use_sudo=True)
        run("service mesos-slave restart")
        run("systemctl restart firewalld")

