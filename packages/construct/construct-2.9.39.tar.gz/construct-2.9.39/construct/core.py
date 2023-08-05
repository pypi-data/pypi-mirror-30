# -*- coding: utf-8 -*-

import struct, io, binascii, itertools, collections, pickle, sys, os, tempfile, hashlib, importlib, imp

from construct.lib import *
from construct.expr import *
from construct.version import *


#===============================================================================
# exceptions
#===============================================================================
class ConstructError(Exception):
    pass
class SizeofError(ConstructError):
    pass
class AdaptationError(ConstructError):
    pass
class ValidationError(ConstructError):
    pass
class StreamError(ConstructError):
    pass
class FormatFieldError(ConstructError):
    pass
class IntegerError(ConstructError):
    pass
class StringError(ConstructError):
    pass
class MappingError(ConstructError):
    pass
class RangeError(ConstructError):
    pass
class RepeatError(ConstructError):
    pass
class ConstError(ConstructError):
    pass
class IndexFieldError(ConstructError):
    pass
class CheckError(ConstructError):
    pass
class ExplicitError(ConstructError):
    pass
class NamedTupleError(ConstructError):
    pass
class TimestampError(ConstructError):
    pass
class UnionError(ConstructError):
    pass
class SelectError(ConstructError):
    pass
class SwitchError(ConstructError):
    pass
class StopFieldError(ConstructError):
    pass
class PaddingError(ConstructError):
    pass
class TerminatedError(ConstructError):
    pass
class RawCopyError(ConstructError):
    pass
class ChecksumError(ConstructError):
    pass
class CancelParsing(ConstructError):
    pass


#===============================================================================
# used internally
#===============================================================================
def singleton(arg):
    x = arg()
    x.__reduce__ = lambda: arg.__name__
    return x


def _read_stream(stream, length):
    if length < 0:
        raise StreamError("length must be non-negative, found %s" % length)
    try:
        data = stream.read(length)
    except Exception:
        raise StreamError("stream.read() failed, requested %s bytes" % (length,))
    if len(data) != length:
        raise StreamError("could not read enough bytes, expected %d, found %d" % (length, len(data)))
    return data


def _read_stream_entire(stream):
    try:
        return stream.read()
    except Exception:
        raise StreamError("stream.read() failed when reading entire stream until EOF")


def _write_stream(stream, data, length=None):
    if not isinstance(data, bytestringtype):
        raise StringError("given non-bytes value, perhaps unicode? %r" % (data,))
    if length is None:
        length = len(data)
    if length < 0:
        raise StreamError("length must be non-negative, found %s" % length)
    if len(data) != length:
        raise StreamError("could not write bytes, expected %d, found %d" % (length, len(data)))
    try:
        written = stream.write(data)
    except Exception:
        raise StreamError("stream.write() failed, given %r" % (data,))
    if written is not None and written != length:
        raise StreamError("could not write bytes, expected %d, written %d" % (length, written))


def _seek_stream(stream, offset, whence=0):
    try:
        return stream.seek(offset, whence)
    except Exception:
        raise StreamError("stream.seek failed: offset %s whence %s" % (offset, whence,))


def _tell_stream(stream):
    try:
        return stream.tell()
    except Exception:
        raise StreamError("stream.tell failed")


class CodeGen:
    def __init__(self):
        self.blocks = []
        self.nextid = 0
        self.parsercache = {}
        self.linkedinstances = {}
        self.linkedparsers = {}

    def allocateId(self):
        self.nextid += 1
        return self.nextid

    def append(self, block):
        block = [s for s in block.splitlines() if s.strip()]
        firstline = block[0]
        trim = len(firstline) - len(firstline.lstrip())
        block = "\n".join(s[trim:] for s in block)
        if block not in self.blocks:
            self.blocks.append(block)

    def toString(self):
        return "\n".join(self.blocks + [""])


def mergefields(*subcons):
    def select(sc):
        if isinstance(sc, (Renamed, Embedded)):
            return select(sc.subcon)
        if isinstance(sc, (Struct, Sequence, FocusedSeq, Union, LazyStruct)):
            return sc.subcons
        raise ConstructError("Embedding only works with: Struct Sequence FocusedSeq Union LazyStruct")

    result = []
    for sc in subcons:
        if sc.flagembedded:
            result.extend(select(sc))
        else:
            result.append(sc)
    return result


def extractfield(sc):
    if isinstance(sc, Renamed):
        return extractfield(sc.subcon)
    if isinstance(sc, Embedded):
        raise ConstructError("Embedded itself is not parsable")
    return sc


#===============================================================================
# abstract constructs
#===============================================================================
class Construct(object):
    r"""
    The mother of all constructs.

    This object is generally not directly instantiated, and it does not directly implement parsing and building, so it is largely only of interest to subclass implementors. There are also other abstract classes sitting on top of this one.

    The external user API:

    * `parse`
    * `parse_stream`
    * `parse_file`
    * `build`
    * `build_stream`
    * `build_file`
    * `sizeof`
    * `compile`
    * `benchmark`

    Subclass authors should not override the external methods. Instead, another API is available:

    * `_parse`
    * `_build`
    * `_sizeof`
    * `_actualsize`
    * `_emitparse`
    * `_emitbuild`
    * `__getstate__`
    * `__setstate__`

    Attributes and Inheritance:

    All constructs have a name and flags. The name is used for naming struct members and context dictionaries. Note that the name can be a string, or None by default. A single underscore "_" is a reserved name, used as up-level in nested containers. The name should be descriptive, short, and valid as a Python identifier, although these rules are not enforced. The flags specify additional behavioral information about this construct. Flags are used by enclosing constructs to determine a proper course of action. Flags are often inherited from inner subconstructs but that depends on each class.
    """

    def __init__(self):
        self.name = None
        self.docs = ""
        self.flagbuildnone = False
        self.flagembedded = False
        self.parsed = None

    def __repr__(self):
        return "<%s%s%s%s%s>" % (self.__class__.__name__, " "+self.name if self.name else "", " +nonbuild" if self.flagbuildnone else "", " +embedded" if self.flagembedded else "", " +docs" if self.docs else "", )

    def __getstate__(self):
        attrs = {}
        if hasattr(self, "__dict__"):
            attrs.update(self.__dict__)
        slots = []
        c = self.__class__
        while c is not None:
            if hasattr(c, "__slots__"):
                slots.extend(c.__slots__)
            c = c.__base__
        for name in slots:
            if hasattr(self, name):
                attrs[name] = getattr(self, name)
        return attrs

    def __setstate__(self, attrs):
        for name, value in attrs.items():
            setattr(self, name, value)

    def __copy__(self):
        self2 = object.__new__(self.__class__)
        self2.__setstate__(self, self.__getstate__())
        return self2

    def parse(self, data, **contextkw):
        r"""
        Parse an in-memory buffer (often bytes object). Strings, buffers, memoryviews, and other complete buffers can be parsed with this method.

        Whenever data cannot be read, ConstructError or its derivative is raised. This method is NOT ALLOWED to raise any other exceptions although (1) user-defined lambdas can raise arbitrary exceptions which are propagated (2) external libraries like numpy can raise arbitrary exceptions which are propagated (3) some list and dict lookups can raise IndexError and KeyError which are propagated.

        Context entries are passed only as keyword parameters \*\*contextkw.

        :param \*\*contextkw: context entries, usually empty

        :returns: some value, usually based on bytes read from the stream but sometimes it is computed from nothing or from the context dictionary, sometimes its non-deterministic

        :raises ConstructError: raised for any reason
        """
        return self.parse_stream(io.BytesIO(data), **contextkw)

    def parse_stream(self, stream, **contextkw):
        r"""
        Parse a stream. Files, pipes, sockets, and other streaming sources of data are handled by this method. See parse().
        """
        context = Container(**contextkw)
        try:
            return self._parsereport(stream, context, "(parsing)")
        except CancelParsing:
            pass

    def parse_file(self, filename, **contextkw):
        r"""
        Parse a closed binary file. See parse().
        """
        with open(filename, 'rb') as f:
            return self.parse_stream(f, **contextkw)

    def _parsereport(self, stream, context, path):
        obj = self._parse(stream, context, path)
        if self.parsed is not None:
            self.parsed(obj, context)
        return obj

    def _parse(self, stream, context, path):
        """Override in your subclass."""
        raise NotImplementedError

    def build(self, obj, **contextkw):
        r"""
        Build an object in memory (a bytes object).

        Whenever data cannot be written, ConstructError or its derivative is raised. This method is NOT ALLOWED to raise any other exceptions although (1) user-defined lambdas can raise arbitrary exceptions which are propagated (2) external libraries like numpy can raise arbitrary exceptions which are propagated (3) some list and dict lookups can raise IndexError and KeyError which are propagated.

        Context entries are passed only as keyword parameters \*\*contextkw.

        :param \*\*contextkw: context entries, usually empty

        :returns: bytes

        :raises ConstructError: raised for any reason
        """
        stream = io.BytesIO()
        self.build_stream(obj, stream, **contextkw)
        return stream.getvalue()

    def build_stream(self, obj, stream, **contextkw):
        r"""
        Build an object directly into a stream. See build().
        """
        context = Container(**contextkw)
        self._build(obj, stream, context, "(building)")

    def build_file(self, obj, filename, **contextkw):
        r"""
        Build an object into a closed binary file. See build().
        """
        with open(filename, 'wb') as f:
            self.build_stream(obj, f, **contextkw)

    def _build(self, obj, stream, context, path):
        """Override in your subclass."""
        raise NotImplementedError

    def sizeof(self, **contextkw):
        r"""
        Calculate the size of this object, optionally using a context.

        Some constructs have fixed size (like FormatField), some have variable-size and can determine their size given a context entry (like Bytes(this.otherfield1)), and some cannot determine their size (like VarInt).

        Whenever size cannot be determined, SizeofError is raised. This method is NOT ALLOWED to raise any other exception, even if eg. context dictionary is missing a key, or subcon propagates ConstructError-derivative exception.

        Context entries are passed only as keyword parameters \*\*contextkw.

        :param \*\*contextkw: context entries, usually empty

        :returns: integer if computable, SizeofError otherwise

        :raises SizeofError: size could not be determined in actual context, or is impossible to be determined
        """
        context = Container(**contextkw)
        return self._sizeof(context, "(sizeof)")

    def _sizeof(self, context, path):
        """Override in your subclass."""
        raise SizeofError

    def _actualsize(self, stream, context, path):
        return self._sizeof(context, path)

    def compile(self, filename=None):
        """
        Transforms a construct into another construct that does same thing (has same parsing and building semantics) but is much faster when parsing. Already compiled instances just compile into itself.

        Optionally, partial source code can be saved to a text file. This is meant only to inspect the generated code, not to import it from external scripts.

        :returns: Compiled instance
        """

        code = CodeGen()
        code.append("""
            # generated by Construct, this source is for inspection only! do not import!

            from construct import *
            from construct.lib import *
            from io import BytesIO
            import struct
            import collections
            import itertools

            def read_bytes(io, count):
                if not count >= 0: raise StreamError
                data = io.read(count)
                if not len(data) == count: raise StreamError
                return data
            def restream(data, func):
                return func(BytesIO(data))
            def reuse(obj, func):
                return func(obj)

            linkedinstances = {}
            linkedparsers = {}

            len_ = len
            sum_ = sum
            min_ = min
            max_ = max
            abs_ = abs
        """)
        code.append("""
            def parseall(io, this):
                return %s
            compiled = Compiled(None, None, parseall)
        """ % (self._compileparse(code),))
        source = code.toString()

        if filename:
            with open(filename, "wt") as f:
                f.write(source)

        modulename = hexlify(hashlib.sha1(source.encode()).digest()).decode()
        module = imp.new_module(modulename)
        c = compile(source, '', 'exec')
        exec(c, module.__dict__)

        module.linkedinstances = code.linkedinstances
        module.linkedparsers = code.linkedparsers
        compiled = module.compiled
        compiled.source = source
        compiled.module = module
        compiled.modulename = modulename
        compiled.defersubcon = self
        return compiled

    def _compileinstance(self, code):
        """Used internally."""
        if id(self) in code.linkedinstances:
            return code.linkedinstances[id(self)]

        code.append("""
            # linkedinstances[%s] is %r
        """ % (id(self), self, ))

        field = extractfield(self)
        code.linkedinstances[id(self)] = field
        code.linkedparsers[id(self)] = field._parse
        return "linkedinstances[%s]" % id(self)

    def _compileparse(self, code):
        """Used internally."""
        try:
            if id(self) in code.parsercache:
                return code.parsercache[id(self)]
            emitted = self._emitparse(code)
            code.parsercache[id(self)] = emitted
            return emitted
        except NotImplementedError:
            self._compileinstance(code)
            return "linkedparsers[%s](io, this, '(???)')" % id(self)

    def _compilebuild(self, code):
        """Used internally."""
        raise NotImplementedError

    def _emitparse(self, code):
        """Override in your subclass."""
        raise NotImplementedError

    def _emitbuild(self, code):
        """Override in your subclass."""
        raise NotImplementedError

    def benchmark(self, sampledata, filename=None):
        """
        Measures performance of your construct (its parsing and building runtime), both for the original instance and the compiled instance. Uses timeit module, over at min 1 sample, and at max over 1 second time.

        Optionally, results are saved to a text file for later inspection. Otherwise you can print the result string to terminal.

        Also this method checks correctness, by comparing parsing/building results from both instances.

        :param sampledata: bytes, a valid blob parsable by this construct
        :param filename: optional, string, source is saved to that file

        :returns: string containing measurements
        """
        from timeit import timeit

        try:
            parsetime = "failed"
            buildtime = "failed"
            parsetime2 = "failed"

            sampleobj = self.parse(sampledata)
            parsetime = timeit(lambda: self.parse(sampledata), number=1)
            runs = min(1000, max(1, int(1./parsetime)))
            if runs > 1:
                parsetime = timeit(lambda: self.parse(sampledata), number=runs)/runs
            parsetime = "{:.10f} sec/call".format(parsetime)

            self.build(sampleobj)
            buildtime = timeit(lambda: self.build(sampleobj), number=1)
            runs = min(1000, max(1, int(1./buildtime)))
            if runs > 1:
                buildtime = timeit(lambda: self.build(sampleobj), number=runs)/runs
            buildtime = "{:.10f} sec/call".format(buildtime)

            compiled = self.compile()

            obj = compiled.parse(sampledata)
            assert sampleobj == obj
            parsetime2 = timeit(lambda: compiled.parse(sampledata), number=1)
            runs = min(1000, max(1, int(1./parsetime2)))
            if runs > 1:
                parsetime2 = timeit(lambda: compiled.parse(sampledata), number=runs)/runs
            parsetime2 = "{:.10f} sec/call".format(parsetime2)

        except Exception:
            pass

        lines = [
            "Timeit measurements:",
            "parsing:           {}",
            "parsing compiled:  {}",
            "building:          {}",
            ""
        ]
        results = "\n".join(lines).format(parsetime, parsetime2, buildtime)

        if filename:
            with open(filename, "wt") as f:
                f.write(results)
        return results

    def __rtruediv__(self, name):
        """
        Used for renaming subcons, usually part of a Struct, like Struct("index" / Byte).
        """
        return Renamed(self, newname=name)

    __rdiv__ = __rtruediv__

    def __mul__(self, other):
        """
        Used for adding docstrings and parsed hooks to subcons, like "field" / Byte * "docstring" * processfunc.
        """
        if isinstance(other, stringtypes):
            return Renamed(self, newdocs=other)
        if callable(other):
            return Renamed(self, newparsed=other)
        raise ConstructError("operator * can only be used with string or lambda")

    def __rmul__(self, other):
        """
        Used for adding docstrings and parsed hooks to subcons, like "field" / Byte * "docstring" * processfunc.
        """
        if isinstance(other, stringtypes):
            return Renamed(self, newdocs=other)
        if callable(other):
            return Renamed(self, newparsed=other)
        raise ConstructError("operator * can only be used with string or lambda")

    def __add__(self, other):
        """
        Used for making Struct like ("index"/Byte + "prefix"/Byte).
        """
        lhs = self.subcons  if isinstance(self,  Struct) else [self]
        rhs = other.subcons if isinstance(other, Struct) else [other]
        return Struct(*(lhs + rhs))

    def __rshift__(self, other):
        """
        Used for making Sequences like (Byte >> Short).
        """
        lhs = self.subcons  if isinstance(self,  Sequence) else [self]
        rhs = other.subcons if isinstance(other, Sequence) else [other]
        return Sequence(*(lhs + rhs))

    def __getitem__(self, count):
        """
        Used for making Arrays and GreedyRanges like Byte[5] and Byte[:].
        """
        if isinstance(count, slice):
            if any(x is not None for x in [count.start, count.stop, count.step]):
                raise ValueError("slice can only be like X[:]")
            return GreedyRange(self)
        if isinstance(count, int) or callable(count):
            return Array(count, self)
        raise TypeError("expected integer, context lambda, or full-slice")


class Subconstruct(Construct):
    r"""
    Abstract subconstruct (wraps an inner construct, inheriting its name and flags). Parsing and building is by default deferred to subcon, same as sizeof.

    :param subcon: Construct instance
    """
    def __init__(self, subcon):
        if not isinstance(subcon, Construct):
            raise TypeError("subcon should be a Construct field")
        super(Subconstruct, self).__init__()
        self.subcon = subcon
        self.flagbuildnone = subcon.flagbuildnone
        self.flagembedded = subcon.flagembedded

    def __repr__(self):
        return "<%s%s%s%s%s %s>" % (self.__class__.__name__, " "+self.name if self.name else "", " +nonbuild" if self.flagbuildnone else "", " +embedded" if self.flagembedded else "", " +docs" if self.docs else "", repr(self.subcon), )

    def _parse(self, stream, context, path):
        return self.subcon._parsereport(stream, context, path)

    def _build(self, obj, stream, context, path):
        return self.subcon._build(obj, stream, context, path)

    def _sizeof(self, context, path):
        return self.subcon._sizeof(context, path)


class Adapter(Subconstruct):
    r"""
    Abstract adapter class.

    Needs to implement `_decode()` for parsing and `_encode()` for building.

    :param subcon: Construct instance
    """
    def _parse(self, stream, context, path):
        obj = self.subcon._parsereport(stream, context, path)
        return self._decode(obj, context, path)

    def _build(self, obj, stream, context, path):
        obj2 = self._encode(obj, context, path)
        buildret = self.subcon._build(obj2, stream, context, path)
        return obj

    def _decode(self, obj, context, path):
        raise NotImplementedError

    def _encode(self, obj, context, path):
        raise NotImplementedError


class SymmetricAdapter(Adapter):
    r"""
    Abstract adapter class.

    Needs to implement `_decode()` only, for both parsing and building.

    :param subcon: Construct instance
    """
    def _encode(self, obj, context, path):
        return self._decode(obj, context, path)


class Validator(SymmetricAdapter):
    r"""
    Abstract class that validates a condition on the encoded/decoded object.

    Needs to implement `_validate()` that returns a bool (or a truthy value)

    :param subcon: Construct instance
    """
    def _decode(self, obj, context, path):
        if not self._validate(obj, context, path):
            raise ValidationError("object failed validation: %s" % (obj,))
        return obj

    def _validate(self, obj, context, path):
        raise NotImplementedError


class Tunnel(Subconstruct):
    r"""
    Abstract class that allows other constructs to read part of the stream as if they were reading the entrie stream. See Prefixed for example.

    Needs to implement `_decode()` for parsing and `_encode()` for building.
    """
    def _parse(self, stream, context, path):
        data = _read_stream_entire(stream)  # reads entire stream
        data = self._decode(data, context, path)
        return self.subcon.parse(data, **context)

    def _build(self, obj, stream, context, path):
        data = self.subcon.build(obj, **context)
        data = self._encode(data, context, path)
        _write_stream(stream, data)
        return obj

    def _sizeof(self, context, path):
        raise SizeofError

    def _decode(self, data, context, path):
        raise NotImplementedError

    def _encode(self, data, context, path):
        raise NotImplementedError


class Compiled(Construct):
    """Used internally."""

    def __init__(self, source, defersubcon, parsefunc):
        super(Compiled, self).__init__()
        self.source = source
        self.defersubcon = defersubcon
        self.parsefunc = parsefunc

    def _parse(self, stream, context, path):
        return self.parsefunc(stream, context)

    def _build(self, obj, stream, context, path):
        return self.defersubcon._build(obj, stream, context, path)

    def _sizeof(self, context, path):
        return self.defersubcon._sizeof(context, path)

    def compile(self, filename=None):
        return self

    def benchmark(self, sampledata, filename=None):
        return self.defersubcon.benchmark(sampledata, filename)


