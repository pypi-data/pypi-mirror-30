
class A():
    A_value = '0' #EAttribute(derived=False, changeable=True, eType=EString) 
    def __init__(self, A_value=None):
        if A_value is not None:
            self.A_value = A_value
        print('A class init')

def hello():
    print('hello, version 0.4')
