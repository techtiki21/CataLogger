from datetime import datetime
import click
import sql
import analyze
import plotext as plt

# extra functions
def getFullOption(letter):
    if letter == None:
        return letter
    if letter.upper() == "L":
        return "Low"
    if letter.upper() == "N":
        return "Normal"
    if letter.upper() == "H":
        return "High"
    if letter.upper() == "S":
        return "Straining"
    if letter.upper() == "D":
        return "Diarrhea"
    if letter.upper() == "C":
        return "Constipated"
    if letter.upper() in ("NA", "N/A"):
        return "N/A"


@click.group()
def main():
    """Catalogger: An AI-Powered Cat Health Logger"""
    print("\n")
    sql.initDB()
    pass

@main.command()
@click.option("--name", required=True, help="Name of your cat.")
@click.option("--birth", help="Formatted as YYYY-MM-DD")
@click.option("--breed", help="Breed of your cat.")
def add_entry(name, birth, breed):
    """Add a new cat to the database"""
    if birth:
        try:
            datetime.strptime(birth, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return
    sql.addEntry(name.lower(), birth, breed)

@main.command()
@click.option("--cat", help="Name or ID of the cat you want to log.")
@click.option("--weight", type=float, help="Weight of the cat in kilograms.")
@click.option("--activity", type=click.IntRange(1, 5), help="How active your cat is on a scale of 1-5.")
@click.option("--appetite", type=click.Choice(["None", "N", "L", "H", "N/A", "NA"], case_sensitive=False), help="None, (N)ormal, (L)ow, (H)igh")
@click.option("--water", type=click.Choice(["None", "N", "L", "H", "N/A", "NA"], case_sensitive=False), help="None, (N)ormal, (L)ow, (H)igh")
@click.option("--litter", type=click.Choice(["None", "N", "S", "D", "C", "N/A", "NA"], case_sensitive=False), help="(N)ormal, (S)training, (D)iarrhea, (C)onstipated")
@click.option("--notes", help="Extra notes the AI can use to better its understanding of the cat.")
def log(cat, weight, activity, appetite, water, litter, notes):
    """Log metrics of a saved cat"""
    while cat == None:
        cat = input("Enter the name of the cat: ")
        if sql.fetchCat(cat.lower()) == "NoName":
            print("That cat does not exist.")
            cat = None
    while weight == None:
        try:
            weight = float(input("Enter the weight of the cat (kg): "))
        except ValueError:
            print("Must be a number")
            weight = None
    while activity == None:
        try:
            activity = int(input("Rate the activity level of the cat from 1-5: "))
        except ValueError:
            activity = 0
        if activity > 5 or activity < 1:
            print("Bad activity level")
            activity = None
    while appetite == None:
        appetite = input("How much appetite does the cat have; None, (N)ormal, (L)ow, (H)igh, (N/A): ")
        if appetite.upper() not in ("NONE", "N", "L", "H", "N/A", "NA"):
            print("Not a valid appetite type")
            appetite = None
    while water == None:
        water = input("How much water does the cat take; None, (N)ormal, (L)ow, (H)igh, (N/A): ")
        if water.upper() not in ("NONE", "N", "L", "H", "N/A", "NA"):
            print("Not a valid water intake type")
            water = None
    while litter == None:
        litter = input("What's the litter of the cat like; (N)ormal, (S)training, (D)iarrhea, (C)onstipated, (N/A):")
        if litter.upper() not in ("N", "S", "D", "C", "N/A", "NA"):
            print("Not a valid litter type")
            litter = None
    if notes == None:
        notes = input("Any extra notes you would like to add (blank to leave empty): ")

    if activity > 5 or activity < 1:
        print("Bad activity level")
        return
    if sql.fetchCat(cat) == "NoName":
        print("That cat does not exist.")
        return
    appetite = getFullOption(appetite)
    water = getFullOption(water)
    litter = getFullOption(litter)
    
    print(f"Cat = {cat} | ID: {sql.fetchCat(cat.lower())}")
    print(f"Weight = {weight}kg")
    print(f"Activity = {activity}")
    print(f"Appetite = {appetite}")
    print(f"Water Intake = {water}")
    print(f"Litter = {litter}")
    print(f"Notes = {notes}")
    userInput = 'a'
    while userInput != 'n' or userInput != 'y':
        userInput = str(input("Confirm metrics? (y/n): "))
        if userInput.lower() == 'y':
            sql.log(sql.fetchCat(cat), cat.lower(), weight, activity, appetite, water, litter, notes)
            print(f"Metrics for {cat} has been logged!")
            break
        elif userInput.lower() == 'n':
            break
        else:
            print("Invalid option.")
            continue

@main.command()
def list_cats():
    """List all cats stored in the database"""
    cats = sql.listCats()
    for cat in cats:
        print(f"{cat[0]}: | Born: {cat[1]} | Breed: {cat[2]} | Entry Created: {cat[3]} | ID: {cat[4]}")

@main.command()
@click.option("--cat", help="Show metrics of a specific cat.")
def history(cat):
    """Show metrics of all cats or a specific cat"""
    log = sql.metricLog(cat)
    if cat == None:
        print("All saved metrics")
        for l in log:
            print(f"Cat: {l[8]} | Logged at: {l[7]} | Weight: {l[1]}kg | Activity: {l[2]} | Appetite: {l[3]} | Water: {l[4]} | Litter: {l[5]} | ID: {l[0]}")
    else:
        log = sql.metricLog(cat.lower())
        print(f"Metrics for {cat}:")
        for l in log:
            print(f"Logged at: {l[7]} | Weight: {l[1]}kg | Activity: {l[2]} | Appetite: {l[3]} | Water: {l[4]} | Litter: {l[5]} | ID: {l[0]}")

@main.command()
@click.option("--cat", required=True, help="Graph the weight of a cat over time")
def graph(cat):
    """Graph the weight of a cat over time"""
    if sql.fetchCat(cat.lower()) == "NoName":
        print("That cat does not exist.")
        return
    log = sql.metricLog(cat.lower())
    dates = []
    weights = []
    for l in log:
        weights.append(l[1])
        dates.append(datetime.strptime(l[7], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y"))
    if weights == []:
        print(f"No weights logged for {cat}.")
        return
    plt.plot(weights)
    plt.xticks(range(len(dates)), dates)
    plt.title(f"{cat}'s Weight Over Time")
    plt.ylabel("kg")
    plt.show()

@main.command()
@click.option("--cat", required=True, help="Name of the cat to analyze.")
def overview(cat):
    """Use AI to provide a health overview of a specific cat"""
    analyze.aiAnalysis(cat)

@main.command()
@click.option("--mode", type=click.Choice(["cats", "cat", "logs", "log"], case_sensitive=False), required=True, help="Clear an entry from saved cats or a log")
@click.option("--id", type=int, help="ID of the row you want to clear")
def delete(mode, id):
    """Delete a cat entry or remove a log from the database permenantly"""
    selectedCat = []
    if mode.lower() == "cat" or mode.lower() == "cats":
        if id == None:
            print("Saved Cats:")
            cats = sql.listCats()
            if cats == []:
                print("No cats to delete.")
                return
            for cat in cats:
                print(f"{cat[0]}: | Born: {cat[1]} | Breed: {cat[2]} | Entry Created: {cat[3]} | ID: {cat[4]}")
            print("\n")
            try:
                id = int(input("Select the cat's ID: "))
            except ValueError:
                print("Not an integer.")
                return
        selectedCat = sql.queryCat(id)
        print("\n")
        if selectedCat == []:
            print("No cats match that ID.")
            return
        for cat in selectedCat:
            print(f"{cat[0]}: | Born: {cat[1]} | Breed: {cat[2]} | Entry Created: {cat[3]} | ID: {cat[4]}")
        userConfirm = "a"
        while userConfirm.lower() != "y" or userConfirm.lower() != "n":
            userConfirm = input("Is this the cat you want to delete? All associated logs will be deleted with it too. (Y/N): ")
            if userConfirm.lower() == "y":
                sql.delete("cats", id)
                print("Cat and its logs have been deleted successfuly!")
                return
            elif userConfirm.lower() == "n":
                 return
            else:
                print("Invalid choice.")
                continue

    if mode.lower() == "log" or mode.lower() == "logs":
        if id == None:
            print("Logged metrics: ")
            logs = sql.metricLog(id)
            if logs == []:
                print("No logs to delete.")
                return
            for l in logs:
                 print(f"Cat: {l[8]} | Logged at: {l[7]} | Weight: {l[1]}kg | Activity: {l[2]} | Appetite: {l[3]} | Water: {l[4]} | Litter: {l[5]} | ID: {l[0]}")
            print("\n")
            try:
                id = int(input("Select the log ID: "))
            except ValueError:
                print("Not an integer.")
                return
        selectedLog = sql.queryLog(id)
        print("\n")
        if selectedLog == []:
            print("No logs match that ID.")
            return
        for l in selectedLog:
            print(f"Cat: {l[8]} | Logged at: {l[7]} | Weight: {l[1]}kg | Activity: {l[2]} | Appetite: {l[3]} | Water: {l[4]} | Litter: {l[5]} | ID: {l[0]}")
        userConfirm = "a"
        while userConfirm.lower() != "y" or userConfirm.lower() != "n":
            userConfirm = input("Is this the log you want to delete (Y/N): ")
            if userConfirm.lower() == "y":
                sql.delete("log", id)
                print("Log has been deleted successfuly!")
                return
            elif userConfirm.lower() == "n":
                return
            else:
                print("Invalid choice.")
                continue

if __name__ == "__main__":
    main()