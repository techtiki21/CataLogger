from groq import Groq, AuthenticationError
from dotenv import load_dotenv
import os
import sql

load_dotenv()

def aiAnalysis(cat_name):
    if not os.getenv("API_KEY"):
        print("No API key found. Add API_KEY to your .env file.")
        return
    cat_id = sql.fetchCat(cat_name)
    if cat_id == "NoName":
        print("This cat does not exist. Check for any misspellings.")
        return
    
    logs = sql.AIfetchLogs(cat_id)

    log_text = "Weight | Activity | Appetite | Water | Litter | Notes\n"
    for row in logs:
        log_text += " | ".join(str(v) for v in row) + "\n"

    user_content = f"Here is the health data for {cat_name}:\n\n{log_text}\nProvide a health overview."

    try:
        client = Groq(api_key=os.getenv("API_KEY"))
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
            {
                "role": "system",
                "content": "You are a cat health assistant. You analyze health and behavior logs for cats and provide brief, clear overviews to their owners.\n\nGiven a cat's profile and logged metrics (weight, activity level 1-5, appetite, water intake, litter status, and notes), you should:\n- Summarize the cat's current condition\n- Identify trends (weight gain/loss, activity changes, appetite shifts)\n- Flag any concerns that may warrant a vet visit\n- Keep your tone friendly and concise\n\nYou are not a veterinarian. If something looks concerning, advise the owner to consult a vet rather than diagnosing. Don't include markup characters in your response for no formatting, just plain text and lists."
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
    except AuthenticationError:
        print("Invalid Groq API Key. Make sure it's correct and not expired.")
        return