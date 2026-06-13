#teste validar senha
from usuario_service import validar_senha

print(validar_senha("Senha@123"))
print(validar_senha("senha123"))



#teste verificar idade
from usuario_service import validar_idade

print(validar_idade("15/03/2000"))
print(validar_idade("01/01/2015"))
print(validar_idade("abc"))

try:
    idade = int(input("Digite sua idade: "))
    print(f"Sua idade é {idade}")

except ValueError:
    print("Você deve digitar apenas números.")



#teste cadastro usuarios
from usuario_service import cadastrar_usuario

usuarios = []

usuario = cadastrar_usuario(
    "Bruno",
    "bruno@email.com",
    "12345678900",
    "15/03/2000",
    "bruno123",
    "Senha@123",
    usuarios
)

print(usuario)
print(len(usuarios))