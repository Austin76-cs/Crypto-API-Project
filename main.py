from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import smtplib
from datetime import datetime
import schedule
import time

url = 'https://pro-api.coinmarketcap.com/v1/'
endpoint = 'cryptocurrency/quotes/latest'
api_key = "c11b110a-bff2-4d34-bd5d-534c56255bfd"
parameters = {
  'symbol':'ETH',
  'convert':'USD'
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': 'c11b110a-bff2-4d34-bd5d-534c56255bfd',
}
file_name = "eth_price.json"

session = Session()
session.headers.update(headers)


def save_price_to_json(file_name, price):
    # Prepare the data to save
    data = {
        "timestamp": datetime.now().isoformat(),
        "last_price": price
    }
    
    # Write the data to the JSON file
    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)
    print("last_price saved to JSON file.")

# Reading the last saved price from the JSON file
def read_price_from_json(file_name):
    with open(file_name, "r") as file:
       data = json.load(file)
       return data["last_price"]

def calc_email():
  #Gets DATA from API
  try:
    response = session.get(url + endpoint, params=parameters)
    data = json.loads(response.text)
    price = data['data']['ETH']['quote']['USD']['price']
  except (ConnectionError, Timeout, TooManyRedirects):
    print("Error couldnt fetch API data")
  
  #Saves last price then updates it to current price
  last_price = read_price_from_json(file_name)
  save_price_to_json(file_name, price)

  #Calcs price change and sends email
  if last_price:
    percentage_change = ((last_price - price) / last_price) * 100
    if percentage_change >= 10:
        sender = "neoncryptoapitest@gmail.com"
        receiver = "neoncryptoapitest@gmail.com"
        password = "cctw itvw bomk zluj"
        subject = "Crypto Prices"
        body = f"There was a {percentage_change} drop in price this last week"

        message = f"""From: {sender}
        To: {receiver}
        Subject: {subject}\n
        {body}
        """
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        try:
          server.login(sender, password)
          print("Logged in...")
          server.sendmail(sender, receiver, message)
          print("Email has been sent")
        except smtplib.SMTPAuthenticationError:
          print("Error: Unable to sign in")
    else:
          print("No big change :( )")
          
schedule.every(20).seconds.do(calc_email)
# Keep the script running to execute the scheduled task
while True:
    schedule.run_pending()
    time.sleep(1)  # Sleep to avoid high CPU usage

