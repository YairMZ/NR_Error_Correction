class Foo:
    def __init__(self, a):
        self.a = a

    def __repr__(self):
        return str(a)


b = Foo(1)
print(b)
