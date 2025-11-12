import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk, ImageEnhance
from PIL import Image, ImageTk
from PIL import ImageEnhance
import pygame
import random
import sys
import os

# --- Helper for PyInstaller ---
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# --- Audio setup ---
pygame.mixer.init()
pygame.mixer.music.load(resource_path("audio/menusong.mp3"))
pygame.mixer.music.play(loops=-1)

start_sfx = pygame.mixer.Sound(resource_path("audio/mg.wav"))
btn_sfx = pygame.mixer.Sound(resource_path("audio/click.mp3"))
count_sfx = pygame.mixer.Sound(resource_path("audio/countdown.mp3"))
fight_sfx = pygame.mixer.Sound(resource_path("audio/click.mp3"))
win_sfx = pygame.mixer.Sound(resource_path("audio/win.mp3"))
lose_sfx = pygame.mixer.Sound(resource_path("audio/lose.mp3"))
draw_sfx = pygame.mixer.Sound(resource_path("audio/draw.mp3"))
winsound_sfx = pygame.mixer.Sound(resource_path("audio/winsound.mp3"))
losesound_sfx = pygame.mixer.Sound(resource_path("audio/losesound.mp3"))
pause_sfx = pygame.mixer.Sound(resource_path("audio/pause.mp3"))
coin_sfx = pygame.mixer.Sound(resource_path("audio/coins.mp3"))

choice_sfx = {
    "rock": pygame.mixer.Sound(resource_path("audio/rock.wav")),
    "paper": pygame.mixer.Sound(resource_path("audio/paper.wav")),
    "scissors": pygame.mixer.Sound(resource_path("audio/scissors.wav"))
}

# --- Tk setup ---
window = tk.Tk()
window.geometry("800x600")
window.resizable(False, False)
window.title("Rock Paper Scissors")

try:
    window.iconbitmap(resource_path("favicon.ico"))
except Exception as e:
    print("Icon load failed:", e)

main_menu = tk.Frame(window)
game_page = tk.Frame(window)
win_screen = tk.Frame(window, bg="black")
lose_screen = tk.Frame(window, bg="black")
for frame in (main_menu, game_page, win_screen, lose_screen):
    frame.place(x=0, y=0, relwidth=1, relheight=1)

# --- Pause system variables ---
is_paused = False
pause_overlay = None
pause_text_id = None
pause_menu_btn = None

# --- Menu background ---
bg_image = Image.open(resource_path("imgs/menu.png"))
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(main_menu, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)


player_lowhp_overlay = None
player_lowhp_pulsing = False



overlay = tk.Frame(main_menu, bg="black")
overlay.place(x=0, y=0, relwidth=1, relheight=1)

# --- Win / Lose Screens ---
def setup_end_screen(frame, text, bg_color):
    label = tk.Label(frame, text=text, font=("Pixel game", 40), fg="white", bg=bg_color)
    label.place(relx=0.5, rely=0.4, anchor="center")

    btn = tk.Button(frame, text="MAIN MENU", font=("Pixel game", 28),
                    bg="#136bae", fg="#FFE5A1", width=12, relief="raised",
                    command=lambda: return_to_menu())
    btn.place(relx=0.5, rely=0.6, anchor="center")

    def on_enter(e):
        btn.config(bg="#1e79c6")
    def on_leave(e):
        btn.config(bg="#136bae")
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

setup_end_screen(win_screen, "YOU WIN!", "#1a7431")
setup_end_screen(lose_screen, "YOU LOSE!", "#8c1c13")

# --- Start button ---
startBtn = tk.Button(main_menu, text="START", font=("Pixel game", 30),
                     width=14, bg="#136bae", fg="#FFE5A1", relief="raised")
startBtn.place(x=-300, y=500)

def on_start_enter(e):
    startBtn.config(bg="#1e79c6")
def on_start_leave(e):
    startBtn.config(bg="#136bae")
startBtn.bind("<Enter>", on_start_enter)
startBtn.bind("<Leave>", on_start_leave)

def go_to_game():
    global player_hp, npc_hp
    player_hp = 3
    npc_hp = 3
    btn_sfx.play()
    pygame.mixer.music.fadeout(1000)
    game_page.tkraise()
    window.after(800, start_game_music)
startBtn.config(command=go_to_game)

def start_game_music():
    try:
        pygame.mixer.music.load(resource_path("audio/gamesong.mp3"))
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(loops=-1)
    except Exception:
        pass

def slide_animation(x=-300):
    if x >= 260:
        startBtn.place(x=260, y=500)
        return
    startBtn.place(x=x, y=500)
    window.after(10, slide_animation, x + 10)

