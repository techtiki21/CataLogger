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
    elif letter.upper() == "N":
        return "Normal"
    elif letter.upper() == "H":
        return "High"
    elif letter.upper() == "S":
        return "Straining"
    elif letter.upper() == "D":
        return "Diarrhea"
    if letter.upper() == "C":
        return "Constipated"


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
    sql.addEntry(name, birth, breed)

@main.command()
@click.option("--cat", help="Name or ID of the cat you want to log.")
@click.option("--weight", help="Weight of the cat in kilograms.")
@click.option("--activity", type=int, help="How active your cat is on a scale of 1-5.")
@click.option("--appetite", help="None, (N)ormal, (L)ow, (H)igh")
@click.option("--water", help="None, (N)ormal, (L)ow, (H)igh")
@click.option("--litter", help="(N)ormal, (S)training, (D)iarrhea, (C)onstipated")
@click.option("--notes", help="Extra notes the AI can use to better its understanding of the cat.")
def log(cat, weight, activity, appetite, water, litter, notes):
    """Log metrics of a saved cat"""
    if cat == None:
        cat = input("Enter the name of the cat: ")
    if weight == None:
        weight = input("Enter the weight of the cat (kg): ")
    if activity == None:
        activity = int(input("Rate the activity level of the cat from 1-5: "))
    if appetite == None:
        appetite = input("How much appetite does the cat have; None, (N)ormal, (L)ow, (H)igh: ")
    if water == None:
        water = input("How much water does the cat take; None, (N)ormal, (L)ow, (H)igh: ")
    if litter == None:
        litter = input("What's the litter of the cat like; (N)ormal, (S)training, (D)iarrhea, (C)onstipated:")
    if notes == None:
        notes = input("Any extra notes you would like to add: ")

    if activity > 5 or activity < 1:
        print("Bad activity level")
        return
    appetite = getFullOption(appetite)
    water = getFullOption(water)
    litter = getFullOption(litter)
    
    print(f"Cat = {cat}/{sql.fetchCat(cat)}")
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
            sql.log(sql.fetchCat(cat), cat, weight, activity, appetite, water, litter, notes)
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
        print(f"{cat[0]}: | Born: {cat[1]} | Breed: {cat[2]} | Entry Created: {cat[3]}")

@main.command()
@click.option("--cat", required=True, help="Show metrics of a specific cat.")
def history(cat):
    """"Show metrics of a specific cat."""
    log = sql.metricLog(cat)
    print(f"Metrics for {cat}:")
    for l in log:
        print(f"Logged at: {l[7]} | Weight: {l[1]}kg | Activity: {l[2]} | Appetite: {l[3]} | Water: {l[4]} | Litter: {l[5]} | ID: {l[0]}")

@main.command()
@click.option("--cat", required=True, help="Graph the weight of a cat over time")
def graph(cat):
    """Graph the weight of a cat over time"""
    log = sql.metricLog(cat)
    weights = []
    for weight in log:
        weights.append(weight[1])
    plt.plot(weights)
    plt.title(f"{cat}'s Weight Over Time")
    plt.ylabel("kg")
    plt.show()

@main.command()
@click.option("--cat", required=True, help="Name of the cat to analyze.")
def overview(cat):
    """Use AI to provide a health overview of a specific cat"""
    analyze.aiAnalysis(cat)


if __name__ == "__main__":
    main()