#===============================================================================
# bytes and bits
#===============================================================================
class Bytes(Construct):
    r"""
    Field consisting of a specified number of bytes.

    Parses into a bytes (of given length). Builds into the stream directly (but checks that given object matches specified length). Can also build from an integer for convenience (although BytesInteger should be used instead). Size is the specified length.

    :param length: integer or context lambda

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises StringError: building from non-bytes value, perhaps unicode

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        >>> d = Bytes(4)
        >>> d.parse(b'beef')
        b'beef'
        >>> d.build(b'beef')
        b'beef'
        >>> d.build(0)
        b'\x00\x00\x00\x00'
        >>> d.sizeof()
        4

        >>> d = Struct(
        ...     "length" / Int8ub,
        ...     "data" / Bytes(this.length),
        ... )
        >>> d.parse(b"\x04beef")
        Container(length=4)(data=b'beef')
        >>> d.sizeof()
        construct.core.SizeofError: cannot calculate size, key not found in context
    """

    def __init__(self, length):
        super(Bytes, self).__init__()
        self.length = length

    def _parse(self, stream, context, path):
        length = self.length(context) if callable(self.length) else self.length
        return _read_stream(stream, length)

    def _build(self, obj, stream, context, path):
        length = self.length(context) if callable(self.length) else self.length
        data = integer2bytes(obj, length) if isinstance(obj, int) else obj
        _write_stream(stream, data, length)
        return data

    def _sizeof(self, context, path):
        try:
            return self.length(context) if callable(self.length) else self.length
        except (KeyError, AttributeError):
            raise SizeofError("cannot calculate size, key not found in context")

    def _emitparse(self, code):
        return "read_bytes(io, %s)" % (self.length,)


@singleton
class GreedyBytes(Construct):
    r"""
    Field consisting of unknown number of bytes.

    Parses the stream to the end. Builds into the stream directly (without checks). Size is undefined.

    :raises StreamError: stream failed when reading until EOF
    :raises StringError: building from non-bytes value, perhaps unicode

    Example::

        >>> GreedyBytes.parse(b"asislight")
        b'asislight'
        >>> GreedyBytes.build(b"asislight")
        b'asislight'
    """

    def _parse(self, stream, context, path):
        return _read_stream_entire(stream)

    def _build(self, obj, stream, context, path):
        stream.write(obj)
        return obj

    def _emitparse(self, code):
        return "io.read()"


