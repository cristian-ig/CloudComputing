import json

import numpy as np


class Node:
    def __init__(self, outputs, weights, bias, activation_function):
        self.outputs = outputs
        self.weights = weights
        self.bias = bias
        self.activation_fuction = activation_function


class Layer:
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs
        self.weights_matrix = np.random.uniform(-2, 2, (outputs, inputs))
        self.biases = np.random.uniform(-2, 2, (1, outputs))
        self.outputdata = []
        # print("Biases",self.biases)
        # nodes = [ Node(next_layer_size,n[0:next_layer_size],n[next_layer_size:next_layer_size+1] if bias else 0,sigmoid) for n in np.random.rand(layer_size,next_layer_size+1)]
        # print(self.weights_matrix)

    def feedLayer(self, inputs):
        data = np.dot(self.weights_matrix, inputs)
        return [sigmoid(data[i] + self.biases[0][i]) for i in range(0, len(data))]
        # print("feedLayer",data)


class NeuralNetwork:

    def __init__(self, nr_inputs, nr_outputs, nr_layers, nr_layer_nodes):
        self.inputs = nr_inputs
        self.outputs = nr_outputs
        self.hidden_layers_count = nr_layers
        self.hidden_layers_size = nr_layer_nodes

        self.layer_objs = []
        self.layer_objs.append(Layer(self.inputs, self.hidden_layers_size))
        for i in range(0, self.hidden_layers_count):
            self.layer_objs.append(Layer(self.hidden_layers_size, self.hidden_layers_size))
        self.layer_objs.append(Layer(self.hidden_layers_size, self.outputs))

    def toJson(self):
        return json.dumps(
            {"inputs": self.inputs,
             "outputs": self.outputs,
             "hidden_layers_count": self.hidden_layers_count,
             "hidden_layers_count": self.hidden_layers_size,
             "weights" : [l.weights_matrix.tolist() for l in self.layer_objs],
             "biases" : [l.biases.tolist() for l in self.layer_objs]
             }
        )
        # print("MATRIX:" ,np.dot(self.layer_objs[len(self.layer_objs)-1].weights_matrix,self.layer_objs[len(self.layer_objs)-2].weights_matrix))
        # print("Feeded layer",self.layer_objs[0].feedLayer([1,2,3]))
        # [Layer(self.inputs,self.hidden_layers_size), Layer(self.hidden_layers_size,self.hidden_layers_size) for i in range(0,self.hidden_layers_count) ]

    def feedNetwork(self, input_data):
        if len(input_data) != self.inputs:
            print("Input lenght does not match the network size")
            return
        else:
            input_data = self.layer_objs[0].feedLayer(input_data)
            self.layer_objs[0].outputdata = input_data
            for i in range(1, len(self.layer_objs) - 1):
                input_data = self.layer_objs[i].feedLayer(input_data)
                self.layer_objs[i].outputdata = input_data
            output_data = self.layer_objs[len(self.layer_objs) - 1].feedLayer(input_data)
            self.layer_objs[len(self.layer_objs) - 1].outputdata = output_data
            self.calculateSecondToLastError(self.layer_objs[len(self.layer_objs) - 1].weights_matrix,
                                            self.calculateOutputError(expected=[0, 2, 0, 0], output=self.layer_objs[
                                                len(self.layer_objs) - 1].outputdata),
                                            self.layer_objs[len(self.layer_objs) - 1].outputdata)
            print("FINAL RESULT:", output_data)
        return output_data

    def calculateOutputError(self, expected, output):
        if len(expected) != len(output):
            print("Lenghts do not match!")
            return
        else:
            return [(expected[i] - output[i]) * sigmoid(output[i], True) for i in range(0, len(expected))]

    def calculateSecondToLastError(self, weights, errors, output):
        error_matrix = []

        for x in range(len(weights)):
            row = []
            for y in range(len(weights[0])):
                row.append(0)
            error_matrix.append(row)
        # error_matrix = [[]*(len(weights))]*len(weights[0])
        # print("error_matrix", error_matrix)
        # print("WHEIGHTS", weights)
        # print("ERRORS", errors)
        # print("OUTPUT", output)
        # print("len(weights)", len(weights))
        # print("len(weights[i]", len(weights[0]))
        for i in range(0, len(weights)):
            for j in range(0, len(weights[i])):
                error_matrix[i][j] = weights[i][j] * errors[i] * sigmoid(output[i], True)

        # print("Error matrix", np.array(error_matrix))


def sigmoid(x, derivative=False):
    return x * (1 - x) if derivative else 1 / (1 + np.exp(-x))

#
# nn = NeuralNetwork(3, 4, 3, 6)
#
# nn.feedNetwork([1, 2, 3])
