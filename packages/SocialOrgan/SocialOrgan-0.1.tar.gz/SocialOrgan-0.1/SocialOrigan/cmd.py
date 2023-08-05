from .proxy import main
from argparse import ArgumentParser


Arger = ArgumentParser()
Arger.add_argument("-u", "--update", default=False, action='store_true', help="update proxy...")
Arger.add_argument("-c", "--country", default='all', help="choose a country")
Arger.add_argument("-l", "--list-code", default=False, action='store_true', help="list country's code")



def run():
	args = Arger.parse_args()
	if args.update:
		main(args.country)
	elif args.list_code:
		main(args.country, help=True)
