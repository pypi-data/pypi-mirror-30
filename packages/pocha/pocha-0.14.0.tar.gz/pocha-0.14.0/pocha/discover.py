"""
pocha test discovery module responsible for creating a dictionary containing
the testing hierarchy as represented by the underlying tests.

"""
import os
import imp
import sys

from collections import OrderedDict

from pocha import common


def __load_modules(path):
    modules = []

    if os.path.isfile(path) and path.endswith('.py'):
        modules.append(path)

    elif os.path.isdir(path):
        # we do recursively attempt to find tests in a directory that contains
        # the pocha.ignore file in it
        if os.path.exists(os.path.join(path, 'pocha.ignore')):
            return modules

        for filename in os.listdir(path):
            if filename == '__init__.py':
                continue

            modules += __load_modules(os.path.join(path, filename))

    return modules

class FalseyDict(dict):

    def __init__(self, dictionary):
        self.dict = dictionary

    def __getitem__(self, key):

        if key in self.dict.keys():
            return self.dict[key]

        else:
            # by returning False the evaluation can happen for tags that
            # are not defined
            return False


def filter_tests(tests, expression):
    filtered_tests = OrderedDict()

    for (key, thing) in tests.items():
        if thing.only:
            return OrderedDict({
                thing.name: thing
            })

        if thing.type == 'test':
            if expression is None:
                filtered_tests[key] = thing
                continue

            global_tags = FalseyDict(thing.tags)

            if eval(expression, global_tags):
                filtered_tests[key] = thing

        elif thing.type == 'suite':
            thing.tests = filter_tests(thing.tests, expression)

            if len(thing.tests) != 0:
                filtered_tests[key] = thing

    return filtered_tests


def search(path, expression):
    modules = __load_modules(path)

    # load each module and then we'll have a complete list of the tests
    # to run
    for module in modules:
        module_path = os.path.dirname(module)

        # handle special case of a relative reference to something in a parent
        # directory
        if module.startswith('..'):
            sys.path.insert(0, '..')
            module = module.replace('../', '')

        sys.path.insert(0, module_path)
        sys.path.insert(0, '.')
        try:
            name = module.replace('/', '.')
            if '.py' in name:
                name = name[:name.index('.py')]
            __import__(name)
        finally:
            sys.path.remove('.')
            sys.path.remove(module_path)

    return filter_tests(common.TESTS, expression)
