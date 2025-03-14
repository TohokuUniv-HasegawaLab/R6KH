# A class utilized when import scinario from setting file
class Distributor:
    def __init__(self, name, distribution, *dist_params, divide_scale=1):
        self.name = name
        self.distribution = distribution
        self.dist_params = dist_params
        self.divide_scale = divide_scale

    def generate(self):
        return self.distribution(*self.dist_params)

    def __str__(self):
        return f'[{self.name}: {self.distribution.__name__}: {self.dist_params}]'