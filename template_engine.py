
class Compiler(object):

    prev_interpolate = "[["
    back_interpolate = "]]"

    def __init__(self):
        pass

    def compile(self,pre_html,userKV):

        #GATHER HTML IN PARSABLE STRING
        self.string_html = pre_html

        #GATHER DICTIONARY OF K,V'S FOR PARSER TO CHANGE FOR
        self.prog_KV = self.preparer(userKV)

        #PARSE
        self.final_html = self.replace(self.string_html,self.prog_KV)


        return self.final_html



    def preparer(self,k_Vs):
        #DICT FOR PROGRAM TO SEARCH WITH
        self.prog_KV = {}
        #MAKE KEYS IN USER DICT TEMPLATED
        for k in k_Vs:
            #TURN USER KEY TO TEMPLATED
            self.key = self.templater(k)
            #ADD KEY AND VALUE TO DICTIONARY FOR PROGRAM
            self.prog_KV[self.key] = k_Vs[k]

        return self.prog_KV

    def replace(self,text,compDict):
        for key in compDict:
            #replace '<<>>' key in html with value
            text = text.replace(key,str(compDict[key]))

        return text

    def templater(self,string):
        #CLEAN KEY SO VARIABLE IS VISIBLE ONLY
        #TAKE KEY ONLY AS STRING
        #TAKE '<<' AND '>>' OFF OF KEY IN html
        #ONLY VARIBALE NAME WILL BE SHOWN
        self.str = self.prev_interpolate+string+self.back_interpolate
        return self.str
Compiler = Compiler()