# ClassicBot
ClassicBot was designed to enhance Classic World of Warcraft communities by allowing them to link directly to in game tooltips in their discord servers. Now when you get the final piece to craft "Sulfuras, Hand of Ragnaros", but no one is online to see your achievement you can link the item straight into discord so that as many eyes as possible can see the item in all its wonderful glory.

![build](https://travis-ci.org/mikeStr8s/ClassicBot.svg?branch=master) 
[![codecov](https://codecov.io/gh/mikeStr8s/ClassicBot/branch/master/graph/badge.svg)](https://codecov.io/gh/mikeStr8s/ClassicBot)
![version](https://img.shields.io/badge/version-v0.2.5-blue.svg)

## Overview
ClassicBot functionality is pretty straight forward, you input a command and get responses back depending on the input.

**Current Commands:**
- `!item` *item name* - Requests the tooltip of the supplied item name
- `!ability` *ability name* - Requests the tooltip of the max rank version, if ranked, of the supplied ability name

## Usage
`!item` *sulfuras, hand of ragnaros*

![Sulfuras, Hand of Ragnaros](https://github.com/mikeStr8s/ClassicBot/blob/master/docs/sulf.PNG?raw=true)

`!ability` *frostbolt*

![Frostbolt](https://github.com/mikeStr8s/ClassicBot/blob/master/docs/fros.PNG?raw=true)


## Feature Requests
Please direct all feature requests to the issues section of this repository, or click [here](https://github.com/mikeStr8s/ClassicBot/issues/new).

## Roadmap
There are a lot of features that I would still like to have be a part of this bot. Many of the pieces and parts of this bot rely on outside sources and so I am restricted to what these sources provide.

**Future features include, but are not limited to:**
- Allowing specific ranks of abilities to be queried by users.
- Allowing talents, and their ranks to be queried by users.
- Replace command specific queries with a dynamic "build your own" style.
  - `!classic` **weapon** *nightfall*
  - `!classic` **spell** *rain of fire* rank 1

## Contribution
Contribution information will be added once an official v1.0.0 of ClassicBot is released.

## Contributors
- MikeStr8s *(Owner/Maintainer)*
- Squatticus *(Web Designer)*
