import pandas as pd
import numpy as np
import torch
from transformers import (
    AutoTokenizer, AutoModel,
    BertTokenizer, BertModel,
    DistilBertTokenizer, DistilBertModel,
    pipeline
)
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.feature_extraction.text import TfidfVectorizer
import plotly.express as px
from sklearn.manifold import TSNE
import re
import streamlit as st
from typing import List, Dict, Tuple
import time
from collections import Counter


class NLPAnalyzer:
    def __init__(self):
        self.skill_patterns = self._load_skill_patterns()

    def _load_skill_patterns(self):
        """Patterns de compétences pour extraction intelligente"""
        return {
            'programming': ['python', 'sql', 'r', 'java', 'scala', 'c++', 'javascript', 'typescript'],
            'ml_frameworks': ['tensorflow', 'pytorch', 'scikit-learn', 'keras', 'mxnet'],
            'big_data': ['spark', 'hadoop', 'kafka', 'hive', 'airflow', 'databricks'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
            'bi_tools': ['tableau', 'power bi', 'looker', 'superset', 'qlik'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'cassandra'],
            'ml_concepts': ['machine learning', 'deep learning', 'nlp', 'computer vision', 'ai'],
            'stats': ['statistics', 'regression', 'classification', 'clustering'],
            'tools': ['git', 'jenkins', 'linux', 'excel', 'jupyter']
        }

    @st.cache_data
    def classify_jobs(_self, df):
        """Classification intelligente des postes"""
        categories = []

        for title in df['job_title'].fillna('').astype(str):
            category = _self._categorize_job_intelligent(title)
            categories.append(category)

        df_result = df.copy()
        df_result['predicted_category'] = categories
        return df_result

    def _categorize_job_intelligent(self, title):
        """Catégorisation intelligente basée sur multiples critères"""
        title_lower = title.lower()

        # Mots-clés hiérarchisés
        primary_keywords = {
            'Data Scientist': ['data scientist', 'ml scientist', 'ai scientist'],
            'Data Engineer': ['data engineer', 'etl engineer', 'data infrastructure'],
            'Data Analyst': ['data analyst', 'business analyst', 'reporting analyst'],
            'Machine Learning Engineer': ['machine learning engineer', 'ml engineer', 'deep learning engineer'],
            'BI Analyst': ['bi analyst', 'business intelligence', 'bi developer'],
            'Data Architect': ['data architect', 'solution architect'],
            'Data Manager': ['data manager', 'data lead', 'head of data']
        }

        secondary_keywords = {
            'Data Scientist': ['machine learning', 'predictive modeling', 'statistical analysis'],
            'Data Engineer': ['pipeline', 'data warehouse', 'big data'],
            'Data Analyst': ['reporting', 'dashboard', 'visualization'],
            'Machine Learning Engineer': ['model deployment', 'mlops', 'model serving']
        }

        # Recherche primaire
        for category, terms in primary_keywords.items():
            if any(term in title_lower for term in terms):
                return category

        # Recherche secondaire
        for category, terms in secondary_keywords.items():
            if any(term in title_lower for term in terms):
                return category

        return 'Autre Rôle Data'

    def extract_skills(self, text):
        """Extraction intelligente des compétences"""
        if not text or pd.isna(text):
            return []

        text_lower = text.lower()
        found_skills = []

        # Recherche par catégories
        for category, skills in self.skill_patterns.items():
            for skill in skills:
                # Recherche exacte pour éviter les faux positifs
                if f" {skill} " in f" {text_lower} ":
                    found_skills.append(skill)

        # Recherche de variantes
        variants_found = self._find_skill_variants(text_lower)
        found_skills.extend(variants_found)

        return list(set(found_skills))  # Éviter les doublons

    def _find_skill_variants(self, text):
        """Trouve des variantes de compétences"""
        variants = []

        # Variantes courantes
        variant_patterns = {
            'python': ['python3', 'python 3'],
            'sql': ['mysql', 'postgresql', 'sql server'],
            'machine learning': ['ml', 'machine-learning'],
            'deep learning': ['dl', 'deep-learning'],
            'aws': ['amazon web services'],
            'power bi': ['powerbi'],
            'tableau': ['tableau software']
        }

        for skill, variant_list in variant_patterns.items():
            for variant in variant_list:
                if variant in text:
                    variants.append(skill)
                    break

        return variants

    def create_skill_embeddings(self, df, n_clusters=6):
        """Crée des embeddings pour le clustering des compétences"""
        try:
            # Préparer les données
            all_skills = df['skills_list'].explode().dropna().unique()
            skill_texts = [str(skill) for skill in all_skills if len(str(skill)) > 2]

            if len(skill_texts) < n_clusters:
                return None, None, skill_texts

            # Vectorisation TF-IDF
            vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2)
            )

            tfidf_matrix = vectorizer.fit_transform(skill_texts)

            # Clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(tfidf_matrix.toarray())

            return tfidf_matrix.toarray(), clusters, skill_texts

        except Exception as e:
            print(f"Erreur clustering: {e}")
            return None, None, []

    def visualize_clusters(self, embeddings, clusters, skill_texts):
        """Visualise les clusters de compétences"""
        if embeddings is None or len(embeddings) == 0:
            return None

        try:
            # Réduction de dimension
            tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(embeddings) - 1))
            embeddings_2d = tsne.fit_transform(embeddings)

            # DataFrame pour visualisation
            plot_df = pd.DataFrame({
                'x': embeddings_2d[:, 0],
                'y': embeddings_2d[:, 1],
                'cluster': clusters,
                'skill': skill_texts
            })

            # Création du graphique
            fig = px.scatter(
                plot_df,
                x='x',
                y='y',
                color='cluster',
                hover_data=['skill'],
                title="🎯 Clustering Intelligent des Compétences",
                labels={'cluster': 'Groupe de Compétences'}
            )

            fig.update_traces(
                marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')),
                selector=dict(mode='markers')
            )

            return fig

        except Exception as e:
            print(f"Erreur visualisation: {e}")
            return None

    def analyze_skill_trends(self, df):
        """Analyse les tendances des compétences"""
        all_skills = df['skills_list'].explode().dropna()

        # Top compétences générales
        top_skills = all_skills.value_counts().head(15)

        # Compétences par type de poste
        skill_by_job = {}
        for job_type in df['job_title_short'].unique():
            if pd.notna(job_type):
                job_skills = df[df['job_title_short'] == job_type]['skills_list'].explode()
                top_job_skills = job_skills.value_counts().head(5)
                skill_by_job[job_type] = top_job_skills

        return {
            'top_skills': top_skills,
            'skills_by_job': skill_by_job
        }


