'''
Módulo nester.py contendo uma função print_nlist()
que imprime listas que podem ou não ter listas
aninhadas, imprimindo-as caso as tenha, e oferecendo
uma opção de tabulação para cada nível.
Uso:
print_nlist(LISTA,[True],[tabs])
Onde:
  LISTA é o nome da lista a ser passada
  [True] é a condição de exibir tabulações, padrão=False
  [tabs] é o número de espaços a serem exibidos antes
         de cada nível.
'''

def print_nlist(a_list, indent=False, level=0):
    for each_item in a_list:
        if isinstance(each_item, list):
            print_nlist(each_item, indent, level+1)
        else:
            if indent:
                    print('  '*level, end='')
            print(each_item)

            
