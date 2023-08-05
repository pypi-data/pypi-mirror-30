# -*- coding: utf-8 -*-


class Neuron(object):
    """Create your own neurons and send messages between them

    Dendrite (int) = Branched protoplasmic prolongation of the nerve cell
    type_neuron(str)= neuron classified as sensory, motor or interneuron
    remaining_life (float)= remaining useful life percentage of your neuron
    """

    def __init__(self, name='name', dendrite=100, type_neuron='sensory',
                 remaining_life=100):
        self.name = name
        self.dendrite = dendrite
        self.type_neuron = type_neuron
        self.remaining_life = remaining_life

    def __str__(self):
        msg = ("The {} have a neuron with {} branches, "
               "with function {} and {}% remaining life").format(
                    self.name,
                    self.dendrite,
                    self.type_neuron,
                    self.remaining_life,
                )

        return msg

    def evolution(self, percentage):
        msg = ("{} your neuron is now {}% artificial"
               "").format(self.name, percentage)
        return msg

    def synapse(self, n, message):
        msg = ("{} the message from your neuron 1: {} to neuron 2: {} is: {} "
               "").format(self.name, self.type_neuron, n.type_neuron, message)
        return msg
