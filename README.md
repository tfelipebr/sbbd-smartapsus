# SmartApSUS  

O **SmartApSUS** é uma plataforma analítica integrada voltada ao aprimoramento das decisões estratégicas na Atenção Primária à Saúde (APS) brasileira. Unificando dados heterogêneos de saúde com técnicas avançadas de predição e otimização, o **SmartApSUS** auxilia gestores públicos na alocação eficiente de profissionais e unidades, reduzindo custos operacionais e ampliando a cobertura populacional. O **SmartApSUS** consiste em um projeto multi‑módulos.

### Informações importantes sobre este repositório

O GitHub impõe limites ao tamanho dos arquivos carregados diretamente em um repositório convencional: 25 MiB via interface web, 50 MiB via Git e bloqueio acima de 100 MiB. Optamos por não subir diretamente os arquivos binários aqui. Este repositório do GitHub contém apenas a estrutura de pastas e arquivos de configuração e suporte do sistema **SmartApSUS**, sendo utilizado exclusivamente para visualização da estrutura do sistema. 

O sistema completo, incluindo todos os arquivos binários necessários (com exceção do **IBM ILOG CPLEX Optimization Studio**), está disponível para download no link abaixo. Para executá-lo localmente, faça o download do arquivo `sistema-smartapsus.zip` que está no link abaixo e extraia os arquivos na sua máquina:

