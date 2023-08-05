.. role:: raw-html-m2r(raw)
   :format: html


**\ ``/n``\ ** or **\ ``/nick``\ ** changes your nickname\ :raw-html-m2r:`<br>`
``/n SparTacus``

**\ ``/j``\ ** or **\ ``/join``\ ** enters a chatroom\ :raw-html-m2r:`<br>`
``/j #music``

**\ ``/p``\ ** or **\ ``/part``\ ** leaves the chatroom

**\ ``/t``\ ** or **\ ``/topic``\ ** changes the channel topic\ :raw-html-m2r:`<br>`
``/t electro swing``

**\ ``/me``\ **\ , the single mandatory feature anywhere\ :raw-html-m2r:`<br>`
``/me regrets adding this``

**\ ``/m``\ ** or **\ ``/msg``\ ** sends a private message\ :raw-html-m2r:`<br>`
``/msg SparTacus stop stealing my nick``

**\ ``/q``\ ** or **\ ``/quit``\ ** disconnects your client

info
====

**\ ``/help``\ ** displays these help pages

**\ ``/na``\ ** or **\ ``/names``\ ** shows a list of people in the channel

**\ ``/st``\ ** or **\ ``/status``\ ** shows info about online users

**\ ``/cmap``\ ** shows a list of colour codes

control
=======

**\ ``/r``\ ** or **\ ``/redraw``\ ** redraws the screen to fix corruption, use this if things are glitchy after resizing the window

**\ ``/by``\ ** and **\ ``/bn``\ ** turns on/off audible alerts when someone mentions your name

**\ ``/sw``\ ** and **\ ``/sh``\ ** sets the terminal width/height in case the detection fails\ :raw-html-m2r:`<br>`
``/sw 80``\ :raw-html-m2r:`<br>`
``/sh 24``

**\ ``/ss``\ ** sets the PgUp/PgDn scroll amount

.. list-table::
   :header-rows: 1

   * - 
     - 
   * - ``/sh 0``
     - entire screen
   * - ``/sh 10``
     - 10 lines
   * - ``/sh 50%``
     - half the screen


navigation
==========

**\ ``/a``\ ** jumps to the oldest unread message across all your channels

**\ ``/3``\ ** jumps to your 3rd window

**\ ``/u``\ **\ , **\ ``/up``\ **\ , **\ ``/d``\ **\ , **\ ``/down``\ ** are PageUp/PageDown for clients where the PgUp/PgDn buttons are busted

**\ ``/l``\ ** or **\ ``/latest``\ ** scrolls to the bottom of the chat window

**\ ``/g``\ ** or **\ ``/goto``\ ** jumps to a point in the past

.. list-table::
   :header-rows: 1

   * - 
     - 
   * - ``/g 19:47``
     - jump to time
   * - ``/g 2018-01-21``
     - jump to date
   * - ``/g 2018-01-21 19:47``
     - jump to datetime
   * - ``/g 3172``
     - jump to message
   * - ``/g 34%``
     - jump to offset


admin commands
==============

**\ ``/auth``\ ** promotes you to administrator\ :raw-html-m2r:`<br>`
``/auth hunter2``

**\ ``/fill``\ ** floods the channel with messages\ :raw-html-m2r:`<br>`
``/fill 30 desu``

**\ ``/sd``\ ** shuts down the server

**\ ``/mem``\ ** dumps server memory to file

**\ ``/repl``\ ** drops server into a shell

**\ ``/gc``\ ** forces a garbage collection
