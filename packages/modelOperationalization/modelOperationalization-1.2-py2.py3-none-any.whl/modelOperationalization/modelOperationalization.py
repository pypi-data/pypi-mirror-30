# -*- coding: utf-8 -*-

"""Main module."""
import pickle as pi


class ModelSerializer:
    def __init__(self, filePath):
        '''
        :param filePath:
            oherwise RuntimeError is raised
        '''
        if filePath == None:
                raise RuntimeError('Filepath  for model location not specified')
        else:
            self.filePath = filePath

    def set_filePath(self, filePath):
        self.filePath = filePath

    def store(self, model, fileName):
        f = open(self.filePath + fileName, 'wb')
        pi.dump(model, f)
        f.close()

    def load(self, fileName):
        f = open(self.filePath+fileName, 'rb')
        result = pi.load(f)
        f.close()
        return result


    def test(self, fileName):
        f = open(self.filePath+fileName, 'rb')
        result = pi.load(f)
        f.close()
        return result


class PythonModel:
    """A Python Model

    Attributes:
        name: A String representing the name of the model. E.G. FuelConsumptionPredictor
        version: A String representing the version of the model. E.G. V1_02
        metaData: A dictionary containg key-value pairs to store meta data about the model.
        model: An object representing a Python model. E.G a regressor, classifier
    """

    def __init__(self, name, version, model,created,metaData):
        """Return a new Model object."""
        self.name = name
        self.version = version
        self.model = model
        self.created = created
        self.metaData = metaData


    def model(self):
        """Return the actual model"""
        return self.model

    def name(self):
        """Return the name of the model"""
        return self.name

    def version(self):
        """Return the version of the model"""
        return self.version

    def created(self):
        """Return the datetime when the model was created"""
        return self.created

    def metaData(self):
        """Return the metaData of the model"""
        return self.metaData
