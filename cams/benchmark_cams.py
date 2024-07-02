import glob
import os
import time

from loguru import logger
from tqdm import tqdm

from utils import (CamsERA5, ParticleVisualizer, load_config, plot_benchmark,
                   save_results)

if __name__ == "__main__":

    dir_path = os.path.dirname(os.path.realpath(__file__))
    config = load_config(file_path=os.path.join(dir_path,"config.yaml"))

    # Dictionary to store benchmarking results

    output_folder = config["output_folder"]
    num_requests = config["num_requests"]

    out_dir = os.path.join(dir_path, output_folder)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    logger.info("start benchmark")

    request_issues = 0

    benchmark = {
            "download_time": [None]* num_requests,
            "data_processing": [None]* num_requests,
            "animation": [None]* num_requests,
            "end_to_end": [None]* num_requests,
            "request_issues": [None]* num_requests,
            }

    query = config["cams_request"]
    cams = CamsERA5()

    # Repeat benchmarking for a specified number of requests
    for r in tqdm(range(num_requests), desc="Processing requests", unit="request", ncols=100, colour="#3eedc4"):

        t0 = time.time()
        try:
            cams.get_data(query=query)
            cams.download(filename="CAMS")
            t1 = time.time()
        except Exception as e:
            logger.error(f"Issue in the data access or download: {e}")
            request_issues += 1
            continue
        ds = cams.process()
        t2 = time.time()
        pm10_anim = ParticleVisualizer.generate_animation(ds)
        
        t3 = time.time()
        # Record benchmarking times
        benchmark["download_time"][r]=(t1-t0)
        benchmark["data_processing"][r]=(t2-t1)
        benchmark["animation"][r]=(t3-t2)
        benchmark["end_to_end"][r]=(t3-t0)
        benchmark["request_issues"][r] = request_issues

        # Cleanup by deleting zip and nc files
        for filename in glob.glob("*CAMS*.zip*"):
            os.remove(filename)
        for filename in glob.glob("*cams*.nc*"):
            os.remove(filename)

    title = 'End to End CAMS particle density animation generation benchmark'
    plot_benchmark(benchmark_dict=benchmark,
                   out_dir=out_dir,title=title)

    filename = os.path.join(out_dir,"cams_benchmark.json")
    save_results(data=benchmark,filename=filename)
    logger.info(f"Benchmark completed. Results saved to {out_dir}", "benchmarks.json")



















