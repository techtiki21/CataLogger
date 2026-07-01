from datetime import datetime
import click
import sql
import csv
import os
import analyze
import plotext as plt

# extra functions
def ok(msg):
    """Print a success message in green."""
    click.echo(click.style(msg, fg="green"))

def err(msg):
    """Print an error/failure message in red."""
    click.echo(click.style(msg, fg="red"))

def warn(msg):
    """Print a warning message in yellow."""
    click.echo(click.style(msg, fg="yellow"))

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
    else:
        return None

def catRow(cat):
    """Format a cat row with white labels and blue values."""
    line = click.style(str(cat[0]), fg="blue")
    line += click.style(": | Born: ", fg="white") + click.style(str(cat[1]), fg="blue")
    line += click.style(" | Breed: ", fg="white") + click.style(str(cat[2]), fg="blue")
    line += click.style(" | Entry Created: ", fg="white") + click.style(str(cat[3]), fg="blue")
    line += click.style(" | ID: ", fg="white") + click.style(str(cat[4]), fg="blue")
    return line

def logRow(l, show_name=True):
    """Format a log row with white labels and blue values."""
    line = ""
    if show_name:
        line += click.style("Cat: ", fg="white") + click.style(str(l[8]), fg="blue") + click.style(" | ", fg="white")
    line += click.style("Logged at: ", fg="white") + click.style(str(l[7]), fg="blue")
    line += click.style(" | Weight: ", fg="white") + click.style(f"{l[1]}kg", fg="blue")
    line += click.style(" | Activity: ", fg="white") + click.style(str(l[2]), fg="blue")
    line += click.style(" | Appetite: ", fg="white") + click.style(str(l[3]), fg="blue")
    line += click.style(" | Water: ", fg="white") + click.style(str(l[4]), fg="blue")
    line += click.style(" | Litter: ", fg="white") + click.style(str(l[5]), fg="blue")
    line += click.style(" | ID: ", fg="white") + click.style(str(l[0]), fg="blue")
    return line

def weightAlert(cat_id, threshold=5.0):
    # ai generated func
    weights = sql.weightHistory(cat_id)
    if len(weights) < 2:
        return None
    prev = weights[-2][0]
    latest = weights[-1][0]
    if prev == 0:
        return None
    pct = (latest - prev) / prev * 100
    if abs(pct) >= threshold:
        direction = "gained" if pct > 0 else "lost"
        return f"Weight alert: {direction} {abs(pct):.1f}% since last log ({prev}kg -> {latest}kg)."
    return None


# cli commands
@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """Catalogger: An AI-Powered Cat Health Logger"""
    print("\n")
    sql.initDB()
    if ctx.invoked_subcommand is None:
        ctx.invoke(intro)

