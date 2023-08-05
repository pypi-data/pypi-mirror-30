==================================================
Python wrapper for the Battlegrounds Developer API
==================================================
`Battlegrounds Developer API Docs <https://developer.playbattlegrounds.com/docs/en/introduction.html>`_

************
Installation
************

.. code-block:: bash

    pip install pubg

***************
Usage
***************

Setup
=====
.. code-block:: python

    from pubg import Battlegrounds, Region

    battlegrounds = Battlegrounds(api_key='API_KEY', region=Region.pc_na)

Match Data
==========
.. code-block:: python

    matches = battlegrounds.matches()

    print(matches.id)
    print(matches.created_at)
    print(matches.duration)

    for roster in matches.rosters:
        print(roster.id)

        for participant in roster.participants:
            print(participant.id)
            print(participant.actor)
            print(participant.shard_id)

        print(roster.won)
        print(roster.shard_id)

    for asset in matches.assets:
        print(asset.id)
        print(asset.title_id)
        print(asset.shard_id)
        print(asset.name)
        print(asset.description)
        print(asset.created_at)
        print(asset.filename)
        print(asset.content_type)
        print(asset.url)

    print(matches.game_mode)
    print(matches.patch_version)
    print(matches.title_id)
    print(matches.shard_id)

Status
======
.. code-block:: python

    status = battlegrounds.status()

    print(status.id)
    print(status.released_at)
    print(status.version)

More will be available as I get more information about the API