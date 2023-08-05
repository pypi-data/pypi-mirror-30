import teager

from unittest import TestCase

class SymItem(object):
    def __init__(self, n, p, l):
        self.name = n
        self.path = p
        self.line = l

class Callback(object):
    def __init__(self):
        self.syms = []

    def __call__(self, symbol=None, filename=None, lineno=None):
        s = SymItem(symbol, filename, lineno)
        self.syms.append(s)

class TeagerFunctionTests(TestCase):

    def test_single_function_c(self):
        callback = Callback()
        teager.parse("test/files/test_single_function.c", callback)
        self.assertEqual(len(callback.syms), 1)
        self.assertEqual(callback.syms[0].name, "only_one_function") 
        self.assertEqual(callback.syms[0].path, "test/files/test_single_function.c") 
        self.assertEqual(callback.syms[0].line, 1) 

    def test_single_function_cpp(self):
        callback = Callback()
        teager.parse("test/files/test_single_function.cpp", callback)
        self.assertEqual(len(callback.syms), 1)
        self.assertEqual(callback.syms[0].name, "only_one_function") 
        self.assertEqual(callback.syms[0].path, "test/files/test_single_function.cpp") 
        self.assertEqual(callback.syms[0].line, 1)
    
    def test_multiple_functions_c(self):
        callback = Callback()
        teager.parse("test/files/test_multiple_functions.c", callback)
        
        self.assertEqual(len(callback.syms), 4)
        
        self.assertEqual(callback.syms[0].name, "function_one")
        self.assertEqual(callback.syms[0].line, 1)

        self.assertEqual(callback.syms[1].name, "function_two")
        self.assertEqual(callback.syms[1].line, 5)

        self.assertEqual(callback.syms[2].name, "function_three")
        self.assertEqual(callback.syms[2].line, 9)

        self.assertEqual(callback.syms[3].name, "function_four")
        self.assertEqual(callback.syms[3].line, 13)

    def test_multiple_functions_cpp(self):
        callback = Callback()
        teager.parse("test/files/test_multiple_functions.cpp", callback)
        
        self.assertEqual(len(callback.syms), 4)
        
        self.assertEqual(callback.syms[0].name, "function_one")
        self.assertEqual(callback.syms[0].line, 1)

        self.assertEqual(callback.syms[1].name, "function_two")
        self.assertEqual(callback.syms[1].line, 5)

        self.assertEqual(callback.syms[2].name, "function_three")
        self.assertEqual(callback.syms[2].line, 9)

        self.assertEqual(callback.syms[3].name, "function_four")
        self.assertEqual(callback.syms[3].line, 13)

    def test_namespace_handling(self):
        callback = Callback()
        teager.parse("test/files/test_naspace_handling.cpp", callback)
        
        self.assertEqual(len(callback.syms), 4)
        self.assertEqual(callback.syms[0].name, "in_namespace_testing_internal")
        self.assertEqual(callback.syms[1].name, "in_namespace_testing")
        self.assertEqual(callback.syms[2].name, "in_namespace_external")
        self.assertEqual(callback.syms[3].name, "in_namespace_anon")

    def test_exception_safety(self):
        class TeagerTestEx(Exception):
            pass

        def callback(**kwargs):
            raise TeagerTestEx('Its a test')
        
        with self.assertRaises(TeagerTestEx):
            teager.parse("test/files/test_naspace_handling.cpp", callback)
