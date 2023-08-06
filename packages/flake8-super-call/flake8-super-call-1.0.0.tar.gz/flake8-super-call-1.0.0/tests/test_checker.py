import ast
import unittest

from flake8_super_call import Checker


def check(should_fail=False):
    super_class = 'self.__class__' if should_fail else 'ClassName'
    tree = ast.parse('super({}, self)'.format(super_class))
    return next(Checker(tree).run(), None)


class TestChecker(unittest.TestCase):

    def test_bad_super_call(self):
        lineno, offset, message, _ = check(should_fail=True)
        self.assertEqual(lineno, 1)
        self.assertEqual(offset, 0)
        self.assertTrue(message.startswith('S777'))

    def test_good_super_call(self):
        self.assertIsNone(check())


if __name__ == '__main__':
    unittest.main()
