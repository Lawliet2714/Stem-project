import random
import getpass
import copy

# ═══════════════════════════════════════════════════════════════
#  DUNGEON ESCAPE  —  A Text Adventure
# ═══════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────
# STATES
# ─────────────────────────────────────────────
STATE_EXPLORE = "explore"
STATE_BOSS    = "boss"

# ─────────────────────────────────────────────
# ROOM DEFINITIONS (now include "state")
# ─────────────────────────────────────────────
rooms_template = {
    "cell":  {
        "description": (
            "You wake up on a cold stone floor. Your head throbs.\n"
            "A wooden door hangs open to the NORTH.\n"
            "Scratched into the wall:Don't trust the guard.\n"
            "A hooded criminal is among us\n"
            "type in command 'look' to check out what you have and your surroundings"
        ),
        "exits": {"north": "corridor"},
        "state": STATE_EXPLORE
    },

    "corridor": {
        "description": (
            "A long torchlit corridor stretches out.\n"
            "A heavy door leads EAST — sounds like clanging metal.\n"
            "The main passage continues NORTH."
        ),
        "exits": {"north": "guard_post", "east": "armory", "south": "cell"},
        "state": STATE_EXPLORE
    },

    "armory": {
        "description": (
            "Dusty weapon racks line the walls.\n"
            "Most are bare, but a SWORD still hangs near the door.\n"
            "The corridor is back to the WEST."
        ),
        "exits": {"west": "corridor"},
        "item": "sword",
        "state": STATE_EXPLORE
    },

    "guard_post": {
        "description": (
            "A burly guard sits at a table, half-asleep.\n"
            "A KEY hangs from his belt.\n"
            "A locked iron door stands to the NORTH. The corridor is SOUTH."
        ),
        "exits": {"north": "great_hall", "south": "corridor"},
        "locked_north": True,
        "item": "key",
        "guard": True,
        "state": STATE_EXPLORE
    },

    "great_hall": {
        "description": (
            "A vaulted great hall. Moonlight pours through high windows.\n"
            "A passage leads EAST — you can see glinting gold.\n"
            "Massive front doors stand to the NORTH."
        ),
        "exits": {"north": "boss_room", "east": "treasure_room", "south": "guard_post"},
        "state": STATE_EXPLORE
    },

    "treasure_room": {
        "description": (
            "Gold coins and jewels blanket the floor.\n"
            "You see a scythe among them that disappears magically.\n"
            "Among them sits a glowing HEALTH POTION.\n"
            "The great hall is back to the WEST."
        ),
        "exits": {"west": "great_hall"},
        "item": "health potion",
        "state": STATE_EXPLORE
    },

    "boss_room": {
        "description": (
            "You enter a giant dark room with a bunch of pillars.\n"
            "You see a black cloaked person.\n"
            "Good luck {name}! Survival is not guaranteed...\n"
            "I almost feel bad for a being like you {name}.\n"
            "He cuts down one of the main pillars with the scythe."
        ),
        "exits": {},
        "state": STATE_BOSS
    },
}

boss_moves = ["parry", "reckless attack", "reinforcement", "blood attack"]
options    = ["attack", "heal", "restart", "tunder clap and flash", "arshy"]

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def show_status(health, inventory):
    items = ", ".join(inventory) if inventory else "empty"
    print(f"\n  ♥  Health: {health}   |   Inventory: {items}")
    print("  " + "─" * 44)

def describe_room(room_name, player_name, rooms):
    desc = rooms[room_name]["description"]
    print("\n" + desc.format(name=player_name))

def look(room_name, player_name, inventory, health, rooms):
    print("\nYou take a careful look around...")
    describe_room(room_name, player_name, rooms)
    show_status(health, inventory)

def handle_item(room, inventory, health):
    if "item" in room:
        item = room["item"]
        print(f"\nYou notice a {item.upper()} here. Pick it up? (yes/no)")
        if input("> ").strip().lower() == "yes":
            inventory.append(item)
            print(f"You picked up the {item}.")
            del room["item"]
            if item == "health potion":
                health = min(100, health + 10)
                print("You feel energy surge through you! (+10 health)")
    return health

def analyze_inventory(inventory, search_item):
    count = sum(1 for item in inventory if item == search_item)
    if count > 0:
        return f"You have {count} {search_item}(s)."
    return f"You do not have a {search_item}."

def handle_guard(room, inventory, health):
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
                return health, True
    return health, False

