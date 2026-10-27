# Controle de Estoque — MVP para Mercadinho

Aplicação web acadêmica para organizar o estoque de um pequeno mercadinho. O MVP permite cadastrar produtos, consultar saldo, registrar entradas e saídas, sinalizar estoque baixo e consultar o histórico das movimentações.

> **Estado do projeto:** protótipo funcional para desenvolvimento e validação acadêmica. Não use para operações comerciais reais sem revisão de segurança, backup, configuração de implantação e testes adicionais.

## Funcionalidades

- Login com senha armazenada por hash; não existe usuário/senha padrão no código.
- Cadastro de produtos com nome, código único, preço, quantidade inicial e estoque mínimo.
- Consulta por nome ou código.
- Alertas textuais e simbólicos quando a quantidade é menor ou igual ao estoque mínimo.
- Registro de entradas e saídas, com validação no servidor.
- Recusa de saída maior que o saldo disponível, sem gravar movimento ou alterar quantidade.
- Atualização do movimento e do saldo na mesma transação SQLite.
- Histórico de entradas/saídas e filtro por produto.
- Proteção CSRF nos formulários, consultas SQL parametrizadas, sessão com cookie HttpOnly/SameSite e rotas internas protegidas.
- Interface responsiva, labels associados aos campos, foco visível, link para pular ao conteúdo e alertas que não dependem só da cor.
- Testes automatizados com pytest e execução automática no GitHub Actions para pushes e pull requests.

## Tecnologias

- Python 3.12 (recomendado para reprodução da atividade)
- Flask 3.x
- Flask-WTF (proteção CSRF)
- SQLite
- pytest
- Git e GitHub Actions

As versões instaladas serão resolvidas dentro dos limites de compatibilidade listados em `requirements.txt`. Para execução de avaliação, registre as versões efetivamente utilizadas.

## Requisitos

- Python 3.12 instalado.
- Git, se for publicar o histórico de commits usando terminal.
- Acesso à internet para instalar dependências; depois de instaladas, o protótipo local não precisa de conexão externa.

## Instalação local

### Linux/macOS

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Abra o arquivo `.env` e substitua `SUBSTITUA_POR_UM_SEGREDO_ALEATORIO` por um valor gerado com:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Não publique o arquivo `.env` nem compartilhe sua chave secreta. O `.gitignore` já exclui esse arquivo. O valor de desenvolvimento padrão do código não deve ser utilizado em produção.

## Inicializar e executar

Execute os comandos na pasta principal do projeto, com o ambiente virtual ativado:

```bash
python -m flask --app mercadinho:create_app init-db
python -m flask --app mercadinho:create_app create-user
python -m flask --app mercadinho:create_app seed-demo
python -m flask --app mercadinho:create_app run --debug
```

O comando `create-user` solicitará nome e senha no terminal; a senha deve ter pelo menos 10 caracteres. Não existe senha padrão. O comando `seed-demo` cria três produtos fictícios (arroz, leite e feijão) e não duplica os códigos já cadastrados. Acesse `http://127.0.0.1:5000` no navegador e entre com o usuário criado.

Para interromper o servidor, pressione `Ctrl+C` no terminal.

## Executar os testes

```bash
pytest
```

Os testes usam um banco temporário e um usuário fictício; não alteram o banco de dados local. Eles cobrem acesso protegido, login inválido/válido, cadastro e duplicidade de produto, atualização de saldo, rejeição de saída excessiva, alerta de estoque baixo e histórico.

## Integração contínua (CI)

O arquivo `.github/workflows/tests.yml` configura o GitHub Actions. A cada `push` ou `pull_request`, o workflow instala as dependências e executa `pytest`. No GitHub, abra a aba **Actions** para conferir o resultado. Um indicador verde significa que os testes passaram naquele commit; vermelho indica que a execução precisa ser investigada.

## Publicar no seu GitHub preservando os commits

1. Crie no GitHub um repositório **público vazio** chamado `controle-estoque-mercadinho`. Se o pacote já tiver histórico Git, não marque a opção para criar outro README no GitHub.
2. Extraia o ZIP e entre na pasta `controle-estoque-mercadinho` pelo terminal.
3. Confira o estado e o histórico:

```bash
git status
git log --oneline
```

4. Adicione o endereço do seu próprio repositório (substitua o endereço de exemplo pelo URL real):

```bash
git remote add origin https://github.com/SEU-USUARIO/controle-estoque-mercadinho.git
git branch -M main
git push -u origin main
```

Os commits no pacote são históricos locais até o envio ser concluído. Só depois do `push` eles estarão visíveis no GitHub. Nunca inclua senhas, tokens, chaves secretas, dados de clientes ou informação privada no repositório público.

## Histórico semântico incluído

O pacote foi organizado com commits locais sobre a fundação do projeto, funcionalidades, interface, testes/CI e documentação. Confira os SHAs reais com `git log --oneline --date=short`. Se você extrair o conteúdo sem a pasta oculta `.git`, o histórico não será preservado e precisará ser recriado.

## Estrutura principal

```text
controle-estoque-mercadinho/
├── .github/workflows/tests.yml   # Pipeline de CI
├── mercadinho/
│   ├── schema.sql                # Tabelas, chaves e restrições SQLite
│   ├── __init__.py               # Fábrica da aplicação Flask
│   ├── db.py                     # Conexão, inicialização e comandos CLI
│   ├── views.py                  # Blueprint, proteção de rotas e validação comum
│   ├── auth.py                   # Login e logout
│   ├── products.py               # Cadastro e consulta de produtos
│   ├── movements.py              # Movimentações e histórico
│   ├── templates/                # Telas HTML com Jinja
│   └── static/style.css          # Interface responsiva e acessível
├── tests/                        # Testes automatizados
├── .env.example                  # Modelo de configuração local
├── .gitignore
├── app.py
├── pytest.ini
└── requirements.txt
```

## Decisões e limites conhecidos

- SQLite é adequado para desenvolvimento e uso inicial de baixo volume; uso simultâneo intenso pode exigir banco servidor, como PostgreSQL.
- O acesso é restrito a usuários cadastrados pelo comando administrativo; o MVP ainda não implementa cadastro de usuários pela interface, recuperação de senha ou controle de diferentes perfis.
- A validação de preço e quantidades ocorre no servidor; a validação HTML melhora a experiência, mas não substitui as regras do servidor.
- O histórico é limitado aos 500 registros mais recentes na tela.
- O MVP não integra pagamentos, emissão fiscal, pedidos automáticos a fornecedores nem dados pessoais de clientes.
- Antes de uma implantação pública: usar HTTPS, definir `COOKIE_SECURE=1`, configurar segredo forte no ambiente do servidor, desativar modo debug, avaliar backups/restauração, atualizar dependências e executar testes de segurança.

## Checklist de validação manual

- [ ] Login incorreto não permite acesso ao estoque.
- [ ] Cadastro rejeita campos vazios, preço inválido e código duplicado.
- [ ] Entrada aumenta o saldo e cria uma movimentação.
- [ ] Saída válida reduz o saldo e cria uma movimentação.
- [ ] Saída maior que o saldo é recusada sem alterar o estoque.
- [ ] Produto com quantidade menor ou igual ao mínimo mostra o texto **Estoque baixo**.
- [ ] Histórico mostra tipo, quantidade, produto e data/hora.
- [ ] É possível navegar com teclado; foco fica visível; alertas são compreensíveis sem depender só de cor.
- [ ] Layout é verificado em largura de 360 px e com zoom do navegador.
