from gimini import Gimei

class Aesthetique:
    
    def __init__(self):
        pass


    def translate(self, input):
        normal = u' 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~'
        wide = u' ０１２３４５６７８９ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ！゛＃＄％＆（）＊＋、ー。／：；〈＝〉？＠［\\］＾＿‘｛｜｝～'
        widemap = dict((ord(x[0]), x[1]) for x in zip(normal, wide))
        wide_output = input.translate(widemap)
        name_output = Gimei().name.kanji
        output = '{0} {1}'.format(wide_output, name_output)
        return output
