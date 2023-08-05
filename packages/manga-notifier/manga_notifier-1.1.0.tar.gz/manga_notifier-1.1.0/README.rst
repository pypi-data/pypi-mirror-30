manga-notifier
--------------

manga-notifier is a command-line tools to send osx notifications when a
new chapter of manga is released (www.mangastream.com)

Setup
-----

First you need to install
```terminal-notifier`` <https://github.com/alloy/terminal-notifier>`__.

Via `Homebrew <https://github.com/Homebrew/homebrew>`__:

::

    $ brew install terminal-notifier

Then:

::

    $ pip install manga-notifier

Or:

::

    $ pip3 install manga-notifier

Usage
-----

First, add your favorite manga and the last chapter. (see
```Mangastream`` <http://www.mangastream.com>`__)

::

    $ manga-notifier add "One piece"

Then:

::

    $ manga-notifier

If there is a new chapter, you will receive a notification. Click on the
notification and it will open the chapter in a browser.

Other commands
~~~~~~~~~~~~~~

Of course, you can delete a favorite

::

    $ manga-notifier delete "One Piece"

You can list all your favorites. It will display the last chapter for
each favorite.

::

    $ manga-notifier list

Finally, you can download the last chapter of your favorite

::

    $ manga-notifier download "One Piece"

Or Download all

::

    $ manga-notifier download --all

All chapter will be stored on the Desktop.

Other usage
~~~~~~~~~~~

You can add it to your .bashrc. In that case, each time you open a
terminal, it will check new release of your favorite manga.

Or you can add it in your crontab.
