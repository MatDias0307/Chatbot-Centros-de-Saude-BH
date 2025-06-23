import pandas as pd
import re
from functools import lru_cache
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def load_and_preprocess_data(filepath: str) -> pd.DataFrame:
    """Carrega e pré-processa os dados dos centros de saúde com cache."""
    relevant_columns = [
        'NOME_CENTRO_SAUDE',
        'TIPO_LOGRADOURO_CS',
        'NOME_LOGRADOURO_CS',
        'NUMERO_IMOVEL_CS',
        'NOME_BAIRRO_POPULAR_CS',
        'TELEFONE_CENTRO_SAUDE',
        'DISTRITO_SANITARIO'
    ]
    
    try:
        logger.info(f"Carregando dados de {filepath}")
        try:
            df = pd.read_csv(filepath, sep=';', encoding='utf-8', usecols=relevant_columns)
        except:
            df = pd.read_csv(filepath, sep=',', encoding='latin1', usecols=relevant_columns)
        
        df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
        
        df['TELEFONE_CENTRO_SAUDE'] = df['TELEFONE_CENTRO_SAUDE'].apply(_normalize_phone)
        
        df['ENDERECO_COMPLETO'] = df.apply(_create_full_address, axis=1)
        
        df = df.drop_duplicates(subset=['NOME_CENTRO_SAUDE'])
        df = df.dropna(subset=['NOME_CENTRO_SAUDE', 'ENDERECO_COMPLETO'])
        
        logger.info(f"Dados carregados com {len(df)} registros válidos")
        
        required_columns = ['NOME_CENTRO_SAUDE', 'ENDERECO_COMPLETO', 'NOME_BAIRRO_POPULAR_CS']
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Coluna obrigatória '{col}' não encontrada nos dados")
                raise ValueError(f"Coluna '{col}' ausente no dataset")
            
        return df
    
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {str(e)}")
        raise

def _normalize_phone(phone: str) -> str:
    """
    Normaliza números de telefone no formato:
    - Entrada: "32777487,32777488,32771301" ou "32460235"
    - Saída: "(31) 3277-7487 / (31) 3277-7488 / (31) 3277-1301"
    """
    if pd.isna(phone) or not phone:
        return ""
    
    phones_cleaned = re.sub(r'[^\d,]', '', str(phone))
    
    formatted_phones = []
    for phone_num in phones_cleaned.split(','):
        phone_num = phone_num.strip()
        if not phone_num:
            continue
            
        if len(phone_num) == 8:
            formatted = f"(31) {phone_num[:4]}-{phone_num[4:]}"
        elif len(phone_num) == 10:
            formatted = f"({phone_num[:2]}) {phone_num[2:6]}-{phone_num[6:]}"
        elif len(phone_num) == 11:
            formatted = f"({phone_num[:2]}) {phone_num[2:7]}-{phone_num[7:]}"
        else:
            formatted = phone_num  
            
        formatted_phones.append(formatted)
    
    return " / ".join(formatted_phones) if formatted_phones else ""

def format_address(logradouro: str, nome_rua: str, numero: str, bairro: str) -> str:
    """Formata endereço de forma mais natural"""
    logradouro = {
        'AVE': 'Avenida',
        'R': 'Rua',
        'TV': 'Travessa',
        'PCA': 'Praça',
        'AL': 'Alameda',
        'ROD': 'Rodovia'
    }.get(logradouro, logradouro)
    
    nome_rua = nome_rua.title() if pd.notnull(nome_rua) else ''
    bairro = bairro.title() if pd.notnull(bairro) else ''
    
    numero = str(numero) if pd.notnull(numero) else 's/n'
    return f"{logradouro} {nome_rua}, {numero} - {bairro}"

def _create_full_address(row: Dict[str, Any]) -> str:
    """Mantém para compatibilidade, mas usa a formatação nova"""
    return format_address(
        row['TIPO_LOGRADOURO_CS'],
        row['NOME_LOGRADOURO_CS'],
        row['NUMERO_IMOVEL_CS'],
        row['NOME_BAIRRO_POPULAR_CS']
    )