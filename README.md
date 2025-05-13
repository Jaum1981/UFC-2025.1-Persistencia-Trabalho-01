## Relatório de Divisão de Atividades

**Projeto:** Desenvolvimento de API REST com FastAPI para Gerenciamento de Entidades com Persistência em CSV

**Disciplina:** Desenvolvimento de Software para Persistência

**Data de entrega:** 13.05.2025

**Dupla:**

* **Aluno 1:** João Victor Amarante Diniz (510466)
* **Aluno 2:** Francisco Breno da Silveira (511429)

---

### 1. Introdução

Este projeto tem como objetivo desenvolver uma API REST utilizando o framework FastAPI para realizar o gerenciamento de três entidades: Filmes (Movies), Sessões de exibição (Sessions) e Ingressos (Tickets), como base no domínio Cinema, adotado para o desenvolvimento deste trabalho. A persistência dos dados foi feita utilizando arquivos CSV, com suporte adicional para exportação dos dados em XML, compactação em arquivos ZIP, cálculo de hash SHA256 para verificação de integridade, e filtragem por atributos.

As tecnologias utilizadas incluem:

* **FastAPI** para construção das rotas REST;
* **Pydantic** para definição e validação de modelos de dados;
* **YAML** para configurações dinâmicas dos caminhos de arquivos;
* **logging** para rastreamento de ações e erros;
* **Python** como linguagem base.

A aplicação está dividida em pastas organizadas por responsabilidade: `routers`, `models`, `utils`, `data`, `compressed`, e `xml_files`.

**Responsável pela redação do relatório:** Francisco Breno

---

### 2. Configuração do Projeto

#### Ambiente de Desenvolvimento

O projeto é compatível com sistemas Windows, Linux e macOS. Abaixo, seguem as instruções para configuração do ambiente em todas as plataformas:

**1. Criar ambiente virtual:**

Windows (CMD ou PowerShell):

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

**2. Instalar dependências:**

Com o ambiente virtual ativado, execute:

```bash
pip install -r requirements.txt
```

**Conteúdo do arquivo `requirements.txt`:**

```
annotated-types==0.7.0
anyio==4.9.0
click==8.1.8
colorama==0.4.6
fastapi==0.115.12
h11==0.16.0
idna==3.10
pydantic==2.11.4
pydantic_core==2.33.2
PyYAML==6.0.2
sniffio==1.3.1
starlette==0.46.2
typing-inspection==0.4.0
typing_extensions==4.13.2
uvicorn==0.34.2
```

#### Estrutura de Diretórios

* **routers/**: contém os arquivos de rotas (`movie.py`, `session.py`, `ticket.py`)
* **models/**: contém os modelos Pydantic utilizados pelas rotas
* **utils/**: configurações e utilitários como o logger e leitura do `config.yaml`
* **data/**: arquivos `.csv` com os dados persistidos
* **compressed/**: arquivos `.zip` gerados
* **xml\_files/**: arquivos `.xml` gerados

#### Configuração por YAML

Todas as rotas utilizam um arquivo `config.yaml` para definir os caminhos dos arquivos de dados (CSV, ZIP, XML) e configurações de logging. Isso torna o projeto mais modular e fácil de manter.

* **Setup do ambiente virtual e dependências**: Francisco Breno
* **Estrutura de pastas e arquivos**: Francisco Breno
* **Arquivo de configuração YAML**: Francisco Breno

#### Execução

```
uvicorn main:app --reload --port 3000
```
#### Acessar documentação
```
http://localhost:3000/docs
```

---

### 3. Implementação dos Models

* **Definição de classes Pydantic** (`Movie`, `Session`, `Ticket`)

  * Responsável: João Victor e Francisco Breno

---

### 4. Leitura e Gravação de CSV

* **Funções `read_*/write_*_csv` para Movies, Sessions e Tickets**

  * Responsável: João Victor (Movies e Sessions) e Francisco Breno (Tickets)
* **Tratamento de parsing de tipos e listas**

  * Responsável: João Victor (Movies e Sessions) e Francisco Breno (Tickets)

---

### 5. Endpoints CRUD

* **Movies (GET, POST, PUT, DELETE)**

  * Responsável: João Victor
* **Sessions (GET, POST, PUT, DELETE)**

  * Responsável: João Victor
* **Tickets (GET, POST, PUT, DELETE)**

  * Responsável: Francisco Breno

---

### 6. Endpoints Auxiliares

* **Contagem de registros** (`-count`)

  * Responsável: João Victor (Movies e Sessions) e Francisco Breno (Tickets)
* **Geração de ZIP** (`-zip`)

  * Responsável: João Victor (Movies e Sessions) e Francisco Breno (Tickets)
* **Cálculo de hash SHA256** (`-hash`)

  * Responsável: João Victor (Movies e Sessions) e Francisco Breno (Tickets)
* **Conversão para XML** (`-xml`)

  * Responsável: João Victor (Movies e Sessions) e Francisco Breno (Tickets)
* **Filtragem por atributos** (`-filter`)

  * Responsável: João Victor e Francisco Breno

---

### 7. Logging e Configuração

* **Implementação do logger** (configuração via `config.yaml`, `configurar_logging`)

  * Responsável: Francisco Breno
* **Inserção de logs nas rotas** (INFO, DEBUG, ERROR)

  * Responsável: João Victor e Francisco Breno

---

### 8. Testes e Validação

* **Testes manuais** (casos de uso verificados)

  * Responsável: João Victor e Francisco Breno

---

### 9. Conclusão

Este projeto implementa as diversas funcionalidades retratadas na descrição do trabalho de _F1_ a _F8_. O domínio escolhido foi cinema, visando desenvolver uma aplicação que não está distante da realidade humana. Para isso, o sistema considera `Movies`, `Sessions` e `Tickets` como as três entidades principais a serem gerenciadas nesse sistema, com os dados persistindo em `CSV`, mas também com suporte para conversão para `ZIP` e `XML`.  

* Link para o repositório no GitHub: https://github.com/Jaum1981/UFC-2025.1-Persistencia-Trabalho-01

---

