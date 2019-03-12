class Metric:
    def default_processor(self):
        return self.value

    def __init__(self, name="", processor=default_processor):
        self.name = name
        self.value = ""
        self.description = "Not set"
        self.processor = processor
        self.legend = ""
        pass

    @staticmethod
    def about():
        print("""init argument should be a function, which returns text to be displayed""")

    def get_text(self):
        return self.value.__str__()+self.legend

    def process(self):
        self.value = self.processor()

    def set_description(self, description):
        self.description = description


    def print(self):
        print("\nName: " + self.name + "\nText: " + self.get_text())
        pass


# def mProc():
#     # return "return from Mproc"
#     # pass
#     return 7
#
#
# m = Metric("M", mProc)
# m.process()
# m.print()
