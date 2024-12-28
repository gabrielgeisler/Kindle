from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm


def parallel_run(lst: list, func: callable, threads=10):
    with tqdm(total=len(lst)) as pbar:
        with ThreadPoolExecutor(max_workers=threads) as ex:
            futures = [ex.submit(func, item) for item in lst]
            for future in as_completed(futures):
                _ = future.result()
                pbar.update(1)
