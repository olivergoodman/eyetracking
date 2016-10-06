from connection import connect
import threading

if __name__ == '__main__':
	t1 = threading.Thread(target=connect)
	t1.start()
	t1.join()