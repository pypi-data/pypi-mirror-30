# ========================================
# [] File Name : asit.py
#
# [] Creation Date : March 2018
#
# [] Created By : Ali Gholami (aligholami7596@gmail.com)
# ========================================
'''
    Advanced System Information Toolbox Python Library.
'''
import platform

class Asit:

    def os_name(self):
        return platform.system()
    
    def processor_family(self):
        return platform.processor()
    
    def arc(self):
        return platform.machine()

    def full_name(self):
        return platform.uname()
