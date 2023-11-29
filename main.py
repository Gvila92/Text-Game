import os
import random
from PIL import Image
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Session

img = Image.open('Map.png')
img.show()

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    health = Column(Integer, default=100)
    inventory = relationship('InventoryItem', back_populates='player')

    def display_info(self):
        print(f"Player: {self.name} \nHealth: {self.health}")

    def attack(self):
        return random.randint(1, 20)

    def take_damage(self, damage):
        self.health -= damage

class InventoryItem(Base):
    __tablename__ = 'inventory_items'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'))
    player = relationship('Player', back_populates='inventory')

def initialize_database():
    engine = create_engine('sqlite:///game.db')
    Base.metadata.create_all(engine)
    return Session(engine)

def main_menu():
    print("\t\tMain Menu\n\n1. New Adventure\n2. Exit")
    choice = input("Enter your choice: ")
    return choice

def prompt():
    print("\t\tWelcome to my game\n\n\
You must collect all six items before fighting the boss.\n\n\
Moves:\t'go {direction}' (travel north, south, east, or west)\n\
\t'get {item}' (add nearby item to inventory)\n")

    input("Press any key to continue...")

def new_adventure(session):
    print("You have awoken! You hear in the far distance. Feeling disoriented, you stand and notice a small light approaching you.")
    input("You feel calm. Suddenly you hear a voice in your head: 'What is your name?'\nPress any key to continue...")

    player_name = input("Enter your character's name: ")
    player = Player(name=player_name)
    session.add(player)
    session.commit()

    player.display_info()
    print("To gain your freedom, you must traverse the world and collect all six items before fighting the boss.")
    input("Press any key to continue...")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

rooms = {
    'Liminal Space': {'North': 'Mirror Maze', 'South': 'Bat Cavern', 'East': 'Bazaar'},
    'Mirror Maze': {'South': 'Liminal Space', 'Item': 'Crystal'},
    'Bat Cavern': {'North': 'Liminal Space', 'East': 'Volcano', 'Item': 'Staff'},
    'Bazaar': {'West': 'Liminal Space', 'North': 'Meat Locker', 'East': 'Dojo', 'Item': 'Altoids'},
    'Meat Locker': {'South': 'Bazaar', 'East': 'Quicksand Pit', 'Item': 'Fig'},
    'Quicksand Pit': {'West': 'Meat Locker', 'Item': 'Robe'},
    'Volcano': {'West': 'Bat Cavern', 'Item': 'Elderberry'},
    'Dojo': {'West': 'Bazaar', 'Boss': 'Shadow Man'}
}

def main():
    session = initialize_database()

    while True:
        clear()
        choice = main_menu()

        if choice == '1':
            clear()
            new_adventure(session)

            current_room = "Liminal Space"
            msg = ""

            while True:
                clear()
                print(f"You are in the {current_room}\n{'-' * 27}")

                player = session.query(Player).first()
                player.display_info()

                print(msg)

                if "Item" in rooms[current_room].keys():
                    nearby_item = rooms[current_room]["Item"]
                    if nearby_item not in [inventory_item.name for inventory_item in player.inventory]:
                        if nearby_item[-1] == 's':
                            print(f"You see {nearby_item}")
                        elif nearby_item[0] in ['a', 'e', 'i', 'o', 'u']:
                            print(f"You see an {nearby_item}")
                        else:
                            print(f"You see a {nearby_item}")

                if "Boss" in rooms[current_room].keys():
                    if len(player.inventory) < 6:
                        print(f"You lost a fight with {rooms[current_room]['Boss']}.")
                        break
                    else:
                        print(f"You beat {rooms[current_room]['Boss']}!")
                        break

                if random.randint(1, 10) <= 3:
                    enemy_types = ['Goblin', 'Orc', 'Skeleton', 'Zombie']
                    enemy = random.choice(enemy_types)
                    print(f"OH no! {enemy} appeared!")
                    input("Press any key to roll the dice...")

                    while True:
                        player_roll = player.attack()
                        enemy_roll = random.randint(1, 20)  

                        print(f"{player.name} rolls {player_roll}. {enemy} rolls {enemy_roll}.")

                        if player_roll > enemy_roll:
                            print(f"You defeated {enemy}!")
                            break
                        else:
                            damage = random.randint(1, 10)  
                            player.take_damage(damage)
                            print(f"{enemy} deals {damage} damage. Your health: {player.health}")

                            if player.health <= 0:
                                print("You have been defeated. Game over.")
                                exit()

                            input("Press any key to roll the dice again...")

                user_input = input("Enter your move:\n")

                next_move = user_input.split(' ')
                action = next_move[0].title()
                item = "Item"
                direction = "null"

                if len(next_move) > 1:
                    item = next_move[1:]
                    direction = next_move[1].title()
                    item = " ".join(item).title()

                if action == "Go":
                    try:
                        current_room = rooms[current_room][direction]
                        msg = f"You travel {direction}"
                    except:
                        msg = "You can't go that way."

                elif action == "Get":
                    try:
                        if item == rooms[current_room]["Item"]:
                            if item not in [inventory_item.name for inventory_item in player.inventory]:
                                inventory_item = InventoryItem(name=rooms[current_room]["Item"])
                                player.inventory.append(inventory_item)
                                session.commit()
                                msg = f"{item} retrieved!"
                            else:
                                msg = f"You already have the {item}"
                        else:
                            msg = f"Can't find {item}"
                    except:
                        msg = f"Can't find {item}"

                elif action == "Exit":
                    break

                else:
                    msg = "Invalid command"

        elif choice == '2':
            print("Exiting the game. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter '1' for New Adventure or '2' to Exit.")
            input("Press any key to continue...")

if __name__ == "__main__":
    main()

