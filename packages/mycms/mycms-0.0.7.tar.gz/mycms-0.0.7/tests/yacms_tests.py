from __future__ import print_function
import unittest
import mock

#from mycms import views
from tests.utilities import module_function_name


class TestPackageSkel(unittest.TestCase):
    
    #@mock.patch(module_function_name(print))
    #def test_should_print_hello_world(self, mock_print):
        #mock_print.assert_called_once_with('Hello world!')

    def test_hello(self):
        self.assertEqual(1,1)	
