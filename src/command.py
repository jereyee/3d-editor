class Command:
    """ 
    Currently, this only supports undo-ing changes to the name, color, position, and orientation of an entity.
    This also does not account for dragging the entity around.
    In the future, it could possibly support undo-ing adding an object to the scene, deleting an object from the scene, etc.

    A class used to represent a Command which supports undo-ing changes to the name, color, position, and orientation of an entity.
    ...

    Attributes
    ----------
    entity : Entity3D
        an instance of the Entity3D class
    previousData : dict
        a dictionary containing the previous state of the entity
    currentData : dict
        a dictionary containing the current state of the entity

    Methods
    -------
    execute():
        Updates the entity with the current data
    undo():
        Reverts the entity to its previous state
    """

    def __init__(self, entity, data):
        self.entity = entity
        self.previousData = entity.toDict()
        self.currentData = data

    def execute(self):
        if self.entity is not None and self.entity.entity is not None:
            self.entity.updateProperties(self.currentData)

    def undo(self):
        if self.entity is not None and self.entity.entity is not None:
            self.entity.updateProperties(self.previousData)
