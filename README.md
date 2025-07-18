# Portal de Eventos da Cidade Inteligente

Um sistema em terminal para **cadastro de cidadãos**, **visualização de eventos**, **inscrição em eventos** e **relatórios gerenciais**, desenvolvido em Python com PostgreSQL.

---

## Funcionalidades Disponíveis

| Opção | Descrição |
|-------|-----------|
| 1 | **Cadastrar Novo Cidadão**: Insere um cidadão na base de dados com nome, CPF, e-mail, telefone, data de nascimento e gênero. |
| 2 | **Listar Próximos Eventos**: Exibe eventos futuros organizados pela prefeitura, incluindo vagas restantes e local. |
| 3 | **Inscrever-se em um Evento**: Permite associar um cidadão existente a um evento. Utiliza procedure `sp_registrar_participante_evento`. |
| 4 | **Relatório de Eventos Mais Populares**: Gera um ranking com base na quantidade de inscritos por evento. |
| 5 | **Sair**: Finaliza a aplicação. |

---

## Tecnologias Utilizadas

- Python 3.11+
- PostgreSQL 15+
- psycopg2 – Conector com o banco de dados
- Rich – Saída formatada no terminal

---

## Requisitos para Executar

### Python e bibliotecas:

```bash
pip install psycopg2-binary rich
````

### PostgreSQL:

* Banco de dados configurado e em execução na porta correta (ajustável no código)
* Stored procedures e funções SQL criadas previamente no banco

---

## Executando o Projeto

```bash
python portal_eventos.py
```

O script se conecta ao banco e exibe o menu interativo em terminal. A interface usa tabelas visuais com cores.

---

## Licença

Projeto acadêmico. Livre para fins educacionais.
