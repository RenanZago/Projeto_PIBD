import psycopg2
import psycopg2.extras
import datetime
from rich.console import Console
from rich.table import Table
from rich import box 

def conectar_banco():
    """
    Estabelece a conexão com o banco de dados PostgreSQL.
    """
    try:
        conexao = psycopg2.connect(
            dbname="postgres",
            user="postgres", 
            password="admin",
            host="localhost",
            port="5433"
        )
        print("Conexão com o banco de dados PostgreSQL bem-sucedida!")
        return conexao
    except psycopg2.OperationalError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def cadastrar_cidadao(conexao):
    """
    Funcionalidade 1: Cadastra um novo cidadão no sistema.
    """
    print("\n--- Cadastro de Novo Cidadão ---")
    try:
        nome = input("Digite o nome completo: ")
        telefone = input("Digite o telefone (opcional): ")
        email = input("Digite o e-mail: ")
        cpf = input("Digite o CPF (apenas números): ")
        genero = input("Digite o gênero: ")
        data_nasc_str = input("Digite a data de nascimento (DD/MM/AAAA): ")

        try:
            data_obj = datetime.datetime.strptime(data_nasc_str, '%d/%m/%Y')
            data_nasc_formatada = data_obj.strftime('%Y-%m-%d')
        except ValueError:
            print("\nERRO: Formato de data inválido. Use DD/MM/AAAA. Cadastro cancelado.")
            return

        with conexao.cursor() as cursor:
            sql_pessoa = """
                INSERT INTO public.pessoa (nome, telefone, email, cpf_cnpj, tipo)
                VALUES (%s, %s, %s, %s, 'CIDADAO')
                RETURNING id;
            """
            cursor.execute(sql_pessoa, (nome, telefone, email, cpf))
            pessoa_id = cursor.fetchone()[0]
            print(f"Registro criado na tabela 'pessoa' com ID: {pessoa_id}")

            sql_cidadao = """
                INSERT INTO public.cidadao (pessoa_id, data_nasc, genero)
                VALUES (%s, %s, %s);
            """
            cursor.execute(sql_cidadao, (pessoa_id, data_nasc_formatada, genero))
            
            conexao.commit()
            print("\nCidadão cadastrado com sucesso!")

    except psycopg2.Error as e:
        conexao.rollback()
        print(f"\nErro ao cadastrar cidadão: {e}")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")

def listar_eventos(conexao):
    """
    Funcionalidade 2: Lista eventos futuros usando uma tabela formatada com a biblioteca rich.
    """
    print("\n--- Próximos Eventos ---")
    try:
        with conexao.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            consulta = """
                SELECT 
                    e.id,
                    e.nome,
                    e.descricao,
                    e.data,
                    e.tipo,
                    e.preco,
                    e.capacidade,
                    l.nome AS nome_local,
                    fn_verificar_vagas_evento(e.id) AS vagas_restantes
                FROM public.evento e
                JOIN public.local l ON e.local_id = l.id
                WHERE e.data > NOW()
                ORDER BY e.data;
            """
            cursor.execute(consulta)
            eventos = cursor.fetchall()

            if not eventos:
                print("Nenhum evento futuro encontrado.")
                return

            console = Console()
            table = Table(
                title="📅 Eventos Futuros - Portal da Cultura",
                box=box.ROUNDED,
                style="cyan",
                header_style="bold white on blue"
            )

            table.add_column("ID", justify="center", style="bold")
            table.add_column("Nome do Evento", style="yellow")
            table.add_column("Data", justify="center")
            table.add_column("Vagas", justify="center", style="green")
            table.add_column("Local", style="magenta")

            for e in eventos:
                data_fmt = e["data"].strftime("%d/%m/%Y %H:%M")
                table.add_row(
                    str(e["id"]),
                    e["nome"],
                    data_fmt,
                    str(e["vagas_restantes"]),
                    e["nome_local"]
                )
            
            console.print(table)

    except Exception as erro:
        print(f"Erro ao listar eventos: {erro}")

