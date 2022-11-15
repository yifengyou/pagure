import multiprocessing
import time
import random


def func(msg):
    sleep_time = random.randint(1, 10)

    print("msg:", msg, " sleep:", sleep_time)
    time.sleep(sleep_time)
    print("msg:", msg, " sleep:", sleep_time, " end")


if __name__ == "__main__":
    target_list = ['a', 'b', 'c']
    pool = multiprocessing.Pool(processes=2)
    for i in target_list:
        msg = "hello %s" % (i)
        pool.apply_async(func, (msg,))  # 维持执行的进程总数为processes，当一个进程执行完毕后会添加新的进程进去

    print("Mark~ Mark~ Mark~~~~~~~~~~~~~~~~~~~~~~")
    pool.close()
    pool.join()  # 调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
    print("Sub-process(es) done.")

# 输出
# Mark~ Mark~ Mark~~~~~~~~~~~~~~~~~~~~~~
# msg: hello 0
# msg: hello 1
# end
# end
# Sub-process(es) done.
