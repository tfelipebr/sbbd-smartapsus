# Este é um projeto Next.js

Este é um projeto [Next.js](https://nextjs.org/) iniciado com [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

## Como Iniciar

### Usando a versão correta do Node.js

Para garantir que você está utilizando a versão correta do Node.js para este projeto, o arquivo `.nvmrc` foi incluído. **Este processo funciona apenas em sistemas Linux/Mac**. Caso você esteja utilizando Windows, recomenda-se utilizar o [nvm-windows](https://github.com/coreybutler/nvm-windows).

### Para Linux/Mac (Usando NVM)
1. **Instalar o NVM (Node Version Manager)**:

    No terminal, execute o seguinte comando para instalar o NVM (caso não tenha o NVM instalado):

    ```bash
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
    ```

    Após a instalação, reinicie o terminal ou execute:

    ```bash
    source ~/.bashrc
    ```

2. **Instalar a versão correta do Node.js**:

    Com o NVM instalado, execute o seguinte comando para instalar a versão do Node.js especificada no arquivo `.nvmrc`:

    ```bash
    nvm install
    ```

    Isso instalará automaticamente a versão do Node.js especificada no arquivo `.nvmrc`.

3. **Usar a versão instalada**:

    Para garantir que está usando a versão correta do Node.js, execute:

    ```bash
    nvm use
    ```

    Isso configura a versão do Node.js conforme definido no arquivo `.nvmrc`.

---

### Para Windows (Usando NVM-Windows)

O NVM (Node Version Manager) não funciona nativamente no Windows. Em vez disso, você deve usar o [nvm-windows](https://github.com/coreybutler/nvm-windows), que é uma versão adaptada para Windows. 

1. **Instalar o nvm-windows**:

    - Baixe o instalador do NVM para Windows a partir do [link oficial](https://github.com/coreybutler/nvm-windows/releases).
    - Execute o instalador e siga os passos para concluir a instalação.

2. **Instalar a versão do Node.js**:

    Após a instalação do nvm-windows, abra o terminal e execute o seguinte comando para instalar a versão do Node.js especificada no arquivo `.nvmrc` (verifique o número da versão antes de prosseguir):

    ```bash
    nvm install <versão_do_node>
    ```

    Exemplo:

    ```bash
    nvm install 20.16.0
    ```

3. **Usar a versão instalada**:

    Para garantir que está usando a versão correta, execute:

    ```bash
    nvm use <versão_do_node>
    ```

---

### Instalando as dependências

Agora que você tem a versão correta do Node.js configurada, instale as dependências do projeto:

```bash
npm install
# ou
yarn install
# ou
pnpm install
```

Este comando irá instalar todas as dependências necessárias para o funcionamento do projeto.

## Iniciando o servidor
Para começar, execute o servidor de desenvolvimento:

```bash
npm run dev
# ou
yarn dev
# ou
pnpm dev
# ou
bun dev
```

Abra [http://localhost:3000](http://localhost:3000) no seu navegador para ver o resultado. As alterações feitas no código serão automaticamente atualizadas no navegador.

## Padrão de Criação de Módulos, Páginas e Rotas no Next.js

### Introdução

Este projeto utiliza um padrão modular para criar **páginas**, **módulos** e **rotas** dentro de uma aplicação Next.js. A principal vantagem desse padrão é a facilidade de manutenção, reutilização e tipagem dinâmica dos recursos ao longo do código. Com isso, criamos uma estrutura onde os componentes principais (páginas e módulos) estão fortemente tipados, e as rotas são gerenciadas de forma centralizada e dinâmica.

Este modelo tem como objetivo aumentar a produtividade e a confiabilidade do sistema, minimizando erros comuns em projetos maiores, como o uso incorreto de rotas ou módulos.

### Estrutura de Diretórios

A estrutura de diretórios foi organizada de maneira modular, com cada módulo/rota/feature sendo autossuficiente. Abaixo está um exemplo de como os arquivos e pastas estão organizados:

```
- pages
  - estimativas
    - cidade.ts
    - index.ts
- routes
  - estimativas
    - cidade.ts
    - index.ts
- types
  - estimativas
    - cidade.ts
    - index.ts
  - base.ts
  - index.ts
```

A ideia é que cada módulo seja gerido de forma isolada, mas ainda assim possa ser referenciado e utilizado de forma global.

### Como Criar uma Página, Módulo e Rota

#### 1. **Criando Rotas**

Para criar rotas de maneira dinâmica, utilizamos a função `criarRotas`. Ela recebe o alias do módulo e o caminho base da rota, além de um objeto de rotas que define os caminhos dinâmicos para cada sub-rota.

Exemplo de como criar rotas para um módulo "cidade":

```ts
export const rotasEstimativasCidade = criarRotas("cidade", "/cidade", {
  lista: "/",
  solicitacao: "/solicitacao",
  detalhes: "/detalhes/:id",
});
```

Com isso, conseguimos criar as rotas de forma centralizada e com a tipagem automática, o que garante maior consistência e evita erros de digitação ao longo do código.

#### 2. **Criando Módulos**

Os módulos são criados utilizando a função `criarModulo`. Ela permite definir um módulo com suas propriedades (como nome e título) e submódulos. A função também gera automaticamente um alias único para cada módulo, facilitando a navegação no código.

Exemplo de como criar um módulo "cidade":

```ts
export const modulosEstimativasCidade = criarModulo("cidade", {
  nome: "Cidade",
  titulo: "Estimativa de Demanda por Cidade",
  submodulos: {
    solicitacao: {
      nome: "Solicitação",
      titulo: "Solicitação de estimativa de demanda por cidade",
    },
    detalhes: {
      nome: "Detalhes",
      titulo: "Detalhes da estimativa de demanda por cidade",
      semLink: true,
    },
  },
});
```

#### 3. **Usando os Módulos e Rotas**

Após definir as rotas e os módulos, podemos usá-los nas páginas do Next.js. O padrão utilizado garante que sempre que uma rota for chamada, ela esteja automaticamente tipada, evitando problemas como o uso de caminhos incorretos.

Por exemplo, para navegar para a rota de **solicitação de estimativa por cidade**, podemos usar a função `router.push` com o caminho obtido dinamicamente pela função `obterCaminho`:

```ts
router.push(obterCaminho("estimativas.cidade.solicitacao"));
```

A função `obterCaminho` gera o caminho completo a partir do alias passado, e o TypeScript garante que o alias esteja correto, o que evita erros.

### Vantagens deste Modelo

1. **Tipagem Dinâmica**: Ao definir as rotas e os módulos com aliases tipados, garantimos que todas as rotas sejam automaticamente verificadas pelo TypeScript. Isso reduz significativamente os erros de digitação e melhora a confiabilidade do código.
   
2. **Centralização das Rotas**: As rotas são centralizadas em um único local, tornando mais fácil a manutenção e o gerenciamento. Qualquer alteração no caminho de uma rota pode ser feita rapidamente sem necessidade de procurar em diversas partes do código.
   
3. **Escalabilidade**: O modelo modular facilita a adição de novos módulos ou submódulos. Como cada módulo é independente, você pode adicionar novas funcionalidades sem impactar outros módulos existentes.

4. **Reutilização de Código**: Com a estrutura modular, é fácil reutilizar módulos em diferentes partes da aplicação, o que reduz a duplicação de código e melhora a organização do projeto.

5. **Facilidade de Navegação**: A utilização dos aliases nas rotas e módulos permite que a navegação pelo código seja mais intuitiva. Em vez de usar strings de caminho de forma desordenada, você pode referenciar rotas e módulos por seus aliases claramente definidos.
