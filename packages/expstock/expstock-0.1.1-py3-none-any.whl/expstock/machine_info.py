import platform
import subprocess

def get_machine_info(self):
    """get_machine_info
    TODO: add function to get resource usage
    """
    machine_info = []
    machine_info.append(('system', platform.system()))
    machine_info.append(('node', platform.node()))
    machine_info.append(('release', platform.release()))
    machine_info.append(('version', platform.version()))
    machine_info.append(('machine', platform.machine()))
    machine_info.append(('processor', platform.processor()))
    return machine_info

def _get_cpu_info(host_type):
    if host_type = 'Linux':
        subprocess.check_output(['cat', '/proc/cpuinfo'])

def _get_memory_info(host_type):
    pass

