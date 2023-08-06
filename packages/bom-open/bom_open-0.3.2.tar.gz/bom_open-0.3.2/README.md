Context manager to open a file or stdin/stdout. Encoding can be detected with chardet. Pass additional arguments to `open()`.

Python writes BOM for utf-8-sig, utf-16, or utf-32.  BOM is not written when endianness is specified.
## Differences from `open()`
If `file=None` or `file='-'`, open stdin (when reading) or stdout (when writing) instead.

If `encoding=None` and `mode='r'` or `'w+'`, then detect file encoding using chardet.
