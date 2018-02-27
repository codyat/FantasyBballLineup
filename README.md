# FantasyBballLineup

This is a script that will update your ESPN Fantasy Basketball lineup.

You will need to provide this script with parameters:
   1. Your League ID
   2. Your Team ID
   3. Your Season ID
   4. Your ESPN Username
   5. Your ESPN Password
   6. Your Personal Email address
   7. Notification Email address
   8. Notification Email's Password

For Example:
`./AutoLineup.py 123456 1 2018 my_username@gmail.com my_password my_email@yahoo.com FantasyBasketballNotification@gmail.com notification_password`

I recommend wrapping all this into a bash script ad simply running something like:
`./setMyLineup.sh`
where the contents of setMyLineup.sh look similar to:
`#!/bin/bash

leagueid=123456
teamid=1
seasonid=2018
username=my_username@gmail.com
password=my_password
email=my_email@yahoo.com
notif_email=FantasyBasketballNotification@gmail.com
notif_email_pw=notification_password

./AutoLineup.py $leagueid $teamid $seasonid $username $password $email $notif_email $notif_email_pw`
