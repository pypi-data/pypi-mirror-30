import json

def _addindent(s_, numSpaces):
    '''
    From pytorch implementation
    :param s_: the string
    :param numSpaces: number of spaces for indentation
    :return:
    '''
    s = s_.split('\n')
    if len(s) == 1:
        return s_
    s = [(numSpaces * ' ') + line for line in s]
    s = '\n'.join(s)
    return s

class Hparam():

    @staticmethod
    def sum(seqs):
        assert len(seqs) != 0, "the sequence length can not be 0"
        res = None
        for seq in seqs:
            assert isinstance(seq, Hparam), "the sequence must consist of hparam objects"
            res = seq if res is None else seq + res
        return res

    @staticmethod
    def mean(seqs):
        return Hparam.sum(seqs) / len(seqs)


    def __init__(self, **kwargs):
        '''
        Update all the hparams into its attributes
        :param kwargs:
        '''
        self.__dict__.update(**kwargs)
        self.unroll()  # unroll all the dictionaries

    def __setitem__(self, key, value):
        self.__dict__[str(key)] = value

    def __setattr__(self, key, value):
        self.__dict__[str(key)] = value

    def __getitem__(self, item):
        if not item in self.__dict__:
            return None
        return self.__dict__[item]

    def __radd__(self, other): return self.__add__(other)
    def __iadd__(self, other): return self.__add__(other)
    def __rmul__(self, other): return self.__mul__(other)
    def __imul__(self, other): return self.__mul__(other)
    def __rfloordiv__(self, other): return self.__floordiv__(other)
    def __ifloordiv__(self, other): return self.__floordiv__(other)
    def __rtruediv__(self, other): return self.__truediv__(other)
    def __itruediv__(self, other): return self.__truediv__(other)
    def __rsub__(self, other): return self.__sub__(other)
    def __isub__(self, other): return self.__sub__(other)

    def __add__(self, other):
        return self.generic_operation(other, '__add__')
    def __mul__(self, other):
        return self.generic_operation(other, '__mul__')
    def __floordiv__(self, other):
        return self.generic_operation(other, '__floordiv__')
    def __truediv__(self, other):
        return self.generic_operation(other, '__truediv__')
    def __sub__(self, other):
        return self.generic_operation(other, '__sub__')

    def generic_operation(self, other, op):
        copy = self.copy()
        if hasattr(other, "__dict__"):
            self.assert_similar_to(other)
            for key in self.__dict__:
                copy.__dict__[key] = getattr(copy.__dict__[key], op)(other.__dict__[key])
        else: # try broadcasting
            for key in self.__dict__:
                copy.__dict__[key] = getattr(copy.__dict__[key], op)(other)
        return copy

    def __str__(self):
        tmpstr = "Hparam: ("
        leading_n = 2
        tmpstr += '\n'
        for key in self.__dict__:
            hparam = self.__dict__[key]
            if isinstance(hparam, Hparam):
                tmpstr += '\n'.join([" " * leading_n + "." + key + s.lstrip()
                                     for s in hparam.__str__().split('\n')][1:-1])
            else:
                tmpstr += " " * leading_n + "." + key + " = " + str(hparam)
            tmpstr += "\n"
        return tmpstr + ")"

    def __repr__(self):
        leadingstr = "Hparam: (\n"
        leading_n = len(leadingstr)
        tmpstr = ""
        for key in self.__dict__:
            hparam = self.__dict__[key]
            tmpstr += key + ": "
            if isinstance(hparam, Hparam):
                tmpstr += '(\n'
                tmpstr += hparam.__repr__()[leading_n:-2]
                tmpstr += '\n)'
            else:
                tmpstr += str(hparam)
            tmpstr += '\n'
        if len(tmpstr) != 0:
            tmpstr = _addindent(tmpstr[:-1], 2)
        return leadingstr + tmpstr + "\n)"

    def assert_similar_to(self, other):
        sym_diff = set(self.__dict__) ^ set(other.__dict__)
        assert len(sym_diff) == 0, "key error, hparam differ by {}".format(sym_diff)

    def copy(self):
        return Hparam(**self.to_dict())

    def unroll(self):
        '''
        Internal function for automatically unrolling the dictionary to hparams
        :return:
        '''
        for key in self.__dict__:
            if type(self.__dict__[key]) is dict:
                self.__dict__[key] = Hparam(**self.__dict__[key])

    def apply(self, fn):
        for key in self.__dict__:
            if isinstance(self.__dict__[key], Hparam):
                self.__dict__[key].apply(fn)
            else:
                self.__dict__[key] = fn(self.__dict__[key])

    def sync_with(self, target_hparam):
        '''
        Syncronize itself with the target hyperparameter
        :param target_hparam:
        :return:
        '''
        assert isinstance(target_hparam, Hparam)
        self.__dict__ = target_hparam.to_dict()

    def add_hparam(self, field, value):
        '''
        Add hparam to the current object
        :param field:
        :param value:
        :return:
        '''
        self.__dict__[str(field)] = value

    def to_dict(self):
        '''
        Represent the hyperparameter in a dictionary (with no Hparam object)
        :return:
        '''
        res_dict = {}
        for key in self.__dict__:
            if isinstance(self.__dict__[key], Hparam):
                res_dict[key] = self.__dict__[key].to_dict()
            else:
                res_dict[key] = self.__dict__[key]
        return res_dict

    def restore(self, fname):
        '''
        Restore the hparam from a file
        :param fname:
        :return:
        '''
        assert fname.split('.')[-1] == "json", "only json format is supported for now"
        dict = json.load(open(fname))
        self.__dict__ = dict
        self.unroll()
        return self

    def save(self, fname):
        '''
        Save the hparam to a file
        :param fname:
        :return:
        '''
        assert fname.split('.')[-1] == "json", "only json format is supported for now"
        json.dump(self.to_dict(), open(fname, 'w'), indent=4, sort_keys=True)
