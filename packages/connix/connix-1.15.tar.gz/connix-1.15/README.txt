Help on module connix.connix in connix:

NAME
    connix.connix

DESCRIPTION
    Connix is a general purpose Python 3.x library that contains a lot of commonly done operations inside of a single package.
    (C) 2018 Patrick Lambert - http://dendory.net - Provided under the MIT License

FUNCTIONS
    alphanum(text, symbols=False, spaces=False)
        Return only letters, numbers and optionally basic symbols and spaces in a string.
        @param text: The string to process
        @param symbols: Whether to leave basic symbols
        @param spaces: Whether to leave spaces
    
    args(format='dict')
        Return the arguments passed to the script, divided by spaces or dashes.
        @param format: Whether to return as a space separated string or as a dash separated dict
    
    ask(question, default='')
        Ask a question with a default answer.
        @param question: The question to ask
        @param default: The default answer (optional)
    
    base36(number)
        Converts an integer to an alphanumeric string.
        @param number: The number to convert
    
    bold(text)
        Return the text in bold (Linux console only).
        @param text: The text to bold
    
    cmd(command)
        Run a command and return the output.
        @param command: The command to run
    
    curl(url, encoding='utf8', cookie=None)
        Get the content of a URL.
        @param url: The URL to query
        @param encoding: The decoding format (optional, defaults to UTF-8)
        @param cookie: The cookie string in format key1=value1;key2=value2 (optional)
    
    decrypt(key, text)
        Return the plain text version of an encrypted string.
        @param key: The key used for the encryption
        @param text: The cipher text to decrypt
    
    download(url, localfile)
        Download a file from the Internet.
        @param url: The url of the file
        @param localfile: Where to save that file
    
    email(fromaddr, toaddr, subject, body)
        This will send an email.
        @param fromaddr: Email of sender
        @param toaddr: Email of recipient
        @param subject: Subject of the email
        @param body: Body of the email
    
    encrypt(key, text)
        Return an AES encrypted version of the text.
        @param key: The key to use for the encryption
        @param text: The string to encrypt
    
    error()
        Return the error message after an exception. Must be used in an 'except' statement.
    
    form()
        Return the GET and POST variables in a CGI application.
    
    guid(length=16)
        Return a unique ID based on the machine, current time in milliseconds, and random number.
        @param length: The length of the ID (optional, defaults to 16 bytes)
    
    hash(text)
        Return a unique hash for a string.
        @param text: The string to hash
    
    hashfile(filename)
        Return a unique hash for the content of a file.
        @param filename: The file to hash
    
    header(content_type='text/html', filename=None)
        Return the header needed for a CGI application.
        @param content_type: The type of content delivered (optional, defaults to text/html)
        @param filename: Set the content to be a downloadable file (optional)
    
    in_list(ldict, key, value)
        Find whether a key/value pair is inside of a list of dictionaries.
        @param ldict: List of dictionaries
        @param key: The key to use for comparision
        @param value: The value to look for
    
    in_tag(text, first, last=None)
        Return what's between the first occurrence of 2 unique tags, or in between an HTML tag.
        @param text: The text to evaluate
        @param first: The first tag
        @param last: The last tag (optional, takes the first as a closing HTML tag otherwise)
    
    is_float(number)
        Check if a variable can be cast as a floating point.
        @param number: The number to check
    
    is_int(number)
        Check if a variable can be cast as an int.
        @param number: The number to check
    
    list_files(folder, pattern='*')
        Return a list of files in a folder recursively.
        @param folder: The folder to list files from
        @param pattern: The pattern files must match (optional)
    
    load(filename)
        Load a JSON file.
        @param filename: The filename to load from
    
    logger(file)
        Return a logger with sensible defaults.
        @param file: Filename where to log
    
    max_len(text, max)
        Return a string capped at a specific length.
        @param text: The text to return
        @param max: The maximum length of the string
    
    now()
        Return the current UTC date and time in a standard format.
    
    remote_ip()
        Return the remote IP of a CGI application.
    
    remove_spaces(text)
        Remove extra spaces from a string.
        @param text: The string to process
    
    remove_tags(text)
        Return the text without any HTML tags in it.
        @param text: The text to process
    
    save(filename, data)
        Save data in a JSON file.
        @param filename: The filename to use
        @param data: The object to save
    
    underline(text)
        Return the text in underline (Linux console only).
        @param text: The text to underline
    
    unixtime()
        Return the current UTC time in seconds.
    
    unixtime2datetime(unixtime)
        Convert unixtime to a date/time string.
        @param unixtime: A numeric unixtime value
    
    urlencode(text)
        Encode text for use on a URL bar.
        @param text: The text to encode

DATA
    __VERSION__ = '1.15'

FILE
    /home/elfguy/git/connix/connix/connix.py


