from subprocess import run


class NotificationCenter(object):
    @staticmethod
    def file_rejection(user, filepath_list):
        notification_header = "File rejection\n"
        notification_file_list = '<b>' + '</b><b>'.join(filepath_list) + '</b>'
        run(['notify-send',
            user + 'sent you some files but some of them were infected.\n\n"',
            'They are removed from file system'], shell=True)
