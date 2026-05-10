import os
from groq import Groq


def get_coach_response(user, goals, chat_history, user_message):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    goals_summary = "\n".join([
        f"- {g.name}: ₦{g.current_amount:,.0f} saved out of ₦{g.target_amount:,.0f} target ({round((g.current_amount / g.target_amount) * 100, 1) if g.target_amount > 0 else 0}% complete)"
        for g in goals
    ])

    system_prompt = f"""You are StackSmart AI, a friendly and practical financial coach for Nigerian youth.
You speak in a warm, encouraging tone — like a knowledgeable friend, not a bank.

Here is the user's current financial profile:
- Name: {user.name}
- Income range: {user.income_range or 'Not specified'}
- Spending habit: {user.spending_habit or 'Not specified'}

Their active savings goals:
{goals_summary if goals_summary else 'No goals created yet'}

Your job is to:
- Give specific, actionable advice based on their actual data
- Encourage them when they're making progress
- Suggest realistic saving strategies for the Nigerian context
- Keep responses concise and conversational
- Use Naira (₦) for all amounts
- Never give generic advice — always reference their specific goals and numbers"""

    messages = [{"role": "system", "content": system_prompt}]

    for msg in chat_history[-10:]:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=1000
    )

    return response.choices[0].message.content