import random
import copy

# ═══════════════════════════════════════════════════════════════
#  DUNGEON ESCAPE  —  A Text Adventure
# ═══════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────
# STATES
# ─────────────────────────────────────────────
STATE_EXPLORE = "explore"
STATE_BOSS    = "boss"

rooms_template = {
    "cell":  {
        "description": (
            "You wake up on a cold stone floor. Your head throbs.\n"
            f"A wooden door hangs open to the \033[91mNORTH.\033[0m\n"
            "Scratched into the wall: Don't trust the guard.\n"
            "A hooded criminal is among us\n"
            "type in command \033[91mlook\033[0m to check out what you have and your surroundings"
        ),
        "exits": {"north": "corridor"},
        "state": STATE_EXPLORE
    },

    "corridor": {
        "description": (
            "A long torchlit corridor stretches out.\n"
            f"A heavy door leads \033[91mEAST\033[0m — sounds like clanging metal.\n"
            f"The main passage continues \033[91mNORTH\033[0m."

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
            f"A \033[91mKEY\033[0m hangs from his belt.\n"
            f"A locked iron door stands to the \033[91mNORTH\033[0m. The corridor is \033[91mSOUTH\033[0m."

        ),
        "exits": {"north": "great_hall", "south": "corridor"},
        "locked_north": True,
        "item": "key",
        "guard": True,
        "state": STATE_EXPLORE
    },

    "great_hall": {
        "description": (
            "A long torchlit corridor stretches out.\n"
f"A heavy door leads \033[91mEAST\033[0m — sounds like clanging metal.\n"
f"The walls shimmer with a \033[93mglinting gold\033[0m hue.\n"
f"The main passage continues \033[91mNORTH\033[0m."

        ),
        "exits": {"north": "boss_room", "east": "treasure_room", "south": "guard_post"},
        "state": STATE_EXPLORE
    },

    "treasure_room": {
        "description": (
            "Gold coins and jewels blanket the floor.\n"
           "You see a \033[94mscythe\033[0m among them that \033[93mdisappears\033[0m magically.\n"
            "Among them sits a glowing \033[94mHEALTH POTION\033[0m.\n"
            "The great hall is back to the \033[91mWEST\033[0m."

        ),
        "exits": {"west": "great_hall"},
        "item": "health potion",
        "state": STATE_EXPLORE
    },

    "boss_room": {
        "description": (
            "You enter a giant dark room with a bunch of pillars.\n"
"You see a black cloaked person.\n"
"Good luck Survival is not guaranteed...\n"
"I almost feel bad for a being like you {name}.\n"
"He cuts down one of the main pillars with the \033[94mscythe\033[0m."
        ),
        "exits": {},
        "state": STATE_BOSS
    },
}

# ─────────────────────────────────────────────
# WEAPON SYSTEM (NEW + CLEAN)
# ─────────────────────────────────────────────

class Weapon:
    def __init__(self, name):
        self.name = name

    def light_attack(self):
        raise NotImplementedError

    def heavy_attack(self):
        raise NotImplementedError

    def special_attack(self):
        raise NotImplementedError


class BloodSword(Weapon):
    def __init__(self):
        super().__init__("Tunder clap and flash")

    # Normal attack (your original 25/20/15)
    def light_attack(self):
        return random.choice([25, 20, 15])

    # Blood attack (your original 35/30/25)
    def heavy_attack(self):
        return random.choice([35, 30, 25])

    # Thunder Clap and Flash (your original 40/35/30)
    def special_attack(self):
        return random.choice([40, 35, 30])


class WeaponManager:
    def __init__(self):
        self.weapon = BloodSword()  # default weapon

    def equip(self, weapon):
        self.weapon = weapon

    def light(self):
        return self.weapon.light_attack()

    def heavy(self):
        return self.weapon.heavy_attack()

    def special(self):
        return self.weapon.special_attack()


weapon_manager = WeaponManager()


boss_moves = ["parry", "reckless attack", "reinforcement", "blood attack"]
options    = ["attack", "heal", "restart", "tunder clap and flash", "arshy"]

STATE_EXPLORE = "explore"
STATE_BOSS = "boss"

# rooms_template must exist in your full file
# (not included in your snippet)

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
# STATE: EXPLORE
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

    next_state = rooms[current_room].get("state", STATE_EXPLORE)
    return health, current_room, next_state, False

# ─────────────────────────────────────────────
# STATE: BOSS
# ─────────────────────────────────────────────

def state_boss(player_name, health, inventory, current_room, rooms):
    boss_health = 100

    while True:
        computer = random.choice(boss_moves)
        print(f"\nThe boss prepares a {computer}!")
        player = input("Choose your move (attack, heal, restart, Tunder Clap And Flash): ").lower().strip()

        # Handle "description" or "description - <move>"
        if player.startswith("description"):
            parts = player.split("-", 1)
            if len(parts) == 2:
                move_to_describe = parts[1].strip()
            else:
                move_to_describe = computer  # default to the boss's current move
            describe_move(move_to_describe)
            continue  # re-prompt without advancing the turn
        if player not in options:
            print("Invalid move.")
            continue


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
            damage = weapon_manager.light()

            if computer == "parry":
                boss_health -= damage
                print(f"He tries to parry but you're too precise! Dealt {damage} damage!")

            elif computer == "reckless attack":
                outcome = random.choice(["fail", "success"])
                if outcome == "fail":
                    health -= damage
                    print(f"You can't keep up with him! Took {damage} damage!")
                else:
                    boss_health -= damage
                    print(f"Dead Calm! You cut him down! Dealt {damage} damage!")

            elif computer == "reinforcement":
                dmg = random.choice([30, 25, 20])
                health -= dmg
                print(f"He calls for backup — you're overwhelmed! Took {dmg} damage!")

            elif computer == "blood attack":
                outcome = random.choice(["fail", "success"])
                if outcome == "fail":
                    dmg = weapon_manager.heavy()
                    health -= dmg
                    print(f"His blood attack tears through you! Took {dmg} damage!")
                else:
                    boss_health -= damage
                    print(f"You dodge and counter! Dealt {damage} damage!")

        elif player == "arshy":
            boss_health = 0
            print("You use getsuga tenshou")

        elif player == "tunder clap and flash":
            if computer in ["reinforcement", "reckless attack"]:
                damage = weapon_manager.special()
                boss_health -= damage
                print(f"Thunder and lightning! The boss is staggered! Dealt {damage} damage!")
            else:
                dmg = random.choice([15, 10, 5])
                health -= dmg
                print(f"The boss saw it coming! You took {dmg} damage!")

        print(f"\n  ♥ Your health: {health}  |  Boss health: {boss_health}")

        if boss_health <= 0:
            print(f"\nYou defeated the boss, {player_name}! You escape the dungeon!")
            return health, current_room, STATE_BOSS, True

        if health <= 0:
            print("\nYou died...")
            return health, current_room, STATE_BOSS, True

# ─────────────────────────────────────────────
# MOVE DESCRIPTIONS
# ─────────────────────────────────────────────

move_descriptions = {
    "Tunder clap and flash ": " ",
    "reckless attack": "A wild, all-or-nothing swing — high risk for both sides.",
    "reinforcement": "He signals for backup. Minions swarm you.",
    "blood attack": "A vicious cursed slash that drains your life force.",
}

def describe_move(move_name):
    desc = move_descriptions.get(move_name.lower())
    if desc:
        print(f"\n[{move_name.upper()}]: {desc}")
    else:
        print(f"\nNo description available for '{move_name}'.")
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
