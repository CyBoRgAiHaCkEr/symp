import os
import discord
from discord.ext import commands
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Bot & Groq Client
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Groq automatically picks up the GROQ_API_KEY environment variable
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

user_data = {}

BADGES = [
    (100, "Absolute Happy"),
    (50, "Happy-Meister"),
    (20, "Joy Sprout"),
    (5, "Warm Smile")
]

def get_badge(points):
    for threshold, badge_name in BADGES:
        if points >= threshold:
            return badge_name
    return "Beginner Seeker"

async def analyze_and_respond(user_message):
    prompt = f"""
    You are Symp, an empathetic, warm, and supportive AI therapy assistant. 
    Analyze the user's situation below, provide customized advice, and rate their potential positivity shift.

    User says: "{user_message}"

    Respond in EXACTLY this format (do not add extra text or sections):
    ADVICE: <Your dynamic, personalized, compassionate response in 2-3 sentences max>
    POINTS: <An integer between 5 and 15 based on how deeply they opened up or sought help>
    """
    
    # Process text using Groq's fast Llama 3 model
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    text = response.choices[0].message.content
    
    advice, points = "I'm here for you. Tell me more about what's going on.", 5
    for line in text.split("\n"):
        if line.startswith("ADVICE:"):
            advice = line.replace("ADVICE:", "").strip()
        elif line.startswith("POINTS:"):
            try:
                points = int(line.replace("POINTS:", "").strip())
            except ValueError:
                points = 10
                
    return advice, points

@bot.event
async def on_ready():
    print(f"Symp (Groq-Powered) is online as {bot.user}")

@bot.command(name="symp")
async def symp(ctx, *, user_input: str = None):
    if not user_input:
        await ctx.send(f"Hello {ctx.author.mention}, I'm **Symp**. Tell me how you're feeling today! Usage: `!symp [your problem]`")
        return

    async with ctx.typing():
        user_id = ctx.author.id
        if user_id not in user_data:
            user_data[user_id] = {"points": 0}

        # Analyze problem live with Groq
        advice, earned_points = await analyze_and_respond(user_input)

        user_data[user_id]["points"] += earned_points
        total_points = user_data[user_id]["points"]
        current_badge = get_badge(total_points)

        embed = discord.Embed(
            title="🌿 Symp Therapy Support",
            description=advice,
            color=discord.Color.teal()
        )
        embed.add_field(name="✨ Happiness Points Earned", value=f"+{earned_points} pts", inline=True)
        embed.add_field(name="🌟 Total Points", value=f"{total_points} pts", inline=True)
        embed.add_field(name="🏅 Badge Earned", value=f"**{current_badge}**", inline=False)
        embed.set_footer(text="Symp provides supportive guidance, not professional medical advice.")

        await ctx.send(embed=embed)

@bot.command(name="profile")
async def profile(ctx):
    user_id = ctx.author.id
    if user_id not in user_data:
        user_data[user_id] = {"points": 0}
    
    total_points = user_data[user_id]["points"]
    current_badge = get_badge(total_points)

    embed = discord.Embed(title=f"🌸 {ctx.author.name}'s Happiness Profile", color=discord.Color.gold())
    embed.add_field(name="Total Happiness Points", value=str(total_points), inline=True)
    embed.add_field(name="Current Badge", value=f"**{current_badge}**", inline=True)
    
    await ctx.send(embed=embed)

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
