from algorithmRunners import masterSlaveRunner
from .masterSlave import MasterSlave
if __name__ == '__main__':
    ins = MasterSlave(population_size=10, chromosome_size=4,
                      number_of_generations=100)
    masterSlaveRunner.run_master_slave_ga(ins)
