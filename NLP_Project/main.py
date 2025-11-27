# import pandas as pd
# import streamlit as st
# import networkx as nx
# from src.data_processing import DataProcessor
# from src.nlp_analysis import NLPAnalyzer
# from src.graph_builder import GraphBuilder
# from src.qa_system import QASystem
#
# # Configuration de la page
# st.set_page_config(
#     page_title="Analyse des Offres d'Emploi Data",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )
#
#
# # Cache pour les données seulement
# @st.cache_data
# def load_data():
#     """Charge les données avec cache"""
#     try:
#         processor = DataProcessor("data/data_jobs_cleaned.xlsx")
#         df = processor.load_and_clean_data()
#
#         # Vérifier que le DataFrame a les colonnes minimales requises
#         if not df.empty:
#             required_columns = ['company_name', 'job_title_short', 'skills_list']
#             missing_columns = [col for col in required_columns if col not in df.columns]
#             if missing_columns:
#                 st.warning(f"⚠️ Colonnes manquantes: {missing_columns}")
#
#         return df
#     except Exception as e:
#         st.error(f"Erreur lors du chargement: {e}")
#         return pd.DataFrame()
#
#
# # Cache pour les analyseurs
# @st.cache_resource
# def load_nlp_analyzer():
#     return NLPAnalyzer()
#
#
# @st.cache_resource
# def load_graph_builder():
#     return GraphBuilder()
#
#
# @st.cache_resource
# def load_qa_system():
#     return QASystem()
#
#
# def main():
#     st.title("🔍 Système d'Analyse des Offres d'Emploi Data")
#
#     # Initialisation avec indicateurs de progression
#     with st.spinner("Initialisation du système..."):
#         df = load_data()
#         nlp_analyzer = load_nlp_analyzer()
#         graph_builder = load_graph_builder()
#         qa_system = load_qa_system()
#
#     if df.empty:
#         st.error("""
#         ❌ Impossible de charger les données.
#
#         Vérifiez que:
#         1. Le fichier `data_jobs_cleaned.xlsx` existe dans le dossier `data/`
#         2. Le fichier n'est pas corrompu
#         3. Vous avez les permissions de lecture
#         """)
#         return
#
#     # Afficher un message de succès avec informations sur les données
#     st.success(f"✅ Données chargées: {len(df):,} offres d'emploi")
#
#     # Afficher les colonnes disponibles pour debug
#     with st.expander("🔍 Informations techniques (debug)"):
#         st.write(f"**Colonnes disponibles:** {list(df.columns)}")
#         st.write(f"**Nombre d'entreprises:** {df['company_name'].nunique() if 'company_name' in df.columns else 'N/A'}")
#         st.write(
#             f"**Nombre de compétences uniques:** {df['skills_list'].explode().nunique() if 'skills_list' in df.columns else 'N/A'}")
#         st.write(f"**Taille du dataset:** {df.memory_usage(deep=True).sum() / 1024 ** 2:.2f} MB")
#
#     # Sidebar pour la navigation
#     st.sidebar.title("📋 Navigation")
#     page = st.sidebar.radio(
#         "Choisir une section",
#         ["🏠 Vue d'ensemble", "🧠 Analyse NLP", "🕸️ Graphe des Compétences", "❓ Système de Q&A"],
#         index=0
#     )
#
#     # Navigation
#     if "Vue d'ensemble" in page:
#         show_overview(df)
#     elif "Analyse NLP" in page:
#         show_nlp_analysis(df, nlp_analyzer)
#     elif "Graphe des Compétences" in page:
#         show_skill_graph(df, graph_builder)
#     elif "Système de Q&A" in page:
#         show_qa_system(df, qa_system)
#
#
# def show_overview(df):
#     st.header("📊 Vue d'ensemble du Marché de l'Emploi Data")
#
#     try:
#         # Métriques principales en temps réel avec vérifications
#         col1, col2, col3, col4 = st.columns(4)
#
#         total_jobs = len(df)
#
#         unique_companies = df['company_name'].nunique() if 'company_name' in df.columns else 0
#         unique_skills = df['skills_list'].explode().nunique() if 'skills_list' in df.columns else 0
#
#         # Gestion du salaire moyen
#         avg_salary = None
#         if 'salary_year_avg' in df.columns:
#             avg_salary = df['salary_year_avg'].mean()
#         salary_display = f"${avg_salary:,.0f}" if avg_salary and not pd.isna(avg_salary) else "N/A"
#
#         with col1:
#             st.metric("📋 Offres d'emploi", f"{total_jobs:,}")
#
#         with col2:
#             st.metric("🏢 Entreprises", f"{unique_companies:,}")
#
#         with col3:
#             st.metric("🛠️ Compétences", f"{unique_skills:,}")
#
#         with col4:
#             st.metric("💰 Salaire moyen", salary_display)
#
#         # Graphiques rapides avec vérifications
#         st.subheader("🎯 Tendances du Marché")
#
#         tab1, tab2, tab3 = st.tabs(["📊 Postes", "🛠️ Compétences", "🏢 Entreprises"])
#
#         with tab1:
#             if 'job_title_short' in df.columns:
#                 top_jobs = df['job_title_short'].value_counts().head(10)
#                 if not top_jobs.empty:
#                     st.bar_chart(top_jobs)
#                     st.write("**Postes les plus demandés:**")
#                     for job, count in top_jobs.head(5).items():
#                         st.write(f"- {job}: {count:,} offres")
#                 else:
#                     st.info("ℹ️ Aucune donnée de postes disponible")
#             else:
#                 st.warning("❌ Colonne 'job_title_short' manquante")
#
#         with tab2:
#             if 'skills_list' in df.columns:
#                 all_skills = df['skills_list'].explode()
#                 top_skills = all_skills.value_counts().head(10)
#                 if not top_skills.empty:
#                     st.bar_chart(top_skills)
#                     st.write("**Compétences les plus recherchées:**")
#                     for skill, count in top_skills.head(5).items():
#                         st.write(f"- {skill}: {count:,} offres")
#                 else:
#                     st.info("ℹ️ Aucune compétence trouvée")
#             else:
#                 st.warning("❌ Colonne 'skills_list' manquante")
#
#         with tab3:
#             if 'company_name' in df.columns:
#                 top_companies = df['company_name'].value_counts().head(10)
#                 if not top_companies.empty:
#                     st.bar_chart(top_companies)
#                     st.write("**Entreprises qui recrutent le plus:**")
#                     for company, count in top_companies.head(5).items():
#                         st.write(f"- {company}: {count:,} offres")
#                 else:
#                     st.info("ℹ️ Aucune donnée d'entreprises disponible")
#             else:
#                 st.warning("❌ Colonne 'company_name' manquante")
#
#     except Exception as e:
#         st.error(f"❌ Erreur dans l'affichage de la vue d'ensemble: {str(e)}")
#         st.info("💡 Vérifiez que votre fichier de données contient les colonnes nécessaires")
#
#
# def show_nlp_analysis(df, nlp_analyzer):
#     st.header("🧠 Analyse Intelligente des Offres")
#
#     tab1, tab2 = st.tabs(["🎪 Classification des Postes", "🔍 Extraction de Compétences"])
#
#     with tab1:
#         st.subheader("Classification Automatique des Postes")
#
#         if st.button("🎯 Classifier tous les postes", type="primary"):
#             with st.spinner("Analyse en cours... Cela peut prendre quelques secondes"):
#                 try:
#                     df_classified = nlp_analyzer.classify_jobs(df)
#
#                     # Afficher les résultats
#                     col1, col2 = st.columns([2, 1])
#
#                     with col1:
#                         st.success("✅ Classification terminée!")
#
#                         # Graphique des catégories
#                         if 'predicted_category' in df_classified.columns:
#                             category_counts = df_classified['predicted_category'].value_counts()
#                             if not category_counts.empty:
#                                 st.bar_chart(category_counts)
#                             else:
#                                 st.warning("❌ Aucune catégorie prédite")
#                         else:
#                             st.warning("❌ Colonne 'predicted_category' manquante")
#
#                     with col2:
#                         st.subheader("📈 Répartition")
#                         if 'predicted_category' in df_classified.columns:
#                             category_counts = df_classified['predicted_category'].value_counts()
#                             for category, count in category_counts.head(8).items():
#                                 st.write(f"**{category}**: {count:,}")
#                         else:
#                             st.write("Aucune donnée disponible")
#
#                     # Exemples
#                     st.subheader("🎓 Exemples de classification")
#                     if 'job_title' in df_classified.columns and 'predicted_category' in df_classified.columns:
#                         sample_data = df_classified[['job_title', 'predicted_category']].head(8)
#                         if not sample_data.empty:
#                             for _, row in sample_data.iterrows():
#                                 st.write(f"- **{row['job_title']}** → *{row['predicted_category']}*")
#                         else:
#                             st.write("Aucun exemple disponible")
#                     else:
#                         st.write("Données d'exemple non disponibles")
#
#                 except Exception as e:
#                     st.error(f"❌ Erreur lors de la classification: {str(e)}")
#
#     with tab2:
#         st.subheader("🔧 Extraction de Compétences")
#
#         # Exemples prédéfinis pour plus de rapidité
#         example_choice = st.selectbox(
#             "Choisir un exemple type:",
#             [
#                 "✍️ Saisir manuellement...",
#                 "👨‍💻 Data Scientist Python SQL ML",
#                 "👨‍🔧 Data Engineer Spark AWS ETL",
#                 "👨‍💼 Data Analyst Tableau SQL Excel",
#                 "🤖 ML Engineer TensorFlow Python",
#                 "📊 Data Engineer compétences techniques"
#             ]
#         )
#
#         # Text input adaptatif
#         default_text = ""
#         if "Data Scientist" in example_choice:
#             default_text = "Nous recherchons un Data Scientist expérimenté avec Python, SQL, Machine Learning, et compétences en analyse statistique."
#         elif "Data Engineer" in example_choice:
#             default_text = "Poste d'Ingénieur Data nécessitant Spark, Hadoop, AWS, ETL, et compétences en architecture données."
#         elif "Data Analyst" in example_choice:
#             default_text = "Analyste données maîtrisant Tableau, SQL, Excel, Power BI et ayant des compétences en visualisation."
#         elif "ML Engineer" in example_choice:
#             default_text = "Ingénieur Machine Learning expert en TensorFlow, PyTorch, Python, Deep Learning et ML ops."
#         elif "compétences techniques" in example_choice:
#             default_text = "Data Engineer avec expertise en Python, SQL, Spark, AWS, Docker, et Data Pipelines."
#
#         text_input = st.text_area(
#             "Description du poste à analyser:",
#             value=default_text if example_choice != "✍️ Saisir manuellement..." else "",
#             height=100,
#             placeholder="Entrez une description de poste pour extraire les compétences techniques..."
#         )
#
#         if st.button("🔎 Extraire les compétences", type="primary") and text_input:
#             with st.spinner("Analyse du texte en cours..."):
#                 try:
#                     skills = nlp_analyzer.extract_skills(text_input)
#
#                     if skills:
#                         st.success(f"🎉 {len(skills)} compétences identifiées:")
#
#                         # Afficher en colonnes
#                         cols = st.columns(3)
#                         for i, skill in enumerate(skills):
#                             with cols[i % 3]:
#                                 st.info(f"**{skill.capitalize()}**")
#                     else:
#                         st.warning("🤔 Aucune compétence technique identifiée dans le texte.")
#                 except Exception as e:
#                     st.error(f"❌ Erreur lors de l'extraction: {str(e)}")
#
#
# def show_skill_graph(df, graph_builder):
#     st.header("🕸️ Réseau des Compétences et Métiers")
#
#     st.info("""
#     **ℹ️ Cette visualisation montre les relations entre:**
#     - 🔴 **Entreprises** et les postes qu'elles proposent
#     - 🔵 **Postes** et les compétences requises
#     - 🟢 **Compétences** partagées entre différents postes
#
#     *Note: Pour les grands datasets, la génération peut prendre quelques instants*
#     """)
#
#     # Vérifier les colonnes nécessaires
#     required_columns = ['company_name', 'job_title_short', 'skills_list']
#     missing_columns = [col for col in required_columns if col not in df.columns]
#
#     if missing_columns:
#         st.error(f"❌ Colonnes manquantes pour construire le graphe: {missing_columns}")
#         st.info("💡 Le graphe nécessite les colonnes: company_name, job_title_short, skills_list")
#         return
#
#     # Contrôles
#     col1, col2, col3 = st.columns(3)
#
#     with col1:
#         graph_size_option = st.selectbox(
#             "Taille du graphe:",
#             ["🔍 Petit (rapide)", "📊 Moyen", "🌐 Grand (complet)"],
#             index=1
#         )
#
#     with col2:
#         sample_data = st.checkbox("Échantillonner les données", value=True,
#                                   help="Prend un échantillon pour accélérer la génération")
#
#     with col3:
#         if st.button("🔄 Générer le Réseau", type="primary", use_container_width=True):
#             st.session_state.generate_graph = True
#
#     # Génération conditionnelle
#     if st.session_state.get('generate_graph', False):
#         with st.spinner("🛠️ Construction du réseau en cours... (cela peut prendre quelques secondes)"):
#             try:
#                 # Paramètres selon la taille
#                 size_params = {
#                     "🔍 Petit (rapide)": (10, 3),
#                     "📊 Moyen": (20, 5),
#                     "🌐 Grand (complet)": (30, 8)
#                 }
#                 max_companies, max_skills = size_params[graph_size_option]
#
#                 # Échantillonner les données si demandé
#                 df_for_graph = df
#                 if sample_data and len(df) > 1000:
#                     df_for_graph = df.sample(min(1000, len(df)), random_state=42)
#                     st.info(f"📊 Utilisation d'un échantillon de {len(df_for_graph):,} offres pour la génération")
#
#                 G = graph_builder.build_graph(df_for_graph, max_companies, max_skills)
#
#                 # Vérifier que le graphe a été construit
#                 if G is None or G.number_of_nodes() == 0:
#                     st.error("❌ Le graphe n'a pas pu être construit (aucun nœud)")
#                     return
#
#                 # Métriques du réseau
#                 st.subheader("📊 Statistiques du Réseau")
#
#                 metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
#
#                 with metrics_col1:
#                     st.metric("🏷️ Nœuds", f"{G.number_of_nodes():,}")
#                     st.metric("🔗 Liens", f"{G.number_of_edges():,}")
#
#                 with metrics_col2:
#                     try:
#                         density = nx.density(G)
#                         st.metric("📈 Densité", f"{density:.4f}")
#                     except:
#                         st.metric("📈 Densité", "N/A")
#
#                     # Vérifier si le graphe est connecté avant de calculer le diamètre
#                     diameter = "N/A"
#                     try:
#                         if nx.is_connected(G):
#                             diameter = nx.diameter(G)
#                         else:
#                             diameter = "Non connecté"
#                     except:
#                         diameter = "N/A"
#                     st.metric("🔄 Diamètre", diameter)
#
#                 with metrics_col3:
#                     if G.number_of_nodes() > 0:
#                         try:
#                             degree_centrality = nx.degree_centrality(G)
#                             if degree_centrality:
#                                 max_node = max(degree_centrality, key=degree_centrality.get)
#                                 node_label = G.nodes[max_node].get('label', str(max_node))
#                                 st.metric("⭐ Nœud central",
#                                           node_label[:25] + "..." if len(node_label) > 25 else node_label)
#                             else:
#                                 st.metric("⭐ Nœud central", "N/A")
#                         except:
#                             st.metric("⭐ Nœud central", "N/A")
#                     else:
#                         st.metric("⭐ Nœud central", "N/A")
#
#                 # Visualisation
#                 st.subheader("🎨 Visualisation Interactive")
#                 fig = graph_builder.visualize_graph(G)
#                 if fig:
#                     st.plotly_chart(fig, use_container_width=True)
#                 else:
#                     st.error("❌ Erreur lors de la génération de la visualisation")
#
#                 # Analyses avancées (optionnelles)
#                 with st.expander("🔍 Analyses Avancées"):
#                     st.write("**Communautés détectées:**")
#                     try:
#                         import community as community_louvain
#                         partition = community_louvain.best_partition(G)
#                         community_count = len(set(partition.values()))
#                         st.write(f"Nombre de communautés: {community_count}")
#
#                         # Afficher les 3 plus grandes communautés
#                         community_sizes = {}
#                         for node, comm_id in partition.items():
#                             community_sizes[comm_id] = community_sizes.get(comm_id, 0) + 1
#
#                         top_communities = sorted(community_sizes.items(), key=lambda x: x[1], reverse=True)[:3]
#                         for comm_id, size in top_communities:
#                             st.write(f"- Communauté {comm_id}: {size} nœuds")
#
#                     except ImportError as e:
#                         st.write("ℹ️ Package 'python-louvain' requis pour cette analyse")
#                     except Exception as e:
#                         st.write(f"❌ Erreur lors de l'analyse des communautés: {e}")
#
#             except Exception as e:
#                 st.error(f"❌ Erreur lors de la construction du graphe: {str(e)}")
#                 st.info("💡 Essayez une taille de graphe plus petite ou activez l'échantillonnage")
#
#
# def show_qa_system(df, qa_system):
#     st.header("❓ Assistant Intelligent - Questions/Réponses")
#
#     # Vérifier que le système Q&A peut fonctionner
#     required_columns = ['company_name', 'job_title_short', 'skills_list']
#     missing_columns = [col for col in required_columns if col not in df.columns]
#
#     if missing_columns:
#         st.error(f"❌ Colonnes manquantes pour le système Q&A: {missing_columns}")
#         st.info("💡 Le système Q&A nécessite les colonnes: company_name, job_title_short, skills_list")
#         return
#
#     # Initialisation du QASystem
#     if not hasattr(st.session_state, 'qa_initialized') or not st.session_state.qa_initialized:
#         with st.spinner("🔄 Initialisation de l'assistant intelligent... (cela peut prendre quelques secondes)"):
#             try:
#                 qa_system.build_knowledge_base(df)
#                 st.session_state.qa_initialized = True
#                 st.success("✅ Assistant initialisé avec succès!")
#
#                 # Afficher les statistiques de l'initialisation
#                 with st.expander("📊 Statistiques de l'assistant"):
#                     if hasattr(qa_system, '_precomputed_answers'):
#                         answers = qa_system._precomputed_answers
#                         st.write(f"• Compétences analysées: {len(answers.get('top_skills', [])):,}")
#                         st.write(f"• Entreprises recensées: {len(answers.get('top_companies', [])):,}")
#                         st.write(f"• Postes suivis: {len(answers.get('top_jobs', [])):,}")
#             except Exception as e:
#                 st.error(f"❌ Erreur lors de l'initialisation de l'assistant: {str(e)}")
#                 st.session_state.qa_initialized = False
#                 return
#
#     st.info("""
#     **💡 Exemples de questions:**
#     - "Quelles sont les compétences les plus demandées ?"
#     - "Quelles entreprises recherchent Python et Machine Learning ?"
#     - "Quels sont les salaires pour les Data Scientists ?"
#     - "Quels postes nécessitent TensorFlow ?"
#     - "Compétences des Data Engineers ?"
#     - "Statistiques du marché data"
#     - "Quelles entreprises recrutent le plus ?"
#     """)
#
#     # Questions rapides
#     st.subheader("🚀 Questions Rapides")
#
#     quick_questions = [
#         "Quelles sont les compétences les plus demandées?",
#         "Quelles entreprises recherchent Python?",
#         "Quels sont les salaires moyens?",
#         "Quels sont les postes les plus courants?",
#         "Compétences des Data Engineers?",
#         "Statistiques du marché data?",
#         "Quelles entreprises recrutent le plus?"
#     ]
#
#     # Afficher les questions rapides en grille
#     cols = st.columns(2)
#     for i, question in enumerate(quick_questions):
#         with cols[i % 2]:
#             if st.button(f"📌 {question}", key=f"quick_{i}", use_container_width=True):
#                 with st.spinner("🔍 Recherche en cours..."):
#                     try:
#                         answer = qa_system.answer_question(question)
#                         st.session_state.last_question = question
#                         st.session_state.last_answer = answer
#                     except Exception as e:
#                         st.error(f"❌ Erreur lors du traitement de la question: {str(e)}")
#                         st.session_state.last_answer = "❌ Une erreur s'est produite lors du traitement de votre question."
#
#     # Question personnalisée
#     st.subheader("🔍 Question Personnalisée")
#
#     question_input = st.text_input(
#         "Votre question:",
#         placeholder="Ex: Quelles entreprises recherchent des compétences en Python et AWS ?",
#         key="custom_question"
#     )
#
#     col1, col2 = st.columns([3, 1])
#
#     with col2:
#         ask_button = st.button("🎯 Poser la question", type="primary", use_container_width=True)
#
#     # Gestion des réponses
#     if ask_button and question_input:
#         with st.spinner("🔍 Analyse en cours..."):
#             try:
#                 answer = qa_system.answer_question(question_input)
#                 st.session_state.last_question = question_input
#                 st.session_state.last_answer = answer
#             except Exception as e:
#                 st.error(f"❌ Erreur lors du traitement de la question: {str(e)}")
#                 st.session_state.last_answer = "❌ Une erreur s'est produite lors du traitement de votre question."
#
#     # Affichage de la réponse
#     if hasattr(st.session_state, 'last_answer') and st.session_state.last_answer:
#         st.markdown("---")
#         st.subheader("💬 Réponse:")
#
#         # Afficher la question
#         if hasattr(st.session_state, 'last_question'):
#             st.write(f"**Question:** {st.session_state.last_question}")
#
#         # Afficher la réponse formatée
#         st.success(st.session_state.last_answer)
#
#         # Bouton pour poser une nouvelle question
#         if st.button("🔄 Poser une nouvelle question"):
#             st.session_state.last_question = ""
#             st.session_state.last_answer = ""
#             st.rerun()
#
#
# # Initialisation des variables de session
# if 'generate_graph' not in st.session_state:
#     st.session_state.generate_graph = False
# if 'last_question' not in st.session_state:
#     st.session_state.last_question = ""
# if 'last_answer' not in st.session_state:
#     st.session_state.last_answer = ""
# if 'qa_initialized' not in st.session_state:
#     st.session_state.qa_initialized = False
#
# if __name__ == "__main__":
#     main()

