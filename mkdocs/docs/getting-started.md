!!! note
    EnduraBot was made for a *specific* Discord server for a *specific* group of friends. This is relevant for configuration, as specific channels and roles are expected to exist for full functionality.

The following will explain how to set up an environment to locally host an instance of EnduraBot on your machine.

## Requirements
Before starting please ensure the following requirements are met.

- [Python 3.13](https://www.python.org/) or greater
- [Git](https://git-scm.com/install/)
- [Discord bot token](https://discord.com/developers/applications)
- Have the `Administrator` permission on a Discord server. It's advised to create a server for the purpose of working with EnduraBot.

## Cloning the repository
!!! info
    This will automatically create a directory called `EnduraBot` and place all code inside of it.

In a terminal, navigate to the desired directory to host EnduraBot's code and execute the following:
``` sh
git clone https://github.com/sirdog9001/EnduraBot.git
```

## Environment Variables
!!! danger
    Your real `.env` file with the `guild` and `token` should *never* leave your machine and/or wherever EnduraBot is being hosted. It absolutely should *not* be committed to any remote repository.

Take `.env-example`, copy it, and rename to `.env`. This expects 2 variables:

```sh
guild=
token=
```

The `guild` is the Discord ID for the server that you want EnduraBot to join. EnduraBot will leave any server that does not match this ID.

The `token` is the bot token you got from Discord's developer portal. Please research online as to how to obtain this.

## Local setup
Navigate to `data` and notice that 3 JSON files exist here.

```
|──data/
|   |──misc_text_example.json
|   |──permissions_example.json
#   └──variables_example.json
```

Copy and paste them all into `data` and rename them to remove the `_example`. 

For the purposes of getting started, `misc_text.json` may be left alone. If you have the `Adminsitrator` permission you may also do this with `permissions.json`. An alternative is to blank the file entirely, though be warned that this means anyone on the server can use any command. If neither options are viable, review the documentation on permissions at XXX.

### variables.json 
For EnduraBot to work, the following variables need proper IDs added. Click the circles with a plus in them for an explanation.

``` json title="variables.json"

{
    "out_of_context_channel_id": 1426036432195289160, //(1)!
    "alert_channel_id": 1426036519692669042, //(2)!
    "based_chat_channel_id": 1426036403506118656, //(3)!
    "sysop_role_id": 1426035389214232656, //(4)!
    "mod_role_id": 1426035365671731292, //(5)!
    "admin_role_id": 1426035308297715742, //(6)!
    "cooldown_exempt_roles": [ //(7)!
        1426035365671731292,
        1426035308297715742
    ]
}

```

1. Channel with messages placed in quotations that represent things people have said out of context; to be used by the `/rquote` and daily bible quote feature.
2. Channel where a message is sent when running `/alert`.
3. Channel where daily bible quotes should be sent.
4. Role that represents a member that runs technical stuff for the community. Used in `/info` to denote the person is a systems operator, is the role pinged by `/alert`, and is used as an exemption criteria for the `alert_detection.py` listener.
5. Role that represents a server moderator. Used by `/info` to determine if the member is a staff member.
6. Role that represents a server administrator. Used by `/info` to determine if the member is a staff member.
7. List of role IDs that bypass the `/rquote` cooldown.

There is also a list of key value pairs at variable `mod_editable_roles`. 

```json title="variables.json" 
"mod_editable_roles": {
        "dummy_role_a": 1122334455667788990,
        "dummy_role_b": 2233445566778899001,
        "dummy_role_c": 3344556677889900112
    }
```

The keys (e.g `dummy_role_a`) serve no programmatic purpose and are there purely for readability. The IDs should be role IDs that you'd like `/editrole` to be able to manipulate, otherwise it will never function.

Other variables can be configured to your liking and are documented more properly at XXX.

### Logs folder
EnduraBot does all logging to files. While it will automatically create the relevant files on startup it will *not* create the *directory* it expects them in. 

Simply create a directory called `logs` in the same directory as `main.py`.

## Python dependencies
!!! info
    You may wish to install these dependencies in a virtualized environment rather than your master Python environment.

Per `requirements.txt` there are 2 dependencies required for EnduraBot to run. You may install them by running the following from within the directory housing the text file:
``` sh
pip install -r requirements.txt
```

## Invite the bot
By this point everything on the coding side is done. But before you run the bot, you need to invite it to the server that you set in the `.env` variable mentioned above, otherwise you will get scary errors.

## Running the bot
By this point everything should be set for the bot to run properly. To run it, execute the following command in a terminal that is running in the directory that houses `main.py`

```sh
python main.py
```

You should see something like this:
``` py hl_lines="7"
[20XX-XX-XX XX:XX:XX]:INFO:endurabot: Loaded cogs.bible_daily
[20XX-XX-XX XX:XX:XX]:INFO:endurabot: Loaded cogs.bot_react
[20XX-XX-XX XX:XX:XX]:INFO:endurabot: Loaded cogs.user_cmds
[20XX-XX-XX XX:XX:XX]:INFO:endurabot.cogs.bible_daily: Waiting for bot to be ready before starting daily bible quote loop...
[20XX-XX-XX XX:XX:XX]:INFO:endurabot.cogs.bible_daily: Bot ready, starting daily bible quote loop.
[20XX-XX-XX XX:XX:XX]:INFO:endurabot: Synced 11 commands.
[20XX-XX-XX XX:XX:XX]:INFO:endurabot: Hello, world! I am awake and ready to work!
```

Once you see the highlighted line the bot is functioning and ready to go.