📥 **[Baixar sistema completo (Dropbox)](https://tinyurl.com/sbbd-smartapsus-repositorio)**


## 1. Visão geral do sistema

O back-end do **SmartApSUS** é uma plataforma composta por três serviços principais que se comunicam via **RabbitMQ Streams** e compartilham um banco **PostgreSQL/PostGIS**:

| Módulo Maven  | Imagem/Dockerfile | Responsabilidade principal |
|---------------|-------------------|----------------------------|
| **commom**            | –                         | Biblioteca interna compartilhada (contrato de mensageria). |
| **servico_spring**    | `Dockerfile`              | API Core + OAuth2 Authorization Server, lógica de negócio. |
| **servico_dados**     | `Dockerfile`              | Importador de dados. |
| **servico_otimizacao**| `Dockerfile` & `Dockerfile_otimizacao` | Algoritmos de otimização (CPLEX, PuLP, NumPy). |

Todo o ecossistema do back-end pode ser iniciado em um único comando usando `docker‑compose`.

O front-end do sistema utiliza **Next.js** (React + TypeScript) para oferecer uma interface web moderna e responsiva, conectando-se diretamente aos serviços do back-end via chamadas REST (HTTP) através da biblioteca **Axios**. O projeto emprega bibliotecas específicas para visualização de dados espaciais, gráficos analíticos e internacionalização. A estrutura modular do front-end permite fácil manutenção, expansão e reutilização dos componentes.

---

## 2. Stack tecnológica

A seguir apresentamos os elementos da stack tecnológica que dão sustentação ao **SmartApSUS**.

No back-end, começamos pelo **ecossistema Java** (JDK 17) sobre o qual se apoiam **Spring Boot 3.2** e o *release train* **Spring Cloud 2023.0**, responsáveis pelo framework web, segurança, mensageria e configuração distribuída; a camada de dados emprega **PostgreSQL 16** estendido com **PostGIS** e seus complementos (**Hibernate Spatial + JTS + GeoTools**) para tratar informações geográficas de forma nativa. A comunicação assíncrona acontece via **RabbitMQ 3** em modo _Streams_, enquanto a construção e o empacotamento de todos os módulos são orquestrados por um **projeto Maven multimódulo** e executados em containers **Docker**, o que garante portabilidade do ambiente. Requisitos de otimização matemática são resolvidos combinando **CPLEX Studio 22.1.1** (solver proprietário) com scripts Python baseados em **PuLP**, completando a pilha de tecnologias que suporta importação de dados, análise espacial, APIs seguras e busca de soluções ótimas de forma integrada.

> **Stack do back-end:**
* **Java 17**, **Spring Boot 3.2**, **Spring Cloud 2023.0**
* **PostgreSQL 16 + PostGIS** (persistência geoespacial)
* **RabbitMQ 3 (Streams + Management UI)**
* **Hibernate Spatial**, **JTS**, **GeoTools**
* **Maven multimódulo** (`pom.xml` de _packaging_ **pom** na raiz)
* **Docker** para build e runtime
* **CPLEX Studio 22.1.1** e **PuLP** para otimização

No front-end, utilizamos o framework **Next.js 14** (com React 18 e TypeScript 5), proporcionando interfaces dinâmicas e responsivas, estrutura modular e gerenciamento centralizado das rotas. O projeto conta ainda com bibliotecas especializadas para visualização e manipulação de dados espaciais (**Leaflet**, **React Leaflet**, **Turf.js**), gráficos e visualizações analíticas (**Chart.js**, **React Chartjs-2**), internacionalização (**i18next**) e experiência do usuário (UX/UI) aprimorada com **Tailwind CSS**, componentes do **Headless UI** e bibliotecas auxiliares como **react-toastify**, **react-select** e **sweetalert2**.

> **Stack do front-end:**
>
> * **Next.js 14**, **React 18**, **TypeScript 5**
> * **Tailwind CSS** (estilização e UI responsiva)
> * **Axios** (requisições HTTP)
> * **i18next** (internacionalização)
> * **Chart.js**, **React Chartjs-2** (visualização de dados)
> * **Leaflet**, **React Leaflet**, **Turf.js** (manipulação de mapas e dados espaciais)
> * **Headless UI**, **React Select**, **React Toastify**, **SweetAlert2** (componentes e experiência do usuário)


---

## 3. Pré‑requisitos

Antes de executar o **SmartApSUS**, verifique se seu ambiente de desenvolvimento possui as ferramentas básicas listadas a seguir. Elas garantem que você consiga construir as imagens Docker, executar o código Java do back-end e iniciar o servidor do front-end (Next.js). Caso pretenda rodar o ambiente exclusivamente dentro dos containers, é suficiente ter **Docker + Compose** instalados; o **JDK 17** e o **Maven** são exigidos apenas para executar módulos Java diretamente na sua máquina. Para o front-end, será necessário o **Node.js** (conforme especificado no `.nvmrc`) e um gerenciador de pacotes como o **npm** ou **yarn**.

| Ferramenta                  | Versão + observações                                                |
| --------------------------- | ------------------------------------------------------------------- |
| **Docker & Docker Compose** | Docker >= 24, Compose‑V2 (plugin)                                   |
| **Java JDK 17**             | Necessário apenas para compilar/executar back-end fora do Docker    |
| **Maven 3.9+**              | Idem                                                                |
| **Node.js (via nvm)**       | v20                             |
| **npm ou yarn**             | Necessário para instalação das dependências e execução do front-end |



---


## 4. Estrutura de diretórios

A árvore a seguir ilustra a organização do **SmartApSUS**: na raiz ficam os artefatos de orquestração ( `pom.xml` multimódulo e `docker‑compose.yml` ) e arquivos auxiliares, enquanto cada subpasta encapsula um componente funcional — o núcleo da API (`servico_spring`), o importador de dados (`servico_dados`), o solver de otimização (`servico_otimizacao`), uma pequena biblioteca de mensageria (`commom`, hoje composta apenas pelas classes `Event` e `Publisher` que padronizam a publicação de mensagens no RabbitMQ/StreamBridge) e, por fim, a interface Web (`frontend‑next`). Cada serviço do back-end inclui seu próprio **Dockerfile**, permitindo builds independentes, mas todos convergem para uma execução integrada via Compose, que também provisiona PostGIS e RabbitMQ; scripts opcionais de inicialização de banco residem em `init.sql`.


```text
smartapsus/
├── commom/                 # Biblioteca de mensageria
├── servico_spring/         # API Core + Auth
│   └── Dockerfile
├── servico_dados/          # Serviço de importação de dados
│   └── Dockerfile
├── servico_otimizacao/     # Serviço de otimização com algoritmos de otimização
│   ├── Dockerfile
│   └── Dockerfile_otimizacao
├── frontend-next/          # Front-end
├── docker-compose.yml      # Orquestração local
├── init.sql                # Script inicial para extensão unaccent do PostgreSQL
└── pom.xml                 # Arquivo Maven raiz que define o projeto multimódulo
```

---

## 5. Configuração de ambiente

Os serviços do back-end leem variáveis definidas no `docker-compose.yml`. Se for executar sem Docker, exporte:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export SPRING_PROFILES_ACTIVE=dev
```

### Perfis Spring

* **dev** – execução local sem Docker
* **docker** – configurações voltadas ao *compose* (URLs internas, limites de memória)
* **test** – configurações in‑memory utilizadas pelos testes automatizados

---

## 6. Back-end

### Serviços

O back-end é organizado em serviços independentes, cada um responsável por funções específicas da aplicação, tais como gerenciamento de dados, otimização de recursos, comunicação via mensagens e persistência em banco de dados. Essa arquitetura modular promove maior escalabilidade, manutenibilidade e eficiência no gerenciamento e processamento das operações realizadas pelo sistema.


### * _Mensageria_

Todos os serviços do **SmartApSUS** publicam / consomem eventos via **RabbitMQ Streams**; o binder do Spring Cloud Stream está configurado em `application.yml`.
A UI web do RabbitMQ expõe o tráfego de mensagens em `localhost:15672`.

---

### * _Banco de Dados_

O `docker-compose.yml` já provisiona um container **postgis/postgis**:

```
user/pass: postgis / postgis
porta local: 5435
database: postgis
```

---

### * _API Core e Autenticação (servico\_spring)_

O serviço `servico_spring` implementa a API principal do sistema **SmartApSUS**, fornecendo os endpoints REST responsáveis pela comunicação direta com o front-end. Este serviço gerencia as operações fundamentais da aplicação, incluindo autenticação e autorização de usuários com base em **Spring Security**, validação dos dados recebidos, controle de acesso baseado em perfis e execução das regras de negócio ao sistema. Além disso, o serviço é responsável por interagir com os demais componentes via mensagens assíncronas no **RabbitMQ Streams**, garantindo desacoplamento e robustez na integração entre módulos. O `servico_spring` é empacotado em uma imagem Docker configurada com todas as dependências necessárias para sua execução local ou em produção.

---

### * _Importador de Dados (servico\_dados)_

[//]: # (>* Aceita *uploads* de arquivos CSV/GeoPackage/Shapefile.)
* Aceita *uploads* de arquivos CSV/GeoJSON.
* Importa dados via API do IBGE.

---

### * _Otimização (servico\_otimizacao)_

Este serviço é responsável por resolver modelos de otimização, com o objetivo de identificar cenários ideais de alocação de recursos no contexto do sistema **SmartApSUS**. O serviço opera em uma imagem Docker pré-configurada, onde são instalados todos os componentes e dependências necessárias para executar as otimizações solicitadas.

---
#### *Pré-requisitos do serviço de otimização*

Para utilizar o serviço de otimização, você precisa baixar o **IBM ILOG CPLEX Optimization Studio**.

**Importante**: O arquivo de instalação (`cplex.bin`) não é distribuído publicamente. Você precisa obtê-lo diretamente com a IBM.

Para obter o **IBM ILOG CPLEX Optimization Studio** há duas opções principais para download:

#### _1. Academic Initiative (gratuito para estudantes e professores)_

1. Acesse [IBM Academic Initiative](http://ibm.biz/CPLEXonAI).
2. Registre-se com seu IBMid e valide seu vínculo acadêmico.
3. Após aprovação, navegue até **Software → ILOG CPLEX Optimization Studio** e baixe a versão para **Linux x86-64** (`cplex_studio2211.linux_x86_64.bin`).

#### _2. IBM Passport Advantage (licenças comerciais ou trials)_

1. Acesse [IBM Passport Advantage](https://www.ibm.com/support/pages/downloading-ibm-ilog-cplex-optimization-studio-2211).
2. Faça login com seu IBMid, consulte seu **site number** para permissões.
3. Na seção **Find Downloads and Media**, baixe a versão multiplataforma (Linux `.bin`).

#### Após o download:

Renomeie o arquivo `cplex_studio2211.linux_x86_64.bin` para`cplex.bin` e coloque-o em:

```bash
sistema-smartapsus/servico_otimizacao/src/main/resources
```

---

#### Construção da Imagem Docker do Serviço de Otimização

Para criar (ou recriar) a imagem do serviço de otimização:

```bash
cd sistema-smartapsus
make otimizacao
```

**Nota**: Isso gera a imagem Docker `smartapsus/otimizacao:0.1` com Python, CPLEX e dependências instaladas.

O serviço de otimização utiliza diversos componentes descritos na tabela abaixo. O CPLEX é o principal resolvedor de problemas de otimização linear e inteira mista, sendo obrigatório para que o serviço funcione corretamente. Os scripts auxiliares escritos em Python (com PuLP e NumPy) são utilizados para pré-processamento e pós-processamento dos dados. 


| Componente                | Função                                                                                          |
| ------------------------- | ----------------------------------------------------------------------------------------------- |
| **CPLEX**                 | Resolve modelos de otimização lineares/mistos. Binário `cplex.bin` deve ser instalado na imagem. Ele faz parte do **IBM ILOG CPLEX Optimization Studio**, que é distribuído diretamente pela IBM.     |
| **Python 3 + PuLP/NumPy** | Scripts auxiliares `facility_v*.py` disponíveis no caminho `servico_otimizacao/src/main/resources`.                                 |
| **RabbitMQ Streams**      | Recebe eventos disparados pelo backend, contendo o identificador da execução e o tipo de algoritmo a ser executado. Após processar esses eventos, retorna as soluções ótimas encontradas.         |



---

### Subindo todos os serviços

Para subir todos os serviços do back-end (PostGIS, RabbitMQ, API core, otimização e outros):

```bash
make up
```

Ou manualmente, com rebuild se necessário:

```bash
docker-compose up --build
```

---

### Verificando Logs e Portas

Concluída a orquestração dos containers, procede‑se à verificação do pleno funcionamento de cada serviço. Para tanto, examine os fluxos de log e certifique‑se de que não há exceções ou mensagens de erro, observando ainda se as portas mapeadas estão efetivamente em escuta. Utilize os comandos abaixo para acompanhar, em tempo real, a saída de cada componente:

```bash
docker-compose logs -f servico_otimizacao
docker-compose logs -f postgis
docker-compose logs -f servico_spring
docker-compose logs -f servico_dados
docker-compose logs -f message
```

Após confirmar nos logs que todos os serviços estão em execução normal, verifique a disponibilidade e o acesso às interfaces e recursos expostos pelos containers. Abaixo estão detalhados os principais pontos de acesso que devem ser verificados após o startup completo dos serviços:

* API Spring Boot disponível em `http://localhost:8080`
* RabbitMQ Management UI disponível em `http://localhost:15672` (usuário/senha: guest/guest)
* PostGIS mapeado na porta `5435`

---

## 7. Front-end (Next.js)

### Instalação

No diretório `frontend-next`, instale as dependências em modo produção:

```bash
cd frontend-next
npm ci --production
```
---

### Configuração das variáveis de ambiente

Caso necessário, ajuste o arquivo `frontend-next\.env`, configurando as variáveis conforme o seu ambiente de execução. Por exemplo:

```ini
NEXT_PUBLIC_BASE_URL=http://localhost:8081
```

* A variável `NEXT_PUBLIC_BASE_URL` define a URL base utilizada pelo front-end para realizar requisições ao backend da aplicação. No exemplo acima, o sistema front-end tentará acessar os serviços do backend localizados em `http://localhost:8081`.

Certifique-se de que o endereço configurado está correto e acessível para garantir o funcionamento adequado do sistema.

---

### Executando o Front-end em Produção

Para iniciar o servidor Next.js:

```bash
cd frontend-next
npm run start
```

O servidor (front-end) ficará disponível por padrão em:

```
http://localhost:3000
```


## 8. Restauração do Banco de Dados

A restauração do banco — seja para reconstruir um ambiente de desenvolvimento ou simplesmente popular uma instância limpa — pode ser realizada de duas maneiras: através da interface gráfica do **pgAdmin** ou por meio dos utilitários de linha de comando **psql/pg\***. As subseções seguintes explicam, passo a passo, cada abordagem, indicando os parâmetros essenciais e os pontos de atenção que asseguram uma recuperação íntegra do esquema **PostGIS** utilizado pelo sistema.

### * Restauração do Banco de Dados usando **pgAdmin**

Quando optar pelo **pgAdmin**, certifique‑se de que o sistema já foi inicializado ao menos uma vez; na primeira execução, o `servico_spring` cria automaticamente o esquema base (tabelas, extensões PostGIS, funções auxiliares). Com essa estrutura previamente estabelecida, o processo de restauração limitar‑se‑á a reinserir dados e objetos adicionais, evitando conflitos de dependência.

#### 1. Selecionar o banco de destino

1. No **pgAdmin**, expanda o servidor e clique em **Databases**.
2. Clique com o botão direito sobre o banco de destino (`postgis`)
3. Escolha **Restore…**

Você será encaminhado para a aba **General**.

#### 2. Aba **General**

| Campo              | O que preencher                                                                                        |
| ------------------ | ------------------------------------------------------------------------------------------------------ |
| **Format**         | Selecione **Custom or tar**                                 |
| **Filename**       | Clique no ícone de pasta e aponte para o arquivo do dump do banco de dados (ex: `database\dump-postgis.sql`)     |
| **Number of jobs** | (opcional) Deixe em branco ou defina quantos processos paralelos quer usar para acelerar a restauração |
| **Role name**      | Usuário que assumirá a posse dos objetos restaurados; selecione `postgis` se estiver disponível ou outro _role_ com privilégios adequados. |


#### 3. Executar a restauração

1. Ajuste, se necessário, a aba **Options** (por exemplo, sobrescrita de objetos existentes).
2. Clique em **Restore**.
3. Acompanhe a aba **Messages** para verificar progresso e possíveis erros.
4. Ao término, pressione **F5** sobre o banco para atualizar a árvore de objetos; tabelas, *views* e demais estruturas devem aparecer imediatamente.



> **Observação** Caso surjam erros na primeira tentativa, repita o procedimento e, na aba **Options**, em “Miscellaneous / Behavior”, marque **Exclude schema** e informe `public`; isso evita conflitos de objetos já criados.



### * Restauração do Banco de Dados usando **psql**

Para administradores que preferem o terminal, os utilitários nativos **`createdb`**, **`dropdb`** e **`psql`** oferecem um caminho direto, sem interface gráfica, mantendo total controle sobre cada etapa do processo.

#### 1. Restaurar um dump **plain SQL** (`.sql`) com o `psql`

1. (Opcional) Se o banco ainda não existir (ou você quiser recriar do zero), execute:

   ```bash
   # remover instância existente
   dropdb -U postgis -h localhost postgis

   # criar instância vazia
   createdb -U postgis -h localhost postgis
   ```
2. Execute o script SQL inteiro:

   ```bash
   psql \
     -U postgis \
     -h localhost \
     -d postgis \
     -f "database\dump-postgis.sql"
   ```

Após a conclusão, o banco estará restaurado, pronto para ser utilizado pelos serviços do **SmartApSUS**.

## 9. Credenciais de Acesso ao Sistema

Após restaurar com sucesso o dump do banco de dados e colocar os serviços em execução, utilize as credenciais abaixo para acessar o sistema:

```
Usuário: admin@smartapsus.com.br  
Senha: 1234
```


