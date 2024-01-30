class Node:
    def __init__(self, func):
        self.func = func
        self.next = None

class FunctionLinkedList:
    def __init__(self):
        self.head = None

    def add_function(self, func):
        new_node = Node(func)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def execute_functions_from(self, func_name):
        current = self.head
        found = False
        while current:
            if current.func.__name__ == func_name:
                found = True
            if found:
                current.func()
            current = current.next

if __name__ == '__main__':
    # Example usage:
    def a():
        print("Function a")

    def b():
        print("Function b")

    def c():
        print("Function c")

    functions_list = FunctionLinkedList()
    functions_list.add_function(a)
    functions_list.add_function(b)
    functions_list.add_function(c)

    # Call with different arguments
    print("From a:")
    functions_list.execute_functions_from("a")
    print()

    print("From b:")
    functions_list.execute_functions_from("b")
    print()

    print("From c:")
    functions_list.execute_functions_from("c")

