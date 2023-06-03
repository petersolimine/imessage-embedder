# imessage-embedder

The goal of this project is to pull all your imessages from Mac automatically so that you can do fun stuff with them
as embeddings.

This only works on Mac.

## Usage

1. First and foremost, you need to give Terminal access to your imessages. Follow the steps below:

As of macOS Mojave, you may need to give your terminal "Full Disk Access" in order to allow Python (terminal, jupyter) to access the iMessage database.

    1. Open System Preferences.
    2. Go to Security & Privacy.
    3. Select the Privacy tab.
    4. Scroll down in the list and click on Full Disk Access.
    5. Click the lock in the bottom left to make changes. Enter your password when prompted.
    6. Click the '+' button to add an application, then navigate to your terminal application (usually located in /Applications/Utilities/).
    7. Close the System Preferences.
    8. Quit and reopen
    9. After granting Full Disk Access to your terminal, rerun script.
    * if you are using the VSCode embedded terminal, you will need to grant access to the VSCode app, not the terminal.

2. Install packages
   `pip install -r requirements.txt`

3. Now we pull our text messages and use Chroma to create and store embeddings

   `python src/embed_messages.py`

This might take a few minutes, just let it cook.

\*optional: you can also stitch together and embed full conversation threads, like so:

`python src/embed_conversations.py`

Nice! Now, here are a few fun things you can do with your imessage embeddings:

### 1. Semantic search queries against your message or conversation history

try it out: `python src/query.py`

### 2. Cluster your imessage history

try it out: `python src/cluster.py`

<details>
<summary>
A note on clustering:
</summary>
The aim of this clustering is to discover patterns and structure within imessage history, for instance grouping similar messages together and identifying key themes within groups. Here's the process:

Clustering: Messages & embeddngs are loaded from chroma, and the embeddings are used to perform dimensionality reduction and clustering.

Cluster Analysis: Each unique cluster is analyzed individually. This involves keyword extraction (using TF-IDF vectorization) to find the most important words for each cluster, and topic modeling (using LDA) to identify the key themes within the cluster.

Cluster Representatives: For each cluster, a representative message (or set of messages) is identified. This is typically the message(s) that is/are closest to the geometric center of the cluster. This representative can provide a snapshot of what the messages in the cluster are like.

Visualization: I made an effort to visualize this data so that the structure can be understand at a glance. Different visualizations are offered depending how much data has been embedded. 4 options are available for labeling:

Viewing clusters without labels,
With representative labels,
With top 10 representatives per cluster (recommended), or
with all data points labeled, (NOT recommended but kinda fun)

</details>

Powered by [Chroma](https://trychroma.com) 🚀
