# Container Monitor
# Monitoring container status, updating to database, and checking related specs
# Author: Chunkun Bo, Deyuan Guo
# Date: Dec 9, 2015

import os
import time

import itf_database
import itf_status
import monitor_qos

# Wrapper for pulling a file from remote container on Internet
def get_container_status(container_addr):
    path = os.path.join(container_addr, 'status.txt')
    status = itf_status.ContainerStatus()
    status.read_from_file(path)
    return status

# update a container information
def update(record):
    status_remote = get_container_status(record.container_addr)
    status_in_db = itf_database.get_status(record.container_id)
    if status_remote == None:
        print '[Container Monitor] Container ' + record.container_id + \
                  ' (' + record.container_addr + ') not available.'
        # TODO: update database and reschedule
    else:
        if status_in_db == None:
            print '[Container Monitor] Insert ' + record.container_id + ' status to database.'
            # Default reserved size = 0
            itf_database.update_container_status(record.container_id, status_remote)
        else:
            # Avoid overwriting the reservable size (container doesn't know this)
            status_remote.StorageReserved = status_in_db.StorageReserved
            itf_database.update_container_status(record.container_id, status_remote)
            # call QoS Monitor
            print '[Container Monitor] Call QoS Monitor for ' + record.container_id
            monitor_qos.monitor_container(record.container_id)

# Insert a new container status to database, called by QoS Manager
def insert(container_addr):
    status_remote = get_container_status(container_addr)
    container_id = status_remote.ContainerId
    added = itf_database.add_to_container_list(container_id, container_addr)
    if added == True:
        print '[Container Monitor] Insert ' + container_id + ' status to database.'
        # Default reserved size = 0
        itf_database.update_container_status(container_id, status_remote)


# Container Monitor Mainloop
if __name__ == '__main__':
    print '[Container Monitor] Start monitoring...'
    while True:
        records = itf_database.get_container_list()
        for record in records:
            print '--------------------'
            print '[Container Monitor] Check ' + record.container_id + \
                  ' (' + record.container_addr + ')'
            update(record)
            time.sleep(3)
        time.sleep(10)

