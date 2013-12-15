#coding=UTF-8
import urllib2, re
from random import shuffle

""" Contains all the important urlfiddle functions for now """
class Fiddle:

    def __init__(self):
        # Define parameter templates
        self.exNumeric = re.compile(r"§(\d+)\-(\d+)§")
        self.exFile = re.compile(r"§f=([^§]*)§")
        self.exFuzz = re.compile(r"§fuzz=(\d+),(\d+)§")
    
    # Recursive fiddle function. Hey, it's even tail-recursive :)
    def generate(self,urllist, ex, str_pos, arguments):
        if (len(urllist) == 0):
            return
        m = ex.search(urllist[0])  # Assume that all urls in urllist are identical
        if m is None:
            return urllist
        else:
            urllist_extended = []
            args = arguments.pop(0)
            for url in urllist:
                for arg in args:
                    urllist_extended.append(ex.sub(str(arg), url, 1))
            return self.generate(urllist_extended, ex, m.pos + 1, arguments)
    
    # Simple fuzzer function. Return a list with listlen elements of length fuzzlen and iterate through source list
    def autofuzz(self,fuzzlen, listlen):
        source = ["--", '"', '"', ">", "<", "/>", "\>", "$", "%", "(", ")", "*", "+", ".", "\\", "`", "&", chr(0x00), chr(0x08), chr(0x09), chr(0x0a), chr(0x0d), chr(0x1a)]
        shuffle(source)
        fuzzlist = []
        for i in range(0, listlen):
            indexStart = i * fuzzlen % len(source)
            indexEnd = indexStart + fuzzlen
            fuzzlist.append(urllib2.quote("".join(source[indexStart:indexEnd])))
        return fuzzlist
    
    # Detect numeric placeholders
    def detectNumerics(self, url):
        numerics = self.exNumeric.findall(url)
        rangeNumerics = []
        for i in numerics:
            rangeNumerics.append(range(int(i[0]), int(i[1]) + 1))
        return rangeNumerics
    
    # Detect file placeholders
    def detectFiles(self, url,urlencode):
        rangeFiles = []
        files = self.exFile.findall(url)
        for infile in files:
            if(urlencode):
                lines = [urllib2.quote(line.rstrip("\n")) for line in open(infile)]
                rangeFiles.append(lines)
            else:
                lines = [line.rstrip("\n") for line in open(infile)]
                rangeFiles.append(lines)
        return rangeFiles
    
    # Detect fuzzing placeholders
    def detectFuzz(self, url):
        rangeFuzz = []
        fuzzes = self.exFuzz.findall(url)
        for param in fuzzes:
            rangeFuzz.append(self.autofuzz(int(param[0]), int(param[1])))
        return rangeFuzz