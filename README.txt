=======================================================================
CHATBOT PARA ATENDIMENTO AO CIDADÃO NA ÁREA DE SAÚDE EM BELO HORIZONTE
=======================================================================


OBJETIVO DO SISTEMA BASEADO EM IA:
--------------------------------------------
O sistema tem como objetivo automatizar o atendimento ao cidadão, fornecendo informações 
sobre os Centros de Saúde de Belo Horizonte, como localização, áreas de abrangência e 
telefones de contato. Ele resolve problemas como a alta demanda por informações repetitivas, 
melhora o acesso aos serviços de saúde e reduz a carga de trabalho dos atendentes humanos, 
além de combater a desinformação e a dificuldade de acesso aos serviços.


DEFINIÇÃO DA JORNADA DO USUÁRIO:
--------------------------------------------
1. O usuário acessa o site do chatbot.
2. Digita sua dúvida, como:
    1️⃣ POR BAIRRO:
    Exemplo: "Postos de saúde no Santa Terezinha"
    → Retorna todos os centros no bairro especificado

    2️⃣ POR REGIÃO/DISTRITO:
    Exemplo: "Centros de saúde na região Nordeste"
    → Retorna unidades por distrito sanitário

    3️⃣ POR NOME DO CENTRO:
    Exemplo: "Centro de Saúde Padre Tiago"
    → Retorna informações detalhadas da unidade
3. O sistema processa a pergunta e consulta os dados oficiais.
4. Retorna informações como nome, endereço e telefones do(s) centro(s).
5. O usuário pode continuar perguntando até obter todas as informações desejadas.


ARQUITETURA DO SISTEMA
--------------------------------------------
[Frontend GitHub Pages] → [Backend Render] → [Dataset PBH]

Componentes:
- Frontend: Interface web responsiva (HTML/CSS/JS)
- Backend: API Python/Flask com:
    * Processamento de linguagem natural (spaCy)
    * Utilização de dados abertos
    * Gerenciamento de conversação
- Dados: Dataset oficial da Prefeitura de BH
 

HOSPEDAGEM
--------------------------------------------
FRONTEND:
- Plataforma: GitHub Pages
- URL: https://matdias0307.github.io/Chatbot-Centros-de-Saude-BH/

BACKEND:
- Plataforma: Render
- URL: https://chatbot-centros-de-saude-bh-backend.onrender.com


DADOS UTILIZADOS
--------------------------------------------
Fonte oficial: Portal de Dados Abertos de BH
Dataset: https://dados.pbh.gov.br/dataset/area-de-abrangencia-saude

Contém:
- Nome dos Centros de Saúde
- Endereços completos
- Telefones de contato
- Bairros e Distritos Sanitários
- Áreas de abrangência


DESENVOLVIMENTO LOCAL
--------------------------------------------
BACKEND:

O backend é responsável por receber perguntas dos usuários, extrair
entidades (bairro, região, nome do centro) e consultar as informações
dos Centros de Saúde no dataset.

1. Clone o repositório:
   git clone https://github.com/MatDias0307/Chatbot-Centros-de-Saude-BH.git
   cd chatbot-saude-bh/backend

2. Configure ambiente virtual:
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate  # Windows

3. Instale dependências:
   pip install -r requirements.txt
   python -m spacy download pt_core_news_sm

4. Execute:
   python app.py

FRONTEND:

Interface web onde os usuários interagem com o chatbot.

1. Acesse a pasta:
   cd frontend

2. Instale dependências:
   npm install

3. Execute servidor de desenvolvimento:
   npm start


ENDPOINTS DA API
--------------------------------------------
POST /api/chat
- Finalidade: Processar mensagens do usuário
- Payload: {"message": "Texto da pergunta"}
- Resposta: {
    "response": "Texto da resposta",
    "data": {dados_adicionais}
  }


CONTATO 
--------------------------------------------
Desenvolvedor Responsável:
Matheus Dias Soares
matheus.diassl0307@gmail.com

Repositório GitHub:
https://github.com/MatDias0307/Chatbot-Centros-de-Saude-BH#