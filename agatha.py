import configparser
import logging
import tweepy
import discord
import asyncio
import random
import os
import time
import sys

# TODO
# Enabled/Disabled flag
# Parse to next command 


class Robot:
	def __init__(self):
		global config
		config = configparser.SafeConfigParser()
		config.read('robotsettings.cfg')

		#set up logging
		logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
		level=config.get('Settings', 'LogLevel'),
		filename='agatha.log',
		datefmt='%m-%d-%y %H:%M:%S')

		#set up twitter
		auth = tweepy.OAuthHandler(config.get('Auth','CONSUMER_KEY'), config.get('Auth','CONSUMER_SECRET'))
		auth.set_access_token(config.get('Auth', 'ACCESS_TOKEN_KEY'), config.get('Auth', 'ACCESS_TOKEN_SECRET'))
		self.api = tweepy.API(auth)

		#discord
		description = '''nice meme'''
		self.token = config.get('Auth', 'DISCORD_TOKEN')
		self.client = discord.Client()
		###############################
		#         Load Admins         #
		###############################

		self.admins = config.get("Settings","Admins").splitlines()
		self.banlist = config.get("Settings","Blacklist").splitlines()
		self.babyjail = []
		self.gaybabyjail = []


		###############################
		# Loading & Enabling Commands #
		###############################
		self.validCmds = []
		self.validCmds.append(Bomp("Bomp"))
		self.validCmds.append(RollMod("RollMod"))
		self.validCmds.append(Roll("Roll"))
		self.validCmds.append(Command("Null"))
		self.validCmds.append(OldRoll("OldRoll"))
		self.validCmds.append(Shutdown("Shutdown"))
		self.validCmds.append(Jade("Jade"))
		self.validCmds.append(Egg("Egg"))
		self.validCmds.append(Bird("Bird"))
		self.validCmds.append(Pep("Pep"))
		self.validCmds.append(Help("Help"))


#TODO: Method to hold entirety of robot stuff
#client runs in this method, and will check for @self.client.event things!
#everything else can be in seperate methods!!
	def robot(self):
		@self.client.event
		async def on_message(message):
			commcount = 0
			logging.info("[{0}] {1}: {2}".format(message.channel, message.author, message.content))
			if not message.channel.is_private:
				if message.author.bot == True or message.author.id in self.gaybabyjail or message.channel.id in self.banlist:
					return
			elif message.author.id not in self.admins:
				return
			msg = message.content.split()
			for i in range(0, len(msg)):
				token = msg[i]
				if token.startswith('!'):
					token = token[1:].lower()
					command = None
					try:
						command = next(x for x in self.validCmds if x.name.lower() == token)
					except StopIteration:
						logging.info("Command not found: {0}".format(token))

					if command is not None and commcount < 4:
						commcount = commcount + 1
						if(command.size > 0):
							#reading a specific amount of values
							data = msg[i+1:i + 1 + command.size]
							#i = 1 + command.size
						elif(command.size == -1):
							#reading until end of message
							data = msg[i+1:]
							#i = len(msg)
							#logging.info(i)
						else:
							data = []
						await self.client.send_typing(message.channel)
						await asyncio.sleep(.5)
						await command.runCommand(self.client, message.channel,data, message.author)
					if commcount >= 4 and message.author.id not in self.babyjail and message.author.id not in self.admins:
						await self.client.send_message(message.channel, message.author.mention + ": Please refrain from excessive commands. This is your only warning.")
						self.babyjail.append(message.author.id)
						return
					if commcount >=4 and message.author.id in self.babyjail:
						await self.client.send_message(message.channel, message.author.mention + ": Your transgressions have been recorded.")
						self.gaybabyjail.append(message.author.id)
						return

		

		self.client.run(self.token)

class Command:
	def __init__(self, name):
		global config
		self.name = name
		self.description = "No description!"
		self.help = "Help not set up!"
		self.size = 0
		try:
			self.description = config.get(name, 'Description')
			self.help = config.get(name, 'Help')
			self.size = config.getint(name, 'Size')
			logging.info("[{0}] Basic info loaded".format(self.name))
		except Exception as e:
			logging.error("[{0}] Failed reading config in setup".format(self.name))
			logging.error("[{0}]: {1}".format(self.name, str(e)))

	async def runCommand(self, client, channel, data, user):
		logging.warning(self.name + ": runCommand not overriden!")
		return

