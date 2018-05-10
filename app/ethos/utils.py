import copy
import itertools
from io import BytesIO

from django.core.files.images import ImageFile

import matplotlib
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import requests

from .models import Hop, ShortCode


def save_graph(graph, format='png'):
    figure = BytesIO()
    plt.savefig(figure, format=format)
    return


def get_ebunchs():
    nodes = []
    edges = []

    # construct json for the graph viz
    hops = Hop.objects.select_related(
        'twitter_profile',
        'previous_hop',
        'previous_hop__twitter_profile',
    ).all()
    for hop in hops:
        node = {
            'label': hop.twitter_profile.username,
            'image': hop.twitter_profile.profile_picture.file,
            'color': 'green',
        }

        try:
            target = nodes.index(node)
        except ValueError:
            nodes.append(node)
            target = len(nodes) - 1

        # Add edge
        if hop.previous_hop:
            try:
                node_prev = nodes.index({
                    'label': hop.previous_hop.twitter_profile.username,
                    'image': hop.previous_hop.twitter_profile.profile_picture.url,
                    'color': 'green',
                })
                time_lapsed = round((hop.created_on - hop.previous_hop.created_on).total_seconds()/60)
                if 0 < time_lapsed < 30:
                    distance = time_lapsed * 10
                else:
                    distance = 300

                edges.append((node_prev, target, {'color': 'gray', 'length': distance}))
            except Exception:
                pass
                # edges.append({'source': node_prev, 'target': target, 'distance': distance})

    G = nx.DiGraph()
    G.add_edges_from(edges)
    G.add_nodes_from(nodes)
    plt.savefig('TESTING.png', format='png')


def get_hop_graph(hops_edges, hops_nodes):
    g = nx.Graph()
    g.add_edges_from(hops_nodes)
    g.add_nodes_from(hops_nodes)
    plt.figure(figsize=(8, 6))
    nx.draw(g, edge_color='gray', node_size=10, node_color='black')
    plt.title('EthOS Coin Hops', size=15)
    plt.savefig('derp.png')
