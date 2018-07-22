class FrameVar(KspNativeArray):

    def __init__(self, name, val, length=None,
                 start_idx=None):
        self._name = name
        self.name = self._name_func
        self.val = val
        if length:
            self.len = length
        else:
            try:
                self.len = len(val)
            except TypeError:
                self.len = 1
        self._start_idx = start_idx
        if start_idx is not None:
            assert isinstance(val, StackArray), \
                f'Expected {StackArray} or not start_idx'
            self.seq = self.val
        if self.len == 1:
            if start_idx is not None:
                self.ref_type = ref_type_from_input(self.val[0])
            else:
                self.ref_type = ref_type_from_input(self.val)
        else:
            self.ref_type = ref_type_from_input(self.val[0])
        self._iterated = False

    def value_get(self):
        if KSP.is_under_test():
            if self._start_idx is not None:
                if self.len == 1:
                    return self.val[self._start_idx]
                return [self.val[i]for i in
                        range(self._start_idx,
                              self._start_idx + self.len)]
            if isinstance(self.val, FrameVar):
                return self.val.val
            return self.val
        if self.len > 1:
            raise TypeError("can't return array on compilation")
        if self._start_idx is not None:
            return self.val[self._start_idx]
        return self.val

    def value_set(self, other):
        if not KSP.is_under_test():
            return
        if self.len == 1:
            if self._start_idx is not None:
                self.val[self._start_idx] = other
                return
            self.val.value_set(other)
            return
        raise TypeError('can not assign to array. use For()')

    def _name_func(self):
        '''intuition tells something wrong here'''
        if self._start_idx is not None:
            if self.len == 1:
                return f'{self.val.name()}[' +\
                    f'{expand_if_callable(self._start_idx)}]'
            return self.val.name()
        return self.val()

    def __call__(self, value=None):
        print(f'{self.name()}.__call__({self}, {value})')
        if value:
            assert self.len == 1, \
                "can't assign value to array. " +\
                "Use '<var>[idx] = val' instead"
            if self._start_idx is not None:
                self.val[self._start_idx] = value
                return
            if isinstance(self.val, KspNative):
                if KSP.is_under_test():
                    value = expand_if_callable(value)
                    if isinstance(self.val, (str, kStr)):
                        value = str(value)
                    return self.val(value)
                self.val(value)
            IOutput.put(AstAsgn(self.val, value)())
            return
        if self.len > 1:
            assert not self._start_idx, \
                f"can't call {StackArray}. This ahoudn't has happend."
        if self._start_idx is not None:
            return self.val[self._start_idx]
        return expand_if_callable(self.val)

    def __getitem__(self, idx):
        if self.len == 1:
            raise TypeError("is not sequence")
        if self._start_idx:
            idx = self.__check_idx(idx)
            # idx = idx
        return self.val[idx]

    def __setitem__(self, idx, value):
        if self.len == 1:
            raise TypeError("is not sequence")
        if self._start_idx:
            idx = self.__check_idx(idx)
        self.val[idx] = value

    def __iter__(self):
        idx = self._start_idx
        length = self.len
        seq = self.val[idx:idx + length]
        return iter(seq)

    def __check_idx(self, idx):
        if not KSP.is_under_test() and isinstance(idx, KspNative):
            return self._start_idx + idx
        if idx >= self.len:
            raise IndexError(f'invalid index {idx}')
        if isinstance(idx, AstMethod):
            return AstAdd(self._start_idx, idx)
        return self._start_idx + idx

    def __len__(self):
        return self.len
