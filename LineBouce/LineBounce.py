#!/usr/bin/kivy

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from random import randint
from kivy.uix.button import Button
from kivy.graphics import Ellipse,Line
from kivy.core.window import Window
from time import sleep
from math import sqrt,atan2,tan

class Background_Line(Widget): #Lines in the background that move down to make the screen seem to move up.
	
	"""makes a new line--height is an int"""
	def create(self,height):
		self.pos=(0,height)
		app.game.screen.background_lines.append(self)

	"""moves the line up--amount is an int, how much it moves"""
	def move(self,amount):
		self.pos=(0,self.y-amount)
		if self.y<0:
			self.pos=(0,self.y+480)


class Target(Widget): #used for the tutorial, a small rectangle for the user to click
	
	"""moves the target to a location-- x and y are ints, x,y coordinates"""
	def move_to(self,x,y):
		self.pos=(x-self.width/2,y-self.height/2)

class Up_token(Widget): #a rocket shaped token that gives the user an extra "double move" when they get it. the user also cannot progress without collecting it.

	"""puts it in a random place"""
	def spawn(self):
		self.times_spawned+=1
		self.x_pos=randint(50,220)
		self.y_pos=randint(300,430)+self.times_spawned*300

	"""moves it according to the amount the screen has scrolled"""
	def move(self):
		self.pos=(self.x_pos,self.y_pos-app.game.screen.ScrollHeight)

class Ball(Widget): #The ball, it bounces around on the line drawn by the user.
	
	"""puts the ball in the middle of the screen, set it's velocities so that it goes down at an angle."""
	def initialize(self):
		self.velocity_x=.5
		self.velocity_y=0
		self.x_pos=app.game.center_x-25
		self.y_pos=app.game.center_y-25#25 is width

	"""moves the ball according to its velocity"""
	def move(self):
		self.x_pos+=self.velocity_x
		self.y_pos+=self.velocity_y
		self.pos=(self.x_pos,self.y_pos-app.game.screen.ScrollHeight)

	"""approximates the x velocity of the ball, given its linear velocity and its angle-- angle is float, angle of ball. length is float, linear velocity.--returns the estimated x velocity"""
	def approximate_x(self,angle,length):
		x=length/1.5 #just a starting point, no real math here.
		y=sqrt(length**2-x**2) #given the above x velocity, calculates what y velocity would have to be
		while atan2(x,y)-angle>.001: #makes sure its pretty close
			x-=(atan2(x,y)-angle) #gets a bit closer to the correct angle
			if abs(length)>abs(x): #makes sure that it doesn't square root a negative
				y=sqrt(length**2-x**2)
			else:
				return x #instead of the program crashing, it just returns the inacurate x (this only happens in very specific situations anyway, when the ball has a small velocity (when they are desperately trying to save it (and probably going to lose anyway)))
		return x

	"""calculates new velocities for the ball after bouncing off of the line-- extra velocity is a float that tells how much extra velocity is imparted to the ball."""
	def bounce(self,extra_velocity):
		#for radians, bottom is pi, top is zero, right is positive, left is negative
		if app.game.screen.point[0].x<app.game.screen.point[1].x: #accounts for the line being upside down
			line_angle=1.57+atan2((app.game.screen.point[1].x-app.game.screen.point[0].x),(app.game.screen.point[1].y-app.game.screen.point[0].y))
		else:
			line_angle=1.57+atan2((app.game.screen.point[0].x-app.game.screen.point[1].x),(app.game.screen.point[0].y-app.game.screen.point[1].y))
		ball_angle=atan2(self.velocity_x,self.velocity_y)
		ball_speed=sqrt(self.velocity_x**2+self.velocity_y**2) #linear velocity
		ball_speed+=extra_velocity/(ball_speed)+extra_velocity/4 #has extra velocity related to ball speed, and not related to ball speed acounted, so that the faster the ball is, the less extra velocity it gets, but everything gets a certain velocity by default
		new_angle=line_angle-ball_angle
		if new_angle>3.14:
			new_angle-=6.28
		if new_angle<-3.14:
			new_angle+=6.28
		self.velocity_x=self.approximate_x(new_angle,ball_speed)
		if ball_speed**2-self.velocity_x**2>0: #another thing to check whether the velocity x isn't too much (thus throwing an error)
			self.velocity_y=sqrt(ball_speed**2-self.velocity_x**2)
		else:
			self.velocity_y=0 #assumes that if the ball x is too much, the y is probably 0

	"""Checks if the ball has collided with the line--returns true or false, as to whether it has collided"""
	def collide(self):
		if self.velocity_y<0: #so that it doesn't get stuck on the line, bouncing every update
			for i in range(30): #creates thirty points along the line to check
				if sqrt(((i*((app.game.screen.point[1].x-app.game.screen.point[0].x)/30)+app.game.screen.point[0].x-self.center_x)**2)+((i*((app.game.screen.point[1].y-app.game.screen.point[0].y)/30)+app.game.screen.point[0].y-self.center_y)**2))<self.width/2: #makes the thirty points, checks for each point whether it is within the correct distance of the ball
					app.game.screen.has_touched=False
					return True
			return False

	"""Moves the ball a bit towards the center if it is near the sides"""
	def bumpers(self):
		if app.game.bumpers_on:
			if self.x_pos<50:
				self.velocity_x+=(50-self.x_pos)/3000
			if self.x_pos>220:
				self.velocity_x+=(220-self.x_pos)/3000

