import pandas as pd
import numpy as np


class DataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_and_clean_data(self):
        """Charge et nettoie les données de façon robuste"""
        try:
            # Chargement avec types optimisés
            df = pd.read_excel(self.file_path)

            # Vérifier que le DataFrame n'est pas vide
            if df.empty:
                print("❌ Le fichier est vide")
                return df

            # Nettoyage basique
            df = df.drop_duplicates()

            # Gestion des colonnes optionnelles
            if 'salary_year_avg' in df.columns:
                df['salary_year_avg'] = pd.to_numeric(df['salary_year_avg'], errors='coerce')

            if 'job_location' in df.columns:
                df['job_location'] = df['job_location'].fillna('Non spécifié')

            if 'company_name' in df.columns:
                df['company_name'] = df['company_name'].fillna('Inconnu')

            # Traitement des compétences - conversion en tuples pour éviter les problèmes de hachage
            if 'job_skills' in df.columns:
                df['skills_list'] = df['job_skills'].apply(
                    lambda x: tuple(skill.strip() for skill in str(x).split(','))
                    if pd.notna(x) and str(x).strip() else tuple()
                )
            else:
                df['skills_list'] = [tuple() for _ in range(len(df))]

            print(f"✅ Données chargées: {len(df):,} lignes")
            print(f"📊 Colonnes disponibles: {list(df.columns)}")

            return df

        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            return pd.DataFrame()