
# Networking
from .pynetlinux import ifconfig, route
import debinterface
import dns.resolver


class NetworkSettings:
    """Network settings class for retrieving and setting network settings

    """
    def __init__(self, form=None):
        self.__interface = ifconfig.Interface(bytes(route.get_default_if(), 'utf-8'))

        try:
            self.__net_interface = debinterface.Interfaces()
        except FileNotFoundError:
            self.__adapter = None
            self.__net_interface = None
        else:
            self.__adapter = self.__net_interface.getAdapter(self.__interface.name.decode("utf-8"))

        if form is not None:
            for name in dir(form):
                if not name.startswith('_'):
                    unbound_field = getattr(form, name)
                    if hasattr(self, name):
                        if unbound_field.data != '':
                            setattr(self, name, unbound_field.data)

    def __str__(self):
        return "Network Card:\n\rHost name:{}\r\nDHCP Mode:{}\r\nIP Address:{}\r\n" \
               "Subnet:{}\r\nGateway:{}\r\nDNS:{}".format(self.host_name,
                                                          self.dhcp_mode,
                                                          self.ip_address,
                                                          self.sub_address,
                                                          self.gw_address,
                                                          self.dns_address)

    @staticmethod
    def mask_to_slash(mask):
        """Converts IP4 format subnet mask text string to linux netmask integer value
        ex) 255.255.255.0 => 24  (24 ones followed by 8 zeros to mark first 24 bits in a 32 bit field)

        :param str mask:
        :return int:
        """
        try:
            ip = mask.split('.')
            s_sum = 0

            for i in ip:
                s = str(format(int(i), 'b'))
                s_cnt = s.count('1')
                s_sum += s_cnt
        except AttributeError:
            return 24
        else:
            return s_sum

    @staticmethod
    def slash_to_mask(slash):
        """Converts linux subnet mask integer value to IP4 format text
        ex) 23 => 255.255.254.000

        :param int slash:
        :return str:
        """

        mask_bits = []

        for i in range(32, 0, -1):
            if i > 32 - slash:
                mask_bits.append('1')
            else:
                mask_bits.append('0')

        # print(''.join(mask_bits))
        mask_txt = str(int(''.join(mask_bits[0:8]), 2)) + '.' + str(int(''.join(mask_bits[8:16]), 2)) + '.' + str(
            int(''.join(mask_bits[16:24]), 2)) + '.' + str(int(''.join(mask_bits[24:32]), 2))

        return mask_txt

    @property
    def host_name(self):
        with open('/etc/hostname', 'r') as f:
            host_name = f.readline().rstrip()
        return host_name

    @host_name.setter
    def host_name(self, hostname):
        assert isinstance(hostname, str), 'Hostname {} needs to be of type string not {}'.format(hostname, type(hostname))

        with open('/etc/hostname', 'r') as f:
            s = f.readline(limit=1).strip('\n')

        if s != hostname:
            s.replace(self.host_name, hostname)
            # Safely write the changed content, if found in the file
            with open('/etc/hostname', 'w') as f:
                f.write(s)

    @property
    def dhcp_mode(self):
        if self.__adapter is not None:
            options = self.__adapter.export()
            return True if (options['source'] == 'manual' or options['source'] == 'dhcp') else False
        else:
            return True

    @dhcp_mode.setter
    def dhcp_mode(self, mode):
        assert isinstance(mode, (bool, str)), 'Mode needs to be of a boolean type'
        if self.__adapter is not None:
            if mode is True or mode == 'dhcp' or mode == 'y':
                self.__adapter.setAddressSource('dhcp')
            else:
                self.__adapter.setAddressSource('static')
            self.__net_interface.writeInterfaces()

    @property
    def mac_address(self):
        return self.__interface.get_mac()

    @property
    def ip_address(self):
        return self.__interface.get_ip()

    @ip_address.setter
    def ip_address(self, address):
        assert isinstance(address, str), 'Address needs to be of type string'
        if self.__adapter is not None:
            self.__adapter.setAddress(address)
            self.__net_interface.writeInterfaces()

    @property
    def sub_address(self):
        return self.slash_to_mask(self.__interface.get_netmask())

    @sub_address.setter
    def sub_address(self, address):
        assert isinstance(address, str), 'Address needs to be of type string'
        if self.dhcp_mode is False and self.__adapter is not None:
            self.__adapter.setNetmask(self.mask_to_slash(address) if len(address) < 3 else address )
            self.__net_interface.writeInterfaces()

    @property
    def gw_address(self):
        return route.get_default_gw()

    @gw_address.setter
    def gw_address(self, address):
        assert isinstance(address, str), 'Address needs to be of type string'
        if self.dhcp_mode is False and self.__adapter is not None:
            self.__adapter.setGateway(address)
            self.__net_interface.writeInterfaces()

    @property
    def dns_address(self):
        if self.dhcp_mode:
            res = dns.resolver.Resolver()

            return ', '.join(res.nameservers)
        else:
            if self.__adapter is not None:
                options = self.__adapter.export()
                return ' '.join(options.get('dns-nameservers'))
            else:
                return '8.8.8.8'

    @dns_address.setter
    def dns_address(self, address):
        if self.dhcp_mode is False and self.__adapter is not None:
            self.__adapter.setDnsNameservers(address)
            self.__net_interface.writeInterfaces()
