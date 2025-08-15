import csv
import json
import pandas as pd


# cria um mapa para as colunas da planilha
def mkColsMap():
    CHARS = [
             'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O' ,'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y','Z', 
             'AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV','AW','AX','AY','AZ'
            ]
    res = {}
    for i in range(len(CHARS)):
        res[CHARS[i]] = i
    return res

COLSMAP = mkColsMap()

# retorna os valores máximos de produção para cada tipo de atendimento e complexidade
# (ainda sem uso - mas pode ser útil no futuro)
def getRoofs(table):
    res = { 'Ambulatorial': {}, 'Hospitalar': {}}
    line = 4
    res['Ambulatorial']['Alta'] = toFloat(table[line][COLSMAP['Y']])
    res['Ambulatorial']['Média'] = toFloat(table[line][COLSMAP['AA']])
    res['Hospitalar']['Alta'] = toFloat(table[line][COLSMAP['AD']])
    res['Hospitalar']['Média'] = toFloat(table[line][COLSMAP['AF']])
    return res

def getRoofValue(roofs, c, t):
    return roofs[t][c]

# Descrição do cabeçalho da planilha (3 níveis: Hospital/coluna inicial e Tipo de atendimento/Complexidade)
DESCR1 = {
    #'Mês': (0, (),()), # literalmente prá 'cumprir tabela'
    'CAISM': ('B', ('Ambulatorial', 'Hospitalar'),('Alta','Média', 'Total')),
    'CEPRE': ('I', ('Ambulatorial',),('Média',)),
    'CIPOI': ('J', ('Ambulatorial',),('Alta', 'Média', 'Total')),
    'GASTRO': ('M', ('Ambulatorial',),('Média',)),
    'HC': ('N', ('Ambulatorial', 'Hospitalar'),('Alta', 'Média', 'Total')),
    'HEMO': ('U', ('Ambulatorial',),('Alta', 'Média', 'Total')),
    'TOTAL UNICAMP': ('X', ('Ambulatorial', 'Hospitalar'),('Alta', 'Teto-alta', 'Média','Teto-média' 'Total')),
    'SUMÁRIO': ('AH', ('SUMÁRIO'),('TOTAL MAC', 'Pago SES/SP', 'Diferença')),
    # a planilha tem mais colunas, ainda por definir o que fazer com elas
}

HOSPITALS = ['CAISM', 'CEPRE', 'CIPOI', 'GASTRO', 'HC', 'HEMO']
COMPLEXIDADES = ['Alta', 'Média']

def getHospitalNames():
    hosp = list(HOSPITALS)
    hosp.append('Todos')  # não achei um jeito melhor de fazer isso...
    return hosp


def getMonthNames():
    return list(DESCR2.keys())



# Descrição de cada grupo de linhas da planilha (2 níveis: mes /linha inicial e 'tipo' do valor)
DESCR2 = {
    #'Mês': (3, '', ''), # literalmente prá 'cumprir tabela'
    'JANEIRO': (6, 'produção', 'rateio'),
    'FEVEREIRO': (8, 'produção', 'rateiro/previsão'),
    'MARÇO': (10, 'produção', 'rateio/previsão'),
    #'MARÇO2': (12, 'produção', 'rateio/definitivo', 'Diferenças'), # desativado, por enquanto
    'ABRIL': (15, 'produção', 'rateio/previsão'),
    'MAIO': (17, 'produção', 'rateio/previsão'),
    'JUNHO': (19, 'produção', 'rateio/previsão'),
    # a cada mes um novo grupo de linha, com o mesmo formato 
}

# retorna uma lista de colunas da planilha (c/ os nomes dos hospitais)
def getColNames():
    return list(DESCR1.keys())

# retorna uma lista de meses da planilha (c/ os nomes dos meses)
def getLineNames():
    return list(DESCR2.keys())

# converter os strings 'monetários' da planilha para float (exemplo: '1.050.205,22' para 1050205.22)
def toFloat(value):
    if value:
        try:
            return float(value.replace('.', '').replace(',', '.'))
        except ValueError:
            print(f"Warning: Could not convert '{value}' to float.")
    return 0.0

# converter float para valor monetário como string(exemplo: 1050205.22 para '1.050.205,22')
def toMoney(value):
    if value is None:
        return ''
    try:
        return f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except ValueError:
        print(f"Warning: Could not format '{value}' as money.")
        return str(value)


