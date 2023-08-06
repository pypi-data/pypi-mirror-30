import os, traceback
from .. project import aliases, construct, load, project
from . import animation
from .. util import json, log


class Collection(animation.Animation):
    """
    A ``Collection`` is a list of ``Animation``s
    """

    @staticmethod
    def pre_recursion(desc):
        animations = []

        for a in desc['animations']:
            loaded = load.load_if_filename(a)
            if loaded:
                animation = loaded.get('animation', {})
                run = loaded.get('run', {})

            elif callable(a) or isinstance(a, str) or 'animation' not in a:
                animation = a
                run = {}

            else:
                animation = a.pop('animation', {})
                run = a.pop('run', {})
                if a:
                    raise ValueError(
                        'Extra fields in animation: ' + ', '.join(a))

            animation = construct.to_type_constructor(
                animation, 'bibliopixel.animation')

            run.update(animation.get('run', {}))
            animation['run'] = run

            # Children without fps or sleep_time get it from their parents.
            if not ('fps' in run or 'sleep_time' in run):
                if 'fps' in desc['run']:
                    run.update(fps=desc['run']['fps'])
                elif 'sleep_time' in desc['run']:
                    run.update(sleep_time=desc['run']['sleep_time'])

            animations.append(animation)

        desc['animations'] = animations
        return desc

    CHILDREN = 'animations',

    def __init__(self, layout, animations=None, **kwds):
        super().__init__(layout, **kwds)
        self.animations = animations or []
        self.internal_delay = 0  # never wait

    # Override to handle all the animations
    def cleanup(self, clean_layout=True):
        self.state = animation.STATE.canceled
        for a in self.animations:
            a.cleanup()
        super().cleanup(clean_layout)

    def add_animation(self, anim, **kwds):
        from .. util import deprecated
        deprecated.deprecated('Collection.add_animation')

        anim._set_runner(kwds)
        self.animations.append(anim)

    def pre_run(self):
        for a in self.animations:
            a.pre_run()


class Indexed(Collection):
    """
    An ``Indexed`` is a :py:class:`bibliopixel.animation.Collection`
    which keeps track of the current animation through an index into the list of
    animations, and gets a callback after that index changes.

    An ``Indexed`` has two properties.

    ``index`` is a mutable property indexing the current animation in the list
    of animations.

    ``current_animation`` returns the animation at position ``index`` or None
    if it is out of the bounds of the ``Collection``.
    """
    _index = -1

    @property
    def index(self):
        """
        :returns int: index of the current animation within the Collection.
        """
        return self._index

    @index.setter
    def index(self, index):
        self._index, old_index = index, self._index
        self._on_index(old_index)

    def _on_index(self, old_index):
        """
        Override this method to get called right after ``self.index`` is set.

        :param int old_index: the previous index, before it was changed.
        """
        if self.current_animation:
            log.debug('%s: %s',
                      self.__class__.__name__, self.current_animation.title)
            self.frames = self.current_animation.generate_frames(False)

    @property
    def current_animation(self):
        """
        :returns: the selected animation based on self.index, or None if
            self.index is out of bounds
        """
        if 0 <= self._index < len(self.animations):
            return self.animations[self._index]


class Wrapper(Indexed):
    # TODO: No unit tests cover any of this.
    @staticmethod
    def pre_recursion(desc):
        if 'animations' in desc:
            raise ValueError('Cannot specify animations in a Wrapper')
        desc['animations'] = [desc.pop('animation')]
        return Collection.pre_recursion(desc)

    def pre_run(self):
        super().pre_run()
        self.index = 0

    @property
    def animation(self):
        # This is used elsewhere in client code.  TODO: pick one or the other!
        return self.current_animation
