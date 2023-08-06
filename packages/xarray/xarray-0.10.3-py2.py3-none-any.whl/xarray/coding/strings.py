

class UnsignedIntegerCoder(VariableCoder):

    def encode(self, variable, name=None):
        dims, data, attrs, encoding = unpack_for_encoding(variable)

        if encoding.get('_Unsigned', False):
            pop_to(encoding, attrs, '_Unsigned')
            signed_dtype = np.dtype('i%s' % data.dtype.itemsize)
            if '_FillValue' in attrs:
                new_fill = signed_dtype.type(attrs['_FillValue'])
                attrs['_FillValue'] = new_fill
            data = duck_array_ops.around(data).astype(signed_dtype)

        return Variable(dims, data, attrs, encoding)

    def decode(self, variable, name=None):
        dims, data, attrs, encoding = unpack_for_decoding(variable)

        if '_Unsigned' in attrs:
            unsigned = pop_to(attrs, encoding, '_Unsigned')

            if data.dtype.kind == 'i':
                if unsigned:
                    unsigned_dtype = np.dtype('u%s' % data.dtype.itemsize)
                    transform = partial(np.asarray, dtype=unsigned_dtype)
                    data = lazy_elemwise_func(data, transform, unsigned_dtype)
                    if '_FillValue' in attrs:
                        new_fill = unsigned_dtype.type(attrs['_FillValue'])
                        attrs['_FillValue'] = new_fill
            else:
                warnings.warn("variable %r has _Unsigned attribute but is not "
                              "of integer type. Ignoring attribute." % name,
                              SerializationWarning, stacklevel=3)

        return Variable(dims, data, attrs, encoding)



class StackedBytesArray(indexing.ExplicitlyIndexedNDArrayMixin):
    """Wrapper around array-like objects to create a new indexable object where
    values, when accessed, are automatically stacked along the last dimension.

    >>> StackedBytesArray(np.array(['a', 'b', 'c']))[:]
    array('abc',
          dtype='|S3')
    """

    def __init__(self, array):
        """
        Parameters
        ----------
        array : array-like
            Original array of values to wrap.
        """
        if array.dtype != 'S1':
            raise ValueError(
                "can only use StackedBytesArray if argument has dtype='S1'")
        self.array = indexing.as_indexable(array)

    @property
    def dtype(self):
        return np.dtype('S' + str(self.array.shape[-1]))

    @property
    def shape(self):
        return self.array.shape[:-1]

    def __str__(self):
        # TODO(shoyer): figure out why we need this special case?
        if self.ndim == 0:
            return str(np.array(self).item())
        else:
            return repr(self)

    def __repr__(self):
        return ('%s(%r)' % (type(self).__name__, self.array))

    def __getitem__(self, key):
        # require slicing the last dimension completely
        key = type(key)(indexing.expanded_indexer(key.tuple, self.array.ndim))
        if key.tuple[-1] != slice(None):
            raise IndexError('too many indices')
        return char_to_bytes(self.array[key])
