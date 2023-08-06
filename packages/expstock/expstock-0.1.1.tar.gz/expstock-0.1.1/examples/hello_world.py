from expstock import expstock


e = expstock.ExpStock(dbsave=True)
x = 1
y = 2
z = 3

e.append_param(x=x, y=y, z=z)
e.set_memo('This is the first experiment')
e.pre_stock()
print('hello')
e.post_stock()
