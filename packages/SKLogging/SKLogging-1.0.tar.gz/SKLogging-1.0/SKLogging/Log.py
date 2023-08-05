import datetime as dt


class Log:
    def __init__(self, filename, level, format='[(time)] (level): (message)', printout=0):
        self.filename = filename
        self.level = level
        self.format = format
        self.printout = printout

        log_file = open(filename, 'a')
        log_file.close()

    def log(self, level, message, printout=0):
        if level.priority >= self.level.priority:
            log_msg = ''

            grab_char = 0
            grabbed_chars = ''
            grabbed_chars_list = []
            for char in self.format:
                if char == '(':
                    grab_char = 1
                if grab_char:
                    grabbed_chars += char
                else:
                    grabbed_chars_list.append(char)
                if char == ')':
                    grab_char = 0
                    grabbed_chars_list.append(grabbed_chars)
                    grabbed_chars = ''

            for item in grabbed_chars_list:
                if '(time)' == item:
                    time = str(dt.datetime.now()).split()[1].split('.')[0]
                    log_msg += time
                elif '(date)' == item:
                    date = str(dt.datetime.now()).split()[0]
                    log_msg += date
                elif '(message)' == item:
                    log_msg += message
                elif '(level)' == item:
                    log_msg += level.name
                else:
                    log_msg += item

            log_msg += '\n'
            log = open(self.filename, 'a')
            log.write(log_msg)
            log.close()
            if printout or self.printout:
                print log_msg
