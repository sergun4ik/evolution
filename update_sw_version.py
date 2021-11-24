# The script takes in a tenant name as first argument and 
# netbox API key as second argument.
# Updates all devices with their respective OS versions in
# custom fields section.
# Sergey Lisitsin, 2021

import pynetbox
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from sys import argv
from re import search

def get_active_netbox_devices(nb,tenant_name):
    '''
    Function takes in netbox api object and tenant
    name as arguments and returns a list of devices
    for the given tenant'''
    device_list = []
    tenant = nb.tenancy.tenants.filter(tenant_name)
    try:
        devices = nb.dcim.devices.filter(tenant=tenant.slug,state = 'Active')
    except:
        print(f"Was unable to collect device information for tenant {tenant_name}. Please, check the spelling")
        exit()
    for device in devices:
        device_list.append(device)
    return device_list

    
def get_sw_version(dev_ip, dev_platform, dev_username, dev_password, enable_password):
    ''' Function takes in IP address, platform type, username,
    password and enable password and returns the software
    version (string) for a given devcie. Uses napalm library'''
    driver = napalm.get_network_driver(dev_platform)
    device = driver(hostname = dev_ip,
                    username= dev_username,
                    password = dev_password,
                    optional_args = {'secret': enable_password})
    device.open()
    facts = device.get_facts()
    os_ver = facts['os_version']
    return os_ver

def main():
    ''' Main function. Reads info about devices for a specified
    tenant. Then iterates over them one by one and tries to 
    obtain software version info using napalm. Once successfully obtained
    it updates the device's object in netbox.
    '''
    nb_token = argv[2]
    url = 'https://demo.netbox.dev'                 # Please, update the URL with your server's address

    nb = pynetbox.api(url, nb_token)
    nb.extras.api.http_session.verify=False 

    drivers = ['ios','eos','nx-os','junos']

    tenant_name = argv[1]
    username = input("Please, provide username to connect to devices: ")
    device_password = getpass("Please, provide password to connect to devices: ")
    enable_password = getpass("Please, provide enable password for devices: ")
    tenant_devices = get_active_netbox_devices(tenant_name)
    for tenant_device in tenant_devices:
        device_ip = search('^[\d\.]+',tenant_device.primary_ip).group()
        for driver in drivers:
            if driver in device.platform.lower():
                device_driver = napalm.get_network_driver(driver)
                break
        device_connection = device_driver(hostname=device_ip,
                                        username=username,
                                        password=device_password,
                                        optional_args={'secret': enable_password})
        device_connection.open()
        device_facts = device_connection.get_facts()
        device_connection.close()
        device_os_version = device_facts['os_version']
        try:
            tenant_device.update({'Custom fields': {'software version': device_os_version}})
            print(f"Device {tenant_device} updated successfully")
        except:
            print(f"An error occured while trying to update device {tenant_device}. Please, ensure the device has custom fields configured.")
        
if __name__ == '__main__':
    main()


