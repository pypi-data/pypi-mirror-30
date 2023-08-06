import modelx as mx


# model---base
#    |     +-----foo
#   top
#    |
#    +----derived<-base


model, base = mx.new_model(), mx.new_space(name='base')

@mx.defcells
def foo(x):
    if x == 0:
        return 123
    else:
        return foo(x - 1)

top = model.new_space(name='topspace')

top.new_space(name='derived', bases=base)

def foo_v2(x):
    if x == 0:
        return 456
    else:
        return foo(x - 1)

# model.derived.new_cells(name='foo', formula=foo_v2)

# model.derived.derived_cells