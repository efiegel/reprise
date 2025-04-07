from datetime import datetime, timedelta

from reprise.dispatcher import MailgunDispatcher

if __name__ == "__main__":
    dispatcher = MailgunDispatcher()

    # 8am and 4pm deliveries, ensuring coverage for the next 3 days
    now = datetime.now()
    target_times = []
    for i in range(3):
        time_floor = {"minute": 0, "second": 0, "microsecond": 0}
        target_times.append(now.replace(hour=8, **time_floor) + timedelta(days=i))
        target_times.append(now.replace(hour=16, **time_floor) + timedelta(days=i))

    dispatcher.schedule(target_times)
