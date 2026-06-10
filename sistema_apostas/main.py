from usuario import Usuario

usuario = Usuario(
    nome="João",
    email="joao@email.com",
    cpf="12345678900",
    data_nascimento="01/01/1990",
    login="joao123",
    senha="Senha@123"
)

print(usuario.nome)
print(usuario.pontos)
print(usuario.status)