def create_shop_button():
    global shopBtn
    shopBtn = tk.Button(main_menu, text="SHOP", font=("Pixel game", 30),
                        width=14, bg="#136bae", fg="#FFE5A1", relief="raised",
                        command=lambda: shop_page.tkraise())
    shopBtn.place(x=260, y=420)  # above Start button
    shopBtn.bind("<Enter>", lambda e: shopBtn.config(bg="#1e79c6"))
    shopBtn.bind("<Leave>", lambda e: shopBtn.config(bg="#136bae"))





# --- Fade in w/ "Made by Luka" ---
def fade_step(alpha):
    if alpha <= 0:
        overlay.destroy()
        create_shop_button()
        if hasattr(main_menu, "made_by_label"):
            main_menu.made_by_label.destroy()
        slide_animation()
        start_sfx.play()
        return
    hex_color = f'#{alpha:02x}{alpha:02x}{alpha:02x}'
    overlay.config(bg=hex_color)
    if not hasattr(main_menu, "made_by_label"):
        main_menu.made_by_label = tk.Label(main_menu, text="Made by Luka",
                                           font=("Pixel game", 24), fg="white", bg="#000000")
        main_menu.made_by_label.place(relx=0.5, rely=0.5, anchor="center")
    window.after(30, fade_step, alpha - 5)
fade_step(255)

# --- Game state ---
wins, losses, draws = 0, 0, 0
choices = ["rock", "paper", "scissors"]
game_active = False
game_over_active = False

# --- Pause state ---
game_paused = False
pause_overlay = None
pause_btn = None
pause_photo = None

# --- Health System ---
player_hp = 3
npc_hp = 3
hp_img_size = (160, 48)
hp_images = {
    1: ImageTk.PhotoImage(Image.open(resource_path("imgs/1hp.png")).resize(hp_img_size)),
    2: ImageTk.PhotoImage(Image.open(resource_path("imgs/2hp.png")).resize(hp_img_size)),
    3: ImageTk.PhotoImage(Image.open(resource_path("imgs/3hp.png")).resize(hp_img_size))
}
player_hp_display = None
npc_hp_display = None

# --- Game canvas ---
game_bg_image = Image.open(resource_path("imgs/gamebg.png")).resize((800, 600))
game_bg_photo = ImageTk.PhotoImage(game_bg_image)
canvas = tk.Canvas(game_page, width=800, height=600, highlightthickness=0)
canvas.pack(fill="both", expand=True)
canvas_bg = canvas.create_image(400, 300, image=game_bg_photo)
score_text_id = canvas.create_text(400, 28, text="Wins: 0  Losses: 0  Draws: 0",
                                   font=("Pixel game", 16), fill="white")


# --- Load images ---
img_size = (120, 120)
player_imgs = {c: ImageTk.PhotoImage(Image.open(resource_path(f"imgs/{c}.png")).resize(img_size)) for c in choices}
npc_imgs = {c: ImageTk.PhotoImage(Image.open(resource_path(f"imgs/{c}.png")).resize(img_size).rotate(180)) for c in choices}
base_player_imgs = player_imgs.copy()
base_npc_imgs = npc_imgs.copy()

# --- Positions ---
center_x = 400
spacing = 190
npc_positions = {"rock": (center_x - spacing, 130), "paper": (center_x, 130), "scissors": (center_x + spacing, 130)}
player_positions = {"rock": (center_x - spacing, 470), "paper": (center_x, 470), "scissors": (center_x + spacing, 470)}
npc_labels = {c: canvas.create_image(x, y, image=npc_imgs[c]) for c, (x, y) in npc_positions.items()}
player_labels = {c: canvas.create_image(x, y, image=player_imgs[c]) for c, (x, y) in player_positions.items()}
countdown_text = canvas.create_text(center_x, 300, text="", font=("Pixel game", 50), fill="white")



# -------------------- COIN / SAVE SYSTEM --------------------
import json

# Save file location (cross-platform; safe for PyInstaller too)
# We save to the user's home directory (not _MEIPASS, which is read-only when frozen).
_SAVE_FILENAME = os.path.join(os.path.expanduser("~"), ".rps_save.json")

# coins variable already exists in your code — if not, it will be created here
try:
    coins  # preserve if already defined in your code above
except NameError:
    coins = 0

# Save file location (already exists)
_SAVE_FILENAME = os.path.join(os.path.expanduser("~"), ".rps_save.json")