class Point(object): #has x and y, that's mostly it

	def __init__(self,x,y):
		self.x=x
		self.y=y


class Drawn_line(Widget): #the more opaque line, which the ball collides with, and the player moves
	
	"""Draws the line in reference to the two points that define the line"""
	def draw(self):
		with self.canvas:
			Line(points=[app.game.screen.point[0].x,app.game.screen.point[0].y,app.game.screen.point[1].x,app.game.screen.point[1].y],width=4)


class Hypothetical_line(Widget): #the less opaque line that indicates where the next Drawn_line should be

	"""Draws the hypothetical line from a point on the line to where the mouse is-- takes in two points: the points within which to draw the line."""
	def draw(self,point_1,point_2):
		with self.canvas:
			Line(points=[point_1.x,point_1.y,point_2.x,point_2.y],width=4,opacity=.1)
			

class MenuScreen(Widget): #The initial scren, with a settings and game button

	"""Makes a screen that says line bounce, and has buttons for the game and the settings"""
	def initialize(self):
		self.title=Label(text="LineBounce!",font_size=50,center_x=app.game.center_x,center_y=app.game.center_y*1.75)
		self.add_widget(self.title)
		self.game_button=Button(text="Play Now!",font_size=50,center_x=app.game.center_x-75,center_y=app.game.center_y*1)
		self.game_button.width=250
		self.add_widget(self.game_button)
		self.game_button.bind(on_press=app.game.start_game) #starts the game if you press that button
		self.settings_button=Button(text="Settings",font_size=50,center_x=app.game.center_x-50,center_y=app.game.center_y*.5)
		self.settings_button.width=200
		self.add_widget(self.settings_button)
		self.settings_button.bind(on_press=app.game.start_settings) #initiates the settings menu if you press that button


