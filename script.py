import os, time, pdb

import_node = 'openstack overcloud node import instackenv.json'
introspect_node = 'nohup openstack overcloud node introspect --all-manageable --provide &'
node_state = "openstack baremetal node list -c 'Provisioning State' | awk '{print $2}'| awk 'NR > 2'"
start_vm = 'ssh  root@dell-r530-62.gsslab.pnq2.redhat.com bash -x collectdstart.sh &> /dev/null'
stop_vm = 'ssh  root@dell-r530-62.gsslab.pnq2.redhat.com bash -x collectdstop.sh &> /dev/null'
deploy_file = raw_input("Enter the deployment file path: ")


def import_and_introspect():
    print("Importing nodes")

    os.system("source ~/stackrc")
    os.system(import_node)

    states = set(os.popen(node_state).read().split())

    if len(states) == 1 and 'manageable' in states:
        print("All node are imported")
        os.system(introspect_node)
        print("starting vms")
        os.system(start_vm)

    while(1) :
        states = set(os.popen(node_state).read().split())
        if len(states) == 1 and 'available' in states:
            print("Introspection completed")
            os.system(stop_vm)
            break
        else:
            print("Node are introspecting")
            time.sleep(90)

def deploy():
    states = set(os.popen(node_state).read().split())
    if len(states) == 1 and 'available' in states:
        print("Starting the deployment")
        deploy_cmd_with_nohup = "nohup  sh " + deploy_file + " &"
        os.system(deploy_cmd_with_nohup)
        
    print("Waiting for call-back")

    while(1):
        states = set(os.popen(node_state).read().split())
        if len(states) == 1 and 'wait' in states:
            os.system(start_vm)
            while(1):
                states = set(os.popen(node_state).read().split())
                if len(states) == 1 and 'active' in states:
                    os.system(start_vm)
                    break
                else:
                    print("Waiting for active")
                    time.sleep(30)
            break
        else:
            print("Waiting for call-back")
            time.sleep(30)

    foobar = input("Do you want to wait to check the deployment log or you want to exit\n1. To continue\n2. Exit")
    if foobar == 2:
        exit(0)
    elif foobar == 1:
        os.system("tailf ~/nohup.out")

import_and_introspect()
deploy()
