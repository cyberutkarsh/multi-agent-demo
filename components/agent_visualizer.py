import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Any
import matplotlib as mpl

def visualize_agent_workflow(current_agent: str = None):
    """Create and display a visualization of the agent workflow."""
    # Set up figure with a larger size and higher DPI
    plt.figure(figsize=(10, 7), dpi=100)
    
    # Use a white background with good contrast
    plt.style.use('default')
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes with full readable names
    agents = {
        "coordinator": "Coordinator",
        "route_optimizer": "Route Optimizer",
        "fleet_monitor": "Fleet Monitor",
        "data_retriever": "Data Retriever",
        "notification": "Notification"
    }
    
    # Add all nodes
    for agent_id, agent_name in agents.items():
        G.add_node(agent_id, label=agent_name)
    
    # Add edges
    G.add_edge("coordinator", "route_optimizer")
    G.add_edge("coordinator", "fleet_monitor")
    G.add_edge("coordinator", "data_retriever")
    G.add_edge("coordinator", "notification")
    G.add_edge("route_optimizer", "data_retriever")
    G.add_edge("route_optimizer", "notification")
    G.add_edge("fleet_monitor", "data_retriever")
    G.add_edge("fleet_monitor", "notification")
    
    # Create a more structured layout
    # Using a hierarchical layout for better visual flow
    pos = {
        "coordinator": (0.5, 0.9),
        "route_optimizer": (0.25, 0.6),
        "fleet_monitor": (0.75, 0.6),
        "data_retriever": (0.25, 0.3),
        "notification": (0.75, 0.3)
    }
    
    # Node colors with better contrast on white background
    node_colors = []
    for node in G.nodes():
        if node == current_agent:
            node_colors.append("#FF8000")  # Bright orange for current agent
        elif node == "coordinator":
            node_colors.append("#0066CC")  # Blue for coordinator
        else:
            node_colors.append("#00AA66")  # Green for other agents
    
    # Draw edges with increased visibility
    nx.draw_networkx_edges(
        G, 
        pos, 
        width=2, 
        edge_color='#666666',
        connectionstyle='arc3,rad=0.1',
        arrowsize=20,
        alpha=0.8
    )
    
    # Draw nodes with custom sizes based on importance
    node_sizes = [
        3200 if node == current_agent else
        2800 if node == "coordinator" else
        2400 for node in G.nodes()
    ]
    
    # Draw nodes with better visibility
    nx.draw_networkx_nodes(
        G, 
        pos, 
        node_color=node_colors,
        node_size=node_sizes,
        edgecolors='#333333',
        linewidths=1.5,
        alpha=0.9
    )
    
    # Draw labels with high contrast and good font size
    labels = {node: agents[node] for node in G.nodes()}
    nx.draw_networkx_labels(
        G, 
        pos, 
        labels=labels,
        font_size=12,
        font_weight='bold',
        font_color='white'  # White text on colored nodes for better contrast
    )
    
    # Add a legend for the node types
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor="#FF8000", markersize=15, label='Current Agent'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor="#0066CC", markersize=15, label='Coordinator'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor="#00AA66", markersize=15, label='Specialized Agent')
    ]
    plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 0.05))
    
    # Add title with current agent information
    if current_agent:
        current_agent_name = agents.get(current_agent, current_agent)
        plt.title(f"Current Agent: {current_agent_name}", fontsize=14, color='black', pad=20)
    else:
        plt.title("Supply Chain Agent Network", fontsize=14, color='black', pad=20)
    
    # Remove axis
    plt.axis("off")
    
    # Add a light border
    plt.gca().spines['top'].set_visible(True)
    plt.gca().spines['right'].set_visible(True)
    plt.gca().spines['bottom'].set_visible(True)
    plt.gca().spines['left'].set_visible(True)
    plt.gca().spines['top'].set_color('#bbbbbb')
    plt.gca().spines['right'].set_color('#bbbbbb')
    plt.gca().spines['bottom'].set_color('#bbbbbb')
    plt.gca().spines['left'].set_color('#bbbbbb')
    
    # Add some padding and a white background
    plt.tight_layout(pad=2.0)
    
    # Set the figure background to white
    fig = plt.gcf()
    fig.patch.set_facecolor('white')
    
    # Return the figure
    return plt 