class GameScreen(Widget): #This class has all of the code for the actual game, and sets up the screen, makes things move, react to the player
	
	"""This makes certain parts of the tutorial happen. The first part puts the target on the screen, with its text. the second part (which is called when they click the rectangle) removes the rectangle and tells them to click on the other side. the third part puts a lot of instructions on the screen. the fourth part takes them down and starts the game.--takes in the part of the tutorial to run."""
	def tutorial(self,part):
		if part==0:
			self.Tutorial_text=Label(text="Press the Rectangle to start",font_size=20,center_x=app.game.center_x,center_y=app.game.center_y*1.75)
			self.add_widget(self.Tutorial_text)
			Clock.schedule_interval(self.update,1.0/60.0)
			self.target=Target()
			self.target.move_to(280,155) #puts the target rectangle in a good place for their first click
			self.add_widget(self.target)
		if part==1:
			self.remove_widget(self.target)
			self.Tutorial_text.text="Your next click moves the other side of the line"
			self.Tutorial_text.font_size=15
		if part==2:
			Clock.unschedule(self.update)
			self.remove_widget(self.Tutorial_text)
			self.Tutorial_text=[]
			self.texts=["You can only move the line once per bounce","Otherwise, it counts as a double-move","the top left number is your score","top right is your number of double-moves","+1 double-moves for every spaceship","You'll stop scrolling if you miss a spaceship","if the ball hits any side, you lose","Bumpers push the ball away from the sides, and","can be turned on and off in settings.","Have Fun! Click to play"]
			for i in range(10): #puts the instructions on the screen
				self.Tutorial_text.append(Label(text=self.texts[i],font_size=15,center_x=app.game.center_x,center_y=470-i*20))
				self.add_widget(self.Tutorial_text[i])
		if part==3:
			for i in self.Tutorial_text:
				self.remove_widget(i)
				self.touched=False
			Clock.schedule_interval(self.update,1.0/60.0)

	"""This moves the ball and the lines around, and runs other functions that make the game work. it checks whether they lose, keeps score, speeds the game up, moves the screen up, a few other things to facilitate the game. details in comments below."""
	def update(self,dt):
		if self.ball.collide(): #checks for collision
			self.ball.bounce(15*self.speed) #bounces according to the speed of the ball (to make up for the speed of the ball)
		if self.first_line_complete>1:
			self.ball.move()
			self.ball.velocity_y-=self.speed
			self.speed*=1.0002
			self.line_speed*=1.00012#these two make the game slowly speed up
		if self.can_draw: #these move the point that is moving toward where they last clicked
			self.point[self.point_to_move].x+=((self.next_point.x-self.point[self.point_to_move].x)*self.line_speed)
			self.point[self.point_to_move].y+=((self.next_point.y-self.point[self.point_to_move].y)*self.line_speed)
		self.remove_widget(self.drawn_line)
		self.drawn_line=Drawn_line()
		self.drawn_line.draw()
		self.add_widget(self.drawn_line)
		if self.touched: #checks that they are touching the screen, then puts the hypothetical line there
			self.remove_widget(self.hypothetical_line)
			self.hypothetical_line=Hypothetical_line()
			self.hypothetical_line.draw(self.point[self.point_to_move],Point(self.Mouse_x,self.Mouse_y))
			self.add_widget(self.hypothetical_line)
		elif self.hypothetical_line in self.children: #takes out the hypothetical line if the are not touching the screen
			self.remove_widget(self.hypothetical_line)
		self.up_token.move()
		self.move_screen_up()
		if self.ball.collide_widget(self.up_token):
			self.up_token.spawn() #this moves the up_token upwards
			self.double_touches+=1
		if (self.ball.y+self.ScrollHeight)/24>self.score:
			self.score=int((self.ball.y+self.ScrollHeight-((self.ball.y+self.ScrollHeight)%24))/24)
			self.Score.text=str(self.score)
		if self.ball.x<0 or self.ball.x>270 or self.ball.y<0 or self.ball.y>430: #checks if the ball went off of fthe screen, and they lost
			Clock.unschedule(self.update)
			app.game.GameOn=False
			Clock.schedule_once(app.game.start_game_over) #goes to the game over screen when they die.
		self.ball.bumpers()
		self.Double_touches.text=str(self.double_touches) #sets the double touches text in the top right to the new amount

	"""This changes the Scroll Height and the points' positions relative to how high on the screen the ball is."""
	def move_screen_up(self):
		if self.ball.y_pos-self.ScrollHeight>240 and self.ScrollHeight<self.up_token.times_spawned*300:
			amount_to_scroll=(self.ball.y_pos-self.ScrollHeight-240)*self.line_speed/20
			self.ScrollHeight+=amount_to_scroll
			self.next_point.y-=amount_to_scroll
			self.point[0].y-=amount_to_scroll
			self.point[1].y-=amount_to_scroll
			for i in self.background_lines:
				i.move(amount_to_scroll)

	"""This changes the point that moves toward where they clicked. if the tutorial is on, it checks whether they clicked in the box, and runs the tutorial text for that, and also deals with the second part of the tutorial."""
	def new_lines(self):
		if app.game.tutorial_on and self.part_of_tutorial==1:
			self.part_of_tutorial=2
			self.tutorial(2)

		self.next_point=Point(self.Mouse_x,self.Mouse_y) #this makes the point that the line moves towards where they let go of the mouse
		if app.game.tutorial_on and self.part_of_tutorial==0:
			if self.Mouse_x>270 and self.Mouse_x<290 and self.Mouse_y>145 and self.Mouse_y<165:
				self.has_touched=False
				self.can_draw=True
				self.first_line_complete=1
				self.part_of_tutorial=1
				self.tutorial(1)

		elif self.first_line_complete==0: #This is if it is the first time, (which happens by default becasue of kivy), and doesn't do anything (sets things to false)
			self.has_touched=False
			self.can_draw=True
			self.point_to_move=1
			
		elif self.has_touched==False: #if it is the first click per bounce, it says that they have already clicked, says that they can move the line
			self.has_touched=True
			self.can_draw=True
		else:
			if self.double_touches>0: #if this is their second click and they have any more double moves, they lose 1 double move, and can draw.
				self.double_touches-=1
				self.can_draw=True
			else:
				self.can_draw=False #they can't draw if they have already clicked and haven't any double moves, nothing happens
		if self.can_draw:
			if self.point_to_move==0:
				self.point_to_move=1 #changes the point to move to
			else:
				self.point_to_move=0
			self.first_line_complete+=1

	"""Updates the Mouse positions when they touch down"""
	def on_touch_down(self,touch):
		if app.game.GameOn:
			self.Mouse_x=touch.x
			self.Mouse_y=touch.y
			self.touched=True

	"""Updates the Mouse positions when the Mouse moves"""
	def on_touch_move(self,touch):
		if app.game.GameOn:
			self.Mouse_x=touch.x
			self.Mouse_y=touch.y
	"""Calls new lines when they lift their mouse (finger)"""
	def on_touch_up(self,touch):
		if app.game.tutorial_on and self.part_of_tutorial==2: #for a specific part of the tutorial
			self.part_of_tutorial=3
			self.tutorial(3)
		elif app.game.GameOn:
			self.new_lines()
			self.touched=False

	"""initializes a bunch of Widgets and variables for the game, everything that is neccessary to make a new game."""
	def initialize(self):

		self.ScrollHeight=0
		self.ball=Ball()
		self.ball.initialize()
		self.add_widget(self.ball)

		sleep(.1)
		self.point=[Point(40,70),Point(280,70)] #makes the starting 2 points

		self.drawn_line=Drawn_line()
		self.drawn_line.draw() #draws the line so that it shows up in the beggining
		self.add_widget(self.drawn_line)

		self.hypothetical_line=Hypothetical_line()
		self.add_widget(self.hypothetical_line)

		self.line_speed=.1
		self.point_to_move=0
		self.next_point=Point(self.point[0].x,self.point[0].y) #this and the past line make sure that if the line moves toward 

		self.speed=(.025)
		self.Mouse_x=self.point[0].x
		self.Mouse_y=self.point[0].y
		
		self.up_token=Up_token()
		self.up_token.times_spawned=-1 #so that the first time, it sets to 0, which works with the upward scrolling
		self.up_token.spawn()
		self.add_widget(self.up_token)
		
		self.background_lines=[] #creates the lines in the background evenly
		for i in range(20):
			background_line=Background_Line()
			background_line.create(i*24)
			self.add_widget(background_line)
		app.game.GameOn=True
		self.touched=False

		self.first_line_complete=0

		self.score=0
		self.Score=Label(text=str(self.score),font_size=20,center_x=20,center_y=460) 
		self.add_widget(self.Score)


		self.can_draw=False
		self.double_touches=1
		self.Double_touches=Label(text=str(self.double_touches),font_size=20,center_x=300,center_y=460)
		self.add_widget(self.Double_touches)

		self.ball.move() #so that it spawns in the middle, not the bottom left
		self.part_of_tutorial=10 #this makes it so that the varibale exists, but won't interact with anything, because its too high (fixes an error)

		if app.game.tutorial_on:
			self.part_of_tutorial=0
			self.tutorial(0)
		else:
			Clock.schedule_interval(self.update, 1.0 / 60.0)

