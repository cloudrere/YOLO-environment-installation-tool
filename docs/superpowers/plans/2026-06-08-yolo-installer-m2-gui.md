# YOLO Installer M2 GUI Plan

M2 adds the PyQt desktop shell around the core installer.

Tasks:

- implement environment detection page
- implement installation configuration page
- implement install progress page
- run the install pipeline in a worker thread
- stream logs into a bounded log view
- expose cancellation and environment removal actions
- package styling in the release build

The GUI keeps the first screen operational and avoids unrelated asset management.
