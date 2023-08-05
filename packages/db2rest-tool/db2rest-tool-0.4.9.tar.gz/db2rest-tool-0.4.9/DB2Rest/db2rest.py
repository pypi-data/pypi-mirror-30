# -*- coding: utf-8 -*-
from DB2Rest.db import Base, db_session, engine, meta
from DB2Rest.render_template import render_to_template,BASE_DIR
import json, pdb, os, importlib
from sqlalchemy import inspect
import ast


class LoadModelClasses(object):

    def __init__(self, path_config_file):
        self.CONFIG_FILE = path_config_file #Path do json de configuração


    def open_config_file(self):
        data = []

        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE) as data_file:
                data = json.load(data_file)
        print('Lendo arquivo de configuração...')

        return data

    def models_list(self):
        models_json = self.open_config_file()
        models_list = []

        for model_json in models_json:
            model = ModelHelper(**model_json)
            models_list.append(model)

        return models_list

    #Verifica se o nome da tabela informado existe na base de dados.
    def check_table_exist(self, table_name):

        table_names = meta.sorted_tables

        if table_name in str(table_names):
            return True

        return False

    def get_table(self, table_name):

        for table in meta.sorted_tables:
            if table.name==table_name:
                return table

        return False

    #Verifica se o nome da coluna informada existe na base de dados.
    def check_column_name(self,table_name, column_name):
        insp = inspect(engine)

        for collumn in insp.get_columns(table_name):
            if collumn.get('name') == column_name:
                return True

        return False

    def check_table_column(self, table_name, column_name):
        table=self.check_table_exist(table_name)
        column=self.check_column_name(table_name,column_name)
        if table and column:
            return True
        return False


    #Formata e checa as informações preenchidas sobre tabelas e atributos do arquivo de especificação.
    def check_model_attributes(self, model):

        if not self.check_table_exist(model.__db_table_name__):
            print('A __db_table_name__ informada para o modelo {0} não existe!'.format(model.__rst_model_name__))
            exit()

        for attributes_list in model.get_model_attributes():
            if not self.check_column_name(model.__db_table_name__, attributes_list.get('db_column_table')):
                print('A propriedade db_column_table ({0}) informado para o modelo {1} não existe na base de dados.'
                      .format(attributes_list.get('db_column_table'), model.__rst_model_name__))
                exit()

        return True

    #Geração do arquivo contendo os modelos.
    def generate_models(self):
        list_models = self.models_list()
        print("Gerando modelos...")
        for model in list_models:
            if self.check_model_attributes(model):
                setattr(model, 'attributes', model.get_model_attributes())
                print('Modelo->Tabela: {0} >>>> {1}'.format(model.__rst_model_name__, model.__db_table_name__))
            else:
                print('O __tablename__ informado para o modelo {0} não existe na base de dados.'.format(model.__modelname__))
                exit()
        return list_models


    def check_relationships(self, model):

        result_list=[]
        for relationship in model.get_relationships():
            table_name = relationship.get('db_referenced_table')#Obtém o nome da tabela com o qual tem relacionamento
            if table_name:
                if not relationship.get('type') == "M2M":
                    if not self.check_table_exist(table_name): #verifica se a tabela de fato existe na base
                        result_list.append({ "status":3,"model": '{0}: A tabela {1} não existe na Base de Dados. Verifique os relacionamentos para o modelo no JSON de configuração e tente novamente.'
                                       .format(model.__rst_model_name__,table_name)})
                    else:
                        mapper_table = inspect(self.get_table(table_name))
                        for pk in mapper_table.primary_key:
                            if not str(pk.name) == relationship.get('db_referenced_table_pk').split(".")[1]:
                                result_list.append({"status":1, "model": '{0}: Relacionamento entre {1} e {2} através da foreign_key {3} NÃO encontrado!'
                                               .format(model.__rst_model_name__,model.__db_table_name__,relationship.get('db_referenced_table'),relationship.get('db_referenced_table_pk'))})
                            else:
                                result_list.append({"status":2,"model": '{0}: Relacionamento entre {1} e {2} detectado!'
                                               .format(model.__rst_model_name__,model.__db_table_name__,relationship.get('db_referenced_table'))})
                        if relationship.get('db_referencing_table_fk'):
                            mapper_referencing_table = inspect(self.get_table(model.__db_table_name__))
                            columns =[]
                            for column in mapper_referencing_table.columns:
                                columns.append(str(column).split(".")[1])

                            if relationship.get('db_referencing_table_fk') not in columns:
                                result_list.append({"status":4, "model": "{0}: O atributo '{1}' (db_referencing_table_fk) informado como Foreign Key para a tabela '{2}' NÃO foi detectado"
                                               .format(model.__rst_model_name__,relationship.get('db_referencing_table_fk'),mapper_table)})

            return result_list


    def relationship_atributes_attrs(self, model, relation_list):
        if not getattr(model, 'relationship_atributes', None):
            setattr(model, 'relationship_atributes', relation_list)
            return model
        else:
            setattr(model, 'relationship_atributes', getattr(model, 'relationship_atributes') + relation_list)
            return model

    def generate_relationships(self,list_models):
        print('\nVerificando relacionamentos....\n')

        results=[]
        for model in list_models:
            if model.get_relationships():
                results.append(self.check_relationships(model))

            if model.get_relationships():
                for relation in model.get_relationships():
                    if relation.get('type') == 'M2O':
                        relation_M2O = [
                                {
                                 'relation_atribute_name': '{0}_id'.format(relation.get('rst_referencing_name')),
                                 'atribute_field': 'Column','atribute_field_name': "'{0}'".format(relation.get('db_referencing_table_fk')),
                                 'atribute_field_type': 'Integer','atribute_field_fk': "'{0}'".format(relation.get('db_referenced_table_pk'))
                                 },
                                 {
                                 'relation_atribute_name': relation.get('rst_referencing_name'),'atribute_field': 'relationship',
                                 'atribute_field_name': "'{0}'".format(relation.get('rst_referenced_model')),
                                 'atribute_field_backref': "'{0}'".format(relation.get('rst_referenced_backref')),
                                 'atribute_field_lazy':"'joined'"
                                 }]
                        self.relationship_atributes_attrs(model,relation_M2O)

                        relation_M2O_target = [
                                   {
                                   'relation_atribute_name': relation.get('rst_referenced_backref'),'atribute_field': 'relationship',
                                   'atribute_field_name': "'{0}'".format(model.__rst_model_name__),
                                   'atribute_field_backref':"'{0}'".format(relation.get('rst_referencing_name'))
                                   }]
                        target = self.get_model_by_name(list_models,relation.get('rst_referenced_model'))
                        self.relationship_atributes_attrs(target,relation_M2O_target)

                    if relation.get('type') == 'O2M':
                        relation_O2M = [
                                 {
                                 'relation_atribute_name': '{0}_id'.format(relation.get('rst_referencing_name')),
                                 'atribute_field': 'Column','atribute_field_name': "'{0}'".format(relation.get('db_referencing_table_fk')),
                                 'atribute_field_type': 'Integer','atribute_field_fk': "'{0}'".format(relation.get('db_referenced_table_pk'))
                                 },
                                 {
                                 'relation_atribute_name': relation.get('rst_referencing_name'),'atribute_field': 'relationship',
                                 'atribute_field_name': "'{0}'".format(relation.get('rst_referenced_model')),
                                 'atribute_field_backref': "'{0}'".format(relation.get('rst_referenced_backref')),
                                 'atribute_field_lazy':"'joined'"
                                 }]

                        self.relationship_atributes_attrs(model,relation_O2M)

                        relation_O2M_target = [
                                  {
                                  'relation_atribute_name': relation.get('rst_referenced_backref'),'atribute_field': 'relationship',
                                  'atribute_field_name': "'{0}'".format(model.__rst_model_name__),
                                  'atribute_field_backref':"'{0}'".format(relation.get('rst_referencing_name'))
                                  }]
                        target = self.get_model_by_name(list_models,relation.get('rst_referenced_model'))
                        self.relationship_atributes_attrs(target,relation_O2M_target)

                    if relation.get('type') == 'O2O':
                        relation_O2O = [
                                 {
                                  'relation_atribute_name': '{0}_id'.format(relation.get('rst_referencing_name')),
                                  'atribute_field': 'Column','atribute_field_name': "'{0}'".format(relation.get('db_referencing_table_fk')),
                                  'atribute_field_type': 'Integer','atribute_field_fk': "'{0}'".format(relation.get('db_referenced_table_pk'))
                                 },
                                 {
                                 'relation_atribute_name': relation.get('rst_referencing_name'),'atribute_field': 'relationship',
                                 'atribute_field_name': "'{0}'".format(relation.get('rst_referenced_model')),
                                 'atribute_field_back_populates': "'{0}'".format(relation.get('rst_referenced_backref'))
                                 }]
                        self.relationship_atributes_attrs(model,relation_O2O)

                        relation_O2O_target = [
                                   {
                                   'relation_atribute_name': relation.get('rst_referenced_backref'),'atribute_field': 'relationship',
                                   'atribute_field_name': "'{0}'".format(model.__rst_model_name__),
                                   'atribute_uselist': False, 'atribute_field_back_populates': "'{0}'".format(relation.get('rst_referencing_name'))
                                   }]
                        target = self.get_model_by_name(list_models,relation.get('rst_referenced_model'))
                        self.relationship_atributes_attrs(target,relation_O2O_target)

                    if relation.get('type') == 'M2M':
                        relation_M2M = [
                                 {
                                  'relation_atribute_name': '{0}_id'.format(relation.get('db_referenced_table_left_pk').split('.')[0]),
                                  'atribute_field': 'Column','atribute_field_type': 'Integer', 'atribute_pk':True,
                                  'atribute_field_fk': "'{0}'".format(relation.get('db_referenced_table_left_pk'))
                                 },
                                 {
                                 'relation_atribute_name': relation.get('rst_referencing_name_left'),'atribute_field': 'relationship',
                                 'atribute_field_name': "'{0}'".format(relation.get('rst_referenced_model_left')),
                                 'atribute_field_back_populates': "'{0}'".format(relation.get('rst_referenced_backref_left'))
                                 },
                                 {
                                 'relation_atribute_name': '{0}_id'.format(relation.get('db_referenced_table_right_pk').split('.')[0]),
                                 'atribute_field': 'Column','atribute_field_type': 'Integer','atribute_pk':True,
                                 'atribute_field_fk': "'{0}'".format(relation.get('db_referenced_table_right_pk'))
                                 },
                                 {
                                 'relation_atribute_name': relation.get('rst_referencing_name_right'),'atribute_field': 'relationship',
                                 'atribute_field_name': "'{0}'".format(relation.get('rst_referenced_model_right')),
                                 'atribute_field_back_populates': "'{0}'".format(relation.get('rst_referenced_backref_right'))
                                 }]
                        self.relationship_atributes_attrs(model,relation_M2M)

                        relation_M2M_target_A = [
                                   {
                                   'relation_atribute_name': relation.get('rst_referenced_backref_left'),'atribute_field': 'relationship',
                                   'atribute_field_name': "'{0}'".format(model.__rst_model_name__),
                                   'atribute_field_back_populates': "'{0}'".format(relation.get('rst_referencing_name_left'))
                                   }]
                        target_a = self.get_model_by_name(list_models,relation.get('rst_referenced_model_left'))
                        self.relationship_atributes_attrs(target_a,relation_M2M_target_A)

                        relation_M2M_target_B = [
                                   {
                                   'relation_atribute_name': relation.get('rst_referenced_backref_right'),'atribute_field': 'relationship',
                                   'atribute_field_name': "'{0}'".format(model.__rst_model_name__),
                                   'atribute_field_back_populates': "'{0}'".format(relation.get('rst_referencing_name_right'))
                                   }]
                        target_b = self.get_model_by_name(list_models,relation.get('rst_referenced_model_right'))
                        self.relationship_atributes_attrs(target_b,relation_M2M_target_B)

        [print('>>> {0}'.format(r.get('model'))) for result in results for r in result]
        return list_models, results


    def get_model_by_name(self, list_models, model_name):

        for model in list_models:
            if model.__rst_model_name__ == model_name:
                return model

    def check_status_relation(self, list_relations_result):
        status_list=[]
        for results in list_relations_result:
            for result in results:
                if result.get('status')==1 or result.get('status')==3 or result.get('status')==4:
                    status_list.append(result)
        return status_list

    def generate_derived_attributes(self, list_models):
        result_list=[]
        derived_attributes_format=[]
        for model in list_models:
            derived_attributes = model.get_derived_attributes()
            if derived_attributes:
                print('\nVerificando atributos derivados...\n')
                for derived_attribute in derived_attributes:
                    for column in derived_attribute.get('db_columns'):
                        validate_fields = self.check_table_column(column.split('.')[0], column.split('.')[1])
                        if validate_fields is True:
                            derived_attributes_format.append({
                                "rst_property_name": derived_attribute.get('rst_property_name'),
                                "table": column.split('.')[0],
                                "column": column.split('.')[1],
                                "db_clause_where_att": derived_attribute.get('db_clause_where')[0],
                                "db_clause_where_value": derived_attribute.get('db_clause_where')[1],
                                "db_rows_many": ast.literal_eval(derived_attribute.get('db_rows_many'))
                            })
                            result_list.append({"status":1, "model":"{0}: O atributo derivado {1} foi criado com sucesso!".
                                format(model.__rst_model_name__,derived_attribute.get('rst_property_name'))})
                        else:
                            result_list.append({"status":2, "model":"{0}: A tabela('{1}') ou atributo('{2}') informados como 'derived_attributes' NÃO existe!".
                                      format(model.__rst_model_name__,column.split('.')[0],column.split('.')[1])})
                setattr(model, 'derived_attributes', derived_attributes_format)
                [print('>>> {0}'.format(result.get('model'))) for result in result_list]

        return list_models, result_list


    def generate_file(self):
       list_models = self.generate_models()
       list_models_relationships = self.generate_relationships(list_models)
       list_derived_attributes = self.generate_derived_attributes(list_models)

       status_list = self.check_status_relation(list_models_relationships[1])
       status_derived_attributes = []
       [status_derived_attributes.append(m.get('status')) for m in list_derived_attributes[1] if m.get('status')==2]
       if not status_list and not status_derived_attributes:
           render_to_template(BASE_DIR+"/models.py", "model_template.py",list_models_relationships[0])
           print('\nArquivo models.py gerado com sucesso! Realize o import deste arquivo para uso dos serviços!\n')
       else:
           print('\nNão foi possível gerar o arquivo models.py devido a inconsistencia nos dados de relacionamentos ou atributos derivados. Verifique o detalhamento acima e faça as correções necessárias.')



class ModelHelper(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_model_attributes(self):
        model_attrs = {}
        for attribute in self.__dict__.keys():
            if not attribute.startswith('__'):
                if attribute == 'attributes':
                    model_attrs = getattr(self,attribute)
                    return model_attrs

        return model_attrs

    def get_relationships(self):
        relationships_attr = getattr(self, 'relationships', None)
        if relationships_attr:
            return relationships_attr

    def get_derived_attributes(self):
        derived_attributes = getattr(self, 'derived_attributes', None)
        derived_attributes_list=[]
        if derived_attributes:
            for derived_attribute in derived_attributes:
                columns = derived_attribute.get('db_columns').split("|")
                derived_attributes_list.append(dict(rst_property_name=derived_attribute.get('rst_property_name'),
                                                    db_columns=columns, db_rows_many=derived_attribute.get('db_rows_many'),
                                                    db_clause_where= derived_attribute.get('db_clause_where').split("|")))
        return derived_attributes_list
