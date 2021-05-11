from nmigen import *
from nmigen_cocotb import run
import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
from random import getrandbits

class Stream(Record):
    def __init__(self, width, **kwargs):
        Record.__init__(self, [('data', width), ('valid', 1), ('ready', 1)], **kwargs)

    def accepted(self):
        return self.valid & self.ready

    class Driver():
        def __init__(self, clk, dut, prefix):
            self.clk = clk
            self.data = getattr(dut, prefix + 'data')
            self.valid = getattr(dut, prefix + 'valid')
            self.ready = getattr(dut, prefix + 'ready')
        
        async def send(self, data):
            self.valid <= 1
            for d in data:
                self.data <= d
                await RisingEdge(self.clk)
                while self.ready.value == 0:
                    await RisingEdge(self.clk)
            self.valid <= 0

        async def recv(self, count):
            self.ready <= 1
            data = []
            for _ in range(count):
                await RisingEdge(self.clk)
                while self.valid.value == 0:
                    await RisingEdge(self.clk)
                data.append(self.data.value.integer)
            self.ready <= 0
            return data



# dut
class Adder(Elaboratable):
    def __init__(self, width):
        self.a = Stream(width, name='a')
        self.b = Stream(width, name='b')
        self.r = Stream(width + 1, name='r')

    def elaborate(self, platform):
        m = Module()
        sync = m.d.sync
        comb = m.d.comb

        with m.If(self.r.accepted()):
            sync += self.r.valid.eq(0)

        with m.If(self.a.accepted() & self.b.accepted()):
            sync += [
                self.r.valid.eq(1),
                self.r.data.eq(self.a.data + self.b.data)
            ]
        comb += [
            self.a.ready.eq((~self.r.valid) | (self.r.accepted())), 
            self.b.ready.eq((~self.r.valid) | (self.r.accepted()))
        ]
        return m


        
# inicialización del dut
async def init_test(dut):
    cocotb.fork(Clock(dut.clk,10,'ns').start())
    dut.rst <= 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst <= 0

# funcion que va a testear
@cocotb.test()
async def burst(dut):
    await init_test(dut)   # reset

    stream_input_a = Stream.Driver(dut.clk, dut, 'a__')  # declaro las señales
    stream_input_b = Stream.Driver(dut.clk, dut, 'b__')
    stream_output = Stream.Driver(dut.clk, dut, 'r__')

    N = 100                 # probamos 100 casos
    width = len(dut.a__data) # obtengo longitud del sumador
    mask = int('1' * (width+1), 2) # máscara para limitar la cantidad de bits. El resultado es el uno mas que los sumandos.

    data_a = [getrandbits(width) for _ in range(N)] # obtengo una lista de 100 numeros enteros 
    data_b = [getrandbits(width) for _ in range(N)] # aleatorios de cantidad de bits 'width'
    
    # Suma de data_a y data_b, con and lógico con la máscara para limitar la cantidad de bits
    #expected = [(x + y) &mask for x in data_a for y in data_b]
    expected = []
    for i in range(len(data_a)):
        expected.append((data_a[i] + data_b[i]) &mask)

    cocotb.fork(stream_input_a.send(data_a))
    cocotb.fork(stream_input_b.send(data_b))
    recved = await stream_output.recv(N)

    assert recved == expected


# simulacion
if __name__ == '__main__':
    core = Adder(5)
    run(
        core, 'ej1',
        ports=
        [
            *list(core.a.fields.values()),
            *list(core.b.fields.values()),
            *list(core.r.fields.values())
        ],
        vcd_file='adder.vcd'
    )