class Bomp(Command):
	def __init__(self, name):
		super().__init__(name)
		self.filename = config.get(name, 'Filename')
		file = open(self.filename, 'r')
		self.bompcount = int(file.read())
		file.close()
		logging.info("[Bomp] Bompcount = " + str(self.bompcount))
		self.specialBomp = config.get(self.name, 'SpecialBomp').splitlines()
	async def runCommand(self, client, channel, data, user):
		if(random.randint(0, 150) < self.bompcount):
			logging.info("[{0}] Special bomp!")
			self.bompcount = 0
			await client.send_message(channel,random.choice(self.specialBomp))
		else:
			self.bompcount = self.bompcount + 1
			logging.info("[Bomp] Bompcount = " + str(self.bompcount))
			file = open(self.filename, 'w')
			file.write(str(self.bompcount))
			file.close()
			await client.send_message(channel, 'bomp')
		return

class Jade(Command):
	def __init__(self, name):
		super().__init__(name)
		self.filename = config.get(name, 'Filename')
		self.cooldown = config.getint(name, 'Cooldown')
		file = open(self.filename, 'r')
		self.jadecount = int(file.read())
		file.close()
		logging.info("[Jade] LARGE MAN = " + str(self.jadecount))
		self.last = 0

	async def runCommand(self, client, channel, data, user):
		if (time.time() - self.last) < self.cooldown:
			logging.info("[Jade] Currently on cooldown!")
			return
		self.jadecount = self.jadecount + 1
		logging.info("[Jade] LARGE MAN = " + str(self.jadecount))
		file = open(self.filename, 'w')
		file.write(str(self.jadecount))
		file.close()
		await client.send_message(channel,"I SUMMON A {0}/{0} LARGE MAN <:malfshades:360804944372170752>".format(self.jadecount))
		self.last = time.time()
		return

class RollMod(Command):
	def __init__(self, name):
		super().__init__(name)
		self.singleOp = config.get(self.name, 'SingleOp')
		self.singleInt = config.get(self.name, 'SingleInt')
		self.singleDie = config.get(self.name, 'SingleDie')
		self.zeroErr = config.get(self.name, 'ZeroErr')
		self.zeroSidedErr = config.get(self.name, 'ZeroSidedErr')
		self.tooLargeErr = config.get(self.name, 'TooLargeErr')
		self.onlyArithErr = config.get(self.name, 'OnlyArithErr')
	async def runCommand(self, client, channel, data, user):
		logging.info("[{0}] Request from {1}, data = {2}".format(self.name, channel, data))

		equation = []
		j = 0
		for i in data:
			temp = self.checkValid(i)
			if (temp is None):
				reason = "Rolling " + (" ".join(data[j:]))
				await client.send_message(channel, reason)
				break
			else:
				j = j +1
				equation.append(temp)
		if (len(equation) < 1):
			#No Equation
			await client.send_message(channel, self.help)
			return
		logging.info("[{0}] Equation: {1}".format(self.name, equation))
		out = self.evalEquation(equation, client)
		for i in out:
			await client.send_message(channel, i)
			await asyncio.sleep(.1)
		return


	def evalEquation(self, equation, client):
		positive = True
		result = 0
		resString = ""
		opAppend = ""
		zero = False
		zeroSides = False
		tooLarge = False
		large = False
		onlyArith = True
		out = []
		if(len(equation) == 1 and not equation[0].eqType == "D"):
			if (equation[0].eqType == "O"):
				out.append(self.singleOp)
			elif (equation[0].eqType == "I"):
				out.append(str(equation[0].evaluate()))
				out.append(self.singleInt)
			return out

		nextOperator = equation[0].eqType == "O"

		if len(equation) > 8:
			large = True

		for j in equation:
			if (onlyArith and j.eqType == "D"):
				onlyArith = False
			if (nextOperator and j.eqType == "O"):
				opAppend = j.value
				positive = (opAppend == "+")
			elif not(nextOperator or j.eqType == "O"):
				try:
					roll = j.evaluate()
				except ZeroError:
					zero = True
					roll = 0
				except ZeroSidedError:
					zeroSides = True
					roll = 0
				except TooLargeError:
					tooLarge = True
					roll = 0
				if positive:
					result += roll
				else:
					result -= roll
				if not large:
					resString += opAppend  + " " + str(roll) + " "
			else:
				logging.debug("[{0}]: Equation broken".format(self.name))
				break
			nextOperator = not nextOperator
		if zero:
			out.append(self.zeroErr)
		if zeroSides:
			out.append(self.zeroSidedErr)
		if tooLarge:
			out.append(self.tooLargeErr)
		if onlyArith:
			out.append(self.onlyArithErr)			
		resOut = "Total: " + str(result)
		if not large:
			resOut = resOut + " Rolls: `[{1}]`".format(result, resString[1:-1])
		out.append(resOut)
		return (out)



	def checkValid(self, inStr):
		logging.debug("In CheckValid " + inStr)

		if(inStr == "+" or inStr == "-"):
			logging.debug("{0} is an operator.".format(inStr))
			return RollValue("O", inStr)
		if Helper.isInt(inStr):
			logging.debug("{0} is an int.".format(inStr))
			return RollValue("I", inStr)
		dice = inStr.lower().split('d', 1)
		try:
			if(Helper.isInt(dice[0]) and Helper.isInt(dice[1])):
				logging.debug("{0} is a valid die.".format(inStr))
				return RollValue("D", dice)
			else:
				logging.debug("{0} is not valid".format(inStr))
				return (None)
		except:
			logging.debug("{0} is not valid".format(inStr))
			return (None)
			