# import pandas as pd
# import streamlit as st
# import networkx as nx
# from src.data_processing import DataProcessor
# from src.nlp_analysis import NLPAnalyzer, AdvancedNLPAnalyzer
# from src.graph_builder import GraphBuilder
# from src.qa_system import QASystem
# from src.advanced_analysis import AdvancedAnalysis
#
# # Configuration de la page
# st.set_page_config(
#     page_title="Analyse des Offres d'Emploi Data",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )
#
#
# # Cache pour les données seulement
# @st.cache_data
# def load_data():
#     """Charge les données avec cache"""
#     try:
#         processor = DataProcessor("data/data_jobs_cleaned.xlsx")
#         df = processor.load_and_clean_data()
#
#         # Vérifier que le DataFrame a les colonnes minimales requises
#         if not df.empty:
#             required_columns = ['company_name', 'job_title_short', 'skills_list']
#             missing_columns = [col for col in required_columns if col not in df.columns]
#             if missing_columns:
#                 st.warning(f"⚠️ Colonnes manquantes: {missing_columns}")
#
#         return df
#     except Exception as e:
#         st.error(f"Erreur lors du chargement: {e}")
#         return pd.DataFrame()
#
#
# # Cache pour les analyseurs
# @st.cache_resource
# def load_nlp_analyzer():
#     return NLPAnalyzer()
#
#
# @st.cache_resource
# def load_advanced_nlp_analyzer():
#     return AdvancedNLPAnalyzer()
#
#
# @st.cache_resource
# def load_graph_builder():
#     return GraphBuilder()
#
#
# @st.cache_resource
# def load_qa_system():
#     return QASystem()
#
#
# def main():
#     st.title("🔍 Système d'Analyse des Offres d'Emploi Data")
#
#     # Initialisation avec indicateurs de progression
#     with st.spinner("Initialisation du système..."):
#         df = load_data()
#         nlp_analyzer = load_nlp_analyzer()
#         advanced_analyzer = load_advanced_nlp_analyzer()
#         graph_builder = load_graph_builder()
#         qa_system = load_qa_system()
#
#     if df.empty:
#         st.error("""
#         ❌ Impossible de charger les données.
#
#         Vérifiez que:
#         1. Le fichier `data_jobs_cleaned.xlsx` existe dans le dossier `data/`
#         2. Le fichier n'est pas corrompu
#         3. Vous avez les permissions de lecture
#         """)
#         return
#
#     # Afficher un message de succès avec informations sur les données
#     st.success(f"✅ Données chargées: {len(df):,} offres d'emploi")
#
#     # Afficher les colonnes disponibles pour debug
#     with st.expander("🔍 Informations techniques (debug)"):
#         st.write(f"**Colonnes disponibles:** {list(df.columns)}")
#         st.write(f"**Nombre d'entreprises:** {df['company_name'].nunique() if 'company_name' in df.columns else 'N/A'}")
#         st.write(
#             f"**Nombre de compétences uniques:** {df['skills_list'].explode().nunique() if 'skills_list' in df.columns else 'N/A'}")
#         st.write(f"**Taille du dataset:** {df.memory_usage(deep=True).sum() / 1024 ** 2:.2f} MB")
#
#     # Sidebar pour la navigation
#     st.sidebar.title("📋 Navigation")
#     page = st.sidebar.radio(
#         "Choisir une section",
#         [
#             "🏠 Vue d'ensemble",
#             "🧠 Analyse NLP",
#             "🤖 Analyse Avancée BERT",
#             "🕸️ Graphe des Compétences",
#             "❓ Système de Q&A"
#         ],
#         index=0
#     )
#
#     # Navigation
#     if "Vue d'ensemble" in page:
#         show_overview(df)
#     elif "Analyse NLP" in page:
#         show_nlp_analysis(df, nlp_analyzer)
#     elif "Analyse Avancée BERT" in page:
#         show_advanced_analysis(df, advanced_analyzer)
#     elif "Graphe des Compétences" in page:
#         show_skill_graph(df, graph_builder)
#     elif "Système de Q&A" in page:
#         show_qa_system(df, qa_system)
#
#
# def show_overview(df):
#     st.header("📊 Vue d'ensemble du Marché de l'Emploi Data")
#
#     try:
#         # Métriques principales en temps réel avec vérifications
#         col1, col2, col3, col4 = st.columns(4)
#
#         total_jobs = len(df)
#
#         unique_companies = df['company_name'].nunique() if 'company_name' in df.columns else 0
#         unique_skills = df['skills_list'].explode().nunique() if 'skills_list' in df.columns else 0
#
#         # Gestion du salaire moyen
#         avg_salary = None
#         if 'salary_year_avg' in df.columns:
#             avg_salary = df['salary_year_avg'].mean()
#         salary_display = f"${avg_salary:,.0f}" if avg_salary and not pd.isna(avg_salary) else "N/A"
#
#         with col1:
#             st.metric("📋 Offres d'emploi", f"{total_jobs:,}")
#
#         with col2:
#             st.metric("🏢 Entreprises", f"{unique_companies:,}")
#
#         with col3:
#             st.metric("🛠️ Compétences", f"{unique_skills:,}")
#
#         with col4:
#             st.metric("💰 Salaire moyen", salary_display)
#
#         # Graphiques rapides avec vérifications
#         st.subheader("🎯 Tendances du Marché")
#
#         tab1, tab2, tab3 = st.tabs(["📊 Postes", "🛠️ Compétences", "🏢 Entreprises"])
#
#         with tab1:
#             if 'job_title_short' in df.columns:
#                 top_jobs = df['job_title_short'].value_counts().head(10)
#                 if not top_jobs.empty:
#                     st.bar_chart(top_jobs)
#                     st.write("**Postes les plus demandés:**")
#                     for job, count in top_jobs.head(5).items():
#                         st.write(f"- {job}: {count:,} offres")
#                 else:
#                     st.info("ℹ️ Aucune donnée de postes disponible")
#             else:
#                 st.warning("❌ Colonne 'job_title_short' manquante")
#
#         with tab2:
#             if 'skills_list' in df.columns:
#                 all_skills = df['skills_list'].explode()
#                 top_skills = all_skills.value_counts().head(10)
#                 if not top_skills.empty:
#                     st.bar_chart(top_skills)
#                     st.write("**Compétences les plus recherchées:**")
#                     for skill, count in top_skills.head(5).items():
#                         st.write(f"- {skill}: {count:,} offres")
#                 else:
#                     st.info("ℹ️ Aucune compétence trouvée")
#             else:
#                 st.warning("❌ Colonne 'skills_list' manquante")
#
#         with tab3:
#             if 'company_name' in df.columns:
#                 top_companies = df['company_name'].value_counts().head(10)
#                 if not top_companies.empty:
#                     st.bar_chart(top_companies)
#                     st.write("**Entreprises qui recrutent le plus:**")
#                     for company, count in top_companies.head(5).items():
#                         st.write(f"- {company}: {count:,} offres")
#                 else:
#                     st.info("ℹ️ Aucune donnée d'entreprises disponible")
#             else:
#                 st.warning("❌ Colonne 'company_name' manquante")
#
#     except Exception as e:
#         st.error(f"❌ Erreur dans l'affichage de la vue d'ensemble: {str(e)}")
#         st.info("💡 Vérifiez que votre fichier de données contient les colonnes nécessaires")
#
#
# def show_nlp_analysis(df, nlp_analyzer):
#     st.header("🧠 Analyse Intelligente des Offres")
#
#     tab1, tab2 = st.tabs(["🎪 Classification des Postes", "🔍 Extraction de Compétences"])
#
#     with tab1:
#         st.subheader("Classification Automatique des Postes")
#
#         if st.button("🎯 Classifier tous les postes", type="primary"):
#             with st.spinner("Analyse en cours... Cela peut prendre quelques secondes"):
#                 try:
#                     df_classified = nlp_analyzer.classify_jobs(df)
#
#                     # Afficher les résultats
#                     col1, col2 = st.columns([2, 1])
#
#                     with col1:
#                         st.success("✅ Classification terminée!")
#
#                         # Graphique des catégories
#                         if 'predicted_category' in df_classified.columns:
#                             category_counts = df_classified['predicted_category'].value_counts()
#                             if not category_counts.empty:
#                                 st.bar_chart(category_counts)
#                             else:
#                                 st.warning("❌ Aucune catégorie prédite")
#                         else:
#                             st.warning("❌ Colonne 'predicted_category' manquante")
#
#                     with col2:
#                         st.subheader("📈 Répartition")
#                         if 'predicted_category' in df_classified.columns:
#                             category_counts = df_classified['predicted_category'].value_counts()
#                             for category, count in category_counts.head(8).items():
#                                 st.write(f"**{category}**: {count:,}")
#                         else:
#                             st.write("Aucune donnée disponible")
#
#                     # Exemples
#                     st.subheader("🎓 Exemples de classification")
#                     if 'job_title' in df_classified.columns and 'predicted_category' in df_classified.columns:
#                         sample_data = df_classified[['job_title', 'predicted_category']].head(8)
#                         if not sample_data.empty:
#                             for _, row in sample_data.iterrows():
#                                 st.write(f"- **{row['job_title']}** → *{row['predicted_category']}*")
#                         else:
#                             st.write("Aucun exemple disponible")
#                     else:
#                         st.write("Données d'exemple non disponibles")
#
#                 except Exception as e:
#                     st.error(f"❌ Erreur lors de la classification: {str(e)}")
#
#     with tab2:
#         st.subheader("🔧 Extraction de Compétences")
#
#         # Exemples prédéfinis pour plus de rapidité
#         example_choice = st.selectbox(
#             "Choisir un exemple type:",
#             [
#                 "✍️ Saisir manuellement...",
#                 "👨‍💻 Data Scientist Python SQL ML",
#                 "👨‍🔧 Data Engineer Spark AWS ETL",
#                 "👨‍💼 Data Analyst Tableau SQL Excel",
#                 "🤖 ML Engineer TensorFlow Python",
#                 "📊 Data Engineer compétences techniques"
#             ]
#         )
#
#         # Text input adaptatif
#         default_text = ""
#         if "Data Scientist" in example_choice:
#             default_text = "Nous recherchons un Data Scientist expérimenté avec Python, SQL, Machine Learning, et compétences en analyse statistique."
#         elif "Data Engineer" in example_choice:
#             default_text = "Poste d'Ingénieur Data nécessitant Spark, Hadoop, AWS, ETL, et compétences en architecture données."
#         elif "Data Analyst" in example_choice:
#             default_text = "Analyste données maîtrisant Tableau, SQL, Excel, Power BI et ayant des compétences en visualisation."
#         elif "ML Engineer" in example_choice:
#             default_text = "Ingénieur Machine Learning expert en TensorFlow, PyTorch, Python, Deep Learning et ML ops."
#         elif "compétences techniques" in example_choice:
#             default_text = "Data Engineer avec expertise en Python, SQL, Spark, AWS, Docker, et Data Pipelines."
#
#         text_input = st.text_area(
#             "Description du poste à analyser:",
#             value=default_text if example_choice != "✍️ Saisir manuellement..." else "",
#             height=100,
#             placeholder="Entrez une description de poste pour extraire les compétences techniques..."
#         )
#
#         if st.button("🔎 Extraire les compétences", type="primary") and text_input:
#             with st.spinner("Analyse du texte en cours..."):
#                 try:
#                     skills = nlp_analyzer.extract_skills(text_input)
#
#                     if skills:
#                         st.success(f"🎉 {len(skills)} compétences identifiées:")
#
#                         # Afficher en colonnes
#                         cols = st.columns(3)
#                         for i, skill in enumerate(skills):
#                             with cols[i % 3]:
#                                 st.info(f"**{skill.capitalize()}**")
#                     else:
#                         st.warning("🤔 Aucune compétence technique identifiée dans le texte.")
#                 except Exception as e:
#                     st.error(f"❌ Erreur lors de l'extraction: {str(e)}")
#
#
# def show_advanced_analysis(df, advanced_analyzer):
#     """Affiche l'analyse avancée avec BERT/DistilBERT"""
#     st.header("🤖 Analyse Avancée avec Transformers (BERT/DistilBERT)")
#
#     advanced = AdvancedAnalysis()
#
#     tab1, tab2, tab3 = st.tabs([
#         "🚀 Benchmark Modèles",
#         "🔍 Extraction Entités",
#         "🎯 Clustering Avancé"
#     ])
#
#     with tab1:
#         advanced.show_bert_vs_distilbert_analysis(df)
#
#     with tab2:
#         advanced.show_entity_extraction_analysis(df)
#
#     with tab3:
#         advanced.show_clustering_analysis(df)
#
#
# def show_skill_graph(df, graph_builder):
#     st.header("🕸️ Réseau des Compétences et Métiers")
#
#     st.info("""
#     **ℹ️ Cette visualisation montre les relations entre:**
#     - 🔴 **Entreprises** et les postes qu'elles proposent
#     - 🔵 **Postes** et les compétences requises
#     - 🟢 **Compétences** partagées entre différents postes
#
#     *Note: Pour les grands datasets, la génération peut prendre quelques instants*
#     """)
#
#     # Vérifier les colonnes nécessaires
#     required_columns = ['company_name', 'job_title_short', 'skills_list']
#     missing_columns = [col for col in required_columns if col not in df.columns]
#
#     if missing_columns:
#         st.error(f"❌ Colonnes manquantes pour construire le graphe: {missing_columns}")
#         st.info("💡 Le graphe nécessite les colonnes: company_name, job_title_short, skills_list")
#         return
#
#     # Contrôles
#     col1, col2, col3 = st.columns(3)
#
#     with col1:
#         graph_size_option = st.selectbox(
#             "Taille du graphe:",
#             ["🔍 Petit (rapide)", "📊 Moyen", "🌐 Grand (complet)"],
#             index=1
#         )
#
#     with col2:
#         sample_data = st.checkbox("Échantillonner les données", value=True,
#                                   help="Prend un échantillon pour accélérer la génération")
#
#     with col3:
#         if st.button("🔄 Générer le Réseau", type="primary", use_container_width=True):
#             st.session_state.generate_graph = True
#
#     # Génération conditionnelle
#     if st.session_state.get('generate_graph', False):
#         with st.spinner("🛠️ Construction du réseau en cours... (cela peut prendre quelques secondes)"):
#             try:
#                 # Paramètres selon la taille
#                 size_params = {
#                     "🔍 Petit (rapide)": (10, 3),
#                     "📊 Moyen": (20, 5),
#                     "🌐 Grand (complet)": (30, 8)
#                 }
#                 max_companies, max_skills = size_params[graph_size_option]
#
#                 # Échantillonner les données si demandé
#                 df_for_graph = df
#                 if sample_data and len(df) > 1000:
#                     df_for_graph = df.sample(min(1000, len(df)), random_state=42)
#                     st.info(f"📊 Utilisation d'un échantillon de {len(df_for_graph):,} offres pour la génération")
#
#                 G = graph_builder.build_graph(df_for_graph, max_companies, max_skills)
#
#                 # Vérifier que le graphe a été construit
#                 if G is None or G.number_of_nodes() == 0:
#                     st.error("❌ Le graphe n'a pas pu être construit (aucun nœud)")
#                     return
#
#                 # Métriques du réseau
#                 st.subheader("📊 Statistiques du Réseau")
#
#                 metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
#
#                 with metrics_col1:
#                     st.metric("🏷️ Nœuds", f"{G.number_of_nodes():,}")
#                     st.metric("🔗 Liens", f"{G.number_of_edges():,}")
#
#                 with metrics_col2:
#                     try:
#                         density = nx.density(G)
#                         st.metric("📈 Densité", f"{density:.4f}")
#                     except:
#                         st.metric("📈 Densité", "N/A")
#
#                     # Vérifier si le graphe est connecté avant de calculer le diamètre
#                     diameter = "N/A"
#                     try:
#                         if nx.is_connected(G):
#                             diameter = nx.diameter(G)
#                         else:
#                             diameter = "Non connecté"
#                     except:
#                         diameter = "N/A"
#                     st.metric("🔄 Diamètre", diameter)
#
#                 with metrics_col3:
#                     if G.number_of_nodes() > 0:
#                         try:
#                             degree_centrality = nx.degree_centrality(G)
#                             if degree_centrality:
#                                 max_node = max(degree_centrality, key=degree_centrality.get)
#                                 node_label = G.nodes[max_node].get('label', str(max_node))
#                                 st.metric("⭐ Nœud central",
#                                           node_label[:25] + "..." if len(node_label) > 25 else node_label)
#                             else:
#                                 st.metric("⭐ Nœud central", "N/A")
#                         except:
#                             st.metric("⭐ Nœud central", "N/A")
#                     else:
#                         st.metric("⭐ Nœud central", "N/A")
#
#                 # Visualisation
#                 st.subheader("🎨 Visualisation Interactive")
#                 fig = graph_builder.visualize_graph(G)
#                 if fig:
#                     st.plotly_chart(fig, use_container_width=True)
#                 else:
#                     st.error("❌ Erreur lors de la génération de la visualisation")
#
#                 # Analyses avancées (optionnelles)
#                 with st.expander("🔍 Analyses Avancées"):
#                     st.write("**Communautés détectées:**")
#                     try:
#                         import community as community_louvain
#                         partition = community_louvain.best_partition(G)
#                         community_count = len(set(partition.values()))
#                         st.write(f"Nombre de communautés: {community_count}")
#
#                         # Afficher les 3 plus grandes communautés
#                         community_sizes = {}
#                         for node, comm_id in partition.items():
#                             community_sizes[comm_id] = community_sizes.get(comm_id, 0) + 1
#
#                         top_communities = sorted(community_sizes.items(), key=lambda x: x[1], reverse=True)[:3]
#                         for comm_id, size in top_communities:
#                             st.write(f"- Communauté {comm_id}: {size} nœuds")
#
#                     except ImportError as e:
#                         st.write("ℹ️ Package 'python-louvain' requis pour cette analyse")
#                     except Exception as e:
#                         st.write(f"❌ Erreur lors de l'analyse des communautés: {e}")
#
#             except Exception as e:
#                 st.error(f"❌ Erreur lors de la construction du graphe: {str(e)}")
#                 st.info("💡 Essayez une taille de graphe plus petite ou activez l'échantillonnage")
#
#
# def show_qa_system(df, qa_system):
#     st.header("❓ Assistant Intelligent - Questions/Réponses")
#
#     # Vérifier que le système Q&A peut fonctionner
#     required_columns = ['company_name', 'job_title_short', 'skills_list']
#     missing_columns = [col for col in required_columns if col not in df.columns]
#
#     if missing_columns:
#         st.error(f"❌ Colonnes manquantes pour le système Q&A: {missing_columns}")
#         st.info("💡 Le système Q&A nécessite les colonnes: company_name, job_title_short, skills_list")
#         return
#
#     # Initialisation du QASystem
#     if not hasattr(st.session_state, 'qa_initialized') or not st.session_state.qa_initialized:
#         with st.spinner("🔄 Initialisation de l'assistant intelligent... (cela peut prendre quelques secondes)"):
#             try:
#                 qa_system.build_knowledge_base(df)
#                 st.session_state.qa_initialized = True
#                 st.success("✅ Assistant initialisé avec succès!")
#
#                 # Afficher les statistiques de l'initialisation
#                 with st.expander("📊 Statistiques de l'assistant"):
#                     if hasattr(qa_system, '_precomputed_answers'):
#                         answers = qa_system._precomputed_answers
#                         st.write(f"• Compétences analysées: {len(answers.get('top_skills', [])):,}")
#                         st.write(f"• Entreprises recensées: {len(answers.get('top_companies', [])):,}")
#                         st.write(f"• Postes suivis: {len(answers.get('top_jobs', [])):,}")
#             except Exception as e:
#                 st.error(f"❌ Erreur lors de l'initialisation de l'assistant: {str(e)}")
#                 st.session_state.qa_initialized = False
#                 return
#
#     st.info("""
#     **💡 Exemples de questions:**
#     - "Quelles sont les compétences les plus demandées ?"
#     - "Quelles entreprises recherchen Python et Machine Learning ?"
#     - "Quels sont les salaires pour les Data Scientists ?"
#     - "Quels postes nécessitent TensorFlow ?"
#     - "Compétences des Data Engineers ?"
#     - "Statistiques du marché data"
#     - "Quelles entreprises recrutent le plus ?"
#     """)
#
#     # Questions rapides
#     st.subheader("🚀 Questions Rapides")
#
#     quick_questions = [
#         "Quelles sont les compétences les plus demandées?",
#         "Quelles entreprises recherchent Python?",
#         "Quels sont les salaires moyens?",
#         "Quels sont les postes les plus courants?",
#         "Compétences des Data Engineers?",
#         "Statistiques du marché data?",
#         "Quelles entreprises recrutent le plus?"
#     ]
#
#     # Afficher les questions rapides en grille
#     cols = st.columns(2)
#     for i, question in enumerate(quick_questions):
#         with cols[i % 2]:
#             if st.button(f"📌 {question}", key=f"quick_{i}", use_container_width=True):
#                 with st.spinner("🔍 Recherche en cours..."):
#                     try:
#                         answer = qa_system.answer_question(question)
#                         st.session_state.last_question = question
#                         st.session_state.last_answer = answer
#                     except Exception as e:
#                         st.error(f"❌ Erreur lors du traitement de la question: {str(e)}")
#                         st.session_state.last_answer = "❌ Une erreur s'est produite lors du traitement de votre question."
#
#     # Question personnalisée
#     st.subheader("🔍 Question Personnalisée")
#
#     question_input = st.text_input(
#         "Votre question:",
#         placeholder="Ex: Quelles entreprises recherchent des compétences en Python et AWS ?",
#         key="custom_question"
#     )
#
#     col1, col2 = st.columns([3, 1])
#
#     with col2:
#         ask_button = st.button("🎯 Poser la question", type="primary", use_container_width=True)
#
#     # Gestion des réponses
#     if ask_button and question_input:
#         with st.spinner("🔍 Analyse en cours..."):
#             try:
#                 answer = qa_system.answer_question(question_input)
#                 st.session_state.last_question = question_input
#                 st.session_state.last_answer = answer
#             except Exception as e:
#                 st.error(f"❌ Erreur lors du traitement de la question: {str(e)}")
#                 st.session_state.last_answer = "❌ Une erreur s'est produite lors du traitement de votre question."
#
#     # Affichage de la réponse
#     if hasattr(st.session_state, 'last_answer') and st.session_state.last_answer:
#         st.markdown("---")
#         st.subheader("💬 Réponse:")
#
#         # Afficher la question
#         if hasattr(st.session_state, 'last_question'):
#             st.write(f"**Question:** {st.session_state.last_question}")
#
#         # Afficher la réponse formatée
#         st.success(st.session_state.last_answer)
#
#         # Bouton pour poser une nouvelle question
#         if st.button("🔄 Poser une nouvelle question"):
#             st.session_state.last_question = ""
#             st.session_state.last_answer = ""
#             st.rerun()
#
#
# # Initialisation des variables de session
# if 'generate_graph' not in st.session_state:
#     st.session_state.generate_graph = False
# if 'last_question' not in st.session_state:
#     st.session_state.last_question = ""
# if 'last_answer' not in st.session_state:
#     st.session_state.last_answer = ""
# if 'qa_initialized' not in st.session_state:
#     st.session_state.qa_initialized = False
#
# if __name__ == "__main__":
#     main()


