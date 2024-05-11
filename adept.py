# Import libraries
import requests
import dgl
import torch as th
import networkx as nx
import matplotlib.pyplot as plt


def load_work_data(workid):
    """
    Retrieves authorship data for a work from the OpenAlex API.

    Parameters:
    - workid (str): The ID of the work to retrieve data for.

    Returns:
    - dict: The retrieved data in JSON format.
    """
    response = requests.get(f"https://api.openalex.org/works/{workid}")
    response_data = response.json()
    return response_data, workid


def add_authorsip_data(work_json):
    """
    Adds authorship data to a graph.

    Parameters:
    - work_json (dict): The data containing authorship information.

    Returns:
    - dgl.DGLGraph: The created graph.
    """
    graph = dgl.DGLGraph()
    authorships = work_json["authorships"]
    authors = set()
    for authorship in authorships:
        author = authorship["author"]["display_name"]
        authors.add(author)
    author_to_id = {author: i for i, author in enumerate(authors)}
    graph.add_nodes(len(authors))
    for authorship in authorships:
        author = authorship["author"]["display_name"]
        author_id = author_to_id[author]
        for other_authorship in authorships:
            other_author = other_authorship["author"]["display_name"]
            other_author_id = author_to_id[other_author]
            if other_author != author:
                graph.add_edges(author_id, other_author_id)
    return graph


def plot_graph(g):
    """
    Plots the graph using NetworkX.

    Parameters:
    - g (dgl.DGLGraph): The graph to plot.

    Returns:
    - None
    """
    nx_g = g.to_networkx().to_undirected()
    pos = nx.spring_layout(nx_g)
    nx.draw(nx_g, pos, with_labels=True)
    plt.savefig("graph.png")


def main():
    workid = "W1009208869"
    work_json, workid = load_work_data(workid)
    graph = add_authorsip_data(work_json)
    plot_graph(graph)


main()
