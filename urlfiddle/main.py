#!/usr/bin/python
# coding=UTF-8
import subprocess, sys, argparse, urllib2, signal, httplib, os, math, multiprocessing, mimetypes
from time import time, sleep
from hashlib import md5 
from fiddle import Fiddle

###########
# GLOBALS #
###########

running_threads = []

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
    for t in running_threads:
        t.terminate()
    sys.exit(0)


    
# Command line options
def parse_args():
    parser = argparse.ArgumentParser(description="", epilog="Visit the project homepage on https://github.com/mhelwig/urlfiddle if you need more information")
    parser.add_argument('url', type=str, help='The URL to fiddle', metavar='URL')
    parser.add_argument('-d', '--delay', type=float, help="Delay between calls", metavar='seconds',)
    parser.add_argument('-a', '--set-user-agent', help="Send user agent information with requests")
    parser.add_argument('-M', '--mime-type', help="Print MIME content type header (if detected)", action='store_true')
    parser.add_argument('--prefix', help="Prefix of output files", metavar='Prefix', default='')
    parser.add_argument('-o', '--output-dir', help="Output directory", metavar='Suffix')
    parser.add_argument('-s', '--silent', help="Silent mode: Just print out urls and do not call them", action='store_true')
    parser.add_argument('-u', '--urlencode', help="urlencode parameter values", action='store_true')
    parser.add_argument('-5', '--md5', help="Output the MD5 value of responses", action='store_true')
    parser.add_argument('-r', '--no-redirect', help="Do NOT follow redirects", action='store_true')
    parser.add_argument('-f', '--file', help="Process urls from file")
#    parser.add_argument('-F', '--detect-forms', help="autodetect forms", action='store_true') #Not yet implemented
    parser.add_argument('-p', '--set-post', help="POST data to send with the request")
    parser.add_argument('-q', '--quiet', help="Suppress copyright notice", action='store_true')
    parser.add_argument('--stdout', help="Pass response to stdout", action='store_true')
    parser.add_argument('-H', '--head', help="Only do HEAD requests", action='store_true')
    parser.add_argument('--headers', help="Print response headers", action='store_true')
    parser.add_argument('-S', '--status', help="Print status code", action='store_true', default=True)
    parser.add_argument('-t', '--time', help="Measure response time", action='store_true')
    parser.add_argument('-c', '--set-cookie', help="Send Cookie with requests")
#   parser.add_argument('-c', '--set-header', help="set arbitrary header value") #Not yet implemented
    parser.add_argument('-P', '--processes', type=int, help="Number of processes to use for starting requests in parallel. EXPERIMENTAL", default=1)
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
    
    rangeFuzz = fiddle.detectFuzz(args.url)
    if(rangeFuzz is not None and len(rangeFuzz) > 0 and not args.urlencode):
        print "Notice: Fuzzed parameters are urlencoded by default."
    
    # Load urls
    urlTemplates = []
    
    if args.file:
        urlTemplates = [line.rstrip("\n") for line in open(args.file)]
    
    urlTemplates.append(args.url)
    
    urllist = []
    
    # Generate urls
    for urlTemplate in urlTemplates:
        urllist.extend(fiddle.generateAll(urlTemplate, args.urlencode))
    
    postParams = []
    if(args.set_post):
        postParams = fiddle.generateAll(args.set_post, args.urlencode)
          
    cookieParams = []
    if(args.set_cookie):
        cookieParams = fiddle.generateAll(args.set_cookie, args.urlencode)
    
    listSize = len(urllist)
    
    if args.processes:
        listSize = int(math.ceil(len(urllist) / args.processes))
    
    global running_threads
    
    offset = 0
    
    if args.processes > 0:
        queue = multiprocessing.Queue()
        queue.put(0)
        for i in range(1, args.processes + 1):
            partialList = urllist[offset:offset + listSize]
            new_thread = Client(partialList, args, cookieParams, postParams, queue,offset)
            running_threads.append(new_thread)
            new_thread.start()
            offset += listSize
    else:
        c = Client(urllist, args, cookieParams, postParams)
        c.run()
    
    for t in running_threads: 
        t.join()
    
         

