# SeCo Project #

[README中文文档](README.zh-CN.md) | [JSON Specs](http://json.org/) | [MsgPack Specs](https://msgpack.org/) | [Python Docs: Pickle](https://docs.python.org/3/library/pickle.html)

## About the SeCo Library ##

This is a library to serialize+compress and deserialize+decompress data. It is very easy to utilize, and can be used under various environments.

By using this library, the user/developer can easily serialize+compress data in Python, like `dict`, `list` etc, save the end result as `blob` to databases, save them to `redis` or `memcached` servers, or exchange them between python processes. It can save quite some space.

To install, please run `pip install SeCo`; and the `Seco` class can be used by adding the `from seco import SeCo` import line and the `seco = SeCo()` instantiate line to your program.

## Choose Serializer and Compressor ##

> The best combination is `msgpack` and `zlib` for it is fast and space conservative. The default is `json` and `zlib` because in most cases it is sufficient.

> The default `json` serializer relies on `simplejson` instead of core `json` because under Python 3.5 the core JSON package cannot use `bytes` as input for loading.
 
However, each combination has its strengths and weaknesses, choose according to your needs.

For example, `json` cannot serialize `bytes` or `bytearray` objects; both `json` and `msgpack` cannot serialize `set`, `frozenset` instances. For the broadest possible serialization support, the user can use `pickle` as the serializer as it can serialize almost all Python objects. But remember that `pickle` is not compatible with other languages, and its result bloats quite a bit, so if you are limited by space, use the other two serializers.

Another example, `zlib` is faster, or much faster, than `bz2`, but the compressed result is not as space efficient as that of `bz2`'s, and the `gzip` is in-between of `zlib` and `bz2` in terms of speed and compression ratio. There is also `lzma` compression library available to Python 3 environment, it is quite slow and it is not available under Python 2, but it has a a quite impressive compression ratio. You can absolutely change the compressor to `lzma` if you want. 

## SeCo Class API References ##

After installing using `pip install SeCo`, one can simply `from seco import SeCo`. `SeCo` is the only class provided in this module, its instance is responsible for serializing + compressing and de-serializing + decompressing functionality. It provides `loads`, `dumps`, `load`, `dump` methods to conform Python conventions, and it also provides `__call__` magic method for quick operations.

Signature: `SeCo(serialize = None, compress = None)`

To construct an instance, simply provide the constructor with two optional, desired parameters.

1. `serialize = None`: the first parameter, can be anything in `(None, 'json', 'msgpack', 'pickle')`.

2. `compress = None`: the second parameter, can be anything in `(None, 'zlib', 'gzip', 'bz2', 'lzma')`.

```python
from seco import SeCo
import json, lzma

# use defaults serializer and compressor
seco = SeCo() # `json` and `zlib`
# use different serializer or compressor
seco = SeCo('msgpack', 'bz2')
seco = SeCo('pickle', 'zlib')

# serialize and compress data payload
#   uses __call__ method, the second parameter is the `switch`
seco({'test': 'case'}) # `bytes` object returned
seco({'test': 'case'}, True) # `bytes` object returned, the same
seco(seco({'test': 'case'}), False) # decompress, {'test': 'case'}

# Python conventions
seco.dumps(100) # `bytes` object
seco.loads(seco.dumps(100)) # 100 returned
seco.dump([1,2,3,4,5], open('test', 'wb'))
seco.load(open('test', 'rb')) # [1,2,3,4,5]

# access and change the serializer and compressor
ser = seco.serializer # access the serializer
seco.serializer = json # change to json
com = seco.compressor # access the compressor
seco.compressor = lzma # change to lzma
```

## Licenses ##

This project is licensed under two permissive licenses, please chose one or both of the licenses to your like. Although not necessary, bug reports or feature improvements, attributes to the author(s), information on how this program is used are welcome and appreciated :-) Happy coding 

[BSD-2-Clause License]

Copyright 2018 Hansheng Zhao

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

[MIT License]

Copyright 2018 Hansheng Zhao

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
