import unittest
from zope.testing import doctest

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('pkgloader.txt',
                             package='p4a.z2utils'),
        ))