class Helper:
	def isInt(value):
		try:
			return value.isdigit()
		except ValueError:
			return False

class RollValue:
	def __init__(self, eqType, value):
		self.eqType = eqType
		self.value = value
	def __repr__(self):
		return "{0} {1}".format(self.eqType, self.value)
	def evaluate(self):
		result = 0
		if (self.eqType == "D"):
			amt = int(self.value[0])
			sides = int(self.value[1])
			if amt == 0:
				raise ZeroError()
			elif sides == 0:
				raise ZeroSidedError()
			elif sides == 1:
				return amt
			if amt > 65535 or sides > 65535:
				raise TooLargeError()
			else:
				for i in range(int(self.value[0])):
					result += random.randint(1,int(self.value[1]))
		else:
			result = int(self.value)
		return result

class OldRoll(Command):
	def __init__(self, name):
		super().__init__(name)
		self.help2 = config.get(self.name, 'Help2')
		self.zeroRoll = config.get(self.name, 'ZeroRoll')
		self.tooLargeErr = config.get(self.name, 'TooLargeErr')
		self.polyhedral = [4,6,8,10,12,20]
		self.polysass = config.get(self.name, 'PolySass')
		self.toolargearray = config.get(self.name, 'TooLargeArray').splitlines()
	async def runCommand(self, client, channel, data, user):
		logging.info("[{0}] Request from {1}, data = {2}".format(self.name, channel, data))
		reason = ""
		out = []
		if len(data) > 1:
			reason = "Rolling " + " ".join(data[1:])
			out.append(reason)
		try:
			tmp = (self.roll(data[0]))
			for j in tmp:
				out.append(j)
		except:
			if (random.randint(1,10) == 1):
				await client.send_message(channel, self.help2)
				return
			await client.send_message(channel, self.help)
			return
		for i in out:
			if(i.startswith("!")):
				crit = await (client.send_message(channel, i[1:]))
				await client.add_reaction(crit, "\U0001F38A")
				continue
			else:
				await client.send_message(channel, i)
		return


	def roll(self, data):
		out = []
		try:
			splt = data.lower().split('d', 1)
			rolls = int(splt[0])
			limit = int(splt[1])
		except Exception:
			logging.warning("[{0}] Splitting {1} failed.".format(self.name, data))
			raise
		try:
			out = []
			if (rolls <= 0 or limit <= 0):
				return [self.zeroRoll]
			if (limit == 1):
				return [("*sigh*. " + str(rolls) + ".")]
			if (rolls > 65535 or limit > 65535):
				return [self.tooLargeErr]
			result = []
			for i in range(rolls):
				result.append(random.randint(1,limit))
			if (rolls>20 or len(str(limit)) > 3):
				return [random.choice(self.toolargearray) + " " + str(sum(result))]
			if(rolls == 1):
				if limit in self.polyhedral and random.randint(1,4)==1:
					out.append(self.polysass)
				if result[0] == limit:
					    out.append("!Total: " + str(sum(result)) + " Rolls: `" + str(result) + "`")
					    return out
			out.append("Total: " + str(sum(result)) + " Rolls: `" + str(result) + "`")
			return out
		except Exception:
			logging.warning("[{0}] Error with rolling dice. boop.".format(self.name))
			raise

class Roll(Command):
	def __init__(self, name):
		super().__init__(name)
		self.redirect = None
	async def runCommand(self, client, channel, data, user):
		if not self.redirect:
			logging.info("[{0}] Redirect not found, attempting to create".format(self.name))
			try:
				self.redirect = next(x for x in agatha.validCmds if x.name == "RollMod")
			except:
				logging.error("[{0}] Could not find RollMod class! Is it enabled?".format(self.name))
				agatha.validCmds.remove(self)
				return
		logging.info("[{0}] Redirecting to {1}".format(self.name, self.redirect.name))
		await self.redirect.runCommand(client, channel, data, user)
		return

