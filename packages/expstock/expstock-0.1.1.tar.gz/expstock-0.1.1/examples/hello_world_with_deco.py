from expstock import expstock
import os

e = expstock.ExpStock(report=True, dbsave=True)
@expstock.expstock(e)
def hello_world(name, message, e):
    print('Hello {}'.format(name))
    print(e.log_dirname)
    my_model = os.path.join(e.log_dirname, 'my_model')
    with open(my_model, 'w') as f:
        f.write('モデルの保存')
    return message

name = 'Chie'
message = 'Nice to meet you!'
e.append_param(name=name, message=message)
e.set_memo('This is the second experiment')
hello_world(name, message, e)
