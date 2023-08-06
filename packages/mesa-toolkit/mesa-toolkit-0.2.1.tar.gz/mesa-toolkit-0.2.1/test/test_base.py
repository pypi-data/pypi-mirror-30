import unittest

# modules under test
from mesa import base
from mesa import utils

# supporting test data
from example import interface, callback

# required modules for tests
import getpass


# python -m unittest test_base

class MesaTest(unittest.TestCase):
    trike = './example/concrete/trike.py'

    def setUp(self):
        self.concrete = base.Casa('example.concrete', interface=interface.Vehicle)
        self.trike = MesaTest.trike

    @classmethod
    def tearDownClass(cls):
        from pathlib import Path
        # if trike exists, delete
        p = Path(MesaTest.trike)
        if p.exists():
            p.unlink()

    # test all classes get loaded
    def test_all_classes_loaded(self):
        self.assertEqual(self.concrete.casa.keys(), {'Bike', 'Bus', 'Car'})

    # test dynamic update
    def test_new_class_loaded(self):
        import os
        # create some new file in concrete
        trike = './example/concrete/trike.py'
        with open(trike, 'w') as f:
            f.write('''
from example import interface

class Trike(interface.Vehicle):
 def __init__(self):
  pass

 def horn(self):
  print('tingaling!')

 def get_engine_size(self):
  return 0.01

 def get_soot_count(self, emissions):
  return ''

 def start(self):
  return []
''')
        self.concrete.rebuild()
        self.assertTrue('Trike' in self.concrete.casa.keys())
        os.remove(trike)
        self.concrete.rebuild()

    # test function calls
    def test_generator_function(self):
        self.assertEqual({x[1] for x in self.concrete.next('get_engine_size')}, {1, 2, 10})

    def test_generate_function(self):
        self.assertEqual(self.concrete.generate('get_engine_size'), {'Bike': 1, 'Car': 2, 'Bus': 10})

    def test_generate_params(self):
        self.assertEqual(self.concrete.generate('get_soot_count', 10), {
            'Car': 'emissions are 10 so soot is medium',
            'Bike': 'emissions are 10 but it\'s a bike so soot is low',
            'Bus': 'emissions are 10 but bus is a diesel so soot is high'
        })

    def test_mesa_method(self):
        start_vehicle = self.concrete.interface.start()
        compare_results = [{'Bike': 'door', 'Car': 'door', 'Bus': 'door'}, {'Bike': 'key', 'Car': 'key', 'Bus': 'key'}]
        results = []
        for step in start_vehicle:
            results.append(self.concrete.generate(step.name))
        self.assertEqual(results, compare_results)

    def test_mesa_method_cb(self):
        # take first vehicle instance in casa
        v = list(self.concrete.casa.items())[0][1]
        service_vehicle = v.service()
        compare_results = ['checking breaks', {'level': 5},
                           ({'password': 'letmein', 'grade': 'low', 'garage url': 'http://example.com'})]
        results = []
        results = utils.run_mesa_methods(v, service_vehicle, callback.CBInstance())
        self.assertEqual(results, compare_results)


if __name__ == '__main__':
    unittest.main()