@main.command()
def intro():
    """Display a full guide to all commands and their arguments"""
    click.echo(click.style("=" * 50, bold=True))
    click.echo(click.style("  CataLogger - AI-Powered Cat Health Logger", bold=True))
    click.echo(click.style("=" * 50, bold=True))
    click.echo()
    click.echo(click.style("COMMANDS:", bold=True))
    click.echo()

    click.echo(click.style("  add-entry", fg="cyan") + " - Add a new cat to the database")
    click.echo("    --name   (required)  Name of your cat")
    click.echo("    --birth  (required)  Birth date, formatted as YYYY-MM-DD")
    click.echo("    --breed              Breed of your cat")
    click.echo()

    click.echo(click.style("  log", fg="cyan") + " - Log daily health metrics for a cat")
    click.echo("    --cat                Name of the cat to log")
    click.echo("    --weight             Weight in kilograms")
    click.echo("    --activity           Activity level (1-5)")
    click.echo("    --appetite           None, (N)ormal, (L)ow, (H)igh, (N/A)")
    click.echo("    --water              None, (N)ormal, (L)ow, (H)igh, (N/A)")
    click.echo("    --litter             (N)ormal, (S)training, (D)iarrhea, (C)onstipated, (N/A)")
    click.echo("    --notes              Extra notes for the AI to analyze")
    click.echo("    If any argument is not provided, you will be prompted to enter it.")
    click.echo()

    click.echo(click.style("  list-cats", fg="cyan") + " - List all cats in the database")
    click.echo()

    click.echo(click.style("  status", fg="cyan") + " - Show each cat and when they were last logged")
    click.echo()

    click.echo(click.style("  history", fg="cyan") + " - View logged metrics")
    click.echo("    --cat                Show logs for a specific cat (optional)")
    click.echo()

    click.echo(click.style("  graph", fg="cyan") + " - Graph a cat's weight over time")
    click.echo("    --cat    (required)  Name of the cat to graph")
    click.echo()

    click.echo(click.style("  overview", fg="cyan") + " - Get an AI-generated health overview")
    click.echo("    --cat    (required)  Name of the cat to analyze")
    click.echo()

    click.echo(click.style("  delete", fg="cyan") + " - Delete a cat or a log entry")
    click.echo("    --mode   (required)  'cat' or 'log'")
    click.echo("    --id                 ID of the entry to delete (optional, will prompt if not given)")
    click.echo()

    click.echo(click.style("  edit", fg="cyan") + " - Edit a saved cat or a log entry")
    click.echo("    --mode   (required)  'cat' or 'log'")
    click.echo("    --id                 ID of the entry to edit (optional, will prompt if not given)")
    click.echo()

    click.echo(click.style("  export", fg="cyan") + " - Export logged metrics to a CSV file")
    click.echo("    --cat                Cat to export (all cats if omitted)")
    click.echo("    --output             Output file path (default: cat_a_log.csv)")
    click.echo()

    click.echo(click.style("EXAMPLES:", bold=True))
    click.echo()
    click.echo("  python main.py add-entry --name Luna --birth 2020-03-15 --breed Siamese")
    click.echo("  python main.py log --cat Luna --weight 4.2 --activity 3")
    click.echo("  python main.py status")
    click.echo("  python main.py history --cat Luna")
    click.echo("  python main.py graph --cat Luna")
    click.echo("  python main.py overview --cat Luna")
    click.echo("  python main.py delete --mode cat --id 1")
    click.echo("  python main.py edit --mode log --id 5")
    click.echo("  python main.py export --cat Luna --output luna_logs.csv")
    click.echo()
    click.echo(click.style("TIP:", bold=True) + " Run any command with --help for more details.")

