toyblock3
=========

Yet another Entity-Component System in the Python way.

Install
-------

Install toyblock3 with *pip*

.. code::

    pip install toyblock3

Example of use
--------------

.. code:: python

    import toyblock3

    PhysicsSystem(toyblock3.System):
        def __init__(self, dt):
            super().__init__()
            self.dt = dt
        def _update(self, entity):
            entity.body.x += self.dt+32.
            entity.body.y += self.dt+32.

    PitSystem(toyblock3.System):
        def _update(self, entity):
            if entity.body.y < 0.:
                entity.free()

    SpriteSystem(toyblock3.System):
        def _update(self, entity):
            position = (entity.body.x, entity.body.y)
            entity.sprite.set_position(position)

    physics_system = PhysicsSystem(1./60.)
    pit_system = PitSystem()
    sprite_system = SpriteSystem()

    class Player:
        SYSTEMS = (physics_system, pit_system, sprite_system)
        Body = MyBody
        def __init__(self, x=0., y=0.):
            self.body = self.Body()
            self.sprite = Sprite("hero")
        def reset(self):
            self.body.x = 32.
            self.body.y = 32.

    # Players start at 32., 32.
    player_manager = toyblock3.Manager(Player, 4, 32., 32.)
    player = player_manager()
    playing = True
    while playing:
        input(player)
        physics_system()
        pit_system()
        sprite_system()

Tests
-----

Run the tests with

.. code::
    
    python3 -m unittest tests.py

License
-------

.. image:: https://www.gnu.org/graphics/lgplv3-147x51.png
    :alt: LGPL-3.0
