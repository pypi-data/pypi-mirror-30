.. This is an RST comment.
   The following directives, when used at the top of the file, set default
   values for all slides:

   This sets the transition style.  Values are: 'dissolve', 'pan',
   'tilt', or 'cut'.  The optional argument of 'duration' sets the
   duration of the transition in seconds (0.4 seconds by default).
   The same syntax may be used within a slide to override these
   transition for that slide alone.

   .. transition:: dissolve
      :duration: 0.4

   This disables display of the title.  Each slide must still have a
   title, and it will be used by the presenter console, but it will
   not be displayed on the slide.  The same syntax may be used within
   a slide to hide the title of that individual slide.

   .. hidetitle::

.. Slides are defined one at a time by starting a new top-level
   section:

Presentty
=========
.. container:: handout

   Content that is placed in a container called "handout" will not be
   displayed with the slides, but will be displayed on the presenter's
   console.

Presentty is a console presentation system where slides are
authored in reStructuredText.

Use the arrow keys to navigate between slides, or ``q`` to quit.

Bullet Lists
============
It is able to display lists of items:

* Pork

  * Eastern North Carolina
  * Lexington

* Ribs
* Brisket


Progressive Display
===================
Bullet lists may include a *progressive* display:

.. container:: progressive

  * Red Leicester
  * Tilsit
  * Caerphilly


Table
=====

=== ===
 p  !p
=== ===
 T   F
 F   T
=== ===

Line Blocks
===========
|
| I bring fresh showers for the thirsting flowers,
|     From the seas and the streams;
| I bear light shade for the leaves when laid
|     In their noonday dreams.
| From my wings are shaken the dews that waken
|     The sweet buds every one,
| When rocked to rest on their mother's breast,
|     As she dances about the sun.
| I wield the flail of the lashing hail,
|     And whiten the green plains under,
| And then again I dissolve it in rain,
|     And laugh as I pass in thunder.
|

(From "The Cloud", Percy Bysshe Shelley)

Dissolve Transition
===================
Transitions may be "dissolve," where one slide cross-fades into the next...

Pan Transition
==============
.. transition:: pan

...or "pan," where the slides appear horizontally adjacent and move
right to left...

Tilt Transition
===============
.. transition:: tilt

...or "tilt," where the slides appear vertically adjacent and move
bottom to top...

Cut Transition
==============
.. transition:: cut

...or "cut," where they abruptly change from one to the next.

Syntax Highligting
==================
Pygments is used to provide syntax highlighting of code in almost any
language:

.. code:: python

  class UrwidTranslator(nodes.GenericNodeVisitor):
    def depart_Text(self, node):
        if self.stack and isinstance(self.stack[-1], 'string'):
            # a comment
            if self.attr:
                t = (self.attr[-1], node.astext())
            else:
                t = node.astext()
            self.stack[-1].append(t)
    visit_literal_block = visit_textelement

Cowsay
======
.. cowsay:: Presentty is a console-based presentation program where
            reStructuredText is used to author slides.

| If cowsay is installed, it can easily
| be used to display text.

Figlet
======
.. container:: handout

   Cowsay and figlet are non-standard directives and will not appear
   if the RST file is rendered with a program other than presentty.
   If you want to ensure that the content appears in all forms, you
   may wish to run the respective commands manually and copy the
   output into a quoted block in the RST file.

.. figlet:: FIGLET

| If figlet is installed, it can be
| used to provide large text.

ANSI Art
========
.. hidetitle::
.. container:: handout

   Note that the ansi directive is specific to presentty, and so if an
   RST file that includes it is rendered with another program,
   included ANSI files will not appear.

.. ansi:: ansi.ans


Nice filesystem listings
========================

.. container:: handout

   You can cut and paste the output of tree to make nice filesystem listings.

.. code::

   files
   ├── hello
   └── world

0 directories, 2 files

Images
======
.. container:: handout

   The standard sphinx image directive can be used to include bitmap
   images (such as JPEG or PNG files) which will be automatically
   converted to ANSI art for display.  This feauter requires that PIL
   or Pillow (Python Image Library) and jp2a be installed.

.. image:: gg.jpg

"Golden Gate Bridge" by Kevin Cole (CC-BY: https://flic.kr/p/7L2Rdu)

Scaling Images
==============
.. container:: handout

   You can also give the image directive a scale parameter to scale the image.
   the image will be centered within the slide.

.. image:: gg.jpg
   :scale: 75

"Golden Gate Bridge" by Kevin Cole (CC-BY: https://flic.kr/p/7L2Rdu)
