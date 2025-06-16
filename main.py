# main.py

from gerenciador_tarefas.logica import GerenciadorDeTarefas

def adicionar_tarefa(gerenciador):
    descricao = input("Digite a descrição da tarefa: ")
    data_vencimento = input("Digite a data de vencimento (YYYY-MM-DD, opcional, deixe em branco se não houver): ")
    data_vencimento = data_vencimento if data_vencimento.strip() else None
    gerenciador.adicionar_tarefa(descricao, data_vencimento)

def visualizar_tarefas(gerenciador):
    print("\n--- Lista de Tarefas ---")
    tarefas_str = gerenciador.visualizar_tarefas()
    if tarefas_str:
        for t_str in tarefas_str:
            print(t_str)
    else:
        print("Nenhuma tarefa para exibir.")
    print("------------------------")

def marcar_tarefa_como_concluida(gerenciador):
    id_tarefa = input("Digite o ID da tarefa a ser marcada como concluída: ")
    gerenciador.marcar_tarefa_como_concluida(id_tarefa)

def remover_tarefa(gerenciador):
    id_tarefa = input("Digite o ID da tarefa a ser removida: ")
    gerenciador.remover_tarefa(id_tarefa)

def exibir_menu():
    """Exibe o menu de opções para o usuário."""
    print("\n--- Gerenciador de Tarefas ---")
    print("1. Adicionar Tarefa")
    print("2. Visualizar Tarefas")
    print("3. Marcar Tarefa como Concluída")
    print("4. Remover Tarefa")
    print("5. Sair")
    print("------------------------------")

def main():
    """Função principal que executa o loop da aplicação CLI."""
    gerenciador = GerenciadorDeTarefas()
    
    # CORREÇÃO: Removido o uso de lambdas desnecessárias.
    # Agora o dicionário armazena as funções diretamente.
    opcoes = {
        "1": adicionar_tarefa,
        "2": visualizar_tarefas,
        "3": marcar_tarefa_como_concluida,
        "4": remover_tarefa,
    }

    while True:
        exibir_menu()
        escolha = input("Escolha uma opção: ")

        if escolha == "5":
            print("Saindo do Gerenciador de Tarefas. Até logo!")
            break
        
        acao = opcoes.get(escolha)
        if acao:
            # A chamada agora funciona, pois passamos o 'gerenciador'
            # para a função correta (ex: adicionar_tarefa).
            acao(gerenciador)
        else:
            # A opção "5" não está no dicionário, então o 'get' retorna None.
            # O caso de opção inválida é tratado aqui.
            if escolha != "5":
                print("Opção inválida. Por favor, tente novamente.")

if __name__ == "__main__":
    main()