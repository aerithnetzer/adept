# Import libraries
import requests
import dgl
import torch as th
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go


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


def add_authorship_data(work_json):
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


def add_citation_data(work_json):
    """
    Adds citation data to a graph.

    Parameters:
    - work_json (dict): The data containing citation information.

    Returns:
    - dgl.DGLGraph: The created graph.
    """
    graph = dgl.DGLGraph()
    citations = work_json["referenced_works"]
    works = set()
    for citation in citations:
        work = citation
        works.add(work)
    work_to_id = {work: i for i, work in enumerate(works)}
    graph.add_nodes(len(works))
    for citation in citations:
        work = citation
        work_id = work_to_id[work]
        for other_citation in citations:
            other_work = other_citation
            other_work_id = work_to_id[other_work]
            if other_work != work:
                graph.add_edges(work_id, other_work_id)
    return graph


def plot_graph(g):
    """
    Plots the graph using plotly.

    Parameters:
    - g (dgl.DGLGraph): The graph to plot.

    Returns:
    - None
    """
    nx_g = g.to_networkx().to_undirected()
    pos = nx.spring_layout(nx_g)
    print(nx_g.edges())
    edge_x = []
    edge_y = []
    for edge in nx_g.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.5, color="#888"),
        hoverinfo="none",
        mode="lines",
    )

    node_x = [pos[node][0] for node in nx_g.nodes()]
    node_y = [pos[node][1] for node in nx_g.nodes()]

    # Add text to each node
    node_text = [f"Node {node}" for node in nx_g.nodes()]

    # Add node colors that scale to number of connections
    node_adjacencies = []
    node_color = []
    for node, adjacencies in enumerate(nx_g.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
    node_color = node_adjacencies

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale="YlGnBu",
            size=10,
            color=node_color,
            line=dict(width=2),
        ),
        text=node_text,
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    fig.show()


def main():
    workid = "W4318069697"
    work_json, workid = load_work_data(workid)
    graph = add_authorship_data(work_json)
    graph = add_citation_data(work_json)
    plot_graph(graph)


main()
