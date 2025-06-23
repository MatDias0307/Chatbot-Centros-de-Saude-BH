import spacy
from spacy.matcher import PhraseMatcher
from typing import Dict, Optional, List
import re
from unidecode import unidecode
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
import pandas as pd
from .patterns import ABREVIACOES_LOGRADOURO, VARIANTES_SAUDE
from .utils import load_and_preprocess_data

logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self, data_path: str):
        self.nlp = spacy.load('pt_core_news_sm')
        self.data = load_and_preprocess_data(data_path)
        self._prepare_matchers()
        self._prepare_similarity_model()
        logger.info("NLPProcessor inicializado com sucesso")

    def _prepare_similarity_model(self):
        """Prepara modelo de similaridade textual para fallback de nomes de centros"""
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(
            self.data['NOME_CENTRO_SAUDE'].apply(self._normalize_text)
        )
        self.similarity_threshold = 0.6  

    def _prepare_matchers(self):
        """Prepara PhraseMatchers para centro, bairro e distrito"""
        self.center_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        center_names = [self._normalize_text(name) for name in self.data['NOME_CENTRO_SAUDE'].unique()]
        self.center_matcher.add('CENTRO_SAUDE', [self.nlp.make_doc(name) for name in center_names])

        self.district_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        districts = [self._normalize_text(district) for district in self.data['DISTRITO_SANITARIO'].unique()]
        self.district_matcher.add('DISTRITO_SANITARIO', [self.nlp.make_doc(district) for district in districts])

        self.neighborhood_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        neighborhoods = [self._normalize_text(bairro) for bairro in self.data['NOME_BAIRRO_POPULAR_CS'].unique()]
        self.neighborhood_matcher.add('BAIRRO', [self.nlp.make_doc(bairro) for bairro in neighborhoods])

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normaliza texto para matching e busca"""
        text = unidecode(text.lower().strip())

        abbreviations = {
            r'\bav\b': 'avenida',
            r'\br\b': 'rua',
            r'\bsta?\b': 'santa',
            r'\bsao\b': 'sao',
            r'\bubs\b': 'unidade basica de saude',
            r'\bcs\b': 'centro de saude'
        }
        for pattern, replacement in abbreviations.items():
            text = re.sub(pattern, replacement, text)

        for abbr, full in ABREVIACOES_LOGRADOURO.items():
            pattern = r'\b' + abbr.lower() + r'\b'
            text = re.sub(pattern, full.lower(), text)

        for variant in VARIANTES_SAUDE:
            variant_norm = unidecode(variant.lower())
            text = re.sub(r'\b' + re.escape(variant_norm) + r'\b', 'centro de saude', text)

        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def extract_entities(self, text: str) -> Dict:
        normalized_text = self._normalize_text(text)
        doc = self.nlp(normalized_text)

        bairro_keywords = [
            "bairro", "vila", "comunidade", "localidade", "setor", "núcleo",
            "quadra", "conjunto", "residencial", "loteamento", "parque",
            "jardim", "favela", "morro"
        ]

        distrito_keywords = [
            "região", "distrito", "área", "zona", "zona sanitária",
            "setor sanitário", "área de saúde", "regional", "território"
        ]

        has_bairro_keyword = any(token.text in bairro_keywords for token in doc)
        has_distrito_keyword = any(token.text in distrito_keywords for token in doc)

        entities = {
            'centro_saude': None,
            'distrito': None,
            'bairro': None
        }

        center_matches = self.center_matcher(doc)
        district_matches = self.district_matcher(doc)
        neighborhood_matches = self.neighborhood_matcher(doc)

        if center_matches:
            span = doc[center_matches[0][1]:center_matches[0][2]]
            entities['centro_saude'] = span.text

        if has_distrito_keyword:
            if district_matches:
                span = doc[district_matches[0][1]:district_matches[0][2]]
                entities['distrito'] = span.text

        elif has_bairro_keyword:
            if neighborhood_matches:
                span = doc[neighborhood_matches[0][1]:neighborhood_matches[0][2]]
                entities['bairro'] = span.text

        else:
            if district_matches:
                span = doc[district_matches[0][1]:district_matches[0][2]]
                entities['distrito'] = span.text
            elif neighborhood_matches:
                span = doc[neighborhood_matches[0][1]:neighborhood_matches[0][2]]
                entities['bairro'] = span.text

        return entities
    
    def _match_with_phrasematcher(self, doc, entities):
        """Faz o matching usando PhraseMatcher"""
        matchers = [
            (self.center_matcher, 'centro_saude'),
            (self.district_matcher, 'distrito'),
            (self.neighborhood_matcher, 'bairro')
        ]

        for matcher, entity_key in matchers:
            matches = matcher(doc)
            if matches:
                span = doc[matches[0][1]:matches[0][2]]
                entities[entity_key] = span.text

    def get_center_info(self, entities: Dict) -> Optional[List[Dict]]:
        """
        Realiza a busca de acordo com a entidade reconhecida:
        1. Nome de centro específico
        2. Bairro
        3. Distrito sanitário (região)

        Executa a busca na ordem de prioridade e NÃO mistura resultados.
        """
        df = self.data
        cs = entities.get('centro_saude')
        bairro = entities.get('bairro')
        distrito = entities.get('distrito')

        def buscar_por_coluna(coluna: str, termo: str, use_similarity: bool = False) -> Optional[pd.DataFrame]:
            if not termo:
                return None

            normalized_term = self._normalize_text(termo)
            filtro = df[coluna].apply(
                lambda x: self._normalize_text(str(x)) if pd.notnull(x) else ""
            ).str.contains(normalized_term, regex=False, na=False)

            resultados = df[filtro]

            if not resultados.empty:
                logger.debug(f"Centros encontrados por {coluna}: {termo}")
                return resultados

            if use_similarity and coluna == 'NOME_CENTRO_SAUDE':
                query_vec = self.vectorizer.transform([normalized_term])
                similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
                top_indices = np.where(similarities > self.similarity_threshold)[0]

                if len(top_indices) > 0:
                    return df.iloc[top_indices]

            return None

        if cs:
            resultado = buscar_por_coluna('NOME_CENTRO_SAUDE', cs, use_similarity=True)
            if resultado is not None and not resultado.empty:
                return resultado.to_dict('records')

        if bairro:
            resultado = buscar_por_coluna('NOME_BAIRRO_POPULAR_CS', bairro)
            if resultado is not None and not resultado.empty:
                return resultado.to_dict('records')

        if distrito:
            resultado = buscar_por_coluna('DISTRITO_SANITARIO', distrito)
            if resultado is not None and not resultado.empty:
                return resultado.to_dict('records')

        logger.debug(f"Nenhum centro encontrado para: {entities}")
        return None