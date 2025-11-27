import pandas as pd
import re
from collections import Counter


class QASystem:
    def __init__(self):
        self.knowledge_base = None
        self._precomputed_answers = {}
        self._initialized = False

    def build_knowledge_base(self, df):
        """Construit la base de connaissances intelligente"""
        try:
            print("🔄 Initialisation du QASystem...")
            self.knowledge_base = df
            self._precompute_common_answers()
            self._initialized = True
            print("✅ QASystem initialisé avec succès")
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation du QASystem: {e}")
            self._initialized = False

    def _precompute_common_answers(self):
        """Pré-calcul des réponses fréquentes avec gestion d'erreur robuste"""
        try:
            print("📊 Pré-calcul des réponses fréquentes...")

            # Initialiser toutes les clés avec des valeurs par défaut
            self._precomputed_answers = {
                'top_skills': pd.Series(dtype=object),
                'top_companies': pd.Series(dtype=object),
                'salaries': pd.Series(dtype=float),
                'top_jobs': pd.Series(dtype=object)
            }

            # Vérifier que knowledge_base n'est pas vide
            if self.knowledge_base is None or self.knowledge_base.empty:
                print("⚠️ Base de connaissances vide")
                return

            # 1. Top compétences
            if 'skills_list' in self.knowledge_base.columns:
                try:
                    # Aplatir toutes les listes de compétences
                    all_skills = []
                    for skills in self.knowledge_base['skills_list']:
                        if isinstance(skills, list):
                            all_skills.extend(skills)

                    if all_skills:
                        skill_series = pd.Series(all_skills)
                        skill_counts = skill_series.value_counts()
                        self._precomputed_answers['top_skills'] = skill_counts.head(20)
                        print(f"✅ Top skills calculé: {len(skill_counts)} compétences uniques")
                    else:
                        print("⚠️ Aucune compétence trouvée dans skills_list")
                except Exception as e:
                    print(f"❌ Erreur calcul top_skills: {e}")

            # 2. Top entreprises
            if 'company_name' in self.knowledge_base.columns:
                try:
                    company_counts = self.knowledge_base['company_name'].value_counts()
                    if not company_counts.empty:
                        self._precomputed_answers['top_companies'] = company_counts.head(15)
                        print(f"✅ Top companies calculé: {len(company_counts)} entreprises")
                except Exception as e:
                    print(f"❌ Erreur calcul top_companies: {e}")

            # 3. Salaires moyens
            if 'salary_year_avg' in self.knowledge_base.columns and 'job_title_short' in self.knowledge_base.columns:
                try:
                    salary_data = self.knowledge_base.dropna(subset=['salary_year_avg'])
                    if not salary_data.empty:
                        salaries = salary_data.groupby('job_title_short')['salary_year_avg'].mean()
                        self._precomputed_answers['salaries'] = salaries
                        print(f"✅ Salaires calculés: {len(salaries)} postes avec salaires")
                except Exception as e:
                    print(f"❌ Erreur calcul salaries: {e}")

            # 4. Top postes
            if 'job_title_short' in self.knowledge_base.columns:
                try:
                    job_counts = self.knowledge_base['job_title_short'].value_counts()
                    if not job_counts.empty:
                        self._precomputed_answers['top_jobs'] = job_counts.head(15)
                        print(f"✅ Top jobs calculé: {len(job_counts)} postes uniques")
                except Exception as e:
                    print(f"❌ Erreur calcul top_jobs: {e}")

            print("✅ Pré-calcul terminé avec succès")

        except Exception as e:
            print(f"❌ Erreur critique dans _precompute_common_answers: {e}")
            # Assurer que _precomputed_answers a toujours les clés de base
            self._precomputed_answers = {
                'top_skills': pd.Series(dtype=object),
                'top_companies': pd.Series(dtype=object),
                'salaries': pd.Series(dtype=float),
                'top_jobs': pd.Series(dtype=object)
            }

    def answer_question(self, question):
        """Système intelligent de questions-réponses"""
        try:
            # Vérifier que le système est initialisé
            if not self._initialized or self.knowledge_base is None:
                return "❌ Le système n'est pas encore initialisé. Veuillez patienter."

            question_lower = question.lower()

            # Détection intelligente du type de question
            if any(word in question_lower for word in
                   ['compétence', 'skill', 'technologie', 'maîtriser', 'connaissance', 'competance', 'competence']):
                return self._answer_skills_question(question)
            elif any(word in question_lower for word in ['entreprise', 'company', 'société', 'boîte']):
                return self._answer_companies_question(question)
            elif any(word in question_lower for word in ['salaire', 'salary', 'rémunération', 'paie']):
                return self._answer_salary_question(question)
            elif any(word in question_lower for word in
                     ['poste', 'job', 'emploi', 'métier', 'data engineer', 'data scientist']):
                return self._answer_jobs_question(question)
            elif any(word in question_lower for word in ['combien', 'nombre', 'statistique', 'total']):
                return self._answer_stats_question(question)
            else:
                return self._answer_general_question(question)
        except Exception as e:
            print(f"❌ Erreur dans answer_question: {e}")
            return f"❌ Une erreur s'est produite lors du traitement de votre question: {str(e)}"

    def _answer_skills_question(self, question):
        """Répond aux questions sur les compétences"""
        try:
            skills_in_question = self._extract_skills_from_text(question)

            # Si la question contient "data engineer", on cherche les compétences spécifiques
            if "data engineer" in question.lower():
                return self._answer_data_engineer_skills()

            if skills_in_question:
                # Trouver les entreprises qui recherchent ces compétences
                companies = []
                job_counts = {}

                for skill in skills_in_question:
                    # Compter le nombre d'offres pour cette compétence
                    count = 0
                    company_list = []

                    for idx, row in self.knowledge_base.iterrows():
                        if isinstance(row.get('skills_list', []), list) and skill in row['skills_list']:
                            count += 1
                            if 'company_name' in row and pd.notna(row['company_name']):
                                company_list.append(row['company_name'])

                    job_counts[skill] = count
                    companies.extend(company_list)

                response = f"**🔍 Analyse des compétences {', '.join(skills_in_question)}:**\n\n"

                # Demandes par compétence
                for skill, count in job_counts.items():
                    response += f"• **{skill}** : {count:,} offres\n"

                response += "\n**🏢 Top entreprises recherchant ces compétences:**\n"
                if companies:
                    company_counts = pd.Series(companies).value_counts().head(5)
                    for company, count in company_counts.items():
                        response += f"• {company} ({count:,} offres)\n"
                else:
                    response += "Aucune entreprise spécifique identifiée.\n"

                # Recommandations de compétences associées
                related_skills = self._find_related_skills(skills_in_question)
                if related_skills:
                    response += f"\n**💡 Compétences souvent associées:**\n"
                    for skill in related_skills[:3]:
                        response += f"• {skill}\n"

            else:
                # Si pas de compétences spécifiques, montrer le top général
                top_skills = self._precomputed_answers.get('top_skills', pd.Series(dtype=object))
                if not top_skills.empty:
                    response = "**🛠️ Top 15 des compétences les plus demandées:**\n\n"
                    for skill, count in top_skills.head(15).items():
                        response += f"• {skill} ({count:,} offres)\n"
                else:
                    # Fallback: calcul en direct
                    all_skills = []
                    for skills in self.knowledge_base['skills_list']:
                        if isinstance(skills, list):
                            all_skills.extend(skills)

                    if all_skills:
                        skill_counts = pd.Series(all_skills).value_counts().head(15)
                        response = "**🛠️ Top 15 des compétences les plus demandées:**\n\n"
                        for skill, count in skill_counts.items():
                            response += f"• {skill} ({count:,} offres)\n"
                    else:
                        response = "❌ Aucune donnée de compétences disponible."

            return response
        except Exception as e:
            print(f"❌ Erreur dans _answer_skills_question: {e}")
            return "❌ Erreur lors de l'analyse des compétences."

    def _answer_data_engineer_skills(self):
        """Répond spécifiquement aux questions sur les compétences des Data Engineers"""
        try:
            # Filtrer les offres de Data Engineer
            data_engineer_jobs = self.knowledge_base[
                self.knowledge_base['job_title_short'].str.contains('data engineer', case=False, na=False)
                | self.knowledge_base['job_title'].str.contains('data engineer', case=False, na=False)
                ]

            if data_engineer_jobs.empty:
                return "❌ Aucune offre de Data Engineer trouvée."

            # Compétences des Data Engineers
            de_skills = []
            for skills in data_engineer_jobs['skills_list']:
                if isinstance(skills, list):
                    de_skills.extend(skills)

            if not de_skills:
                return "❌ Aucune compétence trouvée pour les Data Engineers."

            skill_counts = pd.Series(de_skills).value_counts().head(15)

            response = "**👨‍💻 Compétences les plus demandées pour les Data Engineers:**\n\n"
            for skill, count in skill_counts.items():
                response += f"• {skill} ({count:,} offres)\n"

            # Ajouter des statistiques
            response += f"\n**📊 Statistiques Data Engineer:**\n"
            response += f"• {len(data_engineer_jobs):,} offres analysées\n"

            # Top entreprises qui recrutent des Data Engineers
            top_companies = data_engineer_jobs['company_name'].value_counts().head(5)
            if not top_companies.empty:
                response += f"\n**🏢 Top entreprises recrutant des Data Engineers:**\n"
                for company, count in top_companies.items():
                    response += f"• {company} ({count:,} offres)\n"

            return response
        except Exception as e:
            print(f"❌ Erreur dans _answer_data_engineer_skills: {e}")
            return "❌ Erreur lors de l'analyse des compétences Data Engineer."

    def _answer_companies_question(self, question):
        """Répond aux questions sur les entreprises"""
        try:
            skills_in_question = self._extract_skills_from_text(question)

            # Si on a détecté des compétences non pertinentes (comme 'r' seul), on les filtre
            filtered_skills = [skill for skill in skills_in_question if len(skill) > 1]

            if filtered_skills:
                response = f"**🏢 Entreprises recherchant {', '.join(filtered_skills)}:**\n\n"

                # Pour chaque compétence, trouver les entreprises
                for skill in filtered_skills:
                    companies_for_skill = []
                    for idx, row in self.knowledge_base.iterrows():
                        if isinstance(row.get('skills_list', []), list) and skill in row['skills_list']:
                            if 'company_name' in row and pd.notna(row['company_name']):
                                companies_for_skill.append(row['company_name'])

                    if companies_for_skill:
                        company_counts = pd.Series(companies_for_skill).value_counts().head(3)
                        response += f"**Compétence: {skill}**\n"
                        for company, count in company_counts.items():
                            response += f"• {company} ({count:,} offres)\n"
                        response += "\n"
                    else:
                        response += f"**Compétence: {skill}** - Aucune entreprise trouvée.\n\n"

            else:
                # Top entreprises général (question sans compétences spécifiques)
                top_companies = self._precomputed_answers.get('top_companies', pd.Series(dtype=object))
                if not top_companies.empty:
                    response = "**🏢 Top 10 des entreprises qui recrutent le plus:**\n\n"
                    for company, count in top_companies.head(10).items():
                        response += f"• {company} ({count:,} offres)\n"

                    # Ajouter quelques statistiques
                    total_companies = self.knowledge_base['company_name'].nunique()
                    response += f"\n*Basé sur l'analyse de {total_companies:,} entreprises différentes*"
                else:
                    # Fallback manuel
                    if 'company_name' in self.knowledge_base.columns:
                        company_counts = self.knowledge_base['company_name'].value_counts().head(10)
                        response = "**🏢 Top 10 des entreprises qui recrutent:**\n\n"
                        for company, count in company_counts.items():
                            response += f"• {company} ({count:,} offres)\n"
                    else:
                        response = "❌ Données entreprises non disponibles."

            return response
        except Exception as e:
            print(f"❌ Erreur dans _answer_companies_question: {e}")
            return "❌ Erreur lors de l'analyse des entreprises."

    def _answer_salary_question(self, question):
        """Répond aux questions sur les salaires"""
        try:
            # Vérifier si les données de salaire existent
            if 'salary_year_avg' not in self.knowledge_base.columns:
                return "❌ Aucune donnée de salaire disponible dans le dataset."

            # Extraire le poste de la question si mentionné
            job_titles = ['data scientist', 'data engineer', 'data analyst', 'machine learning', 'analyste']
            target_job = None

            for job in job_titles:
                if job in question.lower():
                    target_job = job
                    break

            if target_job:
                # Salaire pour un poste spécifique
                salary_data = self.knowledge_base.dropna(subset=['salary_year_avg'])
                if 'job_title_short' in salary_data.columns:
                    job_salaries = salary_data[
                        salary_data['job_title_short'].str.contains(target_job, case=False, na=False)]

                    if not job_salaries.empty:
                        avg_salary = job_salaries['salary_year_avg'].mean()
                        count = len(job_salaries)
                        response = f"**💰 Salaire pour les postes de {target_job.title()}:**\n\n"
                        response += f"• Salaire annuel moyen: **${avg_salary:,.0f}**\n"
                        response += f"• Basé sur {count:,} offres\n"
                    else:
                        response = f"❌ Aucune donnée de salaire trouvée pour {target_job}"
                else:
                    response = "❌ Colonne 'job_title_short' manquante pour l'analyse des salaires."
            else:
                # Salaires moyens par type de poste
                salaries = self._precomputed_answers.get('salaries', pd.Series(dtype=float))
                if not salaries.empty:
                    response = "**💰 Salaires annuels moyens par type de poste:**\n\n"
                    valid_salaries = 0
                    for job, salary in salaries.head(8).items():
                        if not pd.isna(salary):
                            response += f"• {job}: ${salary:,.0f}\n"
                            valid_salaries += 1

                    if valid_salaries == 0:
                        response = "❌ Aucune donnée de salaire valide disponible."
                else:
                    response = "❌ Aucune donnée de salaire disponible."

            return response
        except Exception as e:
            print(f"❌ Erreur dans _answer_salary_question: {e}")
            return "❌ Erreur lors de l'analyse des salaires."

    def _answer_jobs_question(self, question):
        """Répond aux questions sur les postes"""
        try:
            skills_in_question = self._extract_skills_from_text(question)

            if skills_in_question:
                response = f"**🎯 Postes recherchant {', '.join(skills_in_question)}:**\n\n"

                for skill in skills_in_question:
                    jobs_for_skill = []
                    for idx, row in self.knowledge_base.iterrows():
                        if isinstance(row.get('skills_list', []), list) and skill in row['skills_list']:
                            if 'job_title_short' in row and pd.notna(row['job_title_short']):
                                jobs_for_skill.append(row['job_title_short'])

                    if jobs_for_skill:
                        job_counts = pd.Series(jobs_for_skill).value_counts().head(3)
                        response += f"**Avec {skill}:**\n"
                        for job, count in job_counts.items():
                            response += f"• {job} ({count:,} offres)\n"
                        response += "\n"
                    else:
                        response += f"**Avec {skill}:** Aucun poste trouvé.\n\n"
            else:
                # Top postes général
                top_jobs = self._precomputed_answers.get('top_jobs', pd.Series(dtype=object))
                if not top_jobs.empty:
                    response = "**🎯 Top 10 des postes les plus demandés:**\n\n"
                    for job, count in top_jobs.head(10).items():
                        response += f"• {job} ({count:,} offres)\n"
                else:
                    # Fallback
                    job_counts = self.knowledge_base['job_title_short'].value_counts().head(10)
                    response = "**🎯 Top 10 des postes les plus demandés:**\n\n"
                    for job, count in job_counts.items():
                        response += f"• {job} ({count:,} offres)\n"

            return response
        except Exception as e:
            print(f"❌ Erreur dans _answer_jobs_question: {e}")
            return "❌ Erreur lors de l'analyse des postes."

    def _answer_stats_question(self, question):
        """Répond aux questions statistiques"""
        try:
            total_jobs = len(self.knowledge_base)
            unique_companies = self.knowledge_base[
                'company_name'].nunique() if 'company_name' in self.knowledge_base.columns else 0

            # Compétences uniques
            unique_skills = 0
            if 'skills_list' in self.knowledge_base.columns:
                all_skills = set()
                for skills in self.knowledge_base['skills_list']:
                    if isinstance(skills, list):
                        all_skills.update(skills)
                unique_skills = len(all_skills)

            # Gestion du salaire moyen
            avg_salary = "N/A"
            if 'salary_year_avg' in self.knowledge_base.columns:
                salary_mean = self.knowledge_base['salary_year_avg'].mean()
                if not pd.isna(salary_mean):
                    avg_salary = f"${salary_mean:,.0f}"

            response = f"""
**📊 Statistiques du marché de l'emploi Data:**

• 📋 **{total_jobs:,}** offres d'emploi analysées
• 🏢 **{unique_companies:,}** entreprises différentes
• 🛠️ **{unique_skills:,}** compétences recensées
• 💰 Salaire moyen: **{avg_salary}**

**🎯 Top postes:**
"""

            # Ajouter les top catégories
            if 'job_title_short' in self.knowledge_base.columns:
                top_jobs = self.knowledge_base['job_title_short'].value_counts().head(3)
                for job, count in top_jobs.items():
                    percentage = (count / total_jobs) * 100
                    response += f"• {job}: {count:,} offres ({percentage:.1f}%)\n"
            else:
                response += "• Données de postes non disponibles\n"

            return response
        except Exception as e:
            print(f"❌ Erreur dans _answer_stats_question: {e}")
            return "❌ Erreur lors du calcul des statistiques."

    def _answer_general_question(self, question):
        """Réponse générale et aide"""
        return """
**🤖 Assistant Intelligent - Aide**

Je peux vous aider à analyser le marché de l'emploi Data. Voici ce que je sais faire:

**🔍 Questions sur les compétences:**
• "Quelles sont les compétences les plus demandées ?"
• "Qui recherche Python et Machine Learning ?"
• "Quelles compétences sont associées à SQL ?"
• "Compétences des Data Engineers ?"

**🏢 Questions sur les entreprises:**
• "Quelles entreprises recrutent le plus ?"
• "Qui recherche des compétences en AWS ?"

**💰 Questions sur les salaires:**
• "Quels sont les salaires moyens ?"
• "Salaire pour les Data Scientists ?"

**🎯 Questions sur les postes:**
• "Quels sont les postes les plus courants ?"
• "Quels postes nécessitent TensorFlow ?"

**📊 Questions statistiques:**
• "Combien d'offres au total ?"
• "Statistiques du marché"

N'hésitez pas à me poser une question spécifique !
"""

    def _extract_skills_from_text(self, text):
        """Extraction intelligente des compétences d'un texte avec gestion des faux positifs"""
        if not text or pd.isna(text):
            return []

        skill_categories = {
            'langages': ['python', 'sql', 'java', 'scala', 'c++', 'javascript', 'typescript'],
            'ml_frameworks': ['tensorflow', 'pytorch', 'scikit-learn', 'keras', 'mxnet'],
            'big_data': ['spark', 'hadoop', 'kafka', 'hive', 'airflow', 'databricks'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
            'bi_tools': ['tableau', 'power bi', 'looker', 'superset', 'qlik'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'cassandra'],
            'concepts': ['machine learning', 'deep learning', 'nlp', 'computer vision', 'ai']
        }

        found_skills = []
        text_lower = text.lower()

        # Mots à ignorer pour éviter les faux positifs
        ignore_words = ['le', 'la', 'les', 'de', 'des', 'du', 'et', 'ou', 'avec', 'sans', 'pour', 'par', 'dans', 'sur',
                        'r']

        for category, skills in skill_categories.items():
            for skill in skills:
                # Vérifier que la compétence n'est pas dans la liste d'ignore
                if skill in ignore_words:
                    continue

                # Recherche contextuelle pour éviter les faux positifs
                patterns = [
                    f' {skill} ',
                    f' {skill},',
                    f',{skill} ',
                    f' {skill}.',
                    f'{skill} ',
                    f' {skill}'
                ]

                if any(pattern in text_lower for pattern in patterns):
                    found_skills.append(skill)

        return list(set(found_skills))

    def _find_related_skills(self, target_skills):
        """Trouve des compétences souvent associées"""
        related = []

        for skill in target_skills:
            # Trouver les offres avec cette compétence
            for idx, row in self.knowledge_base.iterrows():
                if isinstance(row.get('skills_list', []), list) and skill in row['skills_list']:
                    # Extraire les autres compétences de ces offres
                    for other_skill in row['skills_list']:
                        if other_skill not in target_skills and other_skill != skill:
                            related.append(other_skill)

        # Retourner les plus fréquentes
        return [skill for skill, count in Counter(related).most_common(5)]