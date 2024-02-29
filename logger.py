import logging
import os
from datetime import datetime
from pathlib import Path
import traceback
import time
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pytz import timezone, utc


PRINT_TRACEBACK = False
logger = None
TZ = None


def customTime(*args):
    utc_dt = utc.localize(datetime.utcnow())
    converted = utc_dt.astimezone(TZ)
    return converted.timetuple()


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)

        filename, file_extension = os.path.splitext(self.baseFilename)

        dfn = self.rotation_filename(f'{filename}_{time.strftime(self.suffix, timeTuple)}{file_extension}')
        if os.path.exists(dfn):
            os.remove(dfn)
        self.rotate(self.baseFilename, dfn)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt


def print_and_log(level, message):
    current_time = datetime.now(TZ).strftime("%Y/%m/%d %H-%M-%S")
    print(f'[{current_time}] {message}')
    if level == logging.ERROR:
        logger.error(message)
    elif level == logging.WARNING:
        logger.warning(message)
    elif level == logging.INFO:
        logger.info(message)
    else:
        logger.debug(message)


def print_and_log_exception(message):
    print_and_log(logging.ERROR, message)
    if PRINT_TRACEBACK:
        print_and_log(logging.ERROR, traceback.format_exc())


def init_logger(log_path, camera_name, tz, print_traceback=False):
    global logger
    global PRINT_TRACEBACK
    global TZ
    PRINT_TRACEBACK = print_traceback
    TZ = tz

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    logger = logging.getLogger('court')

    logger.propagate = False
    logger.setLevel(logging.INFO)

    handler = CustomTimedRotatingFileHandler(os.path.join(log_path, f'{camera_name}_log.txt'), when='h', interval=1, encoding='utf8')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%d-%b-%y %H:%M:%S')
    handler.setFormatter(formatter)
    formatter.converter = customTime

    logger.addHandler(handler)
