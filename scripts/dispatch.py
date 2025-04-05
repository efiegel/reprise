from reprise.dispatcher import MailgunDispatcher

if __name__ == "__main__":
    print("Dispatching reprise")
    dispatcher = MailgunDispatcher()
    dispatcher.schedule()
