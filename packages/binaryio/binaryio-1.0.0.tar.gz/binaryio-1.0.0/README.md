# binaryio
Python library providing binary reading and writing functionality.

# PyPI
The package can be found on [PyPI](https://pypi.org/project/binaryio/).

# Using the library
The `BinaryReader` and `BinaryWriter` classes take readable and writable stream and contain methods which make
reading from and writing to binary files easy.

## Writing to a binary file
The code snippet below shows how to write to a binary file using the `BinaryWriter` class.
```python
from binaryio.open import open_binary, BinaryWriter

# Open a binary file for writing
with open_binary('./example.bin', 'wb') as file: # type: BinaryWriter
    # Write a string to the file
    file.write_length_prefixed_string("Hello")
    
    # Write a list of integers as 16-bit integers
    file.write_int16s([1, 2, 3, 4, 5])
    
    # Write a list of floats as single-precision
    file.write_singles([1.5, 2.5, 3.5])
```

There are three mehods to write a string:
- `write_length_prefixed_string()`: This first writes the number of bytes the string takes up as an `int16` and then
writes the string.
- `write_zero_string()`: This writes the string and then writes a null-byte to indicate the end of the string.
- `write_raw_string()`: This simply writes the string with no indication of the length or end of the string.

I would recommend to use the `write_length_prefixed_string()` method as this offers the best balance between convenience
and efficiency. The reader does not need to know the length of the string in advance as it is indicated immediately
before the string and once the length is known the string can be read in one go. On the other hand, using
`write_zero_string()` involves reading consecutive bytes one at a time until you reach a null-byte. Reading individual
bytes is much less efficient than reading a chunk. `write_raw_string()` is inconvenient as it requires knowing the
length of the string in advance.


## Reading a binary file
The code snippet below shows how to read the binary file written in the previous section using the `BinaryReader` class.
```python
from binaryio.open import open_binary, BinaryReader

# Open a binary file for reading
with open_binary("./example.bin") as file: # type: BinaryReader
    # Read length-prefixed string
    string = file.read_length_prefixed_string()
    
    # Read integers
    integers = file.read_int16s(5)
    
    # Read single-precision numbers
    singles = file.read_singles(3)
    
    print(f"String read: {string}")
    print(f"Integers read: {integers}")
    print(f"Singles read: {singles}")
```

The output of this is:

```
String read: Hello
Integers read: (1, 2, 3, 4, 5)
Singles read: (1.5, 2.5, 3.5)
```
