from engine.Configuration.VMwareConfigIO import VMwareConfigIO
from engine.Configuration.SystemConfigIO import SystemConfigIO
import re
import os

# Example usage
s = SystemConfigIO()
vc = VMwareConfigIO()

# helper function to perform sort
def num_sort(test_string):
    return list(map(int, re.findall(r'\d+', test_string)))[0]

filename = s.getConfig()['VMWARE']['VMANAGE_VM_PATH']
                          
my_list = vc.refresh_vmpath_to_dict(filename)
print(my_list)

vm_nics = {}
realvmlist = my_list.keys()
for vm in realvmlist:
    vm_nics[vm] = vc.get_vmnics(vm)
print(vm_nics)
