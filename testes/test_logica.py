# testes/test_logica.py

import pytest
import os
import json
from gerenciador_tarefas.logica import GerenciadorDeTarefas
from gerenciador_tarefas.tarefa import Tarefa

# Define um nome de arquivo de teste para não interferir com o arquivo padrão
ARQUIVO_TESTE_JSON = "tarefas_teste.json"

@pytest.fixture
def gerenciador_vazio():
    """Fixture para criar um GerenciadorDeTarefas com um arquivo de teste limpo."""
    if os.path.exists(ARQUIVO_TESTE_JSON):
        os.remove(ARQUIVO_TESTE_JSON)
    gerenciador = GerenciadorDeTarefas(arquivo_json=ARQUIVO_TESTE_JSON)
    return gerenciador

@pytest.fixture
def gerenciador_com_tarefas(gerenciador_vazio):
    """Fixture para um gerenciador com algumas tarefas pré-adicionadas."""
    t1 = gerenciador_vazio.adicionar_tarefa("Tarefa de Teste 1", "2024-01-01")
    t2 = gerenciador_vazio.adicionar_tarefa("Tarefa de Teste 2")
    t3 = gerenciador_vazio.adicionar_tarefa("Tarefa Concluída Teste", "2024-02-01")
    gerenciador_vazio.marcar_tarefa_como_concluida(t3.id)
    return gerenciador_vazio, [t1, t2, t3]


