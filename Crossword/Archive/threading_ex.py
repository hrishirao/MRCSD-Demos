# Python program to illustrate the concept 
# of threading 
# importing the threading module 
import threading
from os import system
from pygame import *

def print_cube(num): 
	""" 
	function to print cube of given num
	"""
	mixer.init()
	mixer.music.load("correct.mp3")
	mixer.music.play()
	for p in range(0,2):system('Say "go solo bro"');print("Cube: {}".format(num * num * num))

def print_square(num): 
	""" 
	function to print square of given num 
	"""
	
	for p in range(0,3):system('Say "yolo"');print("Square: {}".format(num * num))
	mixer.init()
	s = mixer.Sound("wrong.wav")
	s.play()

if __name__ == "__main__": 
	# creating thread 
	t1 = threading.Thread(target=print_square, args=(10,)) 
	t2 = threading.Thread(target=print_cube, args=(10,)) 

	# starting thread 1 
	t1.start() 
	# starting thread 2 
	t2.start() 

	# wait until thread 1 is completely executed 
	t1.join() 
	# wait until thread 2 is completely executed 
	t2.join() 

	# both threads completely executed 
	print("Done!") 
