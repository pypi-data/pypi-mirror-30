'''
Created on 2018年1月10日

@author: sunder3344
'''

class Pmorse():
    '''
    classdocs
    '''
    morse_map = {"A":".-", "B":"-...", "C":"-.-.", "D":"-..", "E":".", "F":"..-.", "G":"--.", "H":"....",
                 "I":"..", "J":".---", "K":"-.-", "L":".-..", "M":"--", "N":"-.", "O":"---", "P":".--.",
                 "Q":"--.-", "R":".-.", "S":"...", "T":"-", "U":"..-", "V":"...-", "W":".--", "X":"-..-",
                 "Y":"-.--", "Z":"--..", "0":"-----", "1":".----", "2":"..---", "3":"...--", "4":"....-",
                 "5":".....", "6":"-....", "7":"--...", "8":"---..", "9":"----.", 
                 ".":".-.-.-", ":":"---...", ",":"--..--", ";":"-.-.-.", "?":"..--..", "=":"-...-",
                 "'":".----.", "/":"-..-.", "!":"-.-.--", "-":"-....-", "_":"..--.-", "\"":".-..-.",
                 "(":"-.--.", "}":"-.--.-", "$":"...-..-", "&":".-...", "@":".--.-."
                 };
    op = "/";

    #encrypt the str
    def encrypt(self, str):
        result = ""
#         try:
        for i in str:
            if i == " ":
                continue
            #判断是否是中文
            ui = i.encode("unicode_escape")
            if ui >= b'\u4e00' and ui <= b'\u9fa5':
                i = ui.__str__();
                i = i.replace("b'", "'")
                i = i.replace("'", "")
                i = i.replace("\\\\", "/")
                i = i.upper()
                for j in i:
                    if result == "":
                        result = self.morse_map[j]
                    else:
                        result = result + self.op + self.morse_map[j]
                continue
            else:
                i = i.upper()
            if result == "":
                result = self.morse_map[i]
            else:
                result = result + self.op + self.morse_map[i]
#         except Exception:
#             pass
        return result;
    
    #decrypt the str
    def decrypt(self, str):
        result = ""
        try:
            pmorse_reverse = dict((v,k) for k,v in self.morse_map.items())
            arr = str.split(self.op)
            for i in arr:
                if result == "":
                    result = pmorse_reverse[i]
                else:
                    result = result + pmorse_reverse[i]
        except Exception:
            pass
        return result
    
    #将可能有的中文转换为中文字符
    def strDecode(self, str):
        str = str.replace("/U", "\\u")
        str = eval("b'" + str + "'")
        return str.decode("unicode_escape")
#         print(str.decode("unicode_escape"))
#         str = str.replace("/U", "\u")
#         print(str)
#         m = str.decode("unicode_escape")
#         return m

    def __init__(self):
        pass