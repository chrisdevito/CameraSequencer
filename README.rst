================
CameraSequencer
================

A Maya Camera Sequencer

Documentation
--------------
You can find more documentation `here <./docs/build/index.html>`_


How to Install
---------------
- Download the package from the github repo http://github.com/chrisdevito/CameraSequencer.git and click Download Zip.
- After extraction, drag and drop the setup.mel (found in the CameraSequencer directory) into any open maya window.
- This will install it into your maya/scripts directory.


How to Run
------------
Drop this code as a button or run from the maya python script editor.

.. code-block:: python
    :name: CameraSequencerUI.py

    import CameraSequencer

    if __name__ == '__main__':

        CameraSequencer.show()