# ─────────────────────────────────────────────
# STATE FUNCTIONS
# ─────────────────────────────────────────────
def state_explore(player_name, health, inventory, current_room, rooms):
    room = rooms[current_room]

    describe_room(current_room, player_name, rooms)
    show_status(health, inventory)

    if room.get("guard"):
        health, game_over = handle_guard(room, inventory, health)
        if game_over:
            return health, current_room, STATE_EXPLORE, True

    health = handle_item(room, inventory, health)

    exits = room["exits"]
    print(f"Exits: {', '.join(exits.keys())}")
    choice = input("> ").strip().lower()

    if choice == "look":
        look(current_room, player_name, inventory, health, rooms)

    elif choice in exits:
        next_room = exits[choice]
        if room.get("locked_north") and choice == "north" and "key" not in inventory:
            print("\n[!] The iron door is locked. You need a KEY.")
        else:
            current_room = next_room

            describe_room(current_room, player_name, rooms)

    else:
        print(f"\n[!] {choice} is not something you can do...")

    # AUTO-DETECT STATE BASED ON ROOM
    next_state = rooms[current_room].get("state", STATE_EXPLORE)

    return health, current_room, next_state, False


def state_boss(player_name, health, inventory, current_room, rooms):
    boss_health = 100

    while True:
        computer = random.choice(boss_moves)
        print(f"\nThe boss prepares a {computer}!")
        player = input("Choose your move (attack, heal, restart, Tunder Clap And Flash): ").lower().strip()

        if player not in options:
            print("Invalid move.")
            continue

        elif player == "restart":
            print("\nRestarting the game...\n")
            play()
            return health, current_room, STATE_BOSS, True

        elif player == "heal":
            health = min(100, health + 20)
            print(f"You healed! Health is now {health}.")

        elif player == "attack":
            if computer == "parry":
                damage = random.choice([25, 20, 15])
                boss_health -= damage
                print(f"He tries to parry but you're too precise! Dealt {damage} damage!")

            elif computer == "reckless attack":
                outcome = random.choice(["fail", "success"])
                if outcome == "fail":
                    damage = random.choice([25, 20, 15])
                    health -= damage
                    print(f"You can't keep up with him! Took {damage} damage!")
                else:
                    damage = random.choice([25, 20, 15])
                    boss_health -= damage
                    print(f"Dead Calm! You cut him down! Dealt {damage} damage!")

            elif computer == "reinforcement":
                damage = random.choice([30, 25, 20])
                health -= damage
                print(f"He calls for backup — you're overwhelmed! Took {damage} damage!")

            elif computer == "blood attack":
                outcome = random.choice(["fail", "success"])
                if outcome == "fail":
                    damage = random.choice([35, 30, 25])
                    health -= damage
                    print(f"His blood attack tears through you! Took {damage} damage!")
                else:
                    damage = random.choice([20, 15, 10])
                    boss_health -= damage
                    print(f"You dodge and counter! Dealt {damage} damage!")

        elif player == "arshy":
            boss_health = 0
            print("A mysterious force surges through you... the boss crumbles instantly.")

        elif player == "tunder clap and flash":
            if computer in ["reinforcement", "reckless attack"]:
                damage = random.choice([40, 35, 30])
                boss_health -= damage
                print(f"Thunder and lightning! The boss is staggered! Dealt {damage} damage!")
            else:
                damage = random.choice([15, 10, 5])
                health -= damage
                print(f"The boss saw it coming! You took {damage} damage!")

        print(f"\n  ♥ Your health: {health}  |  Boss health: {boss_health}")

        if boss_health <= 0:
            print(f"\nYou defeated the boss, {player_name}! You escape the dungeon!")
            return health, current_room, STATE_BOSS, True

        if health <= 0:
            print("\nYou died...")
            return health, current_room, STATE_BOSS, True

# ─────────────────────────────────────────────
# MAIN GAME LOOP
# ─────────────────────────────────────────────
def play():
    rooms = copy.deepcopy(rooms_template)
    player_name = input("What is your name, adventurer? ").strip()
    health      = 100
    inventory   = []
    current_room = "cell"
    state = STATE_EXPLORE

    print(f"\nWelcome, {player_name}. The dungeon stretches ahead.\n")

    states = {
        STATE_EXPLORE: state_explore,
        STATE_BOSS:    state_boss,
    }

    while True:
        handler = states[state]
        health, current_room, state, game_over = handler(
            player_name, health, inventory, current_room, rooms
        )
        if game_over:
            return

if __name__ == "__main__":
    play()
