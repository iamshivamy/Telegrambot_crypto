from telegram import *
from telegram.ext import *
import json
from bitbnspy import bitbns

bot = Bot('')		#Telegram Bot API
key = ''	#Bitbns API
secretKey = ''		#Bitbns Secret key

updater = Updater('', use_context=True)	#telegram	Bot API

dispatcher = updater.dispatcher															#telegram

bitbnsObj = bitbns(key, secretKey)

def get_pretty_print(json_object):	
    return json.dumps(json_object, sort_keys=True, indent=4, separators=(',', ': '))





#print(bot.get_me())



#--------------------------------------------------------#
def CURRENT(update,context):
	user_says = " ".join(context.args)
	coin = user_says.split()
	coin = [elem.upper() for elem in coin ]
	A=(get_pretty_print(bitbnsObj.getTickerApi('')))
	A=A.replace('"','').replace('{','').replace('}','').replace(',','')         #replace
	if len(coin) == 0 :
		if len(A) > 4096:
			for x in range(0,len(A),4096):
				bot.send_message(chat_id = update.effective_chat.id,text=A[x:x+4096])
		else:
			bot.send_message(chat_id = update.effective_chat.id,text=A)
		bot.send_message(chat_id = update.effective_chat.id,text='To get current value of specific CRYPTO type /live_price and crypto name in short form and in capital letters. \nfor e.g - /live_price BTC  or \n /live_price BTC ETH This will give live prices of BTC and ETH ')
	else:
		for coins in coin:
			if coins not in A:
				B = 'No such crypto found. Try again!'
				bot.send_message(chat_id = update.effective_chat.id,text=B)
				break
			else:
				B=(get_pretty_print(bitbnsObj.getTickerApi(coins)))
				B=B.replace('"','').replace('{','').replace('}','')         #replace
				bot.send_message(chat_id = update.effective_chat.id,text=B)    

#	bot.send_message(

#		chat_id = update.effective_chat.id,
#		text= A,

#		)
start_value = CommandHandler("live_price", CURRENT, pass_args=True)
dispatcher.add_handler(start_value)
#--------------------------------------------------------#

#-------------------------------------------------------#
def ALERT(update, context):
	user_says = " ".join(context.args)
	D = user_says.split()
	if len(D) == 3:
		crypto = D[0].upper()
		sign = D[1]
		price = float(D[2])
		if bitbnsObj.cryptoCheck(crypto) & isinstance(price, float) & (sign == '<' or sign == '>'):
			context.job_queue.run_repeating(priceAlertCallback, interval=20, first=5, context=[crypto, sign, price, update.message.chat_id], name=crypto)
			response = f"⏳ I will ALERT you a message when the price of {crypto} reaches {price}, \n"
			response += f"the current price of {crypto} is {bitbnsObj.lastPrice(crypto)}"
		else:
			response = f'Invalid! TRY AGAIN! \n Please provide a crypto code and a price value: \n/price_alert cryptocode > or < price \n for e.g - \n/price_alert DOGE > 20  \n /price_alert DOGE < 50 '

	else:
		response = f'⚠️ Please provide a crypto code and a price value: \n/price_alert cryptocode > or < price \n for e.g - /price_alert DOGE > 20  \n /price_alert DOGE < 50'

	context.bot.send_message(chat_id=update.effective_chat.id, text=response)





def priceAlertCallback(context):
    crypto = context.job.context[0]
    sign = context.job.context[1]
    price = context.job.context[2]
    chat_id = context.job.context[3]

    send = False
    spot_price = bitbnsObj.lastPrice(crypto)

    if sign == '<':
        if float(price) >= float(spot_price):
        	send = True
    else:
        if float(price) <= float(spot_price):
        	send = True

    if send:
        response = f'👋 {crypto} has crossed {price} and has just reached {spot_price}!'
        context.bot.send_message(chat_id=chat_id, text=response)



start_value1 = CommandHandler("price_alert", ALERT, pass_args=True)
dispatcher.add_handler(start_value1)
#-------------------------------------------------------#

#-------------------------------------------------------#
def STOP1(update, context):
	user_says = " ".join(context.args)
	c = user_says.split()
	if len(c) == 1:
		if bitbnsObj.cryptoCheck(c[0].upper()):
			job_names = [job.name for job in context.job_queue.jobs()]
			for i in range(len(job_names)):
				if job_names[i] == c[0].upper():
					job = context.job_queue.get_jobs_by_name(c[0].upper())
					job[0].schedule_removal()
					context.bot.send_message(chat_id=update.effective_chat.id, text=f"Price Alert for {c[0]} has been STOPPED!")
					break
			else:
				context.bot.send_message(chat_id=update.effective_chat.id, text=f'No such alert found for {c[0].upper()} please try again!')
		else:
			context.bot.send_message(chat_id=update.effective_chat.id, text='Invalid Crypto Try again!')
	else:
		context.bot.send_message(chat_id=update.effective_chat.id, text='Please Enter Only one Crypto Name to stop alerts. For e.g - /stop BTC \n /stop ETH \n or you can use /stop_all to stop all alerts')




start_value2 = CommandHandler("stop", STOP1, pass_args=True)
dispatcher.add_handler(start_value2)
#-------------------------------------------------------#

#-------------------------------------------------------#
def STOP2(update, context):
	job_names = [job.name for job in context.job_queue.jobs()]
	if len(job_names) > 0:
		for i in range(len(job_names)):
			job = context.job_queue.get_jobs_by_name(job_names[i])
			job[0].schedule_removal()
		context.bot.send_message(chat_id=update.effective_chat.id, text='All Alerts has been STOPPED!')
	else:
		context.bot.send_message(chat_id=update.effective_chat.id, text='No alert found')



start_value3 = CommandHandler("stop_all", STOP2, pass_args=True)
dispatcher.add_handler(start_value3)
#-------------------------------------------------------#

#-------------------------------------------------------#
def allAlerts(update, context):
	job_details = [job.context for job in context.job_queue.jobs()]
	if len(job_details) >= 1:
		for i in range(len(job_details)):
			R='Alert me when: ',job_details[i][0],job_details[i][1],str(job_details[i][2])
			response1=(' '.join(R))
			context.bot.send_message(chat_id=update.effective_chat.id, text=response1)
	else:
		context.bot.send_message(chat_id=update.effective_chat.id, text="No Price alert Found!")



	#print(len(str(job_details)[1:-1]))



start_value4 = CommandHandler("all_alerts", allAlerts, pass_args=True)
dispatcher.add_handler(start_value4)

#-------------------------------------------------------#

#-------------------------------------------------------#
def HELP(update, context):
	reply = "Hi!\n 1 - /live_price - To know live price of all crypto. \n 2 - /price_alert - To set a price alert for any crypto.\n e.g - /price_alert DOGE > 20 or \n /price_alert DOGE < 10\n 3 - /stop - To stop any particular price alert by giving crypto name.\n e.g - /stop DOGE or /stop BTC \n 4 - /stop_all - To stop all price alerts at once. \n 5 - /all_alerts - To see your all alerts you have set. "
	context.bot.send_message(chat_id=update.effective_chat.id, text=reply)


dispatcher.add_handler(CommandHandler("help", HELP, pass_args=True))

#-------------------------------------------------------#

#-------------------------------------------------------#
def response(update, context):
	reply = "Invalid input. Use /help to know all commands."
	context.bot.send_message(chat_id=update.effective_chat.id, text=reply)


dispatcher.add_handler(MessageHandler(Filters.text, response))

#-------------------------------------------------------#


print(bot.get_me())
updater.start_polling()
