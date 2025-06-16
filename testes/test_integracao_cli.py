# testes/test_integracao_cli.py

import pytest
import os
import io
import json
import re
from main import main
from gerenciador_tarefas.logica import GerenciadorDeTarefas # <--- Importe a classe

# Define o nome do arquivo de teste para evitar sujar o arquivo de produção
ARQUIVO_TESTE = "tarefas_teste.json"

@pytest.fixture
def ambiente_limpo(monkeypatch):
    """
    Fixture do Pytest para garantir um ambiente limpo para cada teste.
    - Usa um arquivo JSON de teste específico.
    - Garante que o arquivo de teste seja removido antes e depois de cada teste.
    """
    # Armazena o método __init__ original
    original_init = GerenciadorDeTarefas.__init__

    # Cria um novo método __init__ que chama o original com o nome do arquivo de teste
    def patched_init(self, arquivo_json=ARQUIVO_TESTE):
        original_init(self, arquivo_json=arquivo_json)

    # Substitui o __init__ da classe pelo nosso método modificado
    monkeypatch.setattr(GerenciadorDeTarefas, '__init__', patched_init)

    # Garante que o ambiente esteja limpo ANTES do teste
    if os.path.exists(ARQUIVO_TESTE):
        os.remove(ARQUIVO_TESTE)

    yield # O teste é executado aqui

    # Limpa o ambiente DEPOIS do teste
    if os.path.exists(ARQUIVO_TESTE):
        os.remove(ARQUIVO_TESTE)

def simular_execucao(monkeypatch, inputs):
    """
    Função auxiliar para simular a execução do CLI com uma série de inputs.
    """
    input_str = "\n".join(inputs)
    monkeypatch.setattr('sys.stdin', io.StringIO(input_str))
    
    captured_output = io.StringIO()
    monkeypatch.setattr('sys.stdout', captured_output)
    
    try:
        main()
    except SystemExit:
        pass
        
    return captured_output.getvalue()

# --- Testes de Integração (sem alterações a partir daqui) ---

def test_e2e_adicionar_e_visualizar_tarefa(ambiente_limpo, monkeypatch):
    """
    TESTE 1: Simula o usuário adicionando uma nova tarefa e depois visualizando-a.
    Verifica se a tarefa aparece na lista com o status "Pendente".
    """
    inputs = ["1", "Pagar a conta de luz", "", "2", "5"]
    output = simular_execucao(monkeypatch, inputs)
    
    assert "Tarefa 'Pagar a conta de luz' adicionada com sucesso." in output
    assert "Descrição: Pagar a conta de luz" in output
    assert "Status: Pendente" in output
    assert "Saindo do Gerenciador de Tarefas" in output

def test_e2e_adicionar_e_concluir_tarefa(ambiente_limpo, monkeypatch):
    """
    TESTE 2: Simula o usuário adicionando uma tarefa, visualizando-a como pendente,
    marcando-a como concluída e visualizando-a novamente com o status atualizado.
    """
    inputs_iniciais = ["1", "Comprar café", "2025-10-20", "2", "5"]
    output_inicial = simular_execucao(monkeypatch, inputs_iniciais)
    
    match = re.search(r"ID: ([\w-]+)", output_inicial)
    assert match, "Não foi possível encontrar o ID da tarefa na saída"
    id_tarefa = match.group(1)
    
    inputs_finais = ["3", id_tarefa, "2", "5"]
    output_final = simular_execucao(monkeypatch, inputs_finais)

    assert "Tarefa 'Comprar café' marcada como concluída." in output_final
    assert f"ID: {id_tarefa}" in output_final
    assert "Descrição: Comprar café" in output_final
    assert "Vencimento: 2025-10-20" in output_final
    assert "Status: Concluída" in output_final

def test_e2e_remover_tarefa(ambiente_limpo, monkeypatch):
    """
    TESTE 3: Simula o usuário adicionando duas tarefas e removendo uma delas.
    Verifica se a tarefa correta foi removida e a outra permaneceu.
    """
    # Adiciona "Tarefa A" e "Tarefa B" em uma primeira execução
    simular_execucao(monkeypatch, ["1", "Tarefa A", "", "1", "Tarefa B", "", "5"])
    
    # Carrega o JSON para pegar o ID da tarefa a ser removida
    with open(ARQUIVO_TESTE, 'r') as f:
        tarefas = json.load(f)
    
    id_tarefa_a = next(t['id'] for t in tarefas if t['descricao'] == 'Tarefa A')
    
    # Executa a remoção e a visualização
    inputs_remover = ["4", id_tarefa_a, "2", "5"]
    output = simular_execucao(monkeypatch, inputs_remover)
    
    # Verifica se a mensagem de sucesso da remoção foi exibida
    assert "Tarefa 'Tarefa A' removida com sucesso." in output
    
    # CORREÇÃO: Verifica a ausência da linha de descrição específica da "Tarefa A"
    # e a presença da linha de descrição da "Tarefa B" na listagem final.
    assert "Descrição: Tarefa A" not in output
    assert "Descrição: Tarefa B" in output

def test_e2e_persistencia_de_dados_entre_sessoes(ambiente_limpo, monkeypatch):
    """
    TESTE 4: Verifica se os dados persistem entre diferentes execuções do programa.
    """
    simular_execucao(monkeypatch, ["1", "Lembrar de testar a persistência", "", "5"])
    
    assert os.path.exists(ARQUIVO_TESTE)
    with open(ARQUIVO_TESTE, 'r') as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]['descricao'] == "Lembrar de testar a persistência"

    output_sessao_2 = simular_execucao(monkeypatch, ["2", "5"])
    
    assert "Tarefas carregadas de tarefas_teste.json" in output_sessao_2
    assert "Lembrar de testar a persistência" in output_sessao_2
    assert "Status: Pendente" in output_sessao_2

def test_e2e_menu_opcao_invalida(ambiente_limpo, monkeypatch):
    """
    TESTE 5: Simula o usuário digitando uma opção inválida no menu.
    """
    inputs = ["9", "5"]
    output = simular_execucao(monkeypatch, inputs)
    
    assert "Opção inválida. Por favor, tente novamente." in output
    assert output.count("--- Gerenciador de Tarefas ---") == 2