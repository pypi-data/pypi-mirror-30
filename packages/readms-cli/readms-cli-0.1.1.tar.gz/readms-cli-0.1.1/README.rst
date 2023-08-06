********
Overview
********
A cli tool for downloading latest manga on https://readms.net

Installation
============
.. code-block:: bash

 $ pip install readms-cli

Usage
============

* List latest manga on readms

  .. code-block:: bash

   $ readms latest
* Download manga, Note: Run "readms latest" first to see available manga for download

  .. code-block:: bash

   #Template $ readms download "${name}"
   #Examples
   $ readms download "Boruto"
   $ readms download "One Piece"
