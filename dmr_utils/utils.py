#!/usr/bin/env python
#
###############################################################################
#   Copyright (C) 2016-2019  Cortney T. Buffington, N0MJS <n0mjs@me.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
###############################################################################

from __future__ import print_function

from json import load as jload
from os.path import isfile, getmtime
from time import time
from urllib import URLopener
from binascii import b2a_hex as ahex

# Does anybody read this stuff? There's a PEP somewhere that says I should do this.
__author__     = 'Cortney T. Buffington, N0MJS'
__copyright__  = 'Copyright (c) 2016-2019 Cortney T. Buffington, N0MJS and the K0USY Group'
__credits__    = 'Colin Durbridge, G4EML, Steve Zingman, N4IRS; Mike Zingman'
__license__    = 'GNU GPLv3'
__maintainer__ = 'Cort Buffington, N0MJS'
__email__      = 'n0mjs@me.com'


# CONSTANTS
SUB_FIELDS   = ('ID', 'CALLSIGN', 'NAME', 'CITY', 'STATE', 'COUNTRY', 'TYPE')
PEER_FIELDS  = ('ID', 'CALLSIGN', 'CITY', 'STATE', 'COUNTRY', 'FREQ', 'CC', 'OFFSET', 'TYPE', 'LINKED', 'TRUSTEE', 'INFO', 'OTHER', 'NETWORK', )
TGID_FIELDS  = ('ID', 'NAME')


#************************************************
#     STRING UTILITY FUNCTIONS
#************************************************

# Create a 2 byte hex string from an integer
def hex_str_2(_int_id):
    try:
        return format(_int_id,'x').rjust(4,'0').decode('hex')
    except TypeError:
        raise

# Create a 3 byte hex string from an integer
def hex_str_3(_int_id):
    try:
        return format(_int_id,'x').rjust(6,'0').decode('hex')
    except TypeError:
        raise

# Create a 4 byte hex string from an integer
def hex_str_4(_int_id):
    try:
        return format(_int_id,'x').rjust(8,'0').decode('hex')
    except TypeError:
        raise

# Convert a hex string to an int (radio ID, etc.)
def int_id(_hex_string):
    return int(ahex(_hex_string), 16)


#************************************************
#     ID ALIAS FUNCTIONS
#************************************************

# Download and build dictionaries for mapping number to aliases
# Used by applications. These lookups take time, please do not shove them
# into this file everywhere and send a pull request!!!
# Download a new file if it doesn't exist, or is older than the stale time
def try_download(_path, _file, _url, _stale,):
    now = time()
    url = URLopener()
    file_exists = isfile(_path+_file) == True
    if file_exists:
        file_old = (getmtime(_path+_file) + _stale) < now
    if not file_exists or (file_exists and file_old):
        try:
            url.retrieve(_url, _path+_file)
            result = 'ID ALIAS MAPPER: \'{}\' successfully downloaded'.format(_file)
        except IOError:
            result = 'ID ALIAS MAPPER: \'{}\' could not be downloaded'.format(_file)
    else:
        result = 'ID ALIAS MAPPER: \'{}\' is current, not downloaded'.format(_file)
    url.close()
    return result

# SHORT VERSION - MAKES A SIMPLE {INTEGER ID: 'CALLSIGN'} DICTIONARY
def mk_id_dict(_path, _file):
    _dict = {}
    try:
        with open(_path+_file, 'rU') as _handle:
            records = jload(_handle)['results']
            _handle.close
            for record in records:
                _dict[int(record['id'])] = record['callsign'].encode('ascii','ignore')
        return _dict
    except IOError:
        return _dict

