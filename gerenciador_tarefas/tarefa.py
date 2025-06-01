# gerenciador_tarefas/tarefa.py

import uuid

class Tarefa:
    """
    Representa uma tarefa individual no sistema.
    """
    def __init__(self, descricao, data_vencimento=None, id_tarefa=None, concluida=False):
        """
        Inicializa uma nova tarefa.

        Args:
            descricao (str): A descrição da tarefa.
            data_vencimento (str, optional): A data de vencimento da tarefa (formato YYYY-MM-DD). 
                                            Defaults to None.
            id_tarefa (str, optional): O ID único da tarefa. Se None, um novo UUID será gerado.
                                     Defaults to None.
            concluida (bool, optional): O status de conclusão da tarefa. Defaults to False.
        """
        if not descricao or not isinstance(descricao, str):
            raise ValueError("A descrição da tarefa não pode ser vazia e deve ser uma string.")

        self.id = id_tarefa if id_tarefa else str(uuid.uuid4())
        self.descricao = descricao
        self.data_vencimento = data_vencimento
        self.concluida = concluida

    def marcar_como_concluida(self):
        """Marca a tarefa como concluída."""
        self.concluida = True

    def marcar_como_pendente(self):
        """Marca a tarefa como pendente."""
        self.concluida = False

    def __str__(self):
        """
        Retorna uma representação em string da tarefa.
        """
        status = "Concluída" if self.concluida else "Pendente"
        data_str = f", Vencimento: {self.data_vencimento}" if self.data_vencimento else ""
        return f"ID: {self.id} | Descrição: {self.descricao}{data_str} | Status: {status}"

    def to_dict(self):
        """
        Converte o objeto Tarefa para um dicionário, útil para serialização JSON.
        """
        return {
            "id": self.id,
            "descricao": self.descricao,
            "data_vencimento": self.data_vencimento,
            "concluida": self.concluida,
        }

    @classmethod
    def from_dict(cls, data_dict):
        """
        Cria um objeto Tarefa a partir de um dicionário.
        """
        if not isinstance(data_dict, dict):
            raise ValueError("Os dados de entrada devem ser um dicionário.")

        # Exige as chaves obrigatórias
        obrigatorias = ["id", "descricao"]
        for chave in obrigatorias:
            if chave not in data_dict:
                raise KeyError(chave)

        return cls(
            descricao=data_dict["descricao"],
            data_vencimento=data_dict.get("data_vencimento"),
            id_tarefa=data_dict["id"],
            concluida=data_dict.get("concluida", False),
        )