def inscrever_em_evento(conexao):
    """
    Funcionalidade 3: Inscreve um cidadão em um evento.
    """
    print("\n--- Inscrição em Evento ---")
    
    listar_eventos(conexao)
    
    try:
        evento_id = int(input("\nDigite o ID do evento para inscrição: "))

        with conexao.cursor() as cursor:
            print("\nCidadãos Cadastrados:")
            cursor.execute("SELECT id, nome FROM public.pessoa WHERE tipo = 'CIDADAO' ORDER BY nome;")
            cidadaos = cursor.fetchall()
            
            if not cidadaos:
                print("Nenhum cidadão cadastrado no sistema.")
                return
            
            print(f"{'ID':<5} | {'Nome':<40}")
            print("-" * 50)
            for cid_id, nome in cidadaos:
                print(f"{cid_id:<5} | {nome:<40}")

            cidadao_id = int(input("\nDigite o ID do cidadão que deseja inscrever: "))
            ingresso = "Pista Padrão"

            print("\nConfigurando a sessão para a inscrição...")
            cursor.execute("SET search_path TO public;")
            
            print(f"Tentando inscrever o cidadão {cidadao_id} no evento {evento_id}...")
            cursor.execute("CALL sp_registrar_participante_evento(%s, %s, %s);", (cidadao_id, evento_id, ingresso))
            
            conexao.commit()
            
            for notice in conexao.notices:
                print(f"\nAVISO DO BANCO: {notice.strip()}")
            conexao.notices.clear()

    except psycopg2.Error as e:
        conexao.rollback()
        print(f"\nERRO NA INSCRIÇÃO: {e}")
    except (ValueError, TypeError):
        print("\nERRO: ID do cidadão e do evento devem ser números inteiros.")
    except Exception as e:
        conexao.rollback()
        print(f"\nOcorreu um erro inesperado: {e}")

def relatorio_eventos_populares(conexao):
    """
    Funcionalidade 4: Gera um relatório de eventos ordenados por popularidade.
    (Versão do amigo integrada e adaptada)
    """
    print("\n--- Relatório Gerencial: Eventos Mais Populares ---")
    try:
        with conexao.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            
            consulta = """
            SELECT 
                e.id,
                e.nome,
                COUNT(ep.cidadao_id) AS total_inscritos
            FROM public.evento e
            LEFT JOIN public.evento_participante ep ON ep.evento_id = e.id
            GROUP BY e.id
            ORDER BY total_inscritos DESC;
            """

            cursor.execute(consulta)
            relatorio = cursor.fetchall()

            if not relatorio:
                print("Nenhum evento encontrado para gerar o relatório.")
                return

            console = Console()
            table = Table(
                title="📈 Relatório Gerencial - Eventos Mais Populares",
                box=box.ROUNDED,
                style="cyan",
                header_style="bold white on magenta"
            )

            table.add_column("Rank", justify="center", style="bold green")
            table.add_column("ID do Evento", justify="center")
            table.add_column("Nome do Evento", style="yellow")
            table.add_column("Total de Inscritos", justify="right", style="bold")

            for i, evento in enumerate(relatorio, start=1):
                table.add_row(
                    str(i),
                    str(evento["id"]),
                    evento["nome"],
                    str(evento["total_inscritos"])
                )

            console.print(table)

    except Exception as erro:
        print("Erro ao gerar relatório:", erro)


def main():
    """
    Função principal que exibe o menu e gerencia a execução.
    """
    conexao = conectar_banco()
    if not conexao:
        return

    try:
        while True:
            print("\n" + "="*12 + " Portal de Eventos da Cidade Inteligente " + "="*12)
            print("1. Cadastrar Novo Cidadão")
            print("2. Listar Próximos Eventos")
            print("3. Inscrever-se em um Evento")
            print("4. Relatório de Eventos Mais Populares")
            print("5. Sair")
            
            escolha = input("Escolha uma opção: ")

            if escolha == '1':
                cadastrar_cidadao(conexao)
            elif escolha == '2':
                listar_eventos(conexao)
            elif escolha == '3':
                inscrever_em_evento(conexao)
            elif escolha == '4':
                relatorio_eventos_populares(conexao)
            elif escolha == '5':
                print("Saindo do sistema...")
                break
            else:
                print("Opção inválida. Tente novamente.")
            
            input("\nPressione Enter para continuar...")

    finally:
        if conexao:
            conexao.close()
            print("\nConexão com o banco de dados fechada.")

if __name__ == "__main__":
    main()