import pandas as pd
import numpy as np
import streamlit as st
import networkx as nx
from src.data_processing import DataProcessor
from src.nlp_analysis import NLPAnalyzer, AdvancedNLPAnalyzer
from src.graph_builder import GraphBuilder
from src.qa_system import QASystem

# Configuration de la page
st.set_page_config(
    page_title="Analyse des Offres d'Emploi Data",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Cache pour les données seulement
@st.cache_data
def load_data():
    """Charge les données avec cache"""
    try:
        processor = DataProcessor("data/data_jobs_cleaned.xlsx")
        df = processor.load_and_clean_data()

        # Vérifier que le DataFrame a les colonnes minimales requises
        if not df.empty:
            required_columns = ['company_name', 'job_title_short', 'skills_list']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                st.warning(f"⚠️ Colonnes manquantes: {missing_columns}")

        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement: {e}")
        return pd.DataFrame()


# Cache pour les analyseurs
@st.cache_resource
def load_nlp_analyzer():
    return NLPAnalyzer()


@st.cache_resource
def load_advanced_nlp_analyzer():
    return AdvancedNLPAnalyzer(use_gpu=False)


@st.cache_resource
def load_graph_builder():
    return GraphBuilder()


@st.cache_resource
def load_qa_system():
    return QASystem()


def main():
    st.title("🔍 Système d'Analyse des Offres d'Emploi Data")

    # Initialisation avec indicateurs de progression
    with st.spinner("Initialisation du système..."):
        df = load_data()
        nlp_analyzer = load_nlp_analyzer()
        advanced_analyzer = load_advanced_nlp_analyzer()
        graph_builder = load_graph_builder()
        qa_system = load_qa_system()

    if df.empty:
        st.error("""
        ❌ Impossible de charger les données. 

        Vérifiez que:
        1. Le fichier `data_jobs_cleaned.xlsx` existe dans le dossier `data/`
        2. Le fichier n'est pas corrompu
        3. Vous avez les permissions de lecture
        """)
        return

    # Afficher un message de succès avec informations sur les données
    st.success(f"✅ Données chargées: {len(df):,} offres d'emploi")

    # Afficher les colonnes disponibles pour debug
    with st.expander("🔍 Informations techniques (debug)"):
        st.write(f"**Colonnes disponibles:** {list(df.columns)}")
        st.write(f"**Nombre d'entreprises:** {df['company_name'].nunique() if 'company_name' in df.columns else 'N/A'}")
        st.write(
            f"**Nombre de compétences uniques:** {df['skills_list'].explode().nunique() if 'skills_list' in df.columns else 'N/A'}")
        st.write(f"**Taille du dataset:** {df.memory_usage(deep=True).sum() / 1024 ** 2:.2f} MB")

    # Sidebar pour la navigation
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.radio(
        "Choisir une section",
        [
            "🏠 Vue d'ensemble",
            "🧠 Analyse NLP",
            "🤖 Analyse Avancée BERT",
            "🕸️ Graphe des Compétences",
            "❓ Système de Q&A"
        ],
        index=0
    )

    # Navigation
    if "Vue d'ensemble" in page:
        show_overview(df)
    elif "Analyse NLP" in page:
        show_nlp_analysis(df, nlp_analyzer)
    elif "Analyse Avancée BERT" in page:
        show_advanced_analysis(df, advanced_analyzer)
    elif "Graphe des Compétences" in page:
        show_skill_graph(df, graph_builder)
    elif "Système de Q&A" in page:
        show_qa_system(df, qa_system)


def show_overview(df):
    st.header("📊 Vue d'ensemble du Marché de l'Emploi Data")

    try:
        # Métriques principales en temps réel avec vérifications
        col1, col2, col3, col4 = st.columns(4)

        total_jobs = len(df)

        unique_companies = df['company_name'].nunique() if 'company_name' in df.columns else 0
        unique_skills = df['skills_list'].explode().nunique() if 'skills_list' in df.columns else 0

        # Gestion du salaire moyen
        avg_salary = None
        if 'salary_year_avg' in df.columns:
            avg_salary = df['salary_year_avg'].mean()
        salary_display = f"${avg_salary:,.0f}" if avg_salary and not pd.isna(avg_salary) else "N/A"

        with col1:
            st.metric("📋 Offres d'emploi", f"{total_jobs:,}")

        with col2:
            st.metric("🏢 Entreprises", f"{unique_companies:,}")

        with col3:
            st.metric("🛠️ Compétences", f"{unique_skills:,}")

        with col4:
            st.metric("💰 Salaire moyen", salary_display)

        # Graphiques rapides avec vérifications
        st.subheader("🎯 Tendances du Marché")

        tab1, tab2, tab3 = st.tabs(["📊 Postes", "🛠️ Compétences", "🏢 Entreprises"])

        with tab1:
            if 'job_title_short' in df.columns:
                top_jobs = df['job_title_short'].value_counts().head(10)
                if not top_jobs.empty:
                    st.bar_chart(top_jobs)
                    st.write("**Postes les plus demandés:**")
                    for job, count in top_jobs.head(5).items():
                        st.write(f"- {job}: {count:,} offres")
                else:
                    st.info("ℹ️ Aucune donnée de postes disponible")
            else:
                st.warning("❌ Colonne 'job_title_short' manquante")

        with tab2:
            if 'skills_list' in df.columns:
                all_skills = df['skills_list'].explode()
                top_skills = all_skills.value_counts().head(10)
                if not top_skills.empty:
                    st.bar_chart(top_skills)
                    st.write("**Compétences les plus recherchées:**")
                    for skill, count in top_skills.head(5).items():
                        st.write(f"- {skill}: {count:,} offres")
                else:
                    st.info("ℹ️ Aucune compétence trouvée")
            else:
                st.warning("❌ Colonne 'skills_list' manquante")

        with tab3:
            if 'company_name' in df.columns:
                top_companies = df['company_name'].value_counts().head(10)
                if not top_companies.empty:
                    st.bar_chart(top_companies)
                    st.write("**Entreprises qui recrutent le plus:**")
                    for company, count in top_companies.head(5).items():
                        st.write(f"- {company}: {count:,} offres")
                else:
                    st.info("ℹ️ Aucune donnée d'entreprises disponible")
            else:
                st.warning("❌ Colonne 'company_name' manquante")

    except Exception as e:
        st.error(f"❌ Erreur dans l'affichage de la vue d'ensemble: {str(e)}")
        st.info("💡 Vérifiez que votre fichier de données contient les colonnes nécessaires")


def show_nlp_analysis(df, nlp_analyzer):
    st.header("🧠 Analyse Intelligente des Offres")

    tab1, tab2 = st.tabs(["🎪 Classification des Postes", "🔍 Extraction de Compétences"])

    with tab1:
        st.subheader("Classification Automatique des Postes")

        if st.button("🎯 Classifier tous les postes", type="primary"):
            with st.spinner("Analyse en cours... Cela peut prendre quelques secondes"):
                try:
                    df_classified = nlp_analyzer.classify_jobs(df)

                    # Afficher les résultats
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.success("✅ Classification terminée!")

                        # Graphique des catégories
                        if 'predicted_category' in df_classified.columns:
                            category_counts = df_classified['predicted_category'].value_counts()
                            if not category_counts.empty:
                                st.bar_chart(category_counts)
                            else:
                                st.warning("❌ Aucune catégorie prédite")
                        else:
                            st.warning("❌ Colonne 'predicted_category' manquante")

                    with col2:
                        st.subheader("📈 Répartition")
                        if 'predicted_category' in df_classified.columns:
                            category_counts = df_classified['predicted_category'].value_counts()
                            for category, count in category_counts.head(8).items():
                                st.write(f"**{category}**: {count:,}")
                        else:
                            st.write("Aucune donnée disponible")

                    # Exemples
                    st.subheader("🎓 Exemples de classification")
                    if 'job_title' in df_classified.columns and 'predicted_category' in df_classified.columns:
                        sample_data = df_classified[['job_title', 'predicted_category']].head(8)
                        if not sample_data.empty:
                            for _, row in sample_data.iterrows():
                                st.write(f"- **{row['job_title']}** → *{row['predicted_category']}*")
                        else:
                            st.write("Aucun exemple disponible")
                    else:
                        st.write("Données d'exemple non disponibles")

                except Exception as e:
                    st.error(f"❌ Erreur lors de la classification: {str(e)}")

    with tab2:
        st.subheader("🔧 Extraction de Compétences")

        # Exemples prédéfinis pour plus de rapidité
        example_choice = st.selectbox(
            "Choisir un exemple type:",
            [
                "✍️ Saisir manuellement...",
                "👨‍💻 Data Scientist Python SQL ML",
                "👨‍🔧 Data Engineer Spark AWS ETL",
                "👨‍💼 Data Analyst Tableau SQL Excel",
                "🤖 ML Engineer TensorFlow Python",
                "📊 Data Engineer compétences techniques"
            ]
        )

        # Text input adaptatif
        default_text = ""
        if "Data Scientist" in example_choice:
            default_text = "Nous recherchons un Data Scientist expérimenté avec Python, SQL, Machine Learning, et compétences en analyse statistique."
        elif "Data Engineer" in example_choice:
            default_text = "Poste d'Ingénieur Data nécessitant Spark, Hadoop, AWS, ETL, et compétences en architecture données."
        elif "Data Analyst" in example_choice:
            default_text = "Analyste données maîtrisant Tableau, SQL, Excel, Power BI et ayant des compétences en visualisation."
        elif "ML Engineer" in example_choice:
            default_text = "Ingénieur Machine Learning expert en TensorFlow, PyTorch, Python, Deep Learning et ML ops."
        elif "compétences techniques" in example_choice:
            default_text = "Data Engineer avec expertise en Python, SQL, Spark, AWS, Docker, et Data Pipelines."

        text_input = st.text_area(
            "Description du poste à analyser:",
            value=default_text if example_choice != "✍️ Saisir manuellement..." else "",
            height=100,
            placeholder="Entrez une description de poste pour extraire les compétences techniques..."
        )

        if st.button("🔎 Extraire les compétences", type="primary") and text_input:
            with st.spinner("Analyse du texte en cours..."):
                try:
                    skills = nlp_analyzer.extract_skills(text_input)

                    if skills:
                        st.success(f"🎉 {len(skills)} compétences identifiées:")

                        # Afficher en colonnes
                        cols = st.columns(3)
                        for i, skill in enumerate(skills):
                            with cols[i % 3]:
                                st.info(f"**{skill.capitalize()}**")
                    else:
                        st.warning("🤔 Aucune compétence technique identifiée dans le texte.")
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'extraction: {str(e)}")


def show_advanced_analysis(df, advanced_analyzer):
    """Affiche l'analyse avancée avec BERT/DistilBERT"""
    st.header("🤖 Analyse Avancée avec Transformers (BERT/DistilBERT)")

    tab1, tab2, tab3 = st.tabs([
        "🚀 Benchmark Modèles",
        "🔍 Extraction Entités",
        "🎯 Clustering Avancé"
    ])

    with tab1:
        st.subheader("Comparaison des Performances BERT vs DistilBERT")
        advanced_analyzer.benchmark_models(df)

        # Visualisation des embeddings
        st.subheader("📊 Visualisation des Embeddings")
        n_clusters = st.slider("Nombre de clusters pour la visualisation", 2, 6, 3, key="viz_clusters")

        if st.button("🔄 Générer les visualisations"):
            with st.spinner("Génération des visualisations..."):
                figs = advanced_analyzer.visualize_embeddings_comparison(df, n_clusters)
                for model_name, fig in figs:
                    if fig:
                        st.subheader(f"{model_name}")
                        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("🧪 Extraction d'Entités Nommées")

        example_choice = st.selectbox(
            "Choisir un exemple:",
            [
                "📝 Saisir manuellement...",
                "👨‍💻 Data Scientist avec Python et ML",
                "👨‍🔧 Data Engineer Spark AWS",
                "📊 Analyste données SQL Tableau"
            ],
            key="entity_example"
        )

        default_text = ""
        if "Data Scientist" in example_choice:
            default_text = "Google recrute un Data Scientist senior maîtrisant Python, TensorFlow, SQL. Expérience en machine learning requise. Basé à Paris."
        elif "Data Engineer" in example_choice:
            default_text = "Amazon cherche un Data Engineer expert en Spark, AWS, Kafka. Connaissance de Docker et Kubernetes nécessaire."
        elif "Analyste" in example_choice:
            default_text = "Microsoft recherche un Analyste données avec compétences en SQL, Tableau, Excel. Poste à Londres."

        text_input = st.text_area(
            "Texte à analyser:",
            value=default_text if example_choice != "📝 Saisir manuellement..." else "",
            height=150,
            key="entity_text"
        )

        if st.button("🔎 Extraire les entités", type="primary", key="extract_entities") and text_input:
            with st.spinner("Extraction des entités en cours..."):
                entities = advanced_analyzer.extract_entities_advanced(text_input)

                # Affichage des résultats
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.subheader("🛠️ Compétences")
                    for skill in entities['skills']:
                        st.success(f"• {skill}")
                    if not entities['skills']:
                        st.info("Aucune compétence trouvée")

                with col2:
                    st.subheader("💻 Technologies")
                    for tech in entities['technologies']:
                        st.info(f"• {tech}")
                    if not entities['technologies']:
                        st.info("Aucune technologie trouvée")

                with col3:
                    st.subheader("🏢 Entreprises")
                    for company in entities['companies']:
                        st.warning(f"• {company}")
                    if not entities['companies']:
                        st.info("Aucune entreprise trouvée")

    with tab3:
        st.subheader("🎯 Clustering Intelligent des Postes")

        col1, col2 = st.columns(2)

        with col1:
            model_choice = st.selectbox(
                "Modèle pour le clustering:",
                ["bert", "distilbert"],
                help="BERT: plus précis mais plus lent, DistilBERT: plus rapide mais légèrement moins précis",
                key="cluster_model"
            )

        with col2:
            n_clusters = st.slider("Nombre de clusters", 3, 10, 5, key="n_clusters")

        if st.button("🎪 Lancer le clustering", type="primary", key="run_clustering"):
            with st.spinner(f"Clustering avec {model_choice} en cours..."):
                df_clustered, embeddings, clusters = advanced_analyzer.cluster_job_titles(
                    df, model_choice, n_clusters
                )

                if embeddings is not None and clusters is not None:
                    st.success(f"✅ Clustering terminé! {len(np.unique(clusters))} clusters identifiés")

                    # Visualisation
                    fig = advanced_analyzer._create_embedding_plot(
                        embeddings, f"Clustering des Postes - {model_choice.upper()}", n_clusters
                    )
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)

                    # Analyse des clusters
                    st.subheader("📋 Analyse des Clusters")

                    cluster_analysis = []
                    for cluster_id in range(n_clusters):
                        cluster_jobs = df_clustered[df_clustered['embedding_cluster'] == cluster_id]
                        if len(cluster_jobs) > 0:
                            common_titles = cluster_jobs['job_title'].value_counts().head(3)
                            cluster_analysis.append({
                                'Cluster': cluster_id,
                                'Nombre de postes': len(cluster_jobs),
                                'Titres représentatifs': ', '.join([f"{title} ({count})"
                                                                    for title, count in common_titles.items()])
                            })

                    if cluster_analysis:
                        analysis_df = pd.DataFrame(cluster_analysis)
                        st.dataframe(analysis_df, use_container_width=True)
                else:
                    st.error("❌ Le clustering n'a pas pu être effectué")


