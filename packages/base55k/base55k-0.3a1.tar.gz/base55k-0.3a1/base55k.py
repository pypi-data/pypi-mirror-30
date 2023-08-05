#!python3

import functools

class Base:
    """
    Base object used for storing value and extracting with \"get_base\" method,
    \"get_decimal\" method, or \"swap_value\" (returns the converted value of what
     was passed into __init__)
    """
    def __init__(self, number=0):
        if type(number) in (str, int):
            self.numType = type(number)
        else:
            raise TypeError("Base(number) must be of type %s or %s" %(str(str), str(int)) )
        self.number = number
        self.base = 55296

    def toBase55k(self, decimal):
        ret_arr = []
        while True:
            remainder = decimal % self.base
            decimal //= self.base
            ret_arr.append(chr(remainder))
            if not decimal:
                break
        return "".join(ret_arr[::-1])

    def toDecimal(self, base32k):
        base32k = list(base32k)[::-1]
        ret_arr = []
        for char in range(len(base32k)):
            ret_arr.append(ord(base32k[char])*(self.base**char))
        return functools.reduce((lambda x, y : x+y), ret_arr)

    def update(self, number):
        if type(number) in (str, int):
            self.numType = type(number)
        else:
            raise TypeError("Base(number) must be of type %s or %s" %(str(str), str(int)) )
        self.number = number

    def to_base(self):
        self.number = self.toBase55k(self.number)
        self.numType = type(self.number)

    def to_decimal(self):
        self.number = self.toDecimal(self.number)
        self.numType = type(self.number)

    def swap_value(self):
        if self.numType == int:
            self.number = self.toBase55k(self.number)

        elif self.numType == str:
            self.number = self.toDecimal(self.number)

    def get_base(self):
        if self.numType == int:
            return self.toBase55k(self.number)
        else:
            return self.number

    def get_decimal(self):
        if self.numType == str:
            return self.toDecimal(self.number)
        else:
            return self.number

    def get_type(self):
        if self.numType == str:
            return str, "base"
        elif self.numType == int:
            return int, "decimal"

    def is_base(self):
        return self.numType == str

    def is_decimal(self):
        return self.numType == int

def Main():
    import sys

    if len(sys.argv) <= 1:
        sys.exit()

    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-i", "--integer", action="store", type=int, help="An integer to convert to a base 55k")
    parser.add_argument("-b", "--base", action="store", type=str, help="A basse55k string to convert to an integer")
    args = parser.parse_args()

    if args.integer and args.base:
        raise Exception("Can't use both integer and base.")

    if args.integer:
        base_obj = Base(args.integer)
        print(base_obj.get_base())

    if args.base:
        base_obj = Base(args.base)
        print(base_obj.get_decimal())

if __name__ == '__main__':
    Main()
