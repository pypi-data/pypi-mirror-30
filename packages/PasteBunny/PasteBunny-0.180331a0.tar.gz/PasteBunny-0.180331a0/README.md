# PasteBunny

PasteBunny is a Pastebin API wrapper, the first wrapper I've seen to do the most basic stuff such as storing the user key on its own.

### Features
  - Post pastes
  - Delete pastes
  - Getting user data
  - Getting trending pastes

### TODO
  - Read lists of pastes into PasteBunny.Models.Paste objects
  - Read user data into PasteBunny.Models.User object

### Dependencies

Synchronous client:
```sh
$ pip3 install requests
```
Asynchronous client:
```sh
$ pip3 install aiohttp aiodns cchardet asyncio
```

### Installation

Installation is as easy as running the setup.py, I don't know how to add it to PyPip so..., too bad.

```sh
$ git clone https://github.com/tmjvonboss/PasteBunny.git
$ python3 setup.py install
```

### Examples

Look at the sync_example.py and async_example.py


### Why did I make this?

It just looks better than the other wrappers I have seen, in a bigger project I was to keep track of too many variables and frankly there was no need to have 3 of them related to a Pastebin wrapper, hence these client classes do it somewhere you won't have to worry about it.

Also none of the were using the https API URL's, and this one is
