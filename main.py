import random
from classes import Player, Enemy, Move
from ui_effects import clear_screen, slow_print, show_divider
from file_manager import load_move_parts

def move_workshop(player):
    effects, deliveries, modifiers = load_move_parts("moves_data.csv")
    
    clear_screen()
    show_divider()
    print("WELCOME TO THE MOVE WORKSHOP")
    show_divider()

    # Choice 1: Effect
    print("\nSelect an Effect:")
    for index, item in enumerate(effects):
        print(f"{index + 1}. {item['name']} - {item['desc']}")
    effect_choice = effects[int(input("Selection: ")) - 1]

    # Choice 2: Delivery
    print("\nSelect a Delivery Method:")
    for index, item in enumerate(deliveries):
        print(f"{index + 1}. {item['name']} - {item['desc']}")
    delivery_choice = deliveries[int(input("Selection: ")) - 1]

    # Choice 3: Modifier
    print("\nSelect a Modifier:")
    for index, item in enumerate(modifiers):
        print(f"{index + 1}. {item['name']} - {item['desc']}")
    modifier_choice = modifiers[int(input("Selection: ")) - 1]

    # Combine move parts
    new_name = f"{modifier_choice['name']} {effect_choice['name']}"
    total_cost = effect_choice['cost'] + delivery_choice['cost'] + modifier_choice['cost']
    
    new_move = Move(new_name, effect_choice, delivery_choice, modifier_choice, total_cost)
    player.moves.append(new_move)
    
    slow_print(f"\nYou have learned {new_name}!")
    input("\nPress Enter to continue...")

def start_combat(player, enemy):
    slow_print(f"\nAn enemy {enemy.name} approaches!")
    
    while enemy.is_alive() and player.health_points > 0:
        try:
            player.show_status()
            print(f"Enemy HP: {enemy.health_points}")
            print("\nWhat will you do?")
            print("1. Standard Attack")
            
            # List custom moves from workshop
            for i, move in enumerate(player.moves):
                print(f"{i + 2}. Use {move.name} ({move.mana_cost} Mana)")
            
            choice = input("> ")
            
            damage_to_deal = 0
            
            if choice == "1":
                damage_to_deal = player.strength_stat + random.randint(1, 5)
                slow_print(f"You hit for {damage_to_deal} damage!")
            else:
                # Logic for custom moves
                move_index = int(choice) - 2
                selected_move = player.moves[move_index]

                if player.mana_points >= selected_move.mana_cost:
                    player.mana_points -= selected_move.mana_cost
                    
                    base_dmg = 0
                    if selected_move.delivery['name'] == "Physical":
                        # Strength + small random roll - enemy armor (Endurance)
                        base_dmg = player.strength_stat + random.randint(5, 15)
                        base_dmg = base_dmg - (enemy.strength_stat // 2) 
                    elif selected_move.delivery['name'] == "Wild":
                        # Stable damage
                        base_dmg = player.strength_stat + 12
                    elif selected_move.delivery['name'] == "Vital":
                        # Based on current health
                        base_dmg = player.strength_stat + int(0.2*player.health_points) 
                    final_dmg = base_dmg
                    
                    if selected_move.effect['name'] == "Strike":
                        # Stable damage
                        final_dmg = int(final_dmg * 1.5)
                    elif selected_move.effect['name'] == "Blast":
                        # Stable damage
                        final_dmg = int(final_dmg * random.float(1.25,1.75))
                    elif selected_move.effect['name'] == "Drain":
                        # Drain health
                        final_dmg = int(final_dmg * 0.8)
                        heal = int(final_dmg * 0.5)
                        player.health_points = min(player.max_health, player.health_points + heal)
                        slow_print(f"Drain! You siphoned {heal} HP!")
                    elif selected_move.effect['name'] == "Mend":
                        final_dmg = 0
                        heal = 25
                        player.health_points = min(player.max_health, player.health_points + heal)
                        slow_print(f"You used Mend and healed {heal} HP!")

                    if selected_move.modifier['name'] == "Piercing":
                        # Adds flat damage to represent ignoring armor
                        final_dmg += 7 
                    elif selected_move.modifier['name'] == "Vampiric":
                        # Heal without drain
                        vamp_heal = int(final_dmg * 0.4)
                        player.health_points = min(player.max_health, player.health_points + vamp_heal)
                        slow_print(f"Vampiric! You healed {vamp_heal} from the strike!")
                    elif selected_move.modifier['name'] == "Stunning":
                        # 25% chance to stun
                        if random.random() < 0.25:
                            print(f"STUNNED! The {enemy.name} loses its next turn!")

                    # Apply final damage to enemy
                    if final_dmg > 0:
                        enemy.health_points -= final_dmg
                        slow_print(f"Your {selected_move.name} dealt {final_dmg} damage!")

                else:
                    slow_print("Not enough mana!")

            enemy.health_points -= damage_to_deal

            if enemy.is_alive():
                enemy_hit = enemy.strength_stat + random.randint(1, 3)
                player.health_points -= enemy_hit
                slow_print(f"The {enemy.name} hits you back for {enemy_hit}!")
        except IndexError:
            slow_print("Invalid move number. Try again.")
    if player.health_points > 0:
        slow_print(f"You defeated the {enemy.name}!")
        return True
    return False

def main():
    clear_screen()
    slow_print("--- DUNGEON ADVENTURE ---")
    name = input("Hero Name: ")
    
    user = Player(name)
    
    # First, go to the workshop
    move_workshop(user)
    
    # Simple enemy list
    monsters = [Enemy("Slime", 60, 2), Enemy("Orc", 80, 6), Enemy("Goblin", 70, 4), Enemy("Demon King", 100, 10)]
    #Combat loop
    for monster in monsters:
        if monster.name == "Demon King":
            slow_print("Final boss...")
            if not start_combat(user, monster):
                slow_print("Game Over...")
                break
            slow_print("You win!")
        if not start_combat(user, monster):
            slow_print("Game Over...")
            break
        user.restore()
        move_workshop(user)
        print("\nYou move deeper...")

if __name__ == "__main__":
    main()