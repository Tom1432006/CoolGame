import pygame, random, json, sys

class Game():
	rects = []
	rect_styles = [
		"normal",
		"normal",
		"normal",
		"normal",
		"normal",
		"normal",
		"normal",
		"normal",
		"death",
		"death"
	] #80% normal 20% death

	circles = []

	def draw_new_tile(self):
		row = (random.randint(1, 4)*100)-20
		rect = pygame.Rect(row, 0, 40, 40)
		pygame.draw.rect(screen, TILES, rect, 0)

		random_style = self.rect_styles[random.randint(0, len(self.rect_styles)-1)]

		self.rects.append([row, 0, random_style])

	def update_tiles(self):
		for rect in self.rects:
			rect[1] += speed # increment y position
			if rect[1] < screen_height:
				shape = pygame.Rect(rect[0], rect[1], 40, 40)

				# if rect[2] == "normal" or screen_height-300 < rect[1] < screen_height-290 or screen_height-280 < rect[1] < screen_height-270 or screen_height-260 < rect[1] < screen_height-250 or rect[1] > screen_height-240:
				if rect[2] == "normal" or screen_height-300 < rect[1]:
					pygame.draw.rect(screen, TILES, shape, 0)
				else:
					pygame.draw.rect(screen, DEATH_TILES, shape, 0)
				
			else: 
				if rect[2] == "death":
					self.rects.remove(rect)
				else:
					shape = pygame.Rect(rect[0], rect[1]-40, 40, 40)
					pygame.draw.rect(screen, TILES, shape, 0)
					end_game()
		
		for circle in self.circles:
			if circle[2] > 50:
				self.circles.remove(circle)
			
			pygame.draw.circle(screen, TILES, (circle[0], circle[1]), circle[2], 3)

			# make circle grow exponentially
			if circle[2] > 40:
				circle[2] += 64
			elif circle[2] > 20:
				circle[2] += 32
			elif circle[2] > 10:
				circle[2] += 16
			else:
				circle[2] += 8

	def check_collision(self, player_rect):
		for rect in self.rects:
			if rect[1] > 600:
				if pygame.Rect.colliderect(player_rect, pygame.Rect(rect[0], rect[1], 40, 40)):
					if rect[2] == "normal":
						audio.play(random.choice(audio.collect))
						self.rects.remove(rect)
						self.circles.append([rect[0]+20, rect[1]+20, 10])
						return True
					else:
						# draw red square when collided
						self.rects.remove(rect)
						shape = pygame.Rect(rect[0], rect[1], 40, 40)
						pygame.draw.rect(screen, DEATH_TILES, shape, 0)
						end_game()
		
		return False

class Player():
	score = 0

	def draw_player(self, player_pos):
		x_axis = min(player_pos, screen_width-40)
		rect = pygame.Rect(x_axis, 650, 40, 40)
		pygame.draw.rect(screen, PLAYER, rect, 0)

		#check collision
		if game.check_collision(rect) is not False:
			self.score += 1


	def get_mouse_position(self):
		return pygame.mouse.get_pos()[0]

class Audio():
	def __init__(self):
		self.collect = [
			pygame.mixer.Sound("audio/pickupCoin.wav"),
			pygame.mixer.Sound("audio/pickupCoin (1).wav"),
			pygame.mixer.Sound("audio/pickupCoin (2).wav")
			]
		self.death = pygame.mixer.Sound("audio/hitHurt.wav")
		self.winning = pygame.mixer.Sound("audio\level-win-6416.wav")
	
	def play(self, audio):
		pygame.mixer.Sound.play(audio)

class Settings():
	settings = ""
	def __init__(self, settings):
		#load settings
		self.settings = settings
		
	def change_setting(self, setting, value):
		with open("./settings.json", "r+") as f:
			json_data = json.load(f)
			json_data[setting] = value
			f.seek(0)
			json.dump(json_data, f, indent=4)
			f.truncate()
		return True

#region load settings
with open("./settings.json") as f:
	settings = json.load(f)

color_scheme = settings["Farben_Thema"]
try:
	colors = settings[color_scheme]
except Exception as e:
	exit("Dieses Farben Thema gibt es nicht")

possible_modes = ["Maus", "Tasten"]
if settings["mode"] not in possible_modes:
	exit("Invalid setting Mode")
#endregion

#region variables
screen_width = 500
screen_height = 700
clock = pygame.time.Clock()
fps = 30
player_pos = 80
mode = settings["mode"]

#region setup pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.display.set_caption("Cool Game")
screen = pygame.display.set_mode([screen_width, screen_height])

icon = pygame.image.load("cool_game_icon.ico")
pygame.display.set_icon(icon)

font_L = pygame.font.SysFont('Arial', 50, True, False)
font = pygame.font.SysFont('Arial', 30, True, False)
#endregion

speed = 4
interval = 350
max_speed = int(settings["Max_Geschwindigkeit"])
min_interval = 150
speed_increment = .15
interval_increment = 4

