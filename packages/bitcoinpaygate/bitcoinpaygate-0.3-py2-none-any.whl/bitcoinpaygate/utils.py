def property_not_empty(p):
    def check(self, value):
        if value:
            p(self, value)
        else:
            raise ValueError('The property %s cannot be empty string or null.' % p.__name__)
    return check