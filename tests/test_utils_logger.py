from utils.logger import Logger

def test_logger_singleton():
    logger1 = Logger()
    logger2 = Logger()
    assert logger1 is logger2
    logger1.info("Logger singleton test message.") 