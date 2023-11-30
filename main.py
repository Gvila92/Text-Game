import os
import random
from PIL import Image
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Session
import time
import imageio


img = Image.open('Map.png')
img.show()

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    health = Column(Integer, default=100)
    inventory = relationship('InventoryItem', back_populates='player')
    
    def __init__(self, name, health=100):
        self.name = name
        self.health = health
        self.inventory = []

    def display_info(self):
        inventory_names = [item.name for item in self.inventory]
        inventory_str = ', '.join(inventory_names)
        print(f"Player: {self.name}\nInventory: [{inventory_str}]\nHealth: {self.health}")

    def attack(self):
        return random.randint(1, 20)

    def take_damage(self, damage):
        if self.health is None:
            self.health = 0
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

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
#MAIN MENU
def convert_frame_to_ascii(frame):
    
    frame = frame.convert('L')

    # Resize the frame 
    width, height = frame.size
    aspect_ratio = height / float(width)
    new_width = 30  # Adjust the width as needed
    new_height = int(aspect_ratio * new_width)
    resized_frame = frame.resize((new_width, new_height))

    # Define ASCII characters from dark to light
    ascii_chars = "@%#*+=-:. "

    ascii_frame = ""
    for pixel_value in resized_frame.getdata():
        index = min(pixel_value * len(ascii_chars) // 256, len(ascii_chars) - 1)
        ascii_frame += ascii_chars[index]

    # Reshape ASCII characters to match the resized frame
    ascii_frame = "\n".join([ascii_frame[i:i+new_width] for i in range(0, len(ascii_frame), new_width)])

    return ascii_frame


# Path to your animated GIF
gif_path = "Skull gif.gif"



# Read the GIF frames
gif_frames = imageio.get_reader(gif_path)

# Display each frame of the animated GIF as ASCII art
try:
    for frame_number, frame_data in enumerate(gif_frames):
        clear()
        frame = Image.fromarray(frame_data)
        ascii_frame = convert_frame_to_ascii(frame)
        print(ascii_frame)
        time.sleep(0.1)  
except KeyboardInterrupt:
    pass

TITLE_SCREEN_FRAME = """
*********************************
* _____ _           _           *
*| ____| |_   _ ___(_)_   _____ *
*|  _| | | | | / __| \ \ / / _ \*
*| |___| | |_| \__ \ |\ V /  __/*
*|_____|_|\__,_|___/_| \_/ \___|*
*********************************
"""



# static title screen

def main_menu():
    print(TITLE_SCREEN_FRAME)  
    print("1. New Adventure\n2. Exit")
    choice = input("Enter your choice: ")
    return choice

def prompt():
    print("\t\tElusive\n\n\
You must collect all six items before fighting the boss.\n\n\
Moves:\t'go {direction}' (travel north, south, east, or west)\n\
\t'get {item}' (add nearby item to inventory)\n")

    input("Press Enter to continue..")
    
    

def new_adventure(session, current_room):
    print("You have awoken! You hear in the far distance. Feeling disoriented, you stand and notice a small light approaching you.")
    input("You feel calm. Suddenly you hear a voice in your head: 'What is your name?'\nPress ENTER to continue...")

    player_name = input("Enter your character's name: ")
    player = Player(name=player_name)

    player.display_info()
    print("To gain your freedom, you must traverse the world and collect all six items before fighting the boss.")
    input("Press Enter to continue..")

   
    player.inventory = []

    
    session.query(InventoryItem).delete()
    session.commit()

    while True:
        clear()
        print(f"You are in the {current_room}\n{'-' * 27}")

        player.display_info()

        msg = ""

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
                if current_room == 'Dojo':
                    print("You have not retrieved all six items and therefore are not worthy! DIE")
                    input("Press enter to return to the Main Menu...")
                    break  
                else:
                    break
            else:
                print(f"You beat {rooms[current_room]['Boss']}!")
                if current_room == 'Dojo':
                    print("Congratulations! You have defeated The shadow man and have gained your freedom for now.")
                    input("Press enter to exit the game...")
                    exit()  
                break

        if random.randint(1, 10) <= 3:
            enemy_types = ['Goblin', 'Orc', 'Skeleton', 'Zombie']
            enemy = random.choice(enemy_types)
            print(f"OH no! a  {enemy} appeared!")
            input("Press enter to roll the dice...")

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
                        input("Press enter to return to the Main Menu...")
                        exit()

                    input("Press enter to roll the dice again...")

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



rooms = {
    'Liminal Space': {'North': 'Mirror Maze', 'South': 'Bat Cavern', 'East': 'Bazaar'},
    'Mirror Maze': {'South': 'Liminal Space', 'Item': 'Crystal'},
    'Bat Cavern': {'North': 'Liminal Space', 'East': 'Volcano', 'Item': 'Staff'},
    'Bazaar': {'West': 'Liminal Space', 'North': 'Meat Locker', 'East': 'Dojo', 'Item': 'Charm'},
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

            current_room = "Liminal Space"  
            new_adventure(session, current_room)

        elif choice == '2':
            print("Exiting the game. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter '1' for New Adventure or '2' to Exit.")
            input("Press enter to continue...")

if __name__ == "__main__":
    main()
