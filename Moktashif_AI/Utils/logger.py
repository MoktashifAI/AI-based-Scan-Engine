from loguru import logger

class Logger:
    def Log(self,message,type=""):
        if type == "Normal":
            logger.add(message)
        elif type == "Error":
            logger.error(message)
        elif type == "Info":
            logger.info(message)

        print(message)