def show_skill_graph(df, graph_builder):
    st.header("🕸️ Réseau des Compétences et Métiers")

    st.info("""
    **ℹ️ Cette visualisation montre les relations entre:**
    - 🔴 **Entreprises** et les postes qu'elles proposent  
    - 🔵 **Postes** et les compétences requises
    - 🟢 **Compétences** partagées entre différents postes

    *Note: Pour les grands datasets, la génération peut prendre quelques instants*
    """)

    # Vérifier les colonnes nécessaires
    required_columns = ['company_name', 'job_title_short', 'skills_list']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"❌ Colonnes manquantes pour construire le graphe: {missing_columns}")
        st.info("💡 Le graphe nécessite les colonnes: company_name, job_title_short, skills_list")
        return

    # Contrôles
    col1, col2, col3 = st.columns(3)

    with col1:
        graph_size_option = st.selectbox(
            "Taille du graphe:",
            ["🔍 Petit (rapide)", "📊 Moyen", "🌐 Grand (complet)"],
            index=1
        )

    with col2:
        sample_data = st.checkbox("Échantillonner les données", value=True,
                                  help="Prend un échantillon pour accélérer la génération")

    with col3:
        if st.button("🔄 Générer le Réseau", type="primary", use_container_width=True):
            st.session_state.generate_graph = True

    # Génération conditionnelle
    if st.session_state.get('generate_graph', False):
        with st.spinner("🛠️ Construction du réseau en cours... (cela peut prendre quelques secondes)"):
            try:
                # Paramètres selon la taille
                size_params = {
                    "🔍 Petit (rapide)": (10, 3),
                    "📊 Moyen": (20, 5),
                    "🌐 Grand (complet)": (30, 8)
                }
                max_companies, max_skills = size_params[graph_size_option]

                # Échantillonner les données si demandé
                df_for_graph = df
                if sample_data and len(df) > 1000:
                    df_for_graph = df.sample(min(1000, len(df)), random_state=42)
                    st.info(f"📊 Utilisation d'un échantillon de {len(df_for_graph):,} offres pour la génération")

                G = graph_builder.build_graph(df_for_graph, max_companies, max_skills)

                # Vérifier que le graphe a été construit
                if G is None or G.number_of_nodes() == 0:
                    st.error("❌ Le graphe n'a pas pu être construit (aucun nœud)")
                    return

                # Métriques du réseau
                st.subheader("📊 Statistiques du Réseau")

                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

                with metrics_col1:
                    st.metric("🏷️ Nœuds", f"{G.number_of_nodes():,}")
                    st.metric("🔗 Liens", f"{G.number_of_edges():,}")

                with metrics_col2:
                    try:
                        density = nx.density(G)
                        st.metric("📈 Densité", f"{density:.4f}")
                    except:
                        st.metric("📈 Densité", "N/A")

                    # Vérifier si le graphe est connecté avant de calculer le diamètre
                    diameter = "N/A"
                    try:
                        if nx.is_connected(G):
                            diameter = nx.diameter(G)
                        else:
                            diameter = "Non connecté"
                    except:
                        diameter = "N/A"
                    st.metric("🔄 Diamètre", diameter)

                with metrics_col3:
                    if G.number_of_nodes() > 0:
                        try:
                            degree_centrality = nx.degree_centrality(G)
                            if degree_centrality:
                                max_node = max(degree_centrality, key=degree_centrality.get)
                                node_label = G.nodes[max_node].get('label', str(max_node))
                                st.metric("⭐ Nœud central",
                                          node_label[:25] + "..." if len(node_label) > 25 else node_label)
                            else:
                                st.metric("⭐ Nœud central", "N/A")
                        except:
                            st.metric("⭐ Nœud central", "N/A")
                    else:
                        st.metric("⭐ Nœud central", "N/A")

                # Visualisation
                st.subheader("🎨 Visualisation Interactive")
                fig = graph_builder.visualize_graph(G)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("❌ Erreur lors de la génération de la visualisation")

                # Analyses avancées (optionnelles)
                with st.expander("🔍 Analyses Avancées"):
                    st.write("**Communautés détectées:**")
                    try:
                        # Correction de l'import community_louvain
                        import community as community_louvain
                        partition = community_louvain.best_partition(G)
                        community_count = len(set(partition.values()))
                        st.write(f"Nombre de communautés: {community_count}")

                        # Afficher les 3 plus grandes communautés
                        community_sizes = {}
                        for node, comm_id in partition.items():
                            community_sizes[comm_id] = community_sizes.get(comm_id, 0) + 1

                        top_communities = sorted(community_sizes.items(), key=lambda x: x[1], reverse=True)[:3]
                        for comm_id, size in top_communities:
                            st.write(f"- Communauté {comm_id}: {size} nœuds")

                    except ImportError as e:
                        st.write("ℹ️ Package 'python-louvain' requis pour cette analyse")
                    except Exception as e:
                        st.write(f"❌ Erreur lors de l'analyse des communautés: {e}")

            except Exception as e:
                st.error(f"❌ Erreur lors de la construction du graphe: {str(e)}")
                st.info("💡 Essayez une taille de graphe plus petite ou activez l'échantillonnage")


