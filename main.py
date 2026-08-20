import os
import discord
from groq import Groq

client = discord.Client(intents=discord.Intents.default())
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@client.event
async def on_ready():
    print(f'Symp is logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!symp'):
        user_input = message.content[6:].strip()
        
        if not user_input:
            await message.channel.send("I'm here for you. Tell me what's on your mind!")
            return

        async with message.channel.typing():
            try:
                # Configured for gpt-oss-120b without streaming
                response = groq_client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {"role": "system", "content": "You are Symp, an empathetic, warm, and supportive AI therapy assistant."},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=1,
                    max_completion_tokens=2048,
                    top_p=1,
                    stream=False  # Must be False for Discord bots!
                )
                
                bot_reply = response.choices[0].message.content
                
                # Discord has a 2000 character limit per message
                if len(bot_reply) > 2000:
                    for i in range(0, len(bot_reply), 2000):
                        await message.channel.send(bot_reply[i:i+2000])
                else:
                    await message.channel.send(bot_reply)

            except Exception as e:
                print(f"Error handling !symp command: {e}")
                await message.channel.send(f"Error: {e}")

client.run(os.environ.get("DISCORD_TOKEN"))
