from cpuinfo.cpuinfo import DataSource, _get_cpu_info_from_proc_cpuinfo, _get_cpu_info_from_sysctl, \
    _parse_dmesg_output
from ereuse_utils import cmd


def get_cpuinfo_from_android():
    return 0, """
Processor	: ARMv7 Processor rev 10 (v7l)
processor	: 0
BogoMIPS	: 597.12

processor	: 1
BogoMIPS	: 597.12

Features	: swp half thumb fastmult vfp edsp thumbee neon vfpv3 
CPU implementer	: 0x41
CPU architecture: 7
CPU variant	: 0x2
CPU part	: 0xc09
CPU revision	: 10

Hardware	: Tuna
Revision	: 0009
Serial		: 01499ef81800d015
    """


DataSource.has_proc_cpuinfo = lambda: True
DataSource.cat_proc_cpuinfo = get_cpuinfo_from_android
print(_get_cpu_info_from_proc_cpuinfo())



print(_parse_dmesg_output(cmd.run('adb', 'shell', 'dmesg').stdout))
