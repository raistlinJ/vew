#!/bin/bash

vmrun -gu kali -gp kali CopyFileFromHostToGuest /home/workshopdev/vmware/hth2024/kali-linux-2024.3-vmware-amd64/kali-linux-2024.3-vmware-amd64_set_1.vmx /home/workshopdev/myscr.sh /tmp/myscr.sh
vmrun -gu kali -gp kali runProgramInGuest /home/workshopdev/vmware/hth2024/kali-linux-2024.3-vmware-amd64/kali-linux-2024.3-vmware-amd64_set_1.vmx /tmp/myscr.sh
vmrun -gu kali -gp kali CopyFileFromGuestToHost /home/workshopdev/vmware/hth2024/kali-linux-2024.3-vmware-amd64/kali-linux-2024.3-vmware-amd64_set_1.vmx /tmp/output.txt /home/workshopdev/output1.txt
vmrun -gu kali -gp kali deleteFileInGuest /home/workshopdev/vmware/hth2024/kali-linux-2024.3-vmware-amd64/kali-linux-2024.3-vmware-amd64_set_1.vmx /tmp/output.txt
vmrun -gu kali -gp kali deleteFileInGuest /home/workshopdev/vmware/hth2024/kali-linux-2024.3-vmware-amd64/kali-linux-2024.3-vmware-amd64_set_1.vmx /tmp/myscr.sh

