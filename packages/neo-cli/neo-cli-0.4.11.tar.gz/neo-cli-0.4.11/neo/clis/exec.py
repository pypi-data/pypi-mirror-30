import os
from .base import Base
from neo.libs import network as network_lib
from neo.libs import vm as vm_lib
from neo.libs import utils, image
from neo.libs import orchestration as orch
from tabulate import tabulate


class Exec(Base):
    """
usage:
        exec [-n] [-m VM_ID]
        exec
        exec vm <VM_ID>
        exec network <NETWORK_ID>

List all stack

Options:
-h --help                            Print usage
-k KEY_FILE --key-file=KEY_FILE      Set neo manifest file
-a --all                             List all Stacks
-m VM_ID --virtual-machine VM_ID     List all Virtual Machines
-n --network                         List all Networks

Commands:
  vm ID                              List all Networks

Run 'neo exec COMMAND --help' for more information on a command.
"""

    def execute(self):
        print(self.args)
        print(self.__doc__)
        if self.args["--network"]:
            # print(vm_lib.get_list()[1].to_dict())
            print(
                vm_lib.detail("fcfdd0c0-a522-48e9-a4fc-6f030283d3d5")
                .to_dict())
            """["key_name"]"""
            exit()
