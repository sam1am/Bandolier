class Character:
    def __init__(self, hit_points, attack_power, defense):
        self.hit_points = hit_points
        self.attack_power = attack_power
        self.defense = defense

    def attack(self, other):
        if not self.is_alive():
            print(f'{self} is no longer alive and cannot attack.')
            return
        damage = self.attack_power - other.defense
        if damage > 0:
            other.receive_damage(damage)

    def receive_damage(self, damage):
        self.hit_points -= damage

    def is_alive(self):
        return self.hit_points > 0


class Player(Character):
    def __init__(self, hit_points, attack_power, defense, experience=0, level=1):
        super().__init__(hit_points, attack_power, defense)
        self.experience = experience
        self.level = level

    def gain_experience(self, amount):
        self.experience += amount
        if self.experience >= self.level * 100:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.hit_points += 10
        self.attack_power += 2
        self.defense += 2
        self.experience = 0


class Enemy(Character):
    def __init__(self, hit_points, attack_power, defense, reward_experience):
        super().__init__(hit_points, attack_power, defense)
        self.reward_experience = reward_experience
