#About
urlfiddle is a simple url generation and scanning tool.

For example you can easily generate URLs with numerical parameters like
```
http://www.example.com/index.php?page=1
http://www.example.com/index.php?page=2
http://www.example.com/index.php?page=3
```
etc and analyse what happens if you call them.

Furthermore, if you pass in two or more parameters, urlfiddle generates all possible combinations (and calls them by default).

You can also load arbitrary parameter values and URL templates from files which can be useful for checking a web application for xss injections, fuzzing, file and directory discovery or generally testing a webservers behaviour on unexpected requests 

The responses can be saved to (text-)files, send to stdout or converted to screenshots if you have wkhtmltopdf present. You can show status codes, get an md5 checksum and more (- see available command line parameters).

There are still many things to do and urlfiddle will only work in basic cases for now (i.e. it will not work when making calls through proxy servers and it does not support HTTP authentication yet). But you can send cookies already.

A typical output may look like this:

```
$ urlfiddle -S http://www.example.tld/index.php?id=§1-10§

[0]	http://www.example.tld/index.php?id=1	301
[1]	http://www.example.tld/index.php?id=2	404
[2]	http://www.example.tld/index.php?id=3	200
[3]	http://www.example.tld/index.php?id=4	200
[4]	http://www.example.tld/index.php?id=5	200
[5]	http://www.example.tld/index.php?id=6	200
[6]	http://www.example.tld/index.php?id=7	200
[7]	http://www.example.tld/index.php?id=8	200
[8]	http://www.example.tld/index.php?id=9	200
[9]	http://www.example.tld/index.php?id=10	200

```

#Installation

Just run

```
python setup.py install
```

#Usage
Basic usage is

```
urlfiddle [URL]
```
Calling help via

```
urlfiddle -h
```
gives an overview over available command line arguments. You always need to pass at least the positional URL parameter, even when loading URLs from file via the -f option.
Here are the available command line options:

```
optional arguments:
  -h, --help            show this help message and exit
  -d seconds, --delay seconds
                        Delay between calls
  -a USER_AGENT, --set-user-agent USER_AGENT
                        Send user agent information with requests (e.g.
                        Mozilla/5.0)
  -M, --mime-type       Print MIME content type header (if detected)
  --prefix Prefix       Prefix of output files
  -o Suffix, --output-dir Suffix
                        Output directory
  -s, --silent          Silent mode: Just print out urls and do not call them
  -u, --urlencode       urlencode parameter values
  -5, --md5             Output the MD5 value of responses
  -r, --no-redirect     Do NOT follow redirects
  -f FILE, --file FILE  Process urls from file
  -p DATA, --set-post DATA
                        POST data to send with the request
  -q, --quiet           Suppress copyright notice
  --stdout              Pass response to stdout
  -H, --head            Only do HEAD requests
  --headers             Print response headers
  -S, --status          Print status code
  -t, --time            Measure response time
  -c VALUES, --set-cookie VALUES
                        Send Cookie with requests
  -P Number, --processes Number
                        Number of processes to use for starting requests in
                        parallel. Should not be larger than the number of
                        (generated) URLs you expect.
  --screenshot /path/to/wkhtmltoimage
                        Take screenshot using wkhtmltoimage. You have to
                        provide the path to the binary as argument here.
                        Implies --write.
  -w, --write           Write output to file. urlfiddle tries to detects
                        filetypes automatically based on MIME headers.
```

#URL formats and placeholders
Placeholders that should be replaced by urlfiddle should be wrapped in §-signs.
For now you basically have these options
* §START-END§

    where START and END are integer values, e.g.
    ``` 
    $ urlfiddle "http://www.example.com/index.php?page=§1-10§"
    ```
    generates (and calls) URLs of the form
    ```
    http://www.example.com/index.php?page=1
    http://www.example.com/index.php?page=2
    ...
    http://www.example.com/index.php?page=10
    ```
    
    You can generate numeric values of fixed length if you prefix START with leading zeros. E.g. §001-100§ generates all numbers with 3 digits length and leading zeros.

* §f=/path/to/file§

    loads the replacement-values from a (newline-seperated) file.
    
* §fuzz=LEN,NUMBER§    
    
    EXPERIMENTAL: uses urlfiddles internal (very basic) fuzzing capabilities to generate NUMBER random strings of length LEN where NUMBER and LEN are integer values. Fuzzed parameters get urlencoded by default.
    Example:
    ```
    urlfiddle --urlencode http://www.example.com/index.php?id=§fuzz=4,3§
    ```
    generates 3 URLs with 4 character long fuzzing values for the parameter "id".

You can use multiple placeholders in one url. So you can do:
```
urllib "http://www.example.com/index.php?param1=§1-10§&param2=§f=/path/to/file§&param3=§fuzz=5,2§"
```
which will generate urls for all possible parameter combinations.

If you just want to see what kind of URLs urlfiddle generates, you can call it with the "-s" option so it will just print out the generated urls.

Urlfiddle does not analyse your URLs in any way but treats them as simple strings. So the replacement may occur wherever you want. You can also do

```
http://server§1-10§.example.tld
```
and urlfiddle will generate the corresponding urls.

Furthermore, all generation mechanisms also apply to POST and COOKIE values which you can send with your requests. Calling urlfiddle with the following options will generate 10 requests, sending param=1, ... , param=10 in the POST body:
```
$ urlfiddle -p param=§1-10§ "http://www.example.com/index.php"
```

#Issues

* Fuzzing often returns parameters of wrong length if NUMBER * LEN gets larger than the internal character list
* Importing urls from files is not working since only the placeholders of the url argument get parsed
* You cannot run more processes than the number of urls that you call. Even if you call one url with hundreds of different POST parameters, you cannot start more than one process for now

Please report any (further) issues to https://github.com/mhelwig/urlfiddle/issues

#Tasks
There is still a lot to do:
* Write more unit tests
* Add some kind of form detection
* Add proxy support
* Add HTTP authentication support
* Add better fuzzing possibilities
* Add support for filters on single placeholders
* Output error page responses
