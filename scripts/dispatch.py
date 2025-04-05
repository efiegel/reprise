from reprise.dispatcher import MailgunDispatcher

if __name__ == "__main__":
    dispatcher = MailgunDispatcher()
    dispatcher.schedule()
