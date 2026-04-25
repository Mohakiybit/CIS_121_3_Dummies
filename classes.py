import random

class Move:
    def __init__(self, name, effect, delivery, modifier, cost):
        self.name = name
        self.effect = effect
        self.delivery = delivery
        self.modifier = modifier
        self.mana_cost = cost

class Player:
    def __init__(self, name):
        self.name = name
        self.moves = [] #Holds custom moves of Player
        self.strength_stat = random.randint(5,10)
        self.max_health = random.randint(80,120)
        self.health_points = self.max_health
        self.max_mana = random.randint(50,90)
        self.mana_points = self.max_mana

    def restore(self):
        self.health_points = min(self.max_health, self.health_points + random.randint(20,50))
        self.mana_points = min(self.max_mana, self.mana_points + random.randint(20,40))
        print("You restored some HP and Mana!")
    def show_status(self):
        print(f"\n--- {self.name} ---")
        print(f"HP: {self.health_points}/{self.max_health} | Mana: {self.mana_points} / {self.max_mana}")

class Enemy:
    def __init__(self, name, health, strength):
        self.name = name
        self.health_points = health
        self.strength_stat = strength

    def is_alive(self):
        return self.health_points > 0