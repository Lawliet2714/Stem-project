import random
import getpass

# ═══════════════════════════════════════════════════════════════
#  DUNGEON ESCAPE  —  A Text Adventure
# ═══════════════════════════════════════════════════════════════

rooms = {
    "cell":  {
        "description":  (
            "You wake up on a cold stone floor. Your head throbs.\n"
            "A wooden door hangs open to the NORTH.\n"
            "Scratched into the wall:'Don't trust the guard.\n"
            "A hooded criminal is among us"
            "type in command 'look' to check out what you have and your surroundings"
        ),
        "exits":  {"north":  "corridor"},
    },
    "corridor":  {
        "description":  (
            "A long torchlit corridor stretches out.\n"
            "A heavy door leads EAST — sounds like clanging metal.\n"
            "The main passage continues NORTH."
        ),
        "exits":  {"north":  "guard_post",  "east":  "armory",  "south":  "cell"},
    },
    "armory":  {
        "description":  (
            "Dusty weapon racks line the walls.\n"
            "Most are bare,      but a SWORD still hangs near the door.\n"
            "The corridor is back to the WEST."
        ),
        "exits":  {"west":  "corridor"},
        "item":  "sword",
    },
    "guard_post":  {
        "description":  (
            "A burly guard sits at a table,      half-asleep.\n"
            "A KEY hangs from his belt.\n"
            "A locked iron door stands to the NORTH. The corridor is SOUTH."
        ),
        "exits":  {"north":  "great_hall",  "south":  "corridor"},
        "locked_north":  True,
        "item":  "key",
        "guard":  True,
    },
    "great_hall":  {
        "description":  (
            "A vaulted great hall. Moonlight pours through high windows.\n"
            "A passage leads EAST — you can see glinting gold.\n"
            "Massive front doors stand to the NORTH."
        ),
        "exits":  {"north":  "boss_room",  "east":  "treasure_room",  "south":  "guard_post"},
    },
    "treasure_room":  {
        "description":  (
            "Gold coins and jewels blanket the floor.\n"
            "You see a scyte among them that disapears magically"
            "Among them sits a glowing HEALTH POTION.\n"
            "The great hall is back to the WEST."
        ),
        "exits":  {"west":  "great_hall"},
        "item":  "health potion",
    },
    "boss_room":  {
        "description":  (
            "You enter a giant dark room with a bunch of pillars\n"
            "you see a black cloaked person\n"
            "Good luck {name}! Survival is not guaranteed..."
            "I almost feel bad for a being like you {name}"
            "he cuts down one of the main pillars with the scythe"
        ),
        "exits":  {},
    },
}

boss_moves =["parry", "reckless attack", "reinforcement", "blood attack"]
options = ["attack","heal",  "restart", "arshy", "Tunder Clap And Flash"]
running = True

# ─────────────────────────────────────────────
# STATE MACHINE
# ─────────────────────────────────────────────
STATE_EXPLORE = "explore"
STATE_BOSS = "boss"


def player_moves_action_1(action,  boss_health):
    if action == "attack":
        boss_health -= 25
    return boss_health

def show_status(health,  inventory):
    items = ",  ".join(inventory) if inventory else "empty"
    print(f"\n  ♥  Health:  {health}   |   Inventory:  {items}")
    print("  " + "─" * 44)

def describe_room(room_name,  player_name):
    desc = rooms[room_name]["description"]
    print("\n" + desc.format(name=player_name))

def look(room_name,  player_name,  inventory,  health):
    print("\nYou take a careful look around...")
    describe_room(room_name,  player_name)
    show_status(health,  inventory)

# Fixed:  Corrected parameter names (North -> north,  etc.)
def move_counter(north,  south,  east,  west):
    pass

#HEALTH POTION HEALING
def handle_item(room, inventory, health):
    if "item" in room:
        item = room["item"]
        print(f"\nYou notice a {item.upper()} here. Pick it up? (yes/no)")
        if input("> ").strip().lower() == "yes":
            inventory.append(item)
            print(f"You picked up the {item}.")
            del room["item"]

            # Health potion effect (+10 HP)
            if item == "health potion":
                health += 10
                print("You feel energy surge through you! (+10 health)")
    return health