class GameOverScreen(Widget):
	
	"""Makes the label that says game over, puts the high scores on, shows their latest score, and has buttons for the menu and the game."""
	def initialize(self,latest_score):
		self.game_over=Label(text="Game Over!",font_size=50,center_x=app.game.center_x,center_y=app.game.center_y*1.75)
		self.add_widget(self.game_over)
		self.game_button=Button(text="Play Again",font_size=30,center_x=70,center_y=80)
		self.game_button.width=150
		self.add_widget(self.game_button)
		self.game_button.bind(on_press=app.game.start_game)
		self.menu_button=Button(text="Menu",font_size=30,center_x=250,center_y=80)
		self.menu_button.width=100
		self.add_widget(self.menu_button)
		self.menu_button.bind(on_press=app.game.start_menu)
		self.highscore_label=Label(text="Highscores:",font_size=30,center_x=app.game.center_x,center_y=app.game.center_y*1.5)
		self.add_widget(self.highscore_label)
		self.highscores=sorted(self.get_highscores())[::-1][:5] #This gets the scores and finds the top 5
		for i in range(len(self.highscores)): #this prints them going down from the "high score" label
			self.score=Label(text="--"+str(self.highscores[i])+"--",font_size=20,center_x=app.game.center_x,center_y=app.game.center_y*(1.3-(float(i)/10)))
			self.add_widget(self.score)
		self.scored_label=Label(text="You Scored:",font_size=30,center_x=app.game.center_x-50,center_y=app.game.center_y*.7)
		self.add_widget(self.scored_label)
		self.score_label=Label(text=latest_score,font_size=30,center_x=app.game.center_x+80,center_y=app.game.center_y*.7)
		self.add_widget(self.score_label)

	"""This returns a list of the scores in int form"""
	def get_highscores(self):
		high_scores=[]
		for line in open('scores.txt'):
			if line.strip().isdigit():
				high_scores.append(int(line.strip()))
		return high_scores


