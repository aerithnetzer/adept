# %%
import requests
import json
import plotly.graph_objects as go
import networkx as nx
import nbformat

# %%
northwestern_data = requests.get("https://api.openalex.org/works?filter=institutions.id:I111979921")
northwestern_data = northwestern_data.json()

# %%
urls = []
for i in northwestern_data['results']:
    urls.append(i['id'])

urls = [url.replace("https://", "https://api.") for url in urls]
urls

# %%
graph = {}

# %%
def get_data(url):
    response = requests.get(url)
    data = response.json()
    return data

# %%
def add_data_to_graph(graph, data):
    for authorship in data['authorships']:
        author = authorship['author']['display_name']
        graph[author] = []
        for other_authorship in data['authorships']:
            other_author = other_authorship['author']['display_name']
            if other_author != author:
                graph[author].append(other_author)

# %%
for i in range(len(urls)):
    data = get_data(urls[i])
    add_data_to_graph(graph, data)

# %%
graph

# %%
add_data_to_graph()

# %%
kelsey = get_data('https://api.openalex.org/works/W2899966731')
kelsey_2= get_data('https://api.openalex.org/works/W3176337531')

# %%
graph = {}

for authorship in kelsey['authorships']:
    author = authorship['author']['display_name']
    graph[author] = []
    for other_authorship in kelsey['authorships']:
        other_author = other_authorship['author']['display_name']
        if other_author != author:
            graph[author].append(other_author)

graph

# %%
for authorship in kelsey_2['authorships']:
    author = authorship['author']['display_name']
    graph[author] = []
    for other_authorship in kelsey_2['authorships']:
        other_author = other_authorship['author']['display_name']
        if other_author != author:
            graph[author].append(other_author)

graph

# %%
# Visualize the graph
import networkx as nx
import matplotlib.pyplot as plt
import nbformat

G = nx.Graph(graph)
pos = nx.spring_layout(G)

edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])

edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')

node_x = [pos[node][0] for node in G.nodes()]
node_y = [pos[node][1] for node in G.nodes()]

# Add text to each node
node_text = [f'Node {node}' for node in G.nodes()]

# Add node colors that scale to number of connections
node_adjacencies = []
node_color = []
for node, adjacencies in enumerate(G.adjacency()):
    node_adjacencies.append(len(adjacencies[1]))
node_color = node_adjacencies

node_trace = go.Scatter(x=node_x, y=node_y, mode='markers', hoverinfo='text', marker=dict(showscale=True, colorscale='YlGnBu', size=10, color=node_color, line=dict(width=2)), text=node_text)

fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(showlegend=False, hovermode='closest', margin=dict(b=20,l=5,r=5,t=40), xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

fig.show()

# %%
# Find outliers in the graph
degree = dict(G.degree())
sorted_degree = sorted(degree.items(), key=lambda x: x[1], reverse=True)
print(sorted_degree)

# Find the most connected node
max_degree = max(degree, key=degree.get)
print(max_degree)

# %%
import torch
from torch_geometric.nn import GCNConv

# %%
class GCN(torch.nn.Module):
    def __init__(self, num_features, num_classes):
        super(GCN, self).__init__()
        self.conv1 = GCNConv(num_features, 16)
        self.conv2 = GCNConv(16, num_classes)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index

        x = self.conv1(x, edge_index)
        x = torch.relu(x)
        x = torch.dropout(x, training=self.training)
        x = self.conv2(x, edge_index)

        return torch.log_softmax(x, dim=1)

# Instantiate the model
model = GCN(num_features, num_classes)

# Define a loss function
criterion = torch.nn.CrossEntropyLoss()

# Define an optimizer
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

# Training loop
for epoch in range(200):
    model.train()
    optimizer.zero_grad()
    out = model(data)
    loss = criterion(out[data.train_mask], data.y[data.train_mask])
    loss.backward()
    optimizer.step()