class Shutdown(Command):
	def __init__(self,name):
		super().__init__(name)
		self.admins = config.get("Settings","Admins").splitlines()
	async def runCommand(self, client, channel, data, user):
		if (user.id not in self.admins):
			await client.send_message(channel, self.help)
			return
		else:
			await client.send_message(channel, "Shutting down. <@85107142603833344>")
			await client.logout()
			sys.exit(0)

class Egg(Command):
	async def runCommand(self, client, channel, data, user):
		#em = discord.Embed(title='Wow!', description='This is something!', colour=0x800000)
		#em.set_author(name=user.display_name, icon_url=user.avatar_url)
		#em.set_footer(text="This is a footer!", icon_url=client.user.avatar_url)
		#em.set_thumbnail(url="https://pbs.twimg.com/profile_images/929896915050754048/I8pe7OMP_400x400.jpg")
		#field1 = em.add_field(name="field 1", value="kill me", inline=True)
		#field2 = field1.add_field(name="field 2", value="help", inline=True)
		#field2.add_field(name="field 3", value="this is dumb", inline=True)
		#msg = await client.send_message(channel, embed=em)

		rlist = []
		for i in user.roles:
			rlist.append((i.name, i.position, i.id))

		em2 = discord.Embed(title='A mystery!')
		#em2.add_field(name="Roles", value=rlist)
		field = em2.add_field(name="(っ◔◡◔)っ", value="(っ◔◡◔)っ", inline=True)
		#field = field.add_field(name="2", value=2, inline=True)
		#field = field.add_field(name="3", value=3, inline=True)
		#field = field.add_field(name="4", value=4, inline=True)
		em2.set_footer(text="You're not supposed to see this yet", icon_url=client.user.avatar_url)
		msg = await client.send_message(channel, embed=em2)
		#msg = await client.send_message(channel, "Egg")
		#await client.add_reaction(msg, "\U0001F38A")

class Bird(Command):
	def __init__(self, name):
		super().__init__(name)
		self.notreadyarray = config.get(self.name, 'NotReadyArray').splitlines()
		self.lastpic = 0
		self.cooldown = config.getint(name, 'Cooldown')
	async def runCommand(self, client, channel, data, user):
		sinceLast = time.time() - self.lastpic
		if sinceLast < self.cooldown:
			logging.info('[{0}] Bird picture on cooldown!'.format(self.name))
			await client.send_message(channel, "{0}\nAbout {1} seconds left.".format(random.choice(self.notreadyarray), int(self.cooldown - sinceLast)))
			return
		else:
			file = "pictures/" + random.choice(os.listdir("pictures"))
			await client.send_file(channel, file, filename="pep"+os.path.splitext(file)[1], content="<:loaf:359002158483636224>")
			logging.info('[{0}] {1} sent!'.format(self.name, file))
			self.lastpic = time.time()
			return

class Pep(Command):
	def __init__(self, name):
		super().__init__(name)
		self.redirect = None
	async def runCommand(self, client, channel, data, id):
		if not self.redirect:
			logging.info("[{0}] Redirect not found, attempting to create".format(self.name))
			try:
				self.redirect = next(x for x in agatha.validCmds if x.name == "Bird")
			except:
				logging.error("[{0}] Could not find bird class! Is it enabled?".format(self.name))
				agatha.validCmds.remove(self)
				return
		logging.info("[{0}] Redirecting to {1}".format(self.name, self.redirect.name))
		await self.redirect.runCommand(client, channel, data, user)
		return

class Help(Command):
	async def runCommand(self, client, channel, data, user):
		try:
			helpstr = next(x for x in agatha.validCmds if x.name.lower() == data[0].lower()).help
		except:
			logging.info("[{0}] Command not found.".format(self.name))
			helpstr = "The following commands are enabled:\n"
			for i in agatha.validCmds:
				helpstr = helpstr + "{0}: {1}\n".format(i.name, i.help)
		await client.send_message(channel, helpstr)





class SingleOpError(ValueError):
	'''raise this when there's only a single operator'''
class ZeroSidedError(ValueError):
	'''raise this when a die has zero sides'''
class ZeroError(ValueError):
	'''raise this when a die is rolled 0 times'''
class TooLargeError(ValueError):
	'''raise this when a number is too big'''


agatha = Robot()
agatha.robot()

sys.exit("Agatha has crashed.")


























