import pygame, random, json, sys
import math

class Game(pygame.sprite.Sprite):
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
		"normal",
		"normal",
		"normal",
		"normal",
		"death",
		"death",
		"death",
		"death",
		"death",
		"item"
	] #80% normal 20% death

	possible_powerups=[
		"Leben",
		"5P",
	]

	#region load image powerups
	leben = pygame.image.load('sprites/Leben.png')
	fuenfP = pygame.image.load('sprites/5P.png')
	Tile = pygame.image.load('sprites/Tile.png')
	apfel = pygame.image.load('sprites/Apfel.png')
	#endregion

	circles = []

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface((50, 50))
		self.image.fill((0, 0, 0))
		self.rect = self.image.get_rect()

	def draw_new_tile(self):
		row = (random.randint(1, 4)*100)-20
		rect = pygame.Rect(row, 0, 40, 40)
		pygame.draw.rect(screen, TILES, rect, 0)

		random_style = self.rect_styles[random.randint(0, len(self.rect_styles)-1)]

		if random_style == "item":
			powerup = random.choice(self.possible_powerups)
			self.rects.append(PowerUp.spawn(PowerUp, row, pygame.image.load(f'sprites/{powerup}.png'), powerup))
		elif random_style == "death":
			self.rects.append([row, 0, random_style, self.apfel])
		else:
			self.rects.append([row, 0, random_style, self.Tile])

	def update_tiles(self):
		for rect in self.rects:
			rect[1] += speed # increment y position
			if rect[1] < screen_height:
				shape = pygame.Rect(rect[0], rect[1], 40, 40)

				# if rect[2] == "normal" or screen_height-300 < rect[1] < screen_height-290 or screen_height-280 < rect[1] < screen_height-270 or screen_height-260 < rect[1] < screen_height-250 or rect[1] > screen_height-240:
				if rect[2] == "death":
					if screen_height-300 < rect[1] and rect[3] == self.apfel:
						rect[3] = self.Tile
					screen.blit(rect[3], [rect[0], rect[1]])
				else:
					screen.blit(rect[3], [rect[0], rect[1]])
				
			else: 
				if rect[2] == "death":
					self.rects.remove(rect)
				elif rect[2] == "normal":
					shape = pygame.Rect(rect[0], rect[1]-40, 40, 40)
					pygame.draw.rect(screen, TILES, shape, 0)
					player.damage()
					self.rects.remove(rect)
				elif rect[2] == "PowerUp":
					self.rects.remove(rect)
		
		for circle in self.circles:
			if circle[2] > 50:
				self.circles.remove(circle)
			
			pygame.draw.circle(screen, circle[3], (circle[0], circle[1]), circle[2], 3)

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
						self.circles.append([rect[0]+20, rect[1]+20, 10, TILES])
						return True
					elif rect[2] == "death":
						# draw red square when collided
						self.rects.remove(rect)
						shape = pygame.Rect(rect[0], rect[1], 40, 40)
						pygame.draw.rect(screen, DEATH_TILES, shape, 0)
						player.damage()

					elif rect[2] == "PowerUp":
						if rect[4] == "Leben":
							player.add_health()
							audio.play(random.choice(audio.collect))
							self.circles.append([rect[0]+20, rect[1]+20, 10, LEBEN])
						if rect[4] == "5P":
							player.score += 5
							audio.play(random.choice(audio.collect))
							self.circles.append([rect[0]+20, rect[1]+20, 10, (0, 0, 0)])
						self.rects.remove(rect)
		
		return False

	def draw_tiles(self):
		for rect in self.rects:
				if rect[2] == "death":
					if screen_height-300 < rect[1] and rect[3] == self.apfel:
						rect[3] = self.Tile
					screen.blit(rect[3], [rect[0], rect[1]])
				else:
					screen.blit(rect[3], [rect[0], rect[1]])
		
		for circle in self.circles:
			if circle[2] > 50:
				self.circles.remove(circle)
			
			pygame.draw.circle(screen, circle[3], (circle[0], circle[1]), circle[2], 3)

class Player(pygame.sprite.Sprite):
	score = 0
	leben = 1

	player = pygame.image.load('sprites/Player.png')

	def draw_player(self, player_pos):
		if self.leben == 0:
			end_game()
		x_axis = min(player_pos, screen_width-40)
		rect = pygame.Rect(x_axis, 650, 40, 40)
		screen.blit(self.player, [rect[0], rect[1]])

		#check collision
		if game.check_collision(rect) is not False:
			self.score += 1


	def get_mouse_position(self):
		return pygame.mouse.get_pos()[0]
	
	def damage(self):
		self.leben -= 1
		audio.play(audio.death)
	
	def add_health(self):
		if self.leben < 3:
			self.leben += 1
	
	def reset(self):
		self.leben = 1

class Audio():
	def __init__(self):
		self.collect = [
			pygame.mixer.Sound("audio/pickupCoin.wav"),
			pygame.mixer.Sound("audio/pickupCoin (1).wav"),
			pygame.mixer.Sound("audio/pickupCoin (2).wav")
			]
		self.death = pygame.mixer.Sound("audio/hitHurt.wav")
		self.winning = [
			pygame.mixer.Sound("audio\level-win-6416.wav"),
			pygame.mixer.Sound("audio\winning2.wav"),
			pygame.mixer.Sound("audio\winning3.wav")
		]
	
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
	
	def update_leaderboard(self, new_score):
		leaderboard = settings["Leaderboard"]
		leaderboard.append(new_score)
		leaderboard.sort(reverse = True)

		new_leaderboard = [0, 0, 0, 0, 0]
		for i in range(0, 5):
			new_leaderboard[i] = leaderboard[i]
		self.change_setting("Leaderboard", new_leaderboard)

