import smtplib
import random
import string

def send_mail(retriever, retriever_password):
    sender = "uselesstestmailforpython@gmail.com"
    password = "qheiessbrscwwaae"
    reciever = retriever
    message = f"Subject: Retrieve password\n\nHere is your new password: {retriever_password}\nDont forget it next time!"
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as connection:
        connection.login(sender, password)
        connection.sendmail(sender, reciever, message.encode())

def generate_password():
    password_list = []

    [password_list.append(random.choice(string.ascii_letters)) for _ in range(random.randint(8, 10))]
    [password_list.append(random.choice(string.digits)) for _ in range(random.randint(2, 4))]
    [password_list.append(random.choice(string.punctuation)) for _ in range(random.randint(2, 4))]
    random.shuffle(password_list)
    password = "".join(password_list)
    return password