# -*- coding: utf-8 -*-
import pytest
import sys
import time
import cPickle as pickle

try:
    import aerospike
except:
    print "Please install aerospike python client."
    sys.exit(1)

class TestRemovebin(object):
    def setup_class(cls):
        """
        Setup class.
        """
        config = {
            'hosts': [('127.0.0.1', 3000)]
        }
        TestRemovebin.client = aerospike.client(config).connect()

    def teardown_class(cls):
        TestRemovebin.client.close()

    def setup_method(self, method):
        """
        Setup method.
        """
        for i in xrange(5):
            key = ('test', 'demo', i)
            rec = {
                'name' : 'name%s' % (str(i)),
                'age' : i
            }
            TestRemovebin.client.put(key, rec)

    def teardown_method(self, method):
        """
        Teardoen method.
        """
        for i in xrange(5):
            key = ('test', 'demo', i)
            (key , meta, bins) = TestRemovebin.client.get(key)
            if bins != None:
                TestRemovebin.client.remove(key)

    def test_remove_bin_with_no_parameters(self):
        """
        Invoke remove_bin() without any mandatory parameters.
        """
        with pytest.raises(TypeError) as typeError:
            TestRemovebin.client.remove_bin()
        assert "Required argument 'key' (pos 1) not found" in typeError.value

    def test_remove_bin_with_correct_parameters(self):
        """
        Invoke remove_bin() with correct parameters
        """
        key = ('test', 'demo', 1)
        TestRemovebin.client.remove_bin(key, ["age"])


        (key , meta, bins) = TestRemovebin.client.get(key)

        assert bins == { 'name': 'name1'}

    def test_remove_bin_with_correct_policy(self):
        """
        Invoke remove_bin() with correct policy
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 1000
        }
        TestRemovebin.client.remove_bin(key, ["age"], {}, policy)


        (key , meta, bins) = TestRemovebin.client.get(key)

        assert bins == { 'name': 'name1'}

    def test_remove_bin_with_policy_send_gen_ignore(self):
        """
        Invoke remove_bin() with policy send
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 1000,
            'retry': aerospike.POLICY_RETRY_ONCE,
            'key': aerospike.POLICY_KEY_SEND,
            'gen': aerospike.POLICY_GEN_IGNORE
        }
        meta = {
            'gen': 2,
            'ttl': 1000
        }
        TestRemovebin.client.remove_bin(key, ["age"], meta, policy)


        (key , meta, bins) = TestRemovebin.client.get(key)

        assert bins == { 'name': 'name1'}
        assert key == ('test', 'demo', None,
                bytearray(b'\xb7\xf4\xb88\x89\xe2\xdag\xdeh>\x1d\xf6\x91\x9a\x1e\xac\xc4F\xc8'))

    def test_remove_bin_with_policy_send_gen_eq_positive(self):
        """
        Invoke remove_bin() with policy gen eq less
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 1000,
            'retry': aerospike.POLICY_RETRY_ONCE,
            'key': aerospike.POLICY_KEY_SEND,
            'gen': aerospike.POLICY_GEN_EQ
        }

        (key, meta) = TestRemovebin.client.exists(key)
        gen = meta['gen']
        meta = {
            'gen': gen,
            'ttl': 1000
        }

        TestRemovebin.client.remove_bin(key, ["age"], meta, policy)


        (key , meta, bins) = TestRemovebin.client.get(key)

        assert bins == { 'name': 'name1'}
        assert key == ('test', 'demo', None,
                bytearray(b'\xb7\xf4\xb88\x89\xe2\xdag\xdeh>\x1d\xf6\x91\x9a\x1e\xac\xc4F\xc8'))

    def test_remove_bin_with_policy_send_gen_eq_not_equal(self):
        """
        Invoke remove_bin() with policy gen eq not equal
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 1000,
            'retry': aerospike.POLICY_RETRY_ONCE,
            'key': aerospike.POLICY_KEY_SEND,
            'gen': aerospike.POLICY_GEN_EQ
        }
        (key, meta) = TestRemovebin.client.exists(key)
        gen = meta['gen']
        meta = {
            'gen': gen + 5,
            'ttl': 1000
        }

        with pytest.raises(Exception) as exception:
            TestRemovebin.client.remove_bin(key, ["age"], meta, policy)

        assert exception.value[0] == 3
        assert exception.value[1] == "AEROSPIKE_ERR_RECORD_GENERATION"


        (key , meta, bins) = TestRemovebin.client.get(key)

        assert bins == { 'age': 1, 'name': 'name1'}
        assert key == ('test', 'demo', None,
                bytearray(b'\xb7\xf4\xb88\x89\xe2\xdag\xdeh>\x1d\xf6\x91\x9a\x1e\xac\xc4F\xc8'))

    def test_remove_bin_with_policy_send_gen_GT_lesser(self):
        """
        Invoke remove_bin() with policy gen GT lesser
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 1000,
            'retry': aerospike.POLICY_RETRY_ONCE,
            'key': aerospike.POLICY_KEY_SEND,
            'gen': aerospike.POLICY_GEN_GT
        }

        (key, meta) = TestRemovebin.client.exists(key)
        gen = meta['gen']
        meta = {
            'gen': gen,
            'ttl': 1000
        }

        with pytest.raises(Exception) as exception:
            TestRemovebin.client.remove_bin(key, ["age"], meta, policy)

        assert exception.value[0] == 3
        assert exception.value[1] == "AEROSPIKE_ERR_RECORD_GENERATION"


        (key , meta, bins) = TestRemovebin.client.get(key)

        assert bins == { 'age': 1, 'name': 'name1'}
        assert key == ('test', 'demo', None,
                bytearray(b'\xb7\xf4\xb88\x89\xe2\xdag\xdeh>\x1d\xf6\x91\x9a\x1e\xac\xc4F\xc8'))

    def test_remove_bin_with_policy_send_gen_GT_positive(self):
        """
        Invoke remove_bin() with policy gen GT positive
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 1000,
            'retry': aerospike.POLICY_RETRY_ONCE,
            'key': aerospike.POLICY_KEY_SEND,
            'gen': aerospike.POLICY_GEN_GT
        }

        (key, meta) = TestRemovebin.client.exists(key)
        gen = meta['gen']
        meta = {
            'gen': gen + 5,
            'ttl': 1000
        }

        TestRemovebin.client.remove_bin(key, ["age"], meta, policy)


        (key , meta, bins) = TestRemovebin.client.get(key)

        assert bins == { 'name': 'name1'}
        assert key == ('test', 'demo', None,
                bytearray(b'\xb7\xf4\xb88\x89\xe2\xdag\xdeh>\x1d\xf6\x91\x9a\x1e\xac\xc4F\xc8'))

    def test_remove_bin_with_policy_key_digest(self):
        """
        Invoke remove_bin() with policy key digest
        """
        key = ( 'test', 'demo', None, bytearray("asd;as[d'as;djk;uyfl",
               "utf-8"))
        rec = {
            'age': 1,
            'name': 'name1'
        }
        TestRemovebin.client.put(key, rec)
        policy = {
            'timeout': 1000,
            'key': aerospike.POLICY_KEY_DIGEST
        }
        TestRemovebin.client.remove_bin(key, ["age"], {}, policy)


        (key , meta, bins) = TestRemovebin.client.get(key)

        assert bins == { 'name': 'name1'}
        assert key == ('test', 'demo', None,
                bytearray(b"asd;as[d\'as;djk;uyfl"))

        TestRemovebin.client.remove(key)

    def test_remove_bin_with_incorrect_policy(self):
        """
        Invoke remove_bin() with incorrect policy
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 0.5
        }
        with pytest.raises(Exception) as exception:
            TestRemovebin.client.remove_bin(key, ["age"], {}, policy)

        assert exception.value[0] == -1
        #assert exception.value[1] == "Invalid value(type) for policy key"
        assert exception.value[1] == "Incorrect policy"

    def test_remove_bin_with_nonexistent_key(self):
        """
        Invoke remove_bin() with non-existent key
        """
        key = ('test', 'demo', "non-existent")
        status = TestRemovebin.client.remove_bin(key, ["age"])

        assert status == 0L

    def test_remove_bin_with_nonexistent_bin(self):
        """
        Invoke remove_bin() with non-existent bin
        """
        key = ('test', 'demo', 1)
        status = TestRemovebin.client.remove_bin(key, ["non-existent"])

        assert status == 0L

    def test_remove_bin_with_extra_parameter(self):
        """
        Invoke remove_bin() with extra parameter.
        """
        key = ('test', 'demo', 1)
        policy = {
            'timeout': 1000
        }
        with pytest.raises(TypeError) as typeError:
            TestRemovebin.client.remove_bin(key, ["age"], {}, policy, "")

        assert "remove_bin() takes at most 4 arguments (5 given)" in typeError.value

    def test_remove_bin_key_is_none(self):
        """
        Invoke remove_bin() with key is none
        """
        with pytest.raises(Exception) as exception:
            TestRemovebin.client.remove_bin(None, ["age"])

        assert exception.value[0] == -2
        assert exception.value[1] == "key is invalid"

    def test_remove_bin_bin_is_none(self):
        """
        Invoke remove_bin() with bin is none
        """
        key = ('test', 'demo', 1)
        with pytest.raises(Exception) as exception:
            TestRemovebin.client.remove_bin(key, None)

        assert exception.value[0] == -2
        assert exception.value[1] == "Bins should be a list"

    def test_remove_bin_no_bin(self):
        """
        Invoke remove_bin() no bin
        """
        key = ('test', 'demo', 1)
        TestRemovebin.client.remove_bin(key, [])


        (key , meta, bins) = TestRemovebin.client.get(key)

        assert bins == { 'name': 'name1', 'age': 1}

    def test_remove_bin_all_bins(self):
        """
        Invoke remove_bin() all bins
        """
        key = ('test', 'demo', 1)
        TestRemovebin.client.remove_bin(key, ["name", "age"])


        (key , meta, bins) = TestRemovebin.client.get(key)

        assert bins == None

    def test_remove_bin_with_unicode_binname(self):
        """
        Invoke remove_bin() with unicode bin name
        """
        key = ('test', 'demo', 2)

        TestRemovebin.client.remove_bin(key, [u"name"])

        (key , meta, bins) = TestRemovebin.client.get(key)

        assert bins == { 'age': 2 }

        key = ('test', 'demo', 3)

        TestRemovebin.client.remove_bin(key, [u"name", "age"])

        (key , meta, bins) = TestRemovebin.client.get(key)

        assert bins == None

        key = ('test', 'demo', 4)

        TestRemovebin.client.remove_bin(key, ["name", u"age"])

        (key , meta, bins) = TestRemovebin.client.get(key)

        assert bins == None
