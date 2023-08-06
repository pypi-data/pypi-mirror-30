import random
import string
import os
import click

@click.command()
@click.option('-l', default=12, type=int, help='length of the password. Default is 12 characters')

def main(l):
	symb = ''
	letters = ''
	digits = ''

	symb = ''.join(set(random.choice(string.punctuation) for x in range(100)))
	letters = ''.join(set(random.choice(string.ascii_letters) for x in range(100)))
	digits = ''.join(set(random.choice(string.digits) for x in range(10)))


	chars_combination = letters + digits + symb

	password = ''
	if l <=0:
	    click.echo('Invalid value for "-l" argument. Please provide value greater than 0.')
	else:
		password = ''.join(random.choice(chars_combination) for x in range(l))
		click.echo(password)


if __name__ == '__main__':
    main()