@main.command()
@click.option("--name", required=True, help="Name of your cat.")
@click.option("--birth", required=True, help="Formatted as YYYY-MM-DD")
@click.option("--breed", help="Breed of your cat.")
def add_entry(name, birth, breed):
    """Add a new cat to the database"""
    if birth:
        try:
            datetime.strptime(birth, "%Y-%m-%d")
        except ValueError:
            err("Invalid date format. Please use YYYY-MM-DD.")
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
            err("That cat does not exist.")
            cat = None
    while weight == None:
        try:
            weight = float(input("Enter the weight of the cat (kg): "))
        except ValueError:
            err("Must be a number")
            weight = None
    while activity == None:
        try:
            activity = int(input("Rate the activity level of the cat from 1-5: "))
        except ValueError:
            activity = 0
        if activity > 5 or activity < 1:
            err("Bad activity level")
            activity = None
    while appetite == None:
        appetite = input("How much appetite does the cat have; None, (N)ormal, (L)ow, (H)igh, (N/A): ")
        if appetite.upper() not in ("NONE", "N", "L", "H", "N/A", "NA"):
            err("Not a valid appetite type")
            appetite = None
    while water == None:
        water = input("How much water does the cat take; None, (N)ormal, (L)ow, (H)igh, (N/A): ")
        if water.upper() not in ("NONE", "N", "L", "H", "N/A", "NA"):
            err("Not a valid water intake type")
            water = None
    while litter == None:
        litter = input("What's the litter of the cat like; (N)ormal, (S)training, (D)iarrhea, (C)onstipated, (N/A):")
        if litter.upper() not in ("N", "S", "D", "C", "N/A", "NA"):
            err("Not a valid litter type")
            litter = None
    if notes == None:
        notes = input("Any extra notes you would like to add (blank to leave empty): ")

    if activity > 5 or activity < 1:
        err("Bad activity level")
        return
    if sql.fetchCat(cat.lower()) == "NoName":
        err("That cat does not exist.")
        return
    appetite = getFullOption(appetite)
    if appetite == None:
        err("Wrong appetite value.")
        return
    water = getFullOption(water)
    if water == None:
        err("Wrong water intake value.")
        return
    litter = getFullOption(litter)
    if litter == None:
        err("Wrong litter value.")
        return
    
    click.echo(click.style("Cat = ", fg="white") + click.style(str(cat), fg="blue") + click.style(" | ID: ", fg="white") + click.style(str(sql.fetchCat(cat.lower())), fg="blue"))
    click.echo(click.style("Weight = ", fg="white") + click.style(f"{weight}kg", fg="blue"))
    click.echo(click.style("Activity = ", fg="white") + click.style(str(activity), fg="blue"))
    click.echo(click.style("Appetite = ", fg="white") + click.style(str(appetite), fg="blue"))
    click.echo(click.style("Water Intake = ", fg="white") + click.style(str(water), fg="blue"))
    click.echo(click.style("Litter = ", fg="white") + click.style(str(litter), fg="blue"))
    click.echo(click.style("Notes = ", fg="white") + click.style(str(notes), fg="blue"))
    userInput = 'a'
    while True:
        userInput = str(input("Confirm metrics? (y/n): "))
        if userInput.lower() == 'y':
            sql.log(sql.fetchCat(cat.lower()), cat.lower(), weight, activity, appetite, water, litter, notes)
            ok(f"Metrics for {cat} has been logged!")
            alert = weightAlert(sql.fetchCat(cat.lower()))
            if alert:
                warn(alert)
            break
        elif userInput.lower() == 'n':
            break
        else:
            err("Invalid option.")
            continue

@main.command()
def list_cats():
    """List all cats stored in the database"""
    cats = sql.listCats()
    for cat in cats:
        click.echo(catRow(cat))

@main.command()
@click.option("--cat", help="Show metrics of a specific cat.")
def history(cat):
    """Show metrics of all cats or a specific cat"""
    if cat == None:
        log = sql.metricLog(cat)
        print("All saved metrics")
        for l in log:
            click.echo(logRow(l, show_name=True))
    else:
        log = sql.metricLog(cat.lower())
        if log == []:
            err(f"No saved logs for {cat}.")
            return
        print(f"Metrics for {cat}:")
        for l in log:
            click.echo(logRow(l, show_name=False))

