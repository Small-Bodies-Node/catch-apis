import time


def example(seconds: int) -> None:
    """ --- """
    print('Starting task')
    for i in range(seconds):
        print(i)
        time.sleep(1)
    print('Task completed')
