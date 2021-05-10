
from nmigen.back.pysim import Simulator
from up_counter import UpCounter

# The testbench is a Python generator function that
# is co-simulated with the counter itself

# yield --> advance the simulation by one clock
# yield sig --> inspect the simulated signal
# yield sig.eq(val) --> update the simulated signal

dut = UpCounter(25)

def bench():
    # Disabled counter should not overflow
    yield dut.en.eq(0) # disable counter
    for _ in range(30):
        yield # advance the sim by 1 clock
        assert not (yield dut.ovf) # ovf should be 0

    # Once enabled, the counter should overflow in 25 cycles
    yield dut.en.eq(1) # enable counter
    for _ in range(25):
        yield 
        assert not (yield dut.ovf)
    
    yield
    assert (yield dut.ovf)

    # The overflow should clear in one cycle
    yield 
    assert not (yield dut.ovf)

sim = Simulator(dut)
sim.add_clock(1e-6) # 1MHz
sim.add_sync_process(bench)
with sim.write_vcd("up_counter.vcd"):
    sim.run()
    
