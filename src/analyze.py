from groq import Groq, AuthenticationError
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import os
import sys
import sql
import click

# Load .env from next to the executable when frozen (PyInstaller), otherwise
# fall back to the normal upward search from the current directory.
if getattr(sys, "frozen", False):
    load_dotenv(Path(sys.executable).parent / ".env")
else:
    load_dotenv()


def err(msg):
    """Print an error/failure message in red."""
    click.echo(click.style(msg, fg="red"))


def calcAge(birth_date):
    """Return the cat's age in years from a YYYY-MM-DD string, or None."""
    if not birth_date:
        return None
    try:
        birth = datetime.strptime(birth_date, "%Y-%m-%d")
    except ValueError:
        return None
    today = datetime.now()
    years = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    return years


def aiAnalysis(cat_name):
    if not os.getenv("API_KEY"):
        err("No API key found. Add API_KEY to your .env file.")
        return
    cat_id = sql.fetchCat(cat_name)
    if cat_id == "NoName":
        err("This cat does not exist. Check for any misspellings.")
        return

    profile = sql.queryCat(cat_id)[0]
    birth_date = profile[1]
    breed = profile[2]
    age = calcAge(birth_date)

    profile_text = f"Name: {cat_name}\n"
    profile_text += f"Breed: {breed if breed else 'Unknown'}\n"
    profile_text += f"Birth date: {birth_date if birth_date else 'Unknown'}\n"
    profile_text += f"Age: {age} years\n" if age is not None else "Age: Unknown\n"

    logs = sql.AIfetchLogs(cat_id)

    log_text = "Weight | Activity | Appetite | Water | Litter | Notes\n"
    for row in logs:
        log_text += " | ".join(str(v) for v in row) + "\n"

    user_content = (
        f"Here is the profile and health data for {cat_name}:\n\n"
        f"{profile_text}\n{log_text}\n"
        "Provide a health overview, taking the cat's breed and age into account "
        "(e.g. breed-typical weight ranges and age-related considerations)."
    )

    try:
        client = Groq(api_key=os.getenv("API_KEY"))
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
            {
                "role": "system",
                "content": "You are a cat health assistant. You analyze health and behavior logs for cats and provide brief, clear overviews to their owners.\n\nGiven a cat's profile (name, breed, age) and logged metrics (weight, activity level 1-5, appetite, water intake, litter status, and notes), you should:\n- Summarize the cat's current condition\n- Identify trends (weight gain/loss, activity changes, appetite shifts)\n- Consider the cat's breed and age when assessing weight and activity (breed-typical ranges and age-related needs)\n- Flag any concerns that may warrant a vet visit\n- Keep your tone friendly and concise\n\nYou are not a veterinarian. If something looks concerning, advise the owner to consult a vet rather than diagnosing. Don't include markup characters in your response for no formatting, just plain text and lists."
            },
            {
                "role": "user",
                "content": user_content
            }
            ],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=True,
            stop=None
        )

        for chunk in completion:
            print(chunk.choices[0].delta.content or "", end="")
        print("\n")
    except AuthenticationError:
        err("Invalid Groq API Key. Make sure it's correct and not expired.")
        return
    except Exception as e:
        err(f"Could not get an AI overview right now: ({e})")
        return