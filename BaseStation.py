import logging

logger = logging.getLogger('main.' + __name__)

# A class of each base stations
class BaseStation:
    def __init__(self, pk, x, y, coverage, b_id, b_type, Wa, Wb, access_slices, backhaul_slices, data_dir):
        # please refer to making instance of each base stations in main.py
        self.pk = pk
        self.x = x
        self.y = y
        self.coverage = coverage
        self.b_id = b_id
        self.b_type = b_type
        self.Wa = Wa
        self.Wb = Wb
        self.access_slices = access_slices
        self.backhaul_slices = backhaul_slices
        logger.info(f"{self}")

    def __str__(self):
        return f'BS_{self.pk:<2}(id={self.b_id},type={self.b_type})'
