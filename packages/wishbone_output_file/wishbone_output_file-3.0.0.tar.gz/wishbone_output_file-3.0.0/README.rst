::
            __       __    __
  .--.--.--|__.-----|  |--|  |--.-----.-----.-----.
  |  |  |  |  |__ --|     |  _  |  _  |     |  -__|
  |________|__|_____|__|__|_____|_____|__|__|_____|


  ===================================
  wishbone_contrib.module.output.file
  ===================================

  Version: 3.0.0

  Writes events to a file.
  ------------------------

      Writes events to a file.

      Parameters::

          - directory(str)("./")
             |  The directory to write the files to.

          - filename(str)("wishbone.out")*
             |  The filename to use.

          - native_events(bool)(False)
             |  Submit Wishbone native events.

          - overwrite(bool)(False)

             |  If `True` overwrites each time the content otherwise appends to
             |  the end of the file.

          - parallel_streams(int)(1)
             |  The number of outgoing parallel data streams.

          - payload(str)(None)
             |  The string to submit.
             |  If defined takes precedence over `selection`.

          - selection(str)("data")*
             |  The part of the event to submit externally.
             |  Use an empty string to refer to the complete event.


      Queues::

          - inbox
             |  Incoming messages


