class Menu:
    def __init__(self):
        self.options = []
        self.pre_menu_text = ()

    def add_option(self, text, callback, params):
        self.options.append((text, callback, params))

    def display(self, options):
        for i in range(100):
            print()
        for line in self.pre_menu_text:
            print(line)
        retval = None
        while True:
            print("********************************************************")
            displaying = 0
            letters = "abcdefghijklmnopqrstuvwxyz1234567890+-=/.,<>|"
            for option in self.options:
                print("* " + letters[displaying] + ": " + option[0])
                displaying += 1
            print("* " + letters[displaying] + ": Back/Exit")
            print("********************************************************")
            u_input = input("> ")
            if u_input not in letters[:displaying+1]:
                print("Please provide proper input!")
                continue
            if u_input == letters[displaying]:
                u_input = None
                break
            if self.options[letters.index(u_input)][1]:
                retval = self.options[letters.index(u_input)][1](self.options[letters.index(u_input)][2])
                if options and "exit_on_choose" in options:
                    return retval
        return retval

    def set_pre_menu_text(self, tup):
        self.pre_menu_text = tup
