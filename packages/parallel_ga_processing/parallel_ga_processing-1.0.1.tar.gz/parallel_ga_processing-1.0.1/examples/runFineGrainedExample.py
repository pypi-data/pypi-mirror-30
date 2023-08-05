from algorithmRunners import run_grained_ga
from .fineGrained import FineGrained

if __name__ == '__main__':
    ins = FineGrained(population_size=10, chromosome_size=4,
                      number_of_generations=100, num_of_neighbours=3,
                      neighbourhood_size=3, server_ip_addr="127.0.0.1")
    run_grained_ga(ins)
