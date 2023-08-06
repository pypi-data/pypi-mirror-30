[![Build Status](https://travis-ci.org/JamesKBowler/opencollect.svg?branch=master)](https://travis-ci.org/JamesKBowler/opencollect)
[![Coverage Status](https://coveralls.io/repos/github/JamesKBowler/opencollect/badge.svg?branch=master)](https://coveralls.io/github/JamesKBowler/opencollect?branch=master)

# opencollect
opencollect is an open-soured data collection engine.

## Requirements  
- python 3

## Installation
```shell   
pip3 install opencollect
```

## Usage
```python   
from opencollect import OpenCollect

session = OpenCollect()
session.start()

# Now send your data to it : )

```

## Example
```shell
python3 openconnect/sources/client.py
```

## Trouble Shooting
```python
socket.error: [Errno 48] Address already in use
```

```shell
nonroot@dev-ubuntu:~/opencollect$ sudo lsof -i:60312
COMMAND   PID    USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
ipython 10731 nonroot   11u  IPv4 1862980      0t0  TCP *:60312 (LISTEN)
nonroot@dev-ubuntu:~/opencollect$ sudo kill -9 10731
nonroot@dev-ubuntu:~/opencollect$ sudo lsof -i:60312
[6]+  Killed                  ipython
nonroot@dev-ubuntu:~/opencollect$ 
```

# License Terms  

## Copyright (c) 2018 James K Bowler  

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:  

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.  

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.