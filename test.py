import smtplib

sender = 'akshayakzzz.777@gmail.com'
password = 'hkohicjvpgngauqy'
receiver = 'akshaysajong@gmail.com'

message = """From: Test <your-email@gmail.com>
To: <recipient@example.com>
Subject: SMTP Test

This is a test message.
"""

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, receiver, message)
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
finally:
    server.quit()