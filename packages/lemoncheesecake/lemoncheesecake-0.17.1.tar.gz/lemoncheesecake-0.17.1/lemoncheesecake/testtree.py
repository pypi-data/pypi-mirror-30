'''
Created on Jun 16, 2017

@author: nicolas
'''

import copy

from lemoncheesecake.utils import get_distincts_in_list
from lemoncheesecake.exceptions import CannotFindTreeNode


class TreeLocation(object):
    TEST_SESSION_SETUP = 0
    TEST_SESSION_TEARDOWN = 1
    SUITE_SETUP = 2
    SUITE_TEARDOWN = 3
    TEST = 4

    def __init__(self, node_type, node_hierarchy=None):
        self.node_type = node_type
        self.node_hierarchy = node_hierarchy
    
    @classmethod
    def in_test_session_setup(cls):
        return cls(cls.TEST_SESSION_SETUP)
    
    @classmethod
    def in_test_session_teardown(cls):
        return cls(cls.TEST_SESSION_TEARDOWN)
    
    @classmethod
    def in_suite_setup(cls, suite):
        return cls(cls.SUITE_SETUP, suite)
    
    @classmethod
    def in_suite_teardown(cls, suite):
        return cls(cls.SUITE_TEARDOWN, suite)

    @classmethod
    def in_test(cls, test):
        return cls(cls.TEST, test)


class BaseTreeNode(object):
    def __init__(self, name, description):
        self.parent_suite = None
        self.name = name
        self.description = description
        self.tags = []
        self.properties = {}
        self.links = []

    @property
    def hierarchy(self):
        if self.parent_suite is not None:
            for node in self.parent_suite.hierarchy:
                yield node
        yield self

    @property
    def hierarchy_depth(self):
        return len(list(self.hierarchy)) - 1

    @property
    def path(self):
        return ".".join([s.name for s in self.hierarchy])

    @property
    def hierarchy_paths(self):
        return map(lambda node: node.path, self.hierarchy)

    @property
    def hierarchy_descriptions(self):
        return map(lambda node: node.description, self.hierarchy)

    @property
    def hierarchy_tags(self):
        tags = []
        for node in self.hierarchy:
            tags.extend(node.tags)
        return get_distincts_in_list(tags)

    @property
    def hierarchy_properties(self):
        properties = {}
        for node in self.hierarchy:
            properties.update(node.properties)
        return properties

    @property
    def hierarchy_links(self):
        links = []
        for node in self.hierarchy:
            links.extend(node.links)
        return get_distincts_in_list(links)

    def pull_node(self):
        node = copy.copy(self)
        node.parent_suite = None
        return node

    def __str__(self):
        return self.path


class BaseTest(BaseTreeNode):
    pass


class BaseSuite(BaseTreeNode):
    def __init__(self, name, description):
        BaseTreeNode.__init__(self, name, description)
        self._tests = []
        self._suites = []

    def add_test(self, test):
        test.parent_suite = self
        self._tests.append(test)

    def get_tests(self):
        return self._tests

    def add_suite(self, suite):
        suite.parent_suite = self
        self._suites.append(suite)

    def get_suites(self, include_empty_suites=False):
        if include_empty_suites:
            return self._suites
        else:
            return list(filter(lambda suite: not suite.is_empty(), self._suites))

    def is_empty(self):
        if len(self.get_tests()) != 0:
            return False

        for sub_suite in self.get_suites():
            if not sub_suite.is_empty():
                return False

        return True

    def pull_node(self):
        node = BaseTreeNode.pull_node(self)
        node._tests = []
        node._suites = []
        return node


def flatten_suites(suites):
    for suite in suites:
        yield suite
        for sub_suite in flatten_suites(suite.get_suites()):
            yield sub_suite


def flatten_tests(suites):
    for suite in flatten_suites(suites):
        for test in suite.get_tests():
            yield test


def _normalize_node_hierarchy(value):
    if isinstance(value, BaseTreeNode):
        return [p.name for p in value.hierarchy]
    else:
        return value.split(".")


def get_suite_by_name(suites, suite_name):
    try:
        return next(s for s in suites if s.name == suite_name)
    except StopIteration:
        raise CannotFindTreeNode("Cannot find suite named '%s'" % suite_name)


def _find_suite(suites, hierarchy):
    lookup_suites = suites
    lookup_suite = None
    for lookup_suite_name in hierarchy:
        lookup_suite = get_suite_by_name(lookup_suites, lookup_suite_name)
        lookup_suites = lookup_suite.get_suites(include_empty_suites=True)
    if lookup_suite is None:
        raise CannotFindTreeNode("Cannot find suite named %s" % hierarchy)

    return lookup_suite


def find_suite(suites, hierarchy):
    return _find_suite(suites, _normalize_node_hierarchy(hierarchy))


def get_test_by_name(suite, test_name):
    try:
        return next(t for t in suite.get_tests() if t.name == test_name)
    except StopIteration:
        raise CannotFindTreeNode("Cannot find test named '%s'" % test_name)


def _find_test(suites, hierarchy):
    lookup_suite = _find_suite(suites, hierarchy[:-1])
    return get_test_by_name(lookup_suite, hierarchy[-1])


def find_test(suites, hierarchy):
    return _find_test(suites, _normalize_node_hierarchy(hierarchy))
