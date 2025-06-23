ABREVIACOES_LOGRADOURO = {
    'AVE': 'Avenida', 'AV': 'Avenida', 'AVEN': 'Avenida',
    'R': 'Rua', 'RUA': 'Rua', 'RU': 'Rua',
    'TV': 'Travessa', 'TRAV': 'Travessa',
    'PCA': 'Praça', 'PRACA': 'Praça',
    'AL': 'Alameda', 'ALAM': 'Alameda',
    'ROD': 'Rodovia', 'RODOV': 'Rodovia',
    'EST': 'Estrada', 'ESTR': 'Estrada',
    'LG': 'Largo', 'LGO': 'Largo',
    'QD': 'Quadra', 'QUAD': 'Quadra',
    'BL': 'Bloco', 'BLOCO': 'Bloco',
    'CJ': 'Conjunto', 'CONJ': 'Conjunto',
    'RES': 'Residencial', 'RESID': 'Residencial'
}

VARIANTES_SAUDE = [
    'posto','posto de saude', 'posto saúde', 'posto medico', 'posto médico',
    'unidade basica', 'unidade básica', 'ubs', 'unidade de saude', 
    'unidade saúde', 'centro', 'centro de saude', 'centro saúde', 'cs',
    'clinica basica', 'clínica básica', 'clinica da familia',
    'clínica família', 'centro medico', 'centro médico',
    'policlinica', 'políclinica', 'unidade mista',
    'posto assistencial', 'unidade publica', 'unidade pública',
    'centro assistencial', 'posto de atendimento', 'caps',
    'unidade basica saude', 'unidade básica saúde', 'ubs usf',
    'posto saude familiar', 'posto saúde familiar'
]

CENTER_NAME_VARIANTS = [
    r'centro[\s\-]?de[\s\-]?saude',
    r'posto[\s\-]?de[\s\-]?saude',
    r'unidade[\s\-]?basica',
    r'ubs',
    r'cs',
    r'posto[\s\-]?medico',
    r'clinica[\s\-]?basica',
    r'centro[\s\-]?medico',
    r'caps[\s\-]?\w*',
    r'usf[\s\-]?\d*'
]