class AdvancedNLPAnalyzer:
    def __init__(self, use_gpu=False):
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.device = torch.device("cuda" if self.use_gpu else "cpu")

        # Chargement des modèles
        self._load_models()
        self._load_skill_patterns()

        # Modèle NER pour l'extraction d'entités
        try:
            self.ner_pipeline = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple",
                device=0 if self.use_gpu else -1
            )
        except Exception as e:
            print(f"NER pipeline non disponible: {e}")
            self.ner_pipeline = None

    def _load_models(self):
        """Charge les modèles BERT et DistilBERT"""
        st.info("🔄 Chargement des modèles BERT et DistilBERT...")

        # BERT
        try:
            self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
            self.bert_model = BertModel.from_pretrained('bert-base-uncased').to(self.device)
            self.bert_model.eval()
            st.success("✅ BERT chargé avec succès")
        except Exception as e:
            st.error(f"❌ Erreur chargement BERT: {e}")
            self.bert_model = None

        # DistilBERT
        try:
            self.distilbert_tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
            self.distilbert_model = DistilBertModel.from_pretrained('distilbert-base-uncased').to(self.device)
            self.distilbert_model.eval()
            st.success("✅ DistilBERT chargé avec succès")
        except Exception as e:
            st.error(f"❌ Erreur chargement DistilBERT: {e}")
            self.distilbert_model = None

    def _load_skill_patterns(self):
        """Patterns de compétences pour extraction intelligente"""
        self.skill_patterns = {
            'programming': ['python', 'sql', 'r', 'java', 'scala', 'c++', 'javascript', 'typescript', 'go', 'rust'],
            'ml_frameworks': ['tensorflow', 'pytorch', 'scikit-learn', 'keras', 'mxnet', 'huggingface', 'transformers'],
            'big_data': ['spark', 'hadoop', 'kafka', 'hive', 'airflow', 'databricks', 'flink', 'beam'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible'],
            'bi_tools': ['tableau', 'power bi', 'looker', 'superset', 'qlik', 'metabase'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'dynamodb', 'snowflake'],
            'ml_concepts': ['machine learning', 'deep learning', 'nlp', 'computer vision', 'ai',
                            'reinforcement learning'],
            'stats': ['statistics', 'regression', 'classification', 'clustering', 'hypothesis testing', 'bayesian'],
            'tools': ['git', 'jenkins', 'linux', 'excel', 'jupyter', 'vscode', 'pycharm']
        }

    def get_embeddings_bert(self, texts: List[str], batch_size: int = 8) -> np.ndarray:
        """Génère des embeddings avec BERT"""
        if not self.bert_model:
            raise ValueError("BERT model not loaded")

        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]

            # Tokenization
            inputs = self.bert_tokenizer(
                batch_texts,
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=256  # Réduit pour éviter les problèmes de mémoire
            ).to(self.device)

            # Génération des embeddings
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
                # Utiliser le token [CLS] pour l'embedding de la phrase
                batch_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                embeddings.append(batch_embeddings)

        return np.vstack(embeddings)

    def get_embeddings_distilbert(self, texts: List[str], batch_size: int = 16) -> np.ndarray:
        """Génère des embeddings avec DistilBERT"""
        if not self.distilbert_model:
            raise ValueError("DistilBERT model not loaded")

        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]

            # Tokenization
            inputs = self.distilbert_tokenizer(
                batch_texts,
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=256  # Réduit pour éviter les problèmes de mémoire
            ).to(self.device)

            # Génération des embeddings
            with torch.no_grad():
                outputs = self.distilbert_model(**inputs)
                # Utiliser le token [CLS] pour l'embedding de la phrase
                batch_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                embeddings.append(batch_embeddings)

        return np.vstack(embeddings)

    def compare_embeddings_performance(self, texts: List[str]) -> Dict:
        """Compare les performances de BERT vs DistilBERT"""
        results = {}

        # Test BERT
        if self.bert_model:
            start_time = time.time()
            try:
                bert_embeddings = self.get_embeddings_bert(texts[:50])  # Test sur 50 textes
                bert_time = time.time() - start_time
                bert_dim = bert_embeddings.shape[1]
                results['bert'] = {
                    'time': bert_time,
                    'dimension': bert_dim,
                    'embedding_shape': bert_embeddings.shape
                }
            except Exception as e:
                st.error(f"❌ Erreur avec BERT: {e}")

        # Test DistilBERT
        if self.distilbert_model:
            start_time = time.time()
            try:
                distilbert_embeddings = self.get_embeddings_distilbert(texts[:50])
                distilbert_time = time.time() - start_time
                distilbert_dim = distilbert_embeddings.shape[1]
                results['distilbert'] = {
                    'time': distilbert_time,
                    'dimension': distilbert_dim,
                    'embedding_shape': distilbert_embeddings.shape
                }
            except Exception as e:
                st.error(f"❌ Erreur avec DistilBERT: {e}")

        return results

    def cluster_job_titles(self, df, model_type='bert', n_clusters=6):
        """Clustering des postes utilisant les embeddings"""
        # Préparer les textes
        job_texts = []
        valid_indices = []

        for idx, row in df.iterrows():
            if pd.notna(row.get('job_title')) and str(row['job_title']).strip():
                text = f"{row.get('job_title', '')}"
                job_texts.append(self.preprocess_text(text))
                valid_indices.append(idx)

        if not job_texts:
            return df, None, None

        try:
            # Générer les embeddings
            if model_type == 'bert' and self.bert_model:
                embeddings = self.get_embeddings_bert(job_texts)
            elif model_type == 'distilbert' and self.distilbert_model:
                embeddings = self.get_embeddings_distilbert(job_texts)
            else:
                st.error("Modèle non disponible")
                return df, None, None

            # Clustering
            kmeans = KMeans(n_clusters=min(n_clusters, len(job_texts)), random_state=42, n_init=10)
            clusters = kmeans.fit_predict(embeddings)

            # Ajouter les clusters au DataFrame
            df_result = df.copy()
            df_result['embedding_cluster'] = np.nan
            for i, idx in enumerate(valid_indices):
                df_result.at[idx, 'embedding_cluster'] = clusters[i]

            return df_result, embeddings, clusters

        except Exception as e:
            st.error(f"❌ Erreur lors du clustering: {e}")
            return df, None, None

    def extract_entities_advanced(self, text: str) -> Dict:
        """Extraction avancée d'entités nommées avec NER"""
        if not text or pd.isna(text):
            return {}

        entities = {
            'skills': [],
            'technologies': [],
            'companies': [],
            'locations': [],
            'other': []
        }

        # Extraction basée sur les patterns
        entities['skills'] = self.extract_skills_from_text(text)

        # Extraction NER si disponible
        if self.ner_pipeline:
            try:
                ner_results = self.ner_pipeline(text[:512])  # Limiter la longueur

                for entity in ner_results:
                    entity_text = entity['word'].strip()
                    entity_type = entity['entity_group']

                    if entity_type in ['ORG'] and self._is_company(entity_text):
                        entities['companies'].append(entity_text)
                    elif entity_type in ['LOC', 'GPE']:
                        entities['locations'].append(entity_text)
                    elif entity_type in ['MISC'] and self._is_technology(entity_text):
                        entities['technologies'].append(entity_text)
                    else:
                        entities['other'].append(f"{entity_text} ({entity_type})")

            except Exception as e:
                print(f"Erreur NER: {e}")

        # Nettoyer les doublons
        for key in entities:
            entities[key] = list(set(entities[key]))

        return entities

    def _is_company(self, text: str) -> bool:
        """Détermine si le texte ressemble à un nom d'entreprise"""
        company_indicators = ['inc', 'corp', 'ltd', 'company', 'tech', 'technologies', 'group']
        return any(indicator in text.lower() for indicator in company_indicators)

    def _is_technology(self, text: str) -> bool:
        """Détermine si le texte ressemble à une technologie"""
        tech_indicators = self.skill_patterns['programming'] + \
                          self.skill_patterns['ml_frameworks'] + \
                          self.skill_patterns['databases']
        return any(tech in text.lower() for tech in tech_indicators)

    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extraction des compétences depuis le texte"""
        if not text:
            return []

        text_lower = text.lower()
        found_skills = []

        # Recherche dans les patterns
        for category, skills in self.skill_patterns.items():
            for skill in skills:
                if self._exact_match(skill, text_lower):
                    found_skills.append(skill)

        return list(set(found_skills))

    def _exact_match(self, skill: str, text: str) -> bool:
        """Recherche exacte d'un skill dans le texte"""
        pattern = r'\b' + re.escape(skill) + r'\b'
        return re.search(pattern, text) is not None

    def preprocess_text(self, text: str) -> str:
        """Prétraitement du texte"""
        if pd.isna(text):
            return ""

        # Conversion en minuscules
        text = str(text).lower()

        # Suppression des URLs
        text = re.sub(r'http\S+', '', text)

        # Suppression des caractères spéciaux (conserve les lettres et quelques symboles)
        text = re.sub(r'[^a-zA-Z\s\.\,\!]', '', text)

        # Suppression des espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def benchmark_models(self, df, sample_size=200):
        """Benchmark complet des modèles BERT vs DistilBERT"""
        st.header("📊 Benchmark BERT vs DistilBERT")

        # Préparer les données
        sample_texts = []
        for _, row in df.head(sample_size).iterrows():
            text = f"{row.get('job_title', '')}"
            processed_text = self.preprocess_text(text)
            if processed_text:
                sample_texts.append(processed_text)

        if not sample_texts:
            st.error("Aucun texte valide pour le benchmark")
            return

        results = self.compare_embeddings_performance(sample_texts)

        # Affichage des résultats
        if 'bert' in results:
            bert = results['bert']
            col1, col2 = st.columns(2)

            with col1:
                st.metric("⏱️ Temps BERT", f"{bert['time']:.2f}s")
                st.metric("📐 Dimension BERT", f"{bert['dimension']}D")

            with col2:
                if 'distilbert' in results:
                    distilbert = results['distilbert']
                    st.metric("⏱️ Temps DistilBERT", f"{distilbert['time']:.2f}s")
                    st.metric("📐 Dimension DistilBERT", f"{distilbert['dimension']}D")

            # Recommandation
            if 'distilbert' in results:
                speed_ratio = results['bert']['time'] / results['distilbert']['time']
                st.info(f"🎯 **Recommandation**: DistilBERT est {speed_ratio:.1f}x plus rapide que BERT")

                if speed_ratio > 1.5:
                    st.success("**✅ DistilBERT recommandé** - Meilleur compromis vitesse/performance")
                else:
                    st.warning("**⚠️ BERT peut être préférable** - Différence de vitesse modérée")
        else:
            st.error("Aucun modèle n'a pu être benchmarké")

    def visualize_embeddings_comparison(self, df, n_clusters=4):
        """Visualisation comparative des embeddings BERT / DistilBERT"""
        # Préparer les textes
        job_texts = []
        for _, row in df.head(100).iterrows():  # Limiter pour la visualisation
            text = f"{row.get('job_title', '')}"
            processed_text = self.preprocess_text(text)
            if processed_text:
                job_texts.append(processed_text)

        if not job_texts:
            return []

        # Créer les visualisations
        figs = []

        # BERT
        if self.bert_model:
            try:
                bert_embeddings = self.get_embeddings_bert(job_texts)
                fig_bert = self._create_embedding_plot(bert_embeddings, "BERT Embeddings", n_clusters)
                figs.append(('BERT', fig_bert))
            except Exception as e:
                st.error(f"❌ Erreur BERT: {e}")

        # DistilBERT
        if self.distilbert_model:
            try:
                distilbert_embeddings = self.get_embeddings_distilbert(job_texts)
                fig_distilbert = self._create_embedding_plot(distilbert_embeddings, "DistilBERT Embeddings", n_clusters)
                figs.append(('DistilBERT', fig_distilbert))
            except Exception as e:
                st.error(f"❌ Erreur DistilBERT: {e}")

        return figs

    def _create_embedding_plot(self, embeddings, title, n_clusters):
        """Crée un plot d'embeddings"""
        try:
            # Réduction de dimension
            tsne = TSNE(n_components=2, random_state=42, perplexity=min(15, len(embeddings) - 1))
            embeddings_2d = tsne.fit_transform(embeddings)

            # Clustering pour la couleur
            kmeans = KMeans(n_clusters=min(n_clusters, len(embeddings)), random_state=42, n_init=10)
            clusters = kmeans.fit_predict(embeddings)

            # Création du plot
            fig = px.scatter(
                x=embeddings_2d[:, 0],
                y=embeddings_2d[:, 1],
                color=clusters.astype(str),
                title=f"🎯 {title} - Clustering",
                labels={'color': 'Cluster'}
            )

            fig.update_traces(
                marker=dict(size=8, line=dict(width=1, color='DarkSlateGrey')),
                selector=dict(mode='markers')
            )

            return fig
        except Exception as e:
            print(f"Erreur création plot: {e}")
            return None

    def analyze_skill_evolution(self, df):
        """Analyse l'évolution des compétences"""
        all_entities = []

        for idx, row in df.iterrows():
            text = f"{row.get('job_title', '')} {row.get('job_description', '')}"
            entities = self.extract_entities_advanced(text)

            entity_record = {
                'index': idx,
                'skills_count': len(entities['skills']),
                'technologies_count': len(entities['technologies']),
                'all_skills': entities['skills'] + entities['technologies']
            }

            all_entities.append(entity_record)

        entities_df = pd.DataFrame(all_entities)

        # Analyse des tendances
        all_skills = [skill for sublist in entities_df['all_skills'] for skill in sublist]
        skill_trends = Counter(all_skills)

        return {
            'entities_df': entities_df,
            'skill_trends': skill_trends,
            'avg_skills_per_job': entities_df['skills_count'].mean(),
            'avg_tech_per_job': entities_df['technologies_count'].mean()
        }