class PowerUp():
	name = ""

	def __init__(self, name):
		self.name = name

	def spawn(self, row, img, name):
		return [row, 0, "PowerUp", img, name]

#region load settings
with open("./settings.json") as f:
	settings = json.load(f)

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
pygame.display.init()
pygame.display.set_caption("Cool Game")
screen = pygame.display.set_mode([screen_width, screen_height])

icon = pygame.image.load("cool_game_icon.ico")
pygame.display.set_icon(icon)

font_s = pygame.font.SysFont('Arial', 25, True, False)
font = pygame.font.SysFont('Arial', 30, True, False)
font_L = pygame.font.SysFont('Arial', 50, True, False)
#endregion

speed = 4
interval = 350
max_speed = int(settings["Max_Geschwindigkeit"])
min_interval = 150
speed_increment = .15
interval_increment = 4
tiles = 0

running = True
game_state = "playing"

game = Game()
player = Player()
audio = Audio()
setting = Settings(settings)

Highscore = int(settings["Highscore"])
Highscore_scored = False

display_score = f"Punkte: {player.score}"
#endregion

#region colors
# Colors https://lospec.com/palette-list/lagoon
LEBEN = (248, 134, 149)
PLAYER = (51, 47, 53)
TILES = (74, 122, 150)
DEATH_TILES = (255, 115, 107)
BACKGROUND = (251, 240, 237)
#endregion

def end_game():
	global game_state
	global Highscore_scored
	global Highscore
	global tiles
	tiles = 0
	game_state = "lost"
	
	leaderboard = settings['Leaderboard']

	if player.score >= Highscore:
		Highscore_scored = True
		Highscore = player.score

		# play winning score
		audio.play(random.choice(audio.winning))
		# write new highscore in json file
		setting.change_setting("Highscore", player.score)
		setting.update_leaderboard(player.score)
	elif leaderboard[4] < player.score:
		setting.update_leaderboard(player.score)

def show_statistics():
	txt = font.render("Q zum schließen", True, (0, 0, 0))
	screen.blit(txt, [10, 80])

	txt = font.render("R zum neustarten", True, (0, 0, 0))
	screen.blit(txt, [10, 120])

	
	txt = font_L.render(display_score, True, (0, 0, 0))
	screen.blit(txt, [50, 200])


	if Highscore_scored:
		txt = font_L.render("Neuer Highscore", True, (0, 0, 0))
		screen.blit(txt, [50, 260])
	else:
		txt = font.render("Highscore: " + str(Highscore), True, (0, 0, 0))
		screen.blit(txt, [50, 260])
	
	
	txt = font.render("Leaderboard:", True, (0, 0, 0))
	screen.blit(txt, [50, 420])
	
	leaderboard = settings['Leaderboard']
	for i in range(0, 5):
		txt = font_s.render(str(i+1) + ": " + str(leaderboard[i]), True, (0,0,0))
		screen.blit(txt, [50, 455+(i*25)])

def pause_screen():
	txt = font.render("T für steuerung mit Tasten", True, (0, 0, 0))
	screen.blit(txt, [10, 50])

	txt = font.render("M für steuerung mit Maus", True, (0, 0, 0))
	screen.blit(txt, [10, 90])

	txt = font_L.render("Pause", True, (0, 0, 0))
	screen.blit(txt, [50, 260])

	txt = font_L.render("Steuerung: " + mode, True, (0, 0, 0))
	screen.blit(txt, [50, 320])

def show_player_score():
	#draw players Score
	score_txt = font.render(display_score, True, (0, 0, 0))
	screen.blit(score_txt, [10, 10])

	score_txt = font.render("Leben: " + str(player.leben), True, (0, 0, 0))
	screen.blit(score_txt, [10, 40])

def event_handeling():
	global game_state
	global mode
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.display.quit()
			pygame.quit(), sys.exit()
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q:
				pygame.display.quit()
				pygame.quit(), sys.exit()

			if game_state == "playing":
				if event.key == pygame.K_ESCAPE:
					game_state = "paused"

				if mode == "Tasten":
					if event.key == pygame.K_LEFT:
						player_pos = max(player_pos-100, 80)
					elif event.key == pygame.K_RIGHT:
						player_pos = min(player_pos+100, 380)
			elif game_state == "lost":
				if event.key == pygame.K_r:
					player.score = 0
					game.rects = []
					speed = 5
					interval = 250
					game_state = "playing"
					player.reset()
					game.draw_new_tile()
			elif game_state == "paused":
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

game.draw_new_tile()

while running:
	event_handeling()
	if game_state == "playing":

		if mode == "Maus":
			#hide mouse cursor
			pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
			player_pos = player.get_mouse_position()-20

		display_score = f"Punkte: {player.score}"
		screen.fill(BACKGROUND)
		player.draw_player(player_pos)

		if game.rects[len(game.rects)-1][1] > interval:
			game.draw_new_tile()
			tiles += 1
			# decrease spanwing time
			interval = max(interval - interval_increment, min_interval)
			# up speed
			speed += speed_increment
			if speed > max_speed:
				# slowly increase spped
				speed = math.log(tiles+1)*1.5+5

		if game.update_tiles() == False:
			end_game()
	
	elif game_state == "lost":

		screen.fill(BACKGROUND)
		game.draw_tiles()
		show_statistics()
		
	elif game_state == "paused":
		screen.fill(BACKGROUND)
		game.draw_tiles()
		pause_screen()

	show_player_score()

	pygame.display.flip()
	clock.tick(fps)
