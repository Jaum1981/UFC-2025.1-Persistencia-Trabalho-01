# Trabalho Prático 1 – API REST com FastAPI e Persistência em CSV

**Universidade Federal do Ceará – Campus Quixadá**  
**QXD0099 – Desenvolvimento de Software para Persistência**  
**Prof. Francisco Victor da Silva Pinheiro**


## Discentes
1. Francisco Breno da Silveira (511429)
2. João Victor Amarante Diniz (510466)

---

## 📄 Descrição

Este projeto implementa uma **API REST** usando **FastAPI** para gerenciar três entidades distintas (por exemplo: Produto, Cliente e Pedido), com persistência de dados em arquivos CSV. Funcionalidades adicionais incluem compactação dos CSVs em ZIP, cálculo de hash SHA-256, geração de XML, filtragem avançada e logging de todas as operações, simulando um cenário real de aplicação com maior controle e auditoria.

---

## 🚀 Funcionalidades

1. **CRUD Completo**  
   - Create, Read, Update, Delete em cada entidade.  
   - Atualização imediata dos respectivos arquivos CSV.  

2. **Listagem de Registros**  
   - Retorna todos os registros da entidade em JSON.  

3. **Contagem de Registros**  
   - Retorna a quantidade total de entidades cadastradas.  

4. **Compactação em ZIP**  
   - Permite baixar o CSV compactado como `<entidade>.zip`.  

5. **Filtragem por Atributos**  
   - Parâmetros de query para filtrar por campos específicos (e.g., categoria, intervalo de preço).  

6. **Hash SHA-256**  
   - Calcula e retorna o hash do CSV, garantindo integridade dos dados.  

7. **Logging de Operações**  
   - Arquivo de log registra data, hora, tipo de operação e status.  

8. **Exportação para XML**  
   - Gera e disponibiliza download do `<entidade>.xml` a partir do CSV.

---

## Estrutura do Projeto

.
├── data/            # CSVs populados
│   ├── movie.csv
│   ├── session.csv
│   └── ticket.csv
├── logs/            # Configuração e arquivos de log
│   ├── configMovie.yaml
│   ├── configSession.yaml
│   └── configTicket.yaml
├── models/          # Definições de Pydantic models
│   ├── movie.py
│   ├── session.py
│   └── ticket.py
├── routers/         # Endpoints FastAPI
│   ├── movie.py
│   ├── session.py
│   └── ticket.py
└── main.py          # Ponto de entrada onde tudo é amarrado


---


## Instruções de Configuração e Execução

1. **Criar ambiente virtual**  
   ```bash
   python -m venv venv
   ```
2. **Ativar o ambiente**
   ```bash
   source/env/bin/activate
   ```
3. **Instalar dependências**
   ```bash
   pip install -r requirements.txt
   ```
4. **Iniciar o servidor**
   ```bash
   uvicorn main:app --reload --port 3000
   ```
5. **Acessar swagger**
   ```bash
   http://localhost:3000/docs
   ```