# LONG VERSION - MAKES A FULL DICTIONARY OF INFORMATION BASED ON TYPE OF ALIAS FILE
# BASED ON DOWNLOADS FROM RADIOID.NET      
def mk_full_id_dict(_path, _file, _type):
    _dict = {}
    try:
        with open(_path+_file, 'rU') as _handle:
            records = jload(_handle)['results']
            _handle.close
            if _type == 'peer':
                for record in records:
                    _dict[int(record['id'])] = {
                        'CALLSIGN': record['callsign'],
                        'CITY': record['city'],
                        'STATE': record['state'],
                        'COUNTRY': record['country'],
                        'FREQ': record['frequency'],
                        'CC': record['color_code'],
                        'OFFSET': record['offset'],
                        'LINKED': record['ts_linked'],
                        'TRUSTEE': record['trustee'],
                        'NETWORK': record['ipsc_network']
                    }
            elif _type == 'subscriber':
                for record in records:
                    _dict[int(record['id'])] = {
                        'CALLSIGN': record['callsign'],
                        'NAME': (record['fname'] + ' ' + record['surname']),
                        'CITY': record['city'],
                        'STATE': record['state'],
                        'COUNTRY': record['country']
                    }
            elif _type == 'tgid':
                for record in records:
                    _dict[int(record['id'])] = {
                        'NAME': record['callsign']
                    }
        return _dict
    except IOError:
        return _dict


# THESE ARE THE SAME THING FOR LEGACY PURPOSES
def get_alias(_id, _dict, *args):
    if type(_id) == str:
        _id = int_id(_id)
    if _id in _dict:
        if args:
            retValue = []
            for _item in args:
                try:
                    retValue.append(_dict[_id][_item])
                except TypeError:
                    return _dict[_id]
            return retValue
        else:
            return _dict[_id]
    return _id

def get_info(_id, _dict, *args):
    if type(_id) == str:
        _id = int_id(_id)
    if _id in _dict:
        if args:
            retValue = []
            for _item in args:
                try:
                    retValue.append(_dict[_id][_item])
                except TypeError:
                    return _dict[_id]
            return retValue
        else:
            return _dict[_id]
    return _id


if __name__ == '__main__':

    '''
    repeater file:  ('callsign', 'city', 'color_code', 'country', 'frequency', 'ipsc_network', 'locator', 'offset', 'state', 'trustee', 'ts_linked')
    user file:      ('callsign', 'city', 'country', 'fname', 'radio_id', 'remarks', 'state', 'surname')
    '''
    
    # Try updating peer aliases file
    result = try_download('/tmp/', 'peers.json', 'https://www.radioid.net/api/dmr/repeater/?country=united%20states', 0)
    print(result)
    
    # Try updating subscriber aliases file
    result = try_download('/tmp/', 'subscribers.json', 'https://www.radioid.net/api/dmr/user/?country=united%20states', 0)
    print(result)
        
    # Make Dictionaries
    peer_ids = mk_id_dict('/tmp/', 'peers.json')
    if peer_ids:
        print('ID ALIAS MAPPER: peer_ids dictionary is available')
   
    subscriber_ids = mk_id_dict('/tmp/', 'subscribers.json')
    if subscriber_ids:
        print('ID ALIAS MAPPER: subscriber_ids dictionary is available')
   
    full_peer_ids = mk_full_id_dict('/tmp/', 'peers.json', 'peer')
    if peer_ids:
        print('ID ALIAS MAPPER: full_peer_ids dictionary is available')
        
    full_subscriber_ids = mk_full_id_dict('/tmp/', 'subscribers.json', 'subscriber')
    if subscriber_ids:
        print('ID ALIAS MAPPER: full_subscriber_ids dictionary is available')

    print(get_alias('\x2f\x9b\xe5', subscriber_ids))
    print(get_info(3120101, subscriber_ids))
    print(get_alias(3120101, full_subscriber_ids))
    print(get_info(3120101, full_subscriber_ids))
    print(get_alias(31201010, subscriber_ids))
    print(get_info(31201010, subscriber_ids))
    
    print(get_alias(312000, peer_ids))
    print(get_info(312000, peer_ids))
    print(get_alias(312000, full_peer_ids))
    print(get_info(312000, full_peer_ids))

    print(repr(hex_str_2(65535)))
    print(repr(hex_str_3(65535)))
    print(ahex(hex_str_4(13120101)))
    print(int_id('\x00\xc8\x32\x65'))

    
    