#ap csp
def analyze_inventory(inventory, search_item):
    count = 0  # sequencing

    for item in inventory:  # iteration
        if item == search_item:  # selection
            count += 1

    if count > 0:
        return f"You have {count} {search_item}(s)."
    else:
        return f"You do not have a {search_item}."
#ap csp

def handle_guard(room,  inventory,  health):
    if room.get("guard") and "key" not in inventory:
        print("\nThe guard jolts awake and steps in front of you!")

        if "sword" in inventory:
            print("You raise your sword. He backs away and drops the KEY.")
            inventory.append("key")
            if "item" in room:
                del room["item"]
            room["guard"] = False
        else:
            print("He shoves you hard! You stumble back and lose 1 health.")
            health -= 1
            if health <= 0:
                print("\nYou collapse from your wounds. Game over.")
                return health,  True  # Game over

    return health,  False

def play():
    player_name = input("What is your name,  adventurer? ").strip()
    health = 100
    inventory = []
    current_room = "cell"
    print(f"\nWelcome,  {player_name}. The dungeon stretches ahead.\n")
    boss_health = 100

    while True:
        room = rooms[current_room]

        describe_room(current_room,  player_name)
        show_status(health,  inventory)

        # Boss room stops the loop

        #boss_moves =["parry", "reckless attack", "reinforcement", "blood attack"]
        #options = ["attack","heal",  "restart", "arshy", "Tunder Clap And Flash"]

        if current_room == "boss_room":
            while running:
                computer = random.choice(boss_moves)
                player = input("Choose your move (attack, blood attack, heal, restart): ").lower().strip()

                if player not in options:
                    print("Invalid move.")
                    continue


                elif player == "attack" and computer == "reckless attack":
                    outcome = random.choice(["fail", "success"])
                    if outcome == "fail":
                        damage = random.choice([25, 20, 15])
                        health -= damage
                        print(f"You can't keep up with him! You took {damage} damage!")

                    if outcome == "fail":
                        print("You can't keep up with him!")
                        damage = random.choice([25, 20, 15])
                        health -= damage
                        print(f"You took {damage} damage!")

                    else:
                        print("You use Dead Calm and cut away at him!")
                        damage = random.choice([25, 20, 15])
                        boss_health -= damage
                        print(f"You dealt {damage} damage!")
                        print(f"Boss health is now {boss_health}")

                elif print("you can't keep up with him"):

                    damage = random.choice([25, 20, 15])
                    health -= damage

                elif print("you use dead calm and you were able to cut away at him"):
                    damage = random.choice([25, 20, 15])
                    boss_health -= damage

                    print(f"You took {damage} damage!")
                    print(f"Boss health is now {boss_health}")

                elif player == "attack" and computer =="parry":
                    print("He tries to parry but your too calm and precise")

                    damage = random.choice([25, 20, 15])

                    boss_health -= damage

                    print(f"You took {damage} damage!")
                    print(f"Boss health is now {boss_health}")

                elif player == "heal":
                    health += 20
                    print("you healed +20")


                elif player == "restart":
                    print("\nRestarting the game...\n")
                    play()  # recursively restart
                    return  # exit the current run entirely

                if boss_health <= 0:
                    print("You defeated the boss! Congratulations!")
                    break

                if health <= 0:
                    print("You died...")
                    break

        if room.get("guard"):
            health,  game_over = handle_guard(room,  inventory,  health)
            if game_over:
                return  # End the game


        health = handle_item(room, inventory, health)

        exits = room["exits"]
        print(f"Exits:  {',  '.join(exits.keys())}")

        choice = input("> ").strip().lower()

        if choice == "look":
            look(current_room,  player_name,  inventory,  health)

        elif choice in exits:
            next_room = exits[choice]
            if room.get("locked_north") and choice == "north" and "key" not in inventory:
                print("\n[!] The iron door is locked. You need a KEY.")
            else:
                current_room = next_room

        else:
            print(f"\n[!] {choice} is not something you can do...")

    play_again = input("play again? (y/n):  ").lower().strip()
    if play_again == "y":
        play()  # Restart the game

if __name__ == "__main__":
    play()