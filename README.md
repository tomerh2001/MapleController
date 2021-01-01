# AFK Bot
A less-detectable, easy to use MapleStory bot using fancy computer vision and clever coding. Train while you're AFK, farm mesos, boost main/secondary characters and more!

**Note: this is not cheats by any means, this bot does not access the game's memory data or files.**

## Download
A download link will be added in the near future.

## Features
- Auto crash detection, restart & login
- Move & attack
- Use skills
- Predict time to rankup
- Activate buffs periodically
- Take potions (HP, MP & Pet)
- Change channels
- Avoide players (by changing channel, to ensure not getting reported)
- Activate ruins
- Teleport back after death (using hyper teleport rock)
- Settings per character

### Upcoming features
- Kanna follower
- In-game overlay
- Email notifications
- And much, much more!

## Setup
1. Download the files using the download link above and extract all of them into the same folder

<img src="https://raw.githubusercontent.com/tomergt45/MapleController/main/docs/images/Download folder.png" alt="alt text">

- Open the `settings.json` file, this file will contain all the insutrctions for the bot, make sure to adjust everything according to your character, if you plan on using the bot with multiple characters than create a `.json` file for each character and name it accordingly, for example `Kanna Settings.json`, `Shade Settings.json`, etc...

- By default the `settings.json` that you download will contain only the default parameters and would look like that:

```
{
  "install_origin": "steam",
  "world": "bera",
  "PIC": "password",
  "hold_up": false,
  "right": "right",
  "left": "left",
  "up": "up",
  "down": "down",
  "jump": "alt",
  "hp_potion": "delete",
  "mana_potion": "insert",
  "pet_food": "end",
  "attack": "d",
  "buffs": [],
}
```


2. While using the bot, maplestory MUST be on 800x600 (4:3) windowed
<img src="https://raw.githubusercontent.com/tomergt45/MapleController/main/docs/images/Resolution.png" alt="alt text" width="500" height="500">

3. Disable UAC (only if you use the auto restart feature).
This is because when maplestory is launched, you are prompted with an admin privileges dialog, this dialog cannot be accepeted via code so in order to automate the process you'll need to disable it while using the bot.

- Search "UAC" in the windows search

  <img src="https://raw.githubusercontent.com/tomergt45/MapleController/main/docs/images/UAC1.png" alt="alt text" width="500" height="500">

- Set it to "Never notify me ..."

  <img src="https://raw.githubusercontent.com/tomergt45/MapleController/main/docs/images/UAC2.png" alt="alt text" width="500" height="500">
