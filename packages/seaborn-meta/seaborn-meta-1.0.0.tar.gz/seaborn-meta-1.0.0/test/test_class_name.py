import unittest
from seaborn_meta.class_name import *


class TestClassName(unittest.TestCase):
    def test_class_name_to_instant_name(self):
        self.assertEqual("parent_name.child_name",
                         class_name_to_instant_name("ParentName_ChildName"))

    def test_instant_name_to_class_name(self):
        self.assertEqual("ParentName_ChildName",
                         instant_name_to_class_name("parent_name.child_name"))

    def test_create_init_files(self):
        success = True
        path = os.path.join(os.path.dirname(__file__), 'data')
        create_init_files(path)

        try:
            with open(os.path.join(path, '__init__.py'), 'r') as fn:
                self.assertEqual('from a import *\nfrom b import *\nimport c\n',
                                 fn.read())
            with open(os.path.join(path, 'c', '__init__.py'), 'r') as fn:
                self.assertEqual('from c import *\n', fn.read())
        finally:
            os.remove(os.path.join(path, '__init__.py'))
            os.remove(os.path.join(path, 'c', '__init__.py'))


if __name__ == '__main__':
    unittest.main()
