import discord
from discord.ext import commands,tasks
import requests
import fitz 
import os
from datetime import datetime, timedelta
import asyncio

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
    check_meniu_loop.start()

@bot.event
async def on_message(message):  
    print(f'Mesaj de la {message.author}: {message.content}')
    await bot.process_commands(message)

current_date = datetime.now()
formatted_date = current_date.strftime("%d.%m.%Y") 
cantina_role_id=1305831673539203082
channel_id = 1303476282813841498
already_sent_today = False

@tasks.loop(minutes=1)  # Verifică la fiecare 1 minut
async def check_meniu_loop():
    global already_sent_today
    current_date = datetime.now().strftime("%d.%m.%Y")
    now = datetime.now()

    # Resetează variabila la ora 00:00 în fiecare zi
    if now.hour == 0 and now.minute == 0:
        already_sent_today = False

    # Verifică dacă meniul nu a fost deja trimis astăzi
    if not already_sent_today and link_exista(meniuGauURL+formatted_date + '.pdf'):
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send("🥗🍗 Meniul de azi este disponibil!", delete_after=5)
            screenshot_paths = take_screenshots_from_pdf(meniuGauURL+formatted_date + '.pdf')
            if screenshot_paths:
                for path in screenshot_paths:
                    await channel.send(file=discord.File(path))
                    os.remove(path)
                await channel.send(f"<@&{cantina_role_id}>")
                already_sent_today = True  # Setează variabila pentru a evita retrimiterea
            else:
                await channel.send("⚠️ Eroare: Nu am putut genera screenshot-urile.", delete_after=5)
        else:
            print("⚠️ Eroare: Canalul nu a fost găsit.")


@bot.command(name='meniu')
async def meniu(ctx, option=None):
   # if ctx.author.name == "logicavietii":
      #  await ctx.send(f"{ctx.author.mention}, din fericire tu nu ai drepturi")
     #   return  

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

    elif option=='test':
        test_url='https://www.cnmc.org.nz/resources/images/publication/test-image.pdf'
        screenshot_paths = take_screenshots_from_pdf(test_url)
        if screenshot_paths:
            for path in screenshot_paths:
                await ctx.send(file=discord.File(path),delete_after=10)
                os.remove(path) 
        else:
            await ctx.send("Eroare: Nu am putut genera screenshot-urile.",delete_after=5)

    elif option == "lgau":
        day = 1  
        max_days = 5  
        last_date = datetime.now() - timedelta(days=day)

        
        while not link_exista(meniuGauURL + last_date.strftime("%d.%m.%Y") + '.pdf') and day < max_days:
            day += 1
            last_date = datetime.now() - timedelta(days=day)

        fo_date = last_date.strftime("%d.%m.%Y")

        if day == max_days:  #
            await ctx.send("Eroare", delete_after=5)
            return

        pdf_url = meniuGauURL + fo_date + '.pdf'
        screenshot_paths = take_screenshots_from_pdf(pdf_url)

        if screenshot_paths:
            for path in screenshot_paths:
                await ctx.send(file=discord.File(path))
                os.remove(path)
        else:
            await ctx.send("Eroare: Nu am putut genera screenshot-urile.", delete_after=5)


    elif option == "r":
       already_sent_today=False
       await ctx.send(f'{already_sent_today}', delete_after=5)

    else:
        await ctx.send('Comanda nu este validă!',delete_after=5)


def link_exista(url):
    try:
        response = requests.head(url, timeout=10)
        if response.status_code == 200:
            return True
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
