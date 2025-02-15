import discord
from discord.ext import commands
import requests
import fitz 
import os
from datetime import datetime


# Token-ul bot-ului (înlocuiește cu token-ul tău)
TOKEN = 'MTMzOTk0NjM3NTQ0NTc0NTc3Ng.G9kqir.yeKY4g-8Fw9ifaBnkR44a55yRdxpouFBfpLvxQ'

# Creează bot-ul
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)
meniuGauURL='https://www.uaic.ro/wp-content/uploads/2025/02/Meniu-site-GAU-'


@bot.event
async def on_ready():
    print(f'Bot-ul este conectat ca {bot.user}')

@bot.event
async def on_message(message):  
    print(f'Mesaj de la {message.author}: {message.content}')
    await bot.process_commands(message)

current_date = datetime.now()
formatted_date = current_date.strftime("%d.%m.%Y") 
cantina_role_id=1305831673539203082
@bot.command(name='meniu')
async def meniu(ctx, option=None):
    if ctx.author.name == "logicavietii":
        await ctx.send(f"{ctx.author.mention}, din fericire tu nu ai drepturi")
        return  

    await ctx.message.delete()
    if option == 'gau': 
        if not link_exista(meniuGauURL+formatted_date + '.pdf'):
            await ctx.send("Eroare: Fișierul PDF nu există!", delete_after=5)
            return
        
        await ctx.send("Îți trimit un screenshot ... Așteaptă un moment!", delete_after=5)
        screenshot_paths = take_screenshots_from_pdf(meniuGauURL+formatted_date + '.pdf')
        if screenshot_paths:
            for path in screenshot_paths:
                await ctx.send(file=discord.File(path))
                os.remove(path)  
            await ctx.send(f"<@&{cantina_role_id}>" )
        else:
            await ctx.send("Eroare: Nu am putut genera screenshot-urile.",delete_after=5)
    else:
        await ctx.send('Comanda nu este validă!',delete_after=5)
        
def link_exista(url):
    try:
        response = requests.head(url, timeout=10)
        if response.status_code == 200:
            return True  # Link valid
        elif response.status_code == 404:
            print("⚠️ Linkul nu există (404)")
            return False  # Link invalid
        else:
            print(f"⚠️ Serverul a răspuns cu codul {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Eroare la verificarea linkului: {e}")
        return False

def take_screenshots_from_pdf(pdf_url):
    try:
        response = requests.get(pdf_url, timeout=200)
        response.raise_for_status()
        pdf_path = 'meniu.pdf'

        with open(pdf_path, 'wb') as f:
            f.write(response.content)

        doc = fitz.open(pdf_path)
        screenshot_paths = []

        for page_num in range(len(doc)):  # Iterăm prin toate paginile
            page = doc[page_num]
            pix = page.get_pixmap()
            screenshot_path = f'screenshot_{page_num + 1}.png'
            pix.save(screenshot_path)
            screenshot_paths.append(screenshot_path)

        doc.close()
        os.remove(pdf_path)  # Ștergem PDF-ul după conversie

        return screenshot_paths if screenshot_paths else None

    except requests.exceptions.Timeout:
        print("Cererea a expirat din cauza unui timeout.")
    except requests.exceptions.RequestException as e:
        print(f"A apărut o eroare la descărcarea PDF-ului: {e}")
    except Exception as e:
        print(f"Eroare neașteptată: {e}")

bot.run(TOKEN)