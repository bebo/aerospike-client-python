# -*- coding: utf-8 -*-
import pytest
import time
import sys
import cPickle as pickle
try:
    import aerospike
except:
    print "Please install aerospike python client."
    sys.exit(1)

class TestScanInfo(object):

    def setup_method(self, method):
        """
        Setup method.
        """
        config = {
            'hosts': [('127.0.0.1', 3000)]
        }
        self.client = aerospike.client(config).connect()
        for i in xrange(5):
            key = ('test', 'demo', i)
            rec = {
                'name' : 'name%s' % (str(i)),
                'age' : i
            }
            self.client.put(key, rec)
        policy = {}
        self.client.udf_put("bin_lua.lua", 0, policy)
        self.scan_id = self.client.scan_apply("test", "demo", "bin_lua", "mytransform", ['age', 2])

    def teardown_method(self, method):
        """
        Teardoen method.
        """
        for i in xrange(5):
            key = ('test', 'demo', i)
            self.client.remove(key)
        self.client.close()

    def test_scan_info_with_no_parameters(self):
        """
        Invoke scan_info() without any mandatory parameters.
        """
        with pytest.raises(TypeError) as typeError:
            self.client.scan_info()
        assert "Required argument 'scanid' (pos 1) not found" in typeError.value

    def test_scan_info_with_correct_parameters(self):
        """
        Invoke scan_info() with correct parameters
        """
        scan_info = self.client.scan_info(self.scan_id)

        if scan_info['status'] == aerospike.SCAN_STATUS_COMPLETED or scan_info['status'] == aerospike.SCAN_STATUS_UNDEF or scan_info['status'] or aerospike.SCAN_STATUS_INPROGRESS or scan_info['status'] == aerospike.SCAN_STATUS_ABORTED:
            assert True == True
        else:
            assert True == False

    def test_scan_info_with_correct_policy(self):
        """
        Invoke scan_info() with correct policy
        """
        policy = {
            'timeout': 1000
        }
        scan_info = self.client.scan_info(self.scan_id, policy)

        if scan_info['status'] == aerospike.SCAN_STATUS_COMPLETED or scan_info['status'] == aerospike.SCAN_STATUS_UNDEF or scan_info['status'] or aerospike.SCAN_STATUS_INPROGRESS or scan_info['status'] == aerospike.SCAN_STATUS_ABORTED:
            assert True == True
        else:
            assert True == False

    def test_scan_info_with_incorrect_policy(self):
        """
        Invoke scan_info() with incorrect policy
        """
        policy = {
            'timeout': 0.5
        }
        with pytest.raises(Exception) as exception:
            scan_id = self.client.scan_info(self.scan_id, policy)

        assert exception.value[0] == -2
        assert exception.value[1] == "timeout is invalid"

    def test_scan_info_with_scanid_negative(self):
        """
        Invoke scan_info() with scan id negative
        """
        scan_info = self.client.scan_info(-2)

        assert scan_info['progress_pct'] == 0

    def test_scan_info_with_scanid_incorrect(self):
        """
        Invoke scan_info() with scan id incorrect
        """
        scan_info = self.client.scan_info(1)

        assert scan_info['progress_pct'] == 0

    def test_scan_info_with_scanid_string(self):
        """
        Invoke scan_info() with scan id incorrect
        """
        with pytest.raises(TypeError) as typeError:
            scan_info = self.client.scan_info("string")

        assert "an integer is required" in typeError.value
