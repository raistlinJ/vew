#!/bin/bash

vmrun -gu kali -gp kali CopyFileFromHostToGuest /home/workshopdev/vmware/hth2024/kali-linux-2024.3-vmware-amd64/kali-linux-2024.3-vmware-amd64_set_1.vmx ExperimentData/hth2024/Materials/checkConns.sh /tmp/checkConns.sh
vmrun -gu kali -gp kali runProgramInGuest /home/workshopdev/vmware/hth2024/kali-linux-2024.3-vmware-amd64/kali-linux-2024.3-vmware-amd64_set_1.vmx /tmp/checkConns.sh
vmrun -gu kali -gp kali CopyFileFromGuestToHost /home/workshopdev/vmware/hth2024/kali-linux-2024.3-vmware-amd64/kali-linux-2024.3-vmware-amd64_set_1.vmx /tmp/output.txt output1.txt
vmrun -gu kali -gp kali deleteFileInGuest /home/workshopdev/vmware/hth2024/kali-linux-2024.3-vmware-amd64/kali-linux-2024.3-vmware-amd64_set_1.vmx /tmp/output.txt
vmrun -gu kali -gp kali deleteFileInGuest /home/workshopdev/vmware/hth2024/kali-linux-2024.3-vmware-amd64/kali-linux-2024.3-vmware-amd64_set_1.vmx /tmp/checkConns.sh

