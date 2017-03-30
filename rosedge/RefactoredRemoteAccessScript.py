# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 09:44:45 2017

@author: Poulastya_Mukherjee
"""

import os
import subprocess
import threading
import md5
import docker
import shutil



class MltThrd(threading.Thread):
    def __init__(self, cmd, queue):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.queue = queue

    def run(self):
        # execute the command, queue the result
        subprocess.call(self.cmd, shell=True)
        # (status, output) = commands.getstatusoutput(self.cmd)
        # self.queue.put((self.cmd, output, status))


'''
MD5 checksum function for comparing input image name and existing image names
'''
def md5checksum(str1, str2):
    m1 = md5.new()
    m2 = md5.new()
    m1.update(str1)
    m2.update(str2)
    if (m1.digest() == m2.digest()):
        return True
    else:
        return False

class RemoteDock():
    
    def __init__(self, image, ip, port, roscommand, rospackage, roslaunchfile):
        self.ip = ip
        self.port = port
        self.roscommand = roscommand
        self.rospackage = rospackage
        self.roslaunchfile = roslaunchfile
        self.rospackage = rospackage
        self.image = rospackage + "_dockerfile"
        self.ip_str = "tcp://" + self.ip + ":" + self.port
        self.container_id = ""
        
    def startcheck(self):
        dockercmd_getimages = "curl -v http://" + self.ip + ":" + self.port +\
        "/images/search?term=" + self.image + " | jq '.[] | .name' >> tmpfile"
        subprocess.call(dockercmd_getimages, shell=True)
        pathtmpfile = os.path.abspath("tmpfile")
        tmpfile = open(pathtmpfile, "r")
        img_nm = tmpfile.read()
        img_nm = img_nm[1:-2]
        os.remove(pathtmpfile)
        var = md5checksum(self.image, img_nm)
        return var
    
    '''
    Takes in the the ip + port number and rospackage name
    Deploys the built image on the server
    '''
    def createDockerImage(self):
        # reading base docker commands
        copysh_path = os.path.abspath("basedocker") + "/ros_entrypoint.sh"
        base_path = os.path.abspath("basedocker") + "/Dockerfile"
        rd_base = open(base_path, "r")
        contents = rd_base.readlines()
        rd_base.close()

        # reading docker file of specific launch files from ros packages
        folder_cmd = "find ~ -type d -name " + self.rospackage + "_Dockerfile >> tmpfile" 
        subprocess.call(folder_cmd, shell=True)
        pathtmpfile = os.path.abspath("tmpfile")
        tmpfile = open(pathtmpfile, "r")
        pkg_path = tmpfile.read()
        tmpfile.close()
        pkg_path = pkg_path[:-1]
        os.remove(pathtmpfile)
        pkg_path = pkg_path + "/Dockerfile"
        dock_read = open(pkg_path, "r")
        tmp_contents = dock_read.readlines()
        dock_read.close()
        idx = 9
        for i in range(len(tmp_contents)):
            contents.insert(idx, tmp_contents[i])
            idx = idx + 1
    
        os.mkdir(self.rospackage + "_docker")
        tmppath = os.getcwd() + '/' + self.rospackage + "_docker"
        tmentrysh = tmppath +  "/ros_entrypoint.sh"
        shutil.copyfile(copysh_path,tmentrysh)
        os.chdir(tmppath)
        make_exec = "chmod +x ros_entrypoint.sh"
        subprocess.call(make_exec,shell=True)
        file = open('Dockerfile', 'w')
        contents = "".join(contents)
        file.write(contents)
        file.close()
        tarcode = "tar zcf Dockerfile.tar.gz Dockerfile ros_entrypoint.sh"
        subprocess.call(tarcode, shell=True)
        buildcode = "curl -v -X POST -H " + '"Content-Type:application/tar"' + \
            " --data-binary '@Dockerfile.tar.gz' http://" + self.ip + ":" + \
            self.port + "/build?t=" + self.image        
        status = subprocess.call(buildcode, shell=True)
        return status
    
    '''
    Creates a Docker container and uses the image built from function 
    createDockerImg and deploys it directly on the server
    '''
    def createDockerContainer(self):
        cli = docker.Client(base_url=self.ip_str)
        container = cli.create_container(self.image,
                                         hostname='3e93a4b05cf6',
                                         user='1000:1000',
                                         stdin_open=True,
                                         tty=True,
                                         entrypoint='/ros_entrypoint.sh',
                                         command=["bash"],
                                         environment=[
                                             "PATH/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"],
                                         working_dir='/',
                                         volumes='$HOME/.config/catkin:/.config/catkin:ro')
        cli.start(container['Id'])
        self.container_id = container['Id']
        return container['Id']
    
    '''
    Runs the created docker container using the generated container id 
    from createDockerContainer function
    '''    
    def runDockerCommands(self):
        cli = docker.Client(base_url=self.ip_str)
        rosip_str = cli.inspect_container(self.container_id)['NetworkSettings']['IPAddress']
        dockerexec_source = "docker -H tcp://" + self.ip + ":" + \
        self.port + " exec -it " + self.container_id + " bash -c \
        'source ros_entrypoint.sh;export ROS_MASTER_URI=http://'" + self.ip + "':11311;\
        export ROS_IP='"+ rosip_str +"';'" + self.roscommand + "' '" + self.rospackage + "' '" \
        + self.roslaunchfile
        subprocess.call(dockerexec_source,shell=True)
    
    '''
    Runs the existing image in the local machine on the robot
    '''  
    def runExistingImage(self):
        dockercmd_runimg = "docker -H tcp://" + self.ip + ":" + self.port + " run -it --rm -u " + \
                            '"$(id -u):$(id -g)" ' + \
                            "-v $HOME/.ros:/.ros -v $HOME/.config/catkin:/.config/catkin:ro " + \
                            "-v $(pwd):$(pwd) -w $(pwd) " + self.image
        
        subprocess.call(dockercmd_runimg, shell=True)