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

def os_name():
    return platform.system()

def processor_family():
    return platform.processor()

def arc():
    return platform.machine()

def full_name():
    return platform.uname()