class SettingsScreen(Widget): 

	"""Makes a label that says settings, buttons to change settings, and buttons to navigate menus"""
	def initialize(self):
		app.game.settings_file_to_var()
		self.settings=Label(text="Settings",font_size=50,center_x=app.game.center_x,center_y=app.game.center_y*1.75)
		self.add_widget(self.settings)
		self.game_button=Button(text="Play Now!",font_size=30,center_x=70,center_y=80)
		self.game_button.width=150
		self.add_widget(self.game_button)
		self.game_button.bind(on_press=app.game.start_game)
		self.menu_button=Button(text="Menu",font_size=30,center_x=250,center_y=80)
		self.menu_button.width=100
		self.add_widget(self.menu_button)
		self.menu_button.bind(on_press=app.game.start_menu)

		if app.game.bumpers_on: #figures out what to write on the buttons
			self.bumpers_text="Bumpers: On"
		else:
			self.bumpers_text="Bumpers: Off"
		
		if app.game.tutorial_on:
			self.tutorial_text="tutorial: On"
		else:
			self.tutorial_text="tutorial: Off"

		self.bumpers_button=Button(text=self.bumpers_text,font_size=30,center_x=100,center_y=app.game.center_y*1.35)
		self.bumpers_button.width=220
		self.add_widget(self.bumpers_button)
		self.bumpers_button.bind(on_press=self.bumpers_callback)

		self.tutorial_button=Button(text=self.tutorial_text,font_size=30,center_x=90,center_y=app.game.center_y*.85)
		self.tutorial_button.width=240
		self.add_widget(self.tutorial_button)
		self.tutorial_button.bind(on_press=self.tutorial_callback)

	"""This changes whether the bumpers are on, then initializes the settings again"""
	def bumpers_callback(self,instance):
		if app.game.bumpers_on:
			app.game.bumpers_on=False
		else:
			app.game.bumpers_on=True
		app.game.settings_var_to_file()
		Clock.schedule_once(app.game.start_settings)

	"""This changes whether the tutorial is on, then initializes the settings again"""
	def tutorial_callback(self,instance):
		if app.game.tutorial_on:
			app.game.tutorial_on=False
		else:
			app.game.tutorial_on=True
		app.game.settings_var_to_file()
		Clock.schedule_once(app.game.start_settings)

