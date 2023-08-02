# clone-arg-logger
This repository contains a Python project allowing you to log chat and
leaderboard of the Clone Clicker game at
https://www.goingtostealyourchannelifyouclickthis.com/CloneClicker.html

The Clone Clicker game by Coffee and Chomperling is part of the Clone Wars ARG
(2023) by Jonny RaZeR, Phaleur, Joe Caine, RoyalPear, Danno Cal Drawings and
Bundun.

This code is licenced under MIT.

## Results of the logger
The logger for season 1 has ran from 2023-07-26T01:06:11Z to
2023-07-31T13:18:22Z with some interruptions due to logger updates. You can use
the timezone converter on timeanddate.com to find the time in your time zone.

The raw dataset is kind of corrupted. All versions of the logger were supposed
to write to the same file. But I wasn't aware that the default encoding wasn't
utf-8. So some of the file is UTF-8 and some of it isn't and some of it is
literally corrupted.

However, as the leaderboard lines were by definition ASCII I have a good
dataset for that.

If you just want to read messages, I have a Discord server to which all of it
was logged. And of course no encoding issues there.

In any case, if you want to work on the dataset, contact @milklineep on Discord
with a short pitch for your idea, and we can discuss further.