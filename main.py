import os
import discord
from groq import Groq
from dotenv import load_dotenv

# 1. Load local .env file if present
load_dotenv()

# 2. Variable Resolution (Handles Wispbyte/Pterodactyl environment quirks)
groq_key = (
    os.environ.get("GROQ_API_KEY") 
    or os.environ.get("ENV_GROQ_API_KEY") 
    or os.environ.get("P_SERVER_GROQ_API_KEY")
)

discord_token = (
    os.environ.get("DISCORD_TOKEN") 
    or os.environ.get("ENV_DISCORD_TOKEN") 
    or os.environ.get("P_SERVER_DISCORD_TOKEN")
)

# Debug status on startup
print("==========================================")
print(f"[Check] Groq API Key Found: {bool(groq_key)}")
print(f"[Check] Discord Token Found: {bool(discord_token)}")
print("==========================================")

if not groq_key:
    raise ValueError("GROQ_API_KEY is missing! Please set it in your panel or .env file.")

if not discord_token:
    raise ValueError("DISCORD_TOKEN is missing! Please set it in your panel or .env file.")

# 3. Client Initialization
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
groq_client = Groq(api_key=groq_key)


@client.event
async def on_ready():
    print(f"Symp is online and logged in as {client.user}")
    print("==========================================")


@client.event
async def on_message(message):
    # Ignore self-messages
    if message.author == client.user:
        return

    # Handle command
    if message.content.startswith("!symp"):
        user_input = message.content[5:].strip()

        if not user_input:
            await message.channel.send("I'm here for you. Tell me what's on your mind!")
            return

        async with message.channel.typing():
            try:
                # Call Groq API with openai/gpt-oss-120b
                response = groq_client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are Symp, an empathetic, warm, and supportive AI therapy assistant. "
                                "Provide thoughtful, comforting, and helpful advice while maintaining a conversational tone."
                            ),
                        },
                        {"role": "user", "content": user_input},
                    ],
                    temperature=1,
                    max_completion_tokens=2048,
                    top_p=1,
                    stream=False,  # Essential for Discord bots
                )

                bot_reply = response.choices[0].message.content

                if not bot_reply:
                    await message.channel.send("I couldn't generate a response. Please try asking again.")
                    return

                # Discord 2000-character safety splitter
                if len(bot_reply) > 2000:
                    for i in range(0, len(bot_reply), 2000):
                        await message.channel.send(bot_reply[i : i + 2000])
                else:
                    await message.channel.send(bot_reply)

            except Exception as e:
                print(f"[Execution Error]: {e}")
                await message.channel.send(f"An error occurred: `{e}`")


# Launch the Bot
client.run(discord_token)
