PyRando
=======
PyRando is a Python module for interacting with the [random.org](https://random.org) JSON API.

Installation
============
    $ pip install pyrando

Getting Started
===============
To interact with random.org, you will first need to get an api key. Go to [api.random.org](https://api.random.org/json-rpc/1/) and click on *Get a Beta Key*.

Your API key can be set either as an env variable or hard coded. To set it as an env variable, edit your profile and add a line similar to the one below. If you enter that line at the cursor during a terminal session, it will be available during the session.

    $ export RO_API_KEY='api_key'

Usage
=====
PyRando is quite easy to use. 

    >>> from pyrando import PyRando
    >>> pr = PyRando('YOUR_API_KEY')
    >>> pr.integers(5, 0, 10)
    [0, 7, 10, 3, 5]

Examples
========
### Integers
The `integers` method generates true random integers within a user-defined range. Integer requests take up to four positional arguments:
* `n` - How many random integers you need. Must be within the [1,1e4] range
* `min` - The lower boundary for the range. Must be within the [-1e9,1e9] range
* `max` - The upper boundary for the range. Must be within the [-1e9,1e9] range
* `base` (optional) - If not provided, the default `base` is set to 10. Allowed values for base are 2, 8, 10, and 16

Example:

    pr.integers(10, 1, 6)
    
### Decimals
The `decimals` method generates true random decimal fractions from a uniform distribution across the [0,1] interval with a user-defined number of decimal places. Decimal requests take three positional arguments: 
* `n` - How many random decimal fractions you need. Must be within the [1,1e4] range
* `decimalPlaces` - The number of decimal places to use. Must be within the [1,20] range

Example:

    pr.decimals(10, 8)

### Gaussians
The `gaussians` method generates true random numbers from a Gaussian distribution. Integer requests take four positional arguments: 
* `n` - How many random numbers you need
* `mean` - The distributions mean. Must be within the [1,1e4] range
* `standardDeviation` - The distributions standard deviation. Must be with the [-1e6,1e6] range
* `significantDigits` - The number of significant digits to use. Must be within the [2,20] range

Example:

    pr.gaussians(4, 0.0, 1.0, 8)


### Strings
The `strings` method generates true random strings. String requests take three positional arguments:
* `n` - How many random strings you need. Must be within the [1,1e4] range
* `length` - The length of each string. Must bbe within the [1,20] range. All strings will be of the same length
* `characters` - A string that contains the set of characters that are allowed to occur in the random stings. The maximum number of characters is 80

Example:

    pr.strings(10, 20, 'abcdefghijklmnopqrstuvwxyz')

### UUIDs
The `uuids` method generates version 4 true random UUIDs. UUID requests take a single positional argument:
* `n` - How many random UUIDs you need. Must be within the [1,1e3] range

Example:

    pr.uuids(1)
    
### Blobs
The `blobs` method generates BLOBs containing true random data. Blob requests take up to three positional argument: 
* `n` - How many random blobs you need. Must be within the [1,100] range
* `size` - The size of each blob, measured in bits. Must be within the [1,1048576] range and divisible by 8. The total size of all requested blobs much not exceed 1,048,576 bits (128KiB)
* `format` - Specifies the format in which the blobs will be returned. Values allowed are `base64` and `hex`. If not value is provided, the default value of `base64` is used.

Example:

    pr.blobs(1, 2048)
    
### Usage
The `usage` method returns information related to the usage of a given API.

Example:

    pr.usage()

