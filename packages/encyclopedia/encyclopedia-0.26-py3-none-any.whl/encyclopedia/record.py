# standard
import unittest
import types
import sys
# external
# internal
from encyclopedia.dictionary import Dictionary
from encyclopedia.templates import Unindexed

class Record(dict, Unindexed):
    '''
    A factory creating Encyclopedia-ified Dictionaries with:

    - restricted keys
    - automatic type conversions and restrictions
    - optional defaults
    '''

    def __init__(self, mapping=None, autopopulate=False):
        if mapping is not None:
            self.update(mapping)
        self.autopopulate = autopopulate

    def __setitem__(self, key, value):
        assert isinstance(value, types.FunctionType)
        value()  # assert it works with no parameters
        return dict.__setitem__(self, key, value)

    @staticmethod
    def _missing(key):
        raise Exception("Missing record key:" + key)

    def instance(self):
        '''
        create an individual (Record) instance
        '''

        class Internal(Dictionary):

            def __init__(dictionary, mapping=None):
                dictionary.frozen=False
                if mapping is not None:
                    dictionary.update(mapping)
                if self.autopopulate:
                    for key in self:
                        dictionary[key] = self[key]()

            def __setitem__(dictionary, key, value):
                if key not in self:
                    Record._missing(key)
                dict.__setitem__(dictionary, key, self[key](value)) # cast type

        return Internal()

class Test_Record(unittest.TestCase):

    def setUp(self):

        def noname(x = None, default='ANONYMOUS'):
            if x is None:
                return default
            else:
                return str(x)

        record = Record({
            'coat': str,
            'tail':int,
            'name':noname,
            'age':float,
            'height':float
            },
            autopopulate=True
            )
        self.Dog = record.instance

    def test_defaults(self):
        harley=self.Dog()
        assert len(harley) == len(self.Dog()) # because it's autopopulated
        assert harley['tail'] == 0
        assert harley['name'] == 'ANONYMOUS'
        harley['name'] = 'Mr. Rascal'
        assert harley['name'] == 'Mr. Rascal'
        assert harley['age'] == 0

    def test_basic(self):
        '''
        test basic functions of Record
        '''
        harley = self.Dog()
        harley['tail'] = 3
        assert harley['tail'] == 3
        try:
            harley['teeth'] = 5 # this is not a valid key
            assert False
        except:
            pass

    def test_sizing(self):
        '''
        assure that the resultant dictionaries do not chew up memory
        Note: can also use https://pypi.python.org/pypi/Pympler to confirm this but
        chose minimize external dependencies
        '''
        n = 10**4
        keys = range(1, n)
        record = Record({key:int for key in keys}).instance()
        dictionary = {}
        for i in range(1, n):
            record[i] = i
            dictionary[i] = i
        assert (sys.getsizeof(record) - sys.getsizeof(dictionary) < 20) # bytes

if __name__ == '__main__':
    unittest.main()