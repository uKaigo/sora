class json:
    """Use essa classe como se fosse o json do javascript."""
    def __getitem__(self, value):
        try:
            attr = getattr(self, value)
        except AttributeError:
            raise KeyError(value)
        else:
            return attr

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __delitem__(self, key):
        delattr(self, key)