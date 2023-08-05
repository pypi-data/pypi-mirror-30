from toolkit.translator import Translator
from toolkit import test_prepare
test_prepare()
with Translator({"WEBSITE": "qq"}) as translator:
    result = translator.translate("what a fuck day it is!")
    translator.logger.info(result)
