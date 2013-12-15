#!/usr/bin/python
# coding=UTF-8
import subprocess, re, sys, argparse, urllib2, signal, httplib
from time import time, sleep
from hashlib import md5 
from fiddle import Fiddle
###########
# Classes #
###########
class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"
    
    
class CustomRedirectHandler(urllib2.HTTPRedirectHandler):
    doFollow = True
    def http_error_301(self, req, fp, code, msg, headers):
        if(not self.doFollow):
            return None
        result = urllib2.HTTPRedirectHandler.http_error_301(
            self, req, fp, code, msg, headers)
        result.status = code
        return result
    
    http_error_302 = http_error_303 = http_error_307 = http_error_301

#############
# Functions #
#############

# Exit cleanly on keyboard interrupt
def exithandler(signum, frame):
    sys.stdout.write("\n")
    sys.exit(0)


    
# Command line options
def parse_args():
    parser = argparse.ArgumentParser(description="", epilog="Visit the project homepage on https://github.com/mhelwig/urlfiddle if you need more information")
    parser.add_argument('url', type=str, help='The URL to fiddle', metavar='URL')
    parser.add_argument('-d', '--delay', type=float, help="Delay between calls", metavar='seconds',)
    parser.add_argument('-a', '--set-user-agent', help="Send user agent information with requests")
    parser.add_argument('-p', '--prefix', help="Prefix of output files", metavar='Prefix', default='')
    parser.add_argument('-o', '--output', help="Suffix of output files (default \"html\")", metavar='Suffix', default='html')
    parser.add_argument('-s', '--silent', help="Silent mode: Just print out urls and do not call them", action='store_true')
    parser.add_argument('-u', '--urlencode', help="urlencode parameter values", action='store_true')
    parser.add_argument('-5', '--md5', help="Output the MD5 value of responses", action='store_true')
    parser.add_argument('-r', '--no-redirect', help="Do NOT follow redirects", action='store_true')
    parser.add_argument('-f', '--file', help="Process urls from file")
    parser.add_argument('-q', '--quiet', help="Suppress copyright notice", action='store_true')
    parser.add_argument('--stdout', help="Pass response to stdout", action='store_true')
    parser.add_argument('-H', '--head', help="Only do HEAD requests", action='store_true')
    parser.add_argument('--headers', help="Print response headers", action='store_true')
    parser.add_argument('-S', '--status', help="Print status code", action='store_true')
    parser.add_argument('-t', '--time', help="Measure response time", action='store_true')
    parser.add_argument('-c', '--set-cookie', help="Send Cookie with requests")
    parser.add_argument('--screenshot', help="Take screenshot using wkhtmltoimage. You have to provide the path to the binary as argument here. Implies --write.", metavar='/path/to/wkhtmltoimage')
    parser.add_argument('-w', '--write', help="Write output to file", action="store_true")
    
    args = parser.parse_args()
    return args

########
# Main #
########
def main():
    # Exit cleanly on keyboard interrupt
    signal.signal(signal.SIGINT, exithandler)
    
    args = parse_args()
    fiddle = Fiddle()
    
    if not args.quiet:
        print("urlfiddle - url manipulation tool by Michael Helwig (info@jhp-consulting.eu)")
    
    # Load or generate arguments
    rangeNumerics = fiddle.detectNumerics(args.url)
    rangeFiles = fiddle.detectFiles(args.url, args.urlencode)
    rangeFuzz = fiddle.detectFuzz(args.url)
    
    if(rangeFuzz is not None and not args.urlencode):
        print "Notice: Fuzzed parameters are urlencoded by default."
    
    # Load urls
    urllist = []
    
    if args.file:
        urllist = [line.rstrip("\n") for line in open(args.file)]
    
    urllist.append(args.url)
    
    # Generate urls
    urllist = fiddle.generate(urllist, fiddle.exNumeric, 0, rangeNumerics)
    urllist = fiddle.generate(urllist, fiddle.exFile, 0, rangeFiles)
    urllist = fiddle.generate(urllist, fiddle.exFuzz, 0, rangeFuzz)
    
    # Do the calls
    for idx, url in enumerate(urllist):
        if(args.silent):
            print url
            continue
        else:
            sys.stdout.write("[" + str(idx) + "]\t" + url)
        response = None
        responseStartTime = 0
        responseTime = 0
        responseError = None
        responseErrorText = None
        responseText = None
        
        redirectHandler = CustomRedirectHandler()
        if(args.no_redirect):
            redirectHandler.doFollow = False
        urlopener = urllib2.build_opener(redirectHandler)
        
        if(args.set_cookie):
            urlopener.addheaders.append(('Cookie', args.set_cookie))
        if(args.set_user_agent):
            urlopener.addheaders.append(('User-agent', args.set_user_agent))
        if(args.time):
            responseStartTime = time()
        try:
            if(args.head):
                response = urlopener.open(HeadRequest(url))
            else:
                response = urlopener.open(url)
            responseText = response.read()
        except urllib2.URLError as e:
                responseError = e
                responseErrorText = str(e.code)
        except httplib.HTTPException as e:
                responseError = e
                responseErrorText = e.__class__.__name__
        except urllib2.URLError as e:
            print("Invalid URL. Try to encode your parameters with --urlencode")
        if(args.time):
            responseTime = time() - responseStartTime
        if(args.status):
            sys.stdout.write("\t")
            if responseErrorText is None:
                try:
                    sys.stdout.write(str(response.status))
                except AttributeError:
                    sys.stdout.write(str(response.getcode()))
                    
            else:
                sys.stdout.write(responseErrorText)
        if(args.time):
            sys.stdout.write("\t" + str(responseTime))
        if(args.headers and responseError is None):
            sys.stdout.write("\n")
            print response.info()
        if(args.md5 and responseError is None):
            m = md5()
            m.update(responseText)
            sys.stdout.write("\t" + m.hexdigest())
        elif(args.md5):
            sys.stdout.write("\t")
        if(args.stdout and responseError is None):
            print("\n" + responseText)
        if((args.write or args.screenshot) and not args.head and responseError is None):
            fopen = open(args.prefix + str(idx) + "." + args.output, "w+")
            fopen.write(responseText)
            fopen.flush()
            if(args.screenshot):
                devnull = open('/dev/null', 'w')
                subprocess.call([args.screenshot, "-f", "png", fopen.name, fopen.name + ".png"], stdout=devnull, stderr=devnull)
            fopen.close()
        if(args.delay > 0):
            sleep(args.delay)
        sys.stdout.write("\n")    
