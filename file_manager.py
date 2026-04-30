import csv

def load_move_parts(file):
    effects = []
    deliveries = []
    modifiers = []

    with open(file, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            #Saves entire row in dictionary
            components = {
                "name": row["Name"],
                "desc": row["Description"],
                "cost": int(row["ManaCost"])
            }
            #Checks type of component then appends to its specific list
            if row["Type"] == "Effect":
                effects.append(components)
            elif row["Type"] == "Delivery":
                deliveries.append(components)
            elif row["Type"] == "Modifier":
                modifiers.append(components)
    
    return effects, deliveries, modifiers