running = True
game_state = "playing"

game = Game()
player = Player()
audio = Audio()
setting = Settings(settings)

Highscore = int(settings["Highscore" + settings["mode"]])
Highscore_scored = False

display_score = f"Punkte: {player.score}"
#endregion

#region colors
# Colors https://lospec.com/palette-list/lagoon
try:
    for color in colors:
        if color["name"] == "Hintergrund":
            BACKGROUND = tuple(map(int, color["farbe"].split(', ')))
        elif color["name"] == "Spieler":
            TILES = tuple(map(int, color["farbe"].split(', ')))
        elif color["name"] == "Teile":
            PLAYER = tuple(map(int, color["farbe"].split(', ')))
        elif color["name"] == "Todes_Teile":
            DEATH_TILES = tuple(map(int, color["farbe"].split(', ')))

    #try colors
    pygame.draw.circle(screen, PLAYER, (0, 0), 0)
    pygame.draw.circle(screen, TILES, (0, 0), 0)
    pygame.draw.circle(screen, DEATH_TILES, (0, 0), 0)
    pygame.draw.circle(screen, BACKGROUND, (0, 0), 0)
except Exception as e:
    exit("Something is wrong with your color scheme!")
#endregion

def end_game():
	global game_state
	global Highscore_scored
	global Highscore
	game_state = "lost"

	audio.play(audio.death)
	if player.score >= Highscore:
		Highscore_scored = True
		Highscore = player.score

		# play winning score
		audio.play(audio.winning)
		# write new highscore in json file
		setting.change_setting("Highscore" + settings["mode"], player.score)

game.draw_new_tile()

while running:
	if game_state == "playing":

		if mode == "Maus":
			#hide mouse cursor
			pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
			player_pos = player.get_mouse_position()-20

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.display.quit()
				pygame.quit(), sys.exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
					pygame.display.quit()
					pygame.quit(), sys.exit()

				if event.key == pygame.K_ESCAPE:
					game_state = "paused"

				if mode == "Tasten":
					if event.key == pygame.K_LEFT:
						player_pos = max(player_pos-100, 80)
					elif event.key == pygame.K_RIGHT:
						player_pos = min(player_pos+100, 380)

		display_score = f"Punkte: {player.score}"
		screen.fill(BACKGROUND)
		player.draw_player(player_pos)

		if game.rects[len(game.rects)-1][1] > interval:
			game.draw_new_tile()
			# decrease spanwing time
			interval = max(interval - interval_increment, min_interval)
			# up speed
			speed = min(speed + speed_increment, max_speed)

		if game.update_tiles() == False:
			end_game()
		
		#draw players Score
		score_txt = font.render(display_score, True, (0, 0, 0))
		screen.blit(score_txt, [10, 10])
	
	elif game_state == "lost":
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.display.quit()
				pygame.quit(), sys.exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
					pygame.display.quit()
					pygame.quit(), sys.exit()
				if event.key == pygame.K_r:
					player.score = 0
					game.rects = []
					speed = 5
					interval = 250
					game_state = "playing"
					game.draw_new_tile()
		
		#region draw text
		txt = font.render("Q zum schließen", True, (0, 0, 0))
		screen.blit(txt, [10, 50])

		txt = font.render("R zum neustarten", True, (0, 0, 0))
		screen.blit(txt, [10, 90])

		
		txt = font_L.render(display_score, True, (0, 0, 0))
		screen.blit(txt, [50, 200])


		if Highscore_scored:
			txt = font_L.render("Neuer Highscore", True, (0, 0, 0))
			screen.blit(txt, [50, 260])
		else:
			txt = font.render("Highscore: " + str(Highscore), True, (0, 0, 0))
			screen.blit(txt, [50, 260])
		
		#endregion

	elif game_state == "paused":
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.display.quit()
				pygame.quit(), sys.exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
					pygame.display.quit()
					pygame.quit(), sys.exit()

				if event.key == pygame.K_ESCAPE:
					game_state = "playing"
				if event.key == pygame.K_t:
					# mode = Tasten
					setting.change_setting("mode", "Tasten")
					mode = "Tasten"
				elif event.key == pygame.K_m:
					# mode = Maus
					setting.change_setting("mode", "Maus")
					mode = "Maus"

		screen.fill(BACKGROUND)
		
		txt = font.render("T für steuerung mit Tasten", True, (0, 0, 0))
		screen.blit(txt, [10, 50])

		txt = font.render("M für steuerung mit Maus", True, (0, 0, 0))
		screen.blit(txt, [10, 90])

		txt = font_L.render("Pause", True, (0, 0, 0))
		screen.blit(txt, [50, 260])

		txt = font_L.render("Steuerung: " + mode, True, (0, 0, 0))
		screen.blit(txt, [50, 320])

	pygame.display.flip()
	clock.tick(fps)
