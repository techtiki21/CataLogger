import click
import sql

@click.group()
def main():
    """Catalogger: An AI-Powered Cat Health Logger"""
    sql.initDB()
    pass

@main.command()
@click.option("--name", required=True, help="Name of your cat")
@click.option("--birth", help="Formatted as YYYY-MM-DD")
@click.option("--breed", help="Breed of your cat")
def add_entry(name, birth, breed):
    """Add a new cat to the database"""
    sql.addEntry(name, birth, breed)
    print(f"{name} added to database successfuly!")


if __name__ == "__main__":
    main()