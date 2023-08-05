
def slotted_getstate(self):
    visited = {None}  # set
    state = {}

    if hasattr(self, '__dict__'):
        state.update(self.__dict__)

    for cls in reversed(self.__class__.__mro__):
        slots = getattr(cls, '__slots__', None)

        if slots in visited:
            continue

        for attr_name in slots:
            if attr_name.startswith('__'):
                attr_name = '_{}{}'.format(cls.__name__, attr_name)

                while attr_name.startswith('__'):
                        attr_name = attr_name[1:]

            if hasattr(self, attr_name):
                state[attr_name] = getattr(self, attr_name)

    return state


def slotted_setstate(self, state):
    for attr_name, val in state.items():
        setattr(self, attr_name, val)


def pickle_slotted(cls):
    cls.__getstate__ = slotted_getstate
    cls.__setstate__ = slotted_setstate
    return cls


def infect_ruamel():
    from ruamel.yaml import tokens, error
    pickle_slotted(tokens.Token)
    pickle_slotted(error.StreamMark)


infect_ruamel()

