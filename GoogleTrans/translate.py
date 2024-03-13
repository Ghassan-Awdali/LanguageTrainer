
from googletrans import *
from googletrans import Translator

    
translator = googletrans.Translator()

trans = translator.translate('Hello there, how are you', dest='korean')
print(trans)



