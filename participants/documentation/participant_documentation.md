# Getting Set Up

The following steps will help you get set up for Minecraft Utopia.


## Set up instructions


### Connecting to an Online Server

If you don't know which version of Minecraft you own, you can find out from one or all of the following:
- If you're on anything but a computer or laptop (i.e. tablet, phone, console), it's **Bedrock Edition**.
- If you're on a computer or laptop, login to the game and on the homescreen check where the version number is:
     - On **Bedrock Edition**, it's on the bottom-right.
     - On **Java Edition**, it's on the bottom-left.
- If you see your character on the right, and a "Marketplace" button, it's **Bedrock Edition**. 


#### Minecraft: Bedrock Edition

1. Log into Minecraft and click "Play" on the main menu.
2. Click "Servers" from the tabs on the top.
![See Example](https://user-images.githubusercontent.com/56898088/123838480-0ac3b400-d8da-11eb-98ba-df1838f1f8ac.png)

4. Scroll down past the "Featured Servers", to reach "Additional Servers".
![See Examples](https://user-images.githubusercontent.com/56898088/123838581-229b3800-d8da-11eb-9e0a-6a1d0e80ec9b.png)

5. Click "Add Server", and enter:

      **Server Name:** Minecraft Utopia

      **Server Address:** 192.81.211.221

      **Port:** 19132

![See Example](https://user-images.githubusercontent.com/54556405/123692297-a7c41580-d824-11eb-9af2-da2efdd33a1a.PNG?raw=true)


#### Minecraft: Java Edition

> *Note: To access a server you need to a version of Minecraft that is at least 1.16. For more information, see [Changing game version](https://help.minecraft.net/hc/en-us/articles/360034754852-Changing-game-versions-).*
`The Minecraft Utopia server runs on 1.16.5`. To join the server, your client will need to be updated to at least a version that is 1.16, though 1.16.5 is ideal.
*You'll be able to connect with a client updated to 1.17, though none of the new features will be present.*


##### Connect to the Server

1. Log into Minecraft and click "Multiplayer" on the main menu.  

2. Click "Add Server" and enter the IP or web address of the server.

      **Server Name:** Minecraft Utopia

      **Server Address:** 192.81.211.221:25566

![See Example](https://user-images.githubusercontent.com/54556405/123692677-1b662280-d825-11eb-892b-c5c1bfa692df.png?raw=true)


## About this server

If you're familiar with Minecraft already, here's what's different.

### GeyserMC/Floodgate

Geyser is a proxy which allows for true cross-platform play between *Minecraft: Bedrock Edition* and *Minecraft: Java Edition* servers.

> With Geyser being a protocol translator between two different games with two different codebases, there are a handful of limitations that Geyser is unfortunately unable to handle. Despite Minecraft Bedrock and Java being quite close in comparison, there are some vast differences in many areas. [@Geyser_MC](https://github.com/GeyserMC/Geyser)

The following things cannot be fixed without changes to Bedrock or the Java protocol in general. As of now, they are not fixable in Geyser.

- Custom heads in inventories
- Clickable links in chat
- Glowing effect
- Crafting in the 2x2 menu while in creative mode
- Distinguishing between left and right clicks in inventories
- Redstone dot blockstates
- "Can be placed on/destroyed" tag for *some* blocks - for example, different colors of clay/wool that don't exist as separate blocks
- Potion colors implemented using NBT
- Various command arguments for any command that doesn't use the Minecraft Brigadier library
- Unable to see banner layers past 6
- Movement issues around bamboo due to offset differences between Java and Bedrock
- Custom anvil recipes
- Heights lower than 0 or above 256 on non-beta versions of Bedrock
- Dolphin's Grace potion effect visuals (effects should still work correctly)