def load_save():
    """Load saved data (coins and equipped skin)."""
    global coins, equipped_skin, owned_skins
    try:
        if os.path.exists(_SAVE_FILENAME):
            with open(_SAVE_FILENAME, "r", encoding="utf-8") as f:
                data = json.load(f)
            coins = int(data.get("coins", 0))
            equipped_skin = data.get("equipped_skin", "Default Skin")
            owned_skins = set(data.get("owned_skins", ["Default Skin"]))
        else:
            coins = 0
            equipped_skin = "Default Skin"
            owned_skins = {"Default Skin"}
    except Exception as e:
        print("Load save failed:", e)
        coins = 0
        equipped_skin = "Default Skin"
        owned_skins = {"Default Skin"}

def save_data():
    """Save coins and equipped skin."""
    data = {
        "coins": int(coins),
        "equipped_skin": equipped_skin,
        "owned_skins": list(owned_skins)
    }
    try:
        with open(_SAVE_FILENAME, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as e:
        print("Save failed:", e)


# Create coin UI elements on the canvas.
coin_img_path = resource_path("imgs/coin.png")

# resize coin to a nice small icon (~28×28)
try:
    coin_pil = Image.open(coin_img_path).resize((100, 80), Image.LANCZOS)
    coin_img = ImageTk.PhotoImage(coin_pil)
except Exception:
    coin_img = tk.PhotoImage(width=28, height=28)  # fallback blank

# draw icon + text close together (top-left corner)
coin_image_id = canvas.create_image(20, 26, image=coin_img, anchor="center")
coin_text_id = canvas.create_text(55, 26, text="x 0",
                                  font=("Pixel game", 20),
                                  fill="white",
                                  anchor="w")

def update_coin_display():
    """Refresh canvas coin text."""
    canvas.itemconfig(coin_text_id, text=f"x {coins}")

def add_coins(n):
    """Add coins, save, play sound, and refresh all displays."""
    global coins
    if n <= 0:
        return
    coins += int(n)
    save_data()
    update_all_coin_displays()  # <-- refresh both displays
    try:
        coin_sfx.play()
    except:
        pass


    # Simple pulse effect
    def pulse(steps=5, growing=True):
        global coin_image_id  # <--- need this here too
        if steps <= 0:
            canvas.coords(coin_image_id, 20, 26)  # reset position
            return

        offset = -5 if growing else 5
        canvas.move(coin_image_id, 0, offset)
        window.after(50, lambda: pulse(steps-1, not growing))

    pulse()




def spend_coins(n):
    """Attempt to spend coins, return True if successful."""
    global coins
    if n <= 0:
        return True
    if coins >= n:
        coins -= int(n)
        update_coin_display()
        save_data()
        return True
    return False

def on_win(award=100):
    """Call this when the player wins a round."""
    add_coins(award)

# Load saved coins immediately and update UI
load_save()
update_coin_display()
# ------------------ END COIN / SAVE SYSTEM ------------------






















# --- SHOP FRAME SETUP ---
shop_page = tk.Frame(window, bg="#222222")
shop_page.place(x=0, y=0, relwidth=1, relheight=1)  # full screen, like other pages






# Shop title
shop_title = tk.Label(shop_page, text="SHOP", font=("Pixel game", 40), fg="white", bg="#222222")
shop_title.place(relx=0.5, y=80, anchor="center")

# Back button
back_btn = tk.Button(shop_page, text="BACK", font=("Pixel game", 28),
                     bg="#136bae", fg="#FFE5A1", width=12, relief="raised",
                     command=lambda: main_menu.tkraise())  # go back to main menu
back_btn.place(relx=0.5, y=500, anchor="center")
back_btn.bind("<Enter>", lambda e: back_btn.config(bg="#1e79c6"))
back_btn.bind("<Leave>", lambda e: back_btn.config(bg="#136bae"))




# Skin prices
skin_prices = {
    "Default Skin": 0,
    "Black Gloves": 1000,
    #more skins
}

# Keep references to image objects so Tkinter doesn't garbage collect them
skin_previews = {}






# Skin buttons
skin_paths = {
    "Default Skin": {
        "rock": "imgs/rock.png",
        "paper": "imgs/paper.png",
        "scissors": "imgs/scissors.png"
    },
    "Black Gloves": {
        "rock": "skins/rockskin.png",
        "paper": "skins/paperskin.png",
        "scissors": "skins/scissorskin.png"
    }
    # Add more skins here
}

y_start = 180
y_step = 60
preview_size = (80, 80)  # size for shop preview






# --- Skin system / purchase ---
owned_skins = {"Default Skin"}  # player starts with default
equipped_skin = "Default Skin"
skin_prices = {
    "Default Skin": 0,
    "Black Gloves": 1000,
    # Add other skins with prices, e.g. "Golden Skin": 500
}

# Preload images for preview
skin_preview_imgs = {}  # {skin_name: PhotoImage}
for skin_name, paths in skin_paths.items():
    try:
        img_path = paths["rock"]  # show rock as preview
        pil_img = Image.open(resource_path(img_path)).resize((120, 120), Image.LANCZOS)
        skin_preview_imgs[skin_name] = ImageTk.PhotoImage(pil_img)
    except:
        skin_preview_imgs[skin_name] = tk.PhotoImage(width=120, height=120)

# --- Preview label ---
skin_preview_label = tk.Label(shop_page, image=None, bg="#222222")
skin_preview_label.place(relx=0.8, y=170, anchor="center")

def equip_skin(skin_name):
    global equipped_skin, coins

    # Show preview
    skin_preview_label.config(image=skin_preview_imgs[skin_name])
    skin_preview_label.image = skin_preview_imgs[skin_name]

    # Determine the "key" for skin_paths (strip any price label)
    skin_key = skin_name.split(" |")[0]

    # Check ownership or buy if enough coins
    if skin_name in owned_skins or skin_prices.get(skin_key, 0) == 0 or coins >= skin_prices.get(skin_key, 0):
        if skin_name not in owned_skins and skin_prices.get(skin_key, 0) > 0:
            coins -= skin_prices[skin_key]
            owned_skins.add(skin_name)
            save_data()  # <-- save coin deduction
            print(f"Bought: {skin_name}")
            update_all_coin_displays()  # <-- refresh both displays
            coin_sfx.play()

        # Equip the skin
        equipped_skin = skin_name
        print(f"Equipped skin: {skin_name}")
        win_sfx.play()

        # Update hand images in the game
        paths = skin_paths[skin_key]  # use correct skin_paths key
        for hand in ["rock", "paper", "scissors"]:
            new_img = ImageTk.PhotoImage(Image.open(resource_path(paths[hand])).resize(img_size))
            player_imgs[hand] = new_img
            base_player_imgs[hand] = new_img
            canvas.itemconfig(player_labels[hand], image=new_img)

        save_data()

    else:
        print("Not enough coins to buy this skin!")
        lose_sfx.play()





# skin_paths keys are internal
# skin_display_names are what you show in buttons
skin_display_names = {
    "Default Skin": "Default Skin",
    "Black Gloves": "Black Gloves"
}





def update_all_coin_displays():
    """Update coin display everywhere (game canvas + shop)."""
    # Game canvas
    canvas.itemconfig(coin_text_id, text=f"x {coins}")
    
    # Shop frame
    shop_coin_text.config(text=f"x {coins}")










load_save()

# Ensure owned_skins includes the saved skin
if equipped_skin not in owned_skins:
    equipped_skin = "Default Skin"

# Equip it properly
for display_name, key in skin_display_names.items():
    if key == equipped_skin:
        equip_skin(display_name)
        break










for idx, skin_key in enumerate(skin_paths):
    # Load preview (rock image as representative)
    path = skin_paths[skin_key]["rock"]
    img = ImageTk.PhotoImage(Image.open(resource_path(path)).resize(preview_size))
    skin_previews[skin_key] = img  # keep reference

    # Coin cost text
    cost_lbl = tk.Label(shop_page, text=f"{skin_prices.get(skin_key, 0)} 💰",
                        font=("Pixel game", 16), fg="yellow", bg="#222222")
    cost_lbl.place(relx=0.1, y=y_start + idx * y_step, anchor="center")

    # Equip / Buy button
    btn = tk.Button(shop_page, text=f"{skin_key}", font=("Pixel game", 24),
                    bg="#444444", fg="white", width=20, relief="raised",
                    command=lambda sk=skin_key: equip_skin(sk))
    btn.place(relx=0.5, y=y_start + idx * y_step, anchor="center")
    btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#555555"))
    btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#444444"))

    # Preview label
    preview_lbl = tk.Label(shop_page, image=img, bg="#222222")
    preview_lbl.place(relx=0.25, y=y_start + idx * y_step, anchor="center")


# --- Coin display in shop ---
shop_coin_img_path = resource_path("imgs/coin.png")
try:
    shop_coin_pil = Image.open(shop_coin_img_path).resize((40, 32), Image.LANCZOS)
    shop_coin_img = ImageTk.PhotoImage(shop_coin_pil)
except Exception:
    shop_coin_img = tk.PhotoImage(width=40, height=32)  # fallback

# Coin icon
shop_coin_label = tk.Label(shop_page, image=shop_coin_img, bg="#222222")
shop_coin_label.image = shop_coin_img  # keep reference
shop_coin_label.place(x=700, y=1)  # top-right corner

# Coin count text
shop_coin_text = tk.Label(shop_page, text=f"x {coins}", font=("Pixel game", 20),
                          fg="white", bg="#222222")
shop_coin_text.place(x=730, y=20, anchor="w")

# Function to update coin text in shop
def update_shop_coins():
    shop_coin_text.config(text=f"x {coins}")



# --- Equip / Buy skin function (update in-game hands too) ---
for idx, skin_key in enumerate(skin_paths):
    # Load preview (rock image as representative)
    path = skin_paths[skin_key]["rock"]
    img = ImageTk.PhotoImage(Image.open(resource_path(path)).resize(preview_size))
    skin_previews[skin_key] = img  # keep reference

    # Coin cost text
    cost_lbl = tk.Label(shop_page, text=f"{skin_prices.get(skin_key, 0)} COINS",
                        font=("Pixel game", 16), fg="yellow", bg="#222222")
    cost_lbl.place(relx=0.1, y=y_start + idx * y_step, anchor="center")

    # Equip / Buy button
    btn = tk.Button(shop_page, text=f"{skin_key}", font=("Pixel game", 24),
                    bg="#444444", fg="white", width=20, relief="raised",
                    command=lambda sk=skin_key: equip_skin(sk))
    btn.place(relx=0.5, y=y_start + idx * y_step, anchor="center")
    btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#555555"))
    btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#444444"))

    # Preview label
    preview_lbl = tk.Label(shop_page, image=img, bg="#222222")
    preview_lbl.place(relx=0.25, y=y_start + idx * y_step, anchor="center")























# --- Pause button in corner ---
pause_btn_corner_img = Image.open(resource_path("imgs/pause.png")).resize((60, 60))
pause_btn_corner_photo = ImageTk.PhotoImage(pause_btn_corner_img)
pause_btn_corner = tk.Button(canvas, image=pause_btn_corner_photo, bd=0, highlightthickness=0,
                             relief="flat", command=lambda: toggle_pause_canvas(),
                             bg="black", activebackground="black")
pause_btn_corner.place(x=730, y=20)  # Top-right corner





















# --- Load heartbeat sound ---
heartbeat_sfx = pygame.mixer.Sound(resource_path("audio/lowhp.wav"))

# --- Update health function ---
def update_health():
    global player_hp_display, npc_hp_display, player_hp, npc_hp
    if player_hp_display:
        canvas.delete(player_hp_display)
    if npc_hp_display:
        canvas.delete(npc_hp_display)
    player_hp = max(0, min(3, player_hp))
    npc_hp = max(0, min(3, npc_hp))
    if player_hp > 0:
        player_hp_display = canvas.create_image(90, 470, image=hp_images[player_hp])
    if npc_hp > 0:
        npc_hp_display = canvas.create_image(90, 130, image=hp_images[npc_hp])
    if player_hp <= 0:
        trigger_game_over("lose")
    elif npc_hp <= 0:
        trigger_game_over("win")




update_health()






















# --- End screen triggers ---
def trigger_game_over(result):
    global game_over_active
    if game_over_active:
        return
    game_over_active = True
    pygame.mixer.music.fadeout(1000)
    if result == "win":
        winsound_sfx.play()
        win_screen.tkraise()
    else:
        losesound_sfx.play()
        lose_screen.tkraise()

def return_to_menu():
    btn_sfx.play()
    pygame.mixer.music.load(resource_path("audio/menusong.mp3"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(loops=-1)
    global player_hp, npc_hp, wins, losses, draws, game_over_active, is_paused, pause_menu_btn, pause_overlay, pause_text_id
    player_hp, npc_hp, wins, losses, draws = 3, 3, 0, 0, 0
    game_over_active = False
    is_paused = False

    # Cleanup pause overlay elements
    if pause_overlay:
        canvas.delete(pause_overlay)
        pause_overlay = None
    if pause_text_id:
        canvas.delete(pause_text_id)
        pause_text_id = None
    if pause_menu_btn:
        pause_menu_btn.destroy()
        pause_menu_btn = None

    update_score()
    update_health()
    main_menu.tkraise()


def update_score():
    canvas.itemconfig(score_text_id, text=f"Wins: {wins}  Losses: {losses}  Draws: {draws}")


# --- Hover setup ---
hover_states = {c: False for c in choices}
scaled_imgs = {}
def make_glow(img, intensity=1.4):
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(intensity)
def pulse_image(choice, grow=True):
    if not hover_states.get(choice, False):
        # Restore equipped skin image when hover ends
        canvas.itemconfig(player_labels[choice], image=base_player_imgs[choice])
        canvas.coords(player_labels[choice], *player_positions[choice])
        return

    # Scale factor for pulse
    scale = 1.08 if grow else 1.0
    size = (int(img_size[0]*scale), int(img_size[1]*scale))

    # Take current equipped skin image for this hand
    # Convert to PIL for brightness adjustment
    hand_img = player_imgs[choice]._PhotoImage__photo  # get internal PhotoImage for PIL (or reload)
    pil_img = Image.open(resource_path(f"imgs/{choice}.png")).resize(img_size)
    
    # If you want equipped skin, use player_imgs dict
    pil_img = ImageTk.getimage(player_imgs[choice])
    bright_img = ImageEnhance.Brightness(pil_img).enhance(1.5)

    img = ImageTk.PhotoImage(bright_img.resize(size))
    scaled_imgs[choice] = img  # keep reference

    canvas.itemconfig(player_labels[choice], image=img)
    x, y = player_positions[choice]
    canvas.coords(player_labels[choice], x, y)

    # Loop
    window.after(250, lambda: pulse_image(choice, not grow))

def on_enter(event, choice):
    if game_active or game_paused:
        return
    hover_states[choice] = True
    pulse_image(choice, True)
def on_leave(event, choice):
    hover_states[choice] = False
    canvas.itemconfig(player_labels[choice], image=base_player_imgs[choice])
    canvas.coords(player_labels[choice], *player_positions[choice])
    scaled_imgs.pop(choice, None)











# --- Pause toggle ---
def toggle_pause_canvas():
    global is_paused, pause_overlay, pause_text_id, pause_menu_btn
    if not is_paused:
        is_paused = True
        pygame.mixer.music.pause()
        try: pause_sfx.play()
        except: pass
        pause_overlay = canvas.create_rectangle(0, 0, 800, 600, fill="black", stipple="gray50")
        pause_text_id = canvas.create_text(400, 250, text="PAUSED", font=("Pixel game", 50), fill="white")
        pause_menu_btn = tk.Button(canvas, text="MAIN MENU", font=("Pixel game", 28),
                                   bg="#136bae", fg="#FFE5A1", width=12, relief="raised",
                                   command=return_to_menu)
        pause_menu_btn.place(relx=0.5, rely=0.6, anchor="center")
        pause_menu_btn.bind("<Enter>", lambda e: pause_menu_btn.config(bg="#1e79c6"))
        pause_menu_btn.bind("<Leave>", lambda e: pause_menu_btn.config(bg="#136bae"))
    else:
        is_paused = False
        pygame.mixer.music.unpause()
        if pause_overlay: canvas.delete(pause_overlay)
        if pause_text_id: canvas.delete(pause_text_id)
        if pause_menu_btn:
            pause_menu_btn.destroy()
            pause_menu_btn = None

# --- Game logic ---
player_streak = 0
npc_streak = 0
streak_text_id = canvas.create_text(400, 50, text="", font=("Pixel game", 14), fill="yellow")

def update_streak_text():
    canvas.itemconfig(streak_text_id, text=f"Player Streak: {player_streak}  NPC Streak: {npc_streak}")

update_streak_text()

# --- Hit animation / screen shake ---
def shake_screen(duration=100, intensity=5):
    def step(elapsed=0):
        if elapsed >= duration:
            canvas.place(x=0, y=0)
            return
        offset_x = random.randint(-intensity, intensity)
        offset_y = random.randint(-intensity, intensity)
        canvas.place(x=offset_x, y=offset_y)
        window.after(20, lambda: step(elapsed + 20))
    step()

# --- Music adjust ---
def adjust_music_for_hp():
    if player_hp == 1:
        pygame.mixer.music.set_volume(0.5)
    else:
        pygame.mixer.music.set_volume(0.4)

# --- Flash tint ---
_STIPPLE_STEPS = ["gray75", "gray50", "gray25", "gray12"]
def flash_tint(color="green", total_time=400):
    rect = canvas.create_rectangle(0, 0, 800, 600, fill=color, outline="")
    canvas.tag_raise(rect)
    step_time = max(30, total_time // (len(_STIPPLE_STEPS) + 1))
    idx = 0
    def step():
        nonlocal idx
        if idx < len(_STIPPLE_STEPS):
            canvas.itemconfig(rect, stipple=_STIPPLE_STEPS[idx])
            idx += 1
            window.after(step_time, step)
        else:
            canvas.delete(rect)
    step()

# --- Countdown ---
def animate_countdown(callback):
    count = 3
    def tick():
        nonlocal count
        if count == 0:
            canvas.itemconfig(countdown_text, text="")
            callback()
        else:
            canvas.itemconfig(countdown_text, text=str(count))
            count_sfx.play()
            count -= 1
            window.after(1000, tick)
    tick()

# --- Move toward ---
def move_toward(center_x, npc_item, player_item, npc_y, player_y, meet_callback, player_choice, npc_choice, step=12):
    next_npc_y = npc_y + step
    next_player_y = player_y - step
    if next_npc_y >= next_player_y:
        meet_y = (npc_y + player_y) // 2
        canvas.coords(npc_item, center_x, meet_y)
        canvas.coords(player_item, center_x, meet_y)
        fight_sfx.play()
        flash_id = canvas.create_rectangle(0, 0, 800, 600, fill="white", outline="")
        canvas.tag_raise(flash_id)
        # Pass the choices here
        window.after(120, lambda: [canvas.delete(flash_id), meet_callback(player_choice, npc_choice)])
        return
    canvas.coords(npc_item, center_x, next_npc_y)
    canvas.coords(player_item, center_x, next_player_y)
    window.after(30, move_toward, center_x, npc_item, player_item, next_npc_y, next_player_y, meet_callback, player_choice, npc_choice, step)


# --- Animate return ---
def animate_return_positions(steps=12):
    current_npc_coords = {c: canvas.coords(npc_labels[c]) for c in npc_labels}
    current_player_coords = {c: canvas.coords(player_labels[c]) for c in player_labels}
    moves = []
    for c, (target_x, target_y) in npc_positions.items():
        cur = current_npc_coords.get(c, (target_x, target_y))
        dx = (target_x - cur[0]) / steps
        dy = (target_y - cur[1]) / steps
        moves.append(("npc", c, dx, dy))
    for c, (target_x, target_y) in player_positions.items():
        cur = current_player_coords.get(c, (target_x, target_y))
        dx = (target_x - cur[0]) / steps
        dy = (target_y - cur[1]) / steps
        moves.append(("player", c, dx, dy))
    def step(i=0):
        if i >= steps:
            return
        for kind, c, dx, dy in moves:
            lbl = npc_labels[c] if kind == "npc" else player_labels[c]
            x, y = canvas.coords(lbl)
            canvas.coords(lbl, x + dx, y + dy)
        window.after(25, lambda: step(i + 1))
    step(0)

def reset_positions():
    canvas.itemconfig(countdown_text, text="", fill="white")
    for c, (x, y) in npc_positions.items():
        canvas.coords(npc_labels[c], x, y)
    for c, (x, y) in player_positions.items():
        canvas.coords(player_labels[c], x, y)
        canvas.itemconfig(player_labels[c], image=base_player_imgs[c])
        canvas.itemconfig(npc_labels[c], image=base_npc_imgs[c])
    scaled_imgs.clear()
    update_health()

# --- Play function ---
def play(choice):
    global wins, losses, draws, game_active, player_hp, npc_hp, player_streak, npc_streak
    if game_active or is_paused:
        return
    game_active = True
    if choice in choice_sfx:
        choice_sfx[choice].play()
    npc_choice = random.choice(choices)

    def after_meet_original(player_choice, npc_choice):
        global wins, losses, draws, player_hp, npc_hp, player_streak, npc_streak
        if player_choice == npc_choice:
            draws += 1
            draw_sfx.play()
            tint_color = "gray"
            player_streak = 0
            npc_streak = 0
        elif (player_choice == "rock" and npc_choice == "scissors") or \
            (player_choice == "paper" and npc_choice == "rock") or \
            (player_choice == "scissors" and npc_choice == "paper"):
            wins += 1
            win_sfx.play()
            on_win(100)
            tint_color = "green"
            if player_hp < 3: player_hp += 1
            npc_hp -= 1
            player_streak += 1
            npc_streak = 0
            shake_screen()
        else:
            losses += 1
            lose_sfx.play()
            tint_color = "red"
            if npc_hp < 3: npc_hp += 1
            player_hp -= 1
            npc_streak += 1
            player_streak = 0
            shake_screen()

        update_health()
        flash_tint(color=tint_color, total_time=500)
        update_score()
        update_streak_text()
        adjust_music_for_hp()
        window.after(900, animate_return_positions)
        window.after(1400, reset_positions)
        window.after(1450, lambda: set_game_unlocked())


    def start_fight():
        npc_item = npc_labels[npc_choice]
        player_item = player_labels[choice]
        _, npc_y = canvas.coords(npc_item)
        _, player_y = canvas.coords(player_item)
        move_toward(center_x, npc_item, player_item, npc_y, player_y, after_meet_original, choice, npc_choice)


    animate_countdown(start_fight)

def set_game_unlocked():
    global game_active
    game_active = False

# --- Bind hover/clicks ---
for c in choices:
    canvas.tag_bind(player_labels[c], "<Enter>", lambda e, ch=c: on_enter(e, ch))
    canvas.tag_bind(player_labels[c], "<Leave>", lambda e, ch=c: on_leave(e, ch))
    canvas.tag_bind(player_labels[c], "<Button-1>", lambda e, ch=c: play(ch))

window.config(cursor="cross")    # crosshair






# --- LOW HP PULSE EFFECT ---
lowhp_overlay_ids = []
lowhp_scale = 1.0
lowhp_grow = True

def pulse_lowhp_effect():
    global lowhp_scale, lowhp_grow, lowhp_overlay_ids

    # remove previous overlays
    for oid in lowhp_overlay_ids:
        canvas.delete(oid)
    lowhp_overlay_ids.clear()

    if player_hp != 1:
        window.after(100, pulse_lowhp_effect)
        return

    for c in choices:
        x, y = player_positions[c]
        # pulsate alpha effect
        alpha = int(80 + (lowhp_scale-1.0)*200)  # pulsate between ~80-96 opacity
        color = f"#ff0000{alpha:02x}" if alpha <= 255 else "#ff0000ff"

        # create a rectangle behind each hand
        size = int(img_size[0]*lowhp_scale)
        oid = canvas.create_rectangle(
            x - size//2, y - size//2,
            x + size//2, y + size//2,
            fill="red", outline="", stipple="gray50"
        )
        canvas.tag_lower(oid, player_labels[c])  # put behind the hand image
        lowhp_overlay_ids.append(oid)

    # update scale for pulsate
    if lowhp_grow:
        lowhp_scale += 0.02
        if lowhp_scale >= 1.08:
            lowhp_grow = False
    else:
        lowhp_scale -= 0.02
        if lowhp_scale <= 1.0:
            lowhp_grow = True

    # loop
    window.after(100, pulse_lowhp_effect)

# --- start low HP pulse effect after all widgets are created ---
pulse_lowhp_effect()



# --- Load heartbeat sound ---
heartbeat_sfx = pygame.mixer.Sound(resource_path("audio/lowhp.wav"))

# Use a dedicated channel for looping heartbeat
heartbeat_channel = pygame.mixer.Channel(5)  # channel 5, can be any free channel

# --- Low HP overlay ---
low_hp_overlay_ids = []
low_hp_pulsing = False

def start_low_hp_effect():
    global low_hp_pulsing
    if low_hp_pulsing:
        return
    low_hp_pulsing = True
    if not heartbeat_channel.get_busy():
        heartbeat_channel.play(heartbeat_sfx, loops=-1)  # loop indefinitely
    pulse_low_hp()

def stop_low_hp_effect():
    global low_hp_pulsing
    low_hp_pulsing = False
    heartbeat_channel.stop()  # stop the heartbeat sound
    for rect_id in low_hp_overlay_ids:
        canvas.delete(rect_id)
    low_hp_overlay_ids.clear()

def pulse_low_hp(grow=True):
    if not low_hp_pulsing:
        return
    # Remove previous overlays
    for rect_id in low_hp_overlay_ids:
        canvas.delete(rect_id)
    low_hp_overlay_ids.clear()

    # Draw overlays for all 3 player hands **under the hand images**
    for c, (x, y) in player_positions.items():
        rect = canvas.create_rectangle(
            x - 60, y - 60, x + 60, y + 60,
            fill="red", stipple="gray50", outline=""
        )
        # Move it under the hand image
        canvas.tag_lower(rect, player_labels[c])
        low_hp_overlay_ids.append(rect)

    # Pulsate effect
    window.after(400, lambda: pulse_low_hp(not grow))


# --- Call inside update_health ---
def update_health():
    global player_hp_display, npc_hp_display, player_hp, npc_hp
    if player_hp_display:
        canvas.delete(player_hp_display)
    if npc_hp_display:
        canvas.delete(npc_hp_display)
    player_hp = max(0, min(3, player_hp))
    npc_hp = max(0, min(3, npc_hp))
    if player_hp > 0:
        player_hp_display = canvas.create_image(90, 470, image=hp_images[player_hp])
    if npc_hp > 0:
        npc_hp_display = canvas.create_image(90, 130, image=hp_images[npc_hp])
    if player_hp <= 0:
        trigger_game_over("lose")
    elif npc_hp <= 0:
        trigger_game_over("win")

    # Low HP effects
    if player_hp == 1:
        start_low_hp_effect()
    else:
        stop_low_hp_effect()



# --- Show menu initially ---
main_menu.tkraise()
window.mainloop()
pygame.mixer.music.stop()