def show_qa_system(df, qa_system):
    st.header("❓ Assistant Intelligent - Questions/Réponses")

    # Vérifier que le système Q&A peut fonctionner
    required_columns = ['company_name', 'job_title_short', 'skills_list']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"❌ Colonnes manquantes pour le système Q&A: {missing_columns}")
        st.info("💡 Le système Q&A nécessite les colonnes: company_name, job_title_short, skills_list")
        return

    # Initialisation du QASystem
    if not hasattr(st.session_state, 'qa_initialized') or not st.session_state.qa_initialized:
        with st.spinner("🔄 Initialisation de l'assistant intelligent... (cela peut prendre quelques secondes)"):
            try:
                qa_system.build_knowledge_base(df)
                st.session_state.qa_initialized = True
                st.success("✅ Assistant initialisé avec succès!")

                # Afficher les statistiques de l'initialisation
                with st.expander("📊 Statistiques de l'assistant"):
                    if hasattr(qa_system, '_precomputed_answers'):
                        answers = qa_system._precomputed_answers
                        st.write(f"• Compétences analysées: {len(answers.get('top_skills', [])):,}")
                        st.write(f"• Entreprises recensées: {len(answers.get('top_companies', [])):,}")
                        st.write(f"• Postes suivis: {len(answers.get('top_jobs', [])):,}")
            except Exception as e:
                st.error(f"❌ Erreur lors de l'initialisation de l'assistant: {str(e)}")
                st.session_state.qa_initialized = False
                return

    st.info("""
    **💡 Exemples de questions:**
    - "Quelles sont les compétences les plus demandées ?"
    - "Quelles entreprises recherchent Python et Machine Learning ?"  
    - "Quels sont les salaires pour les Data Scientists ?"
    - "Quels postes nécessitent TensorFlow ?"
    - "Compétences des Data Engineers ?"
    - "Statistiques du marché data"
    - "Quelles entreprises recrutent le plus ?"
    """)

    # Questions rapides
    st.subheader("🚀 Questions Rapides")

    quick_questions = [
        "Quelles sont les compétences les plus demandées?",
        "Quelles entreprises recherchent Python?",
        "Quels sont les salaires moyens?",
        "Quels sont les postes les plus courants?",
        "Compétences des Data Engineers?",
        "Statistiques du marché data?",
        "Quelles entreprises recrutent le plus?"
    ]

    # Afficher les questions rapides en grille
    cols = st.columns(2)
    for i, question in enumerate(quick_questions):
        with cols[i % 2]:
            if st.button(f"📌 {question}", key=f"quick_{i}", use_container_width=True):
                with st.spinner("🔍 Recherche en cours..."):
                    try:
                        answer = qa_system.answer_question(question)
                        st.session_state.last_question = question
                        st.session_state.last_answer = answer
                    except Exception as e:
                        st.error(f"❌ Erreur lors du traitement de la question: {str(e)}")
                        st.session_state.last_answer = "❌ Une erreur s'est produite lors du traitement de votre question."

    # Question personnalisée
    st.subheader("🔍 Question Personnalisée")

    question_input = st.text_input(
        "Votre question:",
        placeholder="Ex: Quelles entreprises recherchent des compétences en Python et AWS ?",
        key="custom_question"
    )

    col1, col2 = st.columns([3, 1])

    with col2:
        ask_button = st.button("🎯 Poser la question", type="primary", use_container_width=True)

    # Gestion des réponses
    if ask_button and question_input:
        with st.spinner("🔍 Analyse en cours..."):
            try:
                answer = qa_system.answer_question(question_input)
                st.session_state.last_question = question_input
                st.session_state.last_answer = answer
            except Exception as e:
                st.error(f"❌ Erreur lors du traitement de la question: {str(e)}")
                st.session_state.last_answer = "❌ Une erreur s'est produite lors du traitement de votre question."

    # Affichage de la réponse
    if hasattr(st.session_state, 'last_answer') and st.session_state.last_answer:
        st.markdown("---")
        st.subheader("💬 Réponse:")

        # Afficher la question
        if hasattr(st.session_state, 'last_question'):
            st.write(f"**Question:** {st.session_state.last_question}")

        # Afficher la réponse formatée
        st.success(st.session_state.last_answer)

        # Bouton pour poser une nouvelle question
        if st.button("🔄 Poser une nouvelle question"):
            st.session_state.last_question = ""
            st.session_state.last_answer = ""
            st.rerun()


# Initialisation des variables de session
if 'generate_graph' not in st.session_state:
    st.session_state.generate_graph = False
if 'last_question' not in st.session_state:
    st.session_state.last_question = ""
if 'last_answer' not in st.session_state:
    st.session_state.last_answer = ""
if 'qa_initialized' not in st.session_state:
    st.session_state.qa_initialized = False

if __name__ == "__main__":
    main()