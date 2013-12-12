#About
urlfiddle is a python script which generates URLs from templates and calls them.

For example you can easily generate URLs with numerical parameters like
```
http://www.example.com/index.php?page=1
http://www.example.com/index.php?page=2
http://www.example.com/index.php?page=3
```
etc.

You can also load parameter values and URL templates from files which can be useful for checking different xss injections or generally test a webservers behaviour 

The responses can be saved to files, send to stdout or converted to screenshots if you have wkhtmltopdf present. You can show status codes, get an md5 checksum and more (- see available command line parameters).

There are still some things to do and urlfiddle will only work in basic cases for now (i.e. it will not work when making calls through proxy servers and it does not support HTTP authentication yet). But you can send cookies already.

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
  -h, --help            show this help message and exit
  -d seconds, --delay seconds
                        Delay between calls
  -a SET_USER_AGENT, --set-user-agent SET_USER_AGENT
                        Send user agent information with requests
  -p Prefix, --prefix Prefix
                        Prefix of output files
  -o Suffix, --output Suffix
                        Suffix of output files (default "html")
  -s, --silent          Silent mode: Just print out urls and do not call them
  -u, --urlencode       urlencode parameter values
  -5, --md5             Output the MD5 value of responses
  -r, --no-redirect     Do NOT follow redirects
  -f FILE, --file FILE  Process urls from file
  -q, --quiet           Suppress copyright notice
  --stdout              Pass response to stdout
  -H, --head            Only do HEAD requests
  --set-headers         Print response headers
  -S, --status          Print status code
  -t, --time            Measure response time
  -c SET_COOKIE, --set-cookie SET_COOKIE
                        Send Cookie with requests
  --screenshot /path/to/wkhtmltoimage
                        Take screenshot using wkhtmltoimage. You have to
                        provide the path to the binary as argument here.
                        Implies --write.
  -w, --write           Write output to file


```

#URL formats and replacements
Values that should be generated or replaced by urlfiddle should be wrapped in §-signs.
For now you basically have two options
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

* §f=/path/to/file§

    loads the replacement-values from a (line-seperated) file.

You can use multiple replacements in one url. So you can do:
```
http://www.example.com/index.php?param1=§1-10§&param2=§f=/path/to/file§&param3=§5-9§
```
If you just want to see what kind of URLs urlfiddle generates, you can call it with the "-s" option so it will just print out the generated urls.

Note that urlfiddle does not analyse your URLs in any way but treats them as simple strings. So the replacement may occur wherever you want. You can also do

```
http://server§1-10§.example.tld
```
and urlfiddle will generate the corresponding urls.

#Tasks
Still a lot to do:
* Do thorough testing whether all status codes are recognized correctly
* Add proxy support
* For MD5 option: Output MD5 of error pages
* Write unit tests and make the code better testable
* Add threading
* Add more replacement possibilities
