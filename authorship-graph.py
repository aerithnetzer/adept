import requests
import networkx as nx
import plotly.graph_objects as go


def get_data(url):
    """
    Retrieves data from the specified URL.

    Parameters:
    - url (str): The URL to retrieve data from.

    Returns:
    - dict: The retrieved data in JSON format.
    """
    response = requests.get(url, timeout=5)
    response_data = response.json()
    return response_data


def add_authorship_data(graph, data):
    """
    Adds authorship data to a graph.

    Parameters:
    - graph (dict): The graph to add the data to.
    - data (dict): The data containing authorship information.

    Returns:
    - None
    """
    for authorship in data["authorships"]:
        author = authorship["author"]["display_name"]
        graph[author] = []
        for other_authorship in data["authorships"]:
            other_author = other_authorship["author"]["display_name"]
            if other_author != author:
                graph[author].append(other_author)


def create_graph(urls):
    """
    Creates a graph from a list of URLs.

    Parameters:
    - urls (list): The list of URLs to retrieve data from.

    Returns:
    - nx.Graph: The created graph.
    """
    graph = {}
    for url in urls:
        data = get_data(url)
        add_authorship_data(graph, data)
    return nx.Graph(graph)


def plot_graph(graph):
    """
    Plots the graph using Plotly.

    Parameters:
    - graph (nx.Graph): The graph to plot.

    Returns:
    - None
    """
    pos = nx.spring_layout(graph)

    edge_x = []
    edge_y = []
    for edge in graph.edges():
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

    node_x = [pos[node][0] for node in graph.nodes()]
    node_y = [pos[node][1] for node in graph.nodes()]

    # Add text to each node
    node_text = [f"Node {node}" for node in graph.nodes()]

    # Add node colors that scale to number of connections
    node_adjacencies = []
    node_color = []
    for node, adjacencies in enumerate(graph.adjacency()):
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


def test_workflow():
    """
    Implements a test workflow for the Northwestern example.

    Returns:
    - None
    """
    northwestern_data = get_data(
        "https://api.openalex.org/works?filter=institutions.id:I111979921"
    )
    urls = [
        url["id"].replace("https://", "https://api.")
        for url in northwestern_data["results"]
    ]
    graph = create_graph(urls)
    plot_graph(graph)

    # Find outliers in the graph
    degree = dict(graph.degree())
    sorted_degree = sorted(degree.items(), key=lambda x: x[1], reverse=True)
    print(sorted_degree)

    # Find the most connected node
    max_degree = max(degree, key=degree.get)
    print(max_degree)


test_workflow()
