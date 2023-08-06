import random
import string
import os
import click

@click.command()
@click.option('-l', default=12, help='length of the password.')

def pass_gen(l):
	symb = ''
	letters = ''
	digits = ''

	symb = ''.join(set(random.choice(string.punctuation) for x in range(100)))
	letters = ''.join(set(random.choice(string.ascii_letters) for x in range(100)))
	digits = ''.join(set(random.choice(string.digits) for x in range(10)))


	chars_combination = letters + digits + symb
	#print(chars_combination)

	password = ''
	password = ''.join(random.choice(chars_combination) for x in range(l))
	#print(password, len(password))
	click.echo(password)


if __name__ == '__main__':
    pass_gen()
