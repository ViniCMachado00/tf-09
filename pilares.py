# Os pilares na árvore de arquivos: herança, polimorfismo, abstração e interface.
# Rodar no terminal: python3 pilares.py
#
# O Item da Aula 08 tinha um booleano (eh_pasta) e vários "if eh_pasta".
# Aqui ele vira três classes: Item (o geral), Pasta e Arquivo (os específicos),
# e quem usa a árvore deixa de perguntar "você é pasta?".
from abc import ABC, abstractmethod


# INTERFACE: contrato puro, sem estado e sem implementação.
# Quem assina promete saber dizer o próprio tamanho em bytes.
class Medivel(ABC):
    __slots__ = ()

    @abstractmethod
    def tamanho(self):
        pass


# ABSTRAÇÃO + HERANÇA: o que toda pasta e todo arquivo têm em comum.
# Não dá para criar um Item "solto": ele é só o recorte do essencial.
class Item(Medivel):
    __slots__ = ("__nome", "__pai")

    def __init__(self, nome, pai=None):
        self.__validar_nome(nome)
        self.__nome = nome
        self.__pai = None

        if pai is not None:
            self.mover_para(pai)

    def __validar_nome(self, nome):
        if nome == "" or "/" in nome:
            raise ValueError("nome inválido: " + repr(nome))

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, novo_nome):
        self.__validar_nome(novo_nome)
        self.__nome = novo_nome

    @property
    def pai(self):
        return self.__pai

    def mover_para(self, destino):
        if destino is self.__pai:
            return

        destino._receber(self)          # cada tipo decide se aceita
        if self.__pai is not None:
            self.__pai._soltar(self)
        self.__pai = destino

    # PROTEGIDO: o gancho que as filhas sobrescrevem. Por padrão, recusa.
    def _receber(self, item):
        raise ValueError(self.__nome + " é um arquivo, não pode conter itens")

    def caminho(self):
        if self.__pai is None:
            return self.__nome
        return self.__pai.caminho() + "/" + self.__nome

    def profundidade(self):
        if self.__pai is None:
            return 0
        return self.__pai.profundidade() + 1

    @abstractmethod
    def mostrar(self):
        pass


class Arquivo(Item):
    __slots__ = ("__bytes",)

    def __init__(self, nome, tamanho_bytes, pai=None):
        if tamanho_bytes < 0:
            raise ValueError("tamanho não pode ser negativo")
        self.__bytes = tamanho_bytes
        super().__init__(nome, pai)

    def tamanho(self):
        return self.__bytes

    def mostrar(self):
        recuo = "    " * self.profundidade()
        print(recuo + self.nome + " (" + str(self.tamanho()) + " B)")


class Pasta(Item):
    __slots__ = ("__filhos",)

    def __init__(self, nome, pai=None):
        self.__filhos = []
        super().__init__(nome, pai)

    @property
    def filhos(self):
        return tuple(self.__filhos)

    # OVERRIDE do gancho protegido: a pasta aceita, desde que não crie um ciclo.
    def _receber(self, item):
        ancestral = self
        while ancestral is not None:
            if ancestral is item:
                raise ValueError("não dá para mover " + item.nome + " para dentro dela mesma")
            ancestral = ancestral.pai
        self.__filhos.append(item)

    def _soltar(self, item):
        self.__filhos.remove(item)

    # POLIMORFISMO: a pasta soma o que tem dentro; nenhum filho é perguntado
    # se é pasta ou arquivo, cada um responde do seu jeito.
    def tamanho(self):
        total = 0
        for filho in self.__filhos:
            total = total + filho.tamanho()
        return total

    def mostrar(self):
        recuo = "    " * self.profundidade()
        print(recuo + self.nome + "/ (" + str(self.tamanho()) + " B)")
        for filho in self.__filhos:
            filho.mostrar()

# HERANÇA: representa um item que aponta para outro item da árvore.
class Atalho(Item):
    __slots__ = ("__destino",)

    def __init__(self, nome, destino, pai=None):
        """Cria o atalho e valida o destino usando redirecionar."""
        self.__destino = None
        super().__init__(nome, pai)
        self.redirecionar(destino)

    @property
    def destino(self):
        """Permite consultar o destino sem alterá-lo diretamente."""
        return self.__destino

    def redirecionar(self, novo_destino):
        """Troca o destino somente se ele não criar uma referência proibida."""
        if novo_destino is self:
            raise ValueError("um atalho não pode apontar para si mesmo")

        ancestral = self.pai
        while ancestral is not None:
            if novo_destino is ancestral:
                raise ValueError(
                    "um atalho não pode apontar para uma pasta ancestral"
                )
            ancestral = ancestral.pai

        self.__destino = novo_destino

    def tamanho(self):
        """Retorna um byte, independentemente do tamanho do destino."""
        return 1

    def mostrar(self):
        """Mostra o nome do atalho e o caminho do item de destino."""
        recuo = "    " * self.profundidade()
        print(recuo + self.nome + " -> " + self.destino.caminho())

# Outra classe que assina o contrato SEM ser da árvore: a Lixeira.
class Lixeira(Medivel):
    __slots__ = ("__descartados",)

    def __init__(self):
        self.__descartados = []

    def descartar(self, arquivo):
        self.__descartados.append(arquivo)

    def tamanho(self):
        total = 0
        for arquivo in self.__descartados:
            total = total + arquivo.tamanho()
        return total


# Quem usa o contrato não sabe (nem quer saber) quem está do outro lado.
def espaco_total(coisas):
    total = 0
    for coisa in coisas:
        total = total + coisa.tamanho()
    return total


def tentar(rotulo, acao):
    try:
        acao()
        print(rotulo, "-> passou (!)")
    except Exception as erro:
        print(rotulo, "->", type(erro).__name__ + ":", erro)
        

# TESTES: monta uma árvore com arquivos, pastas e atalhos.
disco = Pasta("C:")
usuarios = Pasta("Users", disco)
vinicius = Pasta("vinicius", usuarios)
desktop = Pasta("Desktop", vinicius)
trabalhos = Pasta("Trabalhos", desktop)

notas = Arquivo("notas.txt", 120, desktop)
slide = Arquivo("slide.pdf", 5000, trabalhos)
resumo = Arquivo("resumo.txt", 300, trabalhos)

atalho_arquivo = Atalho("atalho_notas", notas, desktop)
pasta_com_atalho = Pasta("PastaComAtalho", desktop)
atalho_pasta = Atalho("atalho_trabalhos", trabalhos, pasta_com_atalho)

lixeira = Lixeira()
lixeira.descartar(Arquivo("descartado.txt", 50))

# Exibe a árvore completa.
print("\nÁrvore com atalhos:")
disco.mostrar()

# Soma um arquivo, uma pasta com atalho e uma lixeira.
print("\nEspaço total:", espaco_total([
    notas,
    pasta_com_atalho,
    lixeira
]))

# Testes que devem falhar.
tentar(
    "Alterar destino diretamente",
    lambda: setattr(atalho_arquivo, "destino", resumo)
)

tentar(
    "Atalho apontando para si mesmo",
    lambda: atalho_arquivo.redirecionar(atalho_arquivo)
)

tentar(
    "Atalho apontando para a pasta que o contém",
    lambda: atalho_pasta.redirecionar(pasta_com_atalho)
)