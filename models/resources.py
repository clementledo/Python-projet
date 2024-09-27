class Resource:
    def __init__(self, resource_type, amount):
        self.resource_type = resource_type  # ex: bois, or
        self.amount = amount  # Quantité de ressources

    def collect(self, amount):
        if amount <= self.amount:
            self.amount -= amount
        else:
            print("Pas assez de ressources")
