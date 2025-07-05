from celery import shared_task

@shared_task
def add(x,y):
    return x + y





def main():
    add(1,2)



if __name__ == '__main__':
    main()