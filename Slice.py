# A class of each slices
class Slice:
    def __init__(self, pk, name, connected_users, user_share,
                capacity, usage_pattern):
        # please refer to making instance of each base stations in main.py
        self.pk = pk
        self.name = name
        self.connected_users = connected_users
        self.user_share = user_share
        self.capacity = capacity
        self.usage_pattern = usage_pattern
        self.level = 0

    def __str__(self):
        return f'{self.name:<10}'