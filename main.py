import click
import sql

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
    print(f"{name} added to database successfuly!")

@main.command()
@click.option("--cat", required=True, help="Name or ID of the cat you want to log.")
@click.option("--weight", help="Weight of the cat in kilograms.")
@click.option("--activity", type=int, help="How active your cat is on a scale of 1-5.")
@click.option("--appetite", help="None, (N)ormal, (L)ow, (H)igh")
@click.option("--water", help="None, (N)ormal, (L)ow, (H)igh")
@click.option("--litter", help="(N)ormal, (S)training, (D)iarrhea, (C)onstipated")
@click.option("--notes", help="Extra notes the AI can use to better its understanding of the cat.")
def log(cat, weight, activity, appetite, water, litter, notes):
    """Log metrics of a saved cat"""
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


if __name__ == "__main__":
    main()