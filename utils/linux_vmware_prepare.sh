#!/bin/bash

#run the following:
#do a sudo chmod a+rw /dev/vmnet*
sudo chmod a+rw /dev/vmnet*
#Alternatively, open /etc/init.d/vmware and change the vmwareStartVmnet() function as follows:
# vmwareStartVmnet() {
#    vmwareLoadModule $vnet
#    "$BINDIR"/vmware-networks --start >> $VNETLIB_LOG 2>&1
#    chmod a+rw /dev/vmnet*
# }

#May have to set promisc in vmx files with ethernetX.noPromisc = "False"