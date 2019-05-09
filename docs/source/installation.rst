============
Installation
============

Get CameraSequencer for Maya
========================

Using the MEL setup script
---------------------------
- Download the package from the github repo http://github.com/chrisdevito/CameraSequencer.git and click Download Zip.
- After extraction, drag and drop the setup.mel (found in the CameraSequencer directory) into any open maya window.
- This will install it into your maya/scripts directory.

Using Pip
----------
::

    $ pip install CameraSequencer

Git
-----
::

    $ git clone https://github.com/chrisdevito/CameraSequencer
    $ cd CameraSequencer
    $ python setup.py install

Manual
-------
- Download the package from the github repo http://github.com/chrisdevito/CameraSequencer.git and click Download Zip.

- Copy the CameraSequencer folder into your maya/scripts path.

How to Run
===========
Drop this code as a button or run from the maya python script editor.

.. code-block:: python
    :name: CameraSequencerUI.py

    import CameraSequencer

    if __name__ == '__main__':

        CameraSequencer.show()