@main.command()
@click.option("--cat", required=True, help="Graph the weight of a cat over time")
def graph(cat):
    """Graph the weight of a cat over time"""
    if sql.fetchCat(cat.lower()) == "NoName":
        err("That cat does not exist.")
        return
    log = sql.metricLog(cat.lower())
    dates = []
    weights = []
    for l in log:
        if l[1] is None:
            continue
        weights.append(l[1])
        dates.append(datetime.strptime(l[7], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y"))
    if weights == []:
        err(f"No weights logged for {cat}.")
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
    analyze.aiAnalysis(cat.lower())

@main.command()
@click.option("--mode", type=click.Choice(["cats", "cat", "logs", "log"], case_sensitive=False), required=True, help="Clear an entry from saved cats or a log")
@click.option("--id", type=int, help="ID of the row you want to clear")
def delete(mode, id):
    """Delete a cat entry or remove a log from the database permanently"""
    selectedCat = []
    if mode.lower() == "cat" or mode.lower() == "cats":
        if id == None:
            print("Saved Cats:")
            cats = sql.listCats()
            if cats == []:
                err("No cats to delete.")
                return
            for cat in cats:
                click.echo(catRow(cat))
            print("\n")
            try:
                id = int(input("Select the cat's ID: "))
            except ValueError:
                err("Not an integer.")
                return
        selectedCat = sql.queryCat(id)
        print("\n")
        if selectedCat == []:
            err("No cats match that ID.")
            return
        for cat in selectedCat:
            click.echo(catRow(cat))
        userConfirm = "a"
        while True:
            userConfirm = input("Is this the cat you want to delete? All associated logs will be deleted with it too. (Y/N): ")
            if userConfirm.lower() == "y":
                sql.delete("cats", id)
                ok("Cat and its logs have been deleted successfully!")
                return
            elif userConfirm.lower() == "n":
                 return
            else:
                err("Invalid choice.")
                continue

    if mode.lower() == "log" or mode.lower() == "logs":
        if id == None:
            print("Logged metrics: ")
            logs = sql.metricLog(id)
            if logs == []:
                err("No logs to delete.")
                return
            for l in logs:
                 click.echo(logRow(l, show_name=True))
            print("\n")
            try:
                id = int(input("Select the log ID: "))
            except ValueError:
                err("Not an integer.")
                return
        selectedLog = sql.queryLog(id)
        print("\n")
        if selectedLog == []:
            err("No logs match that ID.")
            return
        for l in selectedLog:
            click.echo(logRow(l, show_name=True))
        userConfirm = "a"
        while True:
            userConfirm = input("Is this the log you want to delete? (Y/N): ")
            if userConfirm.lower() == "y":
                sql.delete("log", id)
                ok("Log has been deleted successfully!")
                return
            elif userConfirm.lower() == "n":
                return
            else:
                err("Invalid choice.")
                continue

@main.command()
@click.option("--mode", type=click.Choice(["cats", "cat", "logs", "log"], case_sensitive=False), required=True, help="Edit an entry from saved cats or a log")
@click.option("--id", type=int, help="ID of the row you want to edit")
def edit(mode, id):
    """Edit information about a saved cat or edit a log"""
    if mode.lower() == "cat" or mode.lower() == "cats":
        if id == None:
            print("Saved Cats:")
            cats = sql.listCats()
            if cats == []:
                err("No cats to edit.")
                return
            for cat in cats:
                click.echo(catRow(cat))
            print("\n")
            try:
                id = int(input("Select the cat's ID: "))
            except ValueError:
                err("Not an integer.")
                return
        selectedCat = sql.queryCat(id)
        print("\n")
        if selectedCat == []:
            err("No cats match that ID.")
            return
        for cat in selectedCat:
            click.echo(catRow(cat))
        userConfirm = "a"
        while True:
            userConfirm = input("Is this the cat you want to edit? (Y/N): ")
            if userConfirm.lower() == "y":
                break
            elif userConfirm.lower() == "n":
                return
            else:
                err("Invalid choice.")
                continue

        field = "a"
        while True:
            field = input("What do you want to edit; (N)ame, (B)irth date, Bre(E)d: ")
            if field.upper() == "N":
                value = input("Enter the new name: ").lower()
                if sql.updateEntry(id, "name", value):
                    ok("Name has been updated successfully!")
                return
            elif field.upper() == "B":
                value = input("Enter the new birth date (YYYY-MM-DD): ")
                try:
                    datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    err("Invalid date format. Please use YYYY-MM-DD.")
                    return
                if sql.updateEntry(id, "birth_date", value):
                    ok("Birth date has been updated successfully!")
                return
            elif field.upper() == "E":
                value = input("Enter the new breed: ")
                if sql.updateEntry(id, "breed", value):
                    ok("Breed has been updated successfully!")
                return
            else:
                err("Invalid choice.")
                continue

    if mode.lower() == "log" or mode.lower() == "logs":
        if id == None:
            print("Logged metrics: ")
            logs = sql.metricLog(id)
            if logs == []:
                err("No logs to edit.")
                return
            for l in logs:
                click.echo(logRow(l, show_name=True))
            print("\n")
            try:
                id = int(input("Select the log ID: "))
            except ValueError:
                err("Not an integer.")
                return
        selectedLog = sql.queryLog(id)
        print("\n")
        if selectedLog == []:
            err("No logs match that ID.")
            return
        for l in selectedLog:
            click.echo(logRow(l, show_name=True))
        userConfirm = "a"
        while True:
            userConfirm = input("Is this the log you want to edit? (Y/N): ")
            if userConfirm.lower() == "y":
                break
            elif userConfirm.lower() == "n":
                return
            else:
                err("Invalid choice.")
                continue

        field = "a"
        while True:
            field = input("What do you want to edit; (W)eight, (A)ctivity, App(E)tite, Wa(T)er, (L)itter, (N)otes: ")
            if field.upper() == "W":
                try:
                    value = float(input("Enter the new weight (kg): "))
                except ValueError:
                    err("Must be a number.")
                    return
                if sql.updateLog(id, "weight_kg", value):
                    ok("Weight has been updated successfully!")
                return
            elif field.upper() == "A":
                try:
                    value = int(input("Enter the new activity level (1-5): "))
                except ValueError:
                    err("Must be a number.")
                    return
                if value > 5 or value < 1:
                    err("Bad activity level.")
                    return
                if sql.updateLog(id, "activity_level", value):
                    ok("Activity level has been updated successfully!")
                return
            elif field.upper() == "E":
                value = getFullOption(input("Enter the new appetite; None, (N)ormal, (L)ow, (H)igh, (N/A): "))
                if value == None or value not in ("None", "Normal", "Low", "High", "N/A"):
                    err("Wrong appetite value.")
                    return
                if sql.updateLog(id, "appetite", value):
                    ok("Appetite has been updated successfully!")
                return
            elif field.upper() == "T":
                value = getFullOption(input("Enter the new water intake; None, (N)ormal, (L)ow, (H)igh, (N/A): "))
                if value == None or value not in ("None", "Normal", "Low", "High", "N/A"):
                    err("Wrong water intake value.")
                    return
                if sql.updateLog(id, "water_intake", value):
                    ok("Water intake has been updated successfully!")
                return
            elif field.upper() == "L":
                value = getFullOption(input("Enter the new litter; (N)ormal, (S)training, (D)iarrhea, (C)onstipated, (N/A): "))
                if value == None or value not in ("Normal", "Straining", "Diarrhea", "Constipated", "N/A"):
                    err("Wrong litter value.")
                    return
                if sql.updateLog(id, "litter", value):
                    ok("Litter has been updated successfully!")
                return
            elif field.upper() == "N":
                value = input("Enter the new notes: ")
                if sql.updateLog(id, "notes", value):
                    ok("Notes have been updated successfully!")
                return
            else:
                err("Invalid choice.")
                continue

@main.command()
@click.option("--cat", help="Which cat data would you like to export")
@click.option("--output", default="cat_a_log.csv", help="Where to export the .csv file")
def export(cat, output):
    """Export logged metrics to a CSV file"""
    if cat is not None:
        if sql.fetchCat(cat.lower()) == "NoName":
            err("That cat does not exist.")
            return
        rows = sql.exportLogs(cat.lower())
    else:
        rows = sql.exportLogs(None)

    if rows == []:
        err("No logs to export.")
        return

    if os.path.exists(output):
        err(f"'{output}' already exists.")
        userConfirm = "a"
        while True:
            userConfirm = input("Overwrite it? (Y/N): ")
            if userConfirm.lower() == "y":
                break
            elif userConfirm.lower() == "n":
                return
            else:
                err("Invalid choice.")
                continue

    headers = ["Cat", "Logged At", "Weight (kg)", "Activity", "Appetite", "Water", "Litter", "Notes"]
    try:
        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
    except OSError as e:
        err(f"Could not write file: ({e})")
        return
    ok(f"Exported {len(rows)} log(s) to {output}")

@main.command()
def status():
    """Show each cat and when they were last logged"""
    cats = sql.catStatus()
    if cats == []:
        err("No cats in the database.")
        return
    for name, breed, last in cats:
        if last == None:
            when = "never logged"
        else:
            days = (datetime.now() - datetime.strptime(last, "%Y-%m-%d %H:%M:%S")).days
            if days == 0:
                when = "today"
            elif days == 1:
                when = "1 day ago"
            else:
                when = f"{days} days ago"
        label = " | " if last == None else " | Last logged "
        click.echo(
            click.style(str(name), fg="blue")
            + click.style(label, fg="white") + click.style(when, fg="blue")
        )

if __name__ == "__main__":
    main()