# Carrega os dados do arquivo CSV e retorna uma tabela com todos os valores (incluindo os campos vazios)
def loadData(file_path):
    try:
        with open(file_path, 'r', newline='', encoding='latin1') as csvfile:
            # Create a CSV reader object, specifying the semicolon as the delimiter
            csv_reader = csv.reader(csvfile, delimiter=';')
            # Iterate over each row in the CSV file
            rx = 1
            table = []
            for row in csv_reader:
                table.append(row)
                rx += 1
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    return table


# retorna o valor de produção para um dado hospital, tipo de atendimento, complexidade e mês
# se não houver valor, retorna 0.0
def getProdValue(table, hospital, tipo, complexidade, mes):
    try:
        line = DESCR2[mes][0] - 1
        startCol = COLSMAP[DESCR1[hospital][0]]
        if hospital not in HOSPITALS or mes not in DESCR2 or tipo not in DESCR1[hospital][1] or complexidade not in DESCR1[hospital][2]:
            #print(f"Invalid parameters: hospital={hospital}, tipo={tipo}, complexidade={complexidade}, mes={mes}")
            return 0.0 #None
        t = DESCR1[hospital][1].index(tipo)
        c = DESCR1[hospital][2].index(complexidade)
        col = startCol + t * len(DESCR1[hospital][2]) + c
        value = table[line][col]
        if value == '':
            value =  None
        return toFloat(value)
    except KeyError:
        #print('Key Error - mes:', mes, 'hospital:', hospital, 'tipo:', tipo, 'complexidade:', complexidade)
        return 0.0

# retorna um dataframe com um quadro compartativo de produção para um hospital e tipos de atendimento específicos
# a better name please ...
def getProdData_2(table, types):
    colHospital = []
    colComplexidade = []
    colProd = []
    for h in HOSPITALS:
        for c in COMPLEXIDADES:
            v = 0.0
            for t in types:
                for m in DESCR2.keys(): #monthNames:
                    v += getProdValue(table, h, t, c, m)
            colHospital.append(h)
            colComplexidade.append(c)
            colProd.append(v)
    return pd.DataFrame({
        'Hospital': colHospital,
        'Complexidade': colComplexidade,
        'Produção': colProd
    })


# monta um dataFrame com os dados de produção de uma lista de hospitais, para um tipo de atendimento específico
def getProdData(table, hospitalList, typeList, teto=False):
    #monthNames = getLineNames()
    colMes = []
    colComplexidade = []
    colProd = []
    totRec = {
        'Alta': 0.0,
        'Média': 0.0
    }
    #print('typeList:', typeList)
    for c in COMPLEXIDADES:
        for m in DESCR2.keys(): #monthNames:
            colMes.append(m)
            colComplexidade.append(c)
            v = 0
            for hospital in hospitalList:
                if not hospital  == 'Todos': # tá feio, eu sei...
                    for type in typeList:
                        if not type == 'Ambos':
                            prodValue = getProdValue(table, hospital, type, c, m)
                            v += prodValue if prodValue is not None else 0
            colProd.append(v)
            totRec[c] += v
    if teto:
        tetos = getRoofs(table)
        for c in COMPLEXIDADES:
            for m in DESCR2.keys(): #monthNames:
                v = 0
                colMes.append(m)
                colComplexidade.append(f'Teto({c})')
                for t in typeList:
                    #print('=> teto:', c, m, t)
                    v += getRoofValue(tetos, c, t)
                colProd.append(v)

    return pd.DataFrame({
        'Mes': colMes,
        'Complexidade': colComplexidade,
        'Produção': colProd
    }), totRec

# Exemplo de uso e teste deste módulo
# vai mudar tudo ...
if __name__ == "__main__":
    file_path = 'Indicadores_MAC.csv'

    table = loadData(file_path)
    if table:
        v = getProdValue(table, 'CEPRE', 'Ambulatorial', 'Média', 'JANEIRO')       
        print(f"Valor de produção: {toMoney(v)}")
        for mes in DESCR2.keys():
            for h in HOSPITALS:
                print(f"========== Mes: {mes} ---- Hospital: {h} ==========")
                for t in ['Ambulatorial', 'Hospitalar']:
                    for c in ['Alta', 'Média']:
                        v = getProdValue(table, h, t, c, mes)       
                        print(f"Hospital: {h}, Tipo: {t}, Complexidade: {c}, Valor de produção: {toMoney(v)}")
        df, totRec = getProdData(table, HOSPITALS, ['Ambulatorial', 'Hospitalar'], True)
        #print(df)
        df = getProdData_2(table, ['Ambulatorial', 'Hospitalar'])
        print(df)
        print('-- foi --')




