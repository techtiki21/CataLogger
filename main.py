import click
import sqlite3

@click.command()
@click.argument('type')
def main(type):
    if type == "full":
        print("Full logging")
    elif type == "selective":
        print("Selective logging")
    else:
        print("Invalid logging type")


if __name__ == "__main__":
    main()