# imessage-embedder

The goal of this project is to pull all your imessages from Mac automatically so that you can do fun stuff with them
as embeddings.

This only works on Mac.

For now, just run conversations.py

Check permissions: As of macOS Mojave, Apple introduced new privacy protections that can prevent applications from accessing certain files and directories. You may need to give your terminal "Full Disk Access" in order to allow Python to access the iMessage database. Here's how:

1. Open System Preferences.
2. Go to Security & Privacy.
3. Select the Privacy tab.
4. Scroll down in the list and click on Full Disk Access.
5. Click the lock in the bottom left to make changes. Enter your password when prompted.
6. Click the '+' button to add an application, then navigate to your terminal application (usually located in /Applications/Utilities/).
7. Close the System Preferences.
8. Run your script again: After granting Full Disk Access to your terminal, try running your Python script again.