def Bitwise(subcon):
    r"""
    Converts the stream from bytes to bits, and passes the bitstream to underlying subcon. Bitstream is a stream that contains 8 times as many bytes, and each byte is either \\x00 or \\x01 (in documentation those bytes are called bits).

    Parsing building and size are deferred to subcon, although size gets divided by 8.

    :param subcon: Construct instance, any field that works with bits (like BitsInteger) or is bit-byte agnostic (like Struct or Flag)

    See :class:`~construct.core.TransformData` and :class:`~construct.core.Restreamed` for raisable exceptions.

    Example::

        >>> d = Bitwise(Struct(
        ...     'a' / Nibble,
        ...     'b' / Bytewise(Float32b),
        ...     'c' / Padding(4),
        ... ))
        >>> d.parse(bytes(5))
        Container(a=0)(b=0.0)(c=None)
        >>> d.sizeof()
        5
    """

    try:
        size = subcon.sizeof()
        return TransformData(subcon, bytes2bits, size//8, bits2bytes, size//8)
    except SizeofError:
        return Restreamed(subcon, bytes2bits, 1, bits2bytes, 8, lambda n: n//8)


def Bytewise(subcon):
    r"""
    Converts the bitstream back to normal byte stream. Must be used within :class:`~construct.core.Bitwise`.

    Parsing building and size are deferred to subcon, although size gets multiplied by 8.

    :param subcon: Construct instance, any field that works with bytes or is bit-byte agnostic

    See :class:`~construct.core.TransformData` and :class:`~construct.core.Restreamed` for raisable exceptions.

    Example::

        >>> d = Bitwise(Struct(
        ...     'a' / Nibble,
        ...     'b' / Bytewise(Float32b),
        ...     'c' / Padding(4),
        ... ))
        >>> d.parse(bytes(5))
        Container(a=0)(b=0.0)(c=None)
        >>> d.sizeof()
        5
    """

    try:
        size = subcon.sizeof()
        return TransformData(subcon, bits2bytes, size*8, bytes2bits, size*8)
    except SizeofError:
        return Restreamed(subcon, bits2bytes, 8, bytes2bits, 1, lambda n: n*8)


#===============================================================================
# integers and floats
#===============================================================================
class FormatField(Construct):
    r"""
    Field that uses `struct` module to pack and unpack CPU-sized integers and floats. This is used to implement most Int* Float* fields, but for example cannot pack 24-bit integers, which is left to :class:`~construct.core.BytesInteger` class.

    See `struct module <https://docs.python.org/3/library/struct.html>`_ documentation for instructions on crafting format strings.

    Parses into an integer. Builds from an integer into specified byte count and endianness. Size is determined by `struct` module according to specified format string.

    :param endianity: string, character like: < > =
    :param format: string, character like: f d B H L Q b h l q

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises FormatFieldError: wrong format string, or struct.(un)pack complained about the value

    Example::

        >>> d = FormatField(">", "H") or Int16ub
        >>> d.parse(b"\x01\x00")
        256
        >>> d.build(256)
        b"\x01\x00"
        >>> d.sizeof()
        2
    """

    def __init__(self, endianity, format):
        if endianity not in list("=<>"):
            raise FormatFieldError("endianity must be like: = < >", endianity)
        if format not in list("fdBHLQbhlq"):
            raise FormatFieldError("format must be like: f d B H L Q b h l q", format)
        super(FormatField, self).__init__()
        self.fmtstr = endianity+format
        self.length = struct.calcsize(endianity+format)
        self.packer = struct.Struct(endianity+format)

    def _parse(self, stream, context, path):
        data = _read_stream(stream, self.length)
        try:
            return self.packer.unpack(data)[0]
        except Exception:
            raise FormatFieldError("struct %r error during parsing" % self.fmtstr)

    def _build(self, obj, stream, context, path):
        try:
            data = self.packer.pack(obj)
        except Exception:
            raise FormatFieldError("struct %r error during building, given value %r" % (self.fmtstr, obj))
        _write_stream(stream, data, self.length)
        return obj

    def _sizeof(self, context, path):
        return self.length

    def _emitparse(self, code):
        fname = "formatfield_%s" % code.allocateId()
        code.append("%s = struct.Struct(%r)" % (fname, self.fmtstr, ))
        return "%s.unpack(read_bytes(io, %s))[0]" % (fname, self.length)


class BytesInteger(Construct):
    r"""
    Field that packs arbitrarily large integers. Some Int24* fields use this class.

    Parses into an integer. Builds from an integer into specified byte count and endianness. Size is specified in ctor.

    Analog to :class:`~construct.core.BitsInteger` that operates on bits. In fact, ``BytesInteger(n)`` is equivalent to ``Bitwise(BitsInteger(8*n))`` and ``BitsInteger(n)`` is equivalent to ``Bytewise(BytesInteger(n//8)))`` .

    :param length: integer or context lambda, number of bytes in the field
    :param signed: bool, whether the value is signed (two's complement), default is False (unsigned)
    :param swapped: bool, whether to swap byte order (little endian), default is False (big endian)

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises IntegerError: lenght is negative, given a negative value when field is not signed, or not an integer

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        >>> d = BytesInteger(4) or Int32ub
        >>> d.parse(b"abcd")
        1633837924
        >>> d.build(1)
        b'\x00\x00\x00\x01'
        >>> d.sizeof()
        4
    """

    def __init__(self, length, signed=False, swapped=False):
        super(BytesInteger, self).__init__()
        self.length = length
        self.signed = signed
        self.swapped = swapped

    def _parse(self, stream, context, path):
        length = self.length
        if callable(length):
            length = length(context)
        if length < 0:
            raise IntegerError("length must be non-negative")
        data = _read_stream(stream, length)
        if self.swapped:
            data = data[::-1]
        return bytes2integer(data, self.signed)

    def _build(self, obj, stream, context, path):
        if not isinstance(obj, integertypes):
            raise IntegerError("value %r is not an integer" % (obj,))
        if obj < 0 and not self.signed:
            raise IntegerError("value %r is negative, but field is not signed" % (obj,))
        length = self.length
        if callable(length):
            length = length(context)
        if length < 0:
            raise IntegerError("length must be non-negative")
        data = integer2bytes(obj, length)
        if self.swapped:
            data = data[::-1]
        _write_stream(stream, data, length)
        return obj

    def _sizeof(self, context, path):
        try:
            length = self.length
            if callable(length):
                length = length(context)
            return length
        except (KeyError, AttributeError):
            raise SizeofError("cannot calculate size, key not found in context")

    def _emitparse(self, code):
        return "bytes2integer(read_bytes(io, %s)%s, %s)" % (self.length, "[::-1]" if self.swapped else "", self.signed)


class BitsInteger(Construct):
    r"""
    Field that packs arbitrarily large (or small) integers. Some fields (Bit Nibble Octet) use this class. Must be enclosed in :class:`~construct.core.Bitwise` context.

    Parses into an integer. Builds from an integer into specified bit count and endianness. Size (in bits) is specified in ctor.

    Note that little-endianness is only defined for multiples of 8 bits.

    Analog to :class:`~construct.core.BytesInteger` that operates on bytes. In fact, ``BytesInteger(n)`` is equivalent to ``Bitwise(BitsInteger(8*n))`` and ``BitsInteger(n)`` is equivalent to ``Bytewise(BytesInteger(n//8)))`` .

    :param length: integer or context lambda, number of bits in the field
    :param signed: bool, whether the value is signed (two's complement), default is False (unsigned)
    :param swapped: bool, whether to swap byte order (little endian), default is False (big endian)

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises IntegerError: lenght is negative, given a negative value when field is not signed, or not an integer

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        >>> d = Bitwise(BitsInteger(8)) or Bitwise(Octet)
        >>> d.parse(b"\x10")
        16
        >>> d.build(255)
        b'\xff'
        >>> d.sizeof()
        1
    """

    def __init__(self, length, signed=False, swapped=False):
        super(BitsInteger, self).__init__()
        self.length = length
        self.signed = signed
        self.swapped = swapped

    def _parse(self, stream, context, path):
        length = self.length
        if callable(length):
            length = length(context)
        if length < 0:
            raise IntegerError("length must be non-negative")
        data = _read_stream(stream, length)
        if self.swapped:
            if length & 7:
                raise IntegerError("little-endianness is only defined for multiples of 8 bits")
            data = swapbytes(data)
        return bits2integer(data, self.signed)

    def _build(self, obj, stream, context, path):
        if not isinstance(obj, integertypes):
            raise IntegerError("value %r is not an integer" % (obj,))
        if obj < 0 and not self.signed:
            raise IntegerError("value %r is negative, but field is not signed" % (obj,))
        length = self.length
        if callable(length):
            length = length(context)
        if length < 0:
            raise IntegerError("length must be non-negative")
        data = integer2bits(obj, length)
        if self.swapped:
            if length & 7:
                raise IntegerError("little-endianness is only defined for multiples of 8 bits")
            data = swapbytes(data)
        _write_stream(stream, data, length)
        return obj

    def _sizeof(self, context, path):
        try:
            length = self.length
            if callable(length):
                length = length(context)
            return length
        except (KeyError, AttributeError):
            raise SizeofError("cannot calculate size, key not found in context")

    def _emitparse(self, code):
        return "bits2integer(read_bytes(io, %s)%s, %s)" % (self.length, "[::-1]" if self.swapped else "", self.signed, )


@singleton
def Bit():
    """A 1-bit integer, must be enclosed in a Bitwise (eg. BitStruct)"""
    return BitsInteger(1)
@singleton
def Nibble():
    """A 4-bit integer, must be enclosed in a Bitwise (eg. BitStruct)"""
    return BitsInteger(4)
@singleton
def Octet():
    """A 8-bit integer, must be enclosed in a Bitwise (eg. BitStruct)"""
    return BitsInteger(8)

@singleton
def Int8ub():
    """Unsigned, big endian 8-bit integer"""
    return FormatField(">", "B")
@singleton
def Int16ub():
    """Unsigned, big endian 16-bit integer"""
    return FormatField(">", "H")
@singleton
def Int32ub():
    """Unsigned, big endian 32-bit integer"""
    return FormatField(">", "L")
@singleton
def Int64ub():
    """Unsigned, big endian 64-bit integer"""
    return FormatField(">", "Q")

@singleton
def Int8sb():
    """Signed, big endian 8-bit integer"""
    return FormatField(">", "b")
@singleton
def Int16sb():
    """Signed, big endian 16-bit integer"""
    return FormatField(">", "h")
@singleton
def Int32sb():
    """Signed, big endian 32-bit integer"""
    return FormatField(">", "l")
@singleton
def Int64sb():
    """Signed, big endian 64-bit integer"""
    return FormatField(">", "q")

@singleton
def Int8ul():
    """Unsigned, little endian 8-bit integer"""
    return FormatField("<", "B")
@singleton
def Int16ul():
    """Unsigned, little endian 16-bit integer"""
    return FormatField("<", "H")
@singleton
def Int32ul():
    """Unsigned, little endian 32-bit integer"""
    return FormatField("<", "L")
@singleton
def Int64ul():
    """Unsigned, little endian 64-bit integer"""
    return FormatField("<", "Q")

@singleton
def Int8sl():
    """Signed, little endian 8-bit integer"""
    return FormatField("<", "b")
@singleton
def Int16sl():
    """Signed, little endian 16-bit integer"""
    return FormatField("<", "h")
@singleton
def Int32sl():
    """Signed, little endian 32-bit integer"""
    return FormatField("<", "l")
@singleton
def Int64sl():
    """Signed, little endian 64-bit integer"""
    return FormatField("<", "q")

@singleton
def Int8un():
    """Unsigned, native endianity 8-bit integer"""
    return FormatField("=", "B")
@singleton
def Int16un():
    """Unsigned, native endianity 16-bit integer"""
    return FormatField("=", "H")
@singleton
def Int32un():
    """Unsigned, native endianity 32-bit integer"""
    return FormatField("=", "L")
@singleton
def Int64un():
    """Unsigned, native endianity 64-bit integer"""
    return FormatField("=", "Q")

@singleton
def Int8sn():
    """Signed, native endianity 8-bit integer"""
    return FormatField("=", "b")
@singleton
def Int16sn():
    """Signed, native endianity 16-bit integer"""
    return FormatField("=", "h")
@singleton
def Int32sn():
    """Signed, native endianity 32-bit integer"""
    return FormatField("=", "l")
@singleton
def Int64sn():
    """Signed, native endianity 64-bit integer"""
    return FormatField("=", "q")

Byte  = Int8ub
Short = Int16ub
Int   = Int32ub
Long  = Int64ub

@singleton
def Float32b():
    """Big endian, 32-bit IEEE floating point number"""
    return FormatField(">", "f")
@singleton
def Float32l():
    """Little endian, 32-bit IEEE floating point number"""
    return FormatField("<", "f")
@singleton
def Float32n():
    """Native endianity, 32-bit IEEE floating point number"""
    return FormatField("=", "f")

@singleton
def Float64b():
    """Big endian, 64-bit IEEE floating point number"""
    return FormatField(">", "d")
@singleton
def Float64l():
    """Little endian, 64-bit IEEE floating point number"""
    return FormatField("<", "d")
@singleton
def Float64n():
    """Native endianity, 64-bit IEEE floating point number"""
    return FormatField("=", "d")

Single = Float32b
Double = Float64b

native = (sys.byteorder == "little")

@singleton
def Int24ub():
    """A 3-byte big-endian unsigned integer, as used in ancient file formats."""
    return BytesInteger(3, signed=False, swapped=False)
@singleton
def Int24ul():
    """A 3-byte little-endian unsigned integer, as used in ancient file formats."""
    return BytesInteger(3, signed=False, swapped=True)
@singleton
def Int24un():
    """A 3-byte native-endian unsigned integer, as used in ancient file formats."""
    return BytesInteger(3, signed=False, swapped=native)
@singleton
def Int24sb():
    """A 3-byte big-endian signed integer, as used in ancient file formats."""
    return BytesInteger(3, signed=True, swapped=False)
@singleton
def Int24sl():
    """A 3-byte little-endian signed integer, as used in ancient file formats."""
    return BytesInteger(3, signed=True, swapped=True)
@singleton
def Int24sn():
    """A 3-byte native-endian signed integer, as used in ancient file formats."""
    return BytesInteger(3, signed=True, swapped=native)


@singleton
class VarInt(Construct):
    r"""
    VarInt encoded integer. Each 7 bits of the number are encoded in one byte of the stream, where leftmost bit (MSB) is unset when byte is terminal. Scheme is defined at Google site related to `Protocol Buffers <https://developers.google.com/protocol-buffers/docs/encoding>`_.

    Can only encode non-negative numbers.

    Parses into an integer. Builds from an integer. Size is undefined.

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises IntegerError: given a negative value, or not an integer

    Example::

        >>> VarInt.build(1)
        b'\x01'
        >>> VarInt.build(2**100)
        b'\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x04'
    """

    def _parse(self, stream, context, path):
        acc = []
        while True:
            b = byte2int(_read_stream(stream, 1))
            acc.append(b & 0b01111111)
            if not b & 0b10000000:
                break
        num = 0
        for b in reversed(acc):
            num = (num << 7) | b
        return num

    def _build(self, obj, stream, context, path):
        if not isinstance(obj, integertypes):
            raise IntegerError("value is not an integer")
        if obj < 0:
            raise IntegerError("varint cannot build from negative number: %r" % (obj,))
        while obj > 0b01111111:
            _write_stream(stream, int2byte(0b10000000 | (obj & 0b01111111)), 1)
            obj >>= 7
        _write_stream(stream, int2byte(obj), 1)
        return obj


#===============================================================================
# strings
#===============================================================================

#: Explicitly supported encodings (by PaddedString and CString classes).
#:
possiblestringencodings = dict(
    ascii=1,
    utf8=1, utf_8=1, u8=1,
    utf16=2, utf_16=2, u16=2, utf_16_be=2, utf_16_le=2,
    utf32=4, utf_32=4, u32=4, utf_32_be=4, utf_32_le=4,
)


def selectencoding(encoding):
    """Used internally."""
    if not encoding:
        raise StringError("String* classes require explicit encoding")
    return encoding


def calculateunits(encoding):
    """Used internally."""
    encoding = encoding.replace("-","_").lower()
    if encoding not in possiblestringencodings:
        raise StringError("encoding %r not among %r" % (encoding, possiblestringencodings,))
    unitsize = possiblestringencodings[encoding]
    finalunit = b"\x00" * unitsize
    return unitsize, finalunit


class StringEncoded(Adapter):
    """Used internally."""

    def __init__(self, subcon, encoding):
        super(StringEncoded, self).__init__(subcon)
        self.encoding = selectencoding(encoding)

    def _decode(self, obj, context, path):
        return obj.decode(self.encoding)

    def _encode(self, obj, context, path):
        if not isinstance(obj, unicodestringtype):
            raise StringError("string encoding failed, expected unicode string")
        if obj == u"":
            return b""
        return obj.encode(self.encoding)

    def _emitparse(self, code):
        return "(%s).decode(%r)" % (self.subcon._compileparse(code), self.encoding, )


class StringPaddedTrimmed(Construct):
    """Used internally."""

    def __init__(self, length, encoding):
        super(StringPaddedTrimmed, self).__init__()
        self.length = length
        self.encoding = selectencoding(encoding)

    def _parse(self, stream, context, path):
        length = self.length(context) if callable(self.length) else self.length
        unitsize, finalunit = calculateunits(self.encoding)

        if length % unitsize:
            raise StringError("byte length must be multiple of encoding-unit, %s" % (unitsize,))
        obj = _read_stream(stream, length)
        endsat = 0
        endsatmax = len(obj)
        while endsat+unitsize <= endsatmax and obj[endsat:endsat+unitsize] != finalunit:
            endsat += unitsize
        return obj[:endsat]

    def _build(self, obj, stream, context, path):
        originalobj = obj
        length = self.length(context) if callable(self.length) else self.length
        unitsize, finalunit = calculateunits(self.encoding)

        if length % unitsize:
            raise StringError("byte length must be multiple of encoding-unit, %s" % (unitsize,))
        if len(obj) % unitsize:
            raise StringError("string length must be multiple of encoding-unit, %s" % (unitsize,))
        if len(obj) > length-unitsize:
            obj = obj[:length-unitsize]
        obj = obj.ljust(length, b"\x00")
        _write_stream(stream, obj, length)
        return originalobj

    def _sizeof(self, context, path):
        length = self.length(context) if callable(self.length) else self.length
        return length

    def _emitparse(self, code):
        unitsize, finalunit = calculateunits(self.encoding)
        code.append("""
            def parse_paddedtrimmedstring(io, length, unitsize, finalunit):
                if length % unitsize:
                    raise StringError
                obj = read_bytes(io, length)
                endsat = len(obj)
                while endsat-unitsize >= 0 and obj[endsat-unitsize:endsat] == finalunit:
                    endsat -= unitsize
                return obj[:endsat]
        """)
        return "parse_paddedtrimmedstring(io, %s, %s, %r)" % (self.length, unitsize, finalunit, )


class StringNullTerminated(Construct):
    """Used internally."""

    def __init__(self, encoding):
        super(StringNullTerminated, self).__init__()
        self.encoding = selectencoding(encoding)

    def _parse(self, stream, context, path):
        unitsize, finalunit = calculateunits(self.encoding)
        result = []
        while True:
            unit = _read_stream(stream, unitsize)
            if unit == finalunit:
                break
            result.append(unit)
        return b"".join(result)

    def _build(self, obj, stream, context, path):
        originalobj = obj
        unitsize, finalunit = calculateunits(self.encoding)

        if len(obj) % unitsize:
            raise StringError("string length must be multiple of encoding-unit, %s" % (unitsize,))
        data = obj + finalunit
        _write_stream(stream, data)
        return originalobj

    def _emitparse(self, code):
        unitsize, finalunit = calculateunits(self.encoding)
        code.append("""
            def parse_nullterminatedstring(io, unitsize, finalunit):
                result = []
                while True:
                    unit = read_bytes(io, unitsize)
                    if unit == finalunit:
                        break
                    result.append(unit)
                return b"".join(result)
        """)
        return "parse_nullterminatedstring(io, %s, %r)" % (unitsize, finalunit, )


def PaddedString(length, encoding):
    r"""
    Configurable, fixed-length or variable-length string field.

    When parsing, the byte string is stripped of null bytes (per encoding unit), then decoded. Length is an integer or context lambda. When building, the string is encoded, then trimmed to specified length minus encoding unit, then padded to specified length. Size is same as length parameter.

    .. warning:: PaddedString and CString only support encodings explicitly listed in :class:`~construct.core.possiblestringencodings` .

    :param length: integer or context lambda, length in bytes (not unicode characters)
    :param encoding: string like: utf8 utf16 utf32 ascii

    :raises StringError: building a non-unicode string
    :raises StringError: specified length or object for building is not a multiple of unit
    :raises StringError: selected encoding is not on supported list

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        >>> d = PaddedString(10, "utf8")
        >>> d.build(u"Афон")
        b'\xd0\x90\xd1\x84\xd0\xbe\xd0\xbd\x00\x00'
        >>> d.parse(_)
        u'Афон'
    """
    return StringEncoded(StringPaddedTrimmed(length, encoding), encoding)


def PascalString(lengthfield, encoding):
    r"""
    Length-prefixed string. The length field can be variable length (such as VarInt) or fixed length (such as Int64ub). VarInt is recommended when designing new protocols. Stored length is in bytes, not characters. Size is not defined.

    :class:`~construct.core.VarInt` is recommended for new protocols, as it is more compact and never overflows.

    :param lengthfield: Construct instance, field used to parse and build the length (like VarInt Int64ub)
    :param encoding: string like: utf8 utf16 utf32 ascii

    :raises StringError: building a non-unicode string

    Example::

        >>> d = PascalString(VarInt, "utf8")
        >>> d.build(u"Афон")
        b'\x08\xd0\x90\xd1\x84\xd0\xbe\xd0\xbd'
        >>> d.parse(_)
        u'Афон'
    """
    return StringEncoded(Prefixed(lengthfield, GreedyBytes), encoding)


def CString(encoding):
    r"""
    String ending in a terminating null byte (or null bytes in case of UTF16 UTF32).

    .. warning:: String and CString only support encodings explicitly listed in :class:`~construct.core.possiblestringencodings` .

    :param encoding: string like: utf8 utf16 utf32 ascii

    :raises StringError: building a non-unicode string
    :raises StringError: object for building is not a multiple of unit
    :raises StringError: selected encoding is not on supported list

    Example::

        >>> d = CString("utf8")
        >>> d.build(u"Афон")
        b'\xd0\x90\xd1\x84\xd0\xbe\xd0\xbd\x00'
        >>> d.parse(_)
        u'Афон'
    """
    return StringEncoded(StringNullTerminated(encoding), encoding)


def GreedyString(encoding):
    r"""
    String that reads entire stream until EOF, and writes a given string as-is. If no encoding is specified, this is essentially GreedyBytes.

    Analog to :class:`~construct.core.GreedyBytes` , and identical when no enoding is used.

    :param encoding: string like: utf8 utf16 utf32 ascii

    :raises StringError: building a non-unicode string
    :raises StreamError: stream failed when reading until EOF

    Example::

        >>> d = GreedyString("utf8")
        >>> d.build(u"Афон")
        b'\xd0\x90\xd1\x84\xd0\xbe\xd0\xbd'
        >>> d.parse(_)
        u'Афон'
    """
    return StringEncoded(GreedyBytes, encoding)


#===============================================================================
# mappings
#===============================================================================
@singleton
class Flag(Construct):
    r"""
    One byte (or one bit) field that maps to True or False. Other non-zero bytes are also considered True. Size is defined as 1.

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes

    Example::

        >>> Flag.parse(b"\x01")
        True
        >>> Flag.build(True)
        b'\x01'
    """

    def _parse(self, stream, context, path):
        return _read_stream(stream, 1) != b"\x00"

    def _build(self, obj, stream, context, path):
        _write_stream(stream, b"\x01" if obj else b"\x00", 1)
        return obj

    def _sizeof(self, context, path):
        return 1

    def _emitparse(self, code):
        return "(read_bytes(io, 1) != b'\\x00')"


class EnumInteger(int):
    """Used internally."""
    pass


class EnumIntegerString(str):
    """Used internally."""

    def __repr__(self):
        return "EnumIntegerString.new(%s, %s)" % (self.intvalue, str.__repr__(self), )

    def __int__(self):
        return self.intvalue

    @staticmethod
    def new(intvalue, stringvalue):
        ret = EnumIntegerString(stringvalue)
        ret.intvalue = intvalue
        return ret


class Enum(Adapter):
    r"""
    Translates unicode label names to subcon values, and vice versa.

    Parses integer subcon, then uses that value to lookup mapping dictionary. Returns an integer-convertible string (if mapping found) or an integer (otherwise). Building is a reversed process. Can build from an integer flag or string label. Size is same as subcon, unless it raises SizeofError.

    There is no default parameter, because if no mapping is found, it parses into an integer without error.

    This class supports enum34 module. See examples.

    This class supports exposing member labels as attributes, as integer-convertible strings. See examples.

    :param subcon: Construct instance, subcon to map to/from
    :param \*merge: optional, list of enum.IntEnum and enum.IntFlag instances, to merge labels and values from
    :param \*\*mapping: dict, mapping string names to values

    :raises MappingError: building from string but no mapping found

    Example::

        >>> d = Enum(Byte, one=1, two=2, four=4, eight=8)
        >>> d.parse(b"\x01")
        'one'
        >>> d.parse(b"\xff")
        255
        >>> d.build(d.one)
        b'\x01'
        >>> d.build("one")
        b'\x01'
        >>> d.build(1)
        b'\x01'
        >>> d.one
        'one'
        >>> int(d.one)
        1

        import enum
        class E(enum.IntEnum):
            one = 1
        class F(enum.IntFlag):
            two = 2
        Enum(Byte,      E, F) <--> Enum(Byte,      one=1, two=2)
        FlagsEnum(Byte, E, F) <--> FlagsEnum(Byte, one=1, two=2)
    """

    def __init__(self, subcon, *merge, **mapping):
        super(Enum, self).__init__(subcon)
        for enum in merge:
            for enumentry in enum:
                mapping[enumentry.name] = enumentry.value
        self.encmapping = {EnumIntegerString.new(v,k):v for k,v in mapping.items()}
        self.decmapping = {v:EnumIntegerString.new(v,k) for k,v in mapping.items()}

    def __getattr__(self, name):
        if name in self.encmapping:
            return self.decmapping[self.encmapping[name]]
        raise AttributeError

    def _decode(self, obj, context, path):
        try:
            return self.decmapping[obj]
        except KeyError:
            return EnumInteger(obj)

    def _encode(self, obj, context, path):
        try:
            if isinstance(obj, integertypes):
                return obj
            return self.encmapping[obj]
        except KeyError:
            raise MappingError("building failed, no mapping for %r" % (obj,))

    def _emitparse(self, code):
        fname = "factory_%s" % code.allocateId()
        code.append("%s = %r" % (fname, self.decmapping, ))
        return "reuse(%s, lambda x: %s.get(x, EnumInteger(x)))" % (self.subcon._compileparse(code), fname, )


class BitwisableString(str):
    """Used internally."""

    # def __repr__(self):
    #     return "BitwisableString(%s)" % (str.__repr__(self), )

    def __or__(self, other):
        return BitwisableString("{}|{}".format(self, other))


class FlagsEnum(Adapter):
    r"""
    Translates unicode label names to subcon integer (sub)values, and vice versa.

    Parses integer subcon, then creates a Container, where flags define each key. Builds from a container by bitwise-oring of each flag if it matches a set key. Can build from an integer flag or string label directly, as well as | concatenations thereof (see examples). Size is same as subcon, unless it raises SizeofError.

    This class supports enum34 module. See examples.

    This class supports exposing member labels as attributes, as bitwisable strings. See examples.

    :param subcon: Construct instance, must operate on integers
    :param \*merge: optional, list of enum.IntEnum and enum.IntFlag instances, to merge labels and values from
    :param \*\*flags: dict, mapping string names to integer values

    :raises MappingError: building from object not like: integer string dict
    :raises MappingError: building from string but no mapping found

    Can raise arbitrary exceptions when computing | and & and value is non-integer.

    Example::

        >>> d = FlagsEnum(Byte, one=1, two=2, four=4, eight=8)
        >>> d.parse(b"\x03")
        Container(one=True)(two=True)(four=False)(eight=False)
        >>> d.build(dict(one=True,two=True))
        b'\x03'
        >>> d.build(d.one|d.two)
        b'\x03'
        >>> d.build("one|two")
        b'\x03'
        >>> d.build(1|2)
        b'\x03'
        >>> d.eight
        'eight'
        >>> d.one|d.two
        'one|two'

        import enum
        class E(enum.IntEnum):
            one = 1
        class F(enum.IntFlag):
            two = 2
        Enum(Byte,      E, F) <--> Enum(Byte,      one=1, two=2)
        FlagsEnum(Byte, E, F) <--> FlagsEnum(Byte, one=1, two=2)
    """

    def __init__(self, subcon, *merge, **flags):
        super(FlagsEnum, self).__init__(subcon)
        for enum in merge:
            for enumentry in enum:
                flags[enumentry.name] = enumentry.value
        self.flags = flags

    def __getattr__(self, name):
        if name in self.flags:
            return BitwisableString(name)
        raise AttributeError

    def _decode(self, obj, context, path):
        obj2 = Container()
        obj2._flagsenum = True
        for name,value in self.flags.items():
            obj2[BitwisableString(name)] = bool(obj & value)
        return obj2

    def _encode(self, obj, context, path):
        try:
            if isinstance(obj, integertypes):
                return obj
            if isinstance(obj, stringtypes):
                flags = 0
                for name in obj.split("|"):
                    name = name.strip()
                    if name:
                        flags |= self.flags[name] # KeyError
                return flags
            if isinstance(obj, dict):
                flags = 0
                for name,value in obj.items():
                    if not name.startswith("_"): # assumes key is a string
                        if value:
                            flags |= self.flags[name] # KeyError
                return flags
            raise MappingError("building failed, unknown object: %r" % (obj,))
        except KeyError:
            raise MappingError("building failed, unknown label: %r" % (obj,))

    def _emitparse(self, code):
        return "reuse(%s, lambda x: Container(%s))" % (self.subcon._compileparse(code), ", ".join("%s=bool(x & %s)" % (k,v) for k,v in self.flags.items()), )


class Mapping(Adapter):
    r"""
    Adapter that maps objects to other objects. Translates objects after parsing and before building. Can for example, be used to translate between enum34 objects and strings, but Enum class supports enum34 already and is recommended.

    :param subcon: Construct instance
    :param mapping: dict, for encoding (building) mapping, the reversed is used for parsing mapping

    :raises MappingError: parsing or building but no mapping found

    Example::

        >>> x = object
        >>> d = Mapping(Byte, {x:0})
        >>> d.parse(b"\x00")
        x
        >>> d.build(x)
        b'\x00'
    """

    def __init__(self, subcon, mapping):
        super(Mapping, self).__init__(subcon)
        self.decmapping = {v:k for k,v in mapping.items()}
        self.encmapping = mapping

    def _decode(self, obj, context, path):
        try:
            return self.decmapping[obj] # KeyError
        except (KeyError, TypeError):
            raise MappingError("parsing failed, no decoding mapping for %r" % (obj,))

    def _encode(self, obj, context, path):
        try:
            return self.encmapping[obj] # KeyError
        except (KeyError, TypeError):
            raise MappingError("building failed, no encoding mapping for %r" % (obj,))

    def _emitparse(self, code):
        fname = "factory_%s" % code.allocateId()
        code.append("%s = %r" % (fname, self.decmapping, ))
        return "%s[%s]" % (fname, self.subcon._compileparse(code), )


#===============================================================================
# structures and sequences
#===============================================================================
class Struct(Construct):
    r"""
    Sequence of usually named constructs, similar to structs in C. The members are parsed and build in the order they are defined. If a member is anonymous (its name is None) then it gets parsed and the value discarded, or it gets build from nothing (from None).

    Some fields do not need to be named, since they are built without value anyway. See: Const Padding Check Error Pass Terminated Seek Tell for examples of such fields. :class:`~construct.core.Embedded` fields do not need to (and should not) be named.

    Operator + can also be used to make Structs (although not recommended).

    Parses into a Container (dict with attribute and key access) where keys match subcon names. Builds from a dict (not necessarily a Container) where each member gets a value from the dict matching the subcon name. If field has build-from-none flag, it gets build even when there is no matching entry in the dict. Size is the sum of all subcon sizes, unless any subcon raises SizeofError.

    This class does context nesting, meaning its members are given access to a new dictionary where the "_" entry points to the outer context. When parsing, each member gets parsed and subcon parse return value is inserted into context under matching key only if the member was named. When building, the matching entry gets inserted into context before subcon gets build, and if subcon build returns a new value (not None) that gets replaced in the context.

    This class supports embedding. :class:`~construct.core.Embedded` semantics dictate, that during instance creation (in ctor), each field is checked for embedded flag, and its subcon members are merged. This changes behavior of some code examples. Only few classes are supported: Struct Sequence FocusedSeq Union LazyStruct, although those can be used interchangably (a Struct can embed a Sequence, or rather its members).

    This class exposes subcons as attributes. You can refer to subcons that were inlined (and therefore do not exist as variable in the namespace) by accessing the struct attributes, under same name. Also note that compiler does not support this feature. See examples.

    This class exposes subcons in the context. You can refer to subcons that were inlined (and therefore do not exist as variable in the namespace) within other inlined fields using the context. Note that you need to use a lambda (`this` expression is not supported). Also note that compiler does not support this feature. See examples.

    This class supports stopping. If :class:`~construct.core.StopIf` field is a member, and it evaluates its lambda as positive, this class ends parsing or building as successful without processing further fields.

    :param \*subcons: Construct instances, list of members, some can be anonymous
    :param \*\*subconskw: Construct instances, list of members (requires Python 3.6)

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises KeyError: building a subcon but found no corresponding key in dictionary

    Example::

        >>> d = Struct("num"/Int8ub, "data"/Bytes(this.num))
        >>> d.parse(b"\x04DATA")
        Container(num=4)(data=b"DATA")
        >>> d.build(dict(num=4, data=b"DATA"))
        b"\x04DATA"

        >>> d = Struct(Const(b"MZ"), Padding(2), Pass, Terminated)
        >>> d.build({})
        b'MZ\x00\x00'
        >>> d.parse(_)
        Container()
        >>> d.sizeof()
        4

        >>> d = Struct(
        ...     "animal" / Enum(Byte, giraffe=1),
        ... )
        >>> d.animal.giraffe
        'giraffe'
        >>> d = Struct(
        ...     "count" / Byte,
        ...     "data" / Bytes(lambda this: this.count - this._subcons.count.sizeof()),
        ... )
        >>> d.build(dict(count=3, data=b"12"))
        b'\x0312'

        Alternative syntax (not recommended):
        >>> ("a"/Byte + "b"/Byte + "c"/Byte + "d"/Byte)

        Alternative syntax, but requires Python 3.6:
        >>> Struct(a=Byte, b=Byte, c=Byte, d=Byte)
    """

    def __init__(self, *subcons, **subconskw):
        super(Struct, self).__init__()
        subcons = list(subcons) + list(k/v for k,v in subconskw.items())
        self.subcons = mergefields(*subcons)
        self._subcons = Container((sc.name,sc) for sc in self.subcons if sc.name)
        self.flagbuildnone = all(sc.flagbuildnone for sc in self.subcons)

    def __getattr__(self, name):
        if name in self._subcons:
            return self._subcons[name]
        raise AttributeError

    def _parse(self, stream, context, path):
        obj = Container()
        context = Container(_ = context)
        context._subcons = self._subcons
        for sc in self.subcons:
            try:
                subobj = sc._parsereport(stream, context, path)
                if sc.name:
                    obj[sc.name] = subobj
                    context[sc.name] = subobj
            except StopFieldError:
                break
        return obj

    def _build(self, obj, stream, context, path):
        if obj is None:
            obj = Container()
        context = Container(_ = context)
        context._subcons = self._subcons
        context.update(obj)
        for sc in self.subcons:
            try:
                if sc.flagbuildnone:
                    subobj = obj.get(sc.name, None)
                else:
                    subobj = obj[sc.name] # raises KeyError

                if sc.name:
                    context[sc.name] = subobj

                buildret = sc._build(subobj, stream, context, path)
                if sc.name:
                    context[sc.name] = buildret
            except StopFieldError:
                break
        return context

    def _sizeof(self, context, path):
        context = Container(_ = context)
        context._subcons = self._subcons
        try:
            return sum(sc._sizeof(context, path) for sc in self.subcons)
        except (KeyError, AttributeError):
            raise SizeofError("cannot calculate size, key not found in context")

    def _emitparse(self, code):
        fname = "parse_struct_%s" % code.allocateId()
        block = """
            def %s(io, this):
                this = Container(_ = this)
                try:
        """ % (fname, )
        for sc in self.subcons:
            block += """
                    %s%s
            """ % ("this[%r] = " % sc.name if sc.name else "", sc._compileparse(code))
        block += """
                    pass
                except StopFieldError:
                    pass
                del this['_']
                del this['_index']
                return this
        """
        code.append(block)
        return "%s(io, this)" % (fname,)


class Sequence(Construct):
    r"""
    Sequence of usually un-named constructs. The members are parsed and build in the order they are defined. If a member is named, its parsed value gets inserted into the context. This allows using members that refer to previous members. :class:`~construct.core.Embedded` fields do not need to (and should not) be named.

    Operator >> can also be used to make Sequences (although not recommended).

    Parses into a ListContainer (list with pretty-printing) where values are in same order as subcons. Builds from a list (not necessarily a ListContainer) where each subcon is given the element at respective position. Size is the sum of all subcon sizes, unless any subcon raises SizeofError.

    This class does context nesting, meaning its members are given access to a new dictionary where the "_" entry points to the outer context. When parsing, each member gets parsed and subcon parse return value is inserted into context under matching key only if the member was named. When building, the matching entry gets inserted into context before subcon gets build, and if subcon build returns a new value (not None) that gets replaced in the context.

    This class supports embedding. :class:`~construct.core.Embedded` semantics dictate, that during instance creation (in ctor), each field is checked for embedded flag, and its subcon members are merged. This changes behavior of some code examples. Only few classes are supported: Struct Sequence FocusedSeq Union LazyStruct, although those can be used interchangably (a Struct can embed a Sequence, or rather its members).

    This class exposes subcons as attributes. You can refer to subcons that were inlined (and therefore do not exist as variable in the namespace) by accessing the struct attributes, under same name. Also note that compiler does not support this feature. See examples.

    This class exposes subcons in the context. You can refer to subcons that were inlined (and therefore do not exist as variable in the namespace) within other inlined fields using the context. Note that you need to use a lambda (`this` expression is not supported). Also note that compiler does not support this feature. See examples.

    This class supports stopping. If :class:`~construct.core.StopIf` field is a member, and it evaluates its lambda as positive, this class ends parsing or building as successful without processing further fields.

    :param \*subcons: Construct instances, list of members, some can be named
    :param \*\*subconskw: Construct instances, list of members (requires Python 3.6)

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises KeyError: building a subcon but found no corresponding key in dictionary

    Example::

        >>> d = Sequence(Byte, Float32b)
        >>> d.build([0, 1.23])
        b'\x00?\x9dp\xa4'
        >>> d.parse(_)
        [0, 1.2300000190734863] # a ListContainer

        >>> d = Sequence(
        ...     "animal" / Enum(Byte, giraffe=1),
        ... )
        >>> d.animal.giraffe
        'giraffe'
        >>> d = Sequence(
        ...     "count" / Byte,
        ...     "data" / Bytes(lambda this: this.count - this._subcons.count.sizeof()),
        ... )
        >>> d.build([3, b"12"])
        b'\x0312'

        Alternative syntax (not recommended):
        >>> (Byte >> "Byte >> "c"/Byte >> "d"/Byte)

        Alternative syntax, but requires Python 3.6:
        >>> Sequence(a=Byte, b=Byte, c=Byte, d=Byte)
    """

    def __init__(self, *subcons, **subconskw):
        super(Sequence, self).__init__()
        subcons = list(subcons) + list(k/v for k,v in subconskw.items())
        self.subcons = mergefields(*subcons)
        self._subcons = Container((sc.name,sc) for sc in self.subcons if sc.name)
        self.flagbuildnone = all(sc.flagbuildnone for sc in self.subcons)

    def __getattr__(self, name):
        if name in self._subcons:
            return self._subcons[name]
        raise AttributeError

    def _parse(self, stream, context, path):
        obj = ListContainer()
        context = Container(_ = context)
        context._subcons = self._subcons
        for i,sc in enumerate(self.subcons):
            try:
                subobj = sc._parsereport(stream, context, path)
                obj.append(subobj)
                if sc.name:
                    context[sc.name] = subobj
            except StopFieldError:
                break
        return obj

    def _build(self, obj, stream, context, path):
        if obj is None:
            obj = ListContainer([None for sc in self.subcons])
        context = Container(_ = context)
        context._subcons = self._subcons
        retlist = ListContainer()
        for i,(sc,subobj) in enumerate(zip(self.subcons, obj)):
            try:
                if sc.name:
                    context[sc.name] = subobj

                buildret = sc._build(subobj, stream, context, path)
                retlist.append(buildret)
                if sc.name:
                    context[sc.name] = buildret
            except StopFieldError:
                break
        return retlist

    def _sizeof(self, context, path):
        context = Container(_ = context)
        context._subcons = self._subcons
        try:
            return sum(sc._sizeof(context, path) for sc in self.subcons)
        except (KeyError, AttributeError):
            raise SizeofError("cannot calculate size, key not found in context")

    def _emitparse(self, code):
        fname = "parse_sequence_%s" % code.allocateId()
        block = """
            def %s(io, this):
                result = ListContainer()
                this = Container(_ = this)
                try:
        """ % (fname,)
        for sc in self.subcons:
            block += """
                    result.append(%s)
            """ % (sc._compileparse(code))
            if sc.name:
                block += """
                    this[%r] = result[-1]
                """ % (sc.name, )
        block += """
                    pass
                except StopFieldError:
                    pass
                return result
        """
        code.append(block)
        return "%s(io, this)" % (fname,)


#===============================================================================
# arrays ranges and repeaters
#===============================================================================
class Array(Subconstruct):
    r"""
    Homogenous array of elements, similar to C# generic T[].

    Parses into a ListContainer (a list). Parsing and building processes an exact amount of elements. If given list has more or less than count elements, raises RangeError. Size is defined as count multiplied by subcon size, but only if subcon is fixed size.

    Operator [] can be used to make Array (recommended) and GreedyRange instances.

    :param count: integer or context lambda, strict amount of elements
    :param subcon: Construct instance, subcon to process individual elements
    :param discard: optional, bool, if set then parsing returns empty list

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises RangeError: specified count is not valid
    :raises RangeError: given object has different length than specified count

    Can propagate any exception from the lambdas, possibly non-ConstructError.

    Example::

        >>> d = Array(5, Byte) or Byte[5]
        >>> d.build(range(5))
        b'\x00\x01\x02\x03\x04'
        >>> d.parse(_)
        [0, 1, 2, 3, 4]

        Alternative syntax (recommended):
        >>> Bytes[5] creates Array
        >>> Byte[3:5], Byte[3:], Byte[:5] are invalid
        >>> Byte[:] creates GreedyRange
    """

    def __init__(self, count, subcon, discard=False):
        super(Array, self).__init__(subcon)
        self.count = count
        self.discard = discard

    def _parse(self, stream, context, path):
        count = self.count
        if callable(count):
            count = count(context)
        if not 0 <= count:
            raise RangeError("invalid count %s" % (count,))
        obj = ListContainer()
        for i in range(count):
            context._index = i
            e = self.subcon._parsereport(stream, context, path)
            if not self.discard:
                obj.append(e)
        return obj

    def _build(self, obj, stream, context, path):
        count = self.count
        if callable(count):
            count = count(context)
        if not 0 <= count:
            raise RangeError("invalid count %s" % (count,))
        if not len(obj) == count:
            raise RangeError("expected %d elements, found %d" % (count, len(obj)))
        retlist = ListContainer()
        for i,e in enumerate(obj):
            context._index = i
            buildret = self.subcon._build(e, stream, context, path)
            retlist.append(buildret)
        return retlist

    def _sizeof(self, context, path):
        try:
            count = self.count
            if callable(count):
                count = count(context)
        except (KeyError, AttributeError):
            raise SizeofError("cannot calculate size, key not found in context")
        return count * self.subcon._sizeof(context, path)

    def _emitparse(self, code):
        return "ListContainer((this.__setitem__('_index',i),(%s))[1] for i in range(%s))" % (self.subcon._compileparse(code), self.count, )


class GreedyRange(Subconstruct):
    r"""
    Homogenous array of elements, similar to C# generic IEnumerable<T>, but works with unknown count of elements by parsing until end of stream.

    Parses into a ListContainer (a list). Parsing stops when an exception occured inside subcon, possibly due to EOF. Builds from enumerable. Size is undefined.

    This class supports stopping. If :class:`~construct.core.StopIf` field is a member, and it evaluates its lambda as positive, this class ends parsing or building as successful without processing further fields.

    Operator [] can be used to make Array (recommended) and GreedyRange instances.

    :param subcon: Construct instance, subcon to process individual elements
    :param discard: optional, bool, if set then parsing returns empty list

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises StreamError: stream is not seekable and tellable

    Can propagate any exception from the lambdas, possibly non-ConstructError.

    Example::

        >>> d = GreedyRange(Byte) or Byte[:]
        >>> d.build(range(8))
        b'\x00\x01\x02\x03\x04\x05\x06\x07'
        >>> d.parse(_)
        [0, 1, 2, 3, 4, 5, 6, 7]

        Alternative syntax (recommended):
        >>> Bytes[5] creates Array
        >>> Byte[3:5], Byte[3:], Byte[:5] are invalid
        >>> Byte[:] creates GreedyRange
    """

    def __init__(self, subcon, discard=False):
        super(GreedyRange, self).__init__(subcon)
        self.discard = discard

    def _parse(self, stream, context, path):
        obj = ListContainer()
        try:
            for i in itertools.count():
                context._index = i
                fallback = _tell_stream(stream)
                e = self.subcon._parsereport(stream, context, path)
                if not self.discard:
                    obj.append(e)
        except StopFieldError:
            pass
        except ExplicitError:
            raise
        except Exception:
            _seek_stream(stream, fallback)
        return obj

    def _build(self, obj, stream, context, path):
        try:
            retlist = ListContainer()
            for i,e in enumerate(obj):
                context._index = i
                buildret = self.subcon._build(e, stream, context, path)
                retlist.append(buildret)
            return retlist
        except StopFieldError:
            pass

    def _sizeof(self, context, path):
        raise SizeofError


class RepeatUntil(Subconstruct):
    r"""
    Homogenous array of elements, similar to C# generic IEnumerable<T>, that repeats until the predicate indicates it to stop. Note that the last element (that predicate indicated as True) is included in the return list.

    Parse iterates indefinately until last element passed the predicate. Build iterates indefinately over given list, until an element passed the precicate (or raises RepeatError if no element passed it). Size is undefined.

    :param predicate: lambda that takes (obj, list, context) and returns True to break or False to continue (or a truthy value)
    :param subcon: Construct instance, subcon used to parse and build each element
    :param discard: optional, bool, if set then parsing returns empty list

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises RepeatError: consumed all elements in the stream but neither passed the predicate

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        >>> d = RepeatUntil(lambda x,lst,ctx: x > 7, Byte)
        >>> d.build(range(20))
        b'\x00\x01\x02\x03\x04\x05\x06\x07\x08'
        >>> d.parse(b"\x01\xff\x02")
        [1, 255]

        >>> d = RepeatUntil(lambda x,lst,ctx: lst[-2:] == [0,0], Byte)
        >>> d.parse(b"\x01\x00\x00\xff")
        [1, 0, 0]
    """

    def __init__(self, predicate, subcon, discard=False):
        super(RepeatUntil, self).__init__(subcon)
        self.predicate = predicate
        self.discard = discard

    def _parse(self, stream, context, path):
        predicate = self.predicate
        if not callable(predicate):
            predicate = lambda _1,_2,_3: predicate
        obj = ListContainer()
        for i in itertools.count():
            context._index = i
            e = self.subcon._parsereport(stream, context, path)
            if not self.discard:
                obj.append(e)
            if predicate(e, obj, context):
                return obj

    def _build(self, obj, stream, context, path):
        predicate = self.predicate
        if not callable(predicate):
            predicate = lambda _1,_2,_3: predicate
        partiallist = ListContainer()
        retlist = ListContainer()
        for i,e in enumerate(obj):
            context._index = i
            buildret = self.subcon._build(e, stream, context, path)
            retlist.append(buildret)
            partiallist.append(buildret)
            if predicate(e, partiallist, context):
                break
        else:
            raise RepeatError("expected any item to match predicate, when building")
        return retlist

    def _sizeof(self, context, path):
        raise SizeofError("cannot calculate size, amount depends on actual data")

    def _emitparse(self, code):
        fname = "parse_repeatuntil_%s" % code.allocateId()
        block = """
            def %s(io, this):
                list_ = ListContainer()
                for i in itertools.count():
                    this['_index'] = i
                    obj_ = %s
                    list_.append(obj_)
                    if (%s):
                        return list_
        """ % (fname, self.subcon._compileparse(code), self.predicate, )
        code.append(block)
        return "%s(io, this)" % (fname,)


#===============================================================================
# specials
#===============================================================================
class Embedded(Subconstruct):
    r"""
    Special wrapper that allows outer multiple-subcons construct to merge fields from another multiple-subcons construct. Embedded does not change a field, only wraps it like a candy with a flag.

    .. warning::

        Can only be used between Struct Sequence FocusedSeq Union LazyStruct, although they can be used interchangably, for example Struct can embed fields from a Sequence. There is also :class:`~construct.core.EmbeddedSwitch` macro.

    Parsing building and size are deferred to subcon.

    :param subcon: Construct instance, field to embed inside outer struct or sequence

    Example::

        >>> outer = Struct(
        ...     Embedded(Struct(
        ...         "data" / Bytes(4),
        ...     )),
        ... )
        >>> outer.parse(b"1234")
        Container(data=b'1234')
    """

    def __init__(self, subcon):
        super(Embedded, self).__init__(subcon)
        self.flagembedded = True


class Renamed(Subconstruct):
    r"""
    Special wrapper that allows a Struct (or other similar class) to see a field as having a name (or a different name) or having a parsed hook. Library classes do not have names (its None). Renamed does not change a field, only wraps it like a candy with a label. Used internally by / and * operators.

    Also this wrapper is responsible for building a path info (a chain of names) that gets attached to error message when parsing, building, or sizeof fails. Fields that are not named do not appear in the path string.

    Parsing building and size are deferred to subcon.

    :param subcon: Construct instance
    :param newname: optional, string
    :param newdocs: optional, string
    :param newparsed: optional, lambda

    Example::

        >>> "number" / Int32ub
        <Renamed: number>
    """

    def __init__(self, subcon, newname=None, newdocs=None, newparsed=None):
        super(Renamed, self).__init__(subcon)
        self.name = newname if newname else subcon.name
        self.docs = newdocs if newdocs else subcon.docs
        self.parsed = newparsed if newparsed else subcon.parsed

    def __getattr__(self, name):
        return getattr(self.subcon, name)

    def _parse(self, stream, context, path):
        path += " -> %s" % (self.name,)
        return self.subcon._parsereport(stream, context, path)

    def _build(self, obj, stream, context, path):
        path += " -> %s" % (self.name,)
        return self.subcon._build(obj, stream, context, path)

    def _sizeof(self, context, path):
        path += " -> %s" % (self.name,)
        return self.subcon._sizeof(context, path)

    def _emitparse(self, code):
        return self.subcon._compileparse(code)


#===============================================================================
# miscellaneous
#===============================================================================
class Const(Subconstruct):
    r"""
    Field enforcing a constant. It is used for file signatures, to validate that the given pattern exists. Data in the stream must strictly match the specified value.

    Note that a variable sized subcon may still provide positive verification. Const does not consume a precomputed amount of bytes, but depends on the subcon to read the appropriate amount (eg. VarInt is acceptable). Whatever subcon parses into, gets compared against the specified value.

    Parses using subcon and return its value (after checking). Builds using subcon from nothing (or given object, if not None). Size is the same as subcon, unless it raises SizeofError.

    :param value: expected value, usually a bytes literal
    :param subcon: optional, Construct instance, subcon used to build value from, assumed to be Bytes if value parameter was a bytes literal

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises ConstError: parsed data does not match specified value, or building from wrong value
    :raises StringError: building from non-bytes value, perhaps unicode

    Example::

        >>> d = Const(b"IHDR")
        >>> d.build(None)
        b'IHDR'
        >>> d.parse(b"JPEG")
        construct.core.ConstError: expected b'IHDR' but parsed b'JPEG'

        >>> d = Const(255, Int32ul)
        >>> d.build(None)
        b'\xff\x00\x00\x00'
    """

    def __init__(self, value, subcon=None):
        if subcon is None:
            if not isinstance(value, bytestringtype):
                raise StringError("given non-bytes value, perhaps unicode? %r" % (value,))
            subcon = Bytes(len(value))
        super(Const, self).__init__(subcon)
        self.value = value
        self.flagbuildnone = True

    def _parse(self, stream, context, path):
        obj = self.subcon._parsereport(stream, context, path)
        if obj != self.value:
            raise ConstError("parsing expected %r but parsed %r" % (self.value, obj))
        return obj

    def _build(self, obj, stream, context, path):
        if obj not in (None, self.value):
            raise ConstError("building expected None or %r but got %r" % (self.value, obj))
        return self.subcon._build(self.value, stream, context, path)

    def _sizeof(self, context, path):
        return self.subcon._sizeof(context, path)

    def _emitparse(self, code):
        code.append("""
            def parse_const(value, expected):
                if not value == expected: raise ConstError
                return value
        """)
        return "parse_const(%s, %r)" % (self.subcon._compileparse(code), self.value,)


class Computed(Construct):
    r"""
    Field computing a value from the context dictionary or some outer source like os.urandom or random module. Underlying byte stream is unaffected. The source can be non-deterministic.

    Parsing and Building return the value returned by the context lambda (although a constant value can also be used). Size is defined as 0 because parsing and building does not consume or produce bytes into the stream.

    :param func: context lambda or constant value

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::
        >>> d = Struct(
        ...     "width" / Byte,
        ...     "height" / Byte,
        ...     "total" / Computed(this.width * this.height),
        ... )
        >>> d.build(dict(width=4,height=5))
        b'\x04\x05'
        >>> d.parse(b"12")
        Container(width=49)(height=50)(total=2450)

        >>> d = Computed(7)
        >>> d.parse(b"")
        7
        >>> d = Computed(lambda ctx: 7)
        >>> d.parse(b"")
        7

        >>> import os
        >>> d = Computed(lambda ctx: os.urandom(10))
        >>> d.parse(b"")
        b'\x98\xc2\xec\x10\x07\xf5\x8e\x98\xc2\xec'
    """

    def __init__(self, func):
        super(Computed, self).__init__()
        self.func = func
        self.flagbuildnone = True

    def _parse(self, stream, context, path):
        return self.func(context) if callable(self.func) else self.func

    def _build(self, obj, stream, context, path):
        return self.func(context) if callable(self.func) else self.func

    def _sizeof(self, context, path):
        return 0

    def _emitparse(self, code):
        return "%r" % (self.func,)


@singleton
class Index(Construct):
    r"""
    Indexes a field inside outer :class:`~construct.core.Array` :class:`~construct.core.GreedyRange` :class:`~construct.core.RepeatUntil` context.

    Note that you can use this class, or use `this._index` or `this._._index` expressions instead, depending on how its used. See the examples.

    Parsing and building pulls _index or _._index key from the context, in that order. Size is 0 because stream is unaffected.

    :raises IndexFieldError: did not find either key in context

    Example::

        >>> d = Array(3, Index)
        >>> d.parse(b"")
        [0, 1, 2]
        >>> d = Array(3, Struct("i" / Index))
        >>> d.parse(b"")
        [Container(i=0), Container(i=1), Container(i=2)]

        >>> d = Array(3, Computed(this._index+1))
        >>> d.parse(b"")
        [1, 2, 3]
        >>> d = Array(3, Struct("i" / Computed(this._._index+1)))
        >>> d.parse(b"")
        [Container(i=1), Container(i=2), Container(i=3)]
    """

    def __init__(self):
        super(self.__class__, self).__init__()
        self.flagbuildnone = True

    def _parse(self, stream, context, path):
        if "_index" in context:
            return context._index
        if "_" in context and "_index" in context._:
            return context._._index
        raise IndexFieldError("did not find either key in context")

    def _build(self, obj, stream, context, path):
        if "_index" in context:
            return context._index
        if "_" in context and "_index" in context._:
            return context._._index
        raise IndexFieldError("did not find either key in context")

    def _sizeof(self, context, path):
        return 0


class Rebuild(Subconstruct):
    r"""
    Field where building does not require a value, because the value gets recomputed when needed. Comes handy when building a Struct from a dict with missing keys. Useful for length and count fields when :class:`~construct.core.Prefixed` and :class:`~construct.core.PrefixedArray` cannot be used.

    Parsing defers to subcon. Building is defered to subcon, but it builds from a value provided by the context lambda (or constant). Size is the same as subcon, unless it raises SizeofError.

    Difference between Default and Rebuild, is that in first the build value is optional and in second the build value is ignored.

    :param subcon: Construct instance
    :param func: context lambda or constant value

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        >>> d = Struct(
        ...     "count" / Rebuild(Byte, len_(this.items)),
        ...     "items" / Byte[this.count],
        ... )
        >>> d.build(dict(items=[1,2,3]))
        b'\x03\x01\x02\x03'
    """

    def __init__(self, subcon, func):
        super(Rebuild, self).__init__(subcon)
        self.func = func
        self.flagbuildnone = True

    def _build(self, obj, stream, context, path):
        obj = self.func(context) if callable(self.func) else self.func
        return self.subcon._build(obj, stream, context, path)

    def _emitparse(self, code):
        return self.subcon._compileparse(code)


class Default(Subconstruct):
    r"""
    Field where building does not require a value, because the value gets taken from default. Comes handy when building a Struct from a dict with missing keys.

    Parsing defers to subcon. Building is defered to subcon, but it builds from a default (if given object is None) or from given object. Building does not require a value, but can accept one. Size is the same as subcon, unless it raises SizeofError.

    Difference between Default and Rebuild, is that in first the build value is optional and in second the build value is ignored.

    :param subcon: Construct instance
    :param value: context lambda or constant value

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        >>> d = Struct(
        ...     "a" / Default(Byte, 0),
        ... )
        >>> d.build(dict(a=1))
        b'\x01'
        >>> d.build(dict())
        b'\x00'
    """

    def __init__(self, subcon, value):
        super(Default, self).__init__(subcon)
        self.value = value
        self.flagbuildnone = True

    def _build(self, obj, stream, context, path):
        obj = (self.value(context) if callable(self.value) else self.value) if obj is None else obj
        return self.subcon._build(obj, stream, context, path)

    def _emitparse(self, code):
        return self.subcon._compileparse(code)


class Check(Construct):
    r"""
    Checks for a condition, and raises CheckError if the check fails.

    Parsing and building return nothing (but check the condition). Size is 0 because stream is unaffected.

    :param func: bool or context lambda, that gets run on parsing and building

    :raises CheckError: lambda returned false

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        Check(lambda ctx: len(ctx.payload.data) == ctx.payload_len)
        Check(len_(this.payload.data) == this.payload_len)
    """

    def __init__(self, func):
        super(Check, self).__init__()
        self.func = func
        self.flagbuildnone = True

    def _parse(self, stream, context, path):
        passed = self.func(context) if callable(self.func) else self.func
        if not passed:
            raise CheckError("check failed during parsing")

    def _build(self, obj, stream, context, path):
        passed = self.func(context) if callable(self.func) else self.func
        if not passed:
            raise CheckError("check failed during building")

    def _sizeof(self, context, path):
        return 0

    def _emitparse(self, code):
        code.append("""
            def parse_check(condition):
                if not condition: raise CheckError
        """)
        return "parse_check(%s)" % (self.func,)


@singleton
class Error(Construct):
    r"""
    Raises ExplicitError, unconditionally.

    Parsing and building always raise ExplicitError. Size is undefined.

    :raises ExplicitError: unconditionally, on parsing and building

    Example::

        >>> d = Struct("num"/Byte, Error)
        >>> d.parse(b"data...")
        construct.core.ExplicitError: Error field was activated during parsing
    """

    def __init__(self):
        super(self.__class__, self).__init__()
        self.flagbuildnone = True

    def _parse(self, stream, context, path):
        raise ExplicitError("Error field was activated during parsing")

    def _build(self, obj, stream, context, path):
        raise ExplicitError("Error field was activated during building")

    def _sizeof(self, context, path):
        raise SizeofError("Error does not have size, because it interrupts parsing and building")

    def _emitparse(self, code):
        code.append("""
            def parse_error():
                raise ExplicitError
        """)
        return "parse_error()"


class FocusedSeq(Construct):
    r"""
    Allows constructing more elaborate "adapters" than Adapter class.

    Parse does parse all subcons in sequence, but returns only the element that was selected (discards other values). Build does build all subcons in sequence, where each gets build from nothing (except the selected subcon which is given the object). Size is the sum of all subcon sizes, unless any subcon raises SizeofError.

    This class does context nesting, meaning its members are given access to a new dictionary where the "_" entry points to the outer context. When parsing, each member gets parsed and subcon parse return value is inserted into context under matching key only if the member was named. When building, the matching entry gets inserted into context before subcon gets build, and if subcon build returns a new value (not None) that gets replaced in the context.

    This class supports embedding. :class:`~construct.core.Embedded` semantics dictate, that during instance creation (in ctor), each field is checked for embedded flag, and its subcon members are merged. This changes behavior of some code examples. Only few classes are supported: Struct Sequence FocusedSeq Union LazyStruct, although those can be used interchangably (a Struct can embed a Sequence, or rather its members).

    This class exposes subcons as attributes. You can refer to subcons that were inlined (and therefore do not exist as variable in the namespace) by accessing the struct attributes, under same name. Also note that compiler does not support this feature. See examples.

    This class exposes subcons in the context. You can refer to subcons that were inlined (and therefore do not exist as variable in the namespace) within other inlined fields using the context. Note that you need to use a lambda (`this` expression is not supported). Also note that compiler does not support this feature. See examples.

    This class is used internally to implement :class:`~construct.core.PrefixedArray`.

    :param parsebuildfrom: integer index or string name or context lambda, selects a subcon
    :param \*subcons: Construct instances, list of members, some can be named
    :param \*\*subconskw: Construct instances, list of members (requires Python 3.6)

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises IndexError: selector does not match any subcon
    :raises KeyError: selector does not match any subcon

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Excample::

        >>> d = FocusedSeq(1 or "num", Const(b"SIG"), "num"/Byte, Terminated)
        >>> d.parse(b"SIG\xff")
        255
        >>> d.build(255)
        b'SIG\xff'

        >>> d = FocusedSeq(0,
        ...     "animal" / Enum(Byte, giraffe=1),
        ... )
        >>> d.animal.giraffe
        'giraffe'
        >>> d = FocusedSeq(0,
        ...     "count" / Byte,
        ...     "data" / Padding(lambda this: this.count - this._subcons.count.sizeof()),
        ... )
        >>> d.build(4)
        b'\x04\x00\x00\x00'

        PrefixedArray <--> FocusedSeq(1,
            "count" / Rebuild(lengthfield, len_(this.items)),
            "items" / subcon[this.count],
        )
    """

    def __init__(self, parsebuildfrom, *subcons, **subconskw):
        super(FocusedSeq, self).__init__()
        self.parsebuildfrom = parsebuildfrom
        subcons = list(subcons) + list(k/v for k,v in subconskw.items())
        self.subcons = mergefields(*subcons)
        self._subcons = Container((sc.name,sc) for sc in self.subcons if sc.name)

    def __getattr__(self, name):
        if name in self._subcons:
            return self._subcons[name]
        raise AttributeError

    def _parse(self, stream, context, path):
        context = Container(_ = context)
        context._subcons = self._subcons
        parsebuildfrom = self.parsebuildfrom
        if callable(parsebuildfrom):
            parsebuildfrom = parsebuildfrom(context)
        if isinstance(parsebuildfrom, int):
            index = parsebuildfrom
            self.subcons[index]  # raises IndexError
        if isinstance(parsebuildfrom, str):
            index = {sc.name:i for i,sc in enumerate(self.subcons) if sc.name}[parsebuildfrom] # raises KeyError
        for i,sc in enumerate(self.subcons):
            parseret = sc._parsereport(stream, context, path)
            if sc.name:
                context[sc.name] = parseret
            if i == index:
                finalret = parseret
        return finalret

    def _build(self, obj, stream, context, path):
        context = Container(_ = context)
        context._subcons = self._subcons
        parsebuildfrom = self.parsebuildfrom
        if callable(parsebuildfrom):
            parsebuildfrom = parsebuildfrom(context)
        if isinstance(parsebuildfrom, int):
            index = parsebuildfrom
            self.subcons[index]  # raises IndexError
        if isinstance(parsebuildfrom, str):
            index = {sc.name:i for i,sc in enumerate(self.subcons) if sc.name}[parsebuildfrom] # raises KeyError
        context[index] = obj
        sc = self.subcons[index]
        if sc.name:
            context[sc.name] = obj
        for i,sc in enumerate(self.subcons):
            buildret = sc._build(obj if i==index else None, stream, context, path)
            if sc.name:
                context[sc.name] = buildret
            if i == index:
                finalret = buildret
        return finalret

    def _sizeof(self, context, path):
        context = Container(_ = context)
        context._subcons = self._subcons
        try:
            return sum(sc._sizeof(context, path) for sc in self.subcons)
        except (KeyError, AttributeError):
            raise SizeofError("cannot calculate size, key not found in context")

    def _emitparse(self, code):
        if callable(self.parsebuildfrom):
            raise NotImplementedError("FocusedSeq does not compile non-constant selectors")
        fname = "parse_focusedseq_%s" % code.allocateId()
        block = """
            def %s(io, this):
                result = []
                this = Container(_ = this)
        """ % (fname, )
        for sc in self.subcons:
            block += """
                result.append(%s)
            """ % (sc._compileparse(code), )
            if sc.name:
                block += """
                this[%r] = result[-1]
                """ % (sc.name, )
        parsebuildfrom = self.parsebuildfrom
        if isinstance(parsebuildfrom, int):
            index = parsebuildfrom
            self.subcons[index]  # raises IndexError
        if isinstance(parsebuildfrom, str):
            index = {sc.name:i for i,sc in enumerate(self.subcons) if sc.name}[parsebuildfrom] # raises KeyError
        block += """
                return result[%s]
        """ % (index, )
        code.append(block)
        return "%s(io, this)" % (fname,)


@singleton
class Pickled(Construct):
    r"""
    Preserves arbitrary Python objects.

    Parses using `pickle.load() <https://docs.python.org/3/library/pickle.html#pickle.load>`_ and builds using `pickle.dump() <https://docs.python.org/3/library/pickle.html#pickle.dump>`_ functions, using default Pickle binary protocol. Size is undefined.

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes

    Can propagate pickle.load() and pickle.dump() exceptions.

    Example::

        >>> x = [1, 2.3, {}]
        >>> Pickled.build(x)
        b'\x80\x03]q\x00(K\x01G@\x02ffffff}q\x01e.'
        >>> Pickled.parse(_)
        [1, 2.3, {}]
    """

    def _parse(self, stream, context, path):
        return pickle.load(stream)

    def _build(self, obj, stream, context, path):
        pickle.dump(obj, stream)
        return obj


@singleton
class Numpy(Construct):
    r"""
    Preserves numpy arrays (both shape, dtype and values).

    Parses using `numpy.load() <https://docs.scipy.org/doc/numpy/reference/generated/numpy.load.html#numpy.load>`_ and builds using `numpy.save() <https://docs.scipy.org/doc/numpy/reference/generated/numpy.save.html#numpy.save>`_ functions, using Numpy binary protocol. Size is undefined.

    :raises ImportError: numpy could not be imported during parsing or building
    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes

    Can propagate numpy.load() and numpy.save() exceptions.

    Example::

        >>> import numpy
        >>> a = numpy.asarray([1,2,3])
        >>> Numpy.build(a)
        b"\x93NUMPY\x01\x00F\x00{'descr': '<i8', 'fortran_order': False, 'shape': (3,), }            \n\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00"
        >>> Numpy.parse(_)
        array([1, 2, 3])
    """

    def _parse(self, stream, context, path):
        import numpy
        return numpy.load(stream)

    def _build(self, obj, stream, context, path):
        import numpy
        numpy.save(stream, obj)
        return obj


class NamedTuple(Adapter):
    r"""
    Both arrays, structs, and sequences can be mapped to a namedtuple from `collections module <https://docs.python.org/3/library/collections.html#collections.namedtuple>`_. To create a named tuple, you need to provide a name and a sequence of fields, either a string with space-separated names or a list of string names, like the standard namedtuple.

    Parses into a collections.namedtuple instance, and builds from such instance (although it also builds from lists and dicts). Size is undefined.

    :param tuplename: string
    :param tuplefields: string or list of strings
    :param subcon: Construct instance, either Struct Sequence Array GreedyRange

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises NamedTupleError: subcon is neither Struct Sequence Array GreedyRange

    Can propagate collections exceptions.

    Example::

        >>> d = NamedTuple("coord", "x y z", Byte[3])
        >>> d = NamedTuple("coord", "x y z", Byte >> Byte >> Byte)
        >>> d = NamedTuple("coord", "x y z", "x"/Byte + "y"/Byte + "z"/Byte)
        >>> d.parse(b"123")
        coord(x=49, y=50, z=51)
    """

    def __init__(self, tuplename, tuplefields, subcon):
        if not isinstance(subcon, (Struct,Sequence,Array,GreedyRange)):
            raise NamedTupleError("subcon is neither Struct Sequence Array GreedyRange")
        super(NamedTuple, self).__init__(subcon)
        self.tuplename = tuplename
        self.tuplefields = tuplefields
        self.factory = collections.namedtuple(tuplename, tuplefields)

    def _decode(self, obj, context, path):
        if isinstance(self.subcon, Struct):
            return self.factory(**obj)
        if isinstance(self.subcon, (Sequence,Array,GreedyRange)):
            return self.factory(*obj)
        raise NamedTupleError("subcon is neither Struct Sequence Array GreedyRangeGreedyRange")

    def _encode(self, obj, context, path):
        if isinstance(self.subcon, Struct):
            return Container({sc.name:getattr(obj,sc.name) for sc in self.subcon.subcons if sc.name})
        if isinstance(self.subcon, (Sequence,Array,GreedyRange)):
            return list(obj)
        raise NamedTupleError("subcon is neither Struct Sequence Array GreedyRange")

    def _emitparse(self, code):
        fname = "factory_%s" % code.allocateId()
        code.append("""
            %s = collections.namedtuple(%r, %r)
        """ % (fname, self.tuplename, self.tuplefields, ))
        if isinstance(self.subcon, Struct):
            return "%s(**(%s))" % (fname, self.subcon._compileparse(code), )
        if isinstance(self.subcon, (Sequence,Array,GreedyRange)):
            return "%s(*(%s))" % (fname, self.subcon._compileparse(code), )
        raise NamedTupleError("subcon is neither Struct Sequence Array GreedyRange")


def Timestamp(subcon, unit, epoch):
    r"""
    Datetime, represented as `Arrow <https://pypi.org/project/arrow/>`_ object.

    Note that accuracy is not guaranteed, because building rounds the value to integer (even when Float subcon is used), due to floating-point errors in general, and because MSDOS scheme has only 5-bit (32 values) seconds field (seconds are rounded to multiple of 2).

    Unit is a fraction of a second. 1 is second resolution, 10**-3 is milliseconds resolution, 10**-6 is microseconds resolution, etc. Usually its 1 on Unix and MacOSX, 10**-7 on Windows. Epoch is a year (if integer) or a specific day (if Arrow object). Usually its 1970 on Unix, 1904 on MacOSX, 1600 on Windows. MSDOS format doesnt support custom unit or epoch, it uses 2-seconds resolution and 1980 epoch.

    :param subcon: Construct instance like Int* Float*, or Int32ub with msdos format
    :param unit: integer or float, or msdos string
    :param epoch: integer, or Arrow instance, or msdos string

    :raises ImportError: arrow could not be imported during ctor
    :raises TimestampError: subcon is not a Construct instance
    :raises TimestampError: unit or epoch is a wrong type

    Example::

        >>> d = Timestamp(Int64ub, 1., 1970)
        >>> d.parse(b'\x00\x00\x00\x00ZIz\x00')
        <Arrow [2018-01-01T00:00:00+00:00]>
        >>> d = Timestamp(Int32ub, "msdos", "msdos")
        >>> d.parse(b'H9\x8c"')
        <Arrow [2016-01-25T17:33:04+00:00]>
    """
    import arrow

    if not isinstance(subcon, Construct):
        raise TimestampError("subcon should be Int*, experimentally Float*, or Int32ub when using msdos format")
    if not isinstance(unit, (integertypes, float, stringtypes)):
        raise TimestampError("unit must be one of: int float string")
    if not isinstance(epoch, (integertypes, arrow.Arrow, stringtypes)):
        raise TimestampError("epoch must be one of: int Arrow string")

    if unit == "msdos" or epoch == "msdos":
        st = BitStruct(
            "year" / BitsInteger(7),
            "month" / BitsInteger(4),
            "day" / BitsInteger(5),
            "hour" / BitsInteger(5),
            "minute" / BitsInteger(6),
            "second" / BitsInteger(5),
        )
        class MsdosTimestampAdapter(Adapter):
            def _decode(self, obj, context, path):
                return arrow.Arrow(1980,1,1).shift(years=obj.year, months=obj.month-1, days=obj.day-1, hours=obj.hour, minutes=obj.minute, seconds=obj.second*2)
            def _encode(self, obj, context, path):
                t = obj.timetuple()
                return Container(year=t.tm_year-1980, month=t.tm_mon, day=t.tm_mday, hour=t.tm_hour, minute=t.tm_min, second=t.tm_sec//2)
        return MsdosTimestampAdapter(st)

    if isinstance(epoch, integertypes):
        epoch = arrow.Arrow(epoch, 1, 1)
    class TimestampAdapter(Adapter):
        def _decode(self, obj, context, path):
            return epoch.shift(seconds=obj*unit)
        def _encode(self, obj, context, path):
            return int((obj-epoch).total_seconds()/unit)
    return TimestampAdapter(subcon)


class Hex(Adapter):
    r"""
    Adapter for displaying hexadecimal/hexlified representation of integers/bytes/RawCopy dictionaries.

    Parsing results in int-alike bytes-alike or dict-alike object, whose only difference from original is pretty-printing. If you look at the result, you will be presented with its `repr` which remains as-is. If you print it, then you will see its `str` whic is a hexlified representation. Building and sizeof defer to subcon.

    To obtain a hexlified string (like before Hex HexDump changed semantics) use binascii.(un)hexlify on parsed results.

    Example::

        >>> d = Hex(Int32ub)
        >>> obj = d.parse(b"\x00\x00\x01\x02")
        >>> obj
        258
        >>> print(obj)
        0x00000102

        >>> d = Hex(GreedyBytes)
        >>> obj = d.parse(b"\x00\x00\x01\x02")
        >>> obj
        b'\x00\x00\x01\x02'
        >>> print(obj)
        unhexlify('00000102')

        >>> d = Hex(RawCopy(Int32ub))
        >>> obj = d.parse(b"\x00\x00\x01\x02")
        >>> obj
        {'data': b'\x00\x00\x01\x02',
         'length': 4,
         'offset1': 0,
         'offset2': 4,
         'value': 258}
        >>> print(obj)
        unhexlify('00000102')
    """
    def _decode(self, obj, context, path):
        if isinstance(obj, integertypes):
            return HexDisplayedInteger.new(obj, "0%sX" % (2 * self.subcon._sizeof(context, path)))
        if isinstance(obj, bytestringtype):
            return HexDisplayedBytes(obj)
        if isinstance(obj, dict):
            return HexDisplayedDict(obj)
        return obj

    def _encode(self, obj, context, path):
        return obj

    def _emitparse(self, code):
        return self.subcon._compileparse(code)


class HexDump(Adapter):
    r"""
    Adapter for displaying hexlified representation of bytes/RawCopy dictionaries.

    Parsing results in bytes-alike or dict-alike object, whose only difference from original is pretty-printing. If you look at the result, you will be presented with its `repr` which remains as-is. If you print it, then you will see its `str` whic is a hexlified representation. Building and sizeof defer to subcon.

    To obtain a hexlified string (like before Hex HexDump changed semantics) use construct.lib.hexdump on parsed results.

    Example::

        >>> d = HexDump(GreedyBytes)
        >>> obj = d.parse(b"\x00\x00\x01\x02")
        >>> obj
        b'\x00\x00\x01\x02'
        >>> print(obj)
        hexundump('''
        0000   00 00 01 02                                       ....
        ''')

        >>> d = HexDump(RawCopy(Int32ub))
        >>> obj = d.parse(b"\x00\x00\x01\x02")
        >>> obj
        {'data': b'\x00\x00\x01\x02',
         'length': 4,
         'offset1': 0,
         'offset2': 4,
         'value': 258}
        >>> print(obj)
        hexundump('''
        0000   00 00 01 02                                       ....
        ''')
    """
    def _decode(self, obj, context, path):
        if isinstance(obj, bytestringtype):
            return HexDumpDisplayedBytes(obj)
        if isinstance(obj, dict):
            return HexDumpDisplayedDict(obj)
        return obj

    def _encode(self, obj, context, path):
        return obj

    def _emitparse(self, code):
        return self.subcon._compileparse(code)


#===============================================================================
# conditional
#===============================================================================
class Union(Construct):
    r"""
    Treats the same data as multiple constructs (similar to C union) so you can look at the data in multiple views. Fields are usually named (so parsed values are inserted into dictionary under same name). :class:`~construct.core.Embedded` fields do not need to (and should not) be named.

    Parses subcons in sequence, and reverts the stream back to original position after each subcon. Afterwards, advances the stream by selected subcon. Builds from first subcon that has a matching key in given dict. Size is undefined (because parsefrom is not used for building).

    This class does context nesting, meaning its members are given access to a new dictionary where the "_" entry points to the outer context. When parsing, each member gets parsed and subcon parse return value is inserted into context under matching key only if the member was named. When building, the matching entry gets inserted into context before subcon gets build, and if subcon build returns a new value (not None) that gets replaced in the context.

    This class supports embedding. :class:`~construct.core.Embedded` semantics dictate, that during instance creation (in ctor), each field is checked for embedded flag, and its subcon members are merged. This changes behavior of some code examples. Only few classes are supported: Struct Sequence FocusedSeq Union LazyStruct, although those can be used interchangably (a Struct can embed a Sequence, or rather its members).

    This class exposes subcons as attributes. You can refer to subcons that were inlined (and therefore do not exist as variable in the namespace) by accessing the struct attributes, under same name. Also note that compiler does not support this feature. See examples.

    This class exposes subcons in the context. You can refer to subcons that were inlined (and therefore do not exist as variable in the namespace) within other inlined fields using the context. Note that you need to use a lambda (`this` expression is not supported). Also note that compiler does not support this feature. See examples.

    .. warning:: If you skip `parsefrom` parameter then stream will be left back at starting offset, not seeked to any common denominator.

    :param parsefrom: how to leave stream after parsing, can be integer index or string name selecting a subcon, or None (leaves stream at initial offset, the default), or context lambda
    :param \*subcons: Construct instances, list of members, some can be anonymous
    :param \*\*subconskw: Construct instances, list of members (requires Python 3.6)

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises StreamError: stream is not seekable and tellable
    :raises UnionError: selector does not match any subcon, or dict given to build does not contain any keys matching any subcon
    :raises IndexError: selector does not match any subcon
    :raises KeyError: selector does not match any subcon

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        >>> d = Union(0, "raw"/Bytes(8), "ints"/Int32ub[2], "shorts"/Int16ub[4], "chars"/Byte[8])
        >>> d.parse(b"12345678")
        Container(raw=b'12345678')(ints=[825373492, 892745528])(shorts=[12594, 13108, 13622, 14136])(chars=[49, 50, 51, 52, 53, 54, 55, 56])
        >>> d.build(dict(chars=range(8)))
        b'\x00\x01\x02\x03\x04\x05\x06\x07'

        >>> d = Union(None,
        ...     "animal" / Enum(Byte, giraffe=1),
        ... )
        >>> d.animal.giraffe
        'giraffe'
        >>> d = Union(None,
        ...     "chars" / Byte[4],
        ...     "data" / Bytes(lambda this: this._subcons.chars.sizeof()),
        ... )
        >>> d.parse(b"\x01\x02\x03\x04")
        Container(chars=[1, 2, 3, 4])(data=b'\x01\x02\x03\x04')

        Alternative syntax, but requires Python 3.6:
        >>> Union(0, raw=Bytes(8), ints=Int32ub[2], shorts=Int16ub[4], chars=Byte[8])
    """

    def __init__(self, parsefrom, *subcons, **subconskw):
        if isinstance(parsefrom, Construct):
            raise UnionError("parsefrom should be either: None int str context-function")
        super(Union, self).__init__()
        self.parsefrom = parsefrom
        subcons = list(subcons) + list(k/v for k,v in subconskw.items())
        self.subcons = mergefields(*subcons)
        self._subcons = Container((sc.name,sc) for sc in self.subcons if sc.name)

    def __getattr__(self, name):
        if name in self._subcons:
            return self._subcons[name]
        raise AttributeError

    def _parse(self, stream, context, path):
        obj = Container()
        context = Container(_ = context)
        context._subcons = self._subcons
        fallback = _tell_stream(stream)
        forwards = {}
        for i,sc in enumerate(self.subcons):
            subobj = sc._parsereport(stream, context, path)
            if sc.name:
                obj[sc.name] = subobj
                context[sc.name] = subobj
            forwards[i] = _tell_stream(stream)
            if sc.name:
                forwards[sc.name] = _tell_stream(stream)
            _seek_stream(stream, fallback)
        parsefrom = self.parsefrom
        if callable(parsefrom):
            parsefrom = parsefrom(context)
        if parsefrom is not None:
            _seek_stream(stream, forwards[parsefrom]) # raises KeyError
        return obj

    def _build(self, obj, stream, context, path):
        context = Container(_ = context)
        context._subcons = self._subcons
        context.update(obj)
        for sc in self.subcons:
            if sc.flagbuildnone:
                subobj = obj.get(sc.name, None)
            elif sc.name in obj:
                subobj = obj[sc.name]
            else:
                continue

            if sc.name:
                context[sc.name] = subobj

            buildret = sc._build(subobj, stream, context, path)
            if sc.name:
                context[sc.name] = buildret
            return Container({sc.name:buildret})
        else:
            raise UnionError("cannot build, none of subcons were found in the dictionary %r" % (obj, ))

    def _sizeof(self, context, path):
        raise SizeofError("Union builds depending on actual object dict, size is unknown")

    def _emitparse(self, code):
        if callable(self.parsefrom):
            raise NotImplementedError("Union does not compile non-constant parsefrom")
        fname = "parse_union_%s" % code.allocateId()
        block = """
            def %s(io, this):
                this = Container(_ = this)
                fallback = io.tell()
        """ % (fname, )
        if isinstance(self.parsefrom, type(None)):
            index = -1
            skipfallback = False
            skipforward = True
        if isinstance(self.parsefrom, int):
            index = self.parsefrom
            self.subcons[index] # raises IndexError
            skipfallback = True
            skipforward = self.subcons[index].sizeof() == self.subcons[-1].sizeof()
        if isinstance(self.parsefrom, str):
            index = {sc.name:i for i,sc in enumerate(self.subcons) if sc.name}[self.parsefrom] # raises KeyError
            skipfallback = True
            skipforward = self.subcons[index].sizeof() == self.subcons[-1].sizeof()

        for i,sc in enumerate(self.subcons):
            block += """
                %s%s
            """ % ("this[%r] = " % sc.name if sc.name else "", sc._compileparse(code))
            if i == index and not skipforward:
                block += """
                forward = io.tell()
                """
            if i < len(self.subcons)-1:
                block += """
                io.seek(fallback)
                """
        if not skipfallback:
            block += """
                io.seek(fallback)
            """
        if not skipforward:
            block += """
                io.seek(forward)
            """
        block += """
                del this['_']
                del this['_index']
                return this
        """
        code.append(block)
        return "%s(io, this)" % (fname,)


class Select(Construct):
    r"""
    Selects the first matching subconstruct.

    Parses and builds by literally trying each subcon in sequence until one of them parses or builds without exception. Stream gets reverted back to original position after each failed attempt, but not if parsing succeeds. Size is not defined.

    :param \*subcons: Construct instances, list of members, some can be anonymous
    :param \*\*subconskw: Construct instances, list of members (requires Python 3.6)

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises StreamError: stream is not seekable and tellable
    :raises SelectError: neither subcon succeded when parsing or building

    Example::

        >>> d = Select(Int32ub, CString("utf8"))
        >>> d.build(1)
        b'\x00\x00\x00\x01'
        >>> d.build(u"Афон")
        b'\xd0\x90\xd1\x84\xd0\xbe\xd0\xbd\x00'

        Alternative syntax, but requires Python 3.6:
        >>> Select(num=Int32ub, text=CString("utf8"))
    """

    def __init__(self, *subcons, **subconskw):
        super(Select, self).__init__()
        self.subcons = list(subcons) + list(k/v for k,v in subconskw.items())
        self.flagbuildnone = all(sc.flagbuildnone for sc in self.subcons)
        self.flagembedded = all(sc.flagembedded for sc in self.subcons)

    def _parse(self, stream, context, path):
        for sc in self.subcons:
            fallback = _tell_stream(stream)
            try:
                obj = sc._parsereport(stream, context, path)
            except ExplicitError:
                raise
            except ConstructError:
                _seek_stream(stream, fallback)
            else:
                return obj
        raise SelectError("no subconstruct matched")

    def _build(self, obj, stream, context, path):
        for sc in self.subcons:
            try:
                data = sc.build(obj, **context)
            except ExplicitError:
                raise
            except Exception:
                pass
            else:
                _write_stream(stream, data)
                return obj
        raise SelectError("no subconstruct matched: %s" % (obj,))


def Optional(subcon):
    r"""
    Makes an optional field.

    Parsing attempts to parse subcon. If sub-parsing fails, returns None and reports success. Building attempts to build subcon. If sub-building fails, writes nothing and reports success. Size is undefined, because whether bytes would be consumed or produced depends on actual data and actual context.

    :param subcon: Construct instance

    Example::

        Optional  <-->  Select(subcon, Pass)

        >>> d = Optional(Int64ul)
        >>> d.parse(b"12345678")
        4050765991979987505
        >>> d.parse(b"")
        None
        >>> d.build(1)
        b'\x01\x00\x00\x00\x00\x00\x00\x00'
        >>> d.build(None)
        b''
    """
    return Select(subcon, Pass)


def If(condfunc, subcon):
    r"""
    If-then conditional construct.

    Parsing evaluates condition, if True then subcon is parsed, otherwise just returns None. Building also evaluates condition, if True then subcon gets build from, otherwise does nothing. Size is either same as subcon or 0, depending how condfunc evaluates.

    :param condfunc: bool or context lambda (or a truthy value)
    :param subcon: Construct instance, used if condition indicates True

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        If <--> IfThenElse(condfunc, subcon, Pass)

        >>> d = If(this.x > 0, Byte)
        >>> d.build(255, x=1)
        b'\xff'
        >>> d.build(255, x=0)
        b''
    """
    return IfThenElse(condfunc, subcon, Pass)


class IfThenElse(Construct):
    r"""
    If-then-else conditional construct, similar to ternary operator.

    Parsing and building evaluates condition, and defers to either subcon depending on the value. Size is computed the same way.

    :param condfunc: bool or context lambda (or a truthy value)
    :param thensubcon: Construct instance, used if condition indicates True
    :param elsesubcon: Construct instance, used if condition indicates False

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        >>> d = IfThenElse(this.x > 0, VarInt, Byte)
        >>> d.build(255, dict(x=1))
        b'\xff\x01'
        >>> d.build(255, dict(x=0))
        b'\xff'
    """

    def __init__(self, condfunc, thensubcon, elsesubcon):
        super(IfThenElse, self).__init__()
        self.condfunc = condfunc
        self.thensubcon = thensubcon
        self.elsesubcon = elsesubcon
        self.flagbuildnone = thensubcon.flagbuildnone and elsesubcon.flagbuildnone

    def _parse(self, stream, context, path):
        condfunc = self.condfunc
        if callable(condfunc):
            condfunc = condfunc(context)
        sc = self.thensubcon if condfunc else self.elsesubcon
        return sc._parsereport(stream, context, path)

    def _build(self, obj, stream, context, path):
        condfunc = self.condfunc
        if callable(condfunc):
            condfunc = condfunc(context)
        sc = self.thensubcon if condfunc else self.elsesubcon
        return sc._build(obj, stream, context, path)

    def _sizeof(self, context, path):
        condfunc = self.condfunc
        if callable(condfunc):
            condfunc = condfunc(context)
        sc = self.thensubcon if condfunc else self.elsesubcon
        return sc._sizeof(context, path)

    def _emitparse(self, code):
        return "((%s) if (%s) else (%s))" % (self.thensubcon._compileparse(code), self.condfunc, self.elsesubcon._compileparse(code), )


class Switch(Construct):
    r"""
    A conditional branch.

    Parsing and building evaluate keyfunc and select a subcon based on the value and dictionary entries. Dictionary (cases) maps values into subcons. If no case matches then `default` is used (that is Pass by default). Note that `default` is a Construct instance, not a dictionary key. Size is evaluated in same way as parsing and building, by evaluating keyfunc and selecting a field accordingly.

    :param keyfunc: context lambda or constant, that matches some key in cases
    :param cases: dict mapping keys to Construct instances
    :param default: optional, Construct instance, used when keyfunc is not found in cases, Pass is default value for this parameter, Error is a possible value for this parameter

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        >>> d = Switch(this.n, { 1:Int8ub, 2:Int16ub, 4:Int32ub })
        >>> d.build(5, n=1)
        b'\x05'
        >>> d.build(5, n=4)
        b'\x00\x00\x00\x05'

        >>> d = Switch(this.n, {}, default=Byte)
        >>> d.parse(b"\x01", n=255)
        1
        >>> d.build(1, n=255)
        b"\x01"
    """

    def __init__(self, keyfunc, cases, default=None):
        if default is None:
            default = Pass
        super(Switch, self).__init__()
        self.keyfunc = keyfunc
        self.cases = cases
        self.default = default
        allcases = list(cases.values()) + [default]
        self.flagbuildnone = all(sc.flagbuildnone for sc in allcases)

    def _parse(self, stream, context, path):
        keyfunc = self.keyfunc
        if callable(keyfunc):
            keyfunc = keyfunc(context)
        sc = self.cases.get(keyfunc, self.default)
        return sc._parsereport(stream, context, path)

    def _build(self, obj, stream, context, path):
        keyfunc = self.keyfunc
        if callable(keyfunc):
            keyfunc = keyfunc(context)
        sc = self.cases.get(keyfunc, self.default)
        return sc._build(obj, stream, context, path)

    def _sizeof(self, context, path):
        try:
            keyfunc = self.keyfunc
            if callable(keyfunc):
                keyfunc = keyfunc(context)
            sc = self.cases.get(keyfunc, self.default)
            return sc._sizeof(context, path)

        except (KeyError, AttributeError):
            raise SizeofError("cannot calculate size, key not found in context")

    def _emitparse(self, code):
        fname = "factory_%s" % code.allocateId()
        code.append("%s = {%s}" % (fname, ", ".join("%r : lambda io,this: %s" % (key, sc._compileparse(code)) for key,sc in self.cases.items()), ))

        defaultfname = "compiled_%s" % code.allocateId()
        code.append("%s = lambda io,this: %s" % (defaultfname, self.default._compileparse(code), ))
        return "%s.get(%s, %s)(io, this)" % (fname, self.keyfunc, defaultfname)


def EmbeddedSwitch(merged, selector, mapping):
    r"""
    Macro that simulates embedding Switch, which under new embedding semantics is not possible. This macro does NOT produce a Switch. It generates classes that behave the same way as you would expect from embedded Switch, only that. Instance created by this macro CAN be embedded.

    Both `merged` and all values in `mapping` must be Struct instances. Macro re-creates a single struct that contains all fields, where each field is wrapped in `If(selector == key, ...)`. Note that resulting dictionary contains None values for fields that would not be chosen by switch. Note also that if selector does not match any cases, it passes successfully (default Switch behavior).

    All fields should have unique names. Otherwise fields that were not selected during parsing may return None and override other fields context entries that have same name. This is because `If` field returns None value if condition is not met, but the Struct inserts that None value into the context entry regardless.

    :param merged: Struct instance
    :param selector: this expression, that references one of `merged` fields
    :param mapping: dict with values being Struct instances

    Example::

        d = EmbeddedSwitch(
            Struct(
                "type" / Byte,
            ),
            this.type,
            {
                0: Struct("name" / PascalString(Byte, "utf8")),
                1: Struct("value" / Byte),
            }
        )

        # generates essentially following
        d = Struct(
            "type" / Byte,
            "name" / If(this.type == 0, PascalString(Byte, "utf8")),
            "value" / If(this.type == 1, Byte),
        )

        # both parse like following
        >>> d.parse(b"\x00\x00")
        Container(type=0)(name=u'')(value=None)
        >>> d.parse(b"\x01\x00")
        Container(type=1)(name=None)(value=0)
    """

    merged2 = list(merged.subcons)
    for key,sc in mapping.items():
        for sc2 in sc.subcons:
            merged2.append(sc2.name / If(selector == key, sc2))
    return Struct(*merged2)


class StopIf(Construct):
    r"""
    Checks for a condition, and stops certain classes (:class:`~construct.core.Struct` :class:`~construct.core.Sequence` :class:`~construct.core.GreedyRange`) from parsing or building further.

    Parsing and building check the condition, and raise StopFieldError if indicated. Size is undefined.

    :param condfunc: bool or context lambda (or truthy value)

    :raises StopFieldError: used internally

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        >>> Struct('x'/Byte, StopIf(this.x == 0), 'y'/Byte)
        >>> Sequence('x'/Byte, StopIf(this.x == 0), 'y'/Byte)
        >>> GreedyRange(FocusedSeq(0, 'x'/Byte, StopIf(this.x == 0)))
    """

    def __init__(self, condfunc):
        super(StopIf, self).__init__()
        self.condfunc = condfunc
        self.flagbuildnone = True

    def _parse(self, stream, context, path):
        condfunc = self.condfunc
        if callable(condfunc):
            condfunc = condfunc(context)
        if condfunc:
            raise StopFieldError

    def _build(self, obj, stream, context, path):
        condfunc = self.condfunc
        if callable(condfunc):
            condfunc = condfunc(context)
        if condfunc:
            raise StopFieldError

    def _sizeof(self, context, path):
        raise SizeofError("StopIf cannot determine size because it depends on actual context which then depends on actual data and outer constructs")

    def _emitparse(self, code):
        code.append("""
            def parse_stopif(condition):
                if condition:
                    raise StopFieldError
        """)
        return "parse_stopif(%s)" % (self.condfunc,)


#===============================================================================
# alignment and padding
#===============================================================================
def Padding(length, pattern=b"\x00"):
    r"""
    Appends null bytes.

    Parsing consumes specified amount of bytes and discards it. Building writes specified pattern byte multiplied into specified length. Size is same as specified.

    :param length: integer or context lambda, length of the padding
    :param pattern: b-character, padding pattern, default is \\x00

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises PaddingError: length was negative
    :raises PaddingError: pattern was not bytes (b-character)

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        >>> d = Padding(4)
        >>> d.build(None)
        b'\x00\x00\x00\x00'
        >>> d.parse(b"****")
        None
        >>> d.sizeof()
        4
    """
    return Padded(length, Pass, pattern=pattern)


class Padded(Subconstruct):
    r"""
    Appends additional null bytes to achieve a length.

    Note that subcon can actually be variable size, it is the eventual amount of bytes that is read or written during parsing or building that determines actual padding.

    Parsing first parses subcon, then consumes an amount of bytes to sum up to specified length, and discards it. Building first builds subcon, then writes specified pattern byte to sum up to specified length. Size is same as specified.

    :param length: integer or context lambda, length of the padding
    :param subcon: Construct instance
    :param pattern: b-character, padding pattern, default is \\x00

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises PaddingError: length was negative, or subcon read or written more than the length (would cause negative pad)
    :raises PaddingError: pattern was not bytes (b-character)

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        >>> d = Padded(4, Byte)
        >>> d.build(255)
        b'\xff\x00\x00\x00'
        >>> d.parse(_)
        255
        >>> d.sizeof()
        4

        >>> d = Padded(4, VarInt)
        >>> d.build(1)
        b'\x01\x00\x00\x00'
        >>> d.build(70000)
        b'\xf0\xa2\x04\x00'
    """

    def __init__(self, length, subcon, pattern=b"\x00"):
        if not isinstance(pattern, bytestringtype) or len(pattern) != 1:
            raise PaddingError("pattern expected to be bytes of length 1")
        super(Padded, self).__init__(subcon)
        self.length = length
        self.pattern = pattern

    def _parse(self, stream, context, path):
        length = self.length(context) if callable(self.length) else self.length
        position1 = _tell_stream(stream)
        obj = self.subcon._parsereport(stream, context, path)
        position2 = _tell_stream(stream)
        pad = length - (position2 - position1)
        if pad < 0:
            raise PaddingError("subcon parsed %d bytes but was allowed only %d" % (position2-position1, length))
        _read_stream(stream, pad)
        return obj

    def _build(self, obj, stream, context, path):
        length = self.length(context) if callable(self.length) else self.length
        position1 = _tell_stream(stream)
        buildret = self.subcon._build(obj, stream, context, path)
        position2 = _tell_stream(stream)
        pad = length - (position2 - position1)
        if pad < 0:
            raise PaddingError("subcon build %d bytes but was allowed only %d" % (position2-position1, length))
        _write_stream(stream, self.pattern * pad, pad)
        return buildret

    def _sizeof(self, context, path):
        try:
            return self.length(context) if callable(self.length) else self.length
        except (KeyError, AttributeError):
            raise SizeofError("cannot calculate size, key not found in context")

    def _emitparse(self, code):
        return "(%s, read_bytes(io, (%s)-(%s) ))[0]" % (self.subcon._compileparse(code), self.length, self.subcon.sizeof())


class Aligned(Subconstruct):
    r"""
    Appends additional null bytes to achieve a length that is shortest multiple of a modulus.

    Note that subcon can actually be variable size, it is the eventual amount of bytes that is read or written during parsing or building that determines actual padding.

    Parsing first parses subcon, then consumes an amount of bytes to sum up to specified length, and discards it. Building first builds subcon, then writes specified pattern byte to sum up to specified length. Size is subcon size plus modulo remainder, unless SizeofError was raised.

    :param modulus: integer or context lambda, modulus to final length
    :param subcon: Construct instance
    :param pattern: optional, b-character, padding pattern, default is \\x00

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises PaddingError: modulus was less than 2
    :raises PaddingError: pattern was not bytes (b-character)

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        >>> d = Aligned(4, Int16ub)
        >>> d.parse(b'\x00\x01\x00\x00')
        1
        >>> d.sizeof()
        4
    """

    def __init__(self, modulus, subcon, pattern=b"\x00"):
        if not isinstance(pattern, bytestringtype) or len(pattern) != 1:
            raise PaddingError("pattern expected to be bytes character")
        super(Aligned, self).__init__(subcon)
        self.modulus = modulus
        self.pattern = pattern

    def _parse(self, stream, context, path):
        modulus = self.modulus(context) if callable(self.modulus) else self.modulus
        if modulus < 2:
            raise PaddingError("expected modulo 2 or greater")
        position1 = _tell_stream(stream)
        obj = self.subcon._parsereport(stream, context, path)
        position2 = _tell_stream(stream)
        pad = -(position2 - position1) % modulus
        _read_stream(stream, pad)
        return obj

    def _build(self, obj, stream, context, path):
        modulus = self.modulus(context) if callable(self.modulus) else self.modulus
        if modulus < 2:
            raise PaddingError("expected modulo 2 or greater")
        position1 = _tell_stream(stream)
        buildret = self.subcon._build(obj, stream, context, path)
        position2 = _tell_stream(stream)
        pad = -(position2 - position1) % modulus
        _write_stream(stream, self.pattern * pad, pad)
        return buildret

    def _sizeof(self, context, path):
        try:
            modulus = self.modulus(context) if callable(self.modulus) else self.modulus
            if modulus < 2:
                raise PaddingError("expected modulo 2 or greater")
            subconlen = self.subcon._sizeof(context, path)
            return subconlen + (-subconlen % modulus)
        except (KeyError, AttributeError):
            raise SizeofError("cannot calculate size, key not found in context")

    def _emitparse(self, code):
        return "(%s, read_bytes(io, -(%s) %% (%s) ))[0]" % (self.subcon._compileparse(code), self.subcon.sizeof(), self.modulus, )


def AlignedStruct(modulus, *subcons, **subconskw):
    r"""
    Makes a structure where each field is aligned to the same modulus (it is a struct of aligned fields, NOT an aligned struct).

    See :class:`~construct.core.Aligned` and :class:`~construct.core.Struct` for semantics and raisable exceptions.

    :param modulus: integer or context lambda, passed to each member
    :param \*subcons: Construct instances, list of members, some can be anonymous
    :param \*\*subconskw: Construct instances, list of members (requires Python 3.6)

    Example::

        >>> d = AlignedStruct(4, "a"/Int8ub, "b"/Int16ub)
        >>> d.build(dict(a=0xFF,b=0xFFFF))
        b'\xff\x00\x00\x00\xff\xff\x00\x00'
    """
    subcons = list(subcons) + list(k/v for k,v in subconskw.items())
    return Struct(*[sc.name / Aligned(modulus, sc) for sc in subcons])


def BitStruct(*subcons, **subconskw):
    r"""
    Makes a structure inside a Bitwise.

    See :class:`~construct.core.Bitwise` and :class:`~construct.core.Struct` for semantics and raisable exceptions.

    :param \*subcons: Construct instances, list of members, some can be anonymous
    :param \*\*subconskw: Construct instances, list of members (requires Python 3.6)

    Example::

        BitStruct  <-->  Bitwise(Struct(...))

        >>> d = BitStruct(
        ...     "a" / Flag,
        ...     "b" / Nibble,
        ...     "c" / BitsInteger(10),
        ...     "d" / Padding(1),
        ... )
        >>> d.parse(b"\xbe\xef")
        Container(a=True)(b=7)(c=887)(d=None)
        >>> d.sizeof()
        2
    """
    return Bitwise(Struct(*subcons, **subconskw))


#===============================================================================
# stream manipulation
#===============================================================================
class Pointer(Subconstruct):
    r"""
    Jumps in the stream forth and back for one field.

    Parsing and building seeks the stream to new location, processes subcon, and seeks back to original location. Size is defined as 0 but that does not mean no bytes are written into the stream.

    Offset can be positive, indicating a position from stream beginning forward, or negative, indicating a position from EOF backwards.

    :param offset: integer or context lambda, positive or negative
    :param subcon: Construct instance

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises StreamError: stream is not seekable and tellable

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        >>> d = Pointer(8, Bytes(1))
        >>> d.parse(b"abcdefghijkl")
        b'i'
        >>> d.build(b"Z")
        b'\x00\x00\x00\x00\x00\x00\x00\x00Z'
    """

    def __init__(self, offset, subcon):
        super(Pointer, self).__init__(subcon)
        self.offset = offset

    def _parse(self, stream, context, path):
        offset = self.offset(context) if callable(self.offset) else self.offset
        fallback = _tell_stream(stream)
        _seek_stream(stream, offset, 2 if offset < 0 else 0)
        obj = self.subcon._parsereport(stream, context, path)
        _seek_stream(stream, fallback)
        return obj

    def _build(self, obj, stream, context, path):
        offset = self.offset(context) if callable(self.offset) else self.offset
        fallback = _tell_stream(stream)
        _seek_stream(stream, offset, 2 if offset < 0 else 0)
        buildret = self.subcon._build(obj, stream, context, path)
        _seek_stream(stream, fallback)
        return buildret

    def _sizeof(self, context, path):
        return 0

    def _emitparse(self, code):
        code.append("""
            def parse_pointer(io, offset, func):
                fallback = io.tell()
                io.seek(offset, 2 if offset < 0 else 0)
                obj = func()
                io.seek(fallback)
                return obj
        """)
        return "parse_pointer(io, %s, lambda: %s)" % (self.offset, self.subcon._compileparse(code),)


class Peek(Subconstruct):
    r"""
    Peeks at the stream.

    Parsing sub-parses (and returns None if failed), then reverts stream to original position. Building does nothing (its NOT deferred). Size is defined as 0 because there is no building.

    This class is used in :class:`~construct.core.Union` class to parse each member.

    :param subcon: Construct instance

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises StreamError: stream is not seekable and tellable

    Example::

        >>> d = Sequence(Peek(Int8ub), Peek(Int16ub))
        >>> d.parse(b"\x01\x02")
        [1, 258]
        >>> d.sizeof()
        0
    """

    def __init__(self, subcon):
        super(Peek, self).__init__(subcon)
        self.flagbuildnone = True

    def _parse(self, stream, context, path):
        fallback = _tell_stream(stream)
        try:
            return self.subcon._parsereport(stream, context, path)
        except ExplicitError:
            raise
        except ConstructError:
            pass
        finally:
            _seek_stream(stream, fallback)

    def _build(self, obj, stream, context, path):
        return obj

    def _sizeof(self, context, path):
        return 0

    def _emitparse(self, code):
        code.append("""
            def parse_peek(io, func):
                fallback = io.tell()
                try:
                    return func()
                except ExplicitError:
                    raise
                except ConstructError:
                    pass
                finally:
                    io.seek(fallback)
        """)
        return "parse_peek(io, lambda: %s)" % (self.subcon._compileparse(code),)


class Seek(Construct):
    r"""
    Seeks the stream.

    Parsing and building seek the stream to given location (and whence), and return stream.seek() return value. Size is not defined.

    .. seealso:: Analog :class:`~construct.core.Pointer` wrapper that has same side effect but also processes a subcon, and also seeks back.

    :param at: integer or context lambda, where to jump to
    :param whence: optional, integer or context lambda, is the offset from beginning (0) or from current position (1) or from EOF (2), default is 0

    :raises StreamError: stream is not seekable

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        >>> d = (Seek(5) >> Byte)
        >>> d.parse(b"01234x")
        [5, 120]

        >>> d = (Bytes(10) >> Seek(5) >> Byte)
        >>> d.build([b"0123456789", None, 255])
        b'01234\xff6789'
    """

    def __init__(self, at, whence=0):
        super(Seek, self).__init__()
        self.at = at
        self.whence = whence
        self.flagbuildnone = True

    def _parse(self, stream, context, path):
        at = self.at(context) if callable(self.at) else self.at
        whence = self.whence(context) if callable(self.whence) else self.whence
        return _seek_stream(stream, at, whence)

    def _build(self, obj, stream, context, path):
        at = self.at(context) if callable(self.at) else self.at
        whence = self.whence(context) if callable(self.whence) else self.whence
        return _seek_stream(stream, at, whence)

    def _sizeof(self, context, path):
        raise SizeofError("Seek only moves the stream, size is not meaningful")

    def _emitparse(self, code):
        return "io.seek(%s, %s)" % (self.at, self.whence, )


@singleton
class Tell(Construct):
    r"""
    Tells the stream.

    Parsing and building return current stream offset using using stream.tell(). Size is defined as 0 because parsing and building does not consume or add into the stream.

    Tell is useful for adjusting relative offsets to absolute positions, or to measure sizes of Constructs. To get an absolute pointer, use a Tell plus a relative offset. To get a size, place two Tells and measure their difference using a Compute field. However, its recommended to use :class:`~construct.core.RawCopy` instead of manually extracting two positions and computing difference.

    :raises StreamError: stream is not tellable

    Example::

        >>> d = Struct("num"/VarInt, "offset"/Tell)
        >>> d.parse(b"X")
        Container(num=88)(offset=1)
        >>> d.build(dict(num=88))
        b'X'
    """

    def __init__(self):
        super(self.__class__, self).__init__()
        self.flagbuildnone = True

    def _parse(self, stream, context, path):
        return _tell_stream(stream)

    def _build(self, obj, stream, context, path):
        return _tell_stream(stream)

    def _sizeof(self, context, path):
        return 0

    def _emitparse(self, code):
        return "io.tell()"


@singleton
class Pass(Construct):
    r"""
    No-op construct, useful as default cases for Switch and Enum.

    Parsing returns None. Building does nothing. Size is 0 by definition.

    Example::

        >>> Pass.parse(b"")
        None
        >>> Pass.build(None)
        b''
        >>> Pass.sizeof()
        0
    """

    def __init__(self):
        super(self.__class__, self).__init__()
        self.flagbuildnone = True

    def _parse(self, stream, context, path):
        return None

    def _build(self, obj, stream, context, path):
        return obj

    def _sizeof(self, context, path):
        return 0

    def _emitparse(self, code):
        return "None"


@singleton
class Terminated(Construct):
    r"""
    Asserts end of stream (EOF). You can use it to ensure no more unparsed data follows in the stream.

    Parsing checks if stream reached EOF, and raises TerminatedError if not. Building does nothing. Size is defined as 0 because parsing and building does not consume or add into the stream, as far as other constructs see it.

    :raises TerminatedError: stream not at EOF when parsing

    Example::

        >>> Terminated.parse(b"")
        None
        >>> Terminated.parse(b"remaining")
        construct.core.TerminatedError: expected end of stream
    """

    def __init__(self):
        super(self.__class__, self).__init__()
        self.flagbuildnone = True

    def _parse(self, stream, context, path):
        if stream.read(1):
            raise TerminatedError("expected end of stream")

    def _build(self, obj, stream, context, path):
        return obj

    def _sizeof(self, context, path):
        return 0


#===============================================================================
# tunneling and byte/bit swapping
#===============================================================================
class RawCopy(Subconstruct):
    r"""
    Used to obtain byte representation of a field (aside of object value).

    Returns a dict containing both parsed subcon value, the raw bytes that were consumed by subcon, starting and ending offset in the stream, and amount in bytes. Builds either from raw bytes representation or a value used by subcon. Size is same as subcon.

    Object is a dictionary with either "data" or "value" keys, or both.

    :param subcon: Construct instance

    :raises StreamError: stream is not seekable and tellable
    :raises RawCopyError: building and neither data or value was given
    :raises StringError: building from non-bytes value, perhaps unicode

    Example::

        >>> d = RawCopy(Byte)
        >>> d.parse(b"\xff")
        Container(data=b'\xff')(value=255)(offset1=0)(offset2=1)(length=1)
        >>> d.build(dict(data=b"\xff"))
        '\xff'
        >>> d.build(dict(value=255))
        '\xff'
    """

    def _parse(self, stream, context, path):
        offset1 = _tell_stream(stream)
        obj = self.subcon._parsereport(stream, context, path)
        offset2 = _tell_stream(stream)
        _seek_stream(stream, offset1)
        data = _read_stream(stream, offset2-offset1)
        return Container(data=data, value=obj, offset1=offset1, offset2=offset2, length=(offset2-offset1))

    def _build(self, obj, stream, context, path):
        if obj is None and self.subcon.flagbuildnone:
            obj = dict(value=None)
        if 'data' in obj:
            data = obj['data']
            offset1 = _tell_stream(stream)
            _write_stream(stream, data)
            offset2 = _tell_stream(stream)
            return Container(obj, data=data, offset1=offset1, offset2=offset2, length=(offset2-offset1))
        if 'value' in obj:
            value = obj['value']
            offset1 = _tell_stream(stream)
            buildret = self.subcon._build(value, stream, context, path)
            value = value if buildret is None else buildret
            offset2 = _tell_stream(stream)
            _seek_stream(stream, offset1)
            data = _read_stream(stream, offset2-offset1)
            return Container(obj, data=data, value=value, offset1=offset1, offset2=offset2, length=(offset2-offset1))
        raise RawCopyError('RawCopy cannot build, both data and value keys are missing')


def ByteSwapped(subcon):
    r"""
    Swaps the byte order within boundaries of given subcon. Requires a fixed sized subcon.

    :param subcon: Construct instance, subcon on top of byte swapped bytes

    :raises SizeofError: ctor or compiler could not compute subcon size

    See :class:`~construct.core.TransformData` and :class:`~construct.core.Restreamed` for raisable exceptions.

    Example::

        Int24ul <--> ByteSwapped(Int24ub) <--> BytesInteger(3, swapped=True) <--> ByteSwapped(BytesInteger(3))
    """

    size = subcon.sizeof()
    return TransformData(subcon, swapbytes, size, swapbytes, size)


def BitsSwapped(subcon):
    r"""
    Swaps the bit order within each byte within boundaries of given subcon. Does NOT require a fixed sized subcon.

    :param subcon: Construct instance, subcon on top of bit swapped bytes

    :raises SizeofError: compiler could not compute subcon size

    See :class:`~construct.core.TransformData` and :class:`~construct.core.Restreamed` for raisable exceptions.

    Example::

        >>> d = Bitwise(Bytes(8))
        >>> d.parse(b"\x01")
        '\x00\x00\x00\x00\x00\x00\x00\x01'
        >>>> BitsSwapped(d).parse(b"\x01")
        '\x01\x00\x00\x00\x00\x00\x00\x00'
    """

    try:
        size = subcon.sizeof()
        return TransformData(subcon, swapbitsinbytes, size, swapbitsinbytes, size)
    except SizeofError:
        return Restreamed(subcon, swapbitsinbytes, 1, swapbitsinbytes, 1, lambda n: n)


class Prefixed(Subconstruct):
    r"""
    Prefixes a field with byte count.

    Parses the length field. Then reads that amount of bytes, and parses subcon using only those bytes. Constructs that consume entire remaining stream are constrained to consuming only the specified amount of bytes (a substream). When building, data gets prefixed by its length. Optionally, length field can include its own size. Size is the sum of both fields sizes, unless either raises SizeofError.

    Analog to :class:`~construct.core.PrefixedArray` which prefixes with an element count, instead of byte count. Semantics is similar but implementation is different.

    :class:`~construct.core.VarInt` is recommended for new protocols, as it is more compact and never overflows.

    :param lengthfield: Construct instance, field used for storing the length
    :param subcon: Construct instance, subcon used for storing the value
    :param includelength: optional, bool, whether length field should include its own size, default is False

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes

    Example::

        >>> Prefixed(VarInt, GreedyRange(Int32ul)).parse(b"\x08abcdefgh")
        [1684234849, 1751606885]

        >>> PrefixedArray(VarInt, Int32ul).parse(b"\x02abcdefgh")
        [1684234849, 1751606885]
    """

    def __init__(self, lengthfield, subcon, includelength=False):
        super(Prefixed, self).__init__(subcon)
        self.lengthfield = lengthfield
        self.includelength = includelength

    def _parse(self, stream, context, path):
        length = self.lengthfield._parsereport(stream, context, path)
        if self.includelength:
            length -= self.lengthfield._sizeof(context, path)
        stream2 = io.BytesIO(_read_stream(stream, length))
        return self.subcon._parsereport(stream2, context, path)

    def _build(self, obj, stream, context, path):
        stream2 = io.BytesIO()
        buildret = self.subcon._build(obj, stream2, context, path)
        data = stream2.getvalue()
        length = len(data)
        if self.includelength:
            length += self.lengthfield._sizeof(context, path)
        self.lengthfield._build(length, stream, context, path)
        _write_stream(stream, data)
        return buildret

    def _sizeof(self, context, path):
        return self.lengthfield._sizeof(context, path) + self.subcon._sizeof(context, path)

    def _actualsize(self, stream, context, path):
        position1 = _tell_stream(stream)
        length = self.lengthfield._parse(stream, context, path)
        if self.includelength:
            length -= self.lengthfield._sizeof(context, path)
        position2 = _tell_stream(stream)
        return (position2-position1) + length

    def _emitparse(self, code):
        sub = self.lengthfield.sizeof() if self.includelength else 0
        return "restream(read_bytes(io, (%s)-(%s)), lambda io: %s)" % (self.lengthfield._compileparse(code), sub, self.subcon._compileparse(code), )


def PrefixedArray(countfield, subcon):
    r"""
    Prefixes an array with item count (as opposed to prefixed by byte count, see :class:`~construct.core.Prefixed`).

    :class:`~construct.core.VarInt` is recommended for new protocols, as it is more compact and never overflows.

    :param countfield: Construct instance, field used for storing the element count
    :param subcon: Construct instance, subcon used for storing each element

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises RangeError: consumed or produced too little elements

    Example::

        >>> Prefixed(VarInt, GreedyRange(Int32ul)).parse(b"\x08abcdefgh")
        [1684234849, 1751606885]

        >>> PrefixedArray(VarInt, Int32ul).parse(b"\x02abcdefgh")
        [1684234849, 1751606885]
    """
    macro = FocusedSeq("items",
        "count" / Rebuild(countfield, len_(this.items)),
        "items" / subcon[this.count],
    )
    def _emitparse(code):
        return "ListContainer((%s) for i in range(%s))" % (subcon._compileparse(code), countfield._compileparse(code), )
    macro._emitparse = _emitparse
    def _actualsize(self, stream, context, path):
        position1 = _tell_stream(stream)
        count = countfield._parse(stream, context, path)
        position2 = _tell_stream(stream)
        return (position2-position1) + count * subcon._sizeof(context, path)
    macro._actualsize = _actualsize
    return macro


class RestreamData(Subconstruct):
    r"""
    Parses a field on external data (but does not build).

    Parsing defers to subcon, but provides it a separate stream based on bytes data provided by datafunc (a bytes literal or context lambda). Building does nothing. Size is 0 because as far as other fields see it, this field does not produce or consume any bytes from the stream.

    :param datafunc: bytes or context lambda, provides data for subcon to parse
    :param subcon: Construct instance, subcon used for parsing the value

    Can propagate any exception from the lambdas, possibly non-ConstructError.

    Example::

        >>> d = RestreamData(b"\xff", Byte)
        >>> d.parse(b"")
        255
        >>> d.build(0)
        b''
    """

    def __init__(self, datafunc, subcon):
        super(RestreamData, self).__init__(subcon)
        self.datafunc = datafunc
        self.flagbuildnone = True

    def _parse(self, stream, context, path):
        data = self.datafunc
        if callable(data):
            data = data(context)
        stream2 = io.BytesIO(data)
        return self.subcon._parsereport(stream2, context, path)

    def _build(self, obj, stream, context, path):
        return obj

    def _sizeof(self, context, path):
        return 0

    def _emitparse(self, code):
        return "restream(%r, lambda io: %s)" % (self.datafunc, self.subcon._compileparse(code), )


class TransformData(Subconstruct):
    r"""
    Parses a field on transfored data (or transforms data after building).

    Parsing reads a specified amount, processes data using a bytes-to-bytes decoding function, then parses subcon using those data. Building does build subcon into separate bytes, then processes using encoding encoding, then writes those data into main stream. Size is reported as `encodeamount`.

    Used internally to implement :class:`~construct.core.Bitwise` :class:`~construct.core.Bytewise` :class:`~construct.core.ByteSwapped` :class:`~construct.core.BitsSwapped` .

    Possible use-cases include encryption, obfuscation, byte-level encoding.

    .. warning:: Remember that subcon must consume (or produce) an amount of bytes that is same as `decodeamount` (or `encodeamount`).

    .. warning:: Do NOT use seeking/telling classes inside TransformData context.

    :param subcon: Construct instance
    :param decodefunc: bytes-to-bytes function, applied before parsing subcon
    :param decodeamount: integer, amount of bytes to read
    :param encodefunc: bytes-to-bytes function, applied after building subcon
    :param encodeamount: integer, amount of bytes to write

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises StreamError: subcon parsed less than `decodeamount` bytes
    :raises StreamError: subcon build (and encoder transformed) more or less than `encodeamount` bytes
    :raises StringError: building from non-bytes value, perhaps unicode

    Can propagate any exception from the lambdas, possibly non-ConstructError.

    Example::

        >>> d = TransformData(Bytes(16), bytes2bits, 2, bits2bytes, 16//8)
        >>> d.parse(b"\x00\x00")
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    """

    def __init__(self, subcon, decodefunc, decodeamount, encodefunc, encodeamount):
        super(TransformData, self).__init__(subcon)
        self.decodefunc = decodefunc
        self.decodeamount = decodeamount
        self.encodefunc = encodefunc
        self.encodeamount = encodeamount

    def _parse(self, stream, context, path):
        data = self.decodefunc(_read_stream(stream, self.decodeamount))
        stream2 = io.BytesIO(data)
        obj = self.subcon._parsereport(stream2, context, path)
        if stream2.read(1):
            raise StreamError("decoding transformation did not consume all bytes")
        return obj

    def _build(self, obj, stream, context, path):
        stream2 = io.BytesIO()
        buildret = self.subcon._build(obj, stream2, context, path)
        data = self.encodefunc(stream2.getvalue())
        if len(data) != self.encodeamount:
            raise StreamError("encoding transformation produced wrong amount of bytes")
        _write_stream(stream, data)
        return buildret

    def _sizeof(self, context, path):
        return self.encodeamount


class Restreamed(Subconstruct):
    r"""
    Transforms bytes between the underlying stream and the subcon.

    Used internally to implement :class:`~construct.core.Bitwise` :class:`~construct.core.Bytewise` :class:`~construct.core.ByteSwapped` :class:`~construct.core.BitsSwapped` .

    .. warning:: Remember that subcon must consume or produce an amount of bytes that is a multiple of encoding or decoding units. For example, in a Bitwise context you should process a multiple of 8 bits or the stream will fail during parsing/building.

    .. warning:: Do NOT use seeking/telling classes inside Restreamed context.

    :param subcon: Construct instance, subcon which will operate on the buffer
    :param encoder: function that takes bytes and returns bytes (used when building)
    :param encoderunit: integer ratio, encoder takes that many bytes at once
    :param decoder: function that takes bytes and returns bytes (used when parsing)
    :param decoderunit: integer ratio, decoder takes that many bytes at once
    :param sizecomputer: function that computes amount of bytes outputed

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Can also raise arbitrary exceptions in its implementation.

    Example::

        Bitwise  <--> Restreamed(subcon, bits2bytes, 8, bytes2bits, 1, lambda n: n//8)
        Bytewise <--> Restreamed(subcon, bytes2bits, 1, bits2bytes, 8, lambda n: n*8)
    """

    def __init__(self, subcon, decoder, decoderunit, encoder, encoderunit, sizecomputer):
        super(Restreamed, self).__init__(subcon)
        self.decoder = decoder
        self.decoderunit = decoderunit
        self.encoder = encoder
        self.encoderunit = encoderunit
        self.sizecomputer = sizecomputer

    def _parse(self, stream, context, path):
        stream2 = RestreamedBytesIO(stream, self.decoder, self.decoderunit, self.encoder, self.encoderunit)
        obj = self.subcon._parsereport(stream2, context, path)
        stream2.close()
        return obj

    def _build(self, obj, stream, context, path):
        stream2 = RestreamedBytesIO(stream, self.decoder, self.decoderunit, self.encoder, self.encoderunit)
        buildret = self.subcon._build(obj, stream2, context, path)
        stream2.close()
        return obj

    def _sizeof(self, context, path):
        if self.sizecomputer is None:
            raise SizeofError("Restreamed cannot calculate size without a sizecomputer")
        else:
            return self.sizecomputer(self.subcon._sizeof(context, path))


class Checksum(Construct):
    r"""
    Field that is build or validated by a hash of a given byte range. Usually used with :class:`~construct.core.RawCopy` .

    Parsing compares parsed subcon `checksumfield` with a context entry provided by `bytesfunc` and transformed by `hashfunc`. Building fetches the contect entry, transforms it, then writes is using subcon. Size is same as subcon.

    :param checksumfield: a subcon field that reads the checksum, usually Bytes(int)
    :param hashfunc: function that takes bytes and returns whatever checksumfield takes when building, usually from hashlib module
    :param bytesfunc: context lambda that returns bytes (or object) to be hashed, usually like this.rawcopy1.data

    :raises ChecksumError: parsing and actual checksum does not match actual data

    Can propagate any exception from the lambdas, possibly non-ConstructError.

    Example::

        import hashlib
        d = Struct(
            "fields" / RawCopy(Struct(
                Padding(1000),
            )),
            "checksum" / Checksum(Bytes(64),
                lambda data: hashlib.sha512(data).digest(),
                this.fields.data),
        )
        d.build(dict(fields=dict(value={})))

    ::

        import hashlib
        d = Struct(
            "offset" / Tell,
            "checksum" / Padding(64),
            "fields" / RawCopy(Struct(
                Padding(1000),
            )),
            "checksum" / Pointer(this.offset, Checksum(Bytes(64),
                lambda data: hashlib.sha512(data).digest(),
                this.fields.data)),
        )
        d.build(dict(fields=dict(value={})))
    """

    def __init__(self, checksumfield, hashfunc, bytesfunc):
        super(Checksum, self).__init__()
        self.checksumfield = checksumfield
        self.hashfunc = hashfunc
        self.bytesfunc = bytesfunc
        self.flagbuildnone = True

    def _parse(self, stream, context, path):
        hash1 = self.checksumfield._parsereport(stream, context, path)
        hash2 = self.hashfunc(self.bytesfunc(context))
        if hash1 != hash2:
            raise ChecksumError("wrong checksum, read %r, computed %r" % (
                hash1 if not isinstance(hash1,bytestringtype) else binascii.hexlify(hash1),
                hash2 if not isinstance(hash2,bytestringtype) else binascii.hexlify(hash2), ))
        return hash1

    def _build(self, obj, stream, context, path):
        hash2 = self.hashfunc(self.bytesfunc(context))
        self.checksumfield._build(hash2, stream, context, path)
        return hash2

    def _sizeof(self, context, path):
        return self.checksumfield._sizeof(context, path)


class Compressed(Tunnel):
    r"""
    Compresses and decompresses underlying stream when processing subcon. When parsing, entire stream is consumed. When building, puts compressed bytes without marking the end. This construct should be used with :class:`~construct.core.Prefixed` .

    Parsing and building transforms all bytes using a specified codec. Since data is processed until EOF, it behaves similar to `GreedyBytes`. Size is undefined.

    :param subcon: Construct instance, subcon used for storing the value
    :param encoding: string, any of module names like zlib/gzip/bzip2/lzma, otherwise any of codecs module bytes<->bytes encodings, each codec usually requires some Python version
    :param level: optional, integer between 0..9, although lzma discards it, some encoders allow different compression levels

    :raises ImportError: needed module could not be imported by ctor
    :raises StreamError: stream failed when reading until EOF

    Example::

        >>> d = Prefixed(VarInt, Compressed(GreedyBytes, "zlib"))
        >>> d.build(bytes(100))
        b'\x0cx\x9cc`\xa0=\x00\x00\x00d\x00\x01'

   """

    def __init__(self, subcon, encoding, level=None):
        super(Compressed, self).__init__(subcon)
        self.encoding = encoding
        self.level = level
        if self.encoding == "zlib":
            import zlib
            self.lib = zlib
        elif self.encoding == "gzip":
            import gzip
            self.lib = gzip
        elif self.encoding == "bzip2":
            import bz2
            self.lib = bz2
        elif self.encoding == "lzma":
            import lzma
            self.lib = lzma
        else:
            import codecs
            self.lib = codecs

    def _decode(self, data, context, path):
        if self.encoding in ("zlib", "gzip", "bzip2", "lzma"):
            return self.lib.decompress(data)
        return self.lib.decode(data, self.encoding)

    def _encode(self, data, context, path):
        if self.encoding in ("zlib", "gzip", "bzip2", "lzma"):
            if self.level is None or self.encoding == "lzma":
                return self.lib.compress(data)
            else:
                return self.lib.compress(data, self.level)
        return self.lib.encode(data, self.encoding)


class Rebuffered(Subconstruct):
    r"""
    Caches bytes from underlying stream, so it becomes seekable and tellable, and also becomes blocking on reading. Useful for processing non-file streams like pipes, sockets, etc.

    .. warning:: Experimental implementation. May not be mature enough.

    :param subcon: Construct instance, subcon which will operate on the buffered stream
    :param tailcutoff: optional, integer, amount of bytes kept in buffer, by default buffers everything

    Can also raise arbitrary exceptions in its implementation.

    Example::

        Rebuffered(..., tailcutoff=1024).parse_stream(nonseekable_stream)
    """

    def __init__(self, subcon, tailcutoff=None):
        super(Rebuffered, self).__init__(subcon)
        self.stream2 = RebufferedBytesIO(None, tailcutoff=tailcutoff)

    def _parse(self, stream, context, path):
        self.stream2.substream = stream
        return self.subcon._parsereport(self.stream2, context, path)

    def _build(self, obj, stream, context, path):
        self.stream2.substream = stream
        return self.subcon._build(obj, self.stream2, context, path)


#===============================================================================
# lazy equivalents
#===============================================================================
class LazyContainer(dict):
    """Used internally."""

    def __init__(self, struct, stream, offsets, values, context, path):
        self._struct = struct
        self._stream = stream
        self._offsets = offsets
        self._values = values
        self._context = context
        self._path = path

    def __getattr__(self, name):
        if name in self._struct._subconsindexes:
            return self[name]
        raise AttributeError

    def __getitem__(self, index):
        if isinstance(index, stringtypes):
            index = self._struct._subconsindexes[index] # KeyError
        if index in self._values:
            return self._values[index]
        _seek_stream(self._stream, self._offsets[index]) # KeyError
        parseret = self._struct.subcons[index]._parsereport(self._stream, self._context, self._path)
        self._values[index] = parseret
        return parseret

    def __len__(self):
        return len(self._struct.subcons)

    def keys(self):
        return iter(self._struct._subcons)

    def values(self):
        return (self[k] for k in self._struct._subcons)

    def items(self):
        return ((k, self[k]) for k in self._struct._subcons)

    __iter__ = keys

    def __eq__(self, other):
        return Container.__eq__(self, other)

    def __repr__(self):
        return "<LazyContainer: %s items cached, %s subcons>" % (len(self._values), len(self._struct.subcons), )


class LazyStruct(Construct):
    r"""
    Equivalent to :class:`~construct.core.Struct`, but when this class is parsed, most fields are not parsed (they are skipped if their size can be measured by _actualsize or _sizeof method). See its docstring for details.

    Fields are parsed depending on some factors:

    * Some fields like Int* Float* Bytes(5) Array(5,Byte) Pointer are fixed-size and are therefore skipped. Stream is not read.
    * Some fields like Bytes(this.field) are variable-size but their size is known during parsing when there is a corresponding context entry. Those fields are also skipped. Stream is not read.
    * Some fields like Prefixed PrefixedArray PascalString are variable-size but their size can be computed by partially reading the stream. Only first few bytes are read (the lengthfield).
    * Other fields like VarInt need to be parsed. Stream position that is left after the field was parsed is used.
    * Some fields may not work properly, due to the fact that this class attempts to skip fields, and parses them only out of necessity. Miscellaneous fields often have size defined as 0, and fixed sized fields are skippable.

    Note there are restrictions:

    * If a field like Bytes(this.field) references another field in the same struct, you need to access the referenced field first (to trigger its parsing) and then you can access the Bytes field. Otherwise it would fail due to missing context entry.
    * If a field references another field within inner (nested) or outer (super) struct, things may break. Context is nested, but this class was not rigorously tested in that manner.

    Building and sizeof are greedy, like in Struct.

    :param \*subcons: Construct instances, list of members, some can be anonymous
    :param \*\*subconskw: Construct instances, list of members (requires Python 3.6)
    """

    def __init__(self, *subcons, **subconskw):
        super(LazyStruct, self).__init__()
        subcons = list(subcons) + list(k/v for k,v in subconskw.items())
        self.subcons = mergefields(*subcons)
        self._subcons = Container((sc.name,sc) for sc in self.subcons if sc.name)
        self._subconsindexes = Container((sc.name,i) for i,sc in enumerate(self.subcons) if sc.name)
        self.flagbuildnone = all(sc.flagbuildnone for sc in self.subcons)

    def __getattr__(self, name):
        if name in self._subcons:
            return self._subcons[name]
        raise AttributeError

    def _parse(self, stream, context, path):
        context = Container(_ = context)
        context._subcons = self._subcons
        offset = _tell_stream(stream)
        offsets = {0: offset}
        values = {}
        for i,sc in enumerate(self.subcons):
            try:
                offset += sc._actualsize(stream, context, path)
                _seek_stream(stream, offset)
            except SizeofError:
                parseret = sc._parsereport(stream, context, path)
                values[i] = parseret
                if sc.name:
                    context[sc.name] = parseret
                offset = _tell_stream(stream)
            offsets[i+1] = offset
        return LazyContainer(self, stream, offsets, values, context, path)

    def _build(self, obj, stream, context, path):
        # exact copy from Struct class
        if obj is None:
            obj = Container()
        context = Container(_ = context)
        context._subcons = self._subcons
        context.update(obj)
        for sc in self.subcons:
            try:
                if sc.flagbuildnone:
                    subobj = obj.get(sc.name, None)
                else:
                    subobj = obj[sc.name] # raises KeyError

                if sc.name:
                    context[sc.name] = subobj

                buildret = sc._build(subobj, stream, context, path)
                if sc.name:
                    context[sc.name] = buildret
            except StopFieldError:
                break
        return context

    def _sizeof(self, context, path):
        # exact copy from Struct class
        context = Container(_ = context)
        context._subcons = self._subcons
        try:
            return sum(sc._sizeof(context, path) for sc in self.subcons)
        except (KeyError, AttributeError):
            raise SizeofError("cannot calculate size, key not found in context")


class LazyListContainer(list):
    """Used internally."""

    def __init__(self, subcon, stream, count, offsets, values, context, path):
        self._subcon = subcon
        self._stream = stream
        self._count = count
        self._offsets = offsets
        self._values = values
        self._context = context
        self._path = path

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [self[i] for i in range(*index.indices(self._count))]
        if index in self._values:
            return self._values[index]
        _seek_stream(self._stream, self._offsets[index]) # KeyError
        parseret = self._subcon._parsereport(self._stream, self._context, self._path)
        self._values[index] = parseret
        return parseret

    def __getslice__(self, start, stop):
        if stop == sys.maxsize:
            stop = self._count
        return self.__getitem__(slice(start, stop))

    def __len__(self):
        return self._count

    def __iter__(self):
        return (self[i] for i in range(self._count))

    def __eq__(self, other):
        return len(self) == len(other) and all(self[i] == other[i] for i in range(self._count))

    def __repr__(self):
        return "<LazyListContainer: %s of %s items cached>" % (len(self._values), self._count, )


class LazyArray(Subconstruct):
    r"""
    Equivalent to :class:`~construct.core.Array`, but the subcon is not parsed when possible (it gets skipped if the size can be measured by _actualsize or _sizeof method). See its docstring for details.

    Fields are parsed depending on some factors:

    * Some fields like Int* Float* Bytes(5) Array(5,Byte) Pointer are fixed-size and are therefore skipped. Stream is not read.
    * Some fields like Bytes(this.field) are variable-size but their size is known during parsing when there is a corresponding context entry. Those fields are also skipped. Stream is not read.
    * Some fields like Prefixed PrefixedArray PascalString are variable-size but their size can be computed by partially reading the stream. Only first few bytes are read (the lengthfield).
    * Other fields like VarInt need to be parsed. Stream position that is left after the field was parsed is used.
    * Some fields may not work properly, due to the fact that this class attempts to skip fields, and parses them only out of necessity. Miscellaneous fields often have size defined as 0, and fixed sized fields are skippable.

    Note there are restrictions:

    * If a field references another field within inner (nested) or outer (super) struct, things may break. Context is nested, but this class was not rigorously tested in that manner.

    Building and sizeof are greedy, like in Array.

    :param count: integer or context lambda, strict amount of elements
    :param subcon: Construct instance, subcon to process individual elements
    """

    def __init__(self, count, subcon):
        super(LazyArray, self).__init__(subcon)
        self.count = count

    def _parse(self, stream, context, path):
        sc = self.subcon
        count = self.count
        if callable(count):
            count = count(context)
        if not 0 <= count:
            raise RangeError("invalid count %s" % (count,))
        offset = _tell_stream(stream)
        offsets = {0: offset}
        values = {}
        for i in range(count):
            try:
                offset += sc._actualsize(stream, context, path)
                _seek_stream(stream, offset)
            except SizeofError:
                parseret = sc._parsereport(stream, context, path)
                values[i] = parseret
                offset = _tell_stream(stream)
            offsets[i+1] = offset
        return LazyListContainer(sc, stream, count, offsets, values, context, path)

    def _build(self, obj, stream, context, path):
        # exact copy from Array class
        count = self.count
        if callable(count):
            count = count(context)
        if not 0 <= count:
            raise RangeError("invalid count %s" % (count,))
        if not len(obj) == count:
            raise RangeError("expected %d elements, found %d" % (count, len(obj)))
        retlist = ListContainer()
        for i,e in enumerate(obj):
            context._index = i
            buildret = self.subcon._build(e, stream, context, path)
            retlist.append(buildret)
        return retlist

    def _sizeof(self, context, path):
        # exact copy from Array class
        try:
            count = self.count
            if callable(count):
                count = count(context)
        except (KeyError, AttributeError):
            raise SizeofError("cannot calculate size, key not found in context")
        return count * self.subcon._sizeof(context, path)


class LazyBound(Construct):
    r"""
    Field that binds to the subcon only at runtime (during parsing and building, not ctor). Useful for recursive data structures, like linked-lists and trees, where a construct needs to refer to itself (while it does not exist yet in the namespace).

    Note that it is possible to obtain same effect without using this class, using a loop. However there are usecases where that is not possible (if remaining nodes cannot be sized-up, and there is data following the recursive structure). There is also a significant difference, namely that LazyBound actually does greedy parsing while the loop does lazy parsing. See examples.

    To break recursion, use `If` field. See examples.

    :param subconfunc: parameter-less lambda returning Construct instance, can also return itself

    Example::

        d = Struct(
            "value" / Byte,
            "next" / If(this.value > 0, LazyBound(lambda: d)),
        )
        >>> print(d.parse(b"\x05\x09\x00"))
        Container:
            value = 5
            next = Container:
                value = 9
                next = Container:
                    value = 0
                    next = None

    ::

        d = Struct(
            "value" / Byte,
            "next" / GreedyBytes,
        )
        data = b"\x05\x09\x00"
        while data:
            x = d.parse(data)
            data = x.next
            print(x)
        # print outputs
        Container:
            value = 5
            next = \t\x00 (total 2)
        # print outputs
        Container:
            value = 9
            next = \x00 (total 1)
        # print outputs
        Container:
            value = 0
            next =  (total 0)
    """

    def __init__(self, subconfunc):
        super(LazyBound, self).__init__()
        self.subconfunc = subconfunc

    def _parse(self, stream, context, path):
        sc = self.subconfunc()
        return sc._parsereport(stream, context, path)

    def _build(self, obj, stream, context, path):
        sc = self.subconfunc()
        return sc._build(obj, stream, context, path)


#===============================================================================
# adapters and validators
#===============================================================================
class ExprAdapter(Adapter):
    r"""
    Generic adapter that takes `decoder` and `encoder` lambdas as parameters. You can use ExprAdapter instead of writing a full-blown class deriving from Adapter when only a simple lambda is needed.

    :param subcon: Construct instance, subcon to adapt
    :param decoder: lambda that takes (obj, context) and returns an decoded version of obj
    :param encoder: lambda that takes (obj, context) and returns an encoded version of obj

    Example::

        >>> d = ExprAdapter(Byte, obj_+1, obj_-1)
        >>> d.parse(b'\x04')
        5
        >>> d.build(5)
        b'\x04'
    """
    def __init__(self, subcon, decoder, encoder):
        super(ExprAdapter, self).__init__(subcon)
        self._decode = lambda obj,ctx,path: decoder(obj,ctx)
        self._encode = lambda obj,ctx,path: encoder(obj,ctx)


class ExprSymmetricAdapter(ExprAdapter):
    """
    Macro around :class:`~construct.core.ExprAdapter`.

    :param subcon: Construct instance, subcon to adapt
    :param encoder: lambda that takes (obj, context) and returns both encoded version and decoded version of obj

    Example::

        >>> d = ExprSymmetricAdapter(Byte, obj_ & 0b00001111)
        >>> d.parse(b"\xff")
        15
        >>> d.build(255)
        b'\x0f'
    """
    def __init__(self, subcon, encoder):
        super(ExprAdapter, self).__init__(subcon)
        self._decode = lambda obj,ctx,path: encoder(obj,ctx)
        self._encode = lambda obj,ctx,path: encoder(obj,ctx)


class ExprValidator(Validator):
    r"""
    Generic adapter that takes `validator` lambda as parameter. You can use ExprValidator instead of writing a full-blown class deriving from Validator when only a simple lambda is needed.

    :param subcon: Construct instance, subcon to adapt
    :param validator: lambda that takes (obj, context) and returns a bool

    Example::

        >>> d = ExprValidator(Byte, obj_ & 0b11111110 == 0)
        >>> d.build(1)
        b'\x01'
        >>> d.build(88)
        ValidationError: object failed validation: 88

    """
    def __init__(self, subcon, validator):
        super(ExprValidator, self).__init__(subcon)
        self._validate = lambda obj,ctx,path: validator(obj,ctx)


def OneOf(subcon, valids):
    r"""
    Validates that the object is one of the listed values, both during parsing and building.

    .. note:: For performance, `valids` should be a set/frozenset.

    :param subcon: Construct instance, subcon to validate
    :param valids: collection implementing __contains__, usually a list or set

    :raises ValidationError: parsed or build value is not among valids

    Example::

        >>> d = OneOf(Byte, [1,2,3])
        >>> d.parse(b"\x01")
        1
        >>> d.parse(b"\xff")
        construct.core.ValidationError: object failed validation: 255
    """
    return ExprValidator(subcon, lambda obj,ctx: obj in valids)


def NoneOf(subcon, invalids):
    r"""
    Validates that the object is none of the listed values, both during parsing and building.

    .. note:: For performance, `valids` should be a set/frozenset.

    :param subcon: Construct instance, subcon to validate
    :param invalids: collection implementing __contains__, usually a list or set

    :raises ValidationError: parsed or build value is among invalids

    """
    return ExprValidator(subcon, lambda obj,ctx: obj not in invalids)


def Filter(predicate, subcon):
    r"""
    Filters a list leaving only the elements that passed through the predicate.

    :param subcon: Construct instance, usually Array GreedyRange Sequence
    :param predicate: lambda that takes (obj, context) and returns a bool

    Can propagate any exception from the lambda, possibly non-ConstructError.

    Example::

        >>> d = Filter(obj_ != 0, Byte[:])
        >>> d.parse(b"\x00\x02\x00")
        [2]
        >>> d.build([0,1,0,2,0])
        b'\x01\x02'
    """
    return ExprSymmetricAdapter(subcon, lambda obj,ctx: [x for x in obj if predicate(x,ctx)])


class Slicing(Adapter):
    r"""
    Adapter for slicing a list. Works with GreedyRange and Sequence.

    :param subcon: Construct instance, subcon to slice
    :param count: integer, expected number of elements, needed during building
    :param start: integer for start index (or None for entire list)
    :param stop: integer for stop index (or None for up-to-end)
    :param step: integer, step (or 1 for every element)
    :param empty: object, value to fill the list with, during building

    Example::

        d = Slicing(Array(4,Byte), 4, 1, 3, empty=0)
        assert d.parse(b"\x01\x02\x03\x04") == [2,3]
        assert d.build([2,3]) == b"\x00\x02\x03\x00"
        assert d.sizeof() == 4
    """
    def __init__(self, subcon, count, start, stop, step=1, empty=None):
        super(Slicing, self).__init__(subcon)
        self.count = count
        self.start = start
        self.stop = stop
        self.step = step
        self.empty = empty
    def _decode(self, obj, context, path):
        return obj[self.start:self.stop:self.step]
    def _encode(self, obj, context, path):
        if self.start is None:
            return obj
        elif self.stop is None:
            output = [self.empty] * self.count
            output[self.start::self.step] = obj
        else:
            output = [self.empty] * self.count
            output[self.start:self.stop:self.step] = obj
        return output


class Indexing(Adapter):
    r"""
    Adapter for indexing a list (getting a single item from that list). Works with Range and Sequence and their lazy equivalents.

    :param subcon: Construct instance, subcon to index
    :param count: integer, expected number of elements, needed during building
    :param index: integer, index of the list to get
    :param empty: object, value to fill the list with, during building

    Example::

        d = Indexing(Array(4,Byte), 4, 2, empty=0)
        assert d.parse(b"\x01\x02\x03\x04") == 3
        assert d.build(3) == b"\x00\x00\x03\x00"
        assert d.sizeof() == 4
    """
    def __init__(self, subcon, count, index, empty=None):
        super(Indexing, self).__init__(subcon)
        self.count = count
        self.index = index
        self.empty = empty
    def _decode(self, obj, context, path):
        return obj[self.index]
    def _encode(self, obj, context, path):
        output = [self.empty] * self.count
        output[self.index] = obj
        return output


#===============================================================================
# end of file
#===============================================================================
