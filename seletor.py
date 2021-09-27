import numpy
import random

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

import pandas as pd

import numpy as np

from collections import Counter

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

class Seletor():
    def __init__(self, df,  cargo, temas_esp, qtd_perguntas, IND_INIT_SIZE): 
        self.cargo = cargo
        self.temas_esp = temas_esp
        self.qtd_perguntas = qtd_perguntas
        self.IND_INIT_SIZE = IND_INIT_SIZE
        self.df = df


       #temas = list(set((df.TEMA).to_list()))
        #cargo = 'Cientista Junior'
        #individuos = [0, 1, 1...]
        #população = ([0, 1, 1...], [0, 0, 1...], [0, 0, 1...], [0, 0, 1...], [0, 0, 1...], [0, 0, 1...])

        #self.temas_esp = {'Communication': 2, 'data_science_easy': 2}

        #qtd_perguntas = 4

        #IND_INIT_SIZE = len(df)

    def evaluate(self, x):
        dicti = {}
        temas_qtd = []

        j = 0
        k = 0
        l = 0

        for i, cromossomo in enumerate(x):
           
            tema = self.df.loc[i, 'TEMA']
            temas_qtd.append(tema)
            if cromossomo == 1:
                if tema in self.temas_esp:
                    if self.df.loc[i, 'PESO'] == 1:
                        j = j+1
                        dicti[1] = j
                    if self.df.loc[i, 'PESO'] == 2:
                        k = k+1
                        dicti[2] = k
                    if self.df.loc[i, 'PESO'] == 3:
                        l = l+1
                        dicti[3] = l
                else:
                    dicti[i] = 0

        c = Counter(temas_qtd)
        evaluate = {}
        for tema, repeticoes in c.items():
            if repeticoes > 1:
                result = [indice for indice, item in enumerate(temas_qtd) if item == tema]
                evaluate[tema] = len(result)

        tema = 0 
        for item in evaluate.keys():
            try:
                if self.temas_esp[item] == evaluate[item]:
                    tema = tema + 1
                else:
                    tema = tema
            except:
                tema = tema -1

        peso = 0
        for item in dicti.keys():
            if self.cargo == 'Cientista Junior':
                if item == 1:
                    quantidade = dicti[item] 
                    if quantidade == round(0.7*self.qtd_perguntas):
                        peso = peso + 1
                    else:
                        peso = peso
                if item == 2:
                    quantidade = dicti[item] 
                    if quantidade == round(0.3*self.qtd_perguntas):
                        peso = peso + 1
                    else:
                        peso = peso
                if item == 3:
                    peso = peso - 1


                if self.cargo == 'Cientista Pleno':
                    if item == 1:
                        quantidade = dicti[item] 
                        if quantidade == round(0.5*self.qtd_perguntas):
                            peso = peso + 1
                        else:
                            peso = peso
                    if item == 2:
                        quantidade = dicti[item] 
                        if quantidade == round(0.3*self.qtd_perguntas):
                            peso = peso + 1
                        else:
                            peso = peso
                    if item == 3:
                        quantidade = dicti[item] 
                        if quantidade == round(0.2*self.qtd_perguntas):
                            peso = peso + 1

                    if self.cargo == 'Cientista Pleno':
                        if item == 1:
                            quantidade = dicti[item] 
                            if quantidade == round(0.3*self.qtd_perguntas):
                                peso = peso + 1
                            else:
                                peso = peso
                        if item == 2:
                            quantidade = dicti[item] 
                            if quantidade == round(0.3*self.qtd_perguntas):
                                peso = peso + 1
                            else:
                                peso = peso
                        if item == 3:
                            quantidade = dicti[item] 
                            if quantidade == round(0.2*self.qtd_perguntas):
                                peso = peso + 1
        return tema, peso

    def algoritmo(self):

        def geraindividuo(num_1, tam_lista):
            lista = num_1*[1] + (tam_lista - num_1)*[0]
            randomizado = np.random.permutation(lista)

            return randomizado

        creator.create("Fitness", base.Fitness, weights=(1.0,1.0))

        creator.create("Individual", list, fitness=creator.Fitness)

        toolbox = base.Toolbox()
        # Sorteia o número de 1's entre 2 e 10
        toolbox.register("indices", geraindividuo, self.qtd_perguntas, self.IND_INIT_SIZE)
        toolbox.register("individual", tools.initIterate, creator.Individual,
                         toolbox.indices)

        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        toolbox.register("evaluate", self.evaluate)
        toolbox.register("mate", tools.cxUniform,indpb=0.15)
        toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        toolbox.register("select", tools.selBest)

        random.seed(64)
        NGEN = 10
        LAMBDA = 100
        CXPB = 0.7
        MUTPB = 0.2
        MU = 10000

        pop = toolbox.population(n=MU)
        hof = tools.ParetoFront()
        stats = tools.Statistics(lambda ind: ind.fitness.values[:3])
        stats = tools.Statistics(lambda ind: ind.fitness.values[:3])
        stats.register("avg", np.mean, axis=0)
        stats.register("std", np.std, axis=0)
        stats.register("min", np.min, axis=0)
        stats.register("max", np.max, axis=0)


        algorithms.eaMuPlusLambda(
            pop,
            toolbox,
            MU,
            LAMBDA,
            CXPB,
            MUTPB,
            NGEN,
            stats,
            halloffame=hof,
        )

        
        for i, best in enumerate(hof):
            total = sum(best)
            if total == self.qtd_perguntas:
                retorno = (hof[i], 'Essa é a melhor combinação para você')

                #else:
                #    retorno = (hof[0], "Não encontramos uma combinação como a que você pediu, mas trouxemos a que mais se assemelha")
            else:
                retorno = (hof[0], "Não encontramos uma combinação como a que você pediu, mas trouxemos a que mais se assemelha")
            
        return retorno