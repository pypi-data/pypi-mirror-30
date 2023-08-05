import multiprocessing
from multiprocessing import JoinableQueue, Event
from multiprocessing.queues import Empty
import math
import functools


def _get_reasonable_process_count(cpu_count=multiprocessing.cpu_count()):
    """ Finds a good number of CPUs to use. Will always leave at least one CPU free,
    and uses most of the CPUs available. """
    unused_cpus = int(1 + math.floor(cpu_count / 8))
    return max(1, cpu_count - unused_cpus)


def _thread_run_user_function(user_function,
                              result_queue,
                              data,
                              args,
                              **kwargs):
    """ This is run by each thread. The work is processed and results are put into a queue. """
    for item in data:
        result = user_function(item, *args, **kwargs)
        result_queue.put(result)


def _thread_run_user_iterator(user_function,
                              result_queue,
                              count_queue,
                              finished_signal,
                              data,
                              args,
                              **kwargs):
    count = 0
    for item in data:
        for result in user_function(item, *args, **kwargs):
            result_queue.put(result)
            count += 1
    count_queue.put(count)
    finished_signal.set()


def parallel_map(data,
                 user_function,
                 args=None,
                 kwargs=None,
                 process_count=None):
    """
    Runs a function on an iterable of data in parallel, without copying the data (as long as the user_function
    doesn't modify the data). Only guaranteed to work in Linux.

    :param data: an iterable of data that should be processed in parallel. Each member of this iterable
    should represent a unit of work that can be handled independently.
    :param user_function: a function that takes a single member of data and returns a result. This MUST return
    a single object for every input or else a deadlock will occur. The data to be worked on MUST be the first
    positional parameter.
    :param args: any positional arguments that need to be passed to user_function
    :param kwargs: any keyword arguments that need to be passed to user_function
    :param process_count: how many processes to use. If None, most (but not all) of the cores will be used.

    """
    process_count = _get_reasonable_process_count() if process_count is None else int(process_count)
    assert process_count > 0, 'process_count needs to be a positive integer.'

    i = 0
    # Split up the data into more-or-less evenly-sized chunks, with one chunk for each process
    bins = [[] for _ in range(process_count)]
    for i, item in enumerate(data):
        bins[i % process_count].append(item)

    if i == 0:
        # There was no data
        raise StopIteration

    result_queue = JoinableQueue()
    processes = []
    func = functools.partial(_thread_run_user_function, user_function, result_queue)

    # Make sure the optional arguments are formatted in a way that multiprocessing.Process can accept
    args = () if args is None else args
    kwargs = {} if kwargs is None else kwargs

    # Start all the threads and begin working on the data
    for n in range(process_count):
        if not bins[n]:
            break

        process = multiprocessing.Process(target=func, args=(bins[n], args), kwargs=kwargs)
        processes.append(process)
        process.start()

    # Since i is one less than the number of items, range(i) will give us all but one result
    for j in range(i):
        yield result_queue.get()
    # We need to pull the last item from the queue before we can join on the threads or this will deadlock
    final_result = result_queue.get()
    # Ensure that the threads are shut down
    for process in processes:
        process.join()
    # We have to return this after the threads are joined just to force that part of the code to run
    yield final_result


def parallel_iterator(data,
                      user_iterator,
                      args=None,
                      kwargs=None,
                      process_count=None):
    """
    Runs a function on an iterable of data in parallel, without copying the data (as long as the user_function
    doesn't modify the data). Only guaranteed to work in Linux.

    :param data: an iterable of data that should be processed in parallel. Each member of this iterable
    should represent a unit of work that can be handled independently.
    :param user_iterator: a function that takes a single member of data and yields zero or more results. The data to be
    worked on MUST be the first positional parameter.
    :param args: any positional arguments that need to be passed to user_function
    :param kwargs: any keyword arguments that need to be passed to user_function
    :param process_count: how many processes to use. If None, most (but not all) of the cores will be used.

    """
    process_count = _get_reasonable_process_count() if process_count is None else int(process_count)
    assert process_count > 0, 'process_count needs to be a positive integer.'
    # Split up the data into more-or-less evenly-sized chunks, with one chunk for each process
    bins = [[] for _ in range(process_count)]
    i = 0
    for i, item in enumerate(data):
        bins[i % process_count].append(item)

    if i == 0:
        # There was no data
        raise StopIteration

    result_queue = JoinableQueue()
    count_queue = JoinableQueue()
    processes = []
    finished_signals = []
    func = functools.partial(_thread_run_user_iterator, user_iterator, result_queue, count_queue)

    # Make sure the optional arguments are formatted in a way that multiprocessing.Process can accept
    args = () if args is None else args
    kwargs = {} if kwargs is None else kwargs
    # Start all the threads and begin working on the data
    for n in range(process_count):
        if not bins[n]:
            process_count = n
            break
        finished_signal = Event()
        finished_signals.append(finished_signal)
        process = multiprocessing.Process(target=func, args=(finished_signal, bins[n], args), kwargs=kwargs)
        processes.append(process)
        process.start()
    # While any of the threads are still running, we pull items from the results queue.
    # The queue may sporadically end up being empty before all work is done. We keep trying to get items from it
    # until we're sure everything has been processed
    yielded_result_count = 0
    while not all([e.is_set() for e in finished_signals]):
        while True:
            try:
                result = result_queue.get_nowait()
                yielded_result_count += 1
                yield result
            except Empty:
                break

    # All of the threads are done. We can see how many results they put into the result_queue
    total_result_count = sum([count_queue.get() for _ in range(process_count)])

    # Drain any items that might still be in the result_queue so that we can safely join the threads.
    remaining_result_count = total_result_count - yielded_result_count
    for _ in range(remaining_result_count - 1):
        yield result_queue.get()

    # We need to hang onto one result so that we can have a yield statement after the thread joining, which will
    # force that code to run
    final_result = None
    if remaining_result_count > 0:
        final_result = result_queue.get()

    # The queue must be empty now, and the threads have all signaled that they're done
    for process in processes:
        process.join()

    # We may or may not have one final item to yield
    if final_result is not None:
        yield final_result