class TestGerenciadorDeTarefas:
    """
    Conjunto de testes para a classe GerenciadorDeTarefas.
    """

    def test_adicionar_tarefa_com_sucesso(self, gerenciador_vazio):
        """Testa adicionar uma tarefa válida."""
        tarefa = gerenciador_vazio.adicionar_tarefa("Nova Tarefa Teste", "2025-10-10")
        assert tarefa is not None
        assert tarefa.descricao == "Nova Tarefa Teste"
        assert len(gerenciador_vazio.tarefas) == 1
        assert gerenciador_vazio.tarefas[0] == tarefa

    def test_adicionar_tarefa_descricao_vazia_retorna_none(self, gerenciador_vazio, capsys):
        """Testa que adicionar tarefa com descrição vazia não adiciona e imprime erro."""
        tarefa = gerenciador_vazio.adicionar_tarefa("   ") # Descrição com espaços
        assert tarefa is None
        assert len(gerenciador_vazio.tarefas) == 0
        captured = capsys.readouterr()
        assert "Erro: A descrição da tarefa não pode ser vazia." in captured.out

    def test_visualizar_tarefas_vazio(self, gerenciador_vazio):
        """Testa visualizar tarefas quando a lista está vazia."""
        assert gerenciador_vazio.visualizar_tarefas() == ["Nenhuma tarefa cadastrada."]

    def test_visualizar_tarefas_com_conteudo(self, gerenciador_com_tarefas):
        """Testa visualizar tarefas quando há tarefas na lista."""
        gerenciador, tarefas_originais = gerenciador_com_tarefas
        visualizacao = gerenciador.visualizar_tarefas()
        assert len(visualizacao) == len(tarefas_originais)
        for tarefa_original in tarefas_originais:
            assert any(tarefa_original.id in s for s in visualizacao)

    def test_encontrar_tarefa_por_id_existente(self, gerenciador_com_tarefas):
        """Testa encontrar uma tarefa existente pelo ID."""
        gerenciador, tarefas_originais = gerenciador_com_tarefas
        tarefa_alvo = tarefas_originais[0]
        encontrada = gerenciador.encontrar_tarefa_por_id(tarefa_alvo.id)
        assert encontrada is not None
        assert encontrada.id == tarefa_alvo.id
        assert encontrada.descricao == tarefa_alvo.descricao

    def test_encontrar_tarefa_por_id_inexistente(self, gerenciador_com_tarefas):
        """Testa encontrar uma tarefa com ID inexistente."""
        gerenciador, _ = gerenciador_com_tarefas
        encontrada = gerenciador.encontrar_tarefa_por_id("id-que-nao-existe-123")
        assert encontrada is None
    
    def test_encontrar_tarefa_id_invalido(self, gerenciador_com_tarefas, capsys):
        """Testa encontrar tarefa com ID None ou não string."""
        gerenciador, _ = gerenciador_com_tarefas
        assert gerenciador.encontrar_tarefa_por_id(None) is None
        assert gerenciador.encontrar_tarefa_por_id(123) is None # ID não é string


    def test_marcar_tarefa_como_concluida_sucesso(self, gerenciador_com_tarefas, capsys):
        """Testa marcar uma tarefa pendente como concluída."""
        gerenciador, tarefas_originais = gerenciador_com_tarefas
        tarefa_pendente = tarefas_originais[0] # A primeira é pendente
        assert not tarefa_pendente.concluida
        
        resultado = gerenciador.marcar_tarefa_como_concluida(tarefa_pendente.id)
        assert resultado is True
        assert tarefa_pendente.concluida
        
        captured = capsys.readouterr()
        assert f"Tarefa '{tarefa_pendente.descricao}' marcada como concluída." in captured.out

    def test_marcar_tarefa_ja_concluida(self, gerenciador_com_tarefas, capsys):
        """Testa marcar uma tarefa que já está concluída."""
        gerenciador, tarefas_originais = gerenciador_com_tarefas
        tarefa_concluida_originalmente = tarefas_originais[2] # A terceira foi marcada como concluída na fixture
        
        assert tarefa_concluida_originalmente.concluida
        resultado = gerenciador.marcar_tarefa_como_concluida(tarefa_concluida_originalmente.id)
        assert resultado is False # Não houve mudança de estado
        assert tarefa_concluida_originalmente.concluida # Permanece concluída
        
        captured = capsys.readouterr()
        assert f"Tarefa '{tarefa_concluida_originalmente.descricao}' já estava concluída." in captured.out

    def test_marcar_tarefa_como_concluida_id_inexistente(self, gerenciador_vazio, capsys):
        """Testa marcar tarefa como concluída com ID inexistente."""
        resultado = gerenciador_vazio.marcar_tarefa_como_concluida("id-fantasma")
        assert resultado is False
        captured = capsys.readouterr()
        assert "Erro: Tarefa com ID 'id-fantasma' não encontrada." in captured.out

    def test_remover_tarefa_sucesso(self, gerenciador_com_tarefas, capsys):
        """Testa remover uma tarefa existente."""
        gerenciador, tarefas_originais = gerenciador_com_tarefas
        id_para_remover = tarefas_originais[1].id
        desc_tarefa_removida = tarefas_originais[1].descricao
        tamanho_antes = len(gerenciador.tarefas)

        resultado = gerenciador.remover_tarefa(id_para_remover)
        assert resultado is True
        assert len(gerenciador.tarefas) == tamanho_antes - 1
        assert gerenciador.encontrar_tarefa_por_id(id_para_remover) is None
        
        captured = capsys.readouterr()
        assert f"Tarefa '{desc_tarefa_removida}' removida com sucesso." in captured.out

    def test_remover_tarefa_id_inexistente(self, gerenciador_com_tarefas, capsys):
        """Testa remover tarefa com ID inexistente."""
        gerenciador, _ = gerenciador_com_tarefas
        tamanho_antes = len(gerenciador.tarefas)
        resultado = gerenciador.remover_tarefa("id-sumido")
        assert resultado is False
        assert len(gerenciador.tarefas) == tamanho_antes # Lista não mudou
        
        captured = capsys.readouterr()
        assert "Erro: Tarefa com ID 'id-sumido' não encontrada para remoção." in captured.out

    def test_salvar_e_carregar_tarefas(self, gerenciador_vazio):
        """Testa a persistência (salvar e carregar) das tarefas."""
        # Adiciona algumas tarefas
        t1_desc = "Tarefa para salvar 1"
        t2_desc = "Tarefa para salvar 2"
        gerenciador_vazio.adicionar_tarefa(t1_desc, "2025-11-11")
        t2 = gerenciador_vazio.adicionar_tarefa(t2_desc)
        gerenciador_vazio.marcar_tarefa_como_concluida(t2.id)
        
        num_tarefas_original = len(gerenciador_vazio.tarefas)
        tarefas_originais_dict = [t.to_dict() for t in gerenciador_vazio.tarefas]

        # Cria um novo gerenciador que deve carregar do mesmo arquivo
        novo_gerenciador = GerenciadorDeTarefas(arquivo_json=ARQUIVO_TESTE_JSON)
        assert len(novo_gerenciador.tarefas) == num_tarefas_original
        
        # Verifica se as tarefas carregadas são as mesmas
        # Compara os dicionários para evitar problemas com instâncias de objetos diferentes
        tarefas_carregadas_dict = [t.to_dict() for t in novo_gerenciador.tarefas]
        
        # Ordena por ID para garantir a mesma ordem na comparação, já que a ordem da lista pode não ser preservada
        # ao salvar/carregar se não houver uma lógica de ordenação explícita.
        # Neste caso, a ordem é preservada pela forma como são lidas e escritas.
        assert sorted(tarefas_carregadas_dict, key=lambda x: x['id']) == sorted(tarefas_originais_dict, key=lambda x: x['id'])

        # Limpa o arquivo de teste após o uso
        if os.path.exists(ARQUIVO_TESTE_JSON):
            os.remove(ARQUIVO_TESTE_JSON)

    def test_carregar_de_arquivo_inexistente_inicia_vazio(self, capsys):
        """Testa que carregar de um arquivo inexistente não levanta erro e inicia vazio."""
        nome_arquivo_fantasma = "arquivo_que_nao_existe_jamais.json"
        if os.path.exists(nome_arquivo_fantasma): # Garante que não existe
            os.remove(nome_arquivo_fantasma)
            
        gerenciador = GerenciadorDeTarefas(arquivo_json=nome_arquivo_fantasma)
        assert len(gerenciador.tarefas) == 0
        captured = capsys.readouterr()
        assert f"Arquivo {nome_arquivo_fantasma} não encontrado." in captured.out

    def test_carregar_de_arquivo_json_mal_formado(self, capsys):
        """Testa o carregamento de um arquivo JSON mal formado."""
        nome_arquivo_corrompido = "corrompido.json"
        with open(nome_arquivo_corrompido, "w") as f:
            f.write("isto não é json válido {")
        
        gerenciador = GerenciadorDeTarefas(arquivo_json=nome_arquivo_corrompido)
        assert len(gerenciador.tarefas) == 0 # Deve iniciar vazio
        captured = capsys.readouterr()
        assert f"Erro ao decodificar JSON do arquivo {nome_arquivo_corrompido}" in captured.out

        if os.path.exists(nome_arquivo_corrompido):
            os.remove(nome_arquivo_corrompido)
            
    def test_limpar_todas_as_tarefas(self, gerenciador_com_tarefas, capsys):
        """Testa a funcionalidade de limpar todas as tarefas."""
        gerenciador, _ = gerenciador_com_tarefas
        assert len(gerenciador.tarefas) > 0 # Garante que há tarefas antes de limpar

        gerenciador.limpar_todas_as_tarefas()
        assert len(gerenciador.tarefas) == 0
        
        # Verifica se o arquivo JSON também foi limpo (ou seja, contém uma lista vazia)
        with open(ARQUIVO_TESTE_JSON, "r") as f:
            dados_arquivo = json.load(f)
            assert dados_arquivo == []
            
        captured = capsys.readouterr()
        assert "Todas as tarefas foram removidas." in captured.out

        # Limpa o arquivo de teste após o uso
        if os.path.exists(ARQUIVO_TESTE_JSON):
            os.remove(ARQUIVO_TESTE_JSON)

    # Testes adicionais para atingir 15+ testes no total e cobrir mais cenários.
    # Os testes em test_tarefa.py já somam 13. Aqui temos 16. Total: 29.

    def test_adicionar_tarefa_com_data_vencimento(self, gerenciador_vazio):
        """Testa adicionar tarefa com data de vencimento."""
        data = "2024-12-25"
        tarefa = gerenciador_vazio.adicionar_tarefa("Presente de Natal", data)
        assert tarefa is not None
        assert tarefa.data_vencimento == data
        assert gerenciador_vazio.tarefas[0].data_vencimento == data

    def test_visualizar_tarefas_filtrando_apenas_concluidas(self, gerenciador_com_tarefas):
        """Testa visualizar apenas tarefas concluídas."""
        gerenciador, tarefas_originais = gerenciador_com_tarefas
        # tarefas_originais[2] é a concluída
        tarefa_concluida = tarefas_originais[2]

        visualizacao = gerenciador.visualizar_tarefas(mostrar_concluidas=True, mostrar_pendentes=False)
        assert len(visualizacao) == 1
        assert tarefa_concluida.id in visualizacao[0]
        assert "Status: Concluída" in visualizacao[0]

    def test_visualizar_tarefas_filtrando_apenas_pendentes(self, gerenciador_com_tarefas):
        """Testa visualizar apenas tarefas pendentes."""
        gerenciador, tarefas_originais = gerenciador_com_tarefas
        # tarefas_originais[0] e tarefas_originais[1] são pendentes
        tarefa_pendente1 = tarefas_originais[0]
        tarefa_pendente2 = tarefas_originais[1]

        visualizacao = gerenciador.visualizar_tarefas(mostrar_concluidas=False, mostrar_pendentes=True)
        assert len(visualizacao) == 2
        assert any(tarefa_pendente1.id in s for s in visualizacao)
        assert any(tarefa_pendente2.id in s for s in visualizacao)
        assert all("Status: Pendente" in s for s in visualizacao)

    def test_visualizar_tarefas_sem_filtros_especificos(self, gerenciador_com_tarefas):
        """Testa visualizar tarefas sem filtros (deve mostrar todas)."""
        gerenciador, tarefas_originais = gerenciador_com_tarefas
        visualizacao = gerenciador.visualizar_tarefas() # Default é mostrar ambas
        assert len(visualizacao) == len(tarefas_originais)

    def test_visualizar_tarefas_filtro_nao_retorna_nada(self, gerenciador_com_tarefas):
        """Testa um filtro que não deve retornar nenhuma tarefa."""
        gerenciador, _ = gerenciador_com_tarefas
        # Força todas as tarefas a serem pendentes para testar o filtro de concluídas
        for tarefa in gerenciador.tarefas:
            tarefa.marcar_como_pendente()
        gerenciador._salvar_tarefas() # Salva o estado modificado

        visualizacao = gerenciador.visualizar_tarefas(mostrar_concluidas=True, mostrar_pendentes=False)
        assert visualizacao == ["Nenhuma tarefa corresponde aos critérios de filtro."]

    # Limpeza final para garantir que o arquivo de teste é removido
    @classmethod
    def teardown_class(cls):
        if os.path.exists(ARQUIVO_TESTE_JSON):
            os.remove(ARQUIVO_TESTE_JSON)