class Client(multiprocessing.Process):
    def __init__(self, urllist, args, cookieParams, postParams, queue = None, offset=0): 
            multiprocessing.Process.__init__(self)
            self.queue = queue
            self.counter = 0
            self.lock = multiprocessing.RLock()
            self.urllist = urllist
            self.args = args
            self.cookieParams = cookieParams
            self.postParams = postParams
            self.offset = offset
            self.callcount = 0
            
            
    def run(self):
        self.call_list(self.urllist, self.postParams, self.cookieParams, self.args, self.offset)
    
    # Do the calling according to available parameters
    def call_list(self, urllist, postParams, cookieParams, args, offset):    
        for idx, url in enumerate(urllist):
            if(args.silent):
                print url
                continue
            else:
                if len(cookieParams) > 0 and len(postParams) > 0:
                    for post in postParams:
                        for cookie in cookieParams:
                            self.call(url=url, args=args, idx=idx, post=post, cookie=cookie, offset=offset)
                elif len(postParams) > 0:
                    for post in postParams:
                        self.call(url=url, args=args, idx=idx, post=post, offset=offset)
                elif len(cookieParams) > 0:
                    for cookie in cookieParams:
                        self.call(url=url, args=args, idx=idx, cookie=cookie, offset=offset)
                else:
                    self.call(url=url, args=args, idx=idx, offset=offset)    
        
    # Function to do the actual call
    def call(self, url, args, idx=0, post=None, cookie=None, offset=0):
            self.lock.acquire()
            
            self.counter = self.queue.get()
            
            output = "[" + str(self.counter) + "]\t" + url
            response = None
            responseStartTime = 0
            responseTime = 0
            responseError = None
            responseErrorText = None
            responseText = None
            headers = []
            
            redirectHandler = CustomRedirectHandler()
            if(args.no_redirect):
                redirectHandler.doFollow = False
            urlopener = urllib2.build_opener(redirectHandler)
            
            if(cookie is not None):
                headers.append(('Cookie', cookie))
            if(args.set_user_agent):
                headers.append(('User-agent', args.set_user_agent))
            if(args.time):
                responseStartTime = time()
            try:
                if(len(headers) > 0):
                    urlopener.addheaders = headers
                if(args.head):
                    response = urlopener.open(HeadRequest(url))
                else:
                    if post is not None:
                        response = urlopener.open(url, post)
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
                exit()
            if(args.time):
                responseTime = time() - responseStartTime
            if(args.status):
                output += "\t"
                if responseErrorText is None:
                    try:
                        output += str(response.status)
                    except AttributeError:
                        output += str(response.getcode())
                else:
                    output += responseErrorText
            if(args.time):
                output += "\t" + str(responseTime)
            if(args.headers and responseError is None):
                output += "\n" + str(response.info())
            if(args.mime_type and responseError is None):
                output += "\t"
                output += response.info().getheader('Content-Type')
            if(args.md5 and responseError is None):
                m = md5()
                m.update(responseText)
                output += "\t" + m.hexdigest()
            elif(args.md5):
                output += "\t"
            if(args.stdout and responseError is None):
                output += "\n" + responseText
#            if(args.detect_forms and responseError is None):
#                from analyze import Analyze
#                analyze = Analyze()
#                analyze.setObject(responseText)
#                analyze.findForms()
            if((args.write or args.screenshot) and not args.head and responseError is None):
                suffix = mimetypes.guess_extension(response.info().getheader('Content-Type'))
                fopen = None
                binary = False
                if response.info().getheader('Content-Transfer-Encoding') is not None:
                    if response.info().getheader('Content-Transfer-Encoding').lower() == 'binary':
                        binary = True
                if response.info().getheader('Content-Type') is not None:
                    if response.info().getheader('Content-Type').lower()[0:3] != 'text':
                        binary = True
                if suffix is None:
                    suffix = ".html"
                filename = args.prefix + str(self.counter) + suffix
                
                if args.output_dir:
                    filename = os.path.join(args.output_dir, filename)
                try:
                    if(binary):
                        fopen = open(filename, "wb+")
                    else:
                        fopen = open(filename, "w+")
                except IOError as e:
                    print("\nIOError: Could not open output file: " + filename)
                    return
                fopen.write(responseText)
                fopen.flush()
                if(args.screenshot):
                    devnull = open('/dev/null', 'w')
                    subprocess.call([args.screenshot, "-f", "png", fopen.name, fopen.name + ".png"], stdout=devnull, stderr=devnull)
                fopen.close()
            if(args.delay > 0):
                sleep(args.delay)
            output += "\n"
            sys.stdout.write(output)
            sys.stdout.flush()
            self.counter += 1
            self.queue.put(self.counter)
            self.lock.release()

  
