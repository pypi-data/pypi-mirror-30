#!/usr/bin/env python
#encoding: utf-8
from os import name
from string import ascii_lowercase, ascii_uppercase
import argparse

def hello():

	if name != "nt":
		print """

 ▒█████  ▒██   ██▒  ██████  █     █░ ██▓▄▄▄█████▓ ▄████▄   ██░ ██        █████▒██▀███
▒██▒  ██▒▒▒ █ █ ▒░▒██    ▒ ▓█░ █ ░█░▓██▒▓  ██▒ ▓▒▒██▀ ▀█  ▓██░ ██▒     ▓██   ▒▓██ ▒ ██▒
▒██░  ██▒░░  █   ░░ ▓██▄   ▒█░ █ ░█ ▒██▒▒ ▓██░ ▒░▒▓█    ▄ ▒██▀▀██░     ▒████ ░▓██ ░▄█ ▒
▒██   ██░ ░ █ █ ▒   ▒   ██▒░█░ █ ░█ ░██░░ ▓██▓ ░ ▒▓▓▄ ▄██▒░▓█ ░██      ░▓█▒  ░▒██▀▀█▄
░ ████▓▒░▒██▒ ▒██▒▒██████▒▒░░██▒██▓ ░██░  ▒██▒ ░ ▒ ▓███▀ ░░▓█▒░██▓ ██▓ ░▒█░   ░██▓ ▒██▒
░ ▒░▒░▒░ ▒▒ ░ ░▓ ░▒ ▒▓▒ ▒ ░░ ▓░▒ ▒  ░▓    ▒ ░░   ░ ░▒ ▒  ░ ▒ ░░▒░▒ ▒▓▒  ▒ ░   ░ ▒▓ ░▒▓░
  ░ ▒ ▒░ ░░   ░▒ ░░ ░▒  ░ ░  ▒ ░ ░   ▒ ░    ░      ░  ▒    ▒ ░▒░ ░ ░▒   ░       ░▒ ░ ▒░
░ ░ ░ ▒   ░    ░  ░  ░  ░    ░   ░   ▒ ░  ░      ░         ░  ░░ ░ ░    ░ ░     ░░   ░
    ░ ░   ░    ░        ░      ░     ░           ░ ░       ░  ░  ░  ░            ░
                                                 ░                  ░
		"""
	else:
		print """
  ___                    _ _       _        __      
 / _ \__  _______      _(_) |_ ___| |__    / _|_ __ 
| | | \ \/ / __\ \ /\ / / | __/ __| '_ \  | |_| '__|
| |_| |>  <\__ \\ V  V /| | || (__| | | |_|  _| |   
 \___//_/\_\___/ \_/\_/ |_|\__\___|_| |_(_)_| |_|  """ 
                                                  

def x_split(line, n):
	return [line[i:i+n] for i in range(0, len(line), n)]


def x_pad(s,c,x):
	return s + c * (x - len(s))

def x_xor(s, key):
	return "".join([chr(ord(c) ^ key) for c in s ])

def x_pattern(size=0):

		if(size == 0):
			parser = argparse.ArgumentParser(prog='xswitch')
			parser.add_argument('-c')

			args = parser.parse_args()
			size = int(args.c)

		pattern = ""
		x = 0
		alpha = ascii_lowercase + ascii_uppercase
		while len(pattern) <= size:
			for i in range(0, 26 * 2):
				pattern += (str(x % 10) + alpha[i]) * 2
				if len(pattern) >= size:
					return pattern[:size]
			x += 1
		return pattern[:size]

if __name__ == "__main__":
	hello()
