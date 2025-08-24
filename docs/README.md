# Documentação do Projeto Finanpy

Bem-vindo à documentação completa do Finanpy, um sistema de gestão de finanças pessoais desenvolvido em Django.

## Índice da Documentação

### 📚 Guias Essenciais
- **[Setup e Instalação](./setup-guide.md)** - Como configurar o ambiente de desenvolvimento
- **[Arquitetura do Projeto](./architecture.md)** - Visão geral da estrutura e componentes
- **[Padrões de Código](./coding-standards.md)** - Guidelines e convenções de desenvolvimento

### 🏗️ Desenvolvimento
- **[Estrutura do Banco de Dados](./database-structure.md)** - Modelos e relacionamentos
- **[APIs e Endpoints](./api-documentation.md)** - Documentação das views e URLs
- **[Frontend Guidelines](./frontend-guidelines.md)** - Padrões para templates e TailwindCSS

### 🔧 Configuração e Deploy
- **[Configurações](./configuration.md)** - Variáveis de ambiente e settings
- **[Testes](./testing.md)** - Como executar e escrever testes
- **[Deploy](./deployment.md)** - Guia para produção

### 📋 Referência
- **[Modelos de Dados](./data-models.md)** - Detalhes de todos os models
- **[Utilitários](./utilities.md)** - Funções helpers e ferramentas
- **[Troubleshooting](./troubleshooting.md)** - Problemas comuns e soluções

## Visão Geral do Projeto

O Finanpy é um sistema web de gestão financeira pessoal que permite aos usuários:

- 💰 **Gestão de Contas** - Cadastro e controle de contas bancárias e cartões
- 📊 **Transações** - Registro detalhado de receitas e despesas
- 🎯 **Orçamentos** - Planejamento e acompanhamento de gastos mensais
- 🏆 **Metas** - Definição e monitoramento de objetivos financeiros
- 📈 **Relatórios** - Visualização de dados através de dashboards e gráficos

## Stack Tecnológica

- **Backend**: Python 3.13+ + Django 5.2+
- **Database**: SQLite (desenvolvimento)
- **Frontend**: Django Templates + TailwindCSS + JavaScript
- **Charts**: Chart.js para visualização de dados

## Apps do Django

O projeto está organizado nos seguintes apps:

- `users` - Sistema de autenticação e usuários
- `profiles` - Perfis e informações pessoais
- `accounts` - Contas bancárias e cartões
- `categories` - Categorização de transações
- `transactions` - Registro de movimentações financeiras
- `budgets` - Planejamento orçamentário
- `goals` - Metas e objetivos financeiros

## Começando

Para começar a contribuir com o projeto:

1. Leia o **[Setup e Instalação](./setup-guide.md)**
2. Familiarize-se com os **[Padrões de Código](./coding-standards.md)**
3. Consulte a **[Arquitetura do Projeto](./architecture.md)**

## Contribuição

Este projeto segue padrões específicos de desenvolvimento. Consulte a documentação completa antes de fazer alterações no código.

---

**Versão da Documentação**: 1.0  
**Última Atualização**: Agosto 2024