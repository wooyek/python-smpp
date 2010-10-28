import unittest
from datetime import datetime, timedelta

try:from smpp.esme import *
except:from src.smpp.esme import *

try:from smpp.clickatell import *
except:from src.smpp.clickatell import *

import credentials_priv
import credentials_test

from test.pdu import pdu_objects
from test import pdu_asserts
from test.pdu_hex import pdu_hex_strings
from test import pdu_hex_asserts


def unpack_hex(pdu_hex):
    """Unpack PDU hex string and return it as a dictionary"""
    return unpack_pdu(binascii.a2b_hex(hexclean(pdu_hex)))

def hexclean(dirtyhex):
    """Remove whitespace, comments & newlines from hex string"""
    return re.sub(r'\s','',re.sub(r'#.*\n','\n',dirtyhex))

def prettydump(pdu_obj):
    """Unpack PDU dictionary and dump it as a JSON formatted string"""
    return json.dumps(pdu_obj, indent=4, sort_keys=True)


def create_pdu_asserts():
    pdu_index = 0
    for pdu in pdu_objects:
        pdu_index += 1
        pstr  = "\n########################################\n"
        pstr += "pdu_json_"
        pstr += ('%010d' % pdu_index)
        pstr += " = '''"
        pstr += prettydump(unpack_pdu(pack_pdu(pdu)))
        pstr += "'''"
        print pstr


def create_pdu_hex_asserts():
    pdu_index = 0
    for pdu_hex in pdu_hex_strings:
        pdu_index += 1
        pstr  = "\n########################################\n"
        pstr += "pdu_json_"
        pstr += ('%010d' % pdu_index)
        pstr += " = '''"
        pstr += prettydump(unpack_hex(pdu_hex))
        pstr += "'''"
        print pstr


## :w|!python % > test/pdu_asserts.py
#create_pdu_asserts()
#quit()

## :w|!python % > test/pdu_hex_asserts.py
#create_pdu_hex_asserts()
#quit()


class PduTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pack_unpack_pdu_objects(self):
        print ''
        """
        Take a dictionary, pack and unpack it and dump it as JSON correctly
        """
        pdu_index = 0
        for pdu in pdu_objects:
            pdu_index += 1
            padded_index = '%010d' % pdu_index
            print '...', padded_index
            self.assertEquals(
                    re.sub('\n *','',
                        prettydump(unpack_pdu(pack_pdu(pdu)))),
                    re.sub('\n *','',
                        eval('pdu_asserts.pdu_json_'+padded_index)))


    def test_pack_unpack_pdu_hex_strings(self):
        print ''
        """
        Read the hex data, clean it, and unpack it to JSON correctly
        """
        pdu_index = 0
        for pdu_hex in pdu_hex_strings:
            pdu_index += 1
            padded_index = '%010d' % pdu_index
            print '...', padded_index
            self.assertEquals(
                    re.sub('\n *','',
                        prettydump(unpack_hex(pdu_hex))),
                    re.sub('\n *','',
                        eval('pdu_hex_asserts.pdu_json_'+padded_index)))


    def test_pack_unpack_performance(self):
        print ''
        """
        Pack & unpack 2000 submit_sm PDUs in under 1 second
        """
        submit_sm = {
            'header': {
                'command_length': 0,
                'command_id': 'submit_sm',
                'command_status': 'ESME_ROK',
                'sequence_number': 0,
            },
            'body': {
                'mandatory_parameters': {
                    'service_type':'',
                    'source_addr_ton':1,
                    'source_addr_npi':1,
                    'source_addr':'',
                    'dest_addr_ton':1,
                    'dest_addr_npi':1,
                    'destination_addr':'',
                    'esm_class':0,
                    'protocol_id':0,
                    'priority_flag':0,
                    'schedule_delivery_time':'',
                    'validity_period':'',
                    'registered_delivery':0,
                    'replace_if_present_flag':0,
                    'data_coding':0,
                    'sm_default_msg_id':0,
                    'sm_length':1,
                    'short_message':'',
                },
            },
        }
        start = datetime.now()
        for x in range(2000):
            x += 1
            submit_sm['header']['sequence_number'] = x
            sm = 'testing: x = '+str(x)+''
            submit_sm['body']['mandatory_parameters']['short_message'] = sm
            u = unpack_pdu(pack_pdu(submit_sm))
        delta = datetime.now() - start
        print '... 2000 pack & unpacks in:', delta
        self.assertTrue(delta < timedelta(seconds=1))



class PduBuilderTestCase(unittest.TestCase):

    def test_true(self):
        print ''
        self.assertTrue(True)



if __name__ == '__main__':
    print '\n##########################################################\n'
    esme = ESME()
    esme.loadDefaults(clickatell_defaults)
    esme.loadDefaults(credentials_test.logica)
    print esme.defaults
    esme.bind_transmitter()
    print esme.state
    start = datetime.now()
    for x in range(1):
        esme.submit_sm(
                short_message = 'gobbledygook',
                destination_addr = '555',
                )
        print esme.state
    for x in range(1):
        esme.submit_multi(
                short_message = 'gobbledygook',
                dest_address = ['444','333'],
                )
        print esme.state
    for x in range(1):
        esme.submit_multi(
                short_message = 'gobbledygook',
                dest_address = [
                    {'dest_flag':1, 'destination_addr':'111'},
                    {'dest_flag':2, 'dl_name':'list22222'},
                    ],
                )
        print esme.state
    delta = datetime.now() - start
    esme.disconnect()
    print esme.state
    print 'excluding binding ... time to send messages =', delta


#if __name__ == '__main__':
    #unittest.main()

