import logging
from colorama import Fore, Style 


class ColoredFormatter(logging.Formatter):
    '''
    Созданный форматтер для красивого вывода в консоль
    '''
    COLORS = {logging.DEBUG : Fore.BLUE, 
              logging.INFO : Fore.GREEN, 
              logging.WARNING : Fore.YELLOW, 
              logging.ERROR : Fore.RED, 
              logging.CRITICAL : Fore.RED + Style.BRIGHT}
    
    def format(self, record):
        if record.levelno in self.COLORS:
            record.levelname = (f"{self.COLORS[record.levelno]}"
                                f"{record.levelname}{Style.RESET_ALL}")
            record.msg = (f"{self.COLORS[record.levelno]}"
                          f"{record.msg}{Style.RESET_ALL}")
        
        return super().format(record)
    

class LogManager:
    '''
    класс для логирования всех ошибок во всех модулях
    '''

    def __init__(self,name, level = logging.INFO):
        # Настройка логгера
        self.log = logging.getLogger(name)
        self.log.setLevel(level)

        #TODO: разобраться с тем, как работает BasicConfig

        #logging.basicConfig(level=logging.DEBUG,
        #                    datefmt='%Y-%m-%d %H:%M:%S',
        #                    format = "%(levelname)s.:%(module)s:%[(lineno)d:%(asctime)s.%(msecs)03d] - %(message)s")
        

        # Добавление консольного хэндлера
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColoredFormatter('%(levelname)s : %(module)s : %(lineno)d : [%(asctime)s.%(msecs)03d] - %(message)s'))
        self.log.addHandler(console_handler)

        # Добавление файлового хендлера
        ##TODO: здесь нужно встроить какую то логику либо по очистке log-файла либо там разделять запуски программы между собой
        #file_handler = logging.FileHandler('logger.log')
        #file_formatter = logging.Formatter('%(levelname)s : %(module)s : %(lineno)d : [%(asctime)s.%(msecs)03d] - %(message)s')
        #file_handler.setFormatter(file_formatter)
        #self.log.addHandler(file_handler)


        logging.getLogger("lasio").setLevel(logging.WARNING)
        logging.getLogger("openpyxl").setLevel(logging.WARNING)
        logging.getLogger("pandas").setLevel(logging.WARNING)


if __name__ == '__main__':
    lm = LogManager(__name__)
    lm.log.debug('DEB')
    lm.log.info('INF')
    lm.log.warning('WARN')
    lm.log.error('err')
    #lm.log.critical('crit')