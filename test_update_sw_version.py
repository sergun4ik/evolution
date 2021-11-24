import pynetbox


def test_netbox_connection():
  nb = pynetbox.api('https://demo.netbox.dev','75fd1afe735dbbfdd5335ecf580a81663eb9b164')
  assert nb.version == '3.0'


def test_getting_tenant():
  nb = pynetbox.api('https://demo.netbox.dev','75fd1afe735dbbfdd5335ecf580a81663eb9b164')
  tenant = nb.tenancy.tenants.get(name='Dunder-Mifflin, Inc.')
  assert tenant.id > 0

def test_getting_devices():
  device_list = []
  nb = pynetbox.api('https://demo.netbox.dev','75fd1afe735dbbfdd5335ecf580a81663eb9b164')
  tenant = nb.tenancy.tenants.get(name='Dunder-Mifflin, Inc.')
  devices = nb.dcim.devices.filter(tenant=tenant.slug, state='Active')
  for device in devices:
    device_list.append(device)
  assert len(device_list) > 0