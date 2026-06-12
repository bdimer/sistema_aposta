from usuario_service import validar_senha

print(validar_senha("Senha@123"))
print(validar_senha("senha123"))

from usuario_service import validar_idade

print(validar_idade("15/03/2000"))
print(validar_idade("01/01/2015"))
print(validar_idade("abc"))


try:
    idade = int(input("Digite sua idade: "))
    print(f"Sua idade é {idade}")

except ValueError:
    print("Você deve digitar apenas números.")