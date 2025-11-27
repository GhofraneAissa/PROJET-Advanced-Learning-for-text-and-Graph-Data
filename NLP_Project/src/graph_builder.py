import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import numpy as np


class GraphBuilder:
    def __init__(self):
        self.graph = None

    def build_graph(self, df, max_companies=20, max_skills_per_job=5):
        """Construit le graphe intelligent compétences-postes-entreprises"""
        G = nx.Graph()

        # Échantillonnage intelligent des entreprises les plus actives
        top_companies = df['company_name'].value_counts().head(max_companies).index
        df_filtered = df[df['company_name'].isin(top_companies)].copy()

        node_count = 0

        for idx, row in df_filtered.iterrows():
            if (pd.notna(row['company_name']) and
                    pd.notna(row['job_title_short']) and
                    node_count < 100):  # Limite de sécurité

                # Nœud entreprise
                company_node = f"company_{row['company_name']}"
                G.add_node(company_node, type='company', label=row['company_name'], size=15)

                # Nœud poste
                job_node = f"job_{row['job_title_short']}_{idx}"
                G.add_node(job_node, type='job', label=row['job_title_short'], size=12)

                # Lien entreprise-poste
                G.add_edge(company_node, job_node, relationship='offers', weight=2)

                # Nœuds compétences (limitées)
                if 'skills_list' in row and isinstance(row['skills_list'], list):
                    skills_added = 0
                    for skill in row['skills_list']:
                        if (skill and str(skill).strip() and
                                skills_added < max_skills_per_job):
                            skill_node = f"skill_{skill.strip()}"
                            G.add_node(skill_node, type='skill', label=skill.strip(), size=10)

                            # Lien poste-compétence
                            G.add_edge(job_node, skill_node, relationship='requires', weight=1)
                            skills_added += 1

                node_count += 1

        print(f"✅ Graphe construit: {G.number_of_nodes()} nœuds, {G.number_of_edges()} liens")
        self.graph = G
        return G

    def visualize_graph(self, G):
        """Visualisation interactive du graphe"""
        if G.number_of_nodes() == 0:
            return None

        try:
            # Layout avec contraintes pour meilleure visualisation
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

            # Préparation des arêtes
            edge_x = []
            edge_y = []

            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            # Trace des arêtes
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=1, color='#888'),
                hoverinfo='none',
                mode='lines'
            )

            # Préparation des nœuds
            node_x = []
            node_y = []
            node_text = []
            node_color = []
            node_size = []

            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)

                node_label = G.nodes[node].get('label', node)
                node_text.append(node_label)

                # Couleur et taille par type
                node_type = G.nodes[node].get('type', 'other')
                if node_type == 'company':
                    node_color.append('#FF6B6B')  # Rouge
                    node_size.append(20)
                elif node_type == 'job':
                    node_color.append('#4ECDC4')  # Bleu
                    node_size.append(15)
                else:  # skill
                    node_color.append('#45B7D1')  # Vert
                    node_size.append(12)

            # Trace des nœuds
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                textposition="middle center",
                marker=dict(
                    color=node_color,
                    size=node_size,
                    line=dict(width=2, color='white')
                )
            )

            # Création de la figure
            fig = go.Figure(data=[edge_trace, node_trace],
                            layout=go.Layout(
                                title='🕸️ Réseau Intelligence du Marché',
                                showlegend=False,
                                hovermode='closest',
                                margin=dict(b=20, l=20, r=20, t=40),
                                annotations=[dict(
                                    text="🔴 Entreprises | 🔵 Postes | 🟢 Compétences",
                                    showarrow=False,
                                    xref="paper", yref="paper",
                                    x=0.02, y=-0.05)],
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                            )

            return fig

        except Exception as e:
            print(f"❌ Erreur visualisation: {e}")
            return None

    def detect_communities(self, G):
        """Détecte les communautés dans le graphe"""
        try:
            from community import community_louvain
            partition = community_louvain.best_partition(G)

            communities = {}
            for node, community_id in partition.items():
                if community_id not in communities:
                    communities[community_id] = []
                communities[community_id].append(node)

            return communities
        except ImportError:
            return {}
        except Exception as e:
            print(f"Erreur détection communautés: {e}")
            return {}

    def get_skill_recommendations(self, target_skills, top_n=5):
        """Recommande des compétences associées"""
        if self.graph is None:
            return []

        recommendations = []
        for skill in target_skills:
            skill_node = f"skill_{skill}"
            if skill_node in self.graph:
                # Trouver les postes liés à cette compétence
                neighbors = list(self.graph.neighbors(skill_node))

                for job in neighbors:
                    if self.graph.nodes[job].get('type') == 'job':
                        # Trouver les autres compétences de ce poste
                        job_skills = [
                            n for n in self.graph.neighbors(job)
                            if self.graph.nodes[n].get('type') == 'skill'
                        ]

                        for related_skill in job_skills:
                            if related_skill != skill_node:
                                skill_name = self.graph.nodes[related_skill].get('label', related_skill)
                                recommendations.append(skill_name)

        # Retourner les plus fréquentes
        from collections import Counter
        return [skill for skill, count in Counter(recommendations).most_common(top_n)]