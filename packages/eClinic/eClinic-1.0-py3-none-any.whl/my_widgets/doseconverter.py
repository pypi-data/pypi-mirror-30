import re

class Converter:
    def __init__(self, number):
        self.number = number
        self.digit=None
        self.unit=None
        self.allowed_units=['kg','g','mg','mcg','ng','pg','ml']

        self.pg  = 0.000000001
        self.ng  = 0.000001
        self.mcg = 0.001
        self.mg  = 1 # Taken as a standard unit
        self.g   = 1000
        self.kg  = 1000000
        self.ml  = 1 # Mils should not be converted, >>unity

        self.compile()

    @property
    def units(self):
        return self.unit

    @property
    def value(self):
        return self.digit

    def compile(self):
        if self.number is None:
            self.digit=None
            self.unit = None
            return

        digit_regex = re.compile(r"\d+")
        float_regex = re.compile(r"\d+[.]\d+")
        units_regex = re.compile(r'((mg)|(mcg)|(pg)|(kg)|(ng)|(g)|(ml))', re.IGNORECASE)

        digit = digit_regex.search (self.number)
        double= float_regex.search(self.number)
        unit= units_regex.search(self.number)

        if double and unit:
            self.digit=double.group()
            self.unit=unit.group().lower()
        elif digit and unit:
            self.digit=digit.group()
            self.unit=unit.group().lower()
        else:
            self.digit=None
            self.unit = None

    def to_mg(self, number):
        if number.units is not None:
            unit= getattr(self, number.units)
            n = float(number.value) * float(unit)
            return n

    def __truediv__(self, other):
        numerator= self.to_mg(self)
        denominator= self.to_mg(other)
        if numerator and denominator:
            return round(numerator/denominator,2)


if __name__ == '__main__':
    formulation = Converter("500mg") # Formulation 10* 1000
    dose = Converter("200mg")  # Dose
    quantity= dose/formulation
    print(quantity)
