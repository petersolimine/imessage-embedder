# iMessage Embedder :iphone::rocket:

Welcome to the iMessage Embedder project! We provide an intuitive way for you to extract your iMessages from a Mac and convert them into 'embeddings' - mathematical representations of data. Leveraging these embeddings, you can perform some fascinating operations on your message data and gain insights you never thought possible.

_**Note:** This only works on macOS._

---

## :wrench: Getting Started

Here are the steps you need to follow to get this tool up and running:

### Step 1: Give Terminal Access to Your iMessages

**Important:** As of macOS Mojave, you will need to grant your Terminal "Full Disk Access". This allows Python to interact with your iMessage database. Please follow the steps below to grant this access:

1. Open your **System Preferences**.
2. Navigate to **Security & Privacy**.
3. Select the **Privacy** tab.
4. Scroll down in the list and click on **Full Disk Access**.
5. Click the lock in the bottom left to allow changes. You'll be prompted to enter your password.
6. Click the '+' button to add an application. You should locate your Terminal application, usually found in `/Applications/Utilities/`.
7. Close the **System Preferences**.
8. Quit and reopen your Terminal.
9. After granting Full Disk Access to your Terminal, rerun the script.
   - _**Note:** If you're using the VSCode embedded terminal, you'll need to grant access to the VSCode app, not the Terminal._

### Step 2: Install Required Packages

Run the following command in your Terminal to install the required Python packages:

replaceme
pip install -r requirements.txt
replaceme

### Step 3: Pull Your iMessages and Create Embeddings

Execute the following command:

replaceme
python src/embed_messages.py
replaceme

This might take a few minutes, so hang tight and let the script do its work.

_**Optional:** If you'd like to stitch together and embed full conversation threads, use this command:_

replaceme
python src/embed_conversations.py
replaceme

---

## :tada: Let's Have Some Fun With Your iMessage Embeddings

Now that you have your iMessage embeddings, here are a few fun and interactive things you can do:

### 1. Semantic Search Queries Against Your Message or Conversation History

Try out this feature using the following command:

replaceme
python src/query.py
replaceme

### 2. Cluster Your iMessage History

Group your messages based on patterns and themes:

replaceme
python src/cluster.py
replaceme

<details>
<summary>
Click here for more details on clustering:
</summary>

This clustering process is designed to discover patterns and structure within your iMessage history. Here's a brief overview:

- **Clustering:** Messages and their embeddings are loaded from Chroma, which are then used for dimensionality reduction and clustering.

- **Cluster Analysis:** Each unique cluster is individually analyzed, involving keyword extraction (using TF-IDF vectorization) to pinpoint the most significant words for each cluster, and topic modeling (using LDA) to identify the key themes within the cluster.

- **Cluster Representatives:** A representative message or set of messages is identified for each cluster, typically the one(s) closest to the geometric center of the cluster. This representative provides an overview of what the messages in the cluster look like.

- **Visualization:** We've made an effort to visualize this data so you can grasp the structure at a glance. Different visualizations are offered depending on how much data has been embedded. Four
  options are available for labeling:

Viewing clusters without labels,
With representative labels,
With top 10 representatives per cluster (recommended), or
with all data points labeled, (NOT recommended but kinda fun)

</details>

Powered by [Chroma](https://trychroma.com) 🚀
