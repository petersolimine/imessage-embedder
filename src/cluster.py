import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation as LDA
from chromadb.utils import embedding_functions
import umap
import hdbscan
from chromadb.config import Settings
import chromadb

'''
For more on UMAP, see here: https://umap-learn.readthedocs.io/en/latest/clustering.html
And HDBSCAN: https://hdbscan.readthedocs.io/en/latest/index.html
'''

client = chromadb.Client(Settings(chroma_db_impl='duckdb+parquet',persist_directory=".data"
))

def cluster_messages():
    # Load the messages
    collection = client.get_collection("messages")
    collection_dict = collection.get(include=['embeddings', 'documents'])
    embeddings = collection_dict['embeddings']
    messages = collection_dict['documents']

    # Perform dimensionality reduction using UMAP
    umap_embedding = umap.UMAP(
        n_neighbors=30,
        min_dist=0.0,
        n_components=2,
        random_state=42,
    ).fit_transform(embeddings)

    # Perform clustering using HDBSCAN
    labels = hdbscan.HDBSCAN(
        min_samples=10,
        min_cluster_size=200,
    ).fit_predict(umap_embedding)

    return labels, umap_embedding, messages

def analyze_clusters(labels, messages):
    unique_labels = np.unique(labels)
    for lbl in unique_labels:
        lbl_idx = np.where(labels == lbl)[0]
        lbl_messages = [messages[i] for i in lbl_idx]
        
        # Keyword extraction using tf-idf
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(lbl_messages)
        feature_array = np.array(vectorizer.get_feature_names_out())
        tfidf_sorting = np.argsort(tfidf_matrix.toarray()).flatten()[::-1]
        top_keywords = feature_array[tfidf_sorting][:10]
        print(f'Top keywords for cluster {lbl}: {top_keywords}')

        # Topic modeling using LDA
        lda = LDA(n_components=1, random_state=0)
        lda.fit(tfidf_matrix)
        topics = lda.components_
        top_topics = feature_array[np.argsort(topics)][:10]
        print(f'Top topics for cluster {lbl}: {top_topics}')

def cluster_representatives(labels, umap_embedding, messages):
    unique_labels = np.unique(labels)
    representatives = {}

    for label in unique_labels:
        if label != -1:  # -1 label is considered as noise by HDBSCAN
            cluster_points = umap_embedding[labels == label]
            centroid = np.mean(cluster_points, axis=0)

            distances = np.linalg.norm(cluster_points - centroid, axis=1)
            closest_point_index = np.argmin(distances)
            representatives[label] = messages[closest_point_index]

    return representatives

def visualize_clusters_option(labels, umap_embedding, representatives=None):
    clustered = (labels >= 0)
    plt.scatter(umap_embedding[~clustered, 0], umap_embedding[~clustered, 1], color=(0.5, 0.5, 0.5), s=0.1, alpha=0.5)
    plt.scatter(umap_embedding[clustered, 0], umap_embedding[clustered, 1], c=labels[clustered], s=0.1, cmap='Spectral')

    if representatives is not None:
        for label, message in representatives.items():
            cluster_points = umap_embedding[labels == label]
            centroid = np.mean(cluster_points, axis=0)
            plt.annotate(message, centroid)

    plt.show()

def visualize_all_data_points(labels, umap_embedding, messages):
    clustered = (labels >= 0)
    plt.scatter(umap_embedding[~clustered, 0], umap_embedding[~clustered, 1], color=(0.5, 0.5, 0.5), s=0.1, alpha=0.5)
    plt.scatter(umap_embedding[clustered, 0], umap_embedding[clustered, 1], c=labels[clustered], s=0.1, cmap='Spectral')

    for i, message in enumerate(messages):
        plt.annotate(message, umap_embedding[i])

    plt.show()

def cluster_top_representatives(labels, umap_embedding, messages, top_k=10):
    unique_labels = np.unique(labels)
    representatives = {}

    for label in unique_labels:
        if label != -1:  # -1 label is considered as noise by HDBSCAN
            cluster_points = umap_embedding[labels == label]
            centroid = np.mean(cluster_points, axis=0)

            distances = np.linalg.norm(cluster_points - centroid, axis=1)
            closest_point_indices = np.argsort(distances)[:top_k]

            representatives[label] = [messages[i] for i in closest_point_indices]

    return representatives

def visualize_top_representatives(labels, umap_embedding, representatives):
    clustered = (labels >= 0)
    plt.scatter(umap_embedding[~clustered, 0], umap_embedding[~clustered, 1], color=(0.5, 0.5, 0.5), s=0.1, alpha=0.5)
    plt.scatter(umap_embedding[clustered, 0], umap_embedding[clustered, 1], c=labels[clustered], s=0.1, cmap='Spectral')

    for label, messages in representatives.items():
        cluster_points = umap_embedding[labels == label]
        for message in messages:
            plt.annotate(message, cluster_points[np.random.choice(len(cluster_points))])
    
    plt.show()

def main():
    # Perform clustering on text messages
    labels, umap_embedding, messages = cluster_messages()

    # Analyze the clusters
    analyze_clusters(labels, messages)

    # Get user input for visualization
    option = input("Enter option for visualization (1: No Labels, 2: Representative Labels, 3: Label All Data Points, 4: Top 10 Representatives per Cluster): ")

    if option == "1":
        # Visualize the clusters with no labels
        visualize_clusters_option(labels, umap_embedding)

    elif option == "2":
        # Calculate cluster representatives
        representatives = cluster_representatives(labels, umap_embedding, messages)

        # Visualize the clusters with representative messages
        visualize_clusters_option(labels, umap_embedding, representatives)

    elif option == "3":
        # Visualize all data points with labels
        visualize_all_data_points(labels, umap_embedding, messages)

    elif option == "4":
        # Calculate top 10 representatives per cluster
        representatives = cluster_top_representatives(labels, umap_embedding, messages)

        # Visualize the clusters with top 10 representatives
        visualize_top_representatives(labels, umap_embedding, representatives)

    else:
        print("Invalid option. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