# Fonction utilitaire pour l'analyse comparative
def compare_clustering_quality(embeddings_bert, embeddings_distilbert):
    """Compare la qualité du clustering entre BERT et DistilBERT"""
    results = {}

    # Pour BERT
    if embeddings_bert is not None and len(embeddings_bert) > 1:
        try:
            kmeans_bert = KMeans(n_clusters=min(8, len(embeddings_bert)), random_state=42, n_init=10)
            clusters_bert = kmeans_bert.fit_predict(embeddings_bert)
            silhouette_bert = silhouette_score(embeddings_bert, clusters_bert)
            results['bert'] = {
                'silhouette_score': silhouette_bert,
                'n_clusters': len(np.unique(clusters_bert))
            }
        except Exception as e:
            print(f"Erreur clustering BERT: {e}")

    # Pour DistilBERT
    if embeddings_distilbert is not None and len(embeddings_distilbert) > 1:
        try:
            kmeans_distilbert = KMeans(n_clusters=min(8, len(embeddings_distilbert)), random_state=42, n_init=10)
            clusters_distilbert = kmeans_distilbert.fit_predict(embeddings_distilbert)
            silhouette_distilbert = silhouette_score(embeddings_distilbert, clusters_distilbert)
            results['distilbert'] = {
                'silhouette_score': silhouette_distilbert,
                'n_clusters': len(np.unique(clusters_distilbert))
            }
        except Exception as e:
            print(f"Erreur clustering DistilBERT: {e}")

    return results