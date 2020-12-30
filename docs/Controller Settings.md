# Settings.json
The `settings.json` file is used to contain the settings of the `MapleController` class, below you can find all the optional parameters that can be used within it.

Notes: 
1. The names are case sensitive.
2. An empty default cell means required.

Name | Type | Description | Default
---- | ---- | ---- | ----
`install_origin` | String | The source of your installation, can be either `steam` or `nexon` |
`world` | String | The world your character is in (use this only if you want to use the auto restart system) |
`PIC` | String | Your character's PIC (use this only if you want to use the auto restart system) |
`toggle_pause` | Boolean | The key used to toggle in and out of pause mode | `f5`
`attempt_restart_after_crash` | Boolean | Indication if to attempt restart when the game crashes | `true`
`hyper_teleport` | Boolean | Indication if to attempt to teleport back to the training region after death (using an hyper teleport rock) | `true`
`console_update_period` | Number | The period of which to update the console statistics | 60 (1 minute)
`move_mode` | String | The mode of the movement, can be either `hold` or `teleport` | `hold`
`right` | String | The key of your right movement |
`left` | String | The key of your left movement |
`up` | String | The key of your up movement |
`down` | String | The key of your down movement |
`teleport_right` | String | The key (or key combination, i.e. `right+shift`) used to teleport right (use this only when `move_mode=teleport`) | `None`
`teleport_left` | String | The key (or key combination, i.e. `right+shift`) used to teleport left (use this only when `move_mode=teleport`) | `None`
`teleport_up` | String | The key (or key combination, i.e. `right+shift`) used to teleport up (use this only when `move_mode=teleport`) | `None`
`teleport_down` | String | The key (or key combination, i.e. `right+shift`) used to teleport down (use this only when `move_mode=teleport`) | `None`
`teleport_up_period` | Number | The period of which to teleport up (use this only when `move_mode=teleport`) | 10
`teleport_down_period` | Number | The period of which to teleport down (use this only when `move_mode=teleport`) | 30
`hold_up` | Boolean | Indication if to keep the up key pressed the entire time | `true`
`jump` | String | The key of your character's jump |
`doublejump` | Boolean | Indication if to double jump (press the jump key twice) everytime you jump | `true`
`world_map` | String | The key used to open the world map | `w`
`hp_potion` | String | The key of your HP potion | `None`
`min_potion_hp` | Number | Minimum HP required to take a potion in precent | 50
`mana_potion` | String | The key of your MP potion | `None`
`min_potion_mp` | Number | Minimum MP required to take a potion in precent | 50
`potions_per_use` | Number | The number of potions to take each time (this applies to both HP and MP) | 1
`delay_per_potion` | Number | Delay (in seconds) per potion take | 0
`pet_food` | String | The key of your pet food | `None`
`pet_food_period` | Number | The period of which to take the pet food | 100 (1.4 minutes)
`change_channel_period` | Number | The period of which to change channel | 600 (10 minutes)
`change_direction_period` | Number | The period of which to change direction | 10 (seconds)
`smart_direction` | Boolean | Indicates if the direction of the player is smartly decided (more info below) or is constantly switching between right and left | `true`
`attack` | String | The key of your main attack | 
`attack_repeat` | Number | The number of attacks (key presses) to perform each time you attack | 5
`attack_interval` | Number | The delay (in seconds) between each of the key presses | 0.25
`buffs` | List\<String\> | A list of strings where each string is a key for a buff | `[]` (empty list)
`buffs_interval` | Number | The delay (in seconds) between each buff's keypress | 0.5
`buffs_period` | Number | The period of which to activate the buffs | 50 (seconds)
`skills` | List<{}> | A list of dicts where each dict is a skills containing `key`, `period` and (optional) `hold` | `[]`
`skills_interval` | Number | The delay between skill keypress | 0.25
`spawn_skills` | List<{}> | A list of skills to activate on spawn (death respawn or crash) | `[]`
`spawn_skills_interval` | Number | The delay between skill keypress | 0.25

# Move mode
Move mode dictates the mode of which to move the player, currently the available modes are: 
- `hold`: Leaving the direction key pressed until direction change to keep the player constantly moving.
- `teleport`: Constantly teleports the player, make sure to set all teleportation keys (i.e. if `up+shift` teleport you up than set this as your `teleport_up` key). this would also overwrite `hold_up` to `false`.

# Smart direction
When smart direction is enabled the player will be constantly guided into the center of the map, this feature will overwrite `change_direction_period` to 0.

![alt text](https://raw.githubusercontent.com/tomergt45/MapleController/main/docs/Smart%20direction%20example.png)

In the example the yellow circle is you (the player), using smart direction will ensure that you are always within the red square, which is created using the center of the two portals (blue circles) + x% for each side (by default it is 25%)
