from pygmyhdl import *

@chunk
def fsm(clk_i):
    state = State('INIT', 'A', 'B', 'C', 'D', name='my_state', init_state='B')
    @seq_logic(clk_i.posedge)
    def logic():
        if state == state.s.INIT:
            state.next = state.s.A
        elif state == state.s.A:
            state.next = state.s.B
        elif state == state.s.B:
            state.next = state.s.C
        elif state == state.s.C:
            state.next = state.s.D
        else:
            state.next = state.s.INIT

clk = Wire('clk')
fsm(clk_i=clk)
clk_sim(clk, num_cycles=20)
show_text_table()
