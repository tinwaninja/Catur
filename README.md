# Bot Auto Chess.com
Is a suggestion for chess moves on the chess.com platform. The available features are: chess suggestions and moves automatically.

## installation (Windows)

1. Install Python <br />
You can install it here [Python](https://www.python.org/downloads/). Don't forget to tick (Add Python to PATH)  ![Install Python](./documentation/python_install.jpeg) <br />
To check that Python has been successfully installed, open CMD and type "python", if python is run successfully then Python is successfully installed, but if directed to the Windows Store please solve it by following the advice from [stackoverflow](https://stackoverflow.com/questions/58754860/cmd-opens-window-store-when-i-type-python).
2. Clone Repository <br />
Install [Git](https://git-scm.com/download/win) in Windows, then run the command below:
```
cd C:\Users\USERNAMEWINDOWS\Desktop
git clone https://github.com/tinwaninja/Catur.git
cd Catur
pip install -r requirements.txt
```
3. Install Firefox <br />
To use this script you will need a browser [Mozilla Firefox](https://www.mozilla.org/en-US/firefox/new/).
## Setting up
1. Create an account <br />
Create an account on chess.com, by registering mode **beginner**. <br />
It is recommended to create a username with 5 words and 2 numbers, for example: abcde11 <br />
Confirm registration email.
2. Enter Credentials <br />
Open the file C:\Users\USERNAMEWINDOWS\Desktop\Catur\akun.txt <br />
Change your username and password credentials.
## Start
Open CMD (Administrator mode recommended), then run the command: <br />
```
cd C:\Users\USERNAMEWINDOWS\Desktop\Catur
python catur.py
```
The script will automatically open Mozilla Firefox and automatically login based on existing credentials. <br />
Next, start the match (Live Match).
![Auto Chess](./documentation/Catur.gif) <br />
## Additional
You can change the movement speed of chess moves by changing the value of the mode in the catur.py script on line 19 with the value 'bullet', 'blitz', or 'rapid'. <br />
If you want to find automatic live matches, change the config.ini file and change autostart = 0 to autostart = 1.
### Update
1. First Commit <br />
project published.
2. V2 Commit<br />
automatically run the pawn (if it gets white). <br />
add mode, mode there are 3 options, namely: bullet, blitz, rapid. bullet for quick-paced 1-minute matches, blitz for 3-5-minute matches, rapid for 10-minute matches. <br />
increase the delay, if the game is early then the delay is with a small time value, if it is in the middle of the game then the delay will be a choice of time with a small and medium value
3. V3 Commit<br />
Fixed being stuck looking for new matches.<br />
Fixed a stuck in skip aborted match.<br />
Automatically accept the challenge (rematch).<br />
4. V4 Commit<br />
Skip requests for rematch in the match if your opponent is too weak (unbalanced).<br />
Skip rematch requests if you lost in the previous match.<br />
Accept the challenge if the player against the chess match.<br />
5. V5 Commit<br />
Automatically takes the pawn promotion to queen. (Private in the catur.py script on line 144)<br />
## Thanks
This script is made from libraries and fixes existing scripts. In developing this script I am very grateful to:
1. [StockFish](https://stockfishchess.org/download/)
2. [ChessBot Linux](https://github.com/kraten/chessbot)
3. VIP-Spuc3ngine

## Disclaimer
This is purely for educational purposes, I am not responsible for misuse of the script.