# Quickly add users to CrashPlan

Quickly add users to both the `atlasCrashPlanUsers` AD group and to the ATLAS org on the CrashPlan server.

## Usage

### Initial authentication

```
$ ./atlas-cp
Username: <admin netid>
Password <admin password>
```

This drops you into a `cp>` prompt.

### Find users

```
cp> find user szuta
username   | name                      | org        | AD? | Active?
--------------------------------------------------------------------------------
su-szuta   | su-szuta Szuta            | ATLAS      | Y   | Y
szuta      | Patryk Szuta              | ATLAS      | Y   | Y
```

### Add users
```
cp> add user rezk atlas
Added rezk to our AD group
Sleeping for 5 seconds
User added to CP with userUid 3axxxx1a5fyyyybb
```

*Note*: Sometimes you will receive an error because the 5 second delay wasn't log enough for the AD to sync.
In that case simply up-arrow and try the command again:

```
cp> add user rezk atlas
Added rezk to our AD group
Sleeping for 5 seconds
Error communicating with CP server
Error occurred
cp> add user rezk atlas
Added rezk to our AD group
Sleeping for 5 seconds
User added to CP with userUid 3axxxx1a5fyyyybb 
cp>
```

### Exit
Ctrl-C