class Game(Widget):

	"""This takes out all of the widgets and initializes the game"""
	def start_game(self,dt):
		for i in list(self.screen.children):
			self.screen.remove_widget(i)
		self.screen = GameScreen()
		self.add_widget(self.screen)
		self.screen.initialize()

	"""This takes out all of the widgets and initializes the settings menu"""
	def start_settings(self,dt):
		for i in list(self.screen.children):
			self.screen.remove_widget(i)
		self.screen=SettingsScreen()
		self.add_widget(self.screen)
		self.screen.initialize()
		
	"""This takes out all of the widgets and initializes the main menu"""
	def start_menu(self,dt):
		for i in list(self.screen.children):
			self.screen.remove_widget(i)
		self.screen=MenuScreen()
		self.screen.initialize()
		self.add_widget(self.screen)

	"""This takes out all of the widgets and initializes the game over menu. It also saves their score"""
	def start_game_over(self,dt):
		f=open("scores.txt",'a')
		latest_score=str(self.screen.score)
		f.write(latest_score+"\n")
		f.close()
		for i in list(self.screen.children):
			self.screen.remove_widget(i)
		self.screen=GameOverScreen()
		self.screen.initialize(latest_score)
		self.add_widget(self.screen)
		
	"""This sets the tutorial and bumpers variables to what is written in the settings file"""
	def settings_file_to_var(self):
		
		f=open("settings.txt")
		lines=f.readlines()

		if len(lines)<2: #This is if they have never made settings before, it makes them for you (default is bumpers and tutorial on)
			self.bumpers_on=True
			self.tutorial_on=True
			self.settings_var_to_file()

		f.close()
		f=open("settings.txt")
		lines=f.readlines()

		if lines[0]=="Bumpers: On\n":
			self.bumpers_on=True
		else:
			self.bumpers_on=False
		if lines[1]=="Tutorial: On":
			self.tutorial_on=True
		else:
			self.tutorial_on=False
		f.close()

	"""Writes in the settings file what the settings are (to save them)"""
	def settings_var_to_file(self):
		to_write=""
		f=open("settings.txt","w")
		if self.bumpers_on:
			to_write+="Bumpers: On\n"
		else:
			to_write+="Bumpers: Off\n"
		if self.tutorial_on:
			to_write+="Tutorial: On"
		else:
			to_write+="Tutorial: Off"
		f.write(to_write)
		f.close()

class LineBounceApp(App):

	def build(self):
		self.game=Game()
		self.game.GameOn=False #so that the touch events don't happen
		Window.size=(320,480) #mimics phone screens
		self.game.screen=Widget() #to have children, so that when the start functions try to remove children, it doesn't throw an error
		self.game.settings_file_to_var()
		Clock.schedule_once(self.game.start_menu)
		return self.game

if __name__ == '__main__':
	app=LineBounceApp() #I gave it a name so I can refference parent classes from their children (through app.game, or so on)
	app.run()