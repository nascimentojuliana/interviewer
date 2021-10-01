import re
import io
import os
import random
import gcsfs
import markdown
import pathlib
import pandas as pd
import numpy as np
from PIL import Image
import streamlit as st
from utils import utils
import pydata_google_auth
from seletor import Seletor
from io import BytesIO, StringIO
from google.cloud import storage
from google.oauth2 import service_account
from IPython.core.display import display,HTML

df_i = pd.read_csv('questoes.csv')

left_column, central_colum, right_column = st.columns(3)
with central_colum:
	st.image('chapeu.jpg')

	original_title = '<p style="font-family:Courier; color:Black; font-size: 30px;">* Sorting * *** Hat  ***</p>'
	st.markdown(original_title, unsafe_allow_html=True)


st.sidebar.text_input("Email do candidato", key="name")

cargo = st.sidebar.selectbox(
    'Posição',
    ('Cientista Junior', 'Cientista Pleno', 'Cientista Senior'))

dict_temas = {}

with st.form("my_form"):

	checkbox0 = st.checkbox('Quero gerar questões')

	submitted0 = st.form_submit_button("Gerar questões")

	if checkbox0:

		temas = list(set((df_i.TEMA).to_list()))

		temas_escolhidos = st.multiselect('Quais temas você quer?', temas)

		checkbox1 = st.checkbox('Já escolhi os temas')

		submitted5 = st.form_submit_button("Submeter")

		if checkbox1:

			qtd = []

			for i, item in enumerate(temas_escolhidos):
				qtd.append(st.selectbox('Selecione a quantidade de perguntas para o tema {}'.format(item), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
			
			checkbox2 = st.checkbox('Já selecionei as quantidades de questões')

			submitted6 = st.form_submit_button("Mostrar questões")

			if checkbox2:

				qtd_temas = []
				for item in qtd:
					qtd_temas.append(int(item))

				qtd_perguntas = sum(qtd_temas)

				mask = df_i['TEMA'].isin(temas_escolhidos)

				df = df_i[mask].reset_index(drop=True)

				IND_INIT_SIZE = len(df)

				for i, tema in enumerate(temas_escolhidos):
					dict_temas[tema] = qtd_temas[i]


				alertas = []
				for item in dict_temas.keys():
					limite = df[(df.TEMA == item)].reset_index(drop=True)
					if dict_temas[item] > len(limite):
						alertas.append('Alerta: quantidade de questões do tema {} é maior do que o disponível. Esse tema só tem {} questões'. format(item, len(limite)))

				if alertas:
					alertas
				else:
					questoes = []
					respostas  =[]

					seletor = Seletor(df, cargo, dict_temas, qtd_perguntas, IND_INIT_SIZE)
					resultado, mensagem = seletor.algoritmo()

					final = pd.DataFrame()
					imagens = []
					questoes = []

					contador = 0
					for i, item in enumerate(resultado):
						if item == 1:
							questao = df.loc[i, 'QUESTAO']
							resposta = df.loc[i, 'RESPOSTA']
							link = df.loc[i, 'LINKS']
							
							final.loc[contador, 'QUESTAO'] = questao
							final.loc[contador, 'RESPOSTA'] = resposta
							final.loc[contador, 'LINKS'] = link

							contador = contador+1
							questoes.append('Questão {}: {} \n Resposta: {}'.format(contador, questao, resposta))
							imagens.append(link)

					mensagem

					for i, item in enumerate(imagens):
						try:
							st.image(item) #caption=questoes[i])
							questoes[i]
						except:
							questoes[i]

					final.to_csv('{}_questoes.csv'.format(st.session_state.name), index=False)
					

with st.form("my_form1"):

	checkbox1 = st.checkbox('Quero avaliar o candidato')

	submitted1 = st.form_submit_button("Avaliar questões")

	if checkbox1:

		try:
			df1 = pd.read_csv('{}_questoes.csv'.format(st.session_state.name), encoding='latin-1')
		except:
			'Digite um email válido e existente para esse processo seletivo	'

		questoes = []
		imagens = []
		contador = 1
		for index, row in df1.iterrows():
				questao = row.QUESTAO
				resposta = row.RESPOSTA
				link = row.LINKS

				questoes.append('Questão {}: {} \n Resposta: {}'.format(contador, questao, resposta))
				contador = contador+1 
				imagens.append(link)

		nota = []
		for i, item in enumerate(imagens):
			st.image(item)
			questoes[i]
			result = st.selectbox('Selecione o valor para a questão {}'.format(i+1), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
			nota.append(result)

		checkbox2 = st.checkbox('Quero salvar a avaliação das questões')

		submitted7 = st.form_submit_button("Finalizar")

		if checkbox2:

			notas = []
			for item in nota:
				notas.append(int(item))

			df3 = pd.DataFrame(questoes, columns = ['QUESTAO'])
			df4 = pd.DataFrame(notas, columns = ['NOTA'])

			df2 = pd.concat([df3, df4], axis=1)
		
			df2.to_csv('{}_avaliacao_questoes.csv'.format(st.session_state.name))

			nota_final = sum(notas)

			'A nota final do candidato foi:'
			nota_final

			if nota_final > 10:

				'Alerta: nota final maior do que 10'

			submitted3 = st.form_submit_button("Enviar avaliação para o candidato")
			
			if submitted3:

				try:

					questoes = []
					imagens = []

					final = pd.concat([df1, df2.drop(['QUESTAO'], axis=1)], axis=1)

					final.to_html('filename.html', index=False)
					
					message_text = 'Olá! As questões do seu teste seguem em anexo, com as respostas e avaliação de cada uma. \n Sua NOTA FINAL foi {}.'.format(nota_final)
					to = st.session_state.name + ',' + 'samuel.faeng@gmail.com'
					sender = 'juliana.silva@sulamerica.com.br'
					subject = 'resultado entrevista'
					utils.SendMessage(sender, to, subject, message_text, 'filename.html')
					'Avaliação enviada para o candidato'

				except:

					'Verifique se você tem as credenciais adequadas para enviar email'

			

with st.form("my_form2"):

	checkbox0 = st.checkbox('Quero gerar questões e avaliar o candidato')

	submitted0 = st.form_submit_button("Gerar questões")

	if checkbox0:

		temas = list(set((df_i.TEMA).to_list()))

		temas_escolhidos = st.multiselect('Quais temas você quer?', temas)

		checkbox1 = st.checkbox('Já escolhi os temas')

		submitted5 = st.form_submit_button("Submeter")

		if checkbox1:

			qtd = []

			for i, item in enumerate(temas_escolhidos):
				qtd.append(st.selectbox('Selecione a quantidade de perguntas para o tema {}'.format(item), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
			
			checkbox2 = st.checkbox('Já selecionei as quantidades de questões')

			submitted6 = st.form_submit_button("Mostrar questões")

			if checkbox2:

				qtd_temas = []
				for item in qtd:
					qtd_temas.append(int(item))

				qtd_perguntas = sum(qtd_temas)

				mask = df_i['TEMA'].isin(temas_escolhidos)

				df = df_i[mask].reset_index(drop=True)

				IND_INIT_SIZE = len(df)

				for i, tema in enumerate(temas_escolhidos):
					dict_temas[tema] = qtd_temas[i]


				alertas = []
				for item in dict_temas.keys():
					limite = df[(df.TEMA == item)].reset_index(drop=True)
					if dict_temas[item] > len(limite):
						alertas.append('Alerta: quantidade de questões do tema {} é maior do que o disponível. Esse tema só tem {} questões'. format(item, len(limite)))

				if alertas:
					alertas
				else:
					questoes = []
					respostas  =[]

					seletor = Seletor(df, cargo, dict_temas, qtd_perguntas, IND_INIT_SIZE)
					resultado, mensagem = seletor.algoritmo()
					print(resultado)

					final = pd.DataFrame()
					imagens = []
					questoes = []

					contador = 0
					for i, item in enumerate(resultado):
						if item == 1:
							questao = df.loc[i, 'QUESTAO']
							resposta = df.loc[i, 'RESPOSTA']
							link = df.loc[i, 'LINKS']
							
							final.loc[contador, 'QUESTAO'] = questao
							final.loc[contador, 'RESPOSTA'] = resposta
							final.loc[contador, 'LINKS'] = link

							contador = contador+1
							questoes.append('Questão {}: {} \n Resposta: {}'.format(contador, questao, resposta))
							imagens.append(link)

					nota = []
					for i, item in enumerate(imagens):
						st.image(item)
						questoes[i]
						result = st.selectbox('Selecione o valor para a questão {}'.format(i+1), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
						nota.append(result)

					checkbox2 = st.checkbox('Quero salvar a avaliação das questões')

					submitted7 = st.form_submit_button("Finalizar")

					if checkbox2:

						notas = []
						for item in nota:
							notas.append(int(item))

						df3 = pd.DataFrame(questoes, columns = ['QUESTAO'])
						df4 = pd.DataFrame(notas, columns = ['NOTA'])

						df2 = pd.concat([df3, df4], axis=1).reset_index(drop=True)

						df2.to_csv('{}_avaliacao_questoes.csv'.format(st.session_state.name))

						nota_final = sum(notas)

						'A nota final do candidato foi:'
						nota_final

						if nota_final > 10:

							'Alerta: nota final maior do que 10'

						submitted3 = st.form_submit_button("Enviar avaliação para o candidato")
						
						if submitted3:

							try:

								questoes = []
								imagens = []

								final = pd.concat([final, df2.drop(['QUESTAO'], axis=1)], axis=1)

								final.to_html('filename.html', index=False)
								
								message_text = 'Olá! As questões do seu teste seguem em anexo, com as respostas e avaliação de cada uma. \n Sua NOTA FINAL foi {}.'.format(nota_final)
								to = st.session_state.name + ',' + 'samuel.faeng@gmail.com'
								sender = 'juliana.silva@sulamerica.com.br'
								subject = 'resultado entrevista'
								utils.SendMessage(sender, to, subject, message_text, 'filename.html')
								'Avaliação enviada para o candidato'

							except:

								'Verifique se você tem as credenciais adequadas para enviar email'
