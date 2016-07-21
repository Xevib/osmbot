[![Build Status](https://travis-ci.org/Xevib/osmbot.svg?branch=master)](https://travis-ci.org/Xevib/osmbot)

OSMbot: OpenStreetMap bot for Telegram
======================================
**OSMbot** is a project maintained by the OpenStreetMap Catalan Community. See [WikiProject Catalan/OSMbot](http://wiki.openstreetmap.org/wiki/Ca:WikiProject_Catalan/OSMbot).

Links
-----

* The *Bot*: https://telegram.me/osmbot. In order to use the *Bot* you need to install a Telegram client in your smartphone or [Telegram Desktop](https://desktop.telegram.org/) in your PC (available for Linux, OS X and Windows). You can find more information about how to install Telegram in the [[Getting Telegram]](https://github.com/Xevib/osmbot/wiki/Getting-Telegram) page on the wiki.

* *Wiki*: https://github.com/Xevib/osmbot/wiki
* *Localization*: https://www.transifex.com/osm-catala/osmbot/

* *Telegram @channel*: https://telegram.me/osmbot_channel with news, tips, etc.
* *Twitter @profile*: [@osmbot_telegram](https://twitter.com/osmbot_telegram)

* *StoreBot page*: https://storebot.me/bot/osmbot

General Usage
-------------

Open a chat in Telegram and send [this link](https://telegram.me/osmbot) or search **@OSMbot**.<br/>
Now, try to send a message similiar as follows:

```
/search Barcelona
```

The bot will answer with a list containing a maximum of ten results.<br/>
Next, you can follow links for `Map` or `/details` command.

```
/details rel347950
```

`/details` command shows the information for relevant tags in OpenStreetMap. In this case, will show info (**details**) for a relation (**rel**) with this particular OSM ID (**347950**).<br/>
You can see the same element in the OpenStreetMap site: http://www.openstreetmap.org/relation/347950 .

In case you want to retrieve more data, you can call the command `/raw`.

```
/raw rel347950
```

`/raw` command forces the *Bot* to send messages with all the available data in the OpenStreetMap database for the particular element.

For more information about general usage and tutorials, you can visit our [OSMbot wiki](https://github.com/Xevib/osmbot/wiki).

Localization
------------

For localization we use the [Transifex](https://www.transifex.com/osm-catala/osmbot/) project. More details about the localization project in wiki page [Localization](https://github.com/Xevib/osmbot/wiki/Localization).

Contact
-------

xbarnada at gmail dot com


