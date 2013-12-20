# coding=UTF-8

import unittest, re
from ..fiddle import Fiddle

class TestUrlfiddle(unittest.TestCase):

    baseUrlHttp = "http://www.example.tld"
    
    def setUp(self):
        self.exNumeric = re.compile(r"§(\d+)\-(\d+)§")
        self.exFile = re.compile(r"§f=([^§]*)§")
        self.exFuzz = re.compile(r"§fuzz=(\d+),(\d+)§")
        self.fiddle = Fiddle()
    
    def testGenerateNumeric(self):
        urlNumeric = [self.baseUrlHttp + "/index.php?id=§1-2§"]
        expected = [self.baseUrlHttp + "/index.php?id=1", self.baseUrlHttp + "/index.php?id=2"]
        urllist = self.fiddle.generate(urlNumeric, self.exNumeric, 0, [[1, 2]])
        self.assertEqual(expected, urllist)
    
    def testGenerateMultipleNumeric(self):
        urlNumeric = [self.baseUrlHttp + "/index.php?param1=§1-2§&param2=§1-2§"]
        expected = [self.baseUrlHttp + "/index.php?param1=1&param2=1", self.baseUrlHttp + "/index.php?param1=1&param2=2", self.baseUrlHttp + "/index.php?param1=2&param2=1", self.baseUrlHttp + "/index.php?param1=2&param2=2"]
        urllist = self.fiddle.generate(urlNumeric, self.exNumeric, 0, [range(1, 3), range(1, 3)])
        self.assertEqual(expected, urllist)
        
    def testDetectPlaceholders(self):
        urlMixed = self.baseUrlHttp + "/index.php?param1=§1-2§&param2=§f=myfile.txt§&param3=§fuzz=2,3§"
        numerics = self.fiddle.exNumeric.findall(urlMixed)
        files = self.fiddle.exFile.findall(urlMixed)
        fuzzes = self.fiddle.exFuzz.findall(urlMixed)
        
        self.assertEqual(numerics, [('1', '2')])
        self.assertEqual(files, ['myfile.txt'])
        self.assertEqual(fuzzes, [('2', '3')])
    
    def testGenerateAll(self):
        paramString = "param1=§1-2§&param2=§f=./urlfiddle/test/data/testfile1.txt§&param3=§fuzz=2,3§"
        paramValues = self.fiddle.generateAll(paramString, True)
        
        self.assertEqual(12,len(paramValues))
if __name__ == '__main__':